from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
import joblib
import re
import string
import spacy
import pdfplumber
import pytesseract
from PIL import Image
import fitz  # PyMuPDF
import io
import requests
import feedparser
import json
import yake
import os
from pdf2image import convert_from_bytes  # ✅ added
from models.fixed_template_renderer import FixedTemplateRenderer
import logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
CORS(app)

# Hugging Face API setup
HF_API_TOKEN = os.getenv("HF_API_TOKEN")  # ✅ secure way (set in env vars)
HF_API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-small"  # ✅ free model

if not HF_API_TOKEN:
    app.logger.error("HF_API_TOKEN not set! Run: setx HF_API_TOKEN your_token")

# Tesseract OCR path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Load spaCy
nlp = spacy.load("en_core_web_sm")

# Load models (unchanged)
it_skill_model = joblib.load("models/IT_skill_model.pkl")
nonit_skill_model = joblib.load("models/Non_IT_skill_model.pkl")
it_tfidf = joblib.load("models/IT_tfidf.pkl")
nonit_tfidf = joblib.load("models/Non_IT_tfidf.pkl")
it_mlb = joblib.load("models/IT_mlb.pkl")
nonit_mlb = joblib.load("models/Non_IT_mlb.pkl")
it_role_model = joblib.load("models/IT_job_role_model.pkl")
nonit_role_model = joblib.load("models/Non_IT_job_role_model.pkl")
it_course_model = joblib.load("models/IT_course_model.pkl")
nonit_course_model = joblib.load("models/NonIT_course_model.pkl")
it_cert_model = joblib.load("models/IT_cert_model.pkl")
nonit_cert_model = joblib.load("models/NonIT_cert_model.pkl")
it_coursecert_tfidf = joblib.load("models/IT_coursecert_tfidf.pkl")
nonit_coursecert_tfidf = joblib.load("models/NonIT_coursecert_tfidf.pkl")

IT_SKILL_LIST = ['python', 'java', 'sql', 'machine learning', 'data analysis', 'react', 'c++', 'cloud computing']
NON_IT_SKILL_LIST = ['communication', 'excel', 'salesforce', 'customer support', 'team management', 'public speaking']

# -------------------- Utility Functions --------------------
def clean_text(text):
    text = re.sub(r"<[^>]+>", "", str(text))
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = text.lower()
    return re.sub(r"\s+", " ", text)

def lemmatize(text):
    doc = nlp(text)
    return " ".join([token.lemma_ for token in doc if not token.is_punct and not token.is_stop])

def extract_skills(text, skill_list):
    return [skill for skill in skill_list if skill in text]

def get_missing_skills(resume_skills, required_skills):
    return list(set(required_skills) - set(resume_skills))

def detect_domain(text):
    it_score = sum(skill in text for skill in IT_SKILL_LIST)
    nonit_score = sum(skill in text for skill in NON_IT_SKILL_LIST)
    return "IT" if it_score >= nonit_score else "Non-IT"

# -----------------------------
# PDF Text Extraction
# -----------------------------
def extract_text_from_pdf(file):
    text = ""

    # First try PyMuPDF
    try:
        file.seek(0)  # ✅ reset before reading
        doc = fitz.open(stream=file.read(), filetype="pdf")
        text = "".join(page.get_text() or "" for page in doc)
        if text.strip():
            return text
    except Exception as e:
        app.logger.warning(f"fitz failed: {e}")

    # Fallback: pdfplumber
    try:
        file.seek(0)  # ✅ reset before pdfplumber
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        if text.strip():
            return text
    except Exception as e:
        app.logger.warning(f"pdfplumber failed: {e}")

    # Final fallback: OCR
    try:
        file.seek(0)  # ✅ reset before OCR
        images = convert_from_bytes(file.read())
        for img in images:
            text += pytesseract.image_to_string(img)
    except Exception as e:
        app.logger.error(f"OCR failed: {e}")

    return text.strip()

# -----------------------------
# Hugging Face Model Caller
# -----------------------------
def call_hf_model(prompt, model_url):
    if not HF_API_TOKEN:
        raise ValueError("Missing Hugging Face API token. Set HF_API_TOKEN in environment variables.")

    response = requests.post(
        model_url,
        headers={"Authorization": f"Bearer {HF_API_TOKEN}"},
        json={"inputs": prompt}
    )

    if response.status_code == 403:
        raise PermissionError(f"Access denied for {model_url}. Check if model is gated or token is invalid.")

    response.raise_for_status()
    return response.json()



