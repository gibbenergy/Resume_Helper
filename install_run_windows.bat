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
set "CONDA_DIR=%LocalAppData%\SimpleResumeConda"

if exist "%CONDA_DIR%\python.exe" (
    echo ✔ Existing Miniconda detected – reusing it
) else (
    echo ℹ Installing Miniconda via winget…
    winget install -e --id Anaconda.Miniconda3 ^
          --location "%CONDA_DIR%" ^
          --silent --accept-package-agreements --accept-source-agreements --force
    if not "%ERRORLEVEL%"=="0" if not "%ERRORLEVEL%"=="1" (
    	echo ❌ winget reported failure (exit %ERRORLEVEL%) & pause & exit /b 1
    )

    rem ----- wait loop -----
    echo Waiting for Miniconda to finish…
    for /L %%i in (1,1,60) do (
        if exist "%CONDA_DIR%\python.exe" goto :python_ready
        timeout /t 2 >nul
    )
    echo ❌ Miniconda did not appear in %CONDA_DIR% after 120 s
    pause & exit /b 1
    :python_ready
)

rem now it’s safe to use python
set "PATH=%CONDA_DIR%;%CONDA_DIR%\Scripts;%CONDA_DIR%\Library\bin;%PATH%"
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
::  3-a. Virtual environment
:: -----------------------------------------------------

python -m pip show virtualenv >nul 2>&1 || python -m pip install virtualenv

if not exist venv (
    echo Creating virtual environment...
    python -m virtualenv venv || (
        echo ❌ venv creation failed & pause & exit /b 1
    )
) else (
    echo ✔ venv already exists
)

echo Activating venv...
call venv\Scripts\activate.bat || (
    echo ❌ venv activate failed & pause & exit /b 1
)

:: -----------------------------------------------------
::  3-b. Install GTK runtime (tschoonj) if missing
:: -----------------------------------------------------
set "GTK_DIR=%ProgramFiles%\GTK3-Runtime Win64\bin"
set "GTK_EXE=gtk3-runtime-3.24.31-2022-01-04-ts-win64.exe"
set "GTK_URL=https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases/download/2022-01-04/%GTK_EXE%"

rem 3-b-1.   Already installed?
if exist "%GTK_DIR%\libgtk-3-0.dll" (
    echo ✔ GTK runtime already present
) else (
    echo Installing GTK runtime for WeasyPrint…
    powershell -NoLogo -NoProfile -Command ^
        "Invoke-WebRequest -Uri '%GTK_URL%' -OutFile '%TEMP%\%GTK_EXE%'"
    start /wait "" "%TEMP%\%GTK_EXE%" /S
    if errorlevel 1 (
        echo ❌ GTK installer failed & pause & exit /b 1
    )
)

rem 3-b-2.   Prepend the DLL directory to PATH if not already in it
echo %PATH% | find /I "%GTK_DIR%" >nul 2>&1 || (
    set "PATH=%GTK_DIR%;%PATH%"
    echo ℹ Added GTK runtime to PATH for this session
)


:: -----------------------------------------------------
::  4. Install dependencies
:: -----------------------------------------------------

:: make sure "Common AppData" exists – pip / platformdirs require it
reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders" /v "Common AppData" >nul 2>&1
if errorlevel 1 (
    reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders" ^
            /v "Common AppData" /t REG_SZ /d "%ProgramData%" /f >nul
)

echo Installing requirements...
pip --isolated install -r requirements.txt
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
