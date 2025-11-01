"""
SmartCareer Database Models Package

This package contains MongoDB schema definitions and validation logic
for the SmartCareer recruitment platform.
"""

from .job_model import JobModel
from .shortlist_model import ShortlistModel

__all__ = ['JobModel', 'ShortlistModel']

def initialize_database(db):
    """
    Initialize database with indexes and validation
    
    Args:
        db: MongoDB database instance
    """
    print("🔧 Initializing SmartCareer database...")
    
    # Create indexes
    JobModel.create_indexes(db)
    ShortlistModel.create_indexes(db)
    
    # Optionally create validation schemas
    try:
        db.command({
            'collMod': 'jobs',
            'validator': {
                '$jsonSchema': JobModel.get_schema()
            },
            'validationLevel': 'moderate'  # 'strict' or 'moderate'
        })
        print("✅ Job collection validation schema applied")
    except Exception as e:
        print(f"⚠️  Could not apply job validation schema: {e}")
    
    try:
        db.command({
            'collMod': 'shortlists',
            'validator': {
                '$jsonSchema': ShortlistModel.get_schema()
            },
            'validationLevel': 'moderate'
        })
        print("✅ Shortlist collection validation schema applied")
    except Exception as e:
        print(f"⚠️  Could not apply shortlist validation schema: {e}")
    
    print("✅ Database initialization complete!")

def get_all_schemas():
    """
    Get all model schemas for documentation
    """
    return {
        'job': JobModel.get_schema(),
        'shortlist': ShortlistModel.get_schema(),
        'job_statistics': JobModel.get_job_statistics_schema(),
        'shortlist_statistics': ShortlistModel.get_statistics_schema()
    }