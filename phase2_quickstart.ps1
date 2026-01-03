# ⚡ Quick Start - Phase 2 (Training)
# Run this to start model training

Write-Host ""
Write-Host "=================================" -ForegroundColor Cyan
Write-Host "  Phase 2: Model Training" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Check if in virtual environment
if (-not $env:VIRTUAL_ENV) {
    Write-Host "❌ Virtual environment not activated!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Run this first:" -ForegroundColor Yellow
    Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor White
    Write-Host ""
    exit 1
}

Write-Host "✅ Virtual environment active" -ForegroundColor Green

# Check if training data exists
if (-not (Test-Path "data\training_data.jsonl")) {
    Write-Host "❌ Training data not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Run Phase 1 first:" -ForegroundColor Yellow
    Write-Host "  .\phase1_quickstart.ps1" -ForegroundColor White
    Write-Host ""
    exit 1
}

$dataSize = (Get-Item "data\training_data.jsonl").Length / 1MB
Write-Host "✅ Training data found ($([math]::Round($dataSize, 2)) MB)" -ForegroundColor Green

# Check GPU
Write-Host ""
Write-Host "Checking GPU..." -ForegroundColor Cyan
$gpuCheck = python -c "import torch; print('CUDA' if torch.cuda.is_available() else 'NONE')" 2>$null
if ($gpuCheck -eq "CUDA") {
    Write-Host "✅ GPU available (CUDA enabled)" -ForegroundColor Green
} else {
    Write-Host "❌ GPU not available!" -ForegroundColor Red
    Write-Host ""
    Write-Host "This training requires a CUDA-capable GPU." -ForegroundColor Yellow
    Write-Host "Check: nvidia-smi" -ForegroundColor White
    Write-Host ""
    exit 1
}

# Check training dependencies
Write-Host ""
Write-Host "Checking training dependencies..." -ForegroundColor Cyan
$deps = @("transformers", "peft", "bitsandbytes", "accelerate")
$missing = @()

foreach ($dep in $deps) {
    $check = python -c "import $dep" 2>$null
    if ($LASTEXITCODE -ne 0) {
        $missing += $dep
    }
}

if ($missing.Count -gt 0) {
    Write-Host "⚠️  Missing dependencies: $($missing -join ', ')" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Installing missing packages..." -ForegroundColor Cyan
    pip install $missing -q
    Write-Host "✅ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "✅ All dependencies present" -ForegroundColor Green
}

