from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import re
import spacy

# Load pre-trained model
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

# Define required skills for job roles
job_required_skills = {
    "Data Science": {"python", "sql", "machine learning", "deep learning", "nlp", "pandas", "numpy"},
    "Software Developer": {"java", "c++", "javascript", "react", "nodejs", "html", "css"},
    "Cloud Engineer": {"aws", "azure", "gcp", "docker", "kubernetes", "cloud computing"},
}

def find_missing_skills(category, resume_skills):
    """Identify missing skills for a candidate."""
    required_skills = job_required_skills.get(category, set())
    return list(required_skills - set(resume_skills))

# Define course recommendations
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

# Flask API Setup
app = Flask(__name__)
CORS(app) 

@app.route('/recommend', methods=['POST'])
def recommend():
    """API endpoint to recommend missing skills and courses."""
    req_data = request.get_json()
    resume_text = req_data.get("resume", "")
    
    if not resume_text:
        return jsonify({"error": "Resume text is required"}), 400
    
    cleaned_text = clean_text(resume_text)
    predicted_category = loaded_pipeline.predict([cleaned_text])[0]
    extracted_skills = extract_skills(resume_text)
    missing_skills = find_missing_skills(predicted_category, extracted_skills)
    recommended_courses = recommend_courses(missing_skills)
    
    return jsonify({
        "Predicted_Job_Category": predicted_category,
        "Extracted_Skills": extracted_skills,
        "Missing_Skills": missing_skills,
        "Recommended_Courses": recommended_courses
    })

if __name__ == '__main__':
    app.run(debug=True)
