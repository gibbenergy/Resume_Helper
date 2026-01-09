@echo off
echo ========================================
echo llama.cpp Server DEBUG MODE
echo ========================================
echo.

:: Check CUDA
echo [1/5] Checking CUDA installation...
where nvcc >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ CUDA compiler found
    nvcc --version | findstr "release"
) else (
    echo ⚠ CUDA compiler not found in PATH
)
echo.

:: Check for CUDA DLLs
echo [2/5] Checking CUDA DLLs...
if exist "ggml-cuda.dll" (
    echo ✓ ggml-cuda.dll found
) else (
    echo ✗ ggml-cuda.dll NOT found!
)
echo.

:: Check for model
echo [3/5] Checking model file...
if exist "models\qwen2.5-3b-instruct-q4_k_m.gguf" (
    echo ✓ Model found: models\qwen2.5-3b-instruct-q4_k_m.gguf
) else (
    echo ✗ Model NOT found!
    pause
    exit /b 1
)
echo.

:: Find server executable
echo [4/5] Finding llama-server.exe...
if exist "llama-server.exe" (
    set SERVER_EXE=llama-server.exe
    echo ✓ Found: llama-server.exe
) else if exist "bin\llama-server.exe" (
    set SERVER_EXE=bin\llama-server.exe
    echo ✓ Found: bin\llama-server.exe
) else if exist "build\bin\Release\llama-server.exe" (
    set SERVER_EXE=build\bin\Release\llama-server.exe
    echo ✓ Found: build\bin\Release\llama-server.exe
) else (
    echo ✗ llama-server.exe NOT found!
    pause
    exit /b 1
)
echo.

echo [5/5] Starting server with GPU acceleration...
echo.
echo Command: %SERVER_EXE% -m models\qwen2.5-3b-instruct-q4_k_m.gguf --host 0.0.0.0 --port 8080 -c 16384 -ngl 99 --mlock
echo.
echo ========================================
echo Server Output:
echo ========================================
echo.

:: Start server with verbose output
%SERVER_EXE% -m models\qwen2.5-3b-instruct-q4_k_m.gguf ^
    --host 0.0.0.0 ^
    --port 8080 ^
    -c 16384 ^
    -ngl 99 ^
    --mlock ^
    --verbose

pause
