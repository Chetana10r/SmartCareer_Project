# recruiter_compat_routes.py
"""
Flat routes for the recruiter frontend.
Candidates are loaded from candidates_data.csv (project root).
All other data (jobs, shortlist) remains hardcoded in-memory.

Routes:
  GET  /recruiter_dashboard
  POST /get_recruiter_jobs
  POST /update_job_status
  POST /delete_job
  POST /api/recruiter/post-job
  POST /search_candidates
  POST /shortlist_candidate
  POST /match_resume
  POST /get_shortlisted
  POST /update_candidate_status
  POST /remove_from_shortlist
  POST /get_job_applicants
  GET  /get_analytics
"""

import copy
import csv
import logging
import os
import random

from flask import request, jsonify

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# LOAD CANDIDATES FROM CSV
# ---------------------------------------------------------------------------

def _load_candidates_from_csv():
    """Read candidates_data.csv and return a list of dicts."""
    csv_path = os.path.join(os.path.dirname(__file__), "candidates_data.csv")
    if not os.path.exists(csv_path):
        logger.warning(f"candidates_data.csv not found at {csv_path}. Using empty list.")
        return []

    candidates = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                # skills column is a comma-separated string like "Python, SQL, ..."
                skills_raw = row.get("skills", "")
                skills = [s.strip() for s in skills_raw.split(",") if s.strip()]

                candidates.append({
                    "id":         int(row["id"]),
                    "name":       row["name"].strip(),
                    "email":      row["email"].strip(),
                    "phone":      row["phone"].strip(),
                    "experience": row["experience"].strip(),
                    "location":   row["location"].strip(),
                    "skills":     skills,
                    "education":  row["education"].strip(),
                    "match_score": int(row["match_score"]),
                    "resume_url": row.get("resume_url", "#").strip(),
                })
            except Exception as e:
                logger.warning(f"Skipping CSV row due to error: {e} | row={row}")

    logger.info(f"Loaded {len(candidates)} candidates from candidates_data.csv")
    return candidates


# Load once at import time
_CANDIDATES = _load_candidates_from_csv()

# ---------------------------------------------------------------------------
# HARDCODED JOBS
# ---------------------------------------------------------------------------

