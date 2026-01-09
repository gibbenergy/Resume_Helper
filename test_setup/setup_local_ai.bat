@echo off
echo ========================================
echo Local AI Setup for Resume Helper
echo ========================================
echo.
echo This will help you set up local AI models
echo for testing llama.cpp and LM Studio integration.
echo.
echo These files will be installed in the test_setup folder
echo and will NOT be committed to git (gitignored).
echo.
echo ========================================
echo Choose what to install:
echo ========================================
echo.
echo [1] Install llama.cpp (CLI-based, lightweight)
echo [2] Install LM Studio (GUI-based, user-friendly)
echo [3] Install BOTH
echo [4] Exit
echo.

choice /C 1234 /M "Select option"

if errorlevel 4 exit /b 0
if errorlevel 3 goto :install_both
if errorlevel 2 goto :install_lmstudio
if errorlevel 1 goto :install_llamacpp

:install_llamacpp
echo.
echo Starting llama.cpp installation...
call install_llamacpp.bat
goto :done

:install_lmstudio
echo.
echo Starting LM Studio installation...
call install_lmstudio.bat
goto :done

:install_both
echo.
echo Installing both llama.cpp and LM Studio...
echo.
echo Step 1: llama.cpp
echo ==================
call install_llamacpp.bat

echo.
echo Step 2: LM Studio
echo ==================
call install_lmstudio.bat
goto :done

:done
echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo You can now test the Resume Helper with local AI:
echo.
echo Option 1 - llama.cpp:
echo   1. cd test_setup\llama.cpp
echo   2. Run: start_server.bat
echo   3. In Resume Helper: Select "llama.cpp" provider
echo   4. Base URL: http://localhost:8080/v1
echo.
echo Option 2 - LM Studio:
echo   1. Open LM Studio from Start Menu
echo   2. Download a model (Search tab)
echo   3. Start Local Server (Server tab)
echo   4. In Resume Helper: Select "LM Studio" provider
echo   5. Base URL: http://localhost:1234/v1
echo.
echo All files are in: %cd%
echo (This folder is gitignored and won't be uploaded)
echo.
pause
