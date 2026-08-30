from flask import Flask, request, jsonify, render_template, send_file, make_response
from flask_cors import CORS
import joblib
import re
import string
import spacy
import fitz  # PyMuPDF
import io
import requests
import json
import os
from pdf2image import convert_from_bytes
import logging
import yake
from collections import Counter
from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
from recruiter_compat_routes import register_recruiter_compat_routes

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================
# FLASK APP INITIALIZATION
# ============================================
app = Flask(__name__)


# CORS Configuration
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
        response.headers.add("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS")
        return response

# Configure folders
app.config['UPLOAD_FOLDER'] = 'static/audio'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('static', exist_ok=True)

# ============================================
# MONGODB DATABASE CONFIGURATION
# ============================================
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
DB_NAME = os.getenv('DB_NAME', 'smartcareer_db')

try:
    mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    mongo_client.admin.command('ping')
    mongodb = mongo_client[DB_NAME]
    logger.info(f"✅ Connected to MongoDB: {DB_NAME}")
except Exception as e:
    logger.error(f"❌ MongoDB connection failed: {e}")
    mongodb = None

app.config['db'] = mongodb

# ============================================
# TESSERACT OCR CONFIGURATION
# ============================================
OCR_AVAILABLE = False
try:
    import pytesseract
    if os.name == 'nt':  # Windows
        tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        if os.path.exists(tesseract_path):
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
            OCR_AVAILABLE = True
    else:
        OCR_AVAILABLE = True
    logger.info("✅ Tesseract OCR available")
except ImportError:
    logger.warning("⚠️ pytesseract not installed")
except Exception as e:
    logger.warning(f"⚠️ Tesseract error: {e}")

# ============================================
# LOAD SPACY MODEL
# ============================================
try:
    nlp = spacy.load("en_core_web_sm")
    logger.info("✅ spaCy model loaded")
except OSError:
    logger.error("❌ spaCy model not found. Run: python -m spacy download en_core_web_sm")
    raise

# ============================================
# LOAD ML MODELS
# ============================================
MODEL_FILES = {
    'it_skill_model': 'models/IT_skill_model.pkl',
    'nonit_skill_model': 'models/Non_IT_skill_model.pkl',
    'it_tfidf': 'models/IT_tfidf.pkl',
    'nonit_tfidf': 'models/Non_IT_tfidf.pkl',
    'it_mlb': 'models/IT_mlb.pkl',
    'nonit_mlb': 'models/Non_IT_mlb.pkl',
    'it_role_model': 'models/IT_job_role_model.pkl',
    'nonit_role_model': 'models/Non_IT_job_role_model.pkl',
    'it_course_model': 'models/IT_course_model.pkl',
    'nonit_course_model': 'models/NonIT_course_model.pkl',
    'it_cert_model': 'models/IT_cert_model.pkl',
    'nonit_cert_model': 'models/NonIT_cert_model.pkl',
    'it_coursecert_tfidf': 'models/IT_coursecert_tfidf.pkl',
    'nonit_coursecert_tfidf': 'models/NonIT_coursecert_tfidf.pkl'
}

models = {}
for name, path in MODEL_FILES.items():
    try:
        models[name] = joblib.load(path)
        logger.info(f"✅ Loaded {name}")
    except FileNotFoundError:
        logger.warning(f"⚠️ Model not found: {path}")
        models[name] = None
    except Exception as e:
        logger.error(f"❌ Error loading {name}: {e}")
        models[name] = None

# ============================================
# SKILL LISTS
# ============================================
IT_SKILL_LIST = [
    'python', 'java', 'sql', 'machine learning', 'data analysis', 
    'react', 'c++', 'cloud computing', 'javascript', 'aws', 
    'docker', 'kubernetes', 'tensorflow', 'django', 'flask', 
    'nodejs', 'mongodb', 'postgresql', 'git', 'linux'
]

NON_IT_SKILL_LIST = [
    'communication', 'excel', 'salesforce', 'customer support', 
    'team management', 'public speaking', 'leadership', 
    'project management', 'negotiation', 'time management', 
    'problem solving', 'critical thinking', 'adaptability'
]

# ============================================
# UTILITY FUNCTIONS
# ============================================
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
    """Get skills missing from resume"""
    return list(set(required_skills) - set(resume_skills))

def detect_domain(text):
    """Detect if resume is IT or Non-IT"""
    text_lower = text.lower()
    it_score = sum(1 for skill in IT_SKILL_LIST if skill.lower() in text_lower)
    nonit_score = sum(1 for skill in NON_IT_SKILL_LIST if skill.lower() in text_lower)
    return "IT" if it_score >= nonit_score else "Non-IT"

