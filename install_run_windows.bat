@echo off
echo Resume Helper Setup
echo.

:: Check Python exists
python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found. Install from https://python.org
    pause
    exit /b 1
)

:: Install uv if not present
uv --version >nul 2>&1
if errorlevel 1 (
    echo Installing uv...
    python -m pip install uv --quiet
)

:: Create environment if needed
if not exist .venv (
    echo Creating environment...
    uv venv
    call .venv\Scripts\activate.bat
    echo Installing packages...
    uv pip install -r requirements.txt
    echo Installing Playwright browsers...
    playwright install chromium
) else (
    call .venv\Scripts\activate.bat
    echo Installing Playwright browsers...
    playwright install chromium
)

:: Check if port 53441 is in use and kill that specific process
echo Checking port 53441...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":53441" ^| findstr "LISTENING"') do taskkill /F /PID %%a >nul 2>&1 && echo Stopped old instance PID %%a && timeout /t 2 /nobreak >nul

:: Launch app once
echo Starting app...
cd Resume_Helper
python app.py --host 0.0.0.0 --port 53441
cd ..
pause
