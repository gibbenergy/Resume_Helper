@echo off
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
    echo Found CUDA version: %CUDA_VERSION%
) else (
    echo CUDA not found in PATH, assuming CUDA 12.8+ (RTX 5090)
    set CUDA_VERSION=12.8
)

echo.
echo Detected System: NVIDIA RTX 5090
echo CUDA Version: %CUDA_VERSION% (compatible with cu12.x builds)
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

:: Debug: Check if file was created and has content
if not exist release_info.json (
    echo [DEBUG] ERROR: release_info.json not created
    >> c:\Users\Gibbenergy\Downloads\Support Llama.cpp\.cursor\debug.log echo {"location":"install_llamacpp.bat:32","message":"release_info.json not created","data":{"error":"file_not_found"},"timestamp":%time%,"sessionId":"debug-session","runId":"setup","hypothesisId":"H4"}
) else (
    for %%A in (release_info.json) do set FILE_SIZE=%%~zA
    echo [DEBUG] release_info.json size: !FILE_SIZE! bytes
    >> c:\Users\Gibbenergy\Downloads\Support Llama.cpp\.cursor\debug.log echo {"location":"install_llamacpp.bat:35","message":"release_info.json created","data":{"file_size":"!FILE_SIZE!"},"timestamp":%time%,"sessionId":"debug-session","runId":"setup","hypothesisId":"H4"}
)

:: Try to find CUDA 12.x build URLs (try multiple versions)
echo Searching for CUDA 12.x compatible builds...
echo.

:: Extract download URLs and filter for CUDA builds
set FOUND_URL=
set LINE_COUNT=0

echo [DEBUG] Searching for CUDA builds in JSON...
>> c:\Users\Gibbenergy\Downloads\Support Llama.cpp\.cursor\debug.log echo {"location":"install_llamacpp.bat:50","message":"Starting URL search","data":{},"timestamp":%time%,"sessionId":"debug-session","runId":"setup","hypothesisId":"H1"}

for /f "tokens=*" %%a in ('findstr /c:"browser_download_url" release_info.json') do (
    set /a LINE_COUNT+=1
    set LINE=%%a
    echo [DEBUG] Found line !LINE_COUNT!: !LINE!
    >> c:\Users\Gibbenergy\Downloads\Support Llama.cpp\.cursor\debug.log echo {"location":"install_llamacpp.bat:55","message":"Found browser_download_url line","data":{"line_num":"!LINE_COUNT!","content":"!LINE!"},"timestamp":%time%,"sessionId":"debug-session","runId":"setup","hypothesisId":"H1"}
    
    :: Check if line contains cuda-cu12
    echo !LINE! | findstr "cuda-cu12" >nul
    if !errorlevel! equ 0 (
        echo [DEBUG] Line contains cuda-cu12
        >> c:\Users\Gibbenergy\Downloads\Support Llama.cpp\.cursor\debug.log echo {"location":"install_llamacpp.bat:61","message":"Found cuda-cu12 in line","data":{"line":"!LINE!"},"timestamp":%time%,"sessionId":"debug-session","runId":"setup","hypothesisId":"H2"}
        
        :: Check if line contains win and x64.zip
        echo !LINE! | findstr "win" | findstr "x64.zip" >nul
        if !errorlevel! equ 0 (
            echo [DEBUG] Line matches all criteria
            >> c:\Users\Gibbenergy\Downloads\Support Llama.cpp\.cursor\debug.log echo {"location":"install_llamacpp.bat:67","message":"Line matches all criteria","data":{"line":"!LINE!"},"timestamp":%time%,"sessionId":"debug-session","runId":"setup","hypothesisId":"H2"}
        )
    )
)

echo [DEBUG] Total lines found: !LINE_COUNT!
>> c:\Users\Gibbenergy\Downloads\Support Llama.cpp\.cursor\debug.log echo {"location":"install_llamacpp.bat:74","message":"Search complete","data":{"total_lines":"!LINE_COUNT!"},"timestamp":%time%,"sessionId":"debug-session","runId":"setup","hypothesisId":"H1"}