_JOBS = [
    {
        "id": 1, "title": "Senior Data Scientist", "company": "TechCorp India Pvt. Ltd.",
        "location": "Mumbai, India", "jobType": "full-time", "type": "Full Time",
        "experienceLevel": "senior", "experience": "Senior (5+ years)",
        "salaryMin": "1500000", "salaryMax": "2000000", "salary": "15-20 LPA",
        "description": (
            "We are looking for a Senior Data Scientist to join our growing analytics team. "
            "You will design, develop, and deploy machine learning models that drive business "
            "decisions. Collaborate with product managers, engineers, and stakeholders to "
            "translate complex data into actionable insights."
        ),
        "requirements": (
            "- Master's or PhD in Statistics, Computer Science, or related field\n"
            "- 5+ years of hands-on experience in data science or ML engineering\n"
            "- Proficiency in Python and data manipulation libraries (pandas, NumPy)\n"
            "- Strong understanding of supervised and unsupervised learning algorithms\n"
            "- Experience with TensorFlow or PyTorch for deep learning\n"
            "- Solid SQL skills and experience with large datasets"
        ),
        "skills": ["Python", "Machine Learning", "TensorFlow", "SQL", "Statistics", "Deep Learning"],
        "applications": 45, "status": "active",
        "postedDate": "2026-04-10", "deadline": "2026-05-31", "recruiterId": "recruiter_1",
    },
    {
        "id": 2, "title": "Full Stack Developer", "company": "StartupXYZ Technologies",
        "location": "Bangalore, India", "jobType": "full-time", "type": "Full Time",
        "experienceLevel": "intermediate", "experience": "Intermediate (2-5 years)",
        "salaryMin": "1000000", "salaryMax": "1500000", "salary": "10-15 LPA",
        "description": (
            "Join our fast-growing startup as a Full Stack Developer. You will build scalable "
            "web applications from front to back in an agile environment."
        ),
        "requirements": (
            "- Bachelor's degree in Computer Science or equivalent\n"
            "- 2-5 years of full-stack development experience\n"
            "- Strong proficiency in React.js and modern JavaScript (ES6+)\n"
            "- Backend experience with Node.js and REST API design\n"
            "- Hands-on experience with MongoDB or PostgreSQL\n"
            "- Familiarity with AWS or any cloud provider"
        ),
        "skills": ["React", "Node.js", "MongoDB", "AWS", "JavaScript", "REST API"],
        "applications": 67, "status": "active",
        "postedDate": "2026-04-07", "deadline": "2026-05-15", "recruiterId": "recruiter_1",
    },
    {
        "id": 3, "title": "DevOps Engineer", "company": "Cloud Solutions Ltd.",
        "location": "Remote", "jobType": "contract", "type": "Contract",
        "experienceLevel": "intermediate", "experience": "Intermediate (2-5 years)",
        "salaryMin": "1200000", "salaryMax": "1800000", "salary": "12-18 LPA",
        "description": "Automate deployments, manage containerised workloads, ensure high availability. Fully remote.",
        "requirements": (
            "- 3+ years of DevOps or SRE experience\n"
            "- Strong knowledge of Docker and Kubernetes\n"
            "- Experience with CI/CD pipelines\n"
            "- Proficiency with AWS services\n"
            "- Infrastructure-as-code with Terraform or Ansible"
        ),
        "skills": ["Docker", "Kubernetes", "CI/CD", "AWS", "Terraform", "Linux"],
        "applications": 34, "status": "active",
        "postedDate": "2026-04-01", "deadline": "2026-05-20", "recruiterId": "recruiter_1",
    },
    {
        "id": 4, "title": "Frontend Developer", "company": "Design Hub Creative",
        "location": "Pune, India", "jobType": "part-time", "type": "Part Time",
        "experienceLevel": "entry", "experience": "Entry Level (0-2 years)",
        "salaryMin": "500000", "salaryMax": "800000", "salary": "5-8 LPA",
        "description": "Craft beautiful, responsive user interfaces and translate Figma mockups into React components.",
        "requirements": (
            "- 0-2 years of frontend development experience\n"
            "- Solid HTML5, CSS3, and JavaScript fundamentals\n"
            "- Experience with React.js\n"
            "- Knowledge of Tailwind CSS or Bootstrap"
        ),
        "skills": ["React", "CSS", "JavaScript", "Tailwind", "HTML5", "Figma"],
        "applications": 23, "status": "closed",
        "postedDate": "2026-03-15", "deadline": "2026-04-15", "recruiterId": "recruiter_1",
    },
    {
        "id": 5, "title": "Machine Learning Engineer", "company": "AI Innovations Pvt. Ltd.",
        "location": "Hyderabad, India", "jobType": "full-time", "type": "Full Time",
        "experienceLevel": "intermediate", "experience": "Intermediate (2-5 years)",
        "salaryMin": "1300000", "salaryMax": "1900000", "salary": "13-19 LPA",
        "description": "Build, optimise, and productionise ML models for NLP and computer-vision projects.",
        "requirements": (
            "- 2-5 years of ML engineering experience\n"
            "- Strong Python skills with PyTorch or TensorFlow\n"
            "- Experience with MLOps tools (MLflow, Kubeflow)\n"
            "- Knowledge of model serving and REST APIs"
        ),
        "skills": ["Python", "PyTorch", "MLOps", "NLP", "Computer Vision", "Spark"],
        "applications": 38, "status": "active",
        "postedDate": "2026-04-14", "deadline": "2026-06-01", "recruiterId": "recruiter_1",
    },
    {
        "id": 6, "title": "Data Analyst", "company": "FinTech Solutions Inc.",
        "location": "Chennai, India", "jobType": "full-time", "type": "Full Time",
        "experienceLevel": "entry", "experience": "Entry Level (0-2 years)",
        "salaryMin": "600000", "salaryMax": "900000", "salary": "6-9 LPA",
        "description": "Support risk and product analytics teams. Turn raw financial data into meaningful dashboards.",
        "requirements": (
            "- 0-2 years of data analysis experience\n"
            "- Proficiency in SQL and Excel\n"
            "- Experience with BI tools (Tableau, Power BI)\n"
            "- Familiarity with Python for data wrangling"
        ),
        "skills": ["SQL", "Python", "Tableau", "Excel", "Power BI", "Statistics"],
        "applications": 52, "status": "active",
        "postedDate": "2026-04-18", "deadline": "2026-05-30", "recruiterId": "recruiter_1",
    },
    {
        "id": 7, "title": "Android Developer", "company": "MobileFirst Labs",
        "location": "Delhi, India", "jobType": "full-time", "type": "Full Time",
        "experienceLevel": "intermediate", "experience": "Intermediate (2-5 years)",
        "salaryMin": "900000", "salaryMax": "1400000", "salary": "9-14 LPA",
        "description": "Design and build advanced applications for the Android platform.",
        "requirements": (
            "- 2-5 years of Android development\n"
            "- Strong Kotlin and Java skills\n"
            "- Experience with Android Jetpack components\n"
            "- Published apps on Google Play Store preferred"
        ),
        "skills": ["Kotlin", "Java", "Android SDK", "Jetpack", "REST API", "Firebase"],
        "applications": 29, "status": "active",
        "postedDate": "2026-04-20", "deadline": "2026-06-10", "recruiterId": "recruiter_1",
    },
    {
        "id": 8, "title": "Backend Engineer - Python", "company": "SaaS Global Corp",
        "location": "Kolkata, India", "jobType": "full-time", "type": "Full Time",
        "experienceLevel": "senior", "experience": "Senior (5+ years)",
        "salaryMin": "1400000", "salaryMax": "2200000", "salary": "14-22 LPA",
        "description": "Own and evolve core Python microservices and design APIs for millions of users.",
        "requirements": (
            "- 5+ years of backend development with Python\n"
            "- Expertise in Django or FastAPI\n"
            "- Strong knowledge of PostgreSQL and Redis\n"
            "- Experience with Docker and Kubernetes"
        ),
        "skills": ["Python", "Django", "FastAPI", "PostgreSQL", "Redis", "Microservices"],
        "applications": 41, "status": "active",
        "postedDate": "2026-04-22", "deadline": "2026-06-15", "recruiterId": "recruiter_1",
    },
]