# Show menu
Write-Host ""
Write-Host "=================================" -ForegroundColor Cyan
Write-Host "What would you like to do?" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Check system readiness" -ForegroundColor White
Write-Host "2. Start training (foreground)" -ForegroundColor White
Write-Host "3. Start training (background)" -ForegroundColor White
Write-Host "4. Resume from checkpoint" -ForegroundColor White
Write-Host "5. View training log" -ForegroundColor White
Write-Host "6. Check training progress" -ForegroundColor White
Write-Host "7. Exit" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Enter choice (1-7)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "=== System Readiness Check ===" -ForegroundColor Cyan
        Write-Host ""
        
        # GPU details
        Write-Host "GPU Information:" -ForegroundColor Yellow
        python -c "import torch; print(f'  Device: {torch.cuda.get_device_name(0)}'); print(f'  VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB')"
        Write-Host ""
        
        # Disk space
        Write-Host "Disk Space:" -ForegroundColor Yellow
        $drive = Get-PSDrive C
        $freeGB = [math]::Round($drive.Free / 1GB, 2)
        Write-Host "  Free: $freeGB GB" -ForegroundColor White
        if ($freeGB -lt 15) {
            Write-Host "  ⚠️  Less than 15GB free - may run out of space!" -ForegroundColor Yellow
        } else {
            Write-Host "  ✅ Sufficient space" -ForegroundColor Green
        }
        Write-Host ""
        
        # Training data
        Write-Host "Training Data:" -ForegroundColor Yellow
        $lines = (Get-Content "data\training_data.jsonl" | Measure-Object -Line).Lines
        Write-Host "  Examples: $lines" -ForegroundColor White
        Write-Host "  Size: $([math]::Round($dataSize, 2)) MB" -ForegroundColor White
        Write-Host ""
        
        # Time estimate
        Write-Host "Training Estimate:" -ForegroundColor Yellow
        Write-Host "  Expected time: 13-18 hours" -ForegroundColor White
        Write-Host "  Checkpoints: Every ~7-8 hours (step 500)" -ForegroundColor White
        Write-Host ""
        
        Write-Host "✅ System ready for training!" -ForegroundColor Green
        Write-Host ""
        pause
    }
    
    "2" {
        Write-Host ""
        Write-Host "Starting training in foreground..." -ForegroundColor Cyan
        Write-Host ""
        Write-Host "⏰ Estimated time: 13-18 hours" -ForegroundColor Yellow
        Write-Host "💾 Checkpoints saved every 500 steps (~7-8 hours)" -ForegroundColor Yellow
        Write-Host "🛑 Press Ctrl+C to stop (will save checkpoint)" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Training will start in 5 seconds..." -ForegroundColor Cyan
        Start-Sleep -Seconds 5
        Write-Host ""
        
        python training\train_lora.py
    }
    
    "3" {
        Write-Host ""
        Write-Host "Starting training in background..." -ForegroundColor Cyan
        Write-Host ""
        Write-Host "⏰ Estimated time: 13-18 hours" -ForegroundColor Yellow
        Write-Host "📊 Monitor: .\phase2_quickstart.ps1 → Option 6" -ForegroundColor Yellow
        Write-Host "📝 Logs: logs\training.log" -ForegroundColor Yellow
        Write-Host ""
        
        # Start in minimized window
        Start-Process powershell -ArgumentList @(
            "-NoExit",
            "-Command",
            "cd '$PWD'; .\venv\Scripts\Activate.ps1; Write-Host 'Training started...'; python training\train_lora.py"
        ) -WindowStyle Minimized
        
        Write-Host "✅ Training started in background!" -ForegroundColor Green
        Write-Host ""
        Write-Host "To check progress:" -ForegroundColor Cyan
        Write-Host "  .\phase2_quickstart.ps1 → Option 6" -ForegroundColor White
        Write-Host ""
        pause
    }
    
    "4" {
        Write-Host ""
        Write-Host "Checking for checkpoints..." -ForegroundColor Cyan
        
        $checkpoints = Get-ChildItem "adapters\discord-lora\checkpoint-*" -Directory -ErrorAction SilentlyContinue | Sort-Object Name
        
        if ($checkpoints.Count -eq 0) {
            Write-Host "❌ No checkpoints found" -ForegroundColor Red
            Write-Host ""
            pause
        } else {
            Write-Host ""
            Write-Host "Available checkpoints:" -ForegroundColor Yellow
            for ($i = 0; $i -lt $checkpoints.Count; $i++) {
                Write-Host "  $($i+1). $($checkpoints[$i].Name)"
            }
            Write-Host ""
            
            $cpChoice = Read-Host "Select checkpoint (1-$($checkpoints.Count))"
            $cpIndex = [int]$cpChoice - 1
            
            if ($cpIndex -ge 0 -and $cpIndex -lt $checkpoints.Count) {
                $checkpoint = $checkpoints[$cpIndex].FullName
                Write-Host ""
                Write-Host "Resuming from: $($checkpoints[$cpIndex].Name)" -ForegroundColor Cyan
                Write-Host ""
                Start-Sleep -Seconds 3
                
                python training\train_lora.py --resume $checkpoint
            } else {
                Write-Host "Invalid selection" -ForegroundColor Red
            }
        }
    }
    
    "5" {
        Write-Host ""
        if (Test-Path "logs\training.log") {
            Write-Host "=== Training Log (Last 50 lines) ===" -ForegroundColor Cyan
            Write-Host ""
            Get-Content "logs\training.log" -Tail 50
            Write-Host ""
        } else {
            Write-Host "❌ Training log not found" -ForegroundColor Red
            Write-Host "Training hasn't started yet." -ForegroundColor Yellow
            Write-Host ""
        }
        pause
    }
    
    "6" {
        Write-Host ""
        Write-Host "=== Training Progress ===" -ForegroundColor Cyan
        Write-Host ""
        
        if (Test-Path "logs\training.log") {
            # Get latest step
            $latestStep = Get-Content "logs\training.log" | Select-String "Step \d+/\d+" | Select-Object -Last 1
            if ($latestStep) {
                Write-Host "📊 Latest Progress:" -ForegroundColor Yellow
                Write-Host "  $($latestStep.Line)" -ForegroundColor White
                Write-Host ""
            }
            
            # Get loss trend
            $losses = Get-Content "logs\training.log" | Select-String "Loss: [\d\.]+" | Select-Object -Last 5
            if ($losses.Count -gt 0) {
                Write-Host "📉 Recent Loss Values:" -ForegroundColor Yellow
                foreach ($loss in $losses) {
                    Write-Host "  $($loss.Line)" -ForegroundColor White
                }
                Write-Host ""
            }
            
            # Check checkpoints
            $checkpoints = Get-ChildItem "adapters\discord-lora\checkpoint-*" -Directory -ErrorAction SilentlyContinue
            if ($checkpoints) {
                Write-Host "💾 Saved Checkpoints:" -ForegroundColor Yellow
                foreach ($cp in $checkpoints | Sort-Object Name) {
                    Write-Host "  ✅ $($cp.Name)" -ForegroundColor Green
                }
                Write-Host ""
            }
            
            # GPU status
            Write-Host "🎮 GPU Status:" -ForegroundColor Yellow
            try {
                $gpu = nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu --format=csv,noheader,nounits 2>$null
                if ($gpu) {
                    $parts = $gpu -split ','
                    Write-Host "  Utilization: $($parts[0].Trim())%" -ForegroundColor White
                    Write-Host "  VRAM: $($parts[1].Trim()) / $($parts[2].Trim()) MB" -ForegroundColor White
                    Write-Host "  Temperature: $($parts[3].Trim())°C" -ForegroundColor White
                }
            } catch {
                Write-Host "  (nvidia-smi not available)" -ForegroundColor Gray
            }
            Write-Host ""
            
        } else {
            Write-Host "❌ Training hasn't started yet" -ForegroundColor Red
            Write-Host ""
        }
        
        pause
    }
    
    "7" {
        Write-Host ""
        Write-Host "Goodbye!" -ForegroundColor Cyan
        Write-Host ""
        exit 0
    }
    
    default {
        Write-Host "❌ Invalid choice" -ForegroundColor Red
    }
}

Write-Host ""
