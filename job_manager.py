from datetime import datetime
from bson import ObjectId
from typing import Dict, List, Optional

class JobManager:
    def __init__(self):
        """Initialize Job Manager with database connection"""
        self.db = None
        self._init_db()
    
    def _init_db(self):
        """Initialize database connection"""
        try:
            from app import get_db
            self.db = get_db()
        except:
            print("Warning: Database connection not initialized")
    
    # ============ JOB CRUD OPERATIONS ============
    
    def create_job(self, job_data: Dict) -> str:
        """
        Create a new job posting
        
        Args:
            job_data: Job posting details
        
        Returns:
            Job ID
        """
        job = {
            'title': job_data.get('title'),
            'company': job_data.get('company'),
            'location': job_data.get('location', ''),
            'type': job_data.get('type', 'Full-time'),  # Full-time, Part-time, Contract
            'mode': job_data.get('mode', 'Hybrid'),  # Remote, Hybrid, On-site
            'description': job_data.get('description'),
            'requirements': job_data.get('requirements'),
            'responsibilities': job_data.get('responsibilities', ''),
            'skills': job_data.get('skills', []),
            'experienceRequired': job_data.get('experienceRequired', 0),
            'educationRequired': job_data.get('educationRequired', ''),
            'salary': job_data.get('salary', {}),
            'benefits': job_data.get('benefits', []),
            'recruiterId': job_data.get('recruiterId'),
            'recruiterName': job_data.get('recruiterName', ''),
            'status': 'active',  # active, closed, draft
            'applicationsCount': 0,
            'shortlistedCount': 0,
            'createdAt': datetime.utcnow(),
            'updatedAt': datetime.utcnow(),
            'expiresAt': job_data.get('expiresAt'),
        }
        
        result = self.db.jobs.insert_one(job)
        return str(result.inserted_id)
    
    def get_job_by_id(self, job_id: str) -> Optional[Dict]:
        """Get job by ID"""
        try:
            job = self.db.jobs.find_one({'_id': ObjectId(job_id)})
            if job:
                job['_id'] = str(job['_id'])
                job['createdAt'] = job['createdAt'].isoformat() if 'createdAt' in job else None
                job['updatedAt'] = job['updatedAt'].isoformat() if 'updatedAt' in job else None
            return job
        except:
            return None
    
    def get_jobs_by_recruiter(self, recruiter_id: str) -> List[Dict]:
        """Get all jobs posted by a recruiter"""
        jobs = list(self.db.jobs.find({'recruiterId': recruiter_id}).sort('createdAt', -1))
        
        for job in jobs:
            job['_id'] = str(job['_id'])
            job['createdAt'] = job['createdAt'].isoformat() if 'createdAt' in job else None
            job['updatedAt'] = job['updatedAt'].isoformat() if 'updatedAt' in job else None
        
        return jobs
    
    def update_job(self, job_id: str, update_data: Dict) -> bool:
        """Update job posting"""
        try:
            update_data['updatedAt'] = datetime.utcnow()
            
            result = self.db.jobs.update_one(
                {'_id': ObjectId(job_id)},
                {'$set': update_data}
            )
            
            return result.modified_count > 0
        except:
            return False
    
    def delete_job(self, job_id: str) -> bool:
        """Delete job posting"""
        try:
            # Also delete all shortlist entries for this job
            self.db.shortlists.delete_many({'jobId': job_id})
            
            result = self.db.jobs.delete_one({'_id': ObjectId(job_id)})
            return result.deleted_count > 0
        except:
            return False
    
    def close_job(self, job_id: str) -> bool:
        """Close job posting (mark as closed but don't delete)"""
        return self.update_job(job_id, {'status': 'closed'})
    
    # ============ SHORTLIST OPERATIONS ============
    
    def add_to_shortlist(self, shortlist_data: Dict) -> str:
        """
        Add candidate to shortlist for a job
        
        Args:
            shortlist_data: Shortlist entry details
        
        Returns:
            Shortlist ID
        """
        # Check if already shortlisted
        existing = self.db.shortlists.find_one({
            'jobId': shortlist_data.get('jobId'),
            'candidateId': shortlist_data.get('candidateId')
        })
        
        if existing:
            return str(existing['_id'])
        
        shortlist_entry = {
            'jobId': shortlist_data.get('jobId'),
            'candidateId': shortlist_data.get('candidateId'),
            'recruiterId': shortlist_data.get('recruiterId'),
            'candidateName': shortlist_data.get('candidateName', ''),
            'candidateEmail': shortlist_data.get('candidateEmail', ''),
            'matchScore': shortlist_data.get('matchScore', 0),
            'status': 'shortlisted',  # shortlisted, interview_scheduled, selected, rejected
            'notes': shortlist_data.get('notes', ''),
            'createdAt': datetime.utcnow(),
            'updatedAt': datetime.utcnow()
        }
        
        result = self.db.shortlists.insert_one(shortlist_entry)
        
        # Update job's shortlisted count
        self.db.jobs.update_one(
            {'_id': ObjectId(shortlist_data.get('jobId'))},
            {'$inc': {'shortlistedCount': 1}}
        )
        
        return str(result.inserted_id)
    
    def get_shortlisted_candidates(self, job_id: str) -> List[Dict]:
        """Get all shortlisted candidates for a job"""
        shortlisted = list(self.db.shortlists.find({'jobId': job_id}).sort('matchScore', -1))
        
        for entry in shortlisted:
            entry['_id'] = str(entry['_id'])
            entry['createdAt'] = entry['createdAt'].isoformat() if 'createdAt' in entry else None
            entry['updatedAt'] = entry['updatedAt'].isoformat() if 'updatedAt' in entry else None
        
        return shortlisted
    
    def remove_from_shortlist(self, shortlist_id: str) -> bool:
        """Remove candidate from shortlist"""
        try:
            # Get shortlist entry to update job count
            entry = self.db.shortlists.find_one({'_id': ObjectId(shortlist_id)})
            
            if entry:
                # Delete shortlist entry
                result = self.db.shortlists.delete_one({'_id': ObjectId(shortlist_id)})
                
                # Update job's shortlisted count
                self.db.jobs.update_one(
                    {'_id': ObjectId(entry['jobId'])},
                    {'$inc': {'shortlistedCount': -1}}
                )
                
                return result.deleted_count > 0
            
            return False
        except:
            return False
    
    def update_shortlist_status(self, shortlist_id: str, status: str) -> bool:
        """Update shortlist entry status"""
        try:
            result = self.db.shortlists.update_one(
                {'_id': ObjectId(shortlist_id)},
                {
                    '$set': {
                        'status': status,
                        'updatedAt': datetime.utcnow()
                    }
                }
            )
            
            return result.modified_count > 0
        except:
            return False
    
    def add_shortlist_notes(self, shortlist_id: str, notes: str) -> bool:
        """Add notes to shortlist entry"""
        try:
            result = self.db.shortlists.update_one(
                {'_id': ObjectId(shortlist_id)},
                {
                    '$set': {
                        'notes': notes,
                        'updatedAt': datetime.utcnow()
                    }
                }
            )
            
            return result.modified_count > 0
        except:
            return False
    
    # ============ ANALYTICS & STATISTICS ============
    
    def count_jobs_by_recruiter(self, recruiter_id: str) -> int:
        """Count total jobs posted by recruiter"""
        return self.db.jobs.count_documents({'recruiterId': recruiter_id})
    
    def count_active_jobs(self, recruiter_id: str) -> int:
        """Count active jobs"""
        return self.db.jobs.count_documents({
            'recruiterId': recruiter_id,
            'status': 'active'
        })
    
    def count_shortlisted_candidates(self, recruiter_id: str) -> int:
        """Count total shortlisted candidates"""
        return self.db.shortlists.count_documents({'recruiterId': recruiter_id})
    
    def get_recent_activity(self, recruiter_id: str, limit: int = 5) -> List[Dict]:
        """Get recent activity for recruiter"""
        activities = []
        
        # Recent jobs
        recent_jobs = list(self.db.jobs.find(
            {'recruiterId': recruiter_id}
        ).sort('createdAt', -1).limit(limit))
        
        for job in recent_jobs:
            activities.append({
                'type': 'job_created',
                'title': job.get('title'),
                'timestamp': job.get('createdAt').isoformat() if 'createdAt' in job else None
            })
        
        # Recent shortlists
        recent_shortlists = list(self.db.shortlists.find(
            {'recruiterId': recruiter_id}
        ).sort('createdAt', -1).limit(limit))
        
        for entry in recent_shortlists:
            activities.append({
                'type': 'candidate_shortlisted',
                'candidateName': entry.get('candidateName'),
                'timestamp': entry.get('createdAt').isoformat() if 'createdAt' in entry else None
            })
        
        # Sort by timestamp and limit
        activities.sort(key=lambda x: x['timestamp'], reverse=True)
        return activities[:limit]
    
    def get_job_statistics(self, job_id: str) -> Dict:
        """Get statistics for a specific job"""
        job = self.get_job_by_id(job_id)
        
        if not job:
            return {}
        
        shortlisted_count = self.db.shortlists.count_documents({'jobId': job_id})
        
        # Get status distribution
        status_counts = {}
        pipeline = [
            {'$match': {'jobId': job_id}},
            {'$group': {
                '_id': '$status',
                'count': {'$sum': 1}
            }}
        ]
        
        for result in self.db.shortlists.aggregate(pipeline):
            status_counts[result['_id']] = result['count']
        
        return {
            'jobTitle': job.get('title'),
            'totalShortlisted': shortlisted_count,
            'statusDistribution': status_counts,
            'createdAt': job.get('createdAt'),
            'status': job.get('status')
        }
    
    # ============ SEARCH & FILTER ============
    
    def search_jobs(self, query: str, filters: Dict = None) -> List[Dict]:
        """Search jobs by query and filters"""
        search_criteria = {}
        
        # Text search
        if query:
            search_criteria['$or'] = [
                {'title': {'$regex': query, '$options': 'i'}},
                {'description': {'$regex': query, '$options': 'i'}},
                {'company': {'$regex': query, '$options': 'i'}}
            ]
        
        # Apply filters
        if filters:
            if 'status' in filters:
                search_criteria['status'] = filters['status']
            
            if 'type' in filters:
                search_criteria['type'] = filters['type']
            
            if 'location' in filters:
                search_criteria['location'] = {'$regex': filters['location'], '$options': 'i'}
        
        jobs = list(self.db.jobs.find(search_criteria).sort('createdAt', -1))
        
        for job in jobs:
            job['_id'] = str(job['_id'])
            job['createdAt'] = job['createdAt'].isoformat() if 'createdAt' in job else None
            job['updatedAt'] = job['updatedAt'].isoformat() if 'updatedAt' in job else None
        
        return jobs
    
    def get_all_active_jobs(self) -> List[Dict]:
        """Get all active jobs across all recruiters"""
        return self.search_jobs('', {'status': 'active'})