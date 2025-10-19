from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
import joblib
import re
import string
import spacy
import fitz  # PyMuPDF - using this as primary PDF extractor
import io
import requests
import json
import os
from pdf2image import convert_from_bytes
from models.fixed_template_renderer import FixedTemplateRenderer
import logging

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed, will use system env vars

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
CORS(app)

# Hugging Face API setup - using a more reliable free model
HF_API_TOKEN = os.getenv("HF_API_TOKEN")
HF_API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"  # Free summarization model

if not HF_API_TOKEN:
    app.logger.warning("HF_API_TOKEN not set! Set it with: export HF_API_TOKEN=your_token (Linux/Mac) or setx HF_API_TOKEN your_token (Windows)")

# Tesseract OCR path - make sure this is installed
try:
    import pytesseract
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    OCR_AVAILABLE = True
except ImportError:
    app.logger.warning("pytesseract not installed. OCR fallback disabled.")
    OCR_AVAILABLE = False

# Load spaCy
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    app.logger.error("spaCy model 'en_core_web_sm' not found. Run: python -m spacy download en_core_web_sm")
    raise

# Load models
try:
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
except FileNotFoundError as e:
    app.logger.error(f"Model file not found: {e}")
    raise

IT_SKILL_LIST = ['python', 'java', 'sql', 'machine learning', 'data analysis', 'react', 'c++', 'cloud computing', 
                 'javascript', 'aws', 'docker', 'kubernetes', 'tensorflow', 'django', 'flask', 'nodejs']
NON_IT_SKILL_LIST = ['communication', 'excel', 'salesforce', 'customer support', 'team management', 'public speaking',
                     'leadership', 'project management', 'negotiation', 'time management', 'problem solving']

# -------------------- Utility Functions --------------------
def clean_text(text):
    """Clean and normalize text"""
    text = re.sub(r"<[^>]+>", "", str(text))
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = text.lower()
    return re.sub(r"\s+", " ", text).strip()

def lemmatize(text):
    """Lemmatize text using spaCy"""
    doc = nlp(text)
    return " ".join([token.lemma_ for token in doc if not token.is_punct and not token.is_stop])

def extract_skills(text, skill_list):
    """Extract skills found in text"""
    text_lower = text.lower()
    return [skill for skill in skill_list if skill.lower() in text_lower]

def get_missing_skills(resume_skills, required_skills):
    """Get skills that are missing from resume"""
    return list(set(required_skills) - set(resume_skills))

def detect_domain(text):
    """Detect if resume is IT or Non-IT based on skills"""
    text_lower = text.lower()
    it_score = sum(1 for skill in IT_SKILL_LIST if skill.lower() in text_lower)
    nonit_score = sum(1 for skill in NON_IT_SKILL_LIST if skill.lower() in text_lower)
    return "IT" if it_score >= nonit_score else "Non-IT"

# -----------------------------
# PDF Text Extraction (Fixed)
# -----------------------------
def extract_text_from_pdf(file):
    """Extract text from PDF using multiple methods"""
    text = ""

    # Primary method: PyMuPDF (most reliable)
    try:
        file.seek(0)
        pdf_bytes = file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        for page in doc:
            page_text = page.get_text()
            if page_text:
                text += page_text + "\n"
        
        doc.close()
        
        if text.strip():
            app.logger.info("PDF text extracted successfully using PyMuPDF")
            return text.strip()
    except Exception as e:
        app.logger.warning(f"PyMuPDF extraction failed: {e}")

    # Fallback: OCR if available
    if OCR_AVAILABLE:
        try:
            file.seek(0)
            images = convert_from_bytes(file.read())
            app.logger.info(f"Performing OCR on {len(images)} pages...")
            
            for idx, img in enumerate(images):
                page_text = pytesseract.image_to_string(img)
                text += page_text + "\n"
                app.logger.info(f"OCR page {idx+1} completed")
            
            if text.strip():
                app.logger.info("PDF text extracted successfully using OCR")
                return text.strip()
        except Exception as e:
            app.logger.error(f"OCR extraction failed: {e}")

    return text.strip() if text else "Unable to extract text from PDF"

