from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
from bson import ObjectId
import os
import logging
from werkzeug.utils import secure_filename

# Import your custom modules (make sure they exist)
try:
    from resume_matcher import ResumeMatcher
    from candidate_ranker import CandidateRanker
    from job_manager import JobManager
    from candidate_parser import CandidateParser
    from email_notifier import EmailNotifier
except ImportError as e:
    logging.warning(f"Some modules not found: {e}")
    # Create dummy classes if imports fail
    class ResumeMatcher:
        def match_candidates_to_job(self, job, candidates): return []
        def calculate_match_score(self, resume, job): return 0
    
    class CandidateRanker:
        def rank_candidates(self, matches): return matches
    
    class JobManager:
        def __init__(self): 
            self.db = None
        def create_job(self, data): return "dummy_id"
        def get_jobs_by_recruiter(self, recruiter_id): return []
        def get_job_by_id(self, job_id): return None
        def update_job(self, job_id, data): return False
        def delete_job(self, job_id): return False
        def add_to_shortlist(self, data): return "dummy_id"
        def get_shortlisted_candidates(self, job_id): return []
        def remove_from_shortlist(self, shortlist_id): return False
        def update_shortlist_status(self, shortlist_id, status): return False
        def count_jobs_by_recruiter(self, recruiter_id): return 0
        def count_active_jobs(self, recruiter_id): return 0
        def count_shortlisted_candidates(self, recruiter_id): return 0
        def get_recent_activity(self, recruiter_id): return []
    
    class CandidateParser:
        def parse_resume(self, filepath): return {}
    
    class EmailNotifier:
        def send_shortlist_email(self, candidate, job): pass

logger = logging.getLogger(__name__)

# Create blueprint ONCE at module level
recruiter_bp = Blueprint('recruiter', __name__)

# Initialize components (lazy loading)
_job_manager = None
_resume_matcher = None
_candidate_ranker = None
_candidate_parser = None
_email_notifier = None

def get_components():
    """Lazy initialize components"""
    global _job_manager, _resume_matcher, _candidate_ranker, _candidate_parser, _email_notifier
    
    if _job_manager is None:
        _job_manager = JobManager()
    if _resume_matcher is None:
        _resume_matcher = ResumeMatcher()
    if _candidate_ranker is None:
        _candidate_ranker = CandidateRanker()
    if _candidate_parser is None:
        _candidate_parser = CandidateParser()
    if _email_notifier is None:
        _email_notifier = EmailNotifier()
    
    return _job_manager, _resume_matcher, _candidate_ranker, _candidate_parser, _email_notifier

UPLOAD_FOLDER = 'uploads/resumes'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db():
    """Safely get database connection"""
    try:
        db = current_app.config.get('db')
        if db is None:
            logger.warning("Database connection not initialized")
            return None
        return db
    except RuntimeError:
        logger.error("Working outside application context")
        return None

# ============ JOB POSTING ROUTES ============

