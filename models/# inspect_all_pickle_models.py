# inspect_pickle_models.py
# Utility script to load and inspect all .pkl model files in SmartCareer_Project

import joblib
import os
from pathlib import Path

# Path to the models folder
MODEL_DIR = Path("models")

# List of all model file names to inspect
model_files = [
    "IT_cert_model.pkl",
    "NonIT_cert_model.pkl",
    "IT_course_model.pkl",
    "NonIT_course_model.pkl",
    "IT_skill_model.pkl",
    "Non_IT_skill_model.pkl",
    "IT_job_role_model.pkl",
    "Non_IT_job_role_model.pkl",
    "IT_job_tfidf.pkl",
    "Non_IT_job_tfidf.pkl",
    "IT_tfidf.pkl",
    "Non_IT_tfidf.pkl",
    "IT_mlb.pkl",
    "Non_IT_mlb.pkl",
    "IT_coursecert_tfidf.pkl",
    "NonIT_coursecert_tfidf.pkl"
]

print("\n===== MODEL INSPECTOR =====\n")

for file_name in model_files:
    file_path = MODEL_DIR / file_name
    if not file_path.exists():
        print(f"❌ File not found: {file_name}\n")
        continue

    try:
        model = joblib.load(file_path)
        print(f"✅ Loaded: {file_name}")
        print("Type:", type(model))

        if hasattr(model, 'classes_'):
            print("Classes:", model.classes_[:10])

        if hasattr(model, 'coef_'):
            print("Coefficient shape:", model.coef_.shape)

        if hasattr(model, 'vocabulary_'):
            print("TF-IDF Vocabulary Size:", len(model.vocabulary_))

        print("---\n")

    except Exception as e:
        print(f"❌ Error loading {file_name}: {str(e)}\n")
