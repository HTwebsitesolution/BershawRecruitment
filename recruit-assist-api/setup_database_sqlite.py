#!/usr/bin/env python3
"""
Quick database setup using SQLite (for testing without PostgreSQL).
This creates the database tables immediately without needing PostgreSQL or Docker.
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def setup_sqlite_database():
    """Set up SQLite database and create tables."""
    try:
        print("="*60)
        print("BERSHAW RECRUITMENT - SQLite DATABASE SETUP")
        print("="*60)
        print()
        
        # Update settings to use SQLite
        from app.settings import settings
        settings.database_url = "sqlite:///./recruit_assist.db"
        print(f"Using SQLite database: recruit_assist.db")
        print()
        
        # Import database and models
        from app.database import init_db, get_engine, check_db_connection
        from app.db_models import Candidate, JobPosting, CandidateProfile, Base
        
        # Create tables
        print("Creating database tables...")
        init_db()
        print("[OK] Tables created")
        print()
        
        # Verify tables
        from sqlalchemy import inspect
        engine = get_engine()
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        expected_tables = ["candidates", "job_postings", "candidate_profiles"]
        
        print("Database Tables:")
        all_found = True
        for table in expected_tables:
            if table in tables:
                print(f"  [OK] {table}")
            else:
                print(f"  [MISSING] {table}")
                all_found = False
        
        if all_found:
            print()
            print("="*60)
            print("[SUCCESS] DATABASE SETUP COMPLETE!")
            print("="*60)
            print()
            print("Database file: recruit-assist-api/recruit_assist.db")
            print()
            print("Next steps:")
            print("1. Start the API: uvicorn app.main:app --reload")
            print("2. Check health: http://localhost:8000/healthz")
            print("3. View API docs: http://localhost:8000/docs")
            print()
            print("Note: Using SQLite for testing. Switch to PostgreSQL for production.")
            return 0
        else:
            print()
            print("[ERROR] Some tables are missing")
            return 1
            
    except Exception as e:
        print(f"[ERROR] Setup failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(setup_sqlite_database())