# Map job_id -> list of candidate ids (from CSV) who applied
_JOB_APPLICANTS = {
    1: [1, 2, 4, 10, 12, 15, 18, 22],
    2: [3, 5, 7, 11, 14, 17, 19, 21],
    3: [6, 13, 23, 3, 20, 24],
    4: [7, 11, 16, 18, 21],
    5: [2, 4, 12, 15, 22, 24],
    6: [8, 16, 18, 12, 2],
    7: [9, 20, 14, 23],
    8: [10, 19, 13, 25, 24],
}

_APPLICANT_STATUSES = {
    (1, 1): "shortlisted", (1, 2): "reviewed",  (1, 4): "applied",
    (1, 10): "applied",    (1, 12): "reviewed",  (1, 15): "shortlisted",
    (1, 18): "applied",    (1, 22): "applied",
    (2, 3): "shortlisted", (2, 5): "shortlisted",(2, 7): "applied",
    (2, 11): "reviewed",   (2, 14): "applied",   (2, 17): "applied",
    (2, 19): "applied",    (2, 21): "applied",
    (3, 6): "shortlisted", (3, 13): "reviewed",  (3, 23): "applied",
    (3, 3): "applied",     (3, 20): "applied",   (3, 24): "applied",
    (4, 7): "applied",     (4, 11): "reviewed",  (4, 16): "applied",
    (4, 18): "applied",    (4, 21): "applied",
    (5, 2): "shortlisted", (5, 4): "shortlisted",(5, 12): "applied",
    (5, 15): "reviewed",   (5, 22): "applied",   (5, 24): "applied",
    (6, 8): "shortlisted", (6, 16): "applied",   (6, 18): "reviewed",
    (6, 12): "applied",    (6, 2): "applied",
    (7, 9): "shortlisted", (7, 20): "applied",   (7, 14): "applied",
    (7, 23): "applied",
    (8, 10): "shortlisted",(8, 19): "reviewed",  (8, 13): "applied",
    (8, 25): "applied",    (8, 24): "applied",
}

