@echo off
echo ========================================
echo llama.cpp Setup for Windows
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
echo [1/3] Downloading llama.cpp pre-built binary...
echo.

:: Check if curl is available
where curl >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: curl not found. Please install curl or download manually from:
    echo https://github.com/ggerganov/llama.cpp/releases
    pause
    exit /b 1
)

:: Get latest release URL
echo Fetching latest release info...
curl -s https://api.github.com/repos/ggerganov/llama.cpp/releases/latest > release_info.json

:: Extract download URL for Windows with CUDA (or CPU if you prefer)
echo.
echo Available options:
echo [1] CPU only (works on any PC, slower)
echo [2] CUDA (NVIDIA GPU, much faster - RECOMMENDED if you have NVIDIA)
echo [3] Skip download - I'll download manually
echo.
choice /C 123 /M "Select your option"

if errorlevel 3 goto :manual_download
if errorlevel 2 goto :cuda_download
if errorlevel 1 goto :cpu_download

:cpu_download
echo.
echo Downloading CPU version...
:: You'll need to manually get the URL from GitHub releases
echo.
echo Please download manually from:
echo https://github.com/ggerganov/llama.cpp/releases/latest
echo Look for: llama-*-bin-win-avx2-x64.zip
echo.
pause
goto :manual_download

:cuda_download
echo.
echo Downloading CUDA version (requires NVIDIA GPU)...
echo.
echo Please download manually from:
echo https://github.com/ggerganov/llama.cpp/releases/latest
echo Look for: llama-*-bin-win-cuda-cu12.2.0-x64.zip (or latest CUDA version)
echo.
pause
goto :manual_download

:manual_download
echo.
echo [MANUAL DOWNLOAD REQUIRED]
echo.
echo 1. Go to: https://github.com/ggerganov/llama.cpp/releases/latest
echo 2. Download the appropriate .zip file:
echo    - For CPU: llama-*-bin-win-avx2-x64.zip
echo    - For NVIDIA GPU: llama-*-bin-win-cuda-cu*.zip
echo 3. Extract the contents to: %cd%\llama.cpp\
echo.
echo Press any key after you've extracted llama.cpp...
pause

if not exist "llama.cpp" (
    echo ERROR: llama.cpp folder not found. Please extract the downloaded zip here.
    pause
    exit /b 1
)

:skip_install

echo.
echo [2/3] Downloading a test model (Qwen2.5-3B-Instruct - ~2GB)...
echo.

if not exist "llama.cpp\models" (
    mkdir llama.cpp\models
)

if exist "llama.cpp\models\qwen2.5-3b-instruct-q4_k_m.gguf" (
    echo Model already downloaded.
) else (
    echo This will download ~2GB. It may take a few minutes...
    echo Downloading from HuggingFace...
    
    :: Using curl to download from HuggingFace
    curl -L -o llama.cpp\models\qwen2.5-3b-instruct-q4_k_m.gguf ^
        "https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF/resolve/main/qwen2.5-3b-instruct-q4_k_m.gguf"
    
    if errorlevel 1 (
        echo.
        echo Download failed. You can download manually from:
        echo https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF/tree/main
        echo Save as: llama.cpp\models\qwen2.5-3b-instruct-q4_k_m.gguf
        echo.
        pause
    )
)

echo.
echo [3/3] Creating startup script...
echo.

:: Create a start script
(
echo @echo off
echo echo Starting llama.cpp server...
echo echo.
echo echo Server will be available at: http://localhost:8080
echo echo Press Ctrl+C to stop the server
echo echo.
echo.
echo :: Determine which executable to use
echo if exist "build\bin\Release\llama-server.exe" ^(
echo     set SERVER_EXE=build\bin\Release\llama-server.exe
echo ^) else if exist "llama-server.exe" ^(
echo     set SERVER_EXE=llama-server.exe
echo ^) else if exist "server.exe" ^(
echo     set SERVER_EXE=server.exe
echo ^) else ^(
echo     echo ERROR: Could not find llama server executable
echo     pause
echo     exit /b 1
echo ^)
echo.
echo :: Start the server
echo %%SERVER_EXE%% -m models\qwen2.5-3b-instruct-q4_k_m.gguf --host 0.0.0.0 --port 8080 -c 8192 -ngl 32
echo pause
) > llama.cpp\start_server.bat

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Location: %cd%\llama.cpp
echo Model: qwen2.5-3b-instruct-q4_k_m.gguf (~2GB)
echo.
echo To start the server:
echo   1. Go to: cd test_setup\llama.cpp
echo   2. Run: start_server.bat
echo   3. Server will run at: http://localhost:8080
echo.
echo Then in Resume Helper:
echo   - Select provider: llama.cpp
echo   - Base URL: http://localhost:8080/v1
echo   - Leave API key empty
echo   - Click Set
echo.
echo Note: If you have NVIDIA GPU, edit start_server.bat and adjust -ngl value
echo       (higher = more GPU layers = faster, e.g., -ngl 99 for all layers)
echo.
pause
