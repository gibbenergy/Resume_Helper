@echo off
setlocal enabledelayedexpansion
echo ========================================
echo llama.cpp Automated Setup for RTX 5090
echo ========================================
echo.

:: Check if already installed
if exist "llama.cpp" (
    echo llama.cpp folder already exists.
    choice /C YN /M "Do you want to reinstall"
    if errorlevel 2 goto :skip_install
    echo Removing old installation...
    rmdir /s /q llama.cpp
)

echo.
echo [1/4] Detecting CUDA version...
echo.

:: Detect CUDA version using nvidia-smi
nvcc --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=5" %%v in ('nvcc --version ^| findstr "release"') do set CUDA_VERSION=%%v
    echo Found CUDA version: !CUDA_VERSION!
) else (
    echo CUDA not found in PATH, assuming CUDA 12.8+ (RTX 5090)
    set CUDA_VERSION=12.8
)

echo.
echo Detected System: NVIDIA RTX 5090
echo CUDA Version: !CUDA_VERSION! (compatible with cu12.x builds)
echo.

:: Check if curl is available
where curl >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: curl not found. Please install curl first.
    pause
    exit /b 1
)

:: Check if tar is available (Windows 10+ has it built-in)
where tar >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: tar not found. Falling back to manual extraction.
    goto :manual_download
)

echo.
echo [2/4] Fetching latest llama.cpp release...
echo.

:: Get latest release info (follow redirects with -L flag)
echo Fetching latest release info from GitHub...
curl -L -s https://api.github.com/repos/ggerganov/llama.cpp/releases/latest > release_info.json

:: Verify file was created
if not exist release_info.json (
    echo ERROR: Failed to download release info
    goto :manual_download
)

echo Searching for CUDA 12.x compatible builds...
echo.

:: Extract download URLs and filter for CUDA builds
set FOUND_URL=
set CUDA_BUILD=