# -------------------- Routes --------------------


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/detect_domain", methods=["POST"])
def detect_resume_domain():
    if "resume" not in request.files:
        return jsonify({"error": "No resume file uploaded."}), 400

    file = request.files["resume"]
    if not file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Only PDF files are supported."}), 400

    try:
        text = extract_text_from_pdf(file)
        cleaned = lemmatize(clean_text(text))
        domain = detect_domain(cleaned)

        return jsonify({
            "domain": domain,
            "cleaned_text": cleaned,
            "message": f"Your resume seems to belong to the {domain} domain. Do you want to proceed?"
        })

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route("/proceed_prediction", methods=["POST"])
def proceed_prediction():
    if "resume" not in request.files:
        return jsonify({"error": "No resume file uploaded."}), 400

    file = request.files["resume"]
    if not file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Only PDF files are supported."}), 400

    try:
        text = extract_text_from_pdf(file)
        cleaned = lemmatize(clean_text(text))
        domain = detect_domain(cleaned)

        if domain == "IT":
            vec = it_tfidf.transform([cleaned])
            pred = it_skill_model.predict(vec)
            skills = it_mlb.inverse_transform(pred)[0]
            role = it_role_model.predict(it_tfidf.transform([" ".join(skills)]))[0]
            resume_skills = extract_skills(cleaned, IT_SKILL_LIST)
            missing = get_missing_skills(resume_skills, IT_SKILL_LIST)
            x_vec = it_coursecert_tfidf.transform([" ".join(missing)])
            course = it_course_model.predict(x_vec)[0]
            cert = it_cert_model.predict(x_vec)[0]
        else:
            vec = nonit_tfidf.transform([cleaned])
            pred = nonit_skill_model.predict(vec)
            skills = nonit_mlb.inverse_transform(pred)[0]
            role = nonit_role_model.predict(nonit_tfidf.transform([" ".join(skills)]))[0]
            resume_skills = extract_skills(cleaned, NON_IT_SKILL_LIST)
            missing = get_missing_skills(resume_skills, NON_IT_SKILL_LIST)
            x_vec = nonit_coursecert_tfidf.transform([" ".join(missing)])
            course = nonit_course_model.predict(x_vec)[0]
            cert = nonit_cert_model.predict(x_vec)[0]

        return jsonify({
            "domain": domain,
            "predicted_skills": ", ".join(skills),
            "resume_skills": resume_skills,
            "missing_skills": missing,
            "predicted_role": role,
            "recommendation": {
                "course": course,
                "certificate": cert
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/scrape-jobs", methods=["POST"])
def scrape_jobs():
    data = request.get_json()
    job_role = data.get('job_role', '').strip()
    location = data.get('location', '').strip()
    salary_min = data.get('salary_min', '').strip()

    if not job_role:
        return jsonify([])

    base_url = "https://api.adzuna.com/v1/api/jobs/in/search/1"
    params = {
        "app_id": "30c6c5c3",
        "app_key": "4f3d3ea6ec822580798794aaa7fefd75",
        "results_per_page": 6,
        "what": job_role,
        "content-type": "application/json"
    }

    # Smart filtering: apply only if not "remote" or empty
    if location and location.lower() != "remote":
        params["where"] = location

    # Smart salary filter: skip if not valid number or too low
    if salary_min.isdigit() and int(salary_min) >= 10000:
        params["salary_min"] = salary_min

    try:
        response = requests.get(base_url, params=params)
        if response.status_code != 200:
            return jsonify({"error": f"Adzuna API error: {response.status_code}"}), response.status_code

        data = response.json()
        jobs = []

        for job in data.get("results", []):
            jobs.append({
                "title": job.get("title"),
                "company": job.get("company", {}).get("display_name", "N/A"),
                "location": job.get("location", {}).get("display_name", "N/A"),
                "salary_min": job.get("salary_min", "N/A"),
                "salary_max": job.get("salary_max", "N/A"),
                "url": job.get("redirect_url", "#")
            })

        return jsonify(jobs)

    except Exception as e:
        return jsonify({"error": "Failed to fetch jobs", "details": str(e)}), 500


# -----------------------------
# Resume Optimization Endpoint
# -----------------------------
@app.route('/optimize_resume', methods=['POST'])
def optimize_resume():
    if 'resume' not in request.files:
        return jsonify({"error": "No resume uploaded"}), 400

    resume_file = request.files['resume']
    job_description = request.form.get('job_description', '')
    additional_info = json.loads(request.form.get('additional_info', '{}'))

    # Extract resume text
    resume_text = extract_text_from_pdf(resume_file)

    # Build prompt
    prompt = f"""
    Resume Text:
    {resume_text}

    Job Description:
    {job_description}

    Personal Info:
    {additional_info}

    Please generate JSON with:
    {{
      "summary": "Professional summary tailored to job",
      "skills": ["skill1", "skill2"]
    }}
    """

    try:
        # Try primary model
        try:
            hf_response = call_hf_model(prompt, HF_API_URL)
        except PermissionError:
            # Fallback model (completely free)
            fallback_url = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
            app.logger.warning("403 Forbidden from Hugging Face. Falling back to bart-large-cnn.")
            hf_response = call_hf_model(prompt, fallback_url)

        # Parse response
        if isinstance(hf_response, list) and "generated_text" in hf_response[0]:
            raw_text = hf_response[0]["generated_text"]
        elif isinstance(hf_response, dict):
            raw_text = hf_response.get("generated_text") or hf_response.get("summary_text") or str(hf_response)
        else:
            raw_text = str(hf_response)

        # Extract JSON safely
        json_match = re.search(r'(\{.*\})', raw_text, re.DOTALL)
        json_text = json_match.group(1) if json_match else "{}"
        parsed = json.loads(json_text)

        optimized_resume = {
            "personal_info": additional_info,
            "professional_summary": parsed.get("summary", ""),
            "skills": parsed.get("skills", []),
            "experience": [],
            "education": [],
            "projects": [],
            "certifications": []
        }

        # Ensure static directory exists
        if not os.path.exists('static'):
            os.makedirs('static')

        # Render PDF
        renderer = FixedTemplateRenderer()
        pdf_path = renderer.render_resume(optimized_resume)

        return send_file(pdf_path, as_attachment=True, download_name="optimized_resume.pdf")

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# -----------------------------
# Run App
# -----------------------------
if __name__ == '__main__':
    app.run(debug=True)