def extract_text_from_pdf(file):
    """Extract text from PDF"""
    text = ""
    
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
            logger.info("✅ PDF extracted using PyMuPDF")
            return text.strip()
    except Exception as e:
        logger.warning(f"PyMuPDF failed: {e}")
    
    if OCR_AVAILABLE:
        try:
            file.seek(0)
            images = convert_from_bytes(file.read())
            for img in images:
                text += pytesseract.image_to_string(img) + "\n"
            
            if text.strip():
                logger.info("✅ PDF extracted using OCR")
                return text.strip()
        except Exception as e:
            logger.error(f"OCR failed: {e}")
    
    return text.strip() if text else "Unable to extract text from PDF"

def extract_keywords_from_text(text, max_keywords=20):
    """Extract keywords using YAKE"""
    try:
        kw_extractor = yake.KeywordExtractor(
            lan="en", n=2, dedupLim=0.9, top=max_keywords
        )
        keywords = kw_extractor.extract_keywords(text)
        return [kw[0] for kw in keywords]
    except:
        words = re.findall(r'\b[a-z]{3,}\b', text.lower())
        common_words = Counter(words).most_common(max_keywords)
        return [word for word, _ in common_words]

def optimize_resume_content(resume_text, job_description):
    """Optimize resume based on job description"""
    job_keywords = set(extract_keywords_from_text(job_description, 30))
    resume_words = set(re.findall(r'\b[a-z]{3,}\b', resume_text.lower()))
    
    matched_skills = job_keywords.intersection(resume_words)
    missing_keywords = job_keywords - resume_words
    top_skills = list(matched_skills)[:8]
    
    if top_skills:
        summary = (
            f"Results-driven professional with expertise in {', '.join(top_skills[:5])}. "
            f"Proven track record in delivering high-impact solutions."
        )
    else:
        summary = "Accomplished professional with strong technical background."
    
    return {
        'summary': summary,
        'matched_skills': list(matched_skills)[:15],
        'missing_keywords': list(missing_keywords)[:10],
        'match_score': int((len(matched_skills) / len(job_keywords)) * 100) if job_keywords else 0
    }

# ============================================
# REGISTER BLUEPRINTS (Replace this entire section)
# ============================================

# Flag to prevent double registration
_BLUEPRINTS_REGISTERED = False

def register_blueprints():
    """Register all blueprints once"""
    global _BLUEPRINTS_REGISTERED
    
    if _BLUEPRINTS_REGISTERED:
        logger.info("⚠️ Blueprints already registered, skipping...")
        return
    
    try:
        from interview_engine import interview_bp
        app.register_blueprint(interview_bp, url_prefix='/api/interview')
        logger.info("✅ Interview blueprint registered")
    except Exception as e:
        logger.error(f"❌ Interview blueprint error: {e}")
        import traceback
        traceback.print_exc()

    try:
        from recruiter_engine import recruiter_bp
        app.register_blueprint(recruiter_bp, url_prefix='/api/recruiter')
        logger.info("✅ Recruiter blueprint registered")
    except Exception as e:
        logger.error(f"❌ Recruiter blueprint error: {e}")
        import traceback
        traceback.print_exc()

    try:
        register_recruiter_compat_routes(app)
        logger.info("✅ Recruiter compat routes registered")
    except Exception as e:
        logger.error(f"❌ Recruiter compat routes error: {e}")

    _BLUEPRINTS_REGISTERED = True  

# Register blueprints
register_blueprints()

# Add these routes AFTER the blueprint registration section in app.py
# This provides backward compatibility for old frontend URLs

# ============================================
# BACKWARD COMPATIBILITY ROUTES (Interview)
# ============================================

@app.route('/start_interview', methods=['POST'])
def start_interview_compat():
    """Backward compatibility route - redirects to blueprint"""
    from interview_engine import start_interview
    return start_interview()

@app.route('/get_next_question', methods=['POST'])
def get_next_question_compat():
    """Backward compatibility route"""
    from interview_engine import get_next_question
    return get_next_question()

@app.route('/submit_answer', methods=['POST'])
def submit_answer_compat():
    """Backward compatibility route"""
    from interview_engine import submit_answer
    return submit_answer()

@app.route('/end_interview', methods=['POST'])
def end_interview_compat():
    """Backward compatibility route"""
    from interview_engine import end_interview
    return end_interview()

