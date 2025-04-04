from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd
import re
import string
import spacy

app = Flask(__name__)
CORS(app)

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Load models and vectorizer
it_skill_model = joblib.load("models/it_skill_predictor.pkl")
nonit_skill_model = joblib.load("models/nonit_skill_predictor.pkl")
it_role_model = joblib.load("models/it_role_recommender.pkl")
nonit_role_model = joblib.load("models/nonit_role_recommender.pkl")
it_course_cert_model = joblib.load("models/it_course_cert_recommender.pkl")
nonit_course_cert_model = joblib.load("models/nonit_course_cert_recommender.pkl")
nonit_course_model = joblib.load("models/NonIT_course_model.pkl")
nonit_cert_model = joblib.load("models/NonIT_cert_model.pkl")
nonit_tfidf = joblib.load("models/NonIT_coursecert_tfidf.pkl")

# Define skill list used during training
SKILL_LIST = ['communication', 'excel', 'salesforce', 'customer support', 'team management', 'public speaking']

# Utility functions
def clean_text(text):
    text = re.sub(r"<[^>]+>", "", str(text))
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text

def lemmatize_text(text):
    doc = nlp(text)
    return " ".join([token.lemma_ for token in doc if not token.is_punct])

def extract_skills(text):
    return [skill for skill in SKILL_LIST if skill in text]

def get_missing_skills(resume_skills, required_skills_str):
    required_skills = [skill.strip().lower() for skill in str(required_skills_str).split(',')]
    return list(set(required_skills) - set(resume_skills))

def format_list_output(preds):
    return ", ".join(preds) if isinstance(preds, list) else preds

# Flask Routes
@app.route("/predict_skills_it", methods=["POST"])
def predict_skills_it():
    data = request.get_json()
    resume = data.get("resume", "")
    predicted_skills = it_skill_model.predict([resume])[0]
    return jsonify({"skills": format_list_output(predicted_skills)})

@app.route("/predict_skills_nonit", methods=["POST"])
def predict_skills_nonit():
    data = request.get_json()
    resume = data.get("resume", "")
    predicted_skills = nonit_skill_model.predict([resume])[0]
    return jsonify({"skills": format_list_output(predicted_skills)})

@app.route("/recommend_roles_it", methods=["POST"])
def recommend_roles_it():
    data = request.get_json()
    skills = data.get("skills", "")
    predicted_role = it_role_model.predict([skills])[0]
    return jsonify({"job_role": predicted_role})

@app.route("/recommend_roles_nonit", methods=["POST"])
def recommend_roles_nonit():
    data = request.get_json()
    skills = data.get("skills", "")
    predicted_role = nonit_role_model.predict([skills])[0]
    return jsonify({"job_role": predicted_role})

@app.route("/recommend_courses_cert_it", methods=["POST"])
def recommend_courses_cert_it():
    data = request.get_json()
    resume = data.get("resume", "")
    recommended = it_course_cert_model.predict([resume])[0]
    return jsonify({"recommendation": format_list_output(recommended)})

@app.route("/recommend_courses_cert_nonit", methods=["POST"])
def recommend_courses_cert_nonit():
    data = request.get_json()
    resume = data.get("resume", "")
    # Old non-ML pipeline using tfidf
    cleaned = lemmatize_text(clean_text(resume))
    resume_skills = extract_skills(cleaned)
    missing_skills = get_missing_skills(resume_skills, ", ".join(SKILL_LIST))
    X = nonit_tfidf.transform([" ".join(missing_skills)])
    course_pred = nonit_course_model.predict(X)[0]
    cert_pred = nonit_cert_model.predict(X)[0]
    return jsonify({
        "resume_skills": resume_skills,
        "missing_skills": missing_skills,
        "recommendation": f"Course: {course_pred}\nCertificate: {cert_pred}"
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)
