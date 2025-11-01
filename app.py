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
# REGISTER BLUEPRINTS
# ============================================
try:
    from interview_engine import interview_bp
    app.register_blueprint(interview_bp, url_prefix='/api/interview')
    logger.info("✅ Interview blueprint registered")
except Exception as e:
    logger.warning(f"⚠️ Interview blueprint error: {e}")

try:
    from recruiter_engine import recruiter_bp
    app.register_blueprint(recruiter_bp, url_prefix='/api/recruiter')
    logger.info("✅ Recruiter blueprint registered")
except Exception as e:
    logger.warning(f"⚠️ Recruiter blueprint error: {e}")

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
    """Make predictions"""
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
        
        if domain == "IT":
            if not all([models['it_tfidf'], models['it_skill_model']]):
                return jsonify({"error": "IT models not loaded"}), 500
            
            vec = models['it_tfidf'].transform([cleaned])
            pred = models['it_skill_model'].predict(vec)
            skills = models['it_mlb'].inverse_transform(pred)[0] if models['it_mlb'] else []
            role = models['it_role_model'].predict(models['it_tfidf'].transform([" ".join(skills)]))[0] if skills and models['it_role_model'] else "Not determined"
            resume_skills = extract_skills(cleaned, IT_SKILL_LIST)
            missing = get_missing_skills(resume_skills, IT_SKILL_LIST)
            
            if models['it_coursecert_tfidf'] and models['it_course_model']:
                x_vec = models['it_coursecert_tfidf'].transform([" ".join(missing) if missing else "general"])
                course = models['it_course_model'].predict(x_vec)[0]
                cert = models['it_cert_model'].predict(x_vec)[0] if models['it_cert_model'] else "N/A"
            else:
                course = cert = "N/A"
        else:
            if not all([models['nonit_tfidf'], models['nonit_skill_model']]):
                return jsonify({"error": "Non-IT models not loaded"}), 500
            
            vec = models['nonit_tfidf'].transform([cleaned])
            pred = models['nonit_skill_model'].predict(vec)
            skills = models['nonit_mlb'].inverse_transform(pred)[0] if models['nonit_mlb'] else []
            role = models['nonit_role_model'].predict(models['nonit_tfidf'].transform([" ".join(skills)]))[0] if skills and models['nonit_role_model'] else "Not determined"
            resume_skills = extract_skills(cleaned, NON_IT_SKILL_LIST)
            missing = get_missing_skills(resume_skills, NON_IT_SKILL_LIST)
            
            if models['nonit_coursecert_tfidf'] and models['nonit_course_model']:
                x_vec = models['nonit_coursecert_tfidf'].transform([" ".join(missing) if missing else "general"])
                course = models['nonit_course_model'].predict(x_vec)[0]
                cert = models['nonit_cert_model'].predict(x_vec)[0] if models['nonit_cert_model'] else "N/A"
            else:
                course = cert = "N/A"
        
        return jsonify({
            "domain": domain,
            "predicted_skills": ", ".join(skills) if skills else "No skills predicted",
            "resume_skills": resume_skills,
            "missing_skills": missing,
            "predicted_role": role,
            "recommendation": {"course": course, "certificate": cert}
        })
    except Exception as e:
        logger.error(f"Error in prediction: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

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
# ROUTES - MOCK TEST (MONGODB)
# ============================================
@app.route('/api/get_subjects', methods=['GET'])
def get_subjects():
    """Get subjects and difficulties"""
    try:
        if mongodb is None:
            return jsonify({
                "subjects": ["Python", "Java", "JavaScript", "Data Science", "SQL"],
                "difficulties": ["Easy", "Medium", "Hard"]
            })
        
        subjects = mongodb.questions.distinct("subject")
        difficulties = mongodb.questions.distinct("difficulty")
        
        subjects = list(subjects) if subjects else ["Python", "Java", "JavaScript"]
        difficulties = list(difficulties) if difficulties else ["Easy", "Medium", "Hard"]
        
        return jsonify({"subjects": subjects, "difficulties": difficulties})
    except Exception as e:
        logger.error(f"Error fetching subjects: {e}")
        return jsonify({
            "subjects": ["Python", "Java", "JavaScript"],
            "difficulties": ["Easy", "Medium", "Hard"]
        })

@app.route('/api/get_questions', methods=['POST'])
def get_questions():
    """Get 10 random questions"""
    try:
        data = request.get_json()
        subject = data.get('subject')
        difficulty = data.get('difficulty', None)
        
        if not subject:
            return jsonify({"error": "Subject required"}), 400
        
        if mongodb is None:
            return jsonify({"error": "Database not connected"}), 500
        
        query = {"subject": subject}
        if difficulty:
            query["difficulty"] = difficulty
        
        questions = list(mongodb.questions.find(query).limit(10))
        
        if not questions:
            return jsonify({"error": "No questions found"}), 404
        
        formatted_questions = []
        for q in questions:
            formatted_questions.append({
                "id": str(q['_id']),
                "subject": q.get('subject', ''),
                "question": q.get('question_text', ''),
                "options": {
                    "A": q.get('option_a', ''),
                    "B": q.get('option_b', ''),
                    "C": q.get('option_c', ''),
                    "D": q.get('option_d', '')
                },
                "difficulty": q.get('difficulty', 'Medium')
            })
        
        return jsonify({
            "questions": formatted_questions,
            "total": len(formatted_questions),
            "time_limit": 600
        })
    except Exception as e:
        logger.error(f"Error getting questions: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/submit_test', methods=['POST'])
def submit_test():
    """Submit test"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'guest')
        subject = data.get('subject')
        answers = data.get('answers', {})
        time_taken = data.get('time_taken', 0)
        
        if not subject or not answers:
            return jsonify({"error": "Subject and answers required"}), 400
        
        if mongodb is None:
            return jsonify({"error": "Database not connected"}), 500
        
        question_ids = [ObjectId(qid) for qid in answers.keys()]
        questions = list(mongodb.questions.find({'_id': {'$in': question_ids}}))
        
        score = 0
        results = []
        
        for q in questions:
            q_id = str(q['_id'])
            user_answer = answers.get(q_id, '')
            correct_answer = q.get('correct_option', '')
            is_correct = user_answer.upper() == correct_answer.upper()
            
            if is_correct:
                score += 1
            
            results.append({
                "question_id": q_id,
                "question": q.get('question_text', ''),
                "options": {
                    "A": q.get('option_a', ''),
                    "B": q.get('option_b', ''),
                    "C": q.get('option_c', ''),
                    "D": q.get('option_d', '')
                },
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "is_correct": is_correct,
                "explanation": q.get('explanation', 'No explanation')
            })
        
        total = len(questions)
        percentage = (score / total * 100) if total > 0 else 0
        
        try:
            test_attempt = {
                "user_id": user_id,
                "subject": subject,
                "score": score,
                "total_questions": total,
                "percentage": percentage,
                "time_taken": time_taken,
                "results": results,
                "timestamp": datetime.utcnow()
            }
            mongodb.test_attempts.insert_one(test_attempt)
        except Exception as e:
            logger.warning(f"Could not store test attempt: {e}")
        
        return jsonify({
            "score": score,
            "total": total,
            "percentage": round(percentage, 2),
            "results": results,
            "time_taken": time_taken,
            "passed": percentage >= 60
        })
    except Exception as e:
        logger.error(f"Error submitting test: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/test_history/<user_id>', methods=['GET'])
def get_test_history(user_id):
    """Get test history"""
    try:
        if mongodb is None:
            return jsonify({"error": "Database not connected"}), 500
        
        history_cursor = mongodb.test_attempts.find(
            {"user_id": user_id}
        ).sort("timestamp", -1).limit(20)
        
        history = []
        for h in history_cursor:
            history.append({
                "attempt_id": str(h['_id']),
                "subject": h.get('subject', ''),
                "score": h.get('score', 0),
                "total_questions": h.get('total_questions', 0),
                "percentage": h.get('percentage', 0),
                "time_taken": h.get('time_taken', 0),
                "timestamp": h.get('timestamp').isoformat() if h.get('timestamp') else None
            })
        
        if history:
            total_tests = len(history)
            avg_score = sum(h['percentage'] for h in history) / total_tests
            subjects = list(set(h['subject'] for h in history))
        else:
            total_tests = 0
            avg_score = 0
            subjects = []
        
        return jsonify({
            "history": history,
            "stats": {
                "total_tests": total_tests,
                "average_score": round(avg_score, 2),
                "subjects_attempted": subjects
            }
        })
    except Exception as e:
        logger.error(f"Error fetching history: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/test_result/<attempt_id>', methods=['GET'])
def get_test_result(attempt_id):
    """Get test result"""
    try:
        if mongodb is None:
            return jsonify({"error": "Database not connected"}), 500
        
        result = mongodb.test_attempts.find_one({"_id": ObjectId(attempt_id)})
        
        if not result:
            return jsonify({"error": "Test attempt not found"}), 404
        
        formatted_result = {
            "attempt_id": str(result['_id']),
            "user_id": result.get('user_id', ''),
            "subject": result.get('subject', ''),
            "score": result.get('score', 0),
            "total_questions": result.get('total_questions', 0),
            "percentage": result.get('percentage', 0),
            "time_taken": result.get('time_taken', 0),
            "results": result.get('results', []),
            "timestamp": result.get('timestamp').isoformat() if result.get('timestamp') else None
        }
        
        return jsonify(formatted_result)
    except Exception as e:
        logger.error(f"Error fetching result: {e}")
        return jsonify({"error": str(e)}), 500

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
# ROUTES - CANDIDATE
# ============================================
@app.route('/api/candidate/profile/<user_id>', methods=['GET'])
def get_candidate_profile(user_id):
    """Get candidate profile"""
    if mongodb is None:
        return jsonify({"error": "Database not connected"}), 500
    
    try:
        user = mongodb.users.find_one({'_id': ObjectId(user_id)})
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        user['_id'] = str(user['_id'])
        return jsonify({'profile': user}), 200
    except Exception as e:
        logger.error(f"Profile fetch error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/candidate/profile/<user_id>', methods=['PUT'])
def update_candidate_profile(user_id):
    """Update candidate profile"""
    if mongodb is None:
        return jsonify({"error": "Database not connected"}), 500
    
    try:
        data = request.json
        
        result = mongodb.users.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': data}
        )
        
        if result.modified_count == 0:
            return jsonify({'error': 'Profile not updated'}), 404
        
        return jsonify({'message': 'Profile updated successfully'}), 200
    except Exception as e:
        logger.error(f"Profile update error: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================
# ROUTES - JOB SEARCH
# ============================================
@app.route('/api/jobs/search', methods=['GET'])
def search_jobs_public():
    """Public job search"""
    if mongodb is None:
        return jsonify({"error": "Database not connected"}), 500
    
    try:
        query = request.args.get('query', '')
        location = request.args.get('location', '')
        job_type = request.args.get('type', '')
        
        filters = {'status': 'active'}
        
        if query:
            filters['$or'] = [
                {'title': {'$regex': query, '$options': 'i'}},
                {'description': {'$regex': query, '$options': 'i'}},
                {'skills': {'$regex': query, '$options': 'i'}}
            ]
        
        if location:
            filters['location'] = {'$regex': location, '$options': 'i'}
        
        if job_type:
            filters['type'] = job_type
        
        jobs = list(mongodb.jobs.find(filters).sort('createdAt', -1).limit(50))
        
        for job in jobs:
            job['_id'] = str(job['_id'])
            job['createdAt'] = job['createdAt'].isoformat() if 'createdAt' in job else None
        
        return jsonify({'jobs': jobs, 'count': len(jobs)}), 200
    except Exception as e:
        logger.error(f"Job search error: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================
# ERROR HANDLERS
# ============================================
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({'error': 'File too large. Max 16MB'}), 413

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
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug,
        threaded=True
    )