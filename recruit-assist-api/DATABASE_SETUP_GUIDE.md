# Database Setup Guide - Step by Step

## Current Status
✅ Dependencies installed (SQLAlchemy, Alembic, psycopg2)  
❌ PostgreSQL not running or database doesn't exist  
❌ No migrations created yet

## Option 1: PostgreSQL Setup (Recommended for Production)

### Step 1: Install PostgreSQL (if not installed)

**Windows:**
1. Download from https://www.postgresql.org/download/windows/
2. Run installer
3. Remember the postgres user password you set
4. Default port: 5432

**Or use Chocolatey:**
```powershell
choco install postgresql
```

### Step 2: Start PostgreSQL Service

```powershell
# Check if service exists
Get-Service -Name "*postgres*"

# Start PostgreSQL service
Start-Service postgresql-x64-15  # Adjust version number
# Or
net start postgresql-x64-15
```

### Step 3: Create Database

```powershell
# Connect to PostgreSQL
psql -U postgres

# In psql prompt:
CREATE DATABASE recruit_assist;
\q
```

### Step 4: Verify .env File

Check `recruit-assist-api/.env` has:
```
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/recruit_assist
```

### Step 5: Run Setup Script

```powershell
cd recruit-assist-api
python setup_database.py
```

---

## Option 2: Docker PostgreSQL (Easiest)

If you have Docker installed:

```powershell
# Start PostgreSQL in Docker
docker run --name recruit-assist-db `
  -e POSTGRES_PASSWORD=postgres `
  -e POSTGRES_DB=recruit_assist `
  -p 5432:5432 `
  -d postgres:15

# Verify it's running
docker ps

# Update .env (already correct):
# DATABASE_URL=postgresql://postgres:postgres@localhost:5432/recruit_assist
```

Then run:
```powershell
cd recruit-assist-api
python setup_database.py
```

---

## Option 3: SQLite for Testing (Quick Start)

If you just want to test without PostgreSQL, we can modify to use SQLite temporarily.

**Note**: SQLite is not recommended for production but works for testing.

---

## What the Setup Script Will Do

When you run `python setup_database.py`, it will:

1. ✅ Check dependencies are installed
2. ✅ Test database connection
3. ✅ Create initial Alembic migration
4. ✅ Run migration to create tables:
   - `candidates` - Stores parsed CV data
   - `job_postings` - Stores normalized job descriptions
   - `candidate_profiles` - Links candidates to jobs with match scores
5. ✅ Verify tables were created

---

## Next Steps After Database Setup

Once database is set up:

1. **Test the API**:
   ```powershell
   cd recruit-assist-api
   uvicorn app.main:app --reload
   ```

2. **Check health endpoint**:
   - Visit http://localhost:8000/healthz
   - Should show `"database": "connected"`

3. **Test with real CV**:
   - Upload a CV from `CV/` folder
   - Check it's saved to database

---

## Quick Decision

**Which option do you want to use?**

- **Option 1**: Install/start PostgreSQL (best for production)
- **Option 2**: Docker PostgreSQL (easiest, if Docker available)
- **Option 3**: SQLite for quick testing (modify code temporarily)

Let me know and I'll help you proceed!

