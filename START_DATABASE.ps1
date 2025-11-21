# PowerShell script to set up PostgreSQL database with Docker
# Run this after Docker Desktop is started

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Bershaw Recruitment - Database Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
Write-Host "Checking Docker..." -ForegroundColor Yellow
$dockerCheck = docker ps 2>&1
if ($dockerCheck -match "error|cannot find") {
    Write-Host "[ERROR] Docker Desktop is not running" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please:" -ForegroundColor Yellow
    Write-Host "1. Start Docker Desktop from Start menu" -ForegroundColor White
    Write-Host "2. Wait for whale icon in system tray" -ForegroundColor White
    Write-Host "3. Run this script again" -ForegroundColor White
    exit 1
}

Write-Host "[OK] Docker is running" -ForegroundColor Green
Write-Host ""

# Check if container already exists
Write-Host "Checking for existing container..." -ForegroundColor Yellow
$existing = docker ps -a --filter "name=recruit-assist-db" --format "{{.Names}}"
if ($existing -eq "recruit-assist-db") {
    Write-Host "Container 'recruit-assist-db' already exists" -ForegroundColor Yellow
    $running = docker ps --filter "name=recruit-assist-db" --format "{{.Names}}"
    if ($running -eq "recruit-assist-db") {
        Write-Host "[OK] Container is already running" -ForegroundColor Green
    } else {
        Write-Host "Starting existing container..." -ForegroundColor Yellow
        docker start recruit-assist-db
        Start-Sleep -Seconds 3
    }
} else {
    # Create new container
    Write-Host "Creating PostgreSQL container..." -ForegroundColor Yellow
    docker run --name recruit-assist-db `
        -e POSTGRES_PASSWORD=postgres `
        -e POSTGRES_DB=recruit_assist `
        -p 5432:5432 `
        -d postgres:15
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] PostgreSQL container created" -ForegroundColor Green
        Write-Host "Waiting for PostgreSQL to start..." -ForegroundColor Yellow
        Start-Sleep -Seconds 5
    } else {
        Write-Host "[ERROR] Failed to create container" -ForegroundColor Red
        exit 1
    }
}

# Verify container is running
Write-Host ""
Write-Host "Verifying container status..." -ForegroundColor Yellow
$status = docker ps --filter "name=recruit-assist-db" --format "{{.Status}}"
if ($status) {
    Write-Host "[OK] Container is running: $status" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Container is not running" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "[SUCCESS] PostgreSQL is ready!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next step: Run database setup script" -ForegroundColor Yellow
Write-Host "  cd recruit-assist-api" -ForegroundColor White
Write-Host "  python setup_database.py" -ForegroundColor White
Write-Host ""

