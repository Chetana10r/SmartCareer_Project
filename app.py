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
from models.resume_parser import ResumeParser
import logging
import yake
from collections import Counter

# -----------------------------
# Keyword Extraction & Matching
# -----------------------------
def extract_keywords_from_text(text, max_keywords=20):
    """Extract important keywords using YAKE"""
    try:
        kw_extractor = yake.KeywordExtractor(
            lan="en",
            n=2,  # bigrams
            dedupLim=0.9,
            top=max_keywords
        )
        keywords = kw_extractor.extract_keywords(text)
        return [kw[0] for kw in keywords]
    except:
        # Fallback: simple word frequency
        words = re.findall(r'\b[a-z]{3,}\b', text.lower())
        common_words = Counter(words).most_common(max_keywords)
        return [word for word, _ in common_words]

def optimize_resume_content(resume_text, job_description):
    """
    Optimize resume content based on job description
    Returns optimized summary and matched skills
    """
    # Extract keywords from job description
    job_keywords = set(extract_keywords_from_text(job_description, 30))
    
    # Extract skills from resume
    resume_words = set(re.findall(r'\b[a-z]{3,}\b', resume_text.lower()))
    
    # Find matching skills
    matched_skills = job_keywords.intersection(resume_words)
    missing_keywords = job_keywords - resume_words
    
    # Generate optimized summary
    top_skills = list(matched_skills)[:8]
    
    if top_skills:
        summary = (
            f"Results-driven professional with expertise in {', '.join(top_skills[:5])}. "
            f"Proven track record in delivering high-impact solutions and driving organizational success. "
            f"Strong technical and analytical skills combined with excellent problem-solving abilities."
        )
    else:
        summary = (
            "Accomplished professional with demonstrated expertise in technology and innovation. "
            "Proven ability to deliver results in fast-paced environments. "
            "Strong analytical and communication skills with a focus on continuous improvement."
        )
    
    return {
        'summary': summary,
        'matched_skills': list(matched_skills)[:15],
        'missing_keywords': list(missing_keywords)[:10],
        'match_score': int((len(matched_skills) / len(job_keywords)) * 100) if job_keywords else 0
    }

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed, will use system env vars

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
CORS(app)


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
    """Optimize resume - extract ALL content"""
    if 'resume' not in request.files:
        return jsonify({"error": "No resume uploaded"}), 400

    resume_file = request.files['resume']
    job_description = request.form.get('job_description', '')
    
    resume_text = extract_text_from_pdf(resume_file)
    
    if not resume_text:
        return jsonify({"error": "Could not extract text from resume"}), 400

    try:
        # Parse resume
        parser = ResumeParser()
        parsed_data = parser.parse_resume(resume_text)
        
        app.logger.info(f"Parsed: {parsed_data['personal_info']['name']}")
        app.logger.info(f"Education: {len(parsed_data['education'])} entries")
        app.logger.info(f"Projects: {len(parsed_data['projects'])} entries")
        
        # Optimize based on JD
        if job_description:
            cleaned_text = clean_text(resume_text)
            optimization = optimize_resume_content(cleaned_text, job_description)
            summary = optimization['summary']
            app.logger.info(f"Match score: {optimization['match_score']}%")
        else:
            summary = "Experienced professional with strong technical background."
        
        # Build resume with ALL content
        optimized_resume = {
            "personal_info": parsed_data['personal_info'],
            "professional_summary": summary,
            "education": parsed_data['education'],
            "experience": parsed_data['experience'],
            "projects": parsed_data['projects'],
            "skills": parsed_data['skills'],
            "certifications": parsed_data['certifications'],
            "achievements": parsed_data['achievements'],
            "research": parsed_data['research']
        }
        
        os.makedirs('static', exist_ok=True)
        
        renderer = FixedTemplateRenderer()
        pdf_path = renderer.render_resume(optimized_resume)
        
        app.logger.info(f"Resume generated: {pdf_path}")
        
        return send_file(pdf_path, as_attachment=True, download_name="optimized_resume.pdf")

    except Exception as e:
        app.logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


def prioritize_content_by_jd(parsed_data, matched_skills):
    """Prioritize and trim content to fit one page based on JD"""
    # Limit education to top 4
    parsed_data['education'] = parsed_data['education'][:4]
    
    # Limit projects to 3 most relevant
    if len(parsed_data['projects']) > 3:
        parsed_data['projects'] = parsed_data['projects'][:3]
    
    # Limit project descriptions to 3 bullets each
    for proj in parsed_data['projects']:
        if len(proj.get('description', [])) > 3:
            proj['description'] = proj['description'][:3]
    
    # Limit certifications to 4
    if len(parsed_data['certifications']) > 4:
        parsed_data['certifications'] = parsed_data['certifications'][:4]
    
    # Limit achievements to 5
    if len(parsed_data['achievements']) > 5:
        parsed_data['achievements'] = parsed_data['achievements'][:5]
    
    # Limit research details to 3 bullets
    for res in parsed_data['research']:
        if len(res.get('details', [])) > 3:
            res['details'] = res['details'][:3]
    
    # Limit experience to 2
    if len(parsed_data['experience']) > 2:
        parsed_data['experience'] = parsed_data['experience'][:2]
    
    # Limit experience responsibilities to 3 each
    for exp in parsed_data['experience']:
        if len(exp.get('responsibilities', [])) > 3:
            exp['responsibilities'] = exp['responsibilities'][:3]
    
    return parsed_data