# -----------------------------
# Hugging Face Model Caller (Improved)
# -----------------------------
def call_hf_model(prompt, max_retries=3):
    """Call Hugging Face API with retry logic"""
    if not HF_API_TOKEN:
        app.logger.error("Missing HF_API_TOKEN")
        return generate_fallback_response(prompt)

    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    
    # List of free models to try in order
    models = [
        "facebook/bart-large-cnn",  # Summarization
        "google/flan-t5-small",     # Text generation
        "t5-small"                   # Basic T5
    ]
    
    for model in models:
        url = f"https://api-inference.huggingface.co/models/{model}"
        
        for attempt in range(max_retries):
            try:
                # Truncate prompt if too long
                truncated_prompt = prompt[:1000] if len(prompt) > 1000 else prompt
                
                response = requests.post(
                    url,
                    headers=headers,
                    json={"inputs": truncated_prompt, "parameters": {"max_length": 150}},
                    timeout=30
                )
                
                if response.status_code == 200:
                    app.logger.info(f"Successfully called {model}")
                    return response.json()
                elif response.status_code == 503:
                    app.logger.warning(f"{model} is loading, waiting...")
                    import time
                    time.sleep(5)
                    continue
                elif response.status_code == 403:
                    app.logger.warning(f"Access denied for {model}, trying next model...")
                    break
                else:
                    app.logger.warning(f"API returned {response.status_code}: {response.text}")
                    
            except requests.exceptions.Timeout:
                app.logger.warning(f"Timeout on attempt {attempt+1} for {model}")
            except Exception as e:
                app.logger.error(f"Error calling {model}: {e}")
    
    # If all models fail, use fallback
    app.logger.warning("All HF models failed, using fallback")
    return generate_fallback_response(prompt)

def generate_fallback_response(prompt):
    """Generate basic response without API - improved version"""
    # Extract skills from prompt
    skills_match = re.search(r'Skills?[:\s]+(.+?)(?:\n|Job)', prompt, re.IGNORECASE | re.DOTALL)
    skills_text = skills_match.group(1).strip() if skills_match else ""
    
    # Extract job info
    job_match = re.search(r'Job[:\s]+(.+?)(?:\n|Create|$)', prompt, re.IGNORECASE | re.DOTALL)
    job_text = job_match.group(1).strip() if job_match else ""
    
    # Generate professional summary based on extracted info
    summaries = [
        f"Results-driven professional with demonstrated expertise in {skills_text[:100]}. " +
        "Proven ability to deliver high-impact solutions in fast-paced environments.",
        
        f"Accomplished specialist with strong background in {skills_text[:100]}. " +
        "Track record of excellence in project execution and technical innovation.",
        
        f"Dynamic professional skilled in {skills_text[:100]}. " +
        "Combines technical proficiency with strategic thinking to drive organizational success."
    ]
    
    # Select summary based on skills length
    summary_idx = len(skills_text) % len(summaries)
    
    return [{
        "summary_text": summaries[summary_idx]
    }]

# -------------------- Routes --------------------

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/detect_domain", methods=["POST"])
def detect_resume_domain():
    """Detect if resume is IT or Non-IT domain"""
    if "resume" not in request.files:
        return jsonify({"error": "No resume file uploaded."}), 400

    file = request.files["resume"]
    if not file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Only PDF files are supported."}), 400

    try:
        text = extract_text_from_pdf(file)
        if not text or text == "Unable to extract text from PDF":
            return jsonify({"error": "Could not extract text from PDF. Please ensure the PDF is readable."}), 400
        
        cleaned = lemmatize(clean_text(text))
        domain = detect_domain(cleaned)

        return jsonify({
            "domain": domain,
            "cleaned_text": cleaned[:500] + "..." if len(cleaned) > 500 else cleaned,
            "message": f"Your resume seems to belong to the {domain} domain. Do you want to proceed?"
        })

    except Exception as e:
        app.logger.error(f"Error in detect_domain: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/proceed_prediction", methods=["POST"])
