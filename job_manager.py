# job_manager.py
"""
Job & Shortlist Database Manager
Handles all MongoDB CRUD for jobs, shortlists, and recruiter stats.
Used by recruiter_engine.py Blueprint routes.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional

from bson import ObjectId
from flask import current_app

logger = logging.getLogger(__name__)


def _get_db():
    """Safely retrieve MongoDB from the Flask app context."""
    try:
        db = current_app.config.get("db")
        if db is None:
            logger.error("MongoDB not configured in app.config['db']")
        return db
    except RuntimeError:
        logger.error("Called outside of Flask application context")
        return None


def _to_str(doc: Dict) -> Dict:
    """Convert ObjectId fields to strings and datetime fields to ISO strings."""
    if doc is None:
        return doc
    doc["_id"] = str(doc["_id"])
    for key in ("createdAt", "updatedAt", "shortlistedAt", "interviewDate"):
        if key in doc and hasattr(doc[key], "isoformat"):
            doc[key] = doc[key].isoformat()
    return doc


class JobManager:
    """All database operations for jobs, shortlists, and recruiter analytics."""

    # ─────────────────────────────────────────────
    # JOB CRUD
    # ─────────────────────────────────────────────

    def create_job(self, data: Dict) -> str:
        """
        Insert a new job document.

        Required keys in `data`:
            title, company, description, requirements, recruiterId

        Returns:
            Inserted document _id as string.
        """
        db = _get_db()
        if db is None:
            raise RuntimeError("Database not available")

        job = {
            "title":          data["title"],
            "company":        data["company"],
            "location":       data.get("location", "Not specified"),
            "type":           data.get("type", "Full Time"),
            "experience":     data.get("experience", ""),
            "salary":         data.get("salary", "Competitive"),
            "description":    data["description"],
            "requirements":   data["requirements"],
            "skills":         data.get("skills", []),
            "recruiterId":    data["recruiterId"],
            "status":         "active",
            "applicants":     [],
            "shortlistCount": 0,
            "createdAt":      datetime.utcnow(),
            "updatedAt":      datetime.utcnow(),
        }

        result = db.jobs.insert_one(job)
        logger.info(f"Job created: {result.inserted_id}")
        return str(result.inserted_id)

    def get_jobs_by_recruiter(self, recruiter_id: str) -> List[Dict]:
        """Return all jobs posted by a recruiter, newest first."""
        db = _get_db()
        if db is None:
            return []

        jobs = list(db.jobs.find({"recruiterId": recruiter_id}).sort("createdAt", -1))
        for job in jobs:
            _to_str(job)
            job["applicantCount"] = len(job.get("applicants", []))
        return jobs

    def get_job_by_id(self, job_id: str) -> Optional[Dict]:
        """Return a single job document by its ID."""
        db = _get_db()
        if db is None:
            return None

        try:
            job = db.jobs.find_one({"_id": ObjectId(job_id)})
            if job:
                _to_str(job)
                job["applicantCount"] = len(job.get("applicants", []))
            return job
        except Exception as e:
            logger.error(f"get_job_by_id error: {e}")
            return None

    def update_job(self, job_id: str, data: Dict) -> bool:
        """
        Update a job's fields.
        Strips protected fields (_id, recruiterId, createdAt) from payload.
        Returns True if a document was matched.
        """
        db = _get_db()
        if db is None:
            return False

        # Prevent overwriting protected fields
        for key in ("_id", "recruiterId", "createdAt"):
            data.pop(key, None)

        data["updatedAt"] = datetime.utcnow()

        try:
            result = db.jobs.update_one(
                {"_id": ObjectId(job_id)},
                {"$set": data},
            )
            return result.matched_count > 0
        except Exception as e:
            logger.error(f"update_job error: {e}")
            return False

    def delete_job(self, job_id: str) -> bool:
        """Delete a job and its shortlist entries. Returns True if deleted."""
        db = _get_db()
        if db is None:
            return False

        try:
            result = db.jobs.delete_one({"_id": ObjectId(job_id)})
            if result.deleted_count > 0:
                # Clean up related shortlist entries
                db.shortlist.delete_many({"jobId": job_id})
                logger.info(f"Job deleted: {job_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"delete_job error: {e}")
            return False

    def toggle_job_status(self, job_id: str) -> Optional[str]:
        """Toggle job between 'active' and 'closed'. Returns new status."""
        job = self.get_job_by_id(job_id)
        if not job:
            return None
        new_status = "closed" if job.get("status") == "active" else "active"
        self.update_job(job_id, {"status": new_status})
        return new_status

    # ─────────────────────────────────────────────
    # SHORTLIST CRUD
    # ─────────────────────────────────────────────

    def add_to_shortlist(self, data: Dict) -> str:
        """
        Add a candidate to the shortlist.

        Required keys: jobId, candidateId, recruiterId

        Returns:
            Inserted _id as string.
        """
        db = _get_db()
        if db is None:
            raise RuntimeError("Database not available")

        # Prevent duplicates
        existing = db.shortlist.find_one({
            "jobId":       data["jobId"],
            "candidateId": data["candidateId"],
        })
        if existing:
            return str(existing["_id"])

        shortlist_doc = {
            "jobId":          data["jobId"],
            "candidateId":    data["candidateId"],
            "recruiterId":    data["recruiterId"],
            "status":         data.get("status", "shortlisted"),
            "notes":          data.get("notes", ""),
            "matchScore":     data.get("matchScore", 0),
            "shortlistedAt":  datetime.utcnow(),
            "interviewDate":  None,
        }

        result = db.shortlist.insert_one(shortlist_doc)

        # Increment shortlistCount on the job
        try:
            db.jobs.update_one(
                {"_id": ObjectId(data["jobId"])},
                {"$inc": {"shortlistCount": 1}},
            )
        except Exception:
            pass

        return str(result.inserted_id)

    def get_shortlisted_candidates(self, job_id: str) -> List[Dict]:
        """
        Return shortlisted candidates for a job,
        with candidate & job details embedded.
        """
        db = _get_db()
        if db is None:
            return []

        entries = list(db.shortlist.find({"jobId": job_id}).sort("shortlistedAt", -1))
        return self._enrich_shortlist(db, entries)

    def get_shortlist_by_recruiter(self, recruiter_id: str) -> List[Dict]:
        """Return all shortlisted candidates for a recruiter."""
        db = _get_db()
        if db is None:
            return []

        entries = list(
            db.shortlist.find({"recruiterId": recruiter_id}).sort("shortlistedAt", -1)
        )
        return self._enrich_shortlist(db, entries)

    def remove_from_shortlist(self, shortlist_id: str) -> bool:
        """Remove a shortlist entry by its _id."""
        db = _get_db()
        if db is None:
            return False

        try:
            entry = db.shortlist.find_one({"_id": ObjectId(shortlist_id)})
            result = db.shortlist.delete_one({"_id": ObjectId(shortlist_id)})
            if result.deleted_count > 0 and entry:
                # Decrement counter on the job
                try:
                    db.jobs.update_one(
                        {"_id": ObjectId(entry["jobId"])},
                        {"$inc": {"shortlistCount": -1}},
                    )
                except Exception:
                    pass
                return True
            return False
        except Exception as e:
            logger.error(f"remove_from_shortlist error: {e}")
            return False

    def update_shortlist_status(self, shortlist_id: str, status: str, extra: Dict = None) -> bool:
        """
        Update a shortlist entry's status.

        Valid statuses: shortlisted, contacted, interview_scheduled, hired, rejected
        Optional `extra` dict can carry interviewDate etc.
        """
        db = _get_db()
        if db is None:
            return False

        VALID = {"shortlisted", "contacted", "interview_scheduled", "hired", "rejected"}
        if status not in VALID:
            logger.warning(f"Invalid shortlist status: {status}")
            return False

        update_data = {"status": status, "updatedAt": datetime.utcnow()}
        if extra:
            update_data.update(extra)

        try:
            result = db.shortlist.update_one(
                {"_id": ObjectId(shortlist_id)},
                {"$set": update_data},
            )
            return result.matched_count > 0
        except Exception as e:
            logger.error(f"update_shortlist_status error: {e}")
            return False

    # ─────────────────────────────────────────────
    # ANALYTICS
    # ─────────────────────────────────────────────

    def count_jobs_by_recruiter(self, recruiter_id: str) -> int:
        db = _get_db()
        if db is None:
            return 0
        return db.jobs.count_documents({"recruiterId": recruiter_id})

    def count_active_jobs(self, recruiter_id: str) -> int:
        db = _get_db()
        if db is None:
            return 0
        return db.jobs.count_documents({"recruiterId": recruiter_id, "status": "active"})

    def count_shortlisted_candidates(self, recruiter_id: str) -> int:
        db = _get_db()
        if db is None:
            return 0
        return db.shortlist.count_documents({"recruiterId": recruiter_id})

    def count_interviewed(self, recruiter_id: str) -> int:
        db = _get_db()
        if db is None:
            return 0
        return db.shortlist.count_documents({
            "recruiterId": recruiter_id,
            "status": {"$in": ["interview_scheduled", "hired"]},
        })

    def count_hired(self, recruiter_id: str) -> int:
        db = _get_db()
        if db is None:
            return 0
        return db.shortlist.count_documents({"recruiterId": recruiter_id, "status": "hired"})

    def get_recent_activity(self, recruiter_id: str, limit: int = 10) -> List[Dict]:
        """Return recent jobs and shortlist events for the activity feed."""
        db = _get_db()
        if db is None:
            return []

        activities = []

        # Recent jobs
        recent_jobs = list(
            db.jobs.find({"recruiterId": recruiter_id})
            .sort("createdAt", -1)
            .limit(limit // 2)
        )
        for job in recent_jobs:
            activities.append({
                "type":      "job_posted",
                "title":     f"Posted: {job.get('title', 'Job')}",
                "timestamp": job["createdAt"].isoformat() if "createdAt" in job else "",
                "jobId":     str(job["_id"]),
            })

        # Recent shortlists
        recent_sl = list(
            db.shortlist.find({"recruiterId": recruiter_id})
            .sort("shortlistedAt", -1)
            .limit(limit // 2)
        )
        for sl in recent_sl:
            activities.append({
                "type":        "candidate_shortlisted",
                "title":       f"Shortlisted candidate for job",
                "timestamp":   sl["shortlistedAt"].isoformat() if "shortlistedAt" in sl else "",
                "candidateId": sl.get("candidateId", ""),
            })

        # Sort combined list by timestamp descending
        activities.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return activities[:limit]

    def get_dashboard_stats(self, recruiter_id: str) -> Dict:
        """Return all stats needed for the RecruiterDashboard component."""
        return {
            "activeJobs":        self.count_active_jobs(recruiter_id),
            "totalCandidates":   self.count_shortlisted_candidates(recruiter_id),
            "shortlisted":       self.count_shortlisted_candidates(recruiter_id),
            "interviewed":       self.count_interviewed(recruiter_id),
            "hired":             self.count_hired(recruiter_id),
            "totalJobs":         self.count_jobs_by_recruiter(recruiter_id),
        }

    # ─────────────────────────────────────────────
    # CANDIDATE APPLICATION
    # ─────────────────────────────────────────────

    def add_applicant_to_job(self, job_id: str, applicant_info: Dict) -> bool:
        """Push an applicant entry into a job's `applicants` array."""
        db = _get_db()
        if db is None:
            return False
        try:
            applicant_info["appliedAt"] = datetime.utcnow().isoformat()
            result = db.jobs.update_one(
                {"_id": ObjectId(job_id)},
                {"$push": {"applicants": applicant_info}},
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"add_applicant_to_job error: {e}")
            return False

    # ─────────────────────────────────────────────
    # PRIVATE HELPERS
    # ─────────────────────────────────────────────

    def _enrich_shortlist(self, db, entries: List[Dict]) -> List[Dict]:
        """Embed candidate and job details into shortlist entries."""
        enriched = []
        for entry in entries:
            _to_str(entry)

            # Embed candidate profile
            try:
                candidate = db.users.find_one({"_id": ObjectId(entry["candidateId"])})
                if candidate:
                    candidate.pop("password", None)
                    _to_str(candidate)
                    entry["candidate"] = candidate
            except Exception:
                entry["candidate"] = None

            # Embed job summary
            try:
                job = db.jobs.find_one({"_id": ObjectId(entry["jobId"])})
                if job:
                    entry["job"] = {
                        "_id":     str(job["_id"]),
                        "title":   job.get("title"),
                        "company": job.get("company"),
                    }
            except Exception:
                entry["job"] = None

            enriched.append(entry)
        return enriched