# -----------------------------
# ADD these NEW routes:
# -----------------------------

@app.route('/create_resume', methods=['POST'])
def create_resume():
    """Create resume from user-provided data"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Validate required fields
        if not data.get('name') or not data.get('email'):
            return jsonify({"error": "Name and Email are required"}), 400
        
        # Get job description for optimization
        job_description = data.get('job_description', '')
        
        # Build resume data structure
        resume_data = {
            "personal_info": {
                "name": data.get('name', 'Your Name'),
                "phone": data.get('phone', ''),
                "email": data.get('email', ''),
                "location": data.get('location', ''),
                "linkedin": data.get('linkedin', ''),
                "github": data.get('github', '')
            },
            "professional_summary": data.get('summary', ''),
            "education": data.get('education', []),
            "experience": data.get('experience', []),
            "projects": data.get('projects', []),
            "skills": data.get('skills', {}),
            "certifications": data.get('certifications', []),
            "achievements": data.get('achievements', []),
            "research": data.get('research', [])
        }
        
        # If job description provided, optimize summary
        if job_description and not resume_data['professional_summary']:
            skills_text = str(resume_data['skills'])
            optimization = optimize_resume_content(skills_text, job_description)
            resume_data['professional_summary'] = optimization['summary']
        
        # Default summary if none provided
        if not resume_data['professional_summary']:
            resume_data['professional_summary'] = (
                "Motivated professional with strong analytical and problem-solving skills. "
                "Committed to delivering high-quality results and continuous learning."
            )
        
        # Ensure static directory exists
        os.makedirs('static', exist_ok=True)
        
        # Render PDF
        renderer = FixedTemplateRenderer()
        pdf_path = renderer.render_resume(resume_data)
        
        return send_file(pdf_path, as_attachment=True, download_name="generated_resume.pdf")
    
    except Exception as e:
        app.logger.error(f"Error in create_resume: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Failed to create resume: {str(e)}"}), 500

@app.route('/check_ats_score', methods=['POST'])
def check_ats_score():
    """Check ATS compatibility score of resume against job description"""
    if 'resume' not in request.files:
        return jsonify({"error": "No resume uploaded"}), 400
    
    resume_file = request.files['resume']
    job_description = request.form.get('job_description', '')
    
    if not job_description:
        return jsonify({"error": "Job description is required"}), 400
    
    try:
        # Extract resume text
        resume_text = extract_text_from_pdf(resume_file)
        
        if not resume_text:
            return jsonify({"error": "Could not extract text from resume"}), 400
        
        # Clean and analyze text
        cleaned_resume = clean_text(resume_text)
        cleaned_jd = clean_text(job_description)
        
        # 1. KEYWORD MATCHING SCORE (40% weight)
        jd_keywords = set(extract_keywords_from_text(job_description, 30))
        resume_keywords = set(extract_keywords_from_text(resume_text, 30))
        matched_keywords = jd_keywords.intersection(resume_keywords)
        
        keyword_match_score = int((len(matched_keywords) / len(jd_keywords)) * 100) if jd_keywords else 0
        
        # 2. SKILL EXTRACTION & MATCHING (25% weight)
        domain = detect_domain(cleaned_resume)
        skill_list = IT_SKILL_LIST if domain == "IT" else NON_IT_SKILL_LIST
        
        resume_skills = extract_skills(cleaned_resume, skill_list)
        jd_skills = extract_skills(cleaned_jd, skill_list)
        
        matched_skills = list(set(resume_skills).intersection(set(jd_skills)))
        skill_match_score = int((len(matched_skills) / len(jd_skills)) * 100) if jd_skills else 0
        
        # 3. FORMATTING & STRUCTURE SCORE (20% weight)
        format_score = 100
        
        # Check contact information
        has_email = bool(re.search(r'[\w\.-]+@[\w\.-]+\.\w+', resume_text))
        has_phone = bool(re.search(r'(?:\+\d{1,3}|\d{3})[.\s-]?\d{3}[.\s-]?\d{4}|\(\d{3}\)\s?\d{3}[.\s-]?\d{4}', resume_text))
        has_linkedin = bool(re.search(r'linkedin\.com/in/[\w\-]+', resume_text, re.IGNORECASE))
        
        if not has_email:
            format_score -= 15
        if not has_phone:
            format_score -= 15
        if not has_linkedin:
            format_score -= 10
        
        # Check word count (300-900 words is ideal for ATS)
        word_count = len(resume_text.split())
        if word_count < 250:
            format_score -= 20
        elif word_count > 1500:
            format_score -= 15
        
        # Check for important sections
        sections_found = 0
        section_keywords = ['experience', 'education', 'skill', 'project', 'certification']
        for keyword in section_keywords:
            if keyword.lower() in cleaned_resume:
                sections_found += 1
        
        section_score = int((sections_found / len(section_keywords)) * 10)
        format_score += section_score
        format_score = min(100, max(0, format_score))
        
        # 4. LENGTH & CONTENT COMPLETENESS (15% weight)
        completeness_score = 75  # Base score
        
        # Add points for having key sections
        if re.search(r'education|degree|school|university', cleaned_resume, re.IGNORECASE):
            completeness_score += 10
        if re.search(r'experience|worked|job|responsibility', cleaned_resume, re.IGNORECASE):
            completeness_score += 10
        if re.search(r'skill|proficient|expertise|technical', cleaned_resume, re.IGNORECASE):
            completeness_score += 5
        
        completeness_score = min(100, completeness_score)
        
        # CALCULATE OVERALL ATS SCORE
        overall_score = int(
            (keyword_match_score * 0.40) +
            (skill_match_score * 0.25) +
            (format_score * 0.20) +
            (completeness_score * 0.15)
        )
        
        # Generate intelligent suggestions
        suggestions = []
        
        # Keyword suggestions
        if keyword_match_score < 50:
            missing_keywords = list(jd_keywords - resume_keywords)[:5]
            suggestions.append({
                "type": "warning",
                "message": f"⚠️ Low keyword match ({keyword_match_score}%). Add: {', '.join(missing_keywords)}"
            })
        elif keyword_match_score >= 70:
            suggestions.append({
                "type": "success",
                "message": f"✅ Excellent keyword match ({keyword_match_score}%)"
            })
        else:
            suggestions.append({
                "type": "info",
                "message": f"📝 Good keyword match ({keyword_match_score}%). Could improve further."
            })
        
        # Skill suggestions
        if skill_match_score < 50 and jd_skills:
            missing_skills = list(set(jd_skills) - set(resume_skills))[:5]
            suggestions.append({
                "type": "warning",
                "message": f"⚠️ Add more required skills: {', '.join(missing_skills)}"
            })
        elif skill_match_score >= 70:
            suggestions.append({
                "type": "success",
                "message": f"✅ Strong skills alignment ({skill_match_score}%)"
            })
        
        # Contact info suggestions
        if not has_email or not has_phone:
            missing = []
            if not has_email:
                missing.append("email")
            if not has_phone:
                missing.append("phone")
            suggestions.append({
                "type": "warning",
                "message": f"📞 Add missing contact info: {', '.join(missing)}"
            })
        else:
            suggestions.append({
                "type": "success",
                "message": "✅ Complete contact information"
            })
        
        # Length suggestions
        if word_count < 250:
            suggestions.append({
                "type": "warning",
                "message": f"📄 Resume too short ({word_count} words). Aim for 300-900 words."
            })
        elif word_count > 1500:
            suggestions.append({
                "type": "warning",
                "message": f"📄 Resume too long ({word_count} words). Condense to 300-900 words."
            })
        else:
            suggestions.append({
                "type": "success",
                "message": f"✅ Good resume length ({word_count} words)"
            })
        
        # Missing sections
        missing_sections = []
        if not re.search(r'education|degree', cleaned_resume, re.IGNORECASE):
            missing_sections.append("Education")
        if not re.search(r'experience|worked', cleaned_resume, re.IGNORECASE):
            missing_sections.append("Experience")
        if not re.search(r'skill', cleaned_resume, re.IGNORECASE):
            missing_sections.append("Skills")
        
        if missing_sections:
            suggestions.append({
                "type": "warning",
                "message": f"📋 Add missing sections: {', '.join(missing_sections)}"
            })
        else:
            suggestions.append({
                "type": "success",
                "message": "✅ All key sections present"
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
            "missing_keywords": list(jd_keywords - resume_keywords)[:10],
            "contact_info": {
                "email_found": has_email,
                "phone_found": has_phone,
                "linkedin_found": has_linkedin
            },
            "word_count": word_count,
            "suggestions": suggestions,
            "domain_detected": domain
        })
    
    except Exception as e:
        app.logger.error(f"Error checking ATS score: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
    
# Health check endpoint
@app.route('/health')
def health():
    return jsonify({"status": "healthy", "ocr_available": OCR_AVAILABLE})

# -----------------------------
# Run App
# -----------------------------
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)