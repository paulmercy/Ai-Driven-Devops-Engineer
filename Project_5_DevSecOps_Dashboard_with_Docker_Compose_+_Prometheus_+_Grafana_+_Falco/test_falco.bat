@echo off
echo Testing Falco Security Detection...
echo.

REM Check if Docker Compose is available
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker Compose not found. Please install Docker Desktop.
    pause
    exit /b 1
)

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python.
    pause
    exit /b 1
)

REM Run the Falco test script
python test_falco.py

echo.
echo Test completed. Check the output above for results.
echo.
echo To monitor Falco logs in real-time, run:
echo   docker-compose logs -f falco
echo.
pause
