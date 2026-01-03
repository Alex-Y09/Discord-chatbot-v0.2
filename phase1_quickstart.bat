@echo off
REM ⚡ Quick Start - Phase 1
REM Run this to get started fast!

echo.
echo =================================
echo   Phase 1: Data Collection
echo =================================
echo.

REM Check if in virtual environment
if not defined VIRTUAL_ENV (
    echo ❌ Virtual environment not activated!
    echo.
    echo Run these commands first:
    echo   python -m venv venv
    echo   venv\Scripts\activate.bat
    echo   pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo ✅ Virtual environment active

REM Check if .env exists
if not exist ".env" (
    echo ❌ .env file not found!
    echo.
    echo Creating .env from template...
    copy .env.example .env >nul
    echo ✅ .env created
    echo.
    echo ⚠️  IMPORTANT: Edit .env and add your credentials:
    echo   - DISCORD_BOT_TOKEN
    echo   - DISCORD_GUILD_ID
    echo   - DISCORD_CHANNEL_ID
    echo.
    echo Opening .env in notepad...
    echo Then run this script again.
    echo.
    notepad .env
    pause
    exit /b 0
)

echo ✅ .env file exists

REM Check if credentials are set (simplified check)
findstr /C:"your_bot_token_here" .env >nul 2>&1
if %errorlevel% equ 0 (
    echo ⚠️  .env file needs configuration!
    echo.
    echo Please update these values in .env:
    echo   - DISCORD_BOT_TOKEN=your_bot_token_here
    echo   - DISCORD_GUILD_ID=your_server_id_here
    echo   - DISCORD_CHANNEL_ID=your_channel_id_here
    echo.
    echo Opening .env in notepad...
    notepad .env
    pause
    exit /b 0
)

echo ✅ Credentials configured
echo.

REM Show menu
:menu
echo What would you like to do?
echo.
echo 1. Collect messages (backfill)
echo 2. Analyze data
echo 3. Prepare training data
echo 4. Run complete pipeline (1 -^> 2 -^> 3)
echo 5. View logs
echo 6. Check progress
echo 7. Exit
echo.

set /p choice="Enter choice (1-7): "

if "%choice%"=="1" goto collect
if "%choice%"=="2" goto analyze
if "%choice%"=="3" goto prepare
if "%choice%"=="4" goto pipeline
if "%choice%"=="5" goto logs
if "%choice%"=="6" goto progress
if "%choice%"=="7" goto end
echo ❌ Invalid choice
echo.
goto menu

:collect
echo.
echo Starting message collection...
echo This will take 30-90 minutes depending on your settings.
echo Press Ctrl+C to stop (progress will be saved).
echo.
python scripts\backfill_messages.py
goto menu

:analyze
echo.
echo Analyzing collected data...
echo.
python scripts\analyze_training_data.py
echo.
pause
goto menu

:prepare
echo.
echo Preparing training data...
echo.
python scripts\prepare_training_data.py
echo.
pause
goto menu

:pipeline
echo.
echo Running complete Phase 1 pipeline...
echo.

echo [1/3] Collecting messages...
python scripts\backfill_messages.py
if errorlevel 1 (
    echo ❌ Collection failed!
    pause
    goto menu
)

echo.
echo [2/3] Analyzing data...
python scripts\analyze_training_data.py
if errorlevel 1 (
    echo ❌ Analysis failed!
    pause
    goto menu
)

echo.
echo [3/3] Preparing training data...
python scripts\prepare_training_data.py
if errorlevel 1 (
    echo ❌ Preparation failed!
    pause
    goto menu
)

echo.
echo =================================
echo   ✅ Phase 1 Complete!
echo =================================
echo.
echo Next: Say 'Start Phase 2' to begin training!
echo.
pause
goto menu

:logs
echo.
echo Which log would you like to view?
echo 1. Backfill log
echo 2. Preparation log
echo 3. Back to menu
echo.
set /p logChoice="Enter choice (1-3): "

if "%logChoice%"=="1" (
    if exist "logs\backfill.log" (
        echo.
        echo === Last 50 lines of backfill.log ===
        echo.
        powershell -Command "Get-Content 'logs\backfill.log' -Tail 50"
        echo.
    ) else (
        echo ❌ Backfill log not found
    )
    pause
    goto menu
)

if "%logChoice%"=="2" (
    if exist "logs\prep.log" (
        echo.
        echo === Last 50 lines of prep.log ===
        echo.
        powershell -Command "Get-Content 'logs\prep.log' -Tail 50"
        echo.
    ) else (
        echo ❌ Preparation log not found
    )
    pause
    goto menu
)

if "%logChoice%"=="3" goto menu
echo ❌ Invalid choice
pause
goto logs

:progress
echo.
echo Checking progress...
echo.

REM Check checkpoint
if exist "data\backfill_checkpoint.json" (
    echo 📊 Collection Progress:
    powershell -Command "$c = Get-Content 'data\backfill_checkpoint.json' | ConvertFrom-Json; Write-Host '  Messages collected:' $c.message_count; Write-Host '  Last updated:' $c.timestamp"
    echo.
)

REM Check files
echo 📁 Files:
if exist "data\raw_messages.jsonl" (
    for %%A in ("data\raw_messages.jsonl") do (
        set size=%%~zA
        set /a sizeMB=!size! / 1048576
        echo   ✅ raw_messages.jsonl (!sizeMB! MB^)
    )
) else (
    echo   ❌ raw_messages.jsonl (not found^)
)

if exist "data\training_data.jsonl" (
    for %%A in ("data\training_data.jsonl") do (
        set size=%%~zA
        set /a sizeMB=!size! / 1048576
        echo   ✅ training_data.jsonl (!sizeMB! MB^)
    )
) else (
    echo   ⏭️  training_data.jsonl (not created yet^)
)

echo.
pause
goto menu

:end
echo.
echo Goodbye!
echo.
exit /b 0
