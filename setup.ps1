# Quick Setup Script for Discord Chatbot v0.2
# Run this after creating your .env file

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Discord Chatbot v0.2 Setup" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "[1/6] Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($pythonVersion -match "Python 3\.1[0-9]") {
    Write-Host "✓ $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "✗ Python 3.10+ required! Found: $pythonVersion" -ForegroundColor Red
    exit 1
}

# Create directory structure
Write-Host "[2/6] Creating directory structure..." -ForegroundColor Yellow
$directories = @(
    "data",
    "data/vector_db",
    "logs",
    "adapters",
    "src",
    "src/memory",
    "src/model",
    "src/utils",
    "scripts",
    "training",
    "tests"
)

foreach ($dir in $directories) {
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
}
Write-Host "✓ Directories created" -ForegroundColor Green

# Create __init__.py files
Write-Host "[3/6] Creating Python package files..." -ForegroundColor Yellow
$initFiles = @(
    "src/__init__.py",
    "src/memory/__init__.py",
    "src/model/__init__.py",
    "src/utils/__init__.py"
)

foreach ($file in $initFiles) {
    New-Item -ItemType File -Force -Path $file | Out-Null
}
Write-Host "✓ Package files created" -ForegroundColor Green

# Check for .env file
Write-Host "[4/6] Checking configuration..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "✓ .env file found" -ForegroundColor Green
} else {
    Write-Host "⚠ .env file not found!" -ForegroundColor Red
    Write-Host "  Creating from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✓ .env created - PLEASE EDIT IT WITH YOUR BOT TOKEN!" -ForegroundColor Yellow
}

# Create virtual environment
Write-Host "[5/6] Setting up virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "⚠ Virtual environment already exists, skipping..." -ForegroundColor Yellow
} else {
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
}

# Install dependencies
Write-Host "[6/6] Installing dependencies..." -ForegroundColor Yellow
Write-Host "  This may take a few minutes..." -ForegroundColor Cyan

# Activate venv and install
& ".\venv\Scripts\Activate.ps1"
pip install --upgrade pip | Out-Null
pip install -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "✗ Dependency installation failed!" -ForegroundColor Red
    exit 1
}

# Summary
Write-Host ""
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Edit .env file with your Discord bot token" -ForegroundColor White
Write-Host "  2. Copy code from IMPLEMENTATION.md to src/ files" -ForegroundColor White
Write-Host "  3. Run: python src/bot.py" -ForegroundColor White
Write-Host ""
Write-Host "Documentation:" -ForegroundColor Yellow
Write-Host "  • README.md - Quick start guide" -ForegroundColor White
Write-Host "  • PDR.md - Complete architecture and specifications" -ForegroundColor White
Write-Host "  • IMPLEMENTATION.md - Code implementations" -ForegroundColor White
Write-Host "  • SETUP_SUMMARY.md - What's been created and next steps" -ForegroundColor White
Write-Host ""
Write-Host "Happy coding! 🚀" -ForegroundColor Cyan