# Build shortlist seed from CSV candidate ids
def _build_initial_shortlist():
    id_map = {c["id"]: c for c in _CANDIDATES}
    entries = [
        (1,  "Senior Data Scientist",   "shortlisted",         "2026-04-10", None,         "Strong ML background, excellent communication."),
        (2,  "Full Stack Developer",    "interview_scheduled", "2026-04-08", "2026-04-30", "Great portfolio, can join immediately."),
        (3,  "DevOps Engineer",         "contacted",           "2026-04-07", None,         "Strong DevOps hands-on experience."),
        (4,  "Senior Data Scientist",   "rejected",            "2026-04-02", None,         "Salary expectations above budget."),
        (6,  "DevOps Engineer",         "hired",               "2026-03-25", "2026-04-05", "Exceptional candidate - offer accepted."),
        (9,  "Android Developer",       "shortlisted",         "2026-04-20", None,         "Two published apps with 50k+ downloads."),
        (10, "Backend Engineer-Python", "shortlisted",         "2026-04-22", None,         "Top scorer in technical assessment."),
        (13, "DevOps Engineer",         "contacted",           "2026-04-12", None,         "AWS certified, strong infra skills."),
        (22, "Machine Learning Eng.",   "interview_scheduled", "2026-04-17", "2026-05-05", "Published 3 papers on computer vision."),
    ]
    result = []
    for cid, job, status, sl_date, intv_date, notes in entries:
        c = id_map.get(cid)
        if not c:
            continue
        result.append({
            "id":               c["id"],
            "name":             c["name"],
            "email":            c["email"],
            "phone":            c["phone"],
            "job_applied":      job,
            "match_score":      c["match_score"],
            "status":           status,
            "shortlisted_date": sl_date,
            "interview_date":   intv_date,
            "experience":       c["experience"],
            "location":         c["location"],
            "skills":           c["skills"],
            "resume_url":       "#",
            "notes":            notes,
        })
    return result


# Mutable in-session stores
_jobs_store       = copy.deepcopy(_JOBS)
_shortlist_store  = _build_initial_shortlist()

# ---------------------------------------------------------------------------

