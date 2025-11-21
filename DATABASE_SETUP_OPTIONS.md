# Database Setup - Your Options

## Current Situation
- ✅ Docker Desktop is installed (v4.41.2)
- ⚠️ Docker encountered I/O error when pulling PostgreSQL image
- ✅ All Python dependencies ready
- ✅ Setup script ready

---

## 🚀 Option 1: Fix Docker & Retry (Recommended)

### Try These Steps:

**A. Restart Docker Desktop**
1. Right-click whale icon in system tray
2. Click "Quit Docker Desktop"
3. Wait 10 seconds
4. Start Docker Desktop again from Start menu
5. Wait for it to fully start
6. Try the setup again

**B. Check Disk Space**
```powershell
Get-PSDrive C | Select-Object Used,Free
```
Need at least 2-3 GB free for PostgreSQL image.

**C. Try Different PostgreSQL Version**
```powershell
# Try postgres:14 instead of postgres:15
docker run --name recruit-assist-db -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=recruit_assist -p 5432:5432 -d postgres:14
```

**D. Clean Docker and Retry**
```powershell
# Remove any failed containers
docker rm recruit-assist-db -f 2>$null

# Try again
docker run --name recruit-assist-db -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=recruit_assist -p 5432:5432 -d postgres:15
```

---

## 🚀 Option 2: Install PostgreSQL Directly (Most Reliable)

If Docker keeps having issues, install PostgreSQL directly:

### Windows Installation Steps:

1. **Download PostgreSQL**:
   - Go to: https://www.postgresql.org/download/windows/
   - Click "Download the installer"
   - Download PostgreSQL 15 or 16 for Windows x86-64
   - File will be like: `postgresql-15.x-x-windows-x64.exe`

2. **Run Installer**:
   - Run the downloaded .exe
   - Click "Next" through setup
   - **Set password for postgres user** (remember this!)
   - Port: 5432 (default)
   - Locale: Default
   - Click "Next" → "Next" → "Finish"

3. **Create Database**:
   ```powershell
   # Open Command Prompt or PowerShell
   psql -U postgres
   # Enter the password you set
   CREATE DATABASE recruit_assist;
   \q
   ```

4. **Update .env File**:
   Edit `recruit-assist-api/.env`:
   ```
   DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/recruit_assist
   ```

5. **Run Setup**:
   ```powershell
   cd recruit-assist-api
   python setup_database.py
   ```

---

## 🚀 Option 3: Use SQLite for Quick Testing (Fastest)

I can modify the code to use SQLite so you can test immediately without PostgreSQL.

**Pros**: Works in 1 minute, no setup needed  
**Cons**: Not for production, some features limited

**Would you like me to:**
1. Modify `app/settings.py` to use SQLite?
2. Update database URL?
3. Run setup with SQLite?
4. You can switch to PostgreSQL later

---

## 🎯 My Recommendation

**Try this order:**

1. **First**: Restart Docker Desktop and try again (5 minutes)
2. **If that fails**: Install PostgreSQL directly (15-20 minutes, most reliable)
3. **If you want to test now**: Use SQLite temporarily (1 minute)

---

## Quick Commands to Try Docker Again

After restarting Docker Desktop:

```powershell
# Check Docker is running
docker ps

# Try creating PostgreSQL container
docker run --name recruit-assist-db -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=recruit_assist -p 5432:5432 -d postgres:15

# Wait and check
Start-Sleep -Seconds 8
docker ps

# If successful, run setup
cd recruit-assist-api
python setup_database.py
```

---

## Which Would You Like to Do?

- **A**: Restart Docker Desktop and try again
- **B**: Install PostgreSQL directly (I'll guide you)
- **C**: Use SQLite for quick testing (I'll modify the code)
- **D**: Something else?

Let me know and I'll help you proceed!

