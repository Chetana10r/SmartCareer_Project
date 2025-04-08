from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import joblib
import pandas as pd
import re
import string
import spacy
import pdfplumber
import pytesseract
from PIL import Image
import fitz  # PyMuPDF
import io
from pdf2image import convert_from_bytes

app = Flask(__name__)
CORS(app)

# Path to Tesseract OCR
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Load spaCy
nlp = spacy.load("en_core_web_sm")

# Load all models
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

# Skill lists
IT_SKILL_LIST = ['python', 'java', 'sql', 'machine learning', 'data analysis', 'react', 'c++', 'cloud computing']
NON_IT_SKILL_LIST = ['communication', 'excel', 'salesforce', 'customer support', 'team management', 'public speaking']

# Helper functions
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

# PDF Text Extraction with fallback
def extract_text_from_pdf(file):
    try:
        pdf_bytes = file.read()

        # Try PyMuPDF
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = "".join([page.get_text() for page in doc])
        doc.close()
        if text.strip():
            return text

        # Try pdfplumber
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            text = "".join([page.extract_text() or "" for page in pdf.pages])
        if text.strip():
            return text

        # Fallback to OCR
        images = convert_from_bytes(pdf_bytes)
        ocr_text = ""
        for img in images:
            img = img.convert("RGB")
            ocr_text += pytesseract.image_to_string(img)

        if not ocr_text.strip():
            raise ValueError("Unable to extract text from PDF. Try uploading a clearer file.")

        return ocr_text

    except Exception as e:
        raise ValueError(f"OCR/PDF extraction failed: {str(e)}")

# ---------------- API Routes ---------------- #

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

        # Debugging output
        print("----- DEBUG /detect_domain -----")
        print("Extracted Text Snippet:", text[:300])
        print("Cleaned Text:", cleaned[:300])
        print("Detected Domain:", domain)
        print("--------------------------------")

        return jsonify({
            "domain": domain,
            "cleaned_text": cleaned,
            "message": f"Your resume seems to belong to the {domain} domain. Do you want to proceed?"
        })

    except ValueError as e:
        print("Error in /detect_domain:", str(e))
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

        print("----- DEBUG OUTPUT (Prediction Phase) -----")
        print("Detected Domain:", domain)
        print("Cleaned Resume Text Snippet:", cleaned[:300])

        if domain == "IT":
            vec = it_tfidf.transform([cleaned])
            print("TF-IDF Vector (IT):", vec)

            pred = it_skill_model.predict(vec)
            print("Raw Predicted Labels (IT):", pred)

            skills = it_mlb.inverse_transform(pred)[0]
            print("Predicted Skills (IT):", skills)

            # ✅ FIX: Vectorize role input
            role_input_text = " ".join(skills)
            role_input_vector = it_tfidf.transform([role_input_text])
            role = it_role_model.predict(role_input_vector)[0]
            print("Predicted Role (IT):", role)

            resume_skills = extract_skills(cleaned, IT_SKILL_LIST)
            missing = get_missing_skills(resume_skills, IT_SKILL_LIST)
            print("Resume Skills:", resume_skills)
            print("Missing Skills:", missing)

            X = it_coursecert_tfidf.transform([" ".join(missing)])
            course = it_course_model.predict(X)[0]
            cert = it_cert_model.predict(X)[0]

        else:
            vec = nonit_tfidf.transform([cleaned])
            print("TF-IDF Vector (Non-IT):", vec)

            pred = nonit_skill_model.predict(vec)
            print("Raw Predicted Labels (Non-IT):", pred)

            skills = nonit_mlb.inverse_transform(pred)[0]
            print("Predicted Skills (Non-IT):", skills)

            # ✅ FIX: Vectorize role input
            role_input_text = " ".join(skills)
            role_input_vector = nonit_tfidf.transform([role_input_text])
            role = nonit_role_model.predict(role_input_vector)[0]
            print("Predicted Role (Non-IT):", role)

            resume_skills = extract_skills(cleaned, NON_IT_SKILL_LIST)
            missing = get_missing_skills(resume_skills, NON_IT_SKILL_LIST)
            print("Resume Skills:", resume_skills)
            print("Missing Skills:", missing)

            X = nonit_coursecert_tfidf.transform([" ".join(missing)])
            course = nonit_course_model.predict(X)[0]
            cert = nonit_cert_model.predict(X)[0]

        print("Predicted Course:", course)
        print("Predicted Certificate:", cert)
        print("------------------------------------------")

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
        print("❌ Prediction Error:", str(e))
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    return render_template('index.html')


# Run server
if __name__ == "__main__":
    app.run(debug=True, port=5000)