def proceed_prediction():
    """Make predictions based on resume content"""
    if "resume" not in request.files:
        return jsonify({"error": "No resume file uploaded."}), 400

    file = request.files["resume"]
    if not file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Only PDF files are supported."}), 400

    try:
        text = extract_text_from_pdf(file)
        if not text or text == "Unable to extract text from PDF":
            return jsonify({"error": "Could not extract text from PDF."}), 400
        
        cleaned = lemmatize(clean_text(text))
        domain = detect_domain(cleaned)

        if domain == "IT":
            vec = it_tfidf.transform([cleaned])
            pred = it_skill_model.predict(vec)
            skills = it_mlb.inverse_transform(pred)[0]
            role = it_role_model.predict(it_tfidf.transform([" ".join(skills)]))[0]
            resume_skills = extract_skills(cleaned, IT_SKILL_LIST)
            missing = get_missing_skills(resume_skills, IT_SKILL_LIST)
            x_vec = it_coursecert_tfidf.transform([" ".join(missing) if missing else "general"])
            course = it_course_model.predict(x_vec)[0]
            cert = it_cert_model.predict(x_vec)[0]
        else:
            vec = nonit_tfidf.transform([cleaned])
            pred = nonit_skill_model.predict(vec)
            skills = nonit_mlb.inverse_transform(pred)[0]
            role = nonit_role_model.predict(nonit_tfidf.transform([" ".join(skills)]))[0]
            resume_skills = extract_skills(cleaned, NON_IT_SKILL_LIST)
            missing = get_missing_skills(resume_skills, NON_IT_SKILL_LIST)
            x_vec = nonit_coursecert_tfidf.transform([" ".join(missing) if missing else "general"])
            course = nonit_course_model.predict(x_vec)[0]
            cert = nonit_cert_model.predict(x_vec)[0]

        return jsonify({
            "domain": domain,
            "predicted_skills": ", ".join(skills) if skills else "No specific skills predicted",
            "resume_skills": resume_skills,
            "missing_skills": missing,
            "predicted_role": role,
            "recommendation": {
                "course": course,
                "certificate": cert
            }
        })

    except Exception as e:
        app.logger.error(f"Error in proceed_prediction: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/scrape-jobs", methods=["POST"])
def scrape_jobs():
    """Scrape jobs from Adzuna API"""
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

    if location and location.lower() != "remote":
        params["where"] = location

    if salary_min.isdigit() and int(salary_min) >= 10000:
        params["salary_min"] = salary_min

    try:
        response = requests.get(base_url, params=params, timeout=10)
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
        app.logger.error(f"Error scraping jobs: {e}")
        return jsonify({"error": "Failed to fetch jobs", "details": str(e)}), 500

# -----------------------------
# Resume Optimization Endpoint (Improved)
# -----------------------------
@app.route('/optimize_resume', methods=['POST'])
def optimize_resume():
    """Optimize resume based on job description"""
    if 'resume' not in request.files:
        return jsonify({"error": "No resume uploaded"}), 400

    resume_file = request.files['resume']
    job_description = request.form.get('job_description', '')
    
    try:
        additional_info = json.loads(request.form.get('additional_info', '{}'))
    except json.JSONDecodeError:
        additional_info = {}

    # Extract resume text
    resume_text = extract_text_from_pdf(resume_file)
    
    if not resume_text or resume_text == "Unable to extract text from PDF":
        return jsonify({"error": "Could not extract text from resume"}), 400

    # Extract skills from resume
    cleaned_text = clean_text(resume_text)
    resume_skills = extract_skills(cleaned_text, IT_SKILL_LIST + NON_IT_SKILL_LIST)

    # Build concise prompt for HF model
    prompt = f"""Generate a professional summary for this resume:
Skills: {', '.join(resume_skills[:10])}
Job: {job_description[:200]}
Create a 2-3 sentence professional summary."""

    try:
        # Call HF model
        hf_response = call_hf_model(prompt)

        # Parse response
        if isinstance(hf_response, list) and len(hf_response) > 0:
            if "summary_text" in hf_response[0]:
                summary = hf_response[0]["summary_text"]
            elif "generated_text" in hf_response[0]:
                summary = hf_response[0]["generated_text"]
            else:
                summary = str(hf_response[0])
        else:
            summary = "Experienced professional with proven expertise in delivering results."

        # Build optimized resume data matching the template format
        optimized_resume = {
            "personal_info": {
                "name": additional_info.get('name', 'Your Name'),
                "phone": additional_info.get('phone', '+91-XXXXXXXXXX'),
                "email": additional_info.get('email', 'email@example.com'),
                "location": additional_info.get('location', 'City, Country'),
                "linkedin": additional_info.get('linkedin', ''),
                "github": additional_info.get('github', '')
            },
            "professional_summary": summary,
            "skills": resume_skills[:15] if resume_skills else ["Python", "Machine Learning", "Data Analysis"],
            "education": [],
            "experience": [],
            "projects": [],
            "certifications": [],
            "achievements": []
        }

        # Ensure static directory exists
        os.makedirs('static', exist_ok=True)

        # Render PDF
        renderer = FixedTemplateRenderer()
        pdf_path = renderer.render_resume(optimized_resume)

        return send_file(pdf_path, as_attachment=True, download_name="optimized_resume.pdf")

    except Exception as e:
        app.logger.error(f"Error in optimize_resume: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Failed to optimize resume: {str(e)}"}), 500

# Health check endpoint
@app.route('/health')
def health():
    return jsonify({"status": "healthy", "ocr_available": OCR_AVAILABLE})

# -----------------------------
# Run App
# -----------------------------
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)