@echo off
REM ⚡ Quick Start - Phase 2 (Training)
REM Run this to start model training

echo.
echo =================================
echo   Phase 2: Model Training
echo =================================
echo.

REM Check if in virtual environment
if not defined VIRTUAL_ENV (
    echo ❌ Virtual environment not activated!
    echo.
    echo Run this first:
    echo   venv\Scripts\activate.bat
    echo.
    pause
    exit /b 1
)

echo ✅ Virtual environment active

REM Check if training data exists
if not exist "data\training_data.jsonl" (
    echo ❌ Training data not found!
    echo.
    echo Run Phase 1 first:
    echo   phase1_quickstart.bat
    echo.
    pause
    exit /b 1
)

echo ✅ Training data found

REM Check GPU
echo.
echo Checking GPU...
python -c "import torch; exit(0 if torch.cuda.is_available() else 1)" 2>nul
if errorlevel 1 (
    echo ❌ GPU not available!
    echo.
    echo This training requires a CUDA-capable GPU.
    echo Check: nvidia-smi
    echo.
    pause
    exit /b 1
)

echo ✅ GPU available (CUDA enabled)

REM Show menu
:menu
echo.
echo =================================
echo What would you like to do?
echo.
echo 1. Check system readiness
echo 2. Start training
echo 3. View training log
echo 4. Check progress
echo 5. Resume from checkpoint
echo 6. Exit
echo.

set /p choice="Enter choice (1-6): "

if "%choice%"=="1" goto readiness
if "%choice%"=="2" goto train
if "%choice%"=="3" goto viewlog
if "%choice%"=="4" goto progress
if "%choice%"=="5" goto resume
if "%choice%"=="6" goto end
echo ❌ Invalid choice
goto menu

:readiness
echo.
echo === System Readiness Check ===
echo.

echo GPU Information:
python -c "import torch; print(f'  Device: {torch.cuda.get_device_name(0)}'); print(f'  VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB')"
echo.

echo Training Data:
for %%A in ("data\training_data.jsonl") do (
    set size=%%~zA
    set /a sizeMB=!size! / 1048576
    echo   Size: !sizeMB! MB
)
echo.

echo Training Estimate:
echo   Expected time: 13-18 hours
echo   Checkpoints: Every ~7-8 hours
echo.

echo ✅ System ready for training!
echo.
pause
goto menu

:train
echo.
echo Starting training...
echo.
echo ⏰ Estimated time: 13-18 hours
echo 💾 Checkpoints saved every 500 steps
echo 🛑 Press Ctrl+C to stop (will save checkpoint)
echo.
echo Training will start in 5 seconds...
timeout /t 5 /nobreak >nul
echo.

python training\train_lora.py
pause
goto menu

:viewlog
echo.
if exist "logs\training.log" (
    echo === Training Log (Last 50 lines) ===
    echo.
    powershell -Command "Get-Content 'logs\training.log' -Tail 50"
    echo.
) else (
    echo ❌ Training log not found
    echo Training hasn't started yet.
    echo.
)
pause
goto menu

:progress
echo.
echo === Training Progress ===
echo.

if exist "logs\training.log" (
    REM Get latest step
    echo 📊 Latest Progress:
    powershell -Command "Get-Content 'logs\training.log' | Select-String 'Step \d+/\d+' | Select-Object -Last 1 | ForEach-Object { $_.Line }"
    echo.
    
    REM Get loss trend
    echo 📉 Recent Loss Values:
    powershell -Command "Get-Content 'logs\training.log' | Select-String 'Loss:' | Select-Object -Last 3 | ForEach-Object { $_.Line }"
    echo.
    
    REM GPU status
    echo 🎮 GPU Status:
    nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu --format=csv,noheader,nounits 2>nul
    echo.
) else (
    echo ❌ Training hasn't started yet
    echo.
)

pause
goto menu

:resume
echo.
echo Checking for checkpoints...
echo.

if not exist "adapters\discord-lora\checkpoint-*" (
    echo ❌ No checkpoints found
    echo.
    pause
    goto menu
)

echo Available checkpoints:
dir /b /ad "adapters\discord-lora\checkpoint-*"
echo.

set /p checkpoint="Enter checkpoint name: "
if exist "adapters\discord-lora\%checkpoint%" (
    echo.
    echo Resuming from: %checkpoint%
    echo.
    timeout /t 3 /nobreak >nul
    python training\train_lora.py --resume "adapters\discord-lora\%checkpoint%"
) else (
    echo ❌ Checkpoint not found
)

pause
goto menu

:end
echo.
echo Goodbye!
echo.
exit /b 0