@app.route('/get_interview_history', methods=['POST'])
def get_interview_history():
    """Get interview history for a user"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'guest')
        
        if mongodb is None:
            return jsonify({'error': 'Database not available'}), 500
        
        # Fetch interview history from completed_sessions or database
        history = []
        
        # Try to get from database if you have an interviews collection
        try:
            interviews = list(mongodb.interviews.find(
                {'user_id': user_id}
            ).sort('start_time', -1).limit(20))
            
            for interview in interviews:
                interview['_id'] = str(interview['_id'])
                history.append(interview)
        except Exception as e:
            logger.warning(f"Could not fetch interview history: {e}")
        
        return jsonify({
            'history': history,
            'total': len(history)
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching interview history: {e}")
        return jsonify({'error': str(e)}), 500
    
    
# ============================================
# ROUTES - HOME & HEALTH
# ============================================
@app.route("/")
def home():
    try:
        return render_template("index.html")
    except:
        return jsonify({
            "message": "SmartCareer API",
            "version": "1.0.0",
            "status": "running"
        })

@app.route("/health")
@app.route("/api/health")
def health():
    return jsonify({
        "status": "healthy",
        "ocr_available": OCR_AVAILABLE,
        "database": "connected" if mongodb is not None else "disconnected",
        "models_loaded": sum(1 for m in models.values() if m is not None)
    })

# ============================================
# ROUTES - RESUME ANALYSIS
# ============================================
@app.route("/detect_domain", methods=["POST"])
def detect_resume_domain():
    """Detect resume domain"""
    if "resume" not in request.files:
        return jsonify({"error": "No resume uploaded"}), 400
    
    file = request.files["resume"]
    if not file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Only PDF files supported"}), 400
    
    try:
        text = extract_text_from_pdf(file)
        if not text or text == "Unable to extract text from PDF":
            return jsonify({"error": "Could not extract text"}), 400
        
        cleaned = lemmatize(clean_text(text))
        domain = detect_domain(cleaned)
        
        return jsonify({
            "domain": domain,
            "cleaned_text": cleaned[:500] + "...",
            "message": f"Resume belongs to {domain} domain"
        })
    except Exception as e:
        logger.error(f"Error in detect_domain: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/proceed_prediction", methods=["POST"])
def proceed_prediction():
    """Make predictions based on resume content"""
    # Check file upload
    if "resume" not in request.files:
        return jsonify({"error": "No resume file uploaded."}), 400
    
    file = request.files["resume"]
    
    # Check filename exists
    if not file.filename:
        return jsonify({"error": "Invalid file."}), 400
    
    # Check PDF format
    if not file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Only PDF files are supported."}), 400
    
    try:
        # Extract text
        text = extract_text_from_pdf(file)
        if not text or text == "Unable to extract text from PDF":
            return jsonify({"error": "Could not extract text from PDF."}), 400
        
        # Clean and preprocess
        cleaned = lemmatize(clean_text(text))
        if not cleaned or len(cleaned.strip()) == 0:
            return jsonify({"error": "No valid text content found in resume."}), 400
        
        # Unpack models from dict
        it_tfidf            = models.get('it_tfidf')
        nonit_tfidf         = models.get('nonit_tfidf')
        it_skill_model      = models.get('it_skill_model')
        nonit_skill_model   = models.get('nonit_skill_model')
        it_mlb              = models.get('it_mlb')
        nonit_mlb           = models.get('nonit_mlb')
        it_role_model       = models.get('it_role_model')
        nonit_role_model    = models.get('nonit_role_model')
        it_course_model     = models.get('it_course_model')
        nonit_course_model  = models.get('nonit_course_model')
        it_cert_model       = models.get('it_cert_model')
        nonit_cert_model    = models.get('nonit_cert_model')
        it_coursecert_tfidf   = models.get('it_coursecert_tfidf')
        nonit_coursecert_tfidf = models.get('nonit_coursecert_tfidf')

        # Check all required models are loaded
        required = {
            'it_tfidf': it_tfidf, 'nonit_tfidf': nonit_tfidf,
            'it_skill_model': it_skill_model, 'nonit_skill_model': nonit_skill_model,
        }
        missing_models = [k for k, v in required.items() if v is None]
        if missing_models:
            return jsonify({"error": f"ML models not loaded: {missing_models}. Run the app from the correct directory."}), 500

        # Detect domain
        domain = detect_domain(cleaned)
        app.logger.info(f"Domain detected: {domain}")
        
        # Domain-specific prediction
        if domain == "IT":
            # Skill prediction
            vec = it_tfidf.transform([cleaned])
            pred = it_skill_model.predict(vec)
            skills = it_mlb.inverse_transform(pred)[0]
            
            # Role prediction - FIX: handle empty skills
            skills_text = " ".join(skills) if skills else "general"
            role = it_role_model.predict(it_tfidf.transform([skills_text]))[0]
            
            # Extract and compare skills
            resume_skills = extract_skills(cleaned, IT_SKILL_LIST)
            missing = get_missing_skills(resume_skills, IT_SKILL_LIST)
            
            # Course/cert recommendation
            missing_text = " ".join(missing) if missing else "general"
            x_vec = it_coursecert_tfidf.transform([missing_text])
            course = it_course_model.predict(x_vec)[0]
            cert = it_cert_model.predict(x_vec)[0]
            
        else:  # Non-IT domain
            # Skill prediction
            vec = nonit_tfidf.transform([cleaned])
            pred = nonit_skill_model.predict(vec)
            skills = nonit_mlb.inverse_transform(pred)[0]
            
            # Role prediction - FIX: handle empty skills
            skills_text = " ".join(skills) if skills else "general"
            role = nonit_role_model.predict(nonit_tfidf.transform([skills_text]))[0]
            
            # Extract and compare skills
            resume_skills = extract_skills(cleaned, NON_IT_SKILL_LIST)
            missing = get_missing_skills(resume_skills, NON_IT_SKILL_LIST)
            
            # Course/cert recommendation
            missing_text = " ".join(missing) if missing else "general"
            x_vec = nonit_coursecert_tfidf.transform([missing_text])
            course = nonit_course_model.predict(x_vec)[0]
            cert = nonit_cert_model.predict(x_vec)[0]
        
        # Return response
        return jsonify({
            "domain": domain,
            "predicted_skills": ", ".join(skills) if skills else "No specific skills predicted",
            "resume_skills": resume_skills if resume_skills else [],
            "missing_skills": missing if missing else [],
            "predicted_role": role,
            "recommendation": {
                "course": course,
                "certificate": cert
            }
        }), 200
        
    except AttributeError as ae:
        app.logger.error(f"Model not loaded properly: {ae}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": "System models not initialized. Please contact support."}), 500
        
    except Exception as e:
        app.logger.error(f"Error in proceed_prediction: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# ============================================
# ROUTES - JOB SCRAPING
# ============================================
@app.route("/scrape-jobs", methods=["POST"])
def scrape_jobs():
    """Scrape jobs from Adzuna"""
    data = request.get_json() or {}
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
        "what": job_role
    }
    
    if location and location.lower() != "remote":
        params["where"] = location
    
    if salary_min.isdigit() and int(salary_min) >= 10000:
        params["salary_min"] = salary_min
    
    try:
        response = requests.get(base_url, params=params, timeout=10)
        if response.status_code != 200:
            return jsonify({"error": f"API error: {response.status_code}"}), response.status_code
        
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
        logger.error(f"Job scraping error: {e}")
        return jsonify({"error": str(e)}), 500

# ============================================
# ROUTES - RESUME OPTIMIZATION
# ============================================
@app.route('/optimize_resume', methods=['POST'])
def optimize_resume():
    """Optimize resume"""
    if 'resume' not in request.files:
        return jsonify({"error": "No resume uploaded"}), 400
    
    resume_file = request.files['resume']
    job_description = request.form.get('job_description', '')
    
    try:
        resume_text = extract_text_from_pdf(resume_file)
        
        if not resume_text or resume_text == "Unable to extract text from PDF":
            return jsonify({"error": "Could not extract text"}), 400
        
        try:
            from models.resume_parser import ResumeParser
            from models.fixed_template_renderer import FixedTemplateRenderer
        except ImportError as e:
            logger.error(f"Import error: {e}")
            return jsonify({"error": "Resume parser not available"}), 500
        
        parser = ResumeParser()
        parsed_data = parser.parse_resume(resume_text)
        
        if job_description:
            cleaned_text = clean_text(resume_text)
            optimization = optimize_resume_content(cleaned_text, job_description)
            summary = optimization['summary']
        else:
            summary = "Experienced professional with strong technical background."
        
        optimized_resume = {
            "personal_info": parsed_data.get('personal_info', {}),
            "professional_summary": summary,
            "education": parsed_data.get('education', []),
            "experience": parsed_data.get('experience', []),
            "projects": parsed_data.get('projects', []),
            "skills": parsed_data.get('skills', []),
            "certifications": parsed_data.get('certifications', []),
            "achievements": parsed_data.get('achievements', []),
            "research": parsed_data.get('research', [])
        }
        
        renderer = FixedTemplateRenderer()
        pdf_path = renderer.render_resume(optimized_resume)
        
        return send_file(pdf_path, as_attachment=True, download_name="optimized_resume.pdf")
    except Exception as e:
        logger.error(f"Resume optimization error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/check_ats_score', methods=['POST'])
def check_ats_score():
    """Check ATS score"""
    if 'resume' not in request.files:
        return jsonify({"error": "No resume uploaded"}), 400
    
    resume_file = request.files['resume']
    job_description = request.form.get('job_description', '')
    
    if not job_description:
        return jsonify({"error": "Job description required"}), 400
    
    try:
        resume_text = extract_text_from_pdf(resume_file)
        
        if not resume_text or resume_text == "Unable to extract text from PDF":
            return jsonify({"error": "Could not extract text"}), 400
        
        cleaned_resume = clean_text(resume_text)
        cleaned_jd = clean_text(job_description)
        
        jd_keywords = set(extract_keywords_from_text(job_description, 30))
        resume_keywords = set(extract_keywords_from_text(resume_text, 30))
        matched_keywords = jd_keywords.intersection(resume_keywords)
        
        keyword_match_score = int((len(matched_keywords) / len(jd_keywords)) * 100) if jd_keywords else 0
        
        domain = detect_domain(cleaned_resume)
        skill_list = IT_SKILL_LIST if domain == "IT" else NON_IT_SKILL_LIST
        
        resume_skills = extract_skills(cleaned_resume, skill_list)
        jd_skills = extract_skills(cleaned_jd, skill_list)
        
        matched_skills = list(set(resume_skills).intersection(set(jd_skills)))
        skill_match_score = int((len(matched_skills) / len(jd_skills)) * 100) if jd_skills else 0
        
        format_score = 100
        has_email = bool(re.search(r'[\w\.-]+@[\w\.-]+\.\w+', resume_text))
        has_phone = bool(re.search(r'(?:\+\d{1,3}|\d{3})[.\s-]?\d{3}[.\s-]?\d{4}', resume_text))
        has_linkedin = bool(re.search(r'linkedin\.com/in/[\w\-]+', resume_text, re.IGNORECASE))
        
        if not has_email: format_score -= 15
        if not has_phone: format_score -= 15
        if not has_linkedin: format_score -= 10
        
        word_count = len(resume_text.split())
        if word_count < 250: format_score -= 20
        elif word_count > 1500: format_score -= 15
        
        completeness_score = 75
        if re.search(r'education|degree', cleaned_resume, re.IGNORECASE):
            completeness_score += 10
        if re.search(r'experience|worked', cleaned_resume, re.IGNORECASE):
            completeness_score += 10
        if re.search(r'skill|proficient', cleaned_resume, re.IGNORECASE):
            completeness_score += 5
        
        completeness_score = min(100, completeness_score)
        
        overall_score = int(
            (keyword_match_score * 0.40) +
            (skill_match_score * 0.25) +
            (format_score * 0.20) +
            (completeness_score * 0.15)
        )
        
        suggestions = []
        if keyword_match_score < 50:
            missing = list(jd_keywords - resume_keywords)[:5]
            suggestions.append({
                "type": "warning",
                "message": f"⚠️ Low keyword match ({keyword_match_score}%). Add: {', '.join(missing)}"
            })
        
        if not has_email or not has_phone:
            suggestions.append({
                "type": "warning",
                "message": "📞 Add missing contact information"
            })
        
        return jsonify({
            "ats_score": overall_score,
            "score_breakdown": {
                "keyword_match": keyword_match_score,
                "skill_alignment": skill_match_score,
                "formatting": format_score,
                "completeness": completeness_score
            },
            "matched_skills": matched_skills[:10],
            "missing_skills": list(set(jd_skills) - set(resume_skills))[:10],
            "matched_keywords": list(matched_keywords)[:15],
            "suggestions": suggestions,
            "domain_detected": domain
        })
    except Exception as e:
        logger.error(f"ATS check error: {e}")
        return jsonify({"error": str(e)}), 500

# ============================================
# ROUTES - MOCK TEST (MySQL SINGLE TABLE)
# ============================================
from flask import jsonify, request
import mysql.connector
from datetime import datetime

def get_mysql_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='fcp@123',  # update this
        database='smartcareer'
    )

# ✅ Fetch subjects and difficulties
@app.route('/api/get_subjects', methods=['GET'])
def get_subjects():
    try:
        subjects = ["Python", "SQL", "Machine Learning", "Deep Learning", "Aptitude", "Excel"]
        difficulties = ["Easy", "Medium", "Hard"]
        return jsonify({"subjects": subjects, "difficulties": difficulties})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/get_questions', methods=['POST'])
def get_questions():
    conn = None
    cursor = None
    try:
        data = request.get_json()
        subject = data.get("subject")
        difficulty = data.get("difficulty")

        if not subject:
            return jsonify({"error": "Subject required"}), 400

        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM questions WHERE subject = %s"
        params = [subject]

        if difficulty:
            query += " AND difficulty = %s"
            params.append(difficulty)

        query += " ORDER BY RAND() LIMIT 10"
        cursor.execute(query, params)
        questions = cursor.fetchall()

        if not questions:
            return jsonify({"error": "No questions found"}), 404

        formatted_questions = []
        for q in questions:
            formatted_questions.append({
                "id": q["id"],
                "subject": q["subject"],
                "question": q["question_text"],
                "options": {
                    "A": q["option_a"],
                    "B": q["option_b"],
                    "C": q["option_c"],
                    "D": q["option_d"]
                },
                "difficulty": q["difficulty"]
            })

        return jsonify({
            "questions": formatted_questions,
            "total": len(formatted_questions),
            "time_limit": 600
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()



@app.route('/api/submit_test', methods=['POST'])
def submit_test():
    """Submit test and store results in MySQL"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'guest')
        subject = data.get('subject')
        answers = data.get('answers', {})
        time_taken = data.get('time_taken', 0)

        if not subject or not answers:
            return jsonify({"error": "Subject and answers required"}), 400

        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)

        # Fetch questions from MySQL
        placeholders = ','.join(['%s'] * len(answers))
        query = f"SELECT id, question_text, correct_option FROM questions WHERE id IN ({placeholders})"
        cursor.execute(query, list(answers.keys()))
        questions = cursor.fetchall()

        score = 0
        results = []

        for q in questions:
            q_id = str(q['id'])
            user_answer = answers.get(q_id, '')
            correct_answer = q['correct_option']
            is_correct = user_answer.upper() == correct_answer.upper()
            if is_correct:
                score += 1
            results.append({
                "question_id": q_id,
                "question": q['question_text'],
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "is_correct": is_correct
            })

        total = len(questions)
        percentage = (score / total * 100) if total > 0 else 0

        # Store test attempt in MySQL
        insert_query = """
            INSERT INTO test_attempts (user_id, subject, score, total_questions, percentage, time_taken)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (user_id, subject, score, total, percentage, time_taken))
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({
            "score": score,
            "total": total,
            "percentage": round(percentage, 2),
            "results": results,
            "time_taken": time_taken,
            "passed": percentage >= 60
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/test_history/<user_id>', methods=['GET'])
def get_test_history(user_id):
    """Get test history from MySQL"""
    try:
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT subject, score, total_questions, percentage, time_taken, timestamp
            FROM test_attempts
            WHERE user_id = %s
            ORDER BY timestamp DESC
            LIMIT 20
        """, (user_id,))
        rows = cursor.fetchall()

        history = []
        for row in rows:
            history.append({
                "subject": row["subject"],
                "score": row["score"],
                "total_questions": row["total_questions"],
                "percentage": row["percentage"],
                "time_taken": row["time_taken"],
                "timestamp": row["timestamp"].isoformat() if row["timestamp"] else None
            })

        stats = {
            "total_tests": len(history),
            "average_score": round(sum(r["percentage"] for r in history) / len(history), 2) if history else 0,
            "subjects_attempted": list(set(r["subject"] for r in history))
        }

        return jsonify({"history": history, "stats": stats})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


