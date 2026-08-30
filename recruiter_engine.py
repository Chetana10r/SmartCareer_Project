# recruiter_engine.py
"""
Recruiter Blueprint
Covers every API call made by the recruiter frontend components:

  RecruiterDashboard.js  → GET  /api/recruiter/dashboard/<id>
  JobListings.js         → GET  /api/recruiter/jobs  (query ?recruiterId=)
                         → POST /api/recruiter/jobs/<id>/toggle-status
                         → DELETE /api/recruiter/jobs/<id>
  JobPosting.js          → POST /api/recruiter/post-job   (already in app.py, also here)
  CandidateSearch.js     → POST /api/recruiter/candidates/search
  ResumeMatching.js      → POST /api/recruiter/match-resume-file  (multipart)
  ShortlistManager.js    → GET  /api/recruiter/shortlist  (query ?recruiterId=)
                         → PUT  /api/recruiter/shortlist/<id>/status
                         → DELETE /api/recruiter/shortlist/<id>
                         → POST /api/recruiter/shortlist

Backward-compat flat routes in app.py:
  /get_recruiter_jobs    → proxied here
  /search_candidates     → proxied here
  /match_resume          → proxied here
  /get_shortlisted       → proxied here
  /shortlist_candidate   → proxied here
  /update_candidate_status → proxied here
  /remove_from_shortlist → proxied here
  /recruiter_dashboard   → proxied here
"""

import os
import logging
from datetime import datetime

from bson import ObjectId
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename

# ── Optional imports (fail gracefully) ─────────────────────────────────────
try:
    from resume_matcher import ResumeMatcher
except ImportError:
    class ResumeMatcher:
        def match_candidates_to_job(self, job, candidates): return []
        def calculate_match_score(self, resume, job): return {"overallScore": 0}
        def match_by_text(self, r, j): return {"matchScore": 0, "matchedSkills": [], "missingSkills": []}

try:
    from candidate_ranker import CandidateRanker
except ImportError:
    class CandidateRanker:
        def rank_candidates(self, matches): return matches

try:
    from job_manager import JobManager
except ImportError:
    class JobManager:
        def create_job(self, d): return "dummy"
        def get_jobs_by_recruiter(self, r): return []
        def get_job_by_id(self, i): return None
        def update_job(self, i, d): return False
        def delete_job(self, i): return False
        def toggle_job_status(self, i): return None
        def add_to_shortlist(self, d): return "dummy"
        def get_shortlisted_candidates(self, j): return []
        def get_shortlist_by_recruiter(self, r): return []
        def remove_from_shortlist(self, i): return False
        def update_shortlist_status(self, i, s, e=None): return False
        def get_dashboard_stats(self, r): return {}
        def count_jobs_by_recruiter(self, r): return 0
        def count_active_jobs(self, r): return 0
        def count_shortlisted_candidates(self, r): return 0
        def count_interviewed(self, r): return 0
        def get_recent_activity(self, r): return []

try:
    from candidate_parser import CandidateParser
except ImportError:
    class CandidateParser:
        def parse_resume(self, fp): return {}

try:
    from email_notifier import EmailNotifier
except ImportError:
    class EmailNotifier:
        def send_shortlist_email(self, c, j): pass
        def send_interview_invite(self, c, j, d): pass

logger = logging.getLogger(__name__)

# ── Blueprint & component setup ────────────────────────────────────────────
recruiter_bp = Blueprint("recruiter", __name__)

UPLOAD_FOLDER   = "uploads/resumes"
ALLOWED_EXTENSIONS = {"pdf", "docx", "doc"}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

_jm = _rm = _cr = _cp = _en = None

def _components():
    global _jm, _rm, _cr, _cp, _en
    if _jm is None: _jm = JobManager()
    if _rm is None: _rm = ResumeMatcher()
    if _cr is None: _cr = CandidateRanker()
    if _cp is None: _cp = CandidateParser()
    if _en is None: _en = EmailNotifier()
    return _jm, _rm, _cr, _cp, _en

