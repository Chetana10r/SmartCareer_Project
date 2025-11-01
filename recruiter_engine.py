from flask import Blueprint, request, jsonify
from datetime import datetime
from bson import ObjectId
import os
from werkzeug.utils import secure_filename
from resume_matcher import ResumeMatcher
from candidate_ranker import CandidateRanker
from job_manager import JobManager
from candidate_parser import CandidateParser
from email_notifier import EmailNotifier

recruiter_bp = Blueprint('recruiter', __name__)

# Initialize components
job_manager = JobManager()
resume_matcher = ResumeMatcher()
candidate_ranker = CandidateRanker()
candidate_parser = CandidateParser()
email_notifier = EmailNotifier()

UPLOAD_FOLDER = 'uploads/resumes'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ============ JOB POSTING ROUTES ============

@recruiter_bp.route('/api/recruiter/jobs', methods=['POST'])
def create_job():
    """Create a new job posting"""
    try:
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
        return jsonify({'error': str(e)}), 500


@recruiter_bp.route('/api/recruiter/jobs', methods=['GET'])
def get_jobs():
    """Get all jobs for a recruiter"""
    try:
        recruiter_id = request.args.get('recruiterId')
        
        if not recruiter_id:
            return jsonify({'error': 'Recruiter ID required'}), 400
        
        jobs = job_manager.get_jobs_by_recruiter(recruiter_id)
        
        return jsonify({
            'jobs': jobs,
            'count': len(jobs)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@recruiter_bp.route('/api/recruiter/jobs/<job_id>', methods=['GET'])
def get_job(job_id):
    """Get a specific job by ID"""
    try:
        job = job_manager.get_job_by_id(job_id)
        
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        return jsonify({'job': job}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@recruiter_bp.route('/api/recruiter/jobs/<job_id>', methods=['PUT'])
def update_job(job_id):
    """Update a job posting"""
    try:
        data = request.json
        
        success = job_manager.update_job(job_id, data)
        
        if not success:
            return jsonify({'error': 'Job not found or update failed'}), 404
        
        return jsonify({'message': 'Job updated successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@recruiter_bp.route('/api/recruiter/jobs/<job_id>', methods=['DELETE'])
def delete_job(job_id):
    """Delete a job posting"""
    try:
        success = job_manager.delete_job(job_id)
        
        if not success:
            return jsonify({'error': 'Job not found'}), 404
        
        return jsonify({'message': 'Job deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============ CANDIDATE SEARCH ROUTES ============

@recruiter_bp.route('/api/recruiter/candidates/search', methods=['POST'])
def search_candidates():
    """Search candidates based on filters"""
    try:
        filters = request.json
        
        # Get all candidates (you'll need to implement this based on your DB)
        candidates = get_all_candidates_from_db()
        
        # Apply filters
        filtered_candidates = apply_filters(candidates, filters)
        
        return jsonify({
            'candidates': filtered_candidates,
            'count': len(filtered_candidates)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@recruiter_bp.route('/api/recruiter/candidates/<candidate_id>', methods=['GET'])
def get_candidate_details(candidate_id):
    """Get detailed candidate profile"""
    try:
        # Fetch from your users/candidates database
        candidate = get_candidate_from_db(candidate_id)
        
        if not candidate:
            return jsonify({'error': 'Candidate not found'}), 404
        
        return jsonify({'candidate': candidate}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============ RESUME MATCHING ROUTES ============

@recruiter_bp.route('/api/recruiter/match-resumes', methods=['POST'])
def match_resumes_to_job():
    """Match candidates to a job description"""
    try:
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
        candidates = get_candidates_by_ids(candidate_ids) if candidate_ids else get_all_candidates_from_db()
        
        # Match resumes
        matched_results = resume_matcher.match_candidates_to_job(job, candidates)
        
        # Rank candidates
        ranked_candidates = candidate_ranker.rank_candidates(matched_results)
        
        return jsonify({
            'matches': ranked_candidates,
            'count': len(ranked_candidates)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@recruiter_bp.route('/api/recruiter/match-resume-file', methods=['POST'])
def match_uploaded_resume():
    """Match a single uploaded resume to job"""
    try:
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
        os.remove(filepath)
        
        return jsonify({
            'matchScore': match_score,
            'resumeData': resume_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============ SHORTLIST MANAGEMENT ROUTES ============

@recruiter_bp.route('/api/recruiter/shortlist', methods=['POST'])
def add_to_shortlist():
    """Add candidate to shortlist"""
    try:
        data = request.json
        
        required_fields = ['jobId', 'candidateId', 'recruiterId']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        shortlist_id = job_manager.add_to_shortlist(data)
        
        # Send email notification (optional)
        if data.get('sendEmail', False):
            candidate = get_candidate_from_db(data['candidateId'])
            job = job_manager.get_job_by_id(data['jobId'])
            email_notifier.send_shortlist_email(candidate, job)
        
        return jsonify({
            'message': 'Candidate shortlisted successfully',
            'shortlistId': str(shortlist_id)
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@recruiter_bp.route('/api/recruiter/shortlist/<job_id>', methods=['GET'])
def get_shortlisted_candidates(job_id):
    """Get all shortlisted candidates for a job"""
    try:
        shortlisted = job_manager.get_shortlisted_candidates(job_id)
        
        return jsonify({
            'shortlisted': shortlisted,
            'count': len(shortlisted)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@recruiter_bp.route('/api/recruiter/shortlist/<shortlist_id>', methods=['DELETE'])
def remove_from_shortlist(shortlist_id):
    """Remove candidate from shortlist"""
    try:
        success = job_manager.remove_from_shortlist(shortlist_id)
        
        if not success:
            return jsonify({'error': 'Shortlist entry not found'}), 404
        
        return jsonify({'message': 'Candidate removed from shortlist'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@recruiter_bp.route('/api/recruiter/shortlist/<shortlist_id>/status', methods=['PUT'])
def update_shortlist_status(shortlist_id):
    """Update candidate status in shortlist"""
    try:
        data = request.json
        status = data.get('status')
        
        if not status:
            return jsonify({'error': 'Status required'}), 400
        
        success = job_manager.update_shortlist_status(shortlist_id, status)
        
        if not success:
            return jsonify({'error': 'Update failed'}), 404
        
        return jsonify({'message': 'Status updated successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============ ANALYTICS ROUTES ============

@recruiter_bp.route('/api/recruiter/analytics', methods=['GET'])
def get_recruiter_analytics():
    """Get recruiter dashboard analytics"""
    try:
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
        return jsonify({'error': str(e)}), 500


# ============ HELPER FUNCTIONS ============

def get_all_candidates_from_db():
    """Fetch all candidates from database"""
    # TODO: Implement based on your database structure
    # This should query your users collection where role='candidate'
    from app import get_db
    db = get_db()
    candidates = list(db.users.find({'role': 'candidate'}))
    
    for candidate in candidates:
        candidate['_id'] = str(candidate['_id'])
    
    return candidates


def get_candidate_from_db(candidate_id):
    """Fetch single candidate"""
    from app import get_db
    db = get_db()
    
    try:
        candidate = db.users.find_one({'_id': ObjectId(candidate_id)})
        if candidate:
            candidate['_id'] = str(candidate['_id'])
        return candidate
    except:
        return None


def get_candidates_by_ids(candidate_ids):
    """Fetch multiple candidates by IDs"""
    from app import get_db
    db = get_db()
    
    object_ids = [ObjectId(cid) for cid in candidate_ids]
    candidates = list(db.users.find({'_id': {'$in': object_ids}}))
    
    for candidate in candidates:
        candidate['_id'] = str(candidate['_id'])
    
    return candidates


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