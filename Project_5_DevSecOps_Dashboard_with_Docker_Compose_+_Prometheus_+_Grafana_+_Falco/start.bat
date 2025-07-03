@echo off
REM DevSecOps Dashboard Startup Script for Windows
REM This script starts the complete monitoring and security stack

setlocal enabledelayedexpansion

REM Function to print status messages
:print_status
echo [INFO] %~1
goto :eof

:print_success
echo [SUCCESS] %~1
goto :eof

:print_warning
echo [WARNING] %~1
goto :eof

:print_error
echo [ERROR] %~1
goto :eof

REM Check if Docker is running
:check_docker
docker info >nul 2>&1
if errorlevel 1 (
    call :print_error "Docker is not running. Please start Docker and try again."
    exit /b 1
)
call :print_success "Docker is running"
goto :eof

REM Check if Docker Compose is available
:check_docker_compose
docker-compose --version >nul 2>&1
if errorlevel 1 (
    call :print_error "Docker Compose is not installed. Please install Docker Compose and try again."
    exit /b 1
)
call :print_success "Docker Compose is available"
goto :eof

REM Create necessary directories
:create_directories
call :print_status "Creating necessary directories..."
if not exist "app\logs" mkdir "app\logs"
if not exist "logs\buffer" mkdir "logs\buffer"
if not exist "prometheus\data" mkdir "prometheus\data"
if not exist "grafana\data" mkdir "grafana\data"
call :print_success "Directories created"
goto :eof

REM Pull latest images
:pull_images
call :print_status "Pulling latest Docker images..."
docker-compose pull
if errorlevel 1 (
    call :print_error "Failed to pull images"
    exit /b 1
)
call :print_success "Images pulled successfully"
goto :eof

REM Start the stack
:start_stack
call :print_status "Starting DevSecOps monitoring stack..."

REM Start core services first
docker-compose up -d prometheus grafana app redis node-exporter cadvisor fluentd
if errorlevel 1 (
    call :print_error "Failed to start core services"
    exit /b 1
)

call :print_status "Waiting for core services to initialize..."
timeout /t 30 /nobreak >nul

REM Start Falco
call :print_status "Starting Falco security monitoring..."
docker-compose up -d falco

call :print_success "All services started"
goto :eof

REM Wait for services to be ready
:wait_for_services
call :print_status "Waiting for services to be ready..."

REM Wait for application
call :print_status "Checking application health..."
set /a count=0
:wait_app
set /a count+=1
curl -s http://localhost:3000/health >nul 2>&1
if not errorlevel 1 (
    call :print_success "Application is ready"
    goto :wait_grafana
)
if !count! geq 30 (
    call :print_error "Application failed to start within timeout"
    exit /b 1
)
timeout /t 2 /nobreak >nul
goto :wait_app

:wait_grafana
REM Wait for Grafana
call :print_status "Checking Grafana health..."
set /a count=0
:wait_grafana_loop
set /a count+=1
curl -s http://localhost:3001/api/health >nul 2>&1
if not errorlevel 1 (
    call :print_success "Grafana is ready"
    goto :wait_prometheus
)
if !count! geq 30 (
    call :print_error "Grafana failed to start within timeout"
    exit /b 1
)
timeout /t 2 /nobreak >nul
goto :wait_grafana_loop

:wait_prometheus
REM Wait for Prometheus
call :print_status "Checking Prometheus health..."
set /a count=0
:wait_prometheus_loop
set /a count+=1
curl -s http://localhost:9090/-/healthy >nul 2>&1
if not errorlevel 1 (
    call :print_success "Prometheus is ready"
    goto :eof
)
if !count! geq 30 (
    call :print_error "Prometheus failed to start within timeout"
    exit /b 1
)
timeout /t 2 /nobreak >nul
goto :wait_prometheus_loop

REM Run tests
:run_tests
if exist "test_stack.py" (
    call :print_status "Running stack validation tests..."
    python test_stack.py
    if not errorlevel 1 (
        call :print_success "All tests passed!"
    ) else (
        call :print_warning "Some tests failed. Check the output above for details."
    )
) else (
    call :print_warning "Test script not found. Skipping validation tests."
)
goto :eof

REM Show access information
:show_access_info
echo.
echo 🎉 DevSecOps Dashboard is ready!
echo ==================================
echo.
echo 📱 Access URLs:
echo    • Demo Application:    http://localhost:3000
echo    • Grafana Dashboard:   http://localhost:3001 (admin/admin123)
echo    • Prometheus:          http://localhost:9090
echo    • cAdvisor:            http://localhost:8080
echo    • Node Exporter:       http://localhost:9100
echo.
echo 🚀 Quick Actions:
echo    • Run demo:            python demo.py
echo    • Run tests:           python test_stack.py
echo    • Attack simulation:   docker-compose --profile attack up attack-sim
echo    • View logs:           docker-compose logs -f [service-name]
echo    • Stop stack:          docker-compose down
echo.
echo 📊 Monitoring Features:
echo    • Real-time metrics collection
echo    • Security event monitoring
echo    • Container runtime security (Falco)
echo    • Comprehensive alerting
echo    • Attack simulation capabilities
echo.
goto :eof

REM Show service status
:show_status
call :print_status "Service Status:"
docker-compose ps
goto :eof

REM Main execution
:main
echo 🛡️  DevSecOps Dashboard Startup
echo ================================
echo.

set command=%1
if "%command%"=="" set command=start

if "%command%"=="start" (
    call :check_docker
    if errorlevel 1 exit /b 1
    call :check_docker_compose
    if errorlevel 1 exit /b 1
    call :create_directories
    call :pull_images
    if errorlevel 1 exit /b 1
    call :start_stack
    if errorlevel 1 exit /b 1
    call :wait_for_services
    if errorlevel 1 exit /b 1
    call :show_status
    call :run_tests
    call :show_access_info
) else if "%command%"=="stop" (
    call :print_status "Stopping DevSecOps stack..."
    docker-compose down
    call :print_success "Stack stopped"
) else if "%command%"=="restart" (
    call :print_status "Restarting DevSecOps stack..."
    docker-compose restart
    call :wait_for_services
    call :show_status
    call :print_success "Stack restarted"
) else if "%command%"=="status" (
    call :show_status
) else if "%command%"=="logs" (
    if not "%2"=="" (
        docker-compose logs -f %2
    ) else (
        docker-compose logs -f
    )
) else if "%command%"=="test" (
    call :run_tests
) else if "%command%"=="demo" (
    if exist "demo.py" (
        python demo.py
    ) else (
        call :print_error "Demo script not found"
        exit /b 1
    )
) else if "%command%"=="attack" (
    call :print_status "Starting attack simulation..."
    docker-compose --profile attack up attack-sim
) else if "%command%"=="help" (
    echo Usage: %0 [command]
    echo.
    echo Commands:
    echo   start     Start the complete DevSecOps stack (default)
    echo   stop      Stop all services
    echo   restart   Restart all services
    echo   status    Show service status
    echo   logs      Show logs (optionally for specific service)
    echo   test      Run validation tests
    echo   demo      Run interactive demo
    echo   attack    Run attack simulation
    echo   help      Show this help message
    echo.
    echo Examples:
    echo   %0 start          # Start the stack
    echo   %0 logs app       # Show application logs
    echo   %0 test           # Run tests
    echo   %0 demo           # Run demo
) else (
    call :print_error "Unknown command: %command%"
    echo Use '%0 help' for usage information
    exit /b 1
)

goto :eof

REM Call main function
call :main %*
