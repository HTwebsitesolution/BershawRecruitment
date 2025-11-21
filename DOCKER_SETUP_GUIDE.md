# Docker Desktop Setup Guide

## ✅ Good News: You Have Docker Desktop!

**Status**: Docker Desktop 4.41.2 is **installed** on your system  
**Location**: `C:\Program Files\Docker\Docker`  
**Current State**: Not running (needs to be started)

---

## 🚀 How to Start Docker Desktop

### Method 1: From Start Menu (Easiest)

1. **Press Windows key** or click Start button
2. **Type "Docker Desktop"**
3. **Click on "Docker Desktop"** app
4. **Wait for it to start** (you'll see a whale icon in system tray)
5. Wait until it says "Docker Desktop is running" (usually 30-60 seconds)

### Method 2: From File Explorer

1. **Open File Explorer**
2. **Navigate to**: `C:\Program Files\Docker\Docker`
3. **Double-click**: `Docker Desktop.exe`
4. **Wait for startup**

### Method 3: From Command Line

```powershell
# Start Docker Desktop
& "C:\Program Files\Docker\Docker\Docker Desktop.exe"
```

---

## ⏱️ How to Know Docker Desktop is Running

**Look for these signs:**

1. **System Tray Icon**: Whale icon in bottom-right corner
2. **Notification**: "Docker Desktop is running"
3. **Test command**:
   ```powershell
   docker ps
   ```
   Should return empty list or running containers (not an error)

---

## 🎯 Once Docker Desktop is Running

**Then run these commands to set up PostgreSQL:**

```powershell
# Start PostgreSQL container
docker run --name recruit-assist-db `
  -e POSTGRES_PASSWORD=postgres `
  -e POSTGRES_DB=recruit_assist `
  -p 5432:5432 `
  -d postgres:15

# Wait a few seconds for PostgreSQL to start
Start-Sleep -Seconds 5

# Verify it's running
docker ps

# Run database setup
cd recruit-assist-api
python setup_database.py
```

---

## 📥 If You DON'T Have Docker Desktop (Installation)

### Download & Install Docker Desktop

1. **Go to**: https://www.docker.com/products/docker-desktop/
2. **Click**: "Download for Windows"
3. **Run the installer**: `Docker Desktop Installer.exe`
4. **Follow the installer**:
   - Accept terms
   - Choose installation location
   - Enable WSL 2 (if prompted)
5. **Restart your computer** (if prompted)
6. **Launch Docker Desktop** from Start menu
7. **Wait for first-time setup** (may take a few minutes)

### System Requirements

- Windows 10 64-bit: Pro, Enterprise, or Education (Build 19041 or higher)
- OR Windows 11 64-bit
- WSL 2 feature enabled
- Virtualization enabled in BIOS

### Check if WSL 2 is Available

```powershell
wsl --status
```

If WSL 2 is not installed, Docker Desktop installer will guide you through it.

---

## 🔍 Quick Check Commands

**Check if Docker Desktop is installed:**
```powershell
Test-Path "C:\Program Files\Docker\Docker\Docker Desktop.exe"
# Returns: True (you have it) or False (need to install)
```

**Check if Docker Desktop is running:**
```powershell
docker ps
# If running: Shows containers or empty list
# If not running: Error about connection
```

**Check Docker version:**
```powershell
docker --version
# You have: Docker version 28.1.1
```

---

## 🎯 Your Next Steps

Since you **already have Docker Desktop installed**:

1. **Start Docker Desktop** (from Start menu)
2. **Wait for it to fully start** (whale icon appears)
3. **Run the PostgreSQL setup commands** above
4. **Run the database setup script**

That's it! You're ready to go.

---

## 💡 Alternative: If Docker Desktop Won't Start

If Docker Desktop has issues starting, you can:

1. **Install PostgreSQL directly** (see `DATABASE_SETUP_GUIDE.md`)
2. **Use SQLite for testing** (I can modify the code temporarily)

Let me know if Docker Desktop starts successfully or if you need help with alternatives!

