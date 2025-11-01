#!/usr/bin/env python3
"""
Database Initialization Script for SmartCareer Platform

This script initializes the MongoDB database with:
- Collections
- Indexes
- Validation schemas
- Sample data (optional)

Usage:
    python init_db.py              # Initialize with indexes only
    python init_db.py --sample     # Initialize with sample data
    python init_db.py --reset      # Reset database (WARNING: deletes all data)
"""

import sys
import os
from pymongo import MongoClient
from dotenv import load_dotenv
import argparse

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import JobModel, ShortlistModel, initialize_database

# Load environment variables
load_dotenv()

def get_database():
    """Connect to MongoDB database"""
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    DB_NAME = os.getenv('DB_NAME', 'smartcareer_db')
    
    print(f"📡 Connecting to MongoDB: {MONGO_URI}")
    print(f"📊 Database: {DB_NAME}")
    
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    
    # Test connection
    try:
        client.server_info()
        print("✅ Connected to MongoDB successfully")
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        sys.exit(1)
    
    return db, client

def reset_database(db):
    """Reset database (delete all collections)"""
    print("\n⚠️  WARNING: This will delete all data in the database!")
    confirm = input("Type 'RESET' to confirm: ")
    
    if confirm != 'RESET':
        print("❌ Reset cancelled")
        return False
    
    print("🗑️  Deleting collections...")
    
    collections = ['jobs', 'shortlists', 'users']
    for collection in collections:
        db[collection].drop()
        print(f"   ✓ Dropped {collection}")
    
    print("✅ Database reset complete")
    return True

def create_sample_data(db):
    """Create sample data for testing"""
    print("\n📝 Creating sample data...")
    
    # Sample recruiter user
    sample_recruiter = {
        'name': 'John Recruiter',
        'email': 'recruiter@example.com',
        'password': 'password123',  # In production, hash this!
        'role': 'recruiter',
        'company': 'Tech Innovations Inc.',
        'phone': '+1234567890'
    }
    
    recruiter_id = db.users.insert_one(sample_recruiter).inserted_id
    print(f"   ✓ Created sample recruiter: {recruiter_id}")
    
    # Sample candidate user
    sample_candidate = {
        'name': 'Jane Developer',
        'email': 'candidate@example.com',
        'password': 'password123',  # In production, hash this!
        'role': 'candidate',
        'phone': '+1234567891',
        'skills': ['React', 'Node.js', 'MongoDB', 'JavaScript', 'Python'],
        'experience': 5,
        'education': 'Bachelor\'s in Computer Science',
        'location': 'San Francisco, CA'
    }
    
    candidate_id = db.users.insert_one(sample_candidate).inserted_id
    print(f"   ✓ Created sample candidate: {candidate_id}")
    
    # Sample job
    sample_job_data = JobModel.get_sample_job()
    sample_job_data['recruiterId'] = str(recruiter_id)
    sample_job = JobModel.create_job_document(sample_job_data)
    
    job_id = db.jobs.insert_one(sample_job).inserted_id
    print(f"   ✓ Created sample job: {job_id}")
    
    # Sample shortlist
    sample_shortlist_data = ShortlistModel.get_sample_shortlist()
    sample_shortlist_data['jobId'] = str(job_id)
    sample_shortlist_data['candidateId'] = str(candidate_id)
    sample_shortlist_data['recruiterId'] = str(recruiter_id)
    sample_shortlist_data['candidateName'] = sample_candidate['name']
    sample_shortlist_data['candidateEmail'] = sample_candidate['email']
    sample_shortlist = ShortlistModel.create_shortlist_document(sample_shortlist_data)
    
    shortlist_id = db.shortlists.insert_one(sample_shortlist).inserted_id
    print(f"   ✓ Created sample shortlist: {shortlist_id}")
    
    print("\n✅ Sample data created successfully!")
    print("\n📊 Test Credentials:")
    print(f"   Recruiter: recruiter@example.com / password123")
    print(f"   Candidate: candidate@example.com / password123")

def display_summary(db):
    """Display database summary"""
    print("\n" + "="*60)
    print("📊 DATABASE SUMMARY")
    print("="*60)
    
    collections_stats = {
        'users': db.users.count_documents({}),
        'jobs': db.jobs.count_documents({}),
        'shortlists': db.shortlists.count_documents({})
    }
    
    for collection, count in collections_stats.items():
        print(f"   {collection.capitalize()}: {count} documents")
    
    # Show indexes
    print("\n📑 Indexes:")
    for collection in ['jobs', 'shortlists']:
        indexes = db[collection].list_indexes()
        print(f"\n   {collection.capitalize()}:")
        for idx in indexes:
            print(f"      • {idx['name']}")
    
    print("\n" + "="*60)

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Initialize SmartCareer Database')
    parser.add_argument('--sample', action='store_true', help='Create sample data')
    parser.add_argument('--reset', action='store_true', help='Reset database (WARNING: deletes all data)')
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("🚀 SmartCareer Database Initialization")
    print("="*60 + "\n")
    
    # Connect to database
    db, client = get_database()
    
    # Reset if requested
    if args.reset:
        if not reset_database(db):
            client.close()
            sys.exit(0)
    
    # Initialize database (create indexes and schemas)
    initialize_database(db)
    
    # Create sample data if requested
    if args.sample:
        create_sample_data(db)
    
    # Display summary
    display_summary(db)
    
    print("\n✅ Database initialization complete!")
    print("\n💡 Tips:")
    print("   • Run 'python init_db.py --sample' to add sample data")
    print("   • Run 'python init_db.py --reset' to reset database")
    print("   • Check .env file for database configuration")
    
    # Close connection
    client.close()

if __name__ == '__main__':
    main()