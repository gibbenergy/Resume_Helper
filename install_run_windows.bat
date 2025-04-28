@echo off
setlocal enabledelayedexpansion
chcp 65001 > nul            :: allow UTF-8 for emojis

echo ===================================================
echo  SimpleResumeApp – Windows One-Click Setup
echo ===================================================
echo.

:: -----------------------------------------------------
::  1. Ensure Python 3.11+ is available (install locally if not)
:: -----------------------------------------------------
where python > nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found - installing a private copy...
    set PY_DIR=%LocalAppData%\SimpleResumePython
    if not exist "%PY_DIR%" mkdir "%PY_DIR%"
    set PY_ZIP=python-3.11-embed-amd64.zip
    set PY_URL=https://www.python.org/ftp/python/3.11.8/%PY_ZIP%
    echo Downloading %PY_URL%
    powershell -Command "Invoke-WebRequest -Uri '%PY_URL%' -OutFile '%PY_DIR%\%PY_ZIP%'"
    if not exist "%PY_DIR%\%PY_ZIP%" (
        echo ❌ Failed to download Python.  Please connect to the Internet and try again.
        pause & exit /b 1
    )
    echo Extracting...
    powershell -Command ^
      "Add-Type -A 'System.IO.Compression.FileSystem';" ^
      "[IO.Compression.ZipFile]::ExtractToDirectory('%PY_DIR%\%PY_ZIP%','%PY_DIR%')"

    del "%PY_DIR%\%PY_ZIP%"
    echo Installed private Python to %PY_DIR%
    set "PATH=%PY_DIR%;%PATH%"
) else (
    echo ✔ Found existing Python on PATH
)

python --version || (echo ❌ Python still not available & pause & exit /b 1)

:: -----------------------------------------------------
::  2. Ensure pip
:: -----------------------------------------------------
python -m pip --version > nul 2>&1
if %errorlevel% neq 0 (
    echo pip not found – bootstrapping...
    python -m ensurepip --upgrade || (
        echo ❌ Could not install pip
        pause & exit /b 1
    )
)

:: -----------------------------------------------------
::  3. Virtual environment
:: -----------------------------------------------------
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv || (
        echo ❌ venv creation failed & pause & exit /b 1
    )
) else (
    echo ✔ venv already exists
)

echo Activating venv...
call venv\Scripts\activate.bat || (echo ❌ venv activate failed & pause & exit /b 1)

:: -----------------------------------------------------
::  4. Install dependencies
:: -----------------------------------------------------
echo Installing requirements...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ⚠  requirements.txt failed – installing core libs only
    pip install gradio openai google-generativeai weasyprint python-dotenv
    if %errorlevel% neq 0 (
        echo ❌ Dependency install failed & pause & exit /b 1
    )
)

:: -----------------------------------------------------
::  5. Free port 53630 if busy
:: -----------------------------------------------------
echo Checking port 53630...
for /f "tokens=5" %%p in ('netstat -ano ^| findstr :53630 ^| findstr LISTENING') do (
    echo Closing process %%p occupying port 53630…
    taskkill /F /PID %%p
)

:: -----------------------------------------------------
::  6. Launch the app
:: -----------------------------------------------------
echo.
echo ===================================================
echo  Starting SimpleResumeApp on http://localhost:53630
echo ===================================================
echo (Close this window or press Ctrl+C to stop)
echo.

python -m Resume_Helper.app --host 0.0.0.0 --port 53630 --allow-iframe --allow-cors
if %errorlevel% neq 0 (
    echo ❌ App failed to start – see errors above.
)

:: -----------------------------------------------------
::  7. Clean-up
:: -----------------------------------------------------
call venv\Scripts\deactivate.bat
echo.
echo Press any key to exit…
pause > nul
