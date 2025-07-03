#!/bin/bash

# DevSecOps Dashboard Startup Script
# This script starts the complete monitoring and security stack

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    print_success "Docker is running"
}

# Function to check if Docker Compose is available
check_docker_compose() {
    if ! command -v docker-compose > /dev/null 2>&1; then
        print_error "Docker Compose is not installed. Please install Docker Compose and try again."
        exit 1
    fi
    print_success "Docker Compose is available"
}

# Function to check system requirements
check_requirements() {
    print_status "Checking system requirements..."
    
    # Check available memory (at least 4GB recommended)
    if command -v free > /dev/null 2>&1; then
        MEMORY_GB=$(free -g | awk '/^Mem:/{print $2}')
        if [ "$MEMORY_GB" -lt 4 ]; then
            print_warning "System has less than 4GB RAM. Performance may be affected."
        else
            print_success "Memory check passed (${MEMORY_GB}GB available)"
        fi
    fi
    
    # Check available disk space (at least 10GB recommended)
    DISK_SPACE=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
    if [ "$DISK_SPACE" -lt 10 ]; then
        print_warning "Less than 10GB disk space available. Consider freeing up space."
    else
        print_success "Disk space check passed (${DISK_SPACE}GB available)"
    fi
}

# Function to create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p app/logs
    mkdir -p logs/buffer
    mkdir -p prometheus/data
    mkdir -p grafana/data
    
    # Set proper permissions
    chmod 755 app/logs logs/buffer
    
    print_success "Directories created"
}

# Function to pull latest images
pull_images() {
    print_status "Pulling latest Docker images..."
    docker-compose pull
    print_success "Images pulled successfully"
}

# Function to start the stack
start_stack() {
    print_status "Starting DevSecOps monitoring stack..."

    # Validate docker-compose configuration first
    if ! docker-compose config > /dev/null 2>&1; then
        print_error "Docker Compose configuration is invalid"
        print_status "Running troubleshooting script..."
        if [ -f "troubleshoot.sh" ]; then
            chmod +x troubleshoot.sh
            ./troubleshoot.sh diagnose
        fi
        return 1
    fi

    # Start services step by step for better error handling
    print_status "Starting Redis..."
    if ! docker-compose up -d redis; then
        print_error "Failed to start Redis"
        return 1
    fi

    print_status "Starting application..."
    if ! docker-compose up -d app; then
        print_error "Failed to start application"
        print_status "Checking application logs:"
        docker-compose logs app
        return 1
    fi

    print_status "Starting Prometheus..."
    if ! docker-compose up -d prometheus; then
        print_error "Failed to start Prometheus"
        print_status "Checking Prometheus logs:"
        docker-compose logs prometheus
        return 1
    fi

    print_status "Starting Grafana..."
    if ! docker-compose up -d grafana; then
        print_error "Failed to start Grafana"
        print_status "Checking Grafana logs:"
        docker-compose logs grafana
        return 1
    fi

    print_status "Starting monitoring services..."
    docker-compose up -d node-exporter cadvisor fluentd

    print_status "Waiting for core services to initialize..."
    sleep 30

    # Start Falco (requires special privileges)
    print_status "Starting Falco security monitoring..."
    docker-compose up -d falco

    print_success "All services started"
}

# Function to wait for services to be ready
wait_for_services() {
    print_status "Waiting for services to be ready..."
    
    # Wait for application
    print_status "Checking application health..."
    for i in {1..30}; do
        if curl -s http://localhost:3000/health > /dev/null 2>&1; then
            print_success "Application is ready"
            break
        fi
        if [ $i -eq 30 ]; then
            print_error "Application failed to start within timeout"
            return 1
        fi
        sleep 2
    done
    
    # Wait for Grafana
    print_status "Checking Grafana health..."
    for i in {1..30}; do
        if curl -s http://localhost:3001/api/health > /dev/null 2>&1; then
            print_success "Grafana is ready"
            break
        fi
        if [ $i -eq 30 ]; then
            print_error "Grafana failed to start within timeout"
            return 1
        fi
        sleep 2
    done
    
    # Wait for Prometheus
    print_status "Checking Prometheus health..."
    for i in {1..30}; do
        if curl -s http://localhost:9090/-/healthy > /dev/null 2>&1; then
            print_success "Prometheus is ready"
            break
        fi
        if [ $i -eq 30 ]; then
            print_error "Prometheus failed to start within timeout"
            return 1
        fi
        sleep 2
    done
}

