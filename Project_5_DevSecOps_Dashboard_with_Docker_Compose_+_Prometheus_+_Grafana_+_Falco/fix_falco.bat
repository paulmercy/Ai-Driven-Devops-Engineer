@echo off
echo 🛡️  Falco Fix Tool for WSL2
echo ================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python.
    pause
    exit /b 1
)

REM Check if Docker Compose is available
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker Compose not found. Please install Docker Desktop.
    pause
    exit /b 1
)

echo Diagnosing Falco issues...
echo.

REM Run the Python fix script
python fix_falco.py

echo.
echo Fix attempt completed.
echo.
echo To use Mock Falco specifically, run:
echo   python fix_falco.py --mock
echo.
echo To test Falco after fixing:
echo   python test_falco.py
echo.
pause
