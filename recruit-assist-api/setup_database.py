#!/usr/bin/env python3
"""
Database setup script for Bershaw Recruitment Platform.
This script will:
1. Check database connection
2. Create initial migration if needed
3. Run migrations to create tables
4. Verify tables were created
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def check_dependencies():
    """Check if required dependencies are installed."""
    missing = []
    try:
        import sqlalchemy
    except ImportError:
        missing.append("sqlalchemy")
    
    try:
        import alembic
    except ImportError:
        missing.append("alembic")
    
    try:
        import psycopg2
    except ImportError:
        missing.append("psycopg2-binary")
    
    if missing:
        print(f"Missing dependencies: {', '.join(missing)}")
        print(f"Install with: pip install {' '.join(missing)}")
        return False
    
    print("All dependencies installed")
    return True

def check_database_connection():
    """Check if we can connect to the database."""
    try:
        from app.settings import settings
        from app.database import get_engine, check_db_connection
        
        print(f"\nDatabase Configuration:")
        print(f"   URL: {settings.database_url.split('@')[-1] if '@' in settings.database_url else 'Not set'}")
        
        print(f"\nTesting database connection...")
        if check_db_connection():
            print("Database connection successful!")
            return True
        else:
            print("Database connection failed")
            print("\nPossible issues:")
            print("1. PostgreSQL is not running")
            print("2. Database 'recruit_assist' doesn't exist")
            print("3. Wrong credentials in .env file")
            print("\nTo create database:")
            print("  psql -U postgres")
            print("  CREATE DATABASE recruit_assist;")
            return False
    except Exception as e:
        print(f"Error checking database: {e}")
        return False

def check_migrations():
    """Check if migrations exist."""
    versions_dir = Path(__file__).parent / "alembic" / "versions"
    if versions_dir.exists():
        migrations = list(versions_dir.glob("*.py"))
        # Filter out __pycache__ and __init__
        migrations = [m for m in migrations if m.stem not in ["__init__", "__pycache__"]]
        return len(migrations)
    return 0

def create_initial_migration():
    """Create initial migration using Alembic."""
    import subprocess
    
    print(f"\nCreating initial migration...")
    
    try:
        # Run alembic revision --autogenerate
        result = subprocess.run(
            ["alembic", "revision", "--autogenerate", "-m", "Initial migration - create candidates, job_postings, candidate_profiles tables"],
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("[OK] Initial migration created successfully")
            # Show the migration file
            versions_dir = Path(__file__).parent / "alembic" / "versions"
            if versions_dir.exists():
                migrations = sorted(versions_dir.glob("*.py"), key=lambda x: x.stat().st_mtime, reverse=True)
                migrations = [m for m in migrations if m.stem not in ["__init__", "__pycache__"]]
                if migrations:
                    print(f"   Migration file: {migrations[0].name}")
            return True
        else:
            print(f"[ERROR] Failed to create migration")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"[ERROR] Error creating migration: {e}")
        return False

def run_migrations():
    """Run Alembic migrations."""
    import subprocess
    
    print(f"\nRunning migrations...")
    
    try:
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("[OK] Migrations applied successfully")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print(f"[ERROR] Failed to run migrations")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"[ERROR] Error running migrations: {e}")
        return False

def verify_tables():
    """Verify that tables were created."""
    try:
        from sqlalchemy import inspect
        from app.database import get_engine
        
        engine = get_engine()
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        expected_tables = ["candidates", "job_postings", "candidate_profiles"]
        alembic_version = "alembic_version"
        
        print(f"\nDatabase Tables:")
        for table in expected_tables:
            if table in tables:
                print(f"   [OK] {table}")
            else:
                print(f"   [ERROR] {table} - NOT FOUND")
        
        if alembic_version in tables:
            print(f"   [OK] {alembic_version} (migration tracking)")
        
        all_found = all(table in tables for table in expected_tables)
        return all_found
    except Exception as e:
        print(f"[ERROR] Error verifying tables: {e}")
        return False

def create_tables_directly():
    """Fallback: Create tables directly without migrations."""
    try:
        print(f"\nAttempting direct table creation (fallback)...")
        from app.database import init_db
        
        init_db()
        print("[OK] Tables created directly")
        return True
    except Exception as e:
        print(f"[ERROR] Error creating tables directly: {e}")
        return False

def main():
    """Main setup function."""
    print("="*60)
    print("BERSHAW RECRUITMENT - DATABASE SETUP")
    print("="*60)
    
    # Step 1: Check dependencies
    if not check_dependencies():
        return 1
    
    # Step 2: Check database connection
    if not check_database_connection():
        print("\n" + "="*60)
        print("SETUP INSTRUCTIONS:")
        print("="*60)
        print("\n1. Make sure PostgreSQL is installed and running")
        print("2. Create the database:")
        print("   psql -U postgres")
        print("   CREATE DATABASE recruit_assist;")
        print("3. Update .env file with correct DATABASE_URL")
        print("4. Run this script again")
        return 1
    
    # Step 3: Check if migrations exist
    migration_count = check_migrations()
    print(f"\nExisting migrations: {migration_count}")
    
    # Step 4: Create migration if needed
    if migration_count == 0:
        if not create_initial_migration():
            print("\n[WARNING]  Could not create migration. Trying direct table creation...")
            if create_tables_directly():
                if verify_tables():
                    print("\n[OK] Database setup complete!")
                    return 0
            return 1
    else:
        print(f"[OK] Found {migration_count} existing migration(s)")
    
    # Step 5: Run migrations
    if not run_migrations():
        print("\n[WARNING]  Migration failed. Trying direct table creation...")
        if create_tables_directly():
            if verify_tables():
                print("\n[OK] Database setup complete!")
                return 0
        return 1
    
    # Step 6: Verify tables
    if verify_tables():
        print("\n" + "="*60)
        print("[OK] DATABASE SETUP COMPLETE!")
        print("="*60)
        print("\nNext steps:")
        print("1. Test the API: uvicorn app.main:app --reload")
        print("2. Check health: http://localhost:8000/healthz")
        print("3. View API docs: http://localhost:8000/docs")
        return 0
    else:
        print("\n[ERROR] Some tables are missing. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

