@echo off
REM Start script for React UI with FastAPI backend using UV
REM This script starts both the FastAPI backend and React frontend

echo ========================================
echo Resume Helper - React UI Startup
echo ========================================
echo.

REM Change to script directory FIRST
cd /d "%~dp0"

REM Check if Python is installed, install if not
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found. Attempting to install via winget...
    winget install Python.Python.3.11 --accept-package-agreements --accept-source-agreements
    if errorlevel 1 (
        echo.
        echo ERROR: Could not auto-install Python
        echo Please download and install Python 3.11+ manually from:
        echo https://www.python.org/
        echo.
        echo After installation, restart this script.
        echo.
        pause
        exit /b 1
    )
    echo.
    echo ========================================
    echo Python installed successfully!
    echo ========================================
    echo.
    echo IMPORTANT: Python was just installed but is not yet available
    echo in this terminal session because the PATH has not been updated.
    echo.
    echo Please close this window and double-click start_react_ui.bat again.
    echo This is a one-time setup step. Future runs will work automatically.
    echo.
    pause
    exit /b 0
)
echo Python found

REM Create virtual environment if it doesn't exist
if not exist ".venv\" (
    echo Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment and install UV
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Check if UV is installed in venv, install if not
uv --version >nul 2>&1
if errorlevel 1 (
    echo Installing UV in virtual environment...
    pip install uv
    if errorlevel 1 (
        echo ERROR: Failed to install UV
        pause
        exit /b 1
    )
)
echo UV ready
echo.

REM Check if Node.js is installed, install if not
echo Checking Node.js installation...
node --version >nul 2>&1
if errorlevel 1 (
    echo Node.js not found. Attempting to install via winget...
    winget install OpenJS.NodeJS.LTS --accept-package-agreements --accept-source-agreements
    if errorlevel 1 (
        echo.
        echo ERROR: Could not auto-install Node.js
        echo Please download and install Node.js 18+ manually from:
        echo https://nodejs.org/
        echo.
        echo After installation, restart this script.
        echo.
        pause
        exit /b 1
    )
    echo.
    echo ========================================
    echo Node.js installed successfully!
    echo ========================================
    echo.
    echo IMPORTANT: Node.js was just installed but is not yet available
    echo in this terminal session because the PATH has not been updated.
    echo.
    echo Please do ONE of the following:
    echo   1. Close this window and double-click start_react_ui.bat again
    echo   2. Or open a NEW command prompt and run start_react_ui.bat
    echo.
    echo This is a one-time setup step. Future runs will work automatically.
    echo.
    pause
    exit /b 0
)
echo Node.js found
echo.

REM Use port 5000 for backend (avoids conflicts with LLM services on 8000, 8080, 1234, 11434)
echo Checking backend port...
set BACKEND_PORT=5000
netstat -ano 2>&1 | findstr ":5000" | findstr "LISTENING" >nul 2>&1
if not errorlevel 1 (
    echo WARNING: Port 5000 is already in use!
    echo Switching to port 5001 instead...
    set BACKEND_PORT=5001
    echo.
)

echo [2/5] Checking Python dependencies...
if exist ".venv\Scripts\uvicorn.exe" (
    echo Python dependencies already installed
) else (
    echo Installing Python dependencies with UV...
    echo This may take a few minutes on first run...
    uv sync --link-mode copy
    if errorlevel 1 (
        echo.
        echo ERROR: Failed to install Python dependencies with UV
        echo.
        pause
        exit /b 1
    )
    echo Python dependencies installed successfully
)
echo.

echo [3/5] Checking Playwright browsers...
dir /b "%LOCALAPPDATA%\ms-playwright\chromium-*" >nul 2>&1
if errorlevel 1 (
    echo Installing Playwright browsers...
    echo This may take a few minutes on first run (downloading ~150MB)...
    uv run playwright install chromium
    if errorlevel 1 (
        echo.
        echo ERROR: Failed to install Playwright browsers
        echo PDF generation will not work without this
        echo.
        pause
        exit /b 1
    )
    echo Playwright browsers installed successfully
) else (
    echo Playwright browsers already installed
)
echo.

echo [4/5] Checking Node.js dependencies...
if not exist "frontend\" (
    echo ERROR: frontend directory not found!
    echo Current directory: %CD%
    echo.
    pause
    exit /b 1
)

cd frontend
if exist "node_modules\" (
    echo Node.js dependencies already installed
) else (
    echo Installing Node.js dependencies...
    call npm install
    if errorlevel 1 (
        echo ERROR: Failed to install Node.js dependencies
        cd ..
        echo.
        pause
        exit /b 1
    )
)
cd ..

echo [5/5] Starting servers...
echo.
echo ========================================
echo Starting FastAPI Backend (Port %BACKEND_PORT%)
echo Starting React Frontend (Port 5174)
echo ========================================
echo.
echo Backend API: http://localhost:%BACKEND_PORT%
echo Frontend UI: http://localhost:5174
echo.
echo Press Ctrl+C to stop both servers
echo.

REM Start FastAPI backend in a new window using UV
echo Starting FastAPI backend server on port %BACKEND_PORT%...
start "Resume Helper - FastAPI Backend" cmd /k "cd /d %~dp0 && call .venv\Scripts\activate.bat && uv run uvicorn backend.api.main:app --host 127.0.0.1 --port %BACKEND_PORT%"

REM Wait for backend to start
echo Waiting for backend to start...
timeout /t 3 /nobreak >nul

REM Check if backend started successfully
netstat -ano 2>&1 | findstr ":%BACKEND_PORT%" | findstr "LISTENING" >nul 2>&1
if errorlevel 1 (
    echo.
    echo WARNING: Backend may not have started successfully on port %BACKEND_PORT%
    echo Check the backend window for errors
    echo.
    timeout /t 2 /nobreak >nul
) else (
    echo Backend is running on port %BACKEND_PORT%
)

REM Set environment variable for frontend
set VITE_API_URL=http://localhost:%BACKEND_PORT%

REM Wait for backend to be fully ready
timeout /t 2 /nobreak >nul

REM Start React frontend
echo Starting React frontend...
cd frontend
if errorlevel 1 (
    echo ERROR: Failed to change to frontend directory
    pause
    exit /b 1
)

REM Open browser after a delay
start "" cmd /c "timeout /t 5 /nobreak >nul && start http://localhost:5174"

REM Start frontend (blocking)
call npm run dev
if errorlevel 1 (
    echo.
    echo ERROR: Frontend failed to start
    cd ..
    echo.
    pause
    exit /b 1
)

REM If we get here, the frontend stopped
cd ..
echo.
echo Frontend server stopped.
echo Backend may still be running in the other window.
pause
