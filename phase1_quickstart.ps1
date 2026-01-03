# ⚡ Quick Start - Phase 1
# Run this to get started fast!

Write-Host ""
Write-Host "=================================" -ForegroundColor Cyan
Write-Host "  Phase 1: Data Collection" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Check if in virtual environment
if (-not $env:VIRTUAL_ENV) {
    Write-Host "❌ Virtual environment not activated!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Run these commands first:" -ForegroundColor Yellow
    Write-Host "  python -m venv venv" -ForegroundColor White
    Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor White
    Write-Host "  pip install -r requirements.txt" -ForegroundColor White
    Write-Host ""
    exit 1
}

Write-Host "✅ Virtual environment active" -ForegroundColor Green

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "❌ .env file not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Creating .env from template..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "✅ .env created" -ForegroundColor Green
    Write-Host ""
    Write-Host "⚠️  IMPORTANT: Edit .env and add your credentials:" -ForegroundColor Yellow
    Write-Host "  - DISCORD_BOT_TOKEN" -ForegroundColor White
    Write-Host "  - DISCORD_GUILD_ID" -ForegroundColor White
    Write-Host "  - DISCORD_CHANNEL_ID" -ForegroundColor White
    Write-Host ""
    Write-Host "Then run this script again." -ForegroundColor Yellow
    Write-Host ""
    notepad .env
    exit 0
}

Write-Host "✅ .env file exists" -ForegroundColor Green

# Check if credentials are set
$envContent = Get-Content .env -Raw
if ($envContent -match "your_bot_token_here" -or $envContent -match "your_server_id_here") {
    Write-Host "⚠️  .env file needs configuration!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Please update these values in .env:" -ForegroundColor Yellow
    Write-Host "  - DISCORD_BOT_TOKEN=your_bot_token_here" -ForegroundColor White
    Write-Host "  - DISCORD_GUILD_ID=your_server_id_here" -ForegroundColor White
    Write-Host "  - DISCORD_CHANNEL_ID=your_channel_id_here" -ForegroundColor White
    Write-Host ""
    notepad .env
    exit 0
}

Write-Host "✅ Credentials configured" -ForegroundColor Green
Write-Host ""

# Show menu
Write-Host "What would you like to do?" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Collect messages (backfill)" -ForegroundColor White
Write-Host "2. Analyze data" -ForegroundColor White
Write-Host "3. Prepare training data" -ForegroundColor White
Write-Host "4. Run complete pipeline (1 → 2 → 3)" -ForegroundColor White
Write-Host "5. View logs" -ForegroundColor White
Write-Host "6. Check progress" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Enter choice (1-6)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "Starting message collection..." -ForegroundColor Cyan
        Write-Host "This will take 30-90 minutes depending on your settings." -ForegroundColor Yellow
        Write-Host "Press Ctrl+C to stop (progress will be saved)." -ForegroundColor Yellow
        Write-Host ""
        python scripts/backfill_messages.py
    }
    "2" {
        Write-Host ""
        Write-Host "Analyzing collected data..." -ForegroundColor Cyan
        Write-Host ""
        python scripts/analyze_training_data.py
    }
    "3" {
        Write-Host ""
        Write-Host "Preparing training data..." -ForegroundColor Cyan
        Write-Host ""
        python scripts/prepare_training_data.py
    }
    "4" {
        Write-Host ""
        Write-Host "Running complete Phase 1 pipeline..." -ForegroundColor Cyan
        Write-Host ""
        
        Write-Host "[1/3] Collecting messages..." -ForegroundColor Yellow
        python scripts/backfill_messages.py
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Collection failed!" -ForegroundColor Red
            exit 1
        }
        
        Write-Host ""
        Write-Host "[2/3] Analyzing data..." -ForegroundColor Yellow
        python scripts/analyze_training_data.py
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Analysis failed!" -ForegroundColor Red
            exit 1
        }
        
        Write-Host ""
        Write-Host "[3/3] Preparing training data..." -ForegroundColor Yellow
        python scripts/prepare_training_data.py
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Preparation failed!" -ForegroundColor Red
            exit 1
        }
        
        Write-Host ""
        Write-Host "=================================" -ForegroundColor Green
        Write-Host "  ✅ Phase 1 Complete!" -ForegroundColor Green
        Write-Host "=================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Next: Say 'Start Phase 2' to begin training!" -ForegroundColor Cyan
    }
    "5" {
        Write-Host ""
        Write-Host "Which log would you like to view?" -ForegroundColor Cyan
        Write-Host "1. Backfill log" -ForegroundColor White
        Write-Host "2. Preparation log" -ForegroundColor White
        $logChoice = Read-Host "Enter choice (1-2)"
        
        if ($logChoice -eq "1") {
            if (Test-Path "logs/backfill.log") {
                Get-Content "logs/backfill.log" -Tail 50
            } else {
                Write-Host "❌ Backfill log not found" -ForegroundColor Red
            }
        } elseif ($logChoice -eq "2") {
            if (Test-Path "logs/prep.log") {
                Get-Content "logs/prep.log" -Tail 50
            } else {
                Write-Host "❌ Preparation log not found" -ForegroundColor Red
            }
        }
    }
    "6" {
        Write-Host ""
        Write-Host "Checking progress..." -ForegroundColor Cyan
        Write-Host ""
        
        # Check checkpoint
        if (Test-Path "data/backfill_checkpoint.json") {
            $checkpoint = Get-Content "data/backfill_checkpoint.json" | ConvertFrom-Json
            Write-Host "📊 Collection Progress:" -ForegroundColor Yellow
            Write-Host "  Messages collected: $($checkpoint.message_count)" -ForegroundColor White
            Write-Host "  Last updated: $($checkpoint.timestamp)" -ForegroundColor White
            Write-Host ""
        }
        
        # Check files
        Write-Host "📁 Files:" -ForegroundColor Yellow
        if (Test-Path "data/raw_messages.jsonl") {
            $size = (Get-Item "data/raw_messages.jsonl").Length / 1MB
            Write-Host "  ✅ raw_messages.jsonl ($([math]::Round($size, 2)) MB)" -ForegroundColor Green
        } else {
            Write-Host "  ❌ raw_messages.jsonl (not found)" -ForegroundColor Red
        }
        
        if (Test-Path "data/training_data.jsonl") {
            $size = (Get-Item "data/training_data.jsonl").Length / 1MB
            Write-Host "  ✅ training_data.jsonl ($([math]::Round($size, 2)) MB)" -ForegroundColor Green
        } else {
            Write-Host "  ⏭️  training_data.jsonl (not created yet)" -ForegroundColor Yellow
        }
        
        Write-Host ""
    }
    default {
        Write-Host "❌ Invalid choice" -ForegroundColor Red
    }
}

Write-Host ""