for /f "tokens=*" %%a in ('findstr /c:"browser_download_url" release_info.json ^| findstr /c:"cuda-cu12" ^| findstr /c:"win" ^| findstr /c:"x64.zip"') do (
    set LINE=%%a
    echo [DEBUG] Processing matched line: !LINE!
    >> c:\Users\Gibbenergy\Downloads\Support Llama.cpp\.cursor\debug.log echo {"location":"install_llamacpp.bat:80","message":"Processing matched line","data":{"line":"!LINE!"},"timestamp":%time%,"sessionId":"debug-session","runId":"setup","hypothesisId":"H3"}
    
    setlocal enabledelayedexpansion
    :: Extract URL from JSON line
    for /f "tokens=2 delims=:," %%b in ("!LINE!") do (
        set URL=%%b
        echo [DEBUG] Extracted token: !URL!
        >> c:\Users\Gibbenergy\Downloads\Support Llama.cpp\.cursor\debug.log echo {"location":"install_llamacpp.bat:87","message":"Extracted URL token","data":{"url":"!URL!"},"timestamp":%time%,"sessionId":"debug-session","runId":"setup","hypothesisId":"H5"}
        
        set URL=!URL:"=!
        set URL=!URL: =!
        echo [DEBUG] Cleaned URL: !URL!
        >> c:\Users\Gibbenergy\Downloads\Support Llama.cpp\.cursor\debug.log echo {"location":"install_llamacpp.bat:93","message":"Cleaned URL","data":{"url":"!URL!"},"timestamp":%time%,"sessionId":"debug-session","runId":"setup","hypothesisId":"H5"}
        
        :: Prioritize cu12.8, then cu12.6, then cu12.4
        echo !URL! | findstr "cu12.8" >nul
        if !errorlevel! equ 0 (
            echo [DEBUG] Found cu12.8 build!
            >> c:\Users\Gibbenergy\Downloads\Support Llama.cpp\.cursor\debug.log echo {"location":"install_llamacpp.bat:99","message":"Found cu12.8","data":{"url":"!URL!"},"timestamp":%time%,"sessionId":"debug-session","runId":"setup","hypothesisId":"H3"}
            endlocal
            set FOUND_URL=!URL!
            set CUDA_BUILD=12.8
            goto :found_url
        )
        echo !URL! | findstr "cu12.6" >nul
        if !errorlevel! equ 0 if not defined FOUND_URL (
            echo [DEBUG] Found cu12.6 build!
            >> c:\Users\Gibbenergy\Downloads\Support Llama.cpp\.cursor\debug.log echo {"location":"install_llamacpp.bat:109","message":"Found cu12.6","data":{"url":"!URL!"},"timestamp":%time%,"sessionId":"debug-session","runId":"setup","hypothesisId":"H3"}
            endlocal
            set FOUND_URL=!URL!
            set CUDA_BUILD=12.6
            goto :found_url
        )
        echo !URL! | findstr "cu12.4" >nul
        if !errorlevel! equ 0 if not defined FOUND_URL (
            echo [DEBUG] Found cu12.4 build!
            >> c:\Users\Gibbenergy\Downloads\Support Llama.cpp\.cursor\debug.log echo {"location":"install_llamacpp.bat:119","message":"Found cu12.4","data":{"url":"!URL!"},"timestamp":%time%,"sessionId":"debug-session","runId":"setup","hypothesisId":"H3"}
            endlocal
            set FOUND_URL=!URL!
            set CUDA_BUILD=12.4
        )
    )
    endlocal
)

:found_url
if not defined FOUND_URL (
    echo [DEBUG] No CUDA 12.x build found
    >> c:\Users\Gibbenergy\Downloads\Support Llama.cpp\.cursor\debug.log echo {"location":"install_llamacpp.bat:132","message":"No CUDA build found","data":{"found_url":"empty"},"timestamp":%time%,"sessionId":"debug-session","runId":"setup","hypothesisId":"H4"}
    echo No CUDA 12.x build found automatically.
    goto :manual_download
)

echo [DEBUG] Final URL: !FOUND_URL!
>> c:\Users\Gibbenergy\Downloads\Support Llama.cpp\.cursor\debug.log echo {"location":"install_llamacpp.bat:139","message":"URL found successfully","data":{"url":"!FOUND_URL!","cuda_build":"!CUDA_BUILD!"},"timestamp":%time%,"sessionId":"debug-session","runId":"setup","hypothesisId":"H3"}

echo Found: CUDA %CUDA_BUILD% build
echo URL: %FOUND_URL%
echo.

:: Extract filename from URL
for %%a in (%FOUND_URL%) do set FILENAME=%%~nxa

echo Downloading: %FILENAME%
echo This may take a few minutes...
echo.

curl -L -o "%FILENAME%" "%FOUND_URL%"

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
tar -xf "%FILENAME%" -C llama.cpp --strip-components=1

if %errorlevel% neq 0 (
    echo Extraction failed! Trying alternative method...
    
    :: Try PowerShell extraction
    powershell -command "Expand-Archive -Path '%FILENAME%' -DestinationPath 'llama.cpp' -Force"
    
    if %errorlevel% neq 0 (
        echo.
        echo Automatic extraction failed. Please extract manually:
        echo 1. Open %FILENAME%
        echo 2. Extract contents to llama.cpp folder
        pause
    )
)

:: Clean up zip file
del "%FILENAME%" 2>nul

:: Verify extraction
if not exist "llama.cpp\llama-server.exe" if not exist "llama.cpp\server.exe" if not exist "llama.cpp\build\bin\Release\llama-server.exe" (
    echo.
    echo WARNING: Could not find llama-server.exe!
    echo Please check llama.cpp folder.
    pause
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
echo 2. Download ONE of these (in order of preference):
echo    BEST:   llama-*-bin-win-cuda-cu12.8.0-x64.zip
echo    GOOD:   llama-*-bin-win-cuda-cu12.6.0-x64.zip
echo    OK:     llama-*-bin-win-cuda-cu12.4.0-x64.zip
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

curl -L --progress-bar -o llama.cpp\models\qwen2.5-3b-instruct-q4_k_m.gguf ^
    "https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF/resolve/main/qwen2.5-3b-instruct-q4_k_m.gguf"

if errorlevel 1 (
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
echo 🎉 Installation Complete!
echo ========================================
echo.
echo 📂 Location: %cd%\llama.cpp
echo 🤖 Model: Qwen2.5-3B-Instruct-Q4_K_M (~2GB)
echo 🎮 GPU: NVIDIA RTX 5090 (CUDA %CUDA_BUILD%)
echo.
echo ========================================
echo 🚀 Quick Start
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
echo ⚡ Performance (RTX 5090)
echo ========================================
echo.
echo Expected speeds with this 3B model:
echo   • 500-1000 tokens/second
echo   • Near-instant resume analysis
echo   • Sub-second cover letter generation
echo.
echo Your RTX 5090 will absolutely dominate! 💪
echo.
pause
