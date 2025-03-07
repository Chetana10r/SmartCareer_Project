from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import re
import spacy
from PyPDF2 import PdfReader
from sklearn.metrics.pairwise import cosine_similarity

# Load pre-trained model (used here only for TF-IDF vectorizer)
with open("resume_model.pkl", "rb") as model_file:
    loaded_pipeline = pickle.load(model_file)

# Load NLP model for skill extraction
nlp = spacy.load("en_core_web_sm")

# Define common skills
common_skills = {"python", "java", "c++", "sql", "machine learning", "deep learning", "nlp",
                 "pandas", "numpy", "tensorflow", "pytorch", "cloud computing", "aws", "azure",
                 "gcp", "javascript", "react", "nodejs", "html", "css", "docker", "kubernetes",
                 "power bi", "tableau", "excel", "big data", "hadoop", "spark", "mongodb"}

def clean_text(text):
    text = re.sub(r'[^a-zA-Z ]', '', text)
    return text.lower()

def extract_skills(text):
    """Extract skills from resume."""
    text = str(text).lower()
    skills = {skill for skill in common_skills if skill in text}
    return list(skills)

# Define required skills for each job role
job_required_skills = {
    "Data Science": {"python", "sql", "machine learning", "deep learning", "nlp", "pandas", "numpy"},
    "Software Developer": {"java", "c++", "javascript", "react", "nodejs", "html", "css"},
    "Cloud Engineer": {"aws", "azure", "gcp", "docker", "kubernetes", "cloud computing"},
}

def find_missing_skills(role, resume_skills):
    """Identify missing skills based on the provided job role."""
    required_skills = job_required_skills.get(role, set())
    return list(required_skills - set(resume_skills))

# Define course recommendations based on missing skills
course_recommendations = {
    "python": "Python for Everybody - Coursera",
    "sql": "SQL for Data Science - Udacity",
    "machine learning": "Machine Learning Specialization - Coursera",
    "deep learning": "Deep Learning with TensorFlow - Udemy",
    "nlp": "Natural Language Processing - Stanford",
    "pandas": "Data Analysis with Pandas - Kaggle",
    "numpy": "Numerical Computing with NumPy - Coursera",
    "java": "Java Programming Masterclass - Udemy",
    "c++": "C++ Complete Guide - Pluralsight",
    "javascript": "JavaScript Essentials - Codecademy",
    "react": "React - The Complete Guide - Udemy",
    "nodejs": "Node.js for Beginners - Udemy",
    "html": "HTML & CSS - W3Schools",
    "css": "CSS Basics - W3Schools",
    "aws": "AWS Certified Solutions Architect - Coursera",
    "azure": "Microsoft Azure Fundamentals - Udemy",
    "gcp": "Google Cloud Platform Training - Coursera",
    "docker": "Docker for Developers - Pluralsight",
    "kubernetes": "Kubernetes Mastery - Udemy",
    "cloud computing": "Cloud Computing Fundamentals - Coursera",
}

def recommend_courses(missing_skills):
    """Recommend courses based on missing skills."""
    return [course_recommendations[skill] for skill in missing_skills if skill in course_recommendations]

# -------------------------
# New: Using Cosine Similarity for Job Role Prediction
# -------------------------
# Define reference texts for each job role based on required skills
job_reference_text = {
    "Data Science": "python sql machine learning deep learning nlp pandas numpy",
    "Software Developer": "java c++ javascript react nodejs html css",
    "Cloud Engineer": "aws azure gcp docker kubernetes cloud computing"
}

# Retrieve the vectorizer from the loaded pipeline
vectorizer = loaded_pipeline.named_steps['tfidf']

def predict_role_by_cosine(resume_text, vectorizer, job_reference_text):
    """Predict the job role using cosine similarity between the resume text and reference texts."""
    resume_vector = vectorizer.transform([resume_text])
    similarities = {}
    for role, ref_text in job_reference_text.items():
        ref_vector = vectorizer.transform([ref_text])
        sim = cosine_similarity(resume_vector, ref_vector)[0][0]
        similarities[role] = sim
    best_role = max(similarities, key=similarities.get)
    return best_role, similarities

# -------------------------
# Flask API Setup
# -------------------------
app = Flask(__name__)
CORS(app)  # Allow cross-origin requests

@app.route('/upload', methods=['POST'])
def upload():
    """
    API endpoint to accept a PDF resume file and a job role.
    It extracts the resume text, uses cosine similarity to predict the job role,
    and then computes missing skills and recommends courses.
    """
    if 'resume' not in request.files:
        return jsonify({"error": "No resume file provided"}), 400
    resume_file = request.files['resume']
    if resume_file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    # Get the user-provided job role from the form data
    user_job_role = request.form.get("job_role", "")
    if not user_job_role:
        return jsonify({"error": "Job role is required"}), 400

    # Process the PDF file
    if resume_file.filename.lower().endswith('.pdf'):
        try:
            reader = PdfReader(resume_file)
            resume_text = ""
            for page in reader.pages:
                page_text = page.extract_text() or ""
                print("Extracted text from page:", page_text)  # Debug print
                resume_text += page_text
            if not resume_text.strip():
                return jsonify({"error": "No extractable text found in the PDF. Please upload a text-based PDF."}), 400
        except Exception as e:
            print("Error processing PDF:", e)
            return jsonify({"error": "Error processing PDF file: " + str(e)}), 400
    else:
        return jsonify({"error": "Only PDF files are supported"}), 400


    # Clean the extracted resume text
    cleaned_text = clean_text(resume_text)
    
    # Use cosine similarity to predict the job role based on resume content
    predicted_category, similarity_scores = predict_role_by_cosine(cleaned_text, vectorizer, job_reference_text)

    # For missing skills, you can choose either the predicted role or the one provided by the user.
    # Here, we show both. We'll use the user provided role for computing missing skills.
    used_role = user_job_role

    extracted_skills = extract_skills(resume_text)
    missing_skills = find_missing_skills(used_role, extracted_skills)
    recommended_courses = recommend_courses(missing_skills)
    recommended_certifications = []  # Placeholder for certifications if available

    return jsonify({
        "User_Provided_Job_Role": user_job_role,
        "Predicted_Job_Category": predicted_category,
        "Similarity_Scores": similarity_scores,
        "Extracted_Skills": extracted_skills,
        "Missing_Skills": missing_skills,
        "Recommended_Courses": recommended_courses,
        "Recommended_Certifications": recommended_certifications
    })

if __name__ == '__main__':
    app.run(debug=True)