:: RTX 5090 requires CUDA 12.8+ minimum (but 12.8 doesn't exist, so we use 13.1)
:: Search in priority order: 13.1 -> 12.6 -> 12.4 (last resort)

:: Try CUDA 13.1 first (best for RTX 5090)
for /f "tokens=*" %%a in ('findstr /c:"browser_download_url" release_info.json ^| findstr /c:"win-cuda-13" ^| findstr /c:"x64.zip" ^| findstr /v "cudart"') do (
    set LINE=%%a
    :: Extract URL: remove everything before "https" and remove trailing quotes/commas
    set LINE=!LINE:*https=https!
    set LINE=!LINE:",=!
    set LINE=!LINE:"=!
    set URL=!LINE!
    set FOUND_URL=!URL!
    set CUDA_BUILD=13.1
    goto :found_url
)

:: Try CUDA 12.6 (might work but not recommended)
for /f "tokens=*" %%a in ('findstr /c:"browser_download_url" release_info.json ^| findstr /c:"win-cuda-12.6" ^| findstr /c:"x64.zip" ^| findstr /v "cudart"') do (
    set LINE=%%a
    set LINE=!LINE:*https=https!
    set LINE=!LINE:",=!
    set LINE=!LINE:"=!
    set FOUND_URL=!LINE!
    set CUDA_BUILD=12.6
    goto :found_url
)

:: CUDA 12.4 (last resort - may not work properly with RTX 5090)
for /f "tokens=*" %%a in ('findstr /c:"browser_download_url" release_info.json ^| findstr /c:"win-cuda-12.4" ^| findstr /c:"x64.zip" ^| findstr /v "cudart"') do (
    set LINE=%%a
    set LINE=!LINE:*https=https!
    set LINE=!LINE:",=!
    set LINE=!LINE:"=!
    set FOUND_URL=!LINE!
    set CUDA_BUILD=12.4
    goto :found_url
)

:found_url
if not defined FOUND_URL (
    echo No CUDA 12.x/13.x build found automatically.
    goto :manual_download
)

echo Found: CUDA !CUDA_BUILD! build
echo URL: !FOUND_URL!
echo.

:: Extract filename from URL
for %%a in (!FOUND_URL!) do set FILENAME=%%~nxa

echo Downloading: !FILENAME!
echo This may take a few minutes...
echo.

curl -L -o "!FILENAME!" "!FOUND_URL!"

if %errorlevel% neq 0 (
    echo.
    echo Download failed!
    goto :manual_download
)

echo.
echo [3/4] Extracting llama.cpp...
echo.

:: Create directory
mkdir llama.cpp 2>nul

:: Extract using tar (built into Windows 10+)
tar -xf "!FILENAME!" -C llama.cpp

if %errorlevel% neq 0 (
    echo Extraction failed! Trying alternative method...
    
    :: Try PowerShell extraction
    powershell -command "Expand-Archive -Path '!FILENAME!' -DestinationPath 'llama.cpp' -Force"
    
    if %errorlevel% neq 0 (
        echo.
        echo Automatic extraction failed. Please extract manually:
        echo 1. Open !FILENAME!
        echo 2. Extract contents to llama.cpp folder
        pause
    )
)

:: Clean up zip file
del "!FILENAME!" 2>nul

:: Verify extraction - check for llama-server.exe in the root
if not exist "llama.cpp\llama-server.exe" (
    echo.
    echo WARNING: Could not find llama-server.exe!
    echo Please check llama.cpp folder.
    echo.
    dir llama.cpp\*.exe 2>nul
    pause
) else (
    echo.
    echo SUCCESS: llama.cpp extracted successfully!
    echo Found llama-server.exe and other executables.
    echo.
)

goto :download_model

:manual_download
echo.
echo ========================================
echo MANUAL DOWNLOAD REQUIRED
echo ========================================
echo.
echo Please download llama.cpp manually:
echo.
echo 1. Go to: https://github.com/ggerganov/llama.cpp/releases/latest
echo.
echo 2. Download ONE of these (in order of preference for RTX 5090):
echo    BEST:   llama-*-bin-win-cuda-13.1-x64.zip (CUDA 13.1 - Best for RTX 5090)
echo    OK:     llama-*-bin-win-cuda-12.6-x64.zip (May work)
echo    AVOID:  llama-*-bin-win-cuda-12.4-x64.zip (Too old for RTX 5090)
echo.
echo 3. Extract to: %cd%\llama.cpp\
echo.
pause

if not exist "llama.cpp" (
    echo ERROR: llama.cpp folder not found!
    pause
    exit /b 1
)

:skip_install
:download_model

echo.
echo [4/4] Downloading test model (Qwen2.5-3B-Instruct ~2GB)...
echo.

if not exist "llama.cpp\models" (
    mkdir llama.cpp\models
)

if exist "llama.cpp\models\qwen2.5-3b-instruct-q4_k_m.gguf" (
    echo Model already downloaded.
    goto :create_script
)

echo Downloading from HuggingFace (this will take a few minutes)...
echo Progress may appear slow at first, please be patient...
echo.

curl -L --progress-bar -o llama.cpp\models\qwen2.5-3b-instruct-q4_k_m.gguf "https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF/resolve/main/qwen2.5-3b-instruct-q4_k_m.gguf"

if %errorlevel% neq 0 (
    echo.
    echo Download failed! You can download manually from:
    echo https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF/tree/main
    echo Save as: llama.cpp\models\qwen2.5-3b-instruct-q4_k_m.gguf
    echo.
    pause
)

:create_script
echo.
echo Creating startup script...
echo.

:: Create optimized start script for RTX 5090
(
echo @echo off
echo echo ========================================
echo echo llama.cpp Server ^(RTX 5090 Optimized^)
echo echo ========================================
echo echo.
echo echo Server URL: http://localhost:8080
echo echo API Endpoint: http://localhost:8080/v1
echo echo.
echo echo Press Ctrl+C to stop the server
echo echo.
echo.
echo :: Find server executable
echo if exist "build\bin\Release\llama-server.exe" ^(
echo     set SERVER_EXE=build\bin\Release\llama-server.exe
echo ^) else if exist "bin\llama-server.exe" ^(
echo     set SERVER_EXE=bin\llama-server.exe
echo ^) else if exist "llama-server.exe" ^(
echo     set SERVER_EXE=llama-server.exe
echo ^) else if exist "server.exe" ^(
echo     set SERVER_EXE=server.exe
echo ^) else ^(
echo     echo ERROR: Could not find llama-server.exe
echo     echo Please check your installation
echo     pause
echo     exit /b 1
echo ^)
echo.
echo echo Starting server with RTX 5090 settings:
echo echo   - Model: Qwen2.5-3B-Instruct
echo echo   - GPU Layers: ALL ^(-ngl 99^)
echo echo   - Context: 16K tokens
echo echo   - Port: 8080
echo echo.
echo.
echo :: RTX 5090 Optimized Parameters
echo %%SERVER_EXE%% -m models\qwen2.5-3b-instruct-q4_k_m.gguf ^
echo     --host 0.0.0.0 ^
echo     --port 8080 ^
echo     -c 16384 ^
echo     -ngl 99 ^
echo     --mlock
echo.
echo pause
) > llama.cpp\start_server.bat

echo.
echo ========================================
echo SUCCESS - Installation Complete!
echo ========================================
echo.
echo Location: %cd%\llama.cpp
echo Model: Qwen2.5-3B-Instruct-Q4_K_M (~2GB)
if defined CUDA_BUILD (
    echo GPU: NVIDIA RTX 5090 (CUDA !CUDA_BUILD!)
) else (
    echo GPU: NVIDIA RTX 5090
)
echo.
echo ========================================
echo Quick Start
echo ========================================
echo.
echo 1. Start the server:
echo    cd llama.cpp
echo    start_server.bat
echo.
echo 2. Wait for: "HTTP server listening"
echo.
echo 3. In Resume Helper:
echo    - Provider: llama.cpp
echo    - Base URL: http://localhost:8080/v1
echo    - API Key: (leave empty)
echo    - Click "Set"
echo.
echo ========================================
echo Performance (RTX 5090)
echo ========================================
echo.
echo Expected speeds with this 3B model:
echo   - 500-1000 tokens/second
echo   - Near-instant resume analysis
echo   - Sub-second cover letter generation
echo.
echo Your RTX 5090 will absolutely dominate!
echo.
pause