@recruiter_bp.route('/jobs', methods=['POST'])
def create_job():
    """Create a new job posting"""
    try:
        job_manager, _, _, _, _ = get_components()
        data = request.json
        
        # Validate required fields
        required_fields = ['title', 'company', 'description', 'requirements', 'recruiterId']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create job
        job_id = job_manager.create_job(data)
        
        return jsonify({
            'message': 'Job created successfully',
            'jobId': str(job_id)
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating job: {e}")
        return jsonify({'error': str(e)}), 500


@recruiter_bp.route('/jobs', methods=['GET'])
def get_jobs():
    """Get all jobs for a recruiter"""
    try:
        job_manager, _, _, _, _ = get_components()
        recruiter_id = request.args.get('recruiterId')
        
        if not recruiter_id:
            return jsonify({'error': 'Recruiter ID required'}), 400
        
        jobs = job_manager.get_jobs_by_recruiter(recruiter_id)
        
        return jsonify({
            'jobs': jobs,
            'count': len(jobs)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting jobs: {e}")
        return jsonify({'error': str(e)}), 500


@recruiter_bp.route('/jobs/<job_id>', methods=['GET'])
def get_job(job_id):
    """Get a specific job by ID"""
    try:
        job_manager, _, _, _, _ = get_components()
        job = job_manager.get_job_by_id(job_id)
        
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        return jsonify({'job': job}), 200
        
    except Exception as e:
        logger.error(f"Error getting job: {e}")
        return jsonify({'error': str(e)}), 500


@recruiter_bp.route('/jobs/<job_id>', methods=['PUT'])
def update_job(job_id):
    """Update a job posting"""
    try:
        job_manager, _, _, _, _ = get_components()
        data = request.json
        
        success = job_manager.update_job(job_id, data)
        
        if not success:
            return jsonify({'error': 'Job not found or update failed'}), 404
        
        return jsonify({'message': 'Job updated successfully'}), 200
        
    except Exception as e:
        logger.error(f"Error updating job: {e}")
        return jsonify({'error': str(e)}), 500


@recruiter_bp.route('/jobs/<job_id>', methods=['DELETE'])
def delete_job(job_id):
    """Delete a job posting"""
    try:
        job_manager, _, _, _, _ = get_components()
        success = job_manager.delete_job(job_id)
        
        if not success:
            return jsonify({'error': 'Job not found'}), 404
        
        return jsonify({'message': 'Job deleted successfully'}), 200
        
    except Exception as e:
        logger.error(f"Error deleting job: {e}")
        return jsonify({'error': str(e)}), 500


# ============ CANDIDATE SEARCH ROUTES ============

@recruiter_bp.route('/candidates/search', methods=['POST'])
def search_candidates():
    """Search candidates based on filters"""
    try:
        db = get_db()
        if not db:
            return jsonify({'error': 'Database not available'}), 500
        
        filters = request.json
        
        # Get all candidates
        candidates = get_all_candidates_from_db(db)
        
        # Apply filters
        filtered_candidates = apply_filters(candidates, filters)
        
        return jsonify({
            'candidates': filtered_candidates,
            'count': len(filtered_candidates)
        }), 200
        
    except Exception as e:
        logger.error(f"Error searching candidates: {e}")
        return jsonify({'error': str(e)}), 500


@recruiter_bp.route('/candidates/<candidate_id>', methods=['GET'])
def get_candidate_details(candidate_id):
    """Get detailed candidate profile"""
    try:
        db = get_db()
        if not db:
            return jsonify({'error': 'Database not available'}), 500
        
        candidate = get_candidate_from_db(db, candidate_id)
        
        if not candidate:
            return jsonify({'error': 'Candidate not found'}), 404
        
        return jsonify({'candidate': candidate}), 200
        
    except Exception as e:
        logger.error(f"Error getting candidate: {e}")
        return jsonify({'error': str(e)}), 500


# ============ RESUME MATCHING ROUTES ============

@recruiter_bp.route('/match-resumes', methods=['POST'])
def match_resumes_to_job():
    """Match candidates to a job description"""
    try:
        job_manager, resume_matcher, candidate_ranker, _, _ = get_components()
        db = get_db()
        if not db:
            return jsonify({'error': 'Database not available'}), 500
        
        data = request.json
        job_id = data.get('jobId')
        candidate_ids = data.get('candidateIds', [])
        
        if not job_id:
            return jsonify({'error': 'Job ID required'}), 400
        
        # Get job details
        job = job_manager.get_job_by_id(job_id)
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        # Get candidates
        candidates = get_candidates_by_ids(db, candidate_ids) if candidate_ids else get_all_candidates_from_db(db)
        
        # Match resumes
        matched_results = resume_matcher.match_candidates_to_job(job, candidates)
        
        # Rank candidates
        ranked_candidates = candidate_ranker.rank_candidates(matched_results)
        
        return jsonify({
            'matches': ranked_candidates,
            'count': len(ranked_candidates)
        }), 200
        
    except Exception as e:
        logger.error(f"Error matching resumes: {e}")
        return jsonify({'error': str(e)}), 500


@recruiter_bp.route('/match-resume-file', methods=['POST'])
def match_uploaded_resume():
    """Match a single uploaded resume to job"""
    try:
        job_manager, resume_matcher, _, candidate_parser, _ = get_components()
        
        if 'resume' not in request.files:
            return jsonify({'error': 'No resume file uploaded'}), 400
        
        file = request.files['resume']
        job_id = request.form.get('jobId')
        
        if not job_id:
            return jsonify({'error': 'Job ID required'}), 400
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Only PDF, DOC, DOCX allowed'}), 400
        
        # Save file
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Parse resume
        resume_data = candidate_parser.parse_resume(filepath)
        
        # Get job
        job = job_manager.get_job_by_id(job_id)
        
        # Match
        match_score = resume_matcher.calculate_match_score(resume_data, job)
        
        # Clean up
        if os.path.exists(filepath):
            os.remove(filepath)
        
        return jsonify({
            'matchScore': match_score,
            'resumeData': resume_data
        }), 200
        
    except Exception as e:
        logger.error(f"Error matching uploaded resume: {e}")
        return jsonify({'error': str(e)}), 500


# ============ SHORTLIST MANAGEMENT ROUTES ============

@recruiter_bp.route('/shortlist', methods=['POST'])
def add_to_shortlist():
    """Add candidate to shortlist"""
    try:
        job_manager, _, _, _, email_notifier = get_components()
        db = get_db()
        if not db:
            return jsonify({'error': 'Database not available'}), 500
        
        data = request.json
        
        required_fields = ['jobId', 'candidateId', 'recruiterId']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        shortlist_id = job_manager.add_to_shortlist(data)
        
        # Send email notification (optional)
        if data.get('sendEmail', False):
            candidate = get_candidate_from_db(db, data['candidateId'])
            job = job_manager.get_job_by_id(data['jobId'])
            email_notifier.send_shortlist_email(candidate, job)
        
        return jsonify({
            'message': 'Candidate shortlisted successfully',
            'shortlistId': str(shortlist_id)
        }), 201
        
    except Exception as e:
        logger.error(f"Error adding to shortlist: {e}")
        return jsonify({'error': str(e)}), 500


@recruiter_bp.route('/shortlist/<job_id>', methods=['GET'])
def get_shortlisted_candidates(job_id):
    """Get all shortlisted candidates for a job"""
    try:
        job_manager, _, _, _, _ = get_components()
        shortlisted = job_manager.get_shortlisted_candidates(job_id)
        
        return jsonify({
            'shortlisted': shortlisted,
            'count': len(shortlisted)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting shortlisted candidates: {e}")
        return jsonify({'error': str(e)}), 500


@recruiter_bp.route('/shortlist/<shortlist_id>', methods=['DELETE'])
def remove_from_shortlist(shortlist_id):
    """Remove candidate from shortlist"""
    try:
        job_manager, _, _, _, _ = get_components()
        success = job_manager.remove_from_shortlist(shortlist_id)
        
        if not success:
            return jsonify({'error': 'Shortlist entry not found'}), 404
        
        return jsonify({'message': 'Candidate removed from shortlist'}), 200
        
    except Exception as e:
        logger.error(f"Error removing from shortlist: {e}")
        return jsonify({'error': str(e)}), 500


@recruiter_bp.route('/shortlist/<shortlist_id>/status', methods=['PUT'])
def update_shortlist_status(shortlist_id):
    """Update candidate status in shortlist"""
    try:
        job_manager, _, _, _, _ = get_components()
        data = request.json
        status = data.get('status')
        
        if not status:
            return jsonify({'error': 'Status required'}), 400
        
        success = job_manager.update_shortlist_status(shortlist_id, status)
        
        if not success:
            return jsonify({'error': 'Update failed'}), 404
        
        return jsonify({'message': 'Status updated successfully'}), 200
        
    except Exception as e:
        logger.error(f"Error updating shortlist status: {e}")
        return jsonify({'error': str(e)}), 500


# ============ ANALYTICS ROUTES ============

@recruiter_bp.route('/analytics', methods=['GET'])
def get_recruiter_analytics():
    """Get recruiter dashboard analytics"""
    try:
        job_manager, _, _, _, _ = get_components()
        recruiter_id = request.args.get('recruiterId')
        
        if not recruiter_id:
            return jsonify({'error': 'Recruiter ID required'}), 400
        
        analytics = {
            'totalJobs': job_manager.count_jobs_by_recruiter(recruiter_id),
            'activeJobs': job_manager.count_active_jobs(recruiter_id),
            'totalShortlisted': job_manager.count_shortlisted_candidates(recruiter_id),
            'recentActivity': job_manager.get_recent_activity(recruiter_id)
        }
        
        return jsonify({'analytics': analytics}), 200
        
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        return jsonify({'error': str(e)}), 500


# ============ HELPER FUNCTIONS ============

def get_all_candidates_from_db(db):
    """Fetch all candidates from database"""
    try:
        candidates = list(db.users.find({'role': 'candidate'}))
        
        for candidate in candidates:
            candidate['_id'] = str(candidate['_id'])
        
        return candidates
    except Exception as e:
        logger.error(f"Error fetching candidates: {e}")
        return []


def get_candidate_from_db(db, candidate_id):
    """Fetch single candidate"""
    try:
        candidate = db.users.find_one({'_id': ObjectId(candidate_id)})
        if candidate:
            candidate['_id'] = str(candidate['_id'])
        return candidate
    except Exception as e:
        logger.error(f"Error fetching candidate: {e}")
        return None


def get_candidates_by_ids(db, candidate_ids):
    """Fetch multiple candidates by IDs"""
    try:
        object_ids = [ObjectId(cid) for cid in candidate_ids]
        candidates = list(db.users.find({'_id': {'$in': object_ids}}))
        
        for candidate in candidates:
            candidate['_id'] = str(candidate['_id'])
        
        return candidates
    except Exception as e:
        logger.error(f"Error fetching candidates by IDs: {e}")
        return []


def apply_filters(candidates, filters):
    """Apply search filters to candidates"""
    filtered = candidates
    
    # Filter by skills
    if filters.get('skills'):
        skills = [s.lower() for s in filters['skills']]
        filtered = [c for c in filtered if any(
            skill in [s.lower() for s in c.get('skills', [])] for skill in skills
        )]
    
    # Filter by experience
    if filters.get('minExperience') is not None:
        min_exp = filters['minExperience']
        filtered = [c for c in filtered if c.get('experience', 0) >= min_exp]
    
    # Filter by location
    if filters.get('location'):
        location = filters['location'].lower()
        filtered = [c for c in filtered if location in c.get('location', '').lower()]
    
    # Filter by education
    if filters.get('education'):
        education = filters['education'].lower()
        filtered = [c for c in filtered if education in c.get('education', '').lower()]
    
    return filtered