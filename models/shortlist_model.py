from datetime import datetime
from typing import Dict, List, Optional
from bson import ObjectId

class ShortlistModel:
    """
    Shortlist Model - Defines structure and validation for candidate shortlisting
    """
    
    @staticmethod
    def get_schema() -> Dict:
        """
        Get MongoDB schema for shortlist collection
        """
        return {
            'bsonType': 'object',
            'required': ['jobId', 'candidateId', 'recruiterId', 'status', 'createdAt'],
            'properties': {
                '_id': {
                    'bsonType': 'objectId',
                    'description': 'Unique shortlist entry identifier'
                },
                'jobId': {
                    'bsonType': 'string',
                    'description': 'Job posting ID - required'
                },
                'candidateId': {
                    'bsonType': 'string',
                    'description': 'Candidate user ID - required'
                },
                'recruiterId': {
                    'bsonType': 'string',
                    'description': 'Recruiter user ID - required'
                },
                'candidateName': {
                    'bsonType': 'string',
                    'description': 'Candidate full name'
                },
                'candidateEmail': {
                    'bsonType': 'string',
                    'description': 'Candidate email address'
                },
                'candidatePhone': {
                    'bsonType': 'string',
                    'description': 'Candidate phone number'
                },
                'candidateResume': {
                    'bsonType': 'string',
                    'description': 'URL or path to candidate resume'
                },
                'matchScore': {
                    'bsonType': 'double',
                    'minimum': 0,
                    'maximum': 100,
                    'description': 'AI-calculated match score (0-100)'
                },
                'skillsMatch': {
                    'bsonType': 'double',
                    'minimum': 0,
                    'maximum': 100,
                    'description': 'Skills match percentage'
                },
                'experienceMatch': {
                    'bsonType': 'double',
                    'minimum': 0,
                    'maximum': 100,
                    'description': 'Experience match percentage'
                },
                'educationMatch': {
                    'bsonType': 'double',
                    'minimum': 0,
                    'maximum': 100,
                    'description': 'Education match percentage'
                },
                'matchedSkills': {
                    'bsonType': 'array',
                    'items': {
                        'bsonType': 'string'
                    },
                    'description': 'List of matched skills'
                },
                'missingSkills': {
                    'bsonType': 'array',
                    'items': {
                        'bsonType': 'string'
                    },
                    'description': 'List of skills candidate is missing'
                },
                'status': {
                    'enum': ['shortlisted', 'reviewing', 'interview_scheduled', 'interviewed', 
                            'selected', 'rejected', 'on-hold', 'withdrawn'],
                    'description': 'Current status of candidate - required'
                },
                'stage': {
                    'enum': ['screening', 'first_round', 'second_round', 'final_round', 'offer'],
                    'description': 'Current hiring stage'
                },
                'priority': {
                    'enum': ['low', 'medium', 'high', 'urgent'],
                    'description': 'Priority level for this candidate'
                },
                'rating': {
                    'bsonType': 'int',
                    'minimum': 1,
                    'maximum': 5,
                    'description': 'Recruiter rating (1-5 stars)'
                },
                'notes': {
                    'bsonType': 'string',
                    'description': 'Recruiter notes about the candidate'
                },
                'feedback': {
                    'bsonType': 'array',
                    'items': {
                        'bsonType': 'object',
                        'properties': {
                            'round': {
                                'bsonType': 'string',
                                'description': 'Interview round'
                            },
                            'interviewer': {
                                'bsonType': 'string',
                                'description': 'Interviewer name'
                            },
                            'comments': {
                                'bsonType': 'string',
                                'description': 'Interview feedback'
                            },
                            'score': {
                                'bsonType': 'int',
                                'description': 'Interview score'
                            },
                            'date': {
                                'bsonType': 'date',
                                'description': 'Feedback date'
                            }
                        }
                    },
                    'description': 'Interview feedback history'
                },
                'interviewSchedule': {
                    'bsonType': 'object',
                    'properties': {
                        'date': {
                            'bsonType': 'date',
                            'description': 'Interview date and time'
                        },
                        'duration': {
                            'bsonType': 'int',
                            'description': 'Duration in minutes'
                        },
                        'mode': {
                            'enum': ['video', 'phone', 'in-person'],
                            'description': 'Interview mode'
                        },
                        'meetingLink': {
                            'bsonType': 'string',
                            'description': 'Video call link'
                        },
                        'interviewer': {
                            'bsonType': 'string',
                            'description': 'Interviewer name'
                        },
                        'location': {
                            'bsonType': 'string',
                            'description': 'Interview location (if in-person)'
                        },
                        'confirmed': {
                            'bsonType': 'bool',
                            'description': 'Whether candidate confirmed'
                        }
                    },
                    'description': 'Interview scheduling details'
                },
                'tags': {
                    'bsonType': 'array',
                    'items': {
                        'bsonType': 'string'
                    },
                    'description': 'Custom tags for categorization'
                },
                'source': {
                    'bsonType': 'string',
                    'description': 'How candidate was found (search, direct upload, etc.)'
                },
                'notificationsSent': {
                    'bsonType': 'array',
                    'items': {
                        'bsonType': 'object',
                        'properties': {
                            'type': {
                                'bsonType': 'string',
                                'description': 'Notification type'
                            },
                            'sentAt': {
                                'bsonType': 'date',
                                'description': 'When notification was sent'
                            },
                            'status': {
                                'bsonType': 'string',
                                'description': 'Notification delivery status'
                            }
                        }
                    },
                    'description': 'History of notifications sent to candidate'
                },
                'createdAt': {
                    'bsonType': 'date',
                    'description': 'When candidate was shortlisted - required'
                },
                'updatedAt': {
                    'bsonType': 'date',
                    'description': 'Last update timestamp'
                },
                'lastContactedAt': {
                    'bsonType': 'date',
                    'description': 'When candidate was last contacted'
                },
                'rejectedAt': {
                    'bsonType': 'date',
                    'description': 'When candidate was rejected (if applicable)'
                },
                'selectedAt': {
                    'bsonType': 'date',
                    'description': 'When candidate was selected (if applicable)'
                }
            }
        }
    
    @staticmethod
    def create_indexes(db):
        """
        Create MongoDB indexes for better query performance
        """
        shortlist_collection = db.shortlists
        
        # Create indexes
        shortlist_collection.create_index([('jobId', 1)])
        shortlist_collection.create_index([('candidateId', 1)])
        shortlist_collection.create_index([('recruiterId', 1)])
        shortlist_collection.create_index([('status', 1)])
        shortlist_collection.create_index([('createdAt', -1)])
        shortlist_collection.create_index([('matchScore', -1)])
        
        # Compound indexes
        shortlist_collection.create_index([('jobId', 1), ('status', 1)])
        shortlist_collection.create_index([('jobId', 1), ('matchScore', -1)])
        shortlist_collection.create_index([('recruiterId', 1), ('status', 1)])
        shortlist_collection.create_index([('candidateId', 1), ('jobId', 1)], unique=True)  # Prevent duplicates
        
        print("✅ Shortlist collection indexes created successfully")
    
    @staticmethod
    def validate_shortlist_data(shortlist_data: Dict) -> tuple[bool, Optional[str]]:
        """
        Validate shortlist data before insertion
        
        Returns:
            (is_valid, error_message)
        """
        # Required fields
        required_fields = ['jobId', 'candidateId', 'recruiterId']
        
        for field in required_fields:
            if field not in shortlist_data or not shortlist_data[field]:
                return False, f"Missing or empty required field: {field}"
        
        # Validate status if provided
        valid_statuses = ['shortlisted', 'reviewing', 'interview_scheduled', 'interviewed', 
                         'selected', 'rejected', 'on-hold', 'withdrawn']
        if 'status' in shortlist_data and shortlist_data['status'] not in valid_statuses:
            return False, f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        
        # Validate stage if provided
        valid_stages = ['screening', 'first_round', 'second_round', 'final_round', 'offer']
        if 'stage' in shortlist_data and shortlist_data['stage'] not in valid_stages:
            return False, f"Invalid stage. Must be one of: {', '.join(valid_stages)}"
        
        # Validate priority if provided
        valid_priorities = ['low', 'medium', 'high', 'urgent']
        if 'priority' in shortlist_data and shortlist_data['priority'] not in valid_priorities:
            return False, f"Invalid priority. Must be one of: {', '.join(valid_priorities)}"
        
        # Validate match score if provided
        if 'matchScore' in shortlist_data:
            score = shortlist_data['matchScore']
            if not isinstance(score, (int, float)) or score < 0 or score > 100:
                return False, "Match score must be between 0 and 100"
        
        # Validate rating if provided
        if 'rating' in shortlist_data:
            rating = shortlist_data['rating']
            if not isinstance(rating, int) or rating < 1 or rating > 5:
                return False, "Rating must be between 1 and 5"
        
        return True, None
    
    @staticmethod
    def create_shortlist_document(shortlist_data: Dict) -> Dict:
        """
        Create a properly formatted shortlist document for MongoDB insertion
        """
        # Validate first
        is_valid, error_msg = ShortlistModel.validate_shortlist_data(shortlist_data)
        if not is_valid:
            raise ValueError(error_msg)
        
        # Create document with defaults
        shortlist_document = {
            'jobId': shortlist_data['jobId'],
            'candidateId': shortlist_data['candidateId'],
            'recruiterId': shortlist_data['recruiterId'],
            'candidateName': shortlist_data.get('candidateName', ''),
            'candidateEmail': shortlist_data.get('candidateEmail', ''),
            'candidatePhone': shortlist_data.get('candidatePhone', ''),
            'candidateResume': shortlist_data.get('candidateResume', ''),
            'matchScore': shortlist_data.get('matchScore', 0.0),
            'skillsMatch': shortlist_data.get('skillsMatch', 0.0),
            'experienceMatch': shortlist_data.get('experienceMatch', 0.0),
            'educationMatch': shortlist_data.get('educationMatch', 0.0),
            'matchedSkills': shortlist_data.get('matchedSkills', []),
            'missingSkills': shortlist_data.get('missingSkills', []),
            'status': shortlist_data.get('status', 'shortlisted'),
            'stage': shortlist_data.get('stage', 'screening'),
            'priority': shortlist_data.get('priority', 'medium'),
            'rating': shortlist_data.get('rating'),
            'notes': shortlist_data.get('notes', ''),
            'feedback': shortlist_data.get('feedback', []),
            'interviewSchedule': shortlist_data.get('interviewSchedule'),
            'tags': shortlist_data.get('tags', []),
            'source': shortlist_data.get('source', 'manual'),
            'notificationsSent': [],
            'createdAt': datetime.utcnow(),
            'updatedAt': datetime.utcnow(),
            'lastContactedAt': None,
            'rejectedAt': None,
            'selectedAt': None
        }
        
        return shortlist_document
    
    @staticmethod
    def serialize_shortlist(shortlist_doc: Dict) -> Dict:
        """
        Convert MongoDB document to JSON-serializable format
        """
        if not shortlist_doc:
            return None
        
        serialized = shortlist_doc.copy()
        
        # Convert ObjectId to string
        if '_id' in serialized:
            serialized['_id'] = str(serialized['_id'])
        
        # Convert datetime to ISO format
        date_fields = ['createdAt', 'updatedAt', 'lastContactedAt', 'rejectedAt', 'selectedAt']
        for field in date_fields:
            if field in serialized and serialized[field]:
                serialized[field] = serialized[field].isoformat()
        
        # Handle interview schedule dates
        if 'interviewSchedule' in serialized and serialized['interviewSchedule']:
            if 'date' in serialized['interviewSchedule']:
                serialized['interviewSchedule']['date'] = serialized['interviewSchedule']['date'].isoformat()
        
        # Handle feedback dates
        if 'feedback' in serialized:
            for feedback in serialized['feedback']:
                if 'date' in feedback and feedback['date']:
                    feedback['date'] = feedback['date'].isoformat()
        
        # Handle notification dates
        if 'notificationsSent' in serialized:
            for notification in serialized['notificationsSent']:
                if 'sentAt' in notification and notification['sentAt']:
                    notification['sentAt'] = notification['sentAt'].isoformat()
        
        return serialized
    
    @staticmethod
    def get_status_workflow() -> Dict[str, List[str]]:
        """
        Get valid status transitions
        """
        return {
            'shortlisted': ['reviewing', 'interview_scheduled', 'rejected', 'withdrawn'],
            'reviewing': ['interview_scheduled', 'rejected', 'on-hold'],
            'interview_scheduled': ['interviewed', 'rejected', 'withdrawn'],
            'interviewed': ['selected', 'rejected', 'on-hold'],
            'selected': [],  # Terminal state
            'rejected': [],  # Terminal state
            'on-hold': ['reviewing', 'interview_scheduled', 'rejected'],
            'withdrawn': []  # Terminal state
        }
    
    @staticmethod
    def can_transition_status(current_status: str, new_status: str) -> bool:
        """
        Check if status transition is valid
        """
        workflow = ShortlistModel.get_status_workflow()
        
        if current_status not in workflow:
            return False
        
        allowed_transitions = workflow[current_status]
        return new_status in allowed_transitions or new_status == current_status
    
    @staticmethod
    def get_sample_shortlist() -> Dict:
        """
        Get a sample shortlist document for testing
        """
        return {
            'jobId': 'sample_job_id',
            'candidateId': 'sample_candidate_id',
            'recruiterId': 'sample_recruiter_id',
            'candidateName': 'Jane Smith',
            'candidateEmail': 'jane.smith@example.com',
            'candidatePhone': '+1234567890',
            'matchScore': 87.5,
            'skillsMatch': 90.0,
            'experienceMatch': 85.0,
            'educationMatch': 88.0,
            'matchedSkills': ['React', 'Node.js', 'MongoDB', 'JavaScript'],
            'missingSkills': ['AWS', 'Docker'],
            'status': 'shortlisted',
            'stage': 'screening',
            'priority': 'high',
            'rating': 4,
            'notes': 'Strong candidate with excellent React skills. Would be great fit for the team.',
            'tags': ['frontend', 'experienced', 'recommended'],
            'source': 'AI matching'
        }
    
    @staticmethod
    def get_statistics_schema() -> Dict:
        """
        Schema for shortlist statistics/analytics
        """
        return {
            'jobId': 'string',
            'totalShortlisted': 'int',
            'statusDistribution': {
                'shortlisted': 'int',
                'reviewing': 'int',
                'interview_scheduled': 'int',
                'interviewed': 'int',
                'selected': 'int',
                'rejected': 'int',
                'on-hold': 'int',
                'withdrawn': 'int'
            },
            'averageMatchScore': 'float',
            'stageDistribution': {
                'screening': 'int',
                'first_round': 'int',
                'second_round': 'int',
                'final_round': 'int',
                'offer': 'int'
            },
            'priorityDistribution': {
                'low': 'int',
                'medium': 'int',
                'high': 'int',
                'urgent': 'int'
            },
            'conversionRate': 'float',
            'averageTimeToHire': 'float'
        }