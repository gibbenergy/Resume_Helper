@echo off
echo Resume Helper Setup
echo.

:: Check Python exists - try both 'python' and 'py' commands
set PYTHON_CMD=python
python --version >nul 2>&1
if errorlevel 1 (
    py --version >nul 2>&1
    if errorlevel 1 (
        echo Python not found. Install from https://python.org
        pause
        exit /b 1
    ) else (
        set PYTHON_CMD=py
    )
)

echo Found Python: %PYTHON_CMD%

:: Create environment if needed
if not exist .venv (
    echo Creating virtual environment...
    %PYTHON_CMD% -m venv .venv
    call .venv\Scripts\activate.bat
    echo Installing uv...
    python -m pip install uv --quiet
    echo Installing packages...
    python -m uv pip install -r requirements.txt
    echo Installing Playwright browsers...
    python -m playwright install chromium
) else (
    call .venv\Scripts\activate.bat
)

:: Kill any old Resume Helper instances
echo Checking for old Resume Helper instances...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":53441" ^| findstr "LISTENING"') do (
    echo Stopping old instance on port 53441 (PID %%a)
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":7860" ^| findstr "LISTENING"') do (
    echo Stopping old instance on port 7860 (PID %%a)
    taskkill /F /PID %%a >nul 2>&1
)

:: Wait for ports to be released
echo Waiting for ports to be released...
timeout /t 3 /nobreak >nul

:: Launch app (using venv's python with explicit path)
echo Starting app on port 53441...
.venv\Scripts\python.exe Resume_Helper\app.py --host 0.0.0.0 --port 53441
pause
