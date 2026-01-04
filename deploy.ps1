# ============================================================
#  DISCORD BOT DEPLOYMENT
#  Quick Start Menu for Phase 3
# ============================================================

# ANSI colors
$ESC = [char]27
$GREEN = "$ESC[32m"
$YELLOW = "$ESC[33m"
$RED = "$ESC[31m"
$BLUE = "$ESC[36m"
$RESET = "$ESC[0m"

function Show-Menu {
    Clear-Host
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "  DISCORD CHATBOT v0.2 - DEPLOYMENT MENU" -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. Check deployment readiness" -ForegroundColor White
    Write-Host "2. Start bot (foreground)" -ForegroundColor White
    Write-Host "3. Start bot (background)" -ForegroundColor White
    Write-Host "4. Stop bot" -ForegroundColor White
    Write-Host "5. View bot logs (live)" -ForegroundColor White
    Write-Host "6. View bot logs (file)" -ForegroundColor White
    Write-Host "7. Test model first" -ForegroundColor White
    Write-Host "8. Exit" -ForegroundColor White
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host ""
}

function Check-Readiness {
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "  DEPLOYMENT READINESS CHECK" -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host ""
    
    $allGood = $true
    
    # Check virtual environment
    if ($env:VIRTUAL_ENV) {
        Write-Host "[OK] Virtual environment activated" -ForegroundColor Green
    } else {
        Write-Host "[X] Virtual environment NOT activated" -ForegroundColor Red
        Write-Host "    Run: .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
        $allGood = $false
    }
    
    # Check .env file
    if (Test-Path ".env") {
        Write-Host "[OK] .env file exists" -ForegroundColor Green
        
        # Check for required variables
        $envContent = Get-Content ".env" -Raw
        
        if ($envContent -match "DISCORD_BOT_TOKEN=.+") {
            Write-Host "[OK] DISCORD_BOT_TOKEN is set" -ForegroundColor Green
        } else {
            Write-Host "[X] DISCORD_BOT_TOKEN not set in .env" -ForegroundColor Red
            $allGood = $false
        }
        
    } else {
        Write-Host "[X] .env file missing" -ForegroundColor Red
        Write-Host "    Copy .env.example to .env and fill in your bot token" -ForegroundColor Yellow
        $allGood = $false
    }
    
    # Check trained model
    if (Test-Path "adapters\discord-lora\adapter_model.safetensors") {
        Write-Host "[OK] Trained model found" -ForegroundColor Green
    } else {
        Write-Host "[X] Trained model not found" -ForegroundColor Red
        Write-Host "    Run Phase 2 training first" -ForegroundColor Yellow
        $allGood = $false
    }
    
    # Check GPU
    try {
        $gpuCheck = python -c "import torch; print(torch.cuda.is_available())" 2>$null
        if ($gpuCheck -eq "True") {
            $gpuName = python -c "import torch; print(torch.cuda.get_device_name(0))" 2>$null
            Write-Host "[OK] GPU available: $gpuName" -ForegroundColor Green
        } else {
            Write-Host "[!] No GPU detected - will use CPU (slower)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "[!] Could not check GPU status" -ForegroundColor Yellow
    }
    
    # Check bot files
    if (Test-Path "src\bot.py") {
        Write-Host "[OK] Bot code found" -ForegroundColor Green
    } else {
        Write-Host "[X] src\bot.py missing" -ForegroundColor Red
        $allGood = $false
    }
    
    # Check dependencies
    try {
        $null = python -c "import discord" 2>&1
        Write-Host "[OK] discord.py installed" -ForegroundColor Green
    } catch {
        Write-Host "[X] discord.py not installed" -ForegroundColor Red
        Write-Host "    Run: pip install discord.py" -ForegroundColor Yellow
        $allGood = $false
    }
    
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan
    
    if ($allGood) {
        Write-Host "[OK] All checks passed! Ready to deploy!" -ForegroundColor Green
    } else {
        Write-Host "[X] Some checks failed. Fix the issues above first." -ForegroundColor Red
    }
    
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host ""
}

function Start-BotForeground {
    Write-Host ""
    Write-Host "Starting bot in foreground..." -ForegroundColor Cyan
    Write-Host "Press Ctrl+C to stop the bot" -ForegroundColor Yellow
    Write-Host ""
    
    python src\bot.py
}

function Start-BotBackground {
    Write-Host ""
    Write-Host "Starting bot in background..." -ForegroundColor Cyan
    
    # Start bot as background job
    $job = Start-Job -ScriptBlock {
        Set-Location $using:PWD
        & ".\venv\Scripts\python.exe" src\bot.py
    }
    
    Write-Host "[OK] Bot started! Job ID: $($job.Id)" -ForegroundColor Green
    Write-Host ""
    Write-Host "To view logs: Select option 5 (View bot logs)" -ForegroundColor Yellow
    Write-Host "To stop: Select option 4 (Stop bot)" -ForegroundColor Yellow
    Write-Host ""
}

function Stop-Bot {
    Write-Host ""
    Write-Host "Checking for running bot..." -ForegroundColor Cyan
    
    # Get all Python jobs
    $jobs = Get-Job | Where-Object { $_.Command -like "*bot.py*" }
    
    if ($jobs.Count -eq 0) {
        Write-Host "[!] No bot jobs found" -ForegroundColor Yellow
    } else {
        foreach ($job in $jobs) {
            Stop-Job -Id $job.Id
            Remove-Job -Id $job.Id
            Write-Host "[OK] Stopped bot job: $($job.Id)" -ForegroundColor Green
        }
    }
    
    Write-Host ""
}

function View-LogsLive {
    Write-Host ""
    Write-Host "Viewing bot logs (live)..." -ForegroundColor Cyan
    Write-Host "Press Ctrl+C to stop viewing" -ForegroundColor Yellow
    Write-Host ""
    
    if (Test-Path "logs\bot.log") {
        Get-Content "logs\bot.log" -Wait -Tail 50
    } else {
        Write-Host "[!] No logs yet. Start the bot first." -ForegroundColor Yellow
        Write-Host ""
    }
}

function View-LogsFile {
    Write-Host ""
    Write-Host "Opening bot logs in notepad..." -ForegroundColor Cyan
    
    if (Test-Path "logs\bot.log") {
        notepad "logs\bot.log"
    } else {
        Write-Host "[!] No logs yet. Start the bot first." -ForegroundColor Yellow
        Write-Host ""
    }
}

function Test-Model {
    Write-Host ""
    Write-Host "Running model test..." -ForegroundColor Cyan
    Write-Host ""
    
    python scripts\test_model.py
}

# Main loop
while ($true) {
    Show-Menu
    $choice = Read-Host "Select an option (1-8)"
    
    switch ($choice) {
        "1" {
            Check-Readiness
            Read-Host "Press Enter to continue"
        }
        "2" {
            Start-BotForeground
            Read-Host "Press Enter to continue"
        }
        "3" {
            Start-BotBackground
            Read-Host "Press Enter to continue"
        }
        "4" {
            Stop-Bot
            Read-Host "Press Enter to continue"
        }
        "5" {
            View-LogsLive
            Read-Host "Press Enter to continue"
        }
        "6" {
            View-LogsFile
            Read-Host "Press Enter to continue"
        }
        "7" {
            Test-Model
            Read-Host "Press Enter to continue"
        }
        "8" {
            Write-Host ""
            Write-Host "Goodbye!" -ForegroundColor Cyan
            Write-Host ""
            exit
        }
        default {
            Write-Host ""
            Write-Host "[X] Invalid option. Please select 1-8." -ForegroundColor Red
            Start-Sleep -Seconds 2
        }
    }
}
