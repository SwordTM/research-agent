# Research Agent - Environment Setup Script
# Run this script once to set up your development environment

Write-Host "[SETUP] Research Agent - Environment Setup" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$PythonDir = Join-Path $ProjectRoot "python"
$WebDir = Join-Path $ProjectRoot "research-agent-web"

# Step 1: Check Python installation
Write-Host "[1/8] Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  [OK] $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  [ERROR] Python not found! Please install Python 3.10 or higher" -ForegroundColor Red
    Write-Host "     Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# Step 2: Check Node.js installation
Write-Host ""
Write-Host "[2/8] Checking Node.js installation..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    Write-Host "  [OK] Node.js $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "  [ERROR] Node.js not found! Please install Node.js 18 or higher" -ForegroundColor Red
    Write-Host "     Download from: https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

# Step 3: Create Python virtual environment
Write-Host ""
Write-Host "[3/8] Setting up Python virtual environment..." -ForegroundColor Yellow
Push-Location $PythonDir

$VenvPath = Join-Path $PythonDir "venv"
if (Test-Path $VenvPath) {
    Write-Host "  [INFO] Virtual environment already exists" -ForegroundColor Cyan
} else {
    Write-Host "  Creating virtual environment..." -ForegroundColor Gray
    python -m venv venv
    Write-Host "  [OK] Virtual environment created" -ForegroundColor Green
}

# Step 4: Install Python dependencies
Write-Host ""
Write-Host "[4/8] Installing Python dependencies..." -ForegroundColor Yellow
Write-Host "  This may take a few minutes..." -ForegroundColor Gray

& ".\venv\Scripts\Activate.ps1"
pip install --upgrade pip | Out-Null
pip install -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host "  [OK] Python dependencies installed" -ForegroundColor Green
} else {
    Write-Host "  [WARNING] Some dependencies may have failed to install" -ForegroundColor Yellow
}

Pop-Location

# Step 5: Create .env file if it doesn't exist
Write-Host ""
Write-Host "[5/8] Configuring environment variables..." -ForegroundColor Yellow
$EnvFile = Join-Path $PythonDir ".env"

if (Test-Path $EnvFile) {
    Write-Host "  [INFO] .env file already exists" -ForegroundColor Cyan
} else {
    # Create .env file
    $envContent = @"
# Gemini API Key (required)
GEMINI_API_KEY=your_api_key_here

# Logging
LOG_LEVEL=INFO

# Paths
OUTPUT_DIR=../research-agent-web/public/slides
TEMP_DIR=temp_scenes
"@
    Set-Content -Path $EnvFile -Value $envContent
    Write-Host "  [OK] Created .env file at: $EnvFile" -ForegroundColor Green
    Write-Host "  [WARNING] IMPORTANT: Edit this file and add your GEMINI_API_KEY!" -ForegroundColor Yellow
}

# Step 6: Install Next.js dependencies
Write-Host ""
Write-Host "[6/8] Installing Next.js dependencies..." -ForegroundColor Yellow
Push-Location $WebDir

if (Test-Path "node_modules") {
    Write-Host "  [INFO] node_modules already exists" -ForegroundColor Cyan
    $response = Read-Host "  Reinstall? (y/N)"
    if ($response -eq 'y' -or $response -eq 'Y') {
        Remove-Item -Recurse -Force node_modules
        npm install
    }
} else {
    npm install
}

if ($LASTEXITCODE -eq 0) {
    Write-Host "  [OK] Next.js dependencies installed" -ForegroundColor Green
} else {
    Write-Host "  [ERROR] Failed to install Next.js dependencies" -ForegroundColor Red
}

Pop-Location

# Step 7: Create necessary directories
Write-Host ""
Write-Host "[7/8] Creating necessary directories..." -ForegroundColor Yellow

$dirs = @(
    (Join-Path $PythonDir "temp_scenes"),
    (Join-Path $WebDir "public\slides"),
    (Join-Path $PythonDir "logs")
)

foreach ($dir in $dirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "  [OK] Created: $dir" -ForegroundColor Green
    } else {
        Write-Host "  [INFO] Already exists: $dir" -ForegroundColor Cyan
    }
}

# Step 8: Check FFmpeg (optional but recommended)
Write-Host ""
Write-Host "[8/8] Checking FFmpeg installation (for Manim)..." -ForegroundColor Yellow
try {
    $ffmpegVersion = ffmpeg -version 2>&1 | Select-Object -First 1
    Write-Host "  [OK] FFmpeg installed" -ForegroundColor Green
} catch {
    Write-Host "  [WARNING] FFmpeg not found (optional but recommended for Manim)" -ForegroundColor Yellow
    Write-Host "     Download from: https://ffmpeg.org/download.html" -ForegroundColor Gray
}

# Summary
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  Setup Complete!" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "NEXT STEPS:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  1. Edit the .env file and add your GEMINI_API_KEY:" -ForegroundColor White
Write-Host "     $EnvFile" -ForegroundColor Gray
Write-Host ""
Write-Host "  2. Start the development environment:" -ForegroundColor White
Write-Host "     .\dev-start.ps1" -ForegroundColor Cyan
Write-Host "     or" -ForegroundColor Gray
Write-Host "     npm run dev" -ForegroundColor Cyan
Write-Host ""
Write-Host "  3. Open your browser to:" -ForegroundColor White
Write-Host "     http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "DOCUMENTATION:" -ForegroundColor Yellow
Write-Host "  - DEV_SETUP.md - Development environment guide" -ForegroundColor White
Write-Host "  - MANIM_SLIDES_IMPLEMENTATION_GUIDE.md - Implementation details" -ForegroundColor White
Write-Host "  - python/MCP_SETUP.md - MCP server documentation" -ForegroundColor White
Write-Host ""
