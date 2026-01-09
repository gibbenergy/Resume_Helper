@echo off
echo ========================================
echo LM Studio Setup for Windows
echo ========================================
echo.

:: Check if already installed
if exist "LMStudio" (
    echo LM Studio appears to be already downloaded.
    choice /C YN /M "Do you want to reinstall"
    if errorlevel 2 goto :skip_install
    echo Removing old installation...
    rmdir /s /q LMStudio
)

echo.
echo [1/3] Downloading LM Studio...
echo.

:: LM Studio installer URL
set LM_STUDIO_URL=https://releases.lmstudio.ai/windows/x64/latest

echo Downloading LM Studio installer...
echo This may take a few minutes (installer is ~500MB)...
echo.

:: Check if curl is available
where curl >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: curl not found.
    goto :manual_download_lmstudio
)

:: Download LM Studio
mkdir LMStudio 2>nul
cd LMStudio

echo Downloading from: %LM_STUDIO_URL%
curl -L -o LM-Studio-Setup.exe "%LM_STUDIO_URL%"

if errorlevel 1 (
    echo.
    echo Download failed.
    goto :manual_download_lmstudio
)

echo.
echo Download complete!
echo.

:install_lmstudio
echo [2/3] Installing LM Studio...
echo.
echo The installer will now launch. Please:
echo   1. Follow the installation wizard
echo   2. Choose installation location (default is fine)
echo   3. Complete the installation
echo   4. DO NOT start LM Studio yet
echo.
pause

:: Launch installer
start /wait LM-Studio-Setup.exe

cd ..
goto :download_model

:manual_download_lmstudio
echo.
echo [MANUAL DOWNLOAD REQUIRED]
echo.
echo 1. Go to: https://lmstudio.ai/
echo 2. Click "Download for Windows"
echo 3. Run the installer
echo 4. Come back here after installation
echo.
pause

:skip_install

:download_model
echo.
echo [3/3] Setting up test model...
echo.
echo LM Studio is now installed!
echo.
echo ========================================
echo Next Steps:
echo ========================================
echo.
echo 1. Launch LM Studio from Start Menu or Desktop
echo.
echo 2. Download a model:
echo    - Click the "Search" icon (magnifying glass) in LM Studio
echo    - Search for: "Qwen2.5-3B-Instruct-GGUF"
echo    - Click on "Qwen/Qwen2.5-3B-Instruct-GGUF"
echo    - Download: "qwen2.5-3b-instruct-q4_k_m.gguf" (~2GB)
echo.
echo    Alternative smaller models (if 3B is too large):
echo    - "Qwen/Qwen2.5-1.5B-Instruct-GGUF" (~1GB)
echo    - "microsoft/Phi-3-mini-4k-instruct-gguf" (~2GB)
echo.
echo 3. Start the Local Server:
echo    - Click "Local Server" in the left sidebar
echo    - Select your downloaded model from dropdown
echo    - Click "Start Server"
echo    - Default URL: http://localhost:1234
echo.
echo 4. In Resume Helper:
echo    - Select provider: LM Studio
echo    - Base URL: http://localhost:1234/v1
echo    - Leave API key empty
echo    - Click Set
echo.
echo ========================================
echo Tips:
echo ========================================
echo.
echo - Keep LM Studio running while using Resume Helper
echo - You can monitor requests in LM Studio's Server tab
echo - To use GPU acceleration, ensure CUDA is installed
echo - Check LM Studio settings for GPU/CPU allocation
echo.
echo ========================================
echo Quick Start Guide Created!
echo ========================================
echo.

:: Create a quick reference file
(
echo LM Studio Quick Start
echo =====================
echo.
echo Server URL: http://localhost:1234
echo.
echo In Resume Helper:
echo   Provider: LM Studio
echo   Base URL: http://localhost:1234/v1
echo   API Key: ^(leave empty^)
echo.
echo Recommended Models ^(download via LM Studio^):
echo   - Qwen2.5-3B-Instruct-GGUF ^(~2GB, good quality^)
echo   - Qwen2.5-1.5B-Instruct-GGUF ^(~1GB, faster^)
echo   - Phi-3-mini-4k-instruct-gguf ^(~2GB, Microsoft^)
echo   - Llama-3.2-3B-Instruct-GGUF ^(~2GB, Meta^)
echo.
echo To Start Server:
echo   1. Open LM Studio
echo   2. Click "Local Server" ^(left sidebar^)
echo   3. Select model
echo   4. Click "Start Server"
echo.
) > LMStudio\QUICK_START.txt

echo Quick start guide saved to: LMStudio\QUICK_START.txt
echo.
pause