# Function to run tests
run_tests() {
    if [ -f "test_stack.py" ]; then
        print_status "Running stack validation tests..."
        if python3 test_stack.py; then
            print_success "All tests passed!"
        else
            print_warning "Some tests failed. Check the output above for details."
        fi
    else
        print_warning "Test script not found. Skipping validation tests."
    fi
}

# Function to show access information
show_access_info() {
    echo ""
    echo "🎉 DevSecOps Dashboard is ready!"
    echo "=================================="
    echo ""
    echo "📱 Access URLs:"
    echo "   • Demo Application:    http://localhost:3000"
    echo "   • Grafana Dashboard:   http://localhost:3001 (admin/admin123)"
    echo "   • Prometheus:          http://localhost:9090"
    echo "   • cAdvisor:            http://localhost:8080"
    echo "   • Node Exporter:       http://localhost:9100"
    echo ""
    echo "🚀 Quick Actions:"
    echo "   • Run demo:            python3 demo.py"
    echo "   • Run tests:           python3 test_stack.py"
    echo "   • Attack simulation:   docker-compose --profile attack up attack-sim"
    echo "   • View logs:           docker-compose logs -f [service-name]"
    echo "   • Stop stack:          docker-compose down"
    echo ""
    echo "📊 Monitoring Features:"
    echo "   • Real-time metrics collection"
    echo "   • Security event monitoring"
    echo "   • Container runtime security (Falco)"
    echo "   • Comprehensive alerting"
    echo "   • Attack simulation capabilities"
    echo ""
}

# Function to show service status
show_status() {
    print_status "Service Status:"
    docker-compose ps
}

# Main execution
main() {
    echo "🛡️  DevSecOps Dashboard Startup"
    echo "================================"
    echo ""
    
    # Parse command line arguments
    case "${1:-start}" in
        "start")
            check_docker || exit 1
            check_docker_compose || exit 1
            check_requirements
            create_directories
            pull_images || exit 1
            start_stack || {
                print_error "Failed to start the stack. Running troubleshooting..."
                if [ -f "troubleshoot.sh" ]; then
                    chmod +x troubleshoot.sh
                    ./troubleshoot.sh fix
                else
                    print_error "Troubleshooting script not found"
                    print_status "Try running: docker-compose logs"
                fi
                exit 1
            }
            wait_for_services || {
                print_warning "Some services may not be ready. Check status manually."
            }
            show_status
            run_tests
            show_access_info
            ;;
        "stop")
            print_status "Stopping DevSecOps stack..."
            docker-compose down
            print_success "Stack stopped"
            ;;
        "restart")
            print_status "Restarting DevSecOps stack..."
            docker-compose restart
            wait_for_services
            show_status
            print_success "Stack restarted"
            ;;
        "status")
            show_status
            ;;
        "logs")
            if [ -n "$2" ]; then
                docker-compose logs -f "$2"
            else
                docker-compose logs -f
            fi
            ;;
        "test")
            run_tests
            ;;
        "demo")
            if [ -f "demo.py" ]; then
                python3 demo.py
            else
                print_error "Demo script not found"
                exit 1
            fi
            ;;
        "attack")
            print_status "Starting attack simulation..."
            docker-compose --profile attack up attack-sim
            ;;
        "help"|"-h"|"--help")
            echo "Usage: $0 [command]"
            echo ""
            echo "Commands:"
            echo "  start     Start the complete DevSecOps stack (default)"
            echo "  stop      Stop all services"
            echo "  restart   Restart all services"
            echo "  status    Show service status"
            echo "  logs      Show logs (optionally for specific service)"
            echo "  test      Run validation tests"
            echo "  demo      Run interactive demo"
            echo "  attack    Run attack simulation"
            echo "  help      Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0 start          # Start the stack"
            echo "  $0 logs app       # Show application logs"
            echo "  $0 test           # Run tests"
            echo "  $0 demo           # Run demo"
            ;;
        *)
            print_error "Unknown command: $1"
            echo "Use '$0 help' for usage information"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
