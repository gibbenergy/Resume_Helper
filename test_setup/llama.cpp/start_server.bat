@echo off
echo ========================================
echo llama.cpp Server (RTX 5090 Optimized)
echo ========================================
echo.
echo Server URL: http://localhost:8080
echo API Endpoint: http://localhost:8080/v1
echo.
echo Press Ctrl+C to stop the server
echo.

:: Find server executable
if exist "build\bin\Release\llama-server.exe" (
    set SERVER_EXE=build\bin\Release\llama-server.exe
) else if exist "bin\llama-server.exe" (
    set SERVER_EXE=bin\llama-server.exe
) else if exist "llama-server.exe" (
    set SERVER_EXE=llama-server.exe
) else if exist "server.exe" (
    set SERVER_EXE=server.exe
) else (
    echo ERROR: Could not find llama-server.exe
    echo Please check your installation
    pause
    exit /b 1
)

echo Starting server with RTX 5090 settings:
echo   - Model: Qwen2.5-3B-Instruct
echo   - GPU Layers: ALL (-ngl 99)
echo   - Context: 16K tokens
echo   - Port: 8080
echo.

:: RTX 5090 Optimized Parameters
%SERVER_EXE% -m models\qwen2.5-3b-instruct-q4_k_m.gguf ^
    --host 0.0.0.0 ^
    --port 8080 ^
    -c 16384 ^
    -ngl 99 ^
    --mlock

pause
