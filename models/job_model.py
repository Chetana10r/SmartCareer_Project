from datetime import datetime
from typing import Dict, List, Optional
from bson import ObjectId

class JobModel:
    """
    Job Model - Defines structure and validation for job postings
    """
    
    @staticmethod
    def get_schema() -> Dict:
        """
        Get MongoDB schema for job collection
        """
        return {
            'bsonType': 'object',
            'required': ['title', 'company', 'description', 'requirements', 'recruiterId', 'status', 'createdAt'],
            'properties': {
                '_id': {
                    'bsonType': 'objectId',
                    'description': 'Unique job identifier'
                },
                'title': {
                    'bsonType': 'string',
                    'description': 'Job title - required'
                },
                'company': {
                    'bsonType': 'string',
                    'description': 'Company name - required'
                },
                'location': {
                    'bsonType': 'string',
                    'description': 'Job location (city, state, country)'
                },
                'type': {
                    'enum': ['Full-time', 'Part-time', 'Contract', 'Internship', 'Freelance'],
                    'description': 'Employment type'
                },
                'mode': {
                    'enum': ['Remote', 'Hybrid', 'On-site'],
                    'description': 'Work mode'
                },
                'description': {
                    'bsonType': 'string',
                    'description': 'Detailed job description - required'
                },
                'requirements': {
                    'bsonType': 'string',
                    'description': 'Job requirements - required'
                },
                'responsibilities': {
                    'bsonType': 'string',
                    'description': 'Job responsibilities'
                },
                'skills': {
                    'bsonType': 'array',
                    'items': {
                        'bsonType': 'string'
                    },
                    'description': 'Required skills list'
                },
                'experienceRequired': {
                    'bsonType': 'int',
                    'minimum': 0,
                    'description': 'Years of experience required'
                },
                'educationRequired': {
                    'bsonType': 'string',
                    'description': 'Education qualification required'
                },
                'salary': {
                    'bsonType': 'object',
                    'properties': {
                        'min': {
                            'bsonType': 'int',
                            'description': 'Minimum salary'
                        },
                        'max': {
                            'bsonType': 'int',
                            'description': 'Maximum salary'
                        },
                        'currency': {
                            'bsonType': 'string',
                            'description': 'Currency (USD, INR, EUR, etc.)'
                        },
                        'period': {
                            'enum': ['per hour', 'per month', 'per year'],
                            'description': 'Salary period'
                        }
                    },
                    'description': 'Salary range'
                },
                'benefits': {
                    'bsonType': 'array',
                    'items': {
                        'bsonType': 'string'
                    },
                    'description': 'Employee benefits'
                },
                'recruiterId': {
                    'bsonType': 'string',
                    'description': 'Recruiter user ID - required'
                },
                'recruiterName': {
                    'bsonType': 'string',
                    'description': 'Recruiter name'
                },
                'recruiterEmail': {
                    'bsonType': 'string',
                    'description': 'Recruiter contact email'
                },
                'status': {
                    'enum': ['draft', 'active', 'closed', 'on-hold'],
                    'description': 'Job posting status - required'
                },
                'applicationsCount': {
                    'bsonType': 'int',
                    'minimum': 0,
                    'description': 'Number of applications received'
                },
                'shortlistedCount': {
                    'bsonType': 'int',
                    'minimum': 0,
                    'description': 'Number of candidates shortlisted'
                },
                'viewsCount': {
                    'bsonType': 'int',
                    'minimum': 0,
                    'description': 'Number of times job was viewed'
                },
                'createdAt': {
                    'bsonType': 'date',
                    'description': 'Job creation timestamp - required'
                },
                'updatedAt': {
                    'bsonType': 'date',
                    'description': 'Last update timestamp'
                },
                'expiresAt': {
                    'bsonType': 'date',
                    'description': 'Job posting expiry date'
                },
                'postedDate': {
                    'bsonType': 'date',
                    'description': 'Date when job was published'
                },
                'closedDate': {
                    'bsonType': 'date',
                    'description': 'Date when job was closed'
                }
            }
        }
    
    @staticmethod
    def create_indexes(db):
        """
        Create MongoDB indexes for better query performance
        """
        jobs_collection = db.jobs
        
        # Create indexes
        jobs_collection.create_index([('recruiterId', 1)])
        jobs_collection.create_index([('status', 1)])
        jobs_collection.create_index([('createdAt', -1)])
        jobs_collection.create_index([('title', 'text'), ('description', 'text'), ('skills', 'text')])
        jobs_collection.create_index([('location', 1)])
        jobs_collection.create_index([('type', 1)])
        jobs_collection.create_index([('expiresAt', 1)])
        
        # Compound indexes
        jobs_collection.create_index([('recruiterId', 1), ('status', 1)])
        jobs_collection.create_index([('status', 1), ('createdAt', -1)])
        
        print("✅ Job collection indexes created successfully")
    
    @staticmethod
    def validate_job_data(job_data: Dict) -> tuple[bool, Optional[str]]:
        """
        Validate job data before insertion
        
        Returns:
            (is_valid, error_message)
        """
        # Required fields
        required_fields = ['title', 'company', 'description', 'requirements', 'recruiterId']
        
        for field in required_fields:
            if field not in job_data or not job_data[field]:
                return False, f"Missing or empty required field: {field}"
        
        # Validate title length
        if len(job_data['title']) < 5:
            return False, "Job title must be at least 5 characters long"
        
        if len(job_data['title']) > 200:
            return False, "Job title must not exceed 200 characters"
        
        # Validate description length
        if len(job_data['description']) < 50:
            return False, "Job description must be at least 50 characters long"
        
        # Validate type if provided
        valid_types = ['Full-time', 'Part-time', 'Contract', 'Internship', 'Freelance']
        if 'type' in job_data and job_data['type'] not in valid_types:
            return False, f"Invalid job type. Must be one of: {', '.join(valid_types)}"
        
        # Validate mode if provided
        valid_modes = ['Remote', 'Hybrid', 'On-site']
        if 'mode' in job_data and job_data['mode'] not in valid_modes:
            return False, f"Invalid work mode. Must be one of: {', '.join(valid_modes)}"
        
        # Validate status if provided
        valid_statuses = ['draft', 'active', 'closed', 'on-hold']
        if 'status' in job_data and job_data['status'] not in valid_statuses:
            return False, f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        
        # Validate experience if provided
        if 'experienceRequired' in job_data:
            exp = job_data['experienceRequired']
            if not isinstance(exp, int) or exp < 0 or exp > 50:
                return False, "Experience must be between 0 and 50 years"
        
        # Validate salary if provided
        if 'salary' in job_data:
            salary = job_data['salary']
            if 'min' in salary and 'max' in salary:
                if salary['min'] > salary['max']:
                    return False, "Minimum salary cannot be greater than maximum salary"
        
        return True, None
    
    @staticmethod
    def create_job_document(job_data: Dict) -> Dict:
        """
        Create a properly formatted job document for MongoDB insertion
        """
        # Validate first
        is_valid, error_msg = JobModel.validate_job_data(job_data)
        if not is_valid:
            raise ValueError(error_msg)
        
        # Create document with defaults
        job_document = {
            'title': job_data['title'],
            'company': job_data['company'],
            'location': job_data.get('location', ''),
            'type': job_data.get('type', 'Full-time'),
            'mode': job_data.get('mode', 'Hybrid'),
            'description': job_data['description'],
            'requirements': job_data['requirements'],
            'responsibilities': job_data.get('responsibilities', ''),
            'skills': job_data.get('skills', []),
            'experienceRequired': job_data.get('experienceRequired', 0),
            'educationRequired': job_data.get('educationRequired', ''),
            'salary': job_data.get('salary', {}),
            'benefits': job_data.get('benefits', []),
            'recruiterId': job_data['recruiterId'],
            'recruiterName': job_data.get('recruiterName', ''),
            'recruiterEmail': job_data.get('recruiterEmail', ''),
            'status': job_data.get('status', 'active'),
            'applicationsCount': 0,
            'shortlistedCount': 0,
            'viewsCount': 0,
            'createdAt': datetime.utcnow(),
            'updatedAt': datetime.utcnow(),
            'expiresAt': job_data.get('expiresAt'),
            'postedDate': datetime.utcnow() if job_data.get('status') == 'active' else None,
            'closedDate': None
        }
        
        return job_document
    
    @staticmethod
    def serialize_job(job_doc: Dict) -> Dict:
        """
        Convert MongoDB document to JSON-serializable format
        """
        if not job_doc:
            return None
        
        serialized = job_doc.copy()
        
        # Convert ObjectId to string
        if '_id' in serialized:
            serialized['_id'] = str(serialized['_id'])
        
        # Convert datetime to ISO format
        date_fields = ['createdAt', 'updatedAt', 'expiresAt', 'postedDate', 'closedDate']
        for field in date_fields:
            if field in serialized and serialized[field]:
                serialized[field] = serialized[field].isoformat()
        
        return serialized
    
    @staticmethod
    def get_sample_job() -> Dict:
        """
        Get a sample job document for testing
        """
        return {
            'title': 'Senior Full Stack Developer',
            'company': 'Tech Innovations Inc.',
            'location': 'San Francisco, CA',
            'type': 'Full-time',
            'mode': 'Hybrid',
            'description': 'We are looking for an experienced Full Stack Developer to join our growing team. You will work on cutting-edge web applications using modern technologies.',
            'requirements': 'Bachelor\'s degree in Computer Science or related field. 5+ years of experience in full stack development. Proficiency in React, Node.js, and MongoDB.',
            'responsibilities': 'Design and develop web applications. Collaborate with cross-functional teams. Write clean, maintainable code. Participate in code reviews.',
            'skills': ['React', 'Node.js', 'MongoDB', 'JavaScript', 'TypeScript', 'AWS', 'Docker'],
            'experienceRequired': 5,
            'educationRequired': 'Bachelor\'s in Computer Science or equivalent',
            'salary': {
                'min': 120000,
                'max': 180000,
                'currency': 'USD',
                'period': 'per year'
            },
            'benefits': ['Health Insurance', '401(k)', 'Remote Work', 'Learning Budget', 'Stock Options'],
            'recruiterId': 'sample_recruiter_id',
            'recruiterName': 'John Doe',
            'recruiterEmail': 'john@techinnovations.com',
            'status': 'active'
        }
    
    @staticmethod
    def get_job_statistics_schema() -> Dict:
        """
        Schema for job statistics/analytics
        """
        return {
            'jobId': 'string',
            'totalViews': 'int',
            'totalApplications': 'int',
            'shortlistedCount': 'int',
            'selectedCount': 'int',
            'rejectedCount': 'int',
            'averageMatchScore': 'float',
            'topSkillsRequested': 'array',
            'applicationsByDate': 'array',
            'candidatesByExperience': 'object',
            'candidatesByLocation': 'object'
        }