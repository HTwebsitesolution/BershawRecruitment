# Quick Database Setup - Choose Your Option

## Current Situation
- ✅ Python dependencies installed
- ✅ Setup script ready (`setup_database.py`)
- ❌ PostgreSQL not available (not running or not installed)

---

## 🚀 Option 1: Start Docker Desktop (Easiest - 2 minutes)

If you have Docker Desktop installed:

1. **Start Docker Desktop** (from Start menu or system tray)
2. Wait for it to fully start (whale icon in system tray)
3. **Run this command**:
   ```powershell
   docker run --name recruit-assist-db -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=recruit_assist -p 5432:5432 -d postgres:15
   ```
4. **Then run setup**:
   ```powershell
   cd recruit-assist-api
   python setup_database.py
   ```

---

## 🚀 Option 2: Install PostgreSQL (10-15 minutes)

### Windows Installation:

1. **Download PostgreSQL**:
   - Go to https://www.postgresql.org/download/windows/
   - Download the installer
   - Run installer
   - **Remember the postgres user password** you set
   - Default port: 5432

2. **Create Database**:
   ```powershell
   # Open Command Prompt or PowerShell
   psql -U postgres
   # Enter password when prompted
   CREATE DATABASE recruit_assist;
   \q
   ```

3. **Update .env file** in `recruit-assist-api/.env`:
   ```
   DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/recruit_assist
   ```

4. **Run setup**:
   ```powershell
   cd recruit-assist-api
   python setup_database.py
   ```

---

## 🚀 Option 3: Use SQLite for Testing (Quick - 1 minute)

I can modify the code to use SQLite temporarily so you can test without PostgreSQL.

**Pros**: Works immediately, no setup needed  
**Cons**: Not for production, some PostgreSQL features won't work

Would you like me to:
1. Modify the database URL to use SQLite?
2. Create the tables with SQLite?
3. You can test everything, then switch to PostgreSQL later

---

## 🎯 Recommended: Start Docker Desktop

**If Docker Desktop is installed**, just start it and run:

```powershell
# Start PostgreSQL container
docker run --name recruit-assist-db -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=recruit_assist -p 5432:5432 -d postgres:15

# Wait 5 seconds for PostgreSQL to start
Start-Sleep -Seconds 5

# Run setup
cd recruit-assist-api
python setup_database.py
```

---

## What Happens After Setup

Once database is set up, the script will:
1. ✅ Create Alembic migration
2. ✅ Create 3 tables: `candidates`, `job_postings`, `candidate_profiles`
3. ✅ Verify tables exist
4. ✅ You can then start the API and test!

---

## Which option would you like to proceed with?

- **A**: Start Docker Desktop and use Docker PostgreSQL
- **B**: Install PostgreSQL manually
- **C**: Use SQLite temporarily for quick testing
- **D**: Check if PostgreSQL is already installed but just not running

Let me know and I'll help you set it up!