# ============================================
# ROUTES - AUTH
# ============================================
@app.route('/api/auth/register', methods=['POST'])
def register():
    """User registration"""
    if mongodb is None:
        return jsonify({"error": "Database not connected"}), 500
    
    try:
        data = request.json
        
        required_fields = ['name', 'email', 'password', 'role']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400
        
        existing_user = mongodb.users.find_one({'email': data['email']})
        if existing_user:
            return jsonify({'error': 'User already exists'}), 409
        
        user = {
            'name': data['name'],
            'email': data['email'],
            'password': data['password'],  # TODO: Hash in production!
            'role': data['role'],
            'phone': data.get('phone', ''),
            'company': data.get('company', ''),
            'createdAt': datetime.utcnow()
        }
        
        result = mongodb.users.insert_one(user)
        
        return jsonify({
            'message': 'User registered successfully',
            'userId': str(result.inserted_id)
        }), 201
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login"""
    if mongodb is None:
        return jsonify({"error": "Database not connected"}), 500
    
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        
        user = mongodb.users.find_one({'email': email, 'password': password})
        
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': str(user['_id']),
                'name': user['name'],
                'email': user['email'],
                'role': user['role'],
                'company': user.get('company', '')
            }
        }), 200
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================
# ROUTES - RECRUITER
# ============================================

@app.route('/api/recruiter/post-job', methods=['POST'])
def post_job():
    """Post a new job"""
    if mongodb is None:
        return jsonify({"error": "Database not connected"}), 500
    
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['title', 'company', 'location', 'type', 'description', 'requirements', 'recruiterId']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create job document
        job = {
            'title': data['title'],
            'company': data['company'],
            'location': data['location'],
            'type': data['type'],
            'experience': data.get('experience', ''),
            'salary': data.get('salary', ''),
            'description': data['description'],
            'requirements': data['requirements'],
            'skills': data.get('skills', []),
            'recruiterId': data['recruiterId'],
            'status': 'active',
            'applicants': [],
            'createdAt': datetime.utcnow(),
            'updatedAt': datetime.utcnow()
        }
        
        result = mongodb.jobs.insert_one(job)
        job['_id'] = str(result.inserted_id)
        job['createdAt'] = job['createdAt'].isoformat()
        job['updatedAt'] = job['updatedAt'].isoformat()
        
        return jsonify({
            'message': 'Job posted successfully',
            'job': job
        }), 201
        
    except Exception as e:
        logger.error(f"Job posting error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/recruiter/jobs/<recruiter_id>', methods=['GET'])
def get_recruiter_jobs(recruiter_id):
    """Get all jobs posted by a recruiter"""
    if mongodb is None:
        return jsonify({"error": "Database not connected"}), 500
    
    try:
        jobs = list(mongodb.jobs.find({'recruiterId': recruiter_id}).sort('createdAt', -1))
        
        for job in jobs:
            job['_id'] = str(job['_id'])
            job['createdAt'] = job['createdAt'].isoformat() if 'createdAt' in job else None
            job['updatedAt'] = job['updatedAt'].isoformat() if 'updatedAt' in job else None
            job['applicantCount'] = len(job.get('applicants', []))
        
        return jsonify({'jobs': jobs, 'count': len(jobs)}), 200
        
    except Exception as e:
        logger.error(f"Get recruiter jobs error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/recruiter/job/<job_id>', methods=['GET'])
def get_job_details(job_id):
    """Get job details by ID"""
    if mongodb is None:
        return jsonify({"error": "Database not connected"}), 500
    
    try:
        job = mongodb.jobs.find_one({'_id': ObjectId(job_id)})
        
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        job['_id'] = str(job['_id'])
        job['createdAt'] = job['createdAt'].isoformat() if 'createdAt' in job else None
        job['updatedAt'] = job['updatedAt'].isoformat() if 'updatedAt' in job else None
        job['applicantCount'] = len(job.get('applicants', []))
        
        return jsonify({'job': job}), 200
        
    except Exception as e:
        logger.error(f"Get job details error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/recruiter/job/<job_id>', methods=['PUT'])
def update_job(job_id):
    """Update job details"""
    if mongodb is None:
        return jsonify({"error": "Database not connected"}), 500
    
    try:
        data = request.json
        data['updatedAt'] = datetime.utcnow()
        
        result = mongodb.jobs.update_one(
            {'_id': ObjectId(job_id)},
            {'$set': data}
        )
        
        if result.matched_count == 0:
            return jsonify({'error': 'Job not found'}), 404
        
        return jsonify({'message': 'Job updated successfully'}), 200
        
    except Exception as e:
        logger.error(f"Update job error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/recruiter/job/<job_id>', methods=['DELETE'])
def delete_job(job_id):
    """Delete a job"""
    if mongodb is None:
        return jsonify({"error": "Database not connected"}), 500
    
    try:
        result = mongodb.jobs.delete_one({'_id': ObjectId(job_id)})
        
        if result.deleted_count == 0:
            return jsonify({'error': 'Job not found'}), 404
        
        return jsonify({'message': 'Job deleted successfully'}), 200
        
    except Exception as e:
        logger.error(f"Delete job error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/recruiter/search-candidates', methods=['GET'])
def search_candidates():
    """Search candidates by skills and experience"""
    if mongodb is None:
        return jsonify({"error": "Database not connected"}), 500
    
    try:
        skills = request.args.get('skills', '')
        experience = request.args.get('experience', '')
        location = request.args.get('location', '')
        
        filters = {'role': 'candidate'}
        
        if skills:
            filters['skills'] = {'$regex': skills, '$options': 'i'}
        
        if experience:
            filters['experience'] = {'$regex': experience, '$options': 'i'}
        
        if location:
            filters['location'] = {'$regex': location, '$options': 'i'}
        
        candidates = list(mongodb.users.find(filters).limit(50))
        
        for candidate in candidates:
            candidate['_id'] = str(candidate['_id'])
            # Remove sensitive information
            candidate.pop('password', None)
        
        return jsonify({'candidates': candidates, 'count': len(candidates)}), 200
        
    except Exception as e:
        logger.error(f"Search candidates error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/recruiter/match-resume', methods=['POST'])
def match_resume():
    """Match resume with job description"""
    if mongodb is None:
        return jsonify({"error": "Database not connected"}), 500
    
    try:
        data = request.json
        job_description = data.get('jobDescription', '')
        resume_text = data.get('resumeText', '')
        
        if not job_description or not resume_text:
            return jsonify({'error': 'Job description and resume text required'}), 400
        
        # Simple keyword matching (you can enhance this with NLP)
        job_keywords = set(job_description.lower().split())
        resume_keywords = set(resume_text.lower().split())
        
        matching_keywords = job_keywords.intersection(resume_keywords)
        match_percentage = (len(matching_keywords) / len(job_keywords)) * 100 if job_keywords else 0
        
        return jsonify({
            'matchPercentage': round(match_percentage, 2),
            'matchingKeywords': list(matching_keywords)[:10],
            'feedback': 'Good match' if match_percentage > 60 else 'Moderate match' if match_percentage > 30 else 'Low match'
        }), 200
        
    except Exception as e:
        logger.error(f"Resume matching error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/recruiter/shortlist', methods=['POST'])
def add_to_shortlist():
    """Add candidate to shortlist"""
    if mongodb is None:
        return jsonify({"error": "Database not connected"}), 500
    
    try:
        data = request.json
        
        shortlist = {
            'candidateId': data['candidateId'],
            'jobId': data['jobId'],
            'recruiterId': data['recruiterId'],
            'status': data.get('status', 'shortlisted'),
            'notes': data.get('notes', ''),
            'createdAt': datetime.utcnow()
        }
        
        result = mongodb.shortlist.insert_one(shortlist)
        shortlist['_id'] = str(result.inserted_id)
        shortlist['createdAt'] = shortlist['createdAt'].isoformat()
        
        return jsonify({
            'message': 'Candidate added to shortlist',
            'shortlist': shortlist
        }), 201
        
    except Exception as e:
        logger.error(f"Add to shortlist error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/recruiter/shortlist/<recruiter_id>', methods=['GET'])
def get_shortlist(recruiter_id):
    """Get recruiter's shortlisted candidates"""
    if mongodb is None:
        return jsonify({"error": "Database not connected"}), 500
    
    try:
        shortlist = list(mongodb.shortlist.find({'recruiterId': recruiter_id}).sort('createdAt', -1))
        
        # Populate candidate and job details
        for item in shortlist:
            item['_id'] = str(item['_id'])
            item['createdAt'] = item['createdAt'].isoformat() if 'createdAt' in item else None
            
            # Get candidate details
            candidate = mongodb.users.find_one({'_id': ObjectId(item['candidateId'])})
            if candidate:
                candidate.pop('password', None)
                candidate['_id'] = str(candidate['_id'])
                item['candidate'] = candidate
            
            # Get job details
            job = mongodb.jobs.find_one({'_id': ObjectId(item['jobId'])})
            if job:
                job['_id'] = str(job['_id'])
                item['job'] = job
        
        return jsonify({'shortlist': shortlist, 'count': len(shortlist)}), 200
        
    except Exception as e:
        logger.error(f"Get shortlist error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/recruiter/shortlist/<shortlist_id>', methods=['DELETE'])
def remove_from_shortlist(shortlist_id):
    """Remove candidate from shortlist"""
    if mongodb is None:
        return jsonify({"error": "Database not connected"}), 500
    
    try:
        result = mongodb.shortlist.delete_one({'_id': ObjectId(shortlist_id)})
        
        if result.deleted_count == 0:
            return jsonify({'error': 'Shortlist entry not found'}), 404
        
        return jsonify({'message': 'Removed from shortlist'}), 200
        
    except Exception as e:
        logger.error(f"Remove from shortlist error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/recruiter/dashboard/<recruiter_id>', methods=['GET'])
def get_recruiter_dashboard(recruiter_id):
    """Get recruiter dashboard statistics"""
    if mongodb is None:
        return jsonify({"error": "Database not connected"}), 500
    
    try:
        # Get counts
        total_jobs = mongodb.jobs.count_documents({'recruiterId': recruiter_id})
        active_jobs = mongodb.jobs.count_documents({'recruiterId': recruiter_id, 'status': 'active'})
        total_shortlisted = mongodb.shortlist.count_documents({'recruiterId': recruiter_id})
        
        # Get recent jobs
        recent_jobs = list(mongodb.jobs.find({'recruiterId': recruiter_id})
                          .sort('createdAt', -1)
                          .limit(5))
        
        for job in recent_jobs:
            job['_id'] = str(job['_id'])
            job['createdAt'] = job['createdAt'].isoformat() if 'createdAt' in job else None
            job['applicantCount'] = len(job.get('applicants', []))
        
        return jsonify({
            'stats': {
                'totalJobs': total_jobs,
                'activeJobs': active_jobs,
                'totalShortlisted': total_shortlisted
            },
            'recentJobs': recent_jobs
        }), 200
        
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        return jsonify({'error': str(e)}), 500
    
# ============================================
# RUN APP
# ============================================
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV', 'development') == 'development'
    
    logger.info(f"🚀 SmartCareer API starting on port {port}")
    logger.info(f"📊 Database: {DB_NAME}")
    logger.info(f"🔧 Debug mode: {debug}")
    logger.info(f"📁 OCR Available: {OCR_AVAILABLE}")
    
    # Disable reloader to prevent double registration
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug,
        threaded=True,
        use_reloader=False  # This prevents the double registration issue
    )