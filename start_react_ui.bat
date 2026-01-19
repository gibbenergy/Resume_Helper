@echo off
REM Start script for Resume Helper with React UI and FastAPI backend
REM This script uses UV for fast Python package management

echo ========================================
echo Resume Helper - React UI Startup
echo ========================================
echo.

REM Check if UV is installed
echo [1/4] Checking UV installation...
uv --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: UV is not installed or not in PATH
    echo.
    echo UV is a fast Python package installer (10-100x faster than pip!)
    echo.
    echo To install UV on Windows:
    echo   PowerShell: irm https://astral.sh/uv/install.ps1 ^| iex
    echo   Or download from: https://github.com/astral-sh/uv
    echo.
    pause
    exit /b 1
)
echo UV found
echo.

REM Check if Node.js is installed
echo Checking Node.js installation...
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js 18+ from https://nodejs.org
    echo.
    pause
    exit /b 1
)
echo Node.js found
echo.

REM Change to script directory
cd /d "%~dp0"

REM Check if port 8000 is in use
echo Checking backend port...
set BACKEND_PORT=8000
netstat -ano 2>&1 | findstr ":8000" | findstr "LISTENING" >nul 2>&1
if not errorlevel 1 (
    echo WARNING: Port 8000 is already in use!
    echo Switching to port 8001 instead...
    set BACKEND_PORT=8001
)
echo.

REM Install Python dependencies with UV (this is FAST!)
echo [2/4] Installing Python dependencies with UV...
echo This is much faster than pip (typically 10-100x faster)
uv sync
if errorlevel 1 (
    echo.
    echo ERROR: Failed to install Python dependencies with UV
    echo.
    pause
    exit /b 1
)
echo Python dependencies installed successfully
echo.

REM Install Node.js dependencies
echo [3/4] Installing Node.js dependencies...
if not exist "frontend\" (
    echo ERROR: frontend directory not found!
    pause
    exit /b 1
)

cd frontend
if exist "node_modules\" (
    echo Node.js dependencies already installed
) else (
    echo Installing Node.js dependencies (this may take a while)...
    call npm install
    if errorlevel 1 (
        echo ERROR: Failed to install Node.js dependencies
        cd ..
        pause
        exit /b 1
    )
)
cd ..
echo.

echo [4/4] Starting servers...
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
echo Starting FastAPI backend server...
start "Resume Helper - FastAPI Backend" cmd /k "cd /d %~dp0 && uv run uvicorn backend.api.main:app --host 127.0.0.1 --port %BACKEND_PORT% --reload"

REM Wait for backend to start
echo Waiting for backend to start...
timeout /t 5 /nobreak >nul

REM Check if backend started successfully
netstat -ano 2>&1 | findstr ":%BACKEND_PORT%" | findstr "LISTENING" >nul 2>&1
if errorlevel 1 (
    echo.
    echo WARNING: Backend may not have started successfully
    echo Check the backend window for errors
    echo.
    timeout /t 2 /nobreak >nul
) else (
    echo Backend is running on port %BACKEND_PORT%
)
echo.

REM Set environment variable for frontend
set VITE_API_URL=http://localhost:%BACKEND_PORT%

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
    pause
    exit /b 1
)

REM If we get here, the frontend stopped
cd ..
echo.
echo Frontend server stopped.
echo Backend may still be running in the other window.
pause
