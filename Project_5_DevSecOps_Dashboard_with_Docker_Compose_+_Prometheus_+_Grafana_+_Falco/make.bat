@echo off
REM Windows batch wrapper for Makefile commands
REM Usage: make.bat [target]

if "%1"=="" (
    echo 🛡️  DevSecOps Dashboard - Windows Make Wrapper
    echo ===============================================
    echo.
    echo Usage: make.bat [target]
    echo.
    echo Available targets:
    echo   demo          - Full demo presentation
    echo   start         - Start complete stack
    echo   mock          - Start with Mock Falco ^(WSL2 compatible^)
    echo   stop          - Stop all services
    echo   logs-mock     - Show Mock Falco logs
    echo   monitor       - Monitor security events
    echo   health        - Check service health
    echo   help          - Show all available commands
    echo.
    echo Examples:
    echo   make.bat demo
    echo   make.bat mock
    echo   make.bat logs-mock
    echo.
    goto :eof
)

REM Check if make is available
where make >nul 2>&1
if errorlevel 1 (
    echo ERROR: 'make' command not found.
    echo.
    echo Please install one of the following:
    echo 1. Git for Windows ^(includes make^)
    echo 2. Chocolatey: choco install make
    echo 3. WSL2 with Ubuntu
    echo.
    pause
    exit /b 1
)

REM Run the make command
make %*