def register_recruiter_compat_routes(app):

    # ── /recruiter_dashboard ─────────────────────────────────────────────────
    @app.route("/recruiter_dashboard", methods=["GET"])
    def recruiter_dashboard_flat():
        active  = sum(1 for j in _jobs_store if j["status"] == "active")
        total   = sum(j["applications"] for j in _jobs_store)
        sl      = len(_shortlist_store)
        intv    = sum(1 for c in _shortlist_store if c["status"] == "interview_scheduled")
        stats   = {"activeJobs": active, "totalCandidates": total, "shortlisted": sl, "interviewed": intv}
        recent  = [{"id": j["id"], "title": j["title"], "applications": j["applications"], "posted": j["postedDate"]}
                   for j in _jobs_store[:3]]
        return jsonify({"stats": stats, "recent_jobs": recent, "recent_candidates": []}), 200

    # ── /get_recruiter_jobs ──────────────────────────────────────────────────
    @app.route("/get_recruiter_jobs", methods=["POST"])
    def get_recruiter_jobs_flat():
        return jsonify({"jobs": _jobs_store}), 200

    # ── /update_job_status ───────────────────────────────────────────────────
    @app.route("/update_job_status", methods=["POST"])
    def update_job_status_flat():
        data = request.json or {}
        for job in _jobs_store:
            if job["id"] == data.get("job_id"):
                job["status"] = data.get("status", job["status"])
                break
        return jsonify({"message": "Status updated", "success": True}), 200

    # ── /delete_job ──────────────────────────────────────────────────────────
    @app.route("/delete_job", methods=["POST"])
    def delete_job_flat():
        job_id = (request.json or {}).get("job_id")
        for i, j in enumerate(_jobs_store):
            if j["id"] == job_id:
                _jobs_store.pop(i)
                break
        return jsonify({"message": "Job deleted", "success": True}), 200

    # ── /api/recruiter/post-job ──────────────────────────────────────────────
    @app.route("/api/recruiter/post-job", methods=["POST"])
    def post_job_hardcoded():
        data = request.json or {}
        for f in ["title", "company", "description", "requirements"]:
            if not data.get(f):
                return jsonify({"error": f"Missing required field: {f}"}), 400
        skills = data.get("skills", [])
        if isinstance(skills, str):
            skills = [s.strip() for s in skills.split(",") if s.strip()]
        new_id  = max((j["id"] for j in _jobs_store), default=0) + 1
        new_job = {
            "id": new_id, "title": data["title"], "company": data.get("company", ""),
            "location": data.get("location", "Not specified"),
            "jobType": data.get("type", "Full Time").lower().replace(" ", "-"),
            "type": data.get("type", "Full Time"),
            "experienceLevel": data.get("experience", "Intermediate (2-5 years)").split()[0].lower(),
            "experience": data.get("experience", "Intermediate (2-5 years)"),
            "salaryMin": "800000", "salaryMax": "1200000",
            "salary": data.get("salary", "Competitive"),
            "description": data["description"], "requirements": data["requirements"],
            "skills": skills, "applications": 0, "status": "active",
            "postedDate": "2026-04-26", "deadline": data.get("applicationDeadline", "2026-06-30"),
            "recruiterId": data.get("recruiterId", "recruiter_1"),
        }
        _jobs_store.insert(0, new_job)
        return jsonify({"message": "Job posted successfully", "job": new_job}), 201

    # ── /search_candidates  (reads from CSV-loaded _CANDIDATES) ──────────────
    @app.route("/search_candidates", methods=["POST"])
    def search_candidates_flat():
        filters    = request.json or {}
        skills_raw = filters.get("skills", "").lower().strip()
        location   = filters.get("location", "").lower().strip()
        education  = filters.get("education", "").lower().strip()
        job_role   = filters.get("jobRole", "").lower().strip()
        experience = filters.get("experience", "").strip()

        # No filters → return all candidates from CSV
        if not any([skills_raw, location, education, job_role, experience]):
            return jsonify({"candidates": copy.deepcopy(_CANDIDATES)}), 200

        results = []
        for c in _CANDIDATES:
            c_skills_lower = [s.lower() for s in c["skills"]]

            if skills_raw:
                wanted = [s.strip() for s in skills_raw.split(",") if s.strip()]
                if not any(w in " ".join(c_skills_lower) for w in wanted):
                    continue

            if location and location not in c["location"].lower():
                continue

            if education and education not in c["education"].lower():
                continue

            if job_role and job_role not in (" ".join(c["skills"]).lower() + " " + c["education"].lower()):
                continue

            if experience:
                try:
                    years = int(c["experience"].split()[0])
                except ValueError:
                    years = 0
                if   experience == "0-2"  and not (0  <= years <= 2):  continue
                elif experience == "2-5"  and not (2  <= years <= 5):  continue
                elif experience == "5-10" and not (5  <= years <= 10): continue
                elif experience == "10+"  and years < 10:              continue

            results.append(copy.deepcopy(c))

        return jsonify({"candidates": results}), 200

    # ── /shortlist_candidate ─────────────────────────────────────────────────
    @app.route("/shortlist_candidate", methods=["POST"])
    def shortlist_candidate_flat():
        data         = request.json or {}
        candidate_id = data.get("candidate_id")
        candidate    = next((c for c in _CANDIDATES if c["id"] == candidate_id), None)
        already      = any(s["id"] == candidate_id for s in _shortlist_store)
        if candidate and not already:
            _shortlist_store.append({
                "id":               candidate["id"],
                "name":             candidate["name"],
                "email":            candidate["email"],
                "phone":            candidate["phone"],
                "job_applied":      data.get("job_title", "General Application"),
                "match_score":      candidate["match_score"],
                "status":           "shortlisted",
                "shortlisted_date": "2026-04-26",
                "interview_date":   None,
                "experience":       candidate["experience"],
                "location":         candidate["location"],
                "skills":           candidate["skills"],
                "resume_url":       "#",
                "notes":            "",
            })
        return jsonify({"message": "Candidate shortlisted successfully"}), 201

    # ── /match_resume ────────────────────────────────────────────────────────
    @app.route("/match_resume", methods=["POST"])
    def match_resume_flat():
        job_id      = request.form.get("job_id", "")
        resume_file = request.files.get("resume")
        cname       = "Uploaded Candidate"
        if resume_file and resume_file.filename:
            cname = resume_file.filename.replace(".pdf", "").replace("_", " ").title()

        job = next((j for j in _jobs_store if str(j["id"]) == str(job_id)), None)
        if job:
            matched = job["skills"][:4]
            missing = ["AWS", "Docker"] if "AWS" not in job["skills"] else ["Rust", "Go"]
            sc  = random.randint(82, 95)
            ex  = random.randint(78, 92)
            ed  = random.randint(80, 95)
            rec = "Highly Recommended" if sc >= 88 else "Recommended"
            strengths    = [f"Strong proficiency in {matched[0]} aligns with the role",
                            f"Experience suits the {job['experience']} requirement",
                            "Educational background is highly relevant"]
            improvements = [f"Gaining experience with {missing[0]} would strengthen the profile",
                            "A portfolio or GitHub project would help"]
        else:
            matched = ["Python", "SQL", "Machine Learning", "Communication"]
            missing = ["Cloud Platforms", "Docker"]
            sc, ex, ed  = 79, 75, 80
            rec          = "Recommended"
            strengths    = ["Core technical skills are present", "Good general background"]
            improvements = ["Cloud experience would be beneficial", "Add containerisation skills"]

        return jsonify({
            "match_score":            sc,
            "matched_skills":         matched,
            "missing_skills":         missing,
            "experience_match":       ex,
            "education_match":        ed,
            "overall_recommendation": rec,
            "candidate_name":         cname,
            "key_strengths":          strengths,
            "areas_for_improvement":  improvements,
        }), 200

    # ── /get_shortlisted ─────────────────────────────────────────────────────
    @app.route("/get_shortlisted", methods=["POST"])
    def get_shortlisted_flat():
        return jsonify({"candidates": _shortlist_store}), 200

    # ── /update_candidate_status ─────────────────────────────────────────────
    @app.route("/update_candidate_status", methods=["POST"])
    def update_candidate_status_flat():
        data = request.json or {}
        for c in _shortlist_store:
            if c["id"] == data.get("candidate_id"):
                c["status"] = data.get("status", c["status"])
                if c["status"] == "interview_scheduled":
                    c["interview_date"] = "2026-05-10"
                break
        return jsonify({"message": "Status updated", "success": True}), 200

    # ── /remove_from_shortlist ───────────────────────────────────────────────
    @app.route("/remove_from_shortlist", methods=["POST"])
    def remove_from_shortlist_flat():
        cid = (request.json or {}).get("candidate_id")
        for i, c in enumerate(_shortlist_store):
            if c["id"] == cid:
                _shortlist_store.pop(i)
                break
        return jsonify({"message": "Removed", "success": True}), 200

    # ── /get_job_applicants  (uses CSV candidates) ────────────────────────────
    @app.route("/get_job_applicants", methods=["POST"])
    def get_job_applicants_flat():
        data   = request.json or {}
        job_id = data.get("job_id")
        ids    = _JOB_APPLICANTS.get(job_id, [])
        id_map = {c["id"]: c for c in _CANDIDATES}
        result = []
        for cid in ids:
            c = id_map.get(cid)
            if c:
                entry = copy.deepcopy(c)
                entry["status"] = _APPLICANT_STATUSES.get((job_id, cid), "applied")
                result.append(entry)
        return jsonify({"applicants": result}), 200

    # ── /get_analytics ───────────────────────────────────────────────────────
    @app.route("/get_analytics", methods=["GET"])
    def get_analytics_flat():
        total_apps  = sum(j["applications"] for j in _jobs_store)
        active_jobs = sum(1 for j in _jobs_store if j["status"] == "active")
        total_sl    = len(_shortlist_store)
        total_intv  = sum(1 for c in _shortlist_store if c["status"] == "interview_scheduled")
        total_hired = sum(1 for c in _shortlist_store if c["status"] == "hired")
        avg_apps    = round(total_apps / len(_jobs_store)) if _jobs_store else 0
        hire_rate   = round((total_hired / total_sl) * 100) if total_sl else 0

        type_counts = {}
        for j in _jobs_store:
            t = j.get("type", "Full Time")
            type_counts[t] = type_counts.get(t, 0) + 1
        jobs_by_type = [{"type": t, "count": c}
                        for t, c in sorted(type_counts.items(), key=lambda x: -x[1])]

        skill_counts = {}
        for j in _jobs_store:
            for s in j.get("skills", []):
                skill_counts[s] = skill_counts.get(s, 0) + j.get("applications", 0)
        top_skills = [{"skill": s, "count": c}
                      for s, c in sorted(skill_counts.items(), key=lambda x: -x[1])[:8]]

        monthly = [
            {"month": "Nov", "applications": 87},
            {"month": "Dec", "applications": 112},
            {"month": "Jan", "applications": 98},
            {"month": "Feb", "applications": 134},
            {"month": "Mar", "applications": 156},
            {"month": "Apr", "applications": total_apps},
        ]

        # Derive locations from CSV candidates
        loc_counts = {}
        for c in _CANDIDATES:
            city = c["location"].split(",")[0].strip()
            loc_counts[city] = loc_counts.get(city, 0) + 1
        candidate_locations = [{"city": city, "count": cnt}
                                for city, cnt in sorted(loc_counts.items(), key=lambda x: -x[1])[:7]]

        status_counts = {}
        for c in _shortlist_store:
            status_counts[c["status"]] = status_counts.get(c["status"], 0) + 1
        status_map = {
            "shortlisted":         "Shortlisted",
            "contacted":           "Contacted",
            "interview_scheduled": "Interview Scheduled",
            "hired":               "Hired",
            "rejected":            "Rejected",
        }
        status_breakdown = [{"status": status_map.get(k, k), "count": v}
                             for k, v in sorted(status_counts.items(), key=lambda x: -x[1])]

        top_jobs = sorted(_jobs_store, key=lambda j: j["applications"], reverse=True)[:6]

        top_job   = top_jobs[0] if top_jobs else {}
        top_skill = top_skills[0]["skill"] if top_skills else "Python"
        insights  = [
            {"icon": "🏆", "text": f"'{top_job.get('title','')}' is your top job with {top_job.get('applications',0)} applications."},
            {"icon": "🎯", "text": f"'{top_skill}' is the most sought-after skill across all your job postings."},
            {"icon": "📍", "text": f"Bangalore leads candidate supply with {loc_counts.get('Bangalore',0)} candidates from the database."},
            {"icon": "⚡", "text": f"Your hire rate is {hire_rate}% from shortlist — strong conversion!"},
            {"icon": "📅", "text": f"Applications have grown 47% compared to last quarter — great momentum!"},
            {"icon": "💡", "text": f"You have {len(_CANDIDATES)} candidates in the database ready to be searched."},
        ]

        return jsonify({
            "overview": {
                "total_jobs":              len(_jobs_store),
                "active_jobs":             active_jobs,
                "total_applications":      total_apps,
                "total_shortlisted":       total_sl,
                "total_interviewed":       total_intv,
                "total_hired":             total_hired,
                "avg_applications_per_job": avg_apps,
                "hire_rate":               hire_rate,
            },
            "jobs_by_type":         jobs_by_type,
            "top_skills":           top_skills,
            "monthly_applications": monthly,
            "candidate_locations":  candidate_locations,
            "status_breakdown":     status_breakdown,
            "top_jobs":             top_jobs,
            "insights":             insights,
        }), 200

    logger.info(f"Recruiter routes registered — {len(_CANDIDATES)} candidates loaded from CSV")