def _db():
    try:
        db = current_app.config.get("db")
        if db is None:
            logger.warning("DB not in app config")
        return db
    except RuntimeError:
        logger.error("Outside app context")
        return None

def _allowed(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def _to_str(doc):
    if doc is None: return doc
    doc["_id"] = str(doc["_id"])
    for k in ("createdAt", "updatedAt", "shortlistedAt"):
        if k in doc and hasattr(doc[k], "isoformat"):
            doc[k] = doc[k].isoformat()
    return doc


# ════════════════════════════════════════════════════════
# DASHBOARD
# ════════════════════════════════════════════════════════

@recruiter_bp.route("/dashboard/<recruiter_id>", methods=["GET"])
def dashboard(recruiter_id):
    """RecruiterDashboard.js  →  GET /api/recruiter/dashboard/<recruiter_id>"""
    jm, *_ = _components()
    try:
        stats     = jm.get_dashboard_stats(recruiter_id)
        recent_jobs = jm.get_jobs_by_recruiter(recruiter_id)[:5]
        activity    = jm.get_recent_activity(recruiter_id)
        return jsonify({
            "stats":           stats,
            "recent_jobs":     recent_jobs,
            "recent_activity": activity,
        }), 200
    except Exception as e:
        logger.error(f"dashboard error: {e}")
        return jsonify({"error": str(e)}), 500


# ════════════════════════════════════════════════════════
# JOB MANAGEMENT
# ════════════════════════════════════════════════════════

@recruiter_bp.route("/post-job", methods=["POST"])
def post_job():
    """JobPosting.js  →  POST /api/recruiter/post-job"""
    jm, *_ = _components()
    data = request.json or {}

    required = ["title", "company", "description", "requirements", "recruiterId"]
    for f in required:
        if f not in data:
            return jsonify({"error": f"Missing required field: {f}"}), 400

    try:
        job_id = jm.create_job(data)
        return jsonify({"message": "Job posted successfully", "jobId": job_id}), 201
    except Exception as e:
        logger.error(f"post_job error: {e}")
        return jsonify({"error": str(e)}), 500


@recruiter_bp.route("/jobs", methods=["GET"])
def list_jobs():
    """JobListings.js  →  GET /api/recruiter/jobs?recruiterId=<id>"""
    jm, *_ = _components()
    recruiter_id = request.args.get("recruiterId")
    if not recruiter_id:
        return jsonify({"error": "recruiterId required"}), 400
    try:
        jobs = jm.get_jobs_by_recruiter(recruiter_id)
        return jsonify({"jobs": jobs, "count": len(jobs)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@recruiter_bp.route("/jobs/<job_id>", methods=["GET"])
def get_job(job_id):
    jm, *_ = _components()
    job = jm.get_job_by_id(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    return jsonify({"job": job}), 200


@recruiter_bp.route("/jobs/<job_id>", methods=["PUT"])
def update_job(job_id):
    jm, *_ = _components()
    data = request.json or {}
    ok = jm.update_job(job_id, data)
    if not ok:
        return jsonify({"error": "Job not found or update failed"}), 404
    return jsonify({"message": "Job updated"}), 200


@recruiter_bp.route("/jobs/<job_id>", methods=["DELETE"])
def delete_job(job_id):
    """JobListings.js  →  DELETE /api/recruiter/jobs/<id>"""
    jm, *_ = _components()
    ok = jm.delete_job(job_id)
    if not ok:
        return jsonify({"error": "Job not found"}), 404
    return jsonify({"message": "Job deleted"}), 200


@recruiter_bp.route("/jobs/<job_id>/toggle-status", methods=["POST"])
def toggle_job_status(job_id):
    """JobListings.js  →  POST /api/recruiter/jobs/<id>/toggle-status"""
    jm, *_ = _components()
    new_status = jm.toggle_job_status(job_id)
    if new_status is None:
        return jsonify({"error": "Job not found"}), 404
    return jsonify({"message": "Status updated", "status": new_status}), 200


# ════════════════════════════════════════════════════════
# CANDIDATE SEARCH
# ════════════════════════════════════════════════════════

@recruiter_bp.route("/candidates/search", methods=["POST"])
def search_candidates():
    """CandidateSearch.js  →  POST /api/recruiter/candidates/search"""
    db = _db()
    if not db:
        return jsonify({"error": "Database not available"}), 500

    filters = request.json or {}

    try:
        query = {"role": "candidate"}

        # Skills filter
        skills_raw = filters.get("skills", "")
        if skills_raw:
            skill_list = [s.strip() for s in skills_raw.split(",") if s.strip()]
            if skill_list:
                query["skills"] = {
                    "$elemMatch": {
                        "$regex": "|".join(skill_list),
                        "$options": "i",
                    }
                }

        # Location filter
        if filters.get("location"):
            query["location"] = {"$regex": filters["location"], "$options": "i"}

        # Education filter
        if filters.get("education"):
            query["education"] = {"$regex": filters["education"], "$options": "i"}

        # Job role filter
        if filters.get("jobRole"):
            query["$or"] = [
                {"jobRole": {"$regex": filters["jobRole"], "$options": "i"}},
                {"summary":  {"$regex": filters["jobRole"], "$options": "i"}},
            ]

        candidates = list(db.users.find(query).limit(50))
        for c in candidates:
            c.pop("password", None)
            _to_str(c)

        return jsonify({"candidates": candidates, "count": len(candidates)}), 200

    except Exception as e:
        logger.error(f"search_candidates error: {e}")
        return jsonify({"error": str(e)}), 500


@recruiter_bp.route("/candidates/<candidate_id>", methods=["GET"])
def get_candidate(candidate_id):
    db = _db()
    if not db:
        return jsonify({"error": "Database not available"}), 500
    try:
        c = db.users.find_one({"_id": ObjectId(candidate_id)})
        if not c:
            return jsonify({"error": "Candidate not found"}), 404
        c.pop("password", None)
        _to_str(c)
        return jsonify({"candidate": c}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ════════════════════════════════════════════════════════
# RESUME MATCHING
# ════════════════════════════════════════════════════════

@recruiter_bp.route("/match-resume-file", methods=["POST"])
def match_resume_file():
    """
    ResumeMatching.js  →  POST /api/recruiter/match-resume-file
    Accepts: multipart/form-data  { resume: File, job_id: str, job_description: str }
    """
    jm, rm, _, cp, _ = _components()

    if "resume" not in request.files:
        return jsonify({"error": "No resume file uploaded"}), 400

    file       = request.files["resume"]
    job_id     = request.form.get("job_id", "")
    job_desc   = request.form.get("job_description", "")

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400
    if not _allowed(file.filename):
        return jsonify({"error": "Only PDF, DOC, DOCX files allowed"}), 400

    # Save temporarily
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    try:
        # Parse resume
        resume_data = cp.parse_resume(filepath)

        # Get job context
        job = jm.get_job_by_id(job_id) if job_id else None
        if not job and job_desc:
            job = {
                "title": "Custom Job",
                "description": job_desc,
                "requirements": job_desc,
                "skills": [],
            }

        if not job:
            return jsonify({"error": "Provide job_id or job_description"}), 400

        # Score
        result = rm.calculate_match_score(resume_data, job)

        # Enrich with parsed fields
        result["candidateName"]    = resume_data.get("name", "Unknown")
        result["matchedSkillsList"] = result.get("matchedSkills", [])
        result["missingSkillsList"] = result.get("missingSkills", [])

        # Map to what ResumeMatching.js expects
        response = {
            "match_score":              result.get("overallScore", result.get("matchScore", 0)),
            "matched_skills":           result.get("matchedSkills", []),
            "missing_skills":           result.get("missingSkills", []),
            "experience_match":         result.get("experienceMatch", 70),
            "education_match":          result.get("educationMatch", 70),
            "overall_recommendation":   result.get("recommendation", "Consider"),
            "candidate_name":           result.get("candidateName", "Unknown"),
            "key_strengths":            _build_strengths(result),
            "areas_for_improvement":    _build_improvements(result),
            "score_breakdown": {
                "skills":     result.get("skillsMatch", 0),
                "experience": result.get("experienceMatch", 0),
                "education":  result.get("educationMatch", 0),
                "semantic":   result.get("semanticMatch", 0),
            },
        }

        return jsonify(response), 200

    except Exception as e:
        logger.error(f"match_resume_file error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)


@recruiter_bp.route("/match-resumes", methods=["POST"])
def match_resumes_to_job():
    """Bulk match all (or specific) candidates to a job."""
    jm, rm, cr, _, _ = _components()
    db = _db()
    if not db:
        return jsonify({"error": "Database not available"}), 500

    data          = request.json or {}
    job_id        = data.get("jobId")
    candidate_ids = data.get("candidateIds", [])

    if not job_id:
        return jsonify({"error": "jobId required"}), 400

    job = jm.get_job_by_id(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404

    try:
        if candidate_ids:
            oids       = [ObjectId(cid) for cid in candidate_ids]
            candidates = list(db.users.find({"_id": {"$in": oids}}))
        else:
            candidates = list(db.users.find({"role": "candidate"}))

        for c in candidates:
            c.pop("password", None)
            _to_str(c)

        matched = rm.match_candidates_to_job(job, candidates)
        ranked  = cr.rank_candidates(matched)

        return jsonify({"matches": ranked, "count": len(ranked)}), 200

    except Exception as e:
        logger.error(f"match_resumes_to_job error: {e}")
        return jsonify({"error": str(e)}), 500


# ════════════════════════════════════════════════════════
# SHORTLIST MANAGEMENT
# ════════════════════════════════════════════════════════

@recruiter_bp.route("/shortlist", methods=["POST"])
def add_to_shortlist():
    """
    ShortlistManager / CandidateSearch  →  POST /api/recruiter/shortlist
    Body: { jobId, candidateId, recruiterId, notes?, matchScore?, sendEmail? }
    """
    jm, _, _, _, en = _components()
    db = _db()

    data = request.json or {}
    for f in ("jobId", "candidateId", "recruiterId"):
        if f not in data:
            return jsonify({"error": f"Missing field: {f}"}), 400

    try:
        sl_id = jm.add_to_shortlist(data)

        # Optional email
        if data.get("sendEmail") and db:
            try:
                candidate = db.users.find_one({"_id": ObjectId(data["candidateId"])})
                job       = jm.get_job_by_id(data["jobId"])
                if candidate and job:
                    en.send_shortlist_email(candidate, job)
            except Exception as email_err:
                logger.warning(f"Email notification failed: {email_err}")

        return jsonify({"message": "Candidate shortlisted", "shortlistId": sl_id}), 201

    except Exception as e:
        logger.error(f"add_to_shortlist error: {e}")
        return jsonify({"error": str(e)}), 500


@recruiter_bp.route("/shortlist", methods=["GET"])
def get_shortlist():
    """ShortlistManager.js  →  GET /api/recruiter/shortlist?recruiterId=<id>"""
    jm, *_ = _components()
    recruiter_id = request.args.get("recruiterId")
    if not recruiter_id:
        return jsonify({"error": "recruiterId required"}), 400
    try:
        candidates = jm.get_shortlist_by_recruiter(recruiter_id)
        return jsonify({"candidates": candidates, "count": len(candidates)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@recruiter_bp.route("/shortlist/<shortlist_id>", methods=["DELETE"])
def remove_from_shortlist(shortlist_id):
    """ShortlistManager.js  →  DELETE /api/recruiter/shortlist/<id>"""
    jm, *_ = _components()
    ok = jm.remove_from_shortlist(shortlist_id)
    if not ok:
        return jsonify({"error": "Entry not found"}), 404
    return jsonify({"message": "Removed from shortlist"}), 200


@recruiter_bp.route("/shortlist/<shortlist_id>/status", methods=["PUT"])
def update_shortlist_status(shortlist_id):
    """ShortlistManager.js  →  PUT /api/recruiter/shortlist/<id>/status"""
    jm, *_ = _components()
    data   = request.json or {}
    status = data.get("status")
    if not status:
        return jsonify({"error": "status required"}), 400

    extra = {}
    if data.get("interviewDate"):
        extra["interviewDate"] = data["interviewDate"]

    ok = jm.update_shortlist_status(shortlist_id, status, extra)
    if not ok:
        return jsonify({"error": "Update failed or entry not found"}), 404
    return jsonify({"message": "Status updated"}), 200


# ════════════════════════════════════════════════════════
# ANALYTICS
# ════════════════════════════════════════════════════════

@recruiter_bp.route("/analytics", methods=["GET"])
def get_analytics():
    """GET /api/recruiter/analytics?recruiterId=<id>"""
    jm, *_ = _components()
    recruiter_id = request.args.get("recruiterId")
    if not recruiter_id:
        return jsonify({"error": "recruiterId required"}), 400
    try:
        return jsonify({
            "analytics": {
                "totalJobs":         jm.count_jobs_by_recruiter(recruiter_id),
                "activeJobs":        jm.count_active_jobs(recruiter_id),
                "totalShortlisted":  jm.count_shortlisted_candidates(recruiter_id),
                "totalInterviewed":  jm.count_interviewed(recruiter_id),
                "recentActivity":    jm.get_recent_activity(recruiter_id),
            }
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ════════════════════════════════════════════════════════
# BACKWARD-COMPAT FLAT ROUTES  (called by old frontend)
# These mirror the original flat URL paths the JS files call
# e.g. CandidateSearch.js uses /search_candidates not /api/recruiter/…
# ════════════════════════════════════════════════════════

@recruiter_bp.route("/compat/recruiter_dashboard", methods=["GET"])
def compat_dashboard():
    """Flat: GET /recruiter_dashboard"""
    recruiter_id = request.args.get("recruiter_id", "")
    jm, *_ = _components()
    stats       = jm.get_dashboard_stats(recruiter_id)
    recent_jobs = jm.get_jobs_by_recruiter(recruiter_id)[:5]
    return jsonify({"stats": stats, "recent_jobs": recent_jobs}), 200


# ════════════════════════════════════════════════════════
# INTERNAL HELPERS
# ════════════════════════════════════════════════════════

def _build_strengths(result: dict) -> list:
    strengths = []
    if result.get("skillsMatch", 0) >= 70:
        strengths.append("Strong skills alignment with job requirements")
    if result.get("experienceMatch", 0) >= 75:
        strengths.append("Relevant work experience matches role needs")
    if result.get("educationMatch", 0) >= 80:
        strengths.append("Educational background meets requirements")
    if result.get("semanticMatch", 0) >= 70:
        strengths.append("Overall profile closely matches job description")
    if not strengths:
        strengths.append("Profile shows potential for the role")
    return strengths


def _build_improvements(result: dict) -> list:
    improvements = []
    missing = result.get("missingSkills", [])
    if missing:
        improvements.append(f"Missing key skills: {', '.join(missing[:3])}")
    if result.get("experienceMatch", 100) < 60:
        improvements.append("Limited relevant work experience for this level")
    if result.get("educationMatch", 100) < 60:
        improvements.append("Educational qualification may not fully meet requirements")
    if not improvements:
        improvements.append("No major gaps identified")
    return improvements
