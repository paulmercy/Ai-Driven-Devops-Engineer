#!/bin/bash

# DevSecOps Dashboard Troubleshooting Script
# This script helps diagnose and fix common issues

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Function to clean up everything
cleanup_all() {
    print_status "Cleaning up all containers and volumes..."
    
    # Stop and remove all containers
    docker-compose down --remove-orphans --volumes 2>/dev/null || true
    
    # Remove any dangling containers
    docker container prune -f 2>/dev/null || true
    
    # Remove any dangling images
    docker image prune -f 2>/dev/null || true
    
    # Remove any dangling volumes
    docker volume prune -f 2>/dev/null || true
    
    print_success "Cleanup completed"
}

# Function to check Docker system
check_docker_system() {
    print_status "Checking Docker system..."
    
    # Check Docker daemon
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker daemon is not running"
        return 1
    fi
    
    # Check available space
    DISK_USAGE=$(docker system df --format "table {{.Type}}\t{{.TotalCount}}\t{{.Size}}\t{{.Reclaimable}}")
    echo "$DISK_USAGE"
    
    # Check for any issues
    docker system events --since 1m --until now 2>/dev/null || true
    
    print_success "Docker system check completed"
}

# Function to validate configuration files
validate_configs() {
    print_status "Validating configuration files..."
    
    # Check if required files exist
    REQUIRED_FILES=(
        "docker-compose.yml"
        "app/Dockerfile"
        "app/main.py"
        "app/requirements.txt"
        "prometheus/prometheus.yml"
        "prometheus/rules/alerts.yml"
        "grafana/provisioning/datasources/prometheus.yml"
        "grafana/dashboards/devsecops-dashboard.json"
        "falco/falco.yaml"
        "falco/rules/custom_rules.yaml"
        "fluentd/fluent.conf"
    )
    
    for file in "${REQUIRED_FILES[@]}"; do
        if [ -f "$file" ]; then
            print_success "Found: $file"
        else
            print_error "Missing: $file"
        fi
    done
    
    # Validate docker-compose.yml syntax
    if docker-compose config > /dev/null 2>&1; then
        print_success "docker-compose.yml syntax is valid"
    else
        print_error "docker-compose.yml has syntax errors"
        docker-compose config
        return 1
    fi
}

# Function to build images individually
build_images() {
    print_status "Building Docker images individually..."
    
    # Build app image
    print_status "Building application image..."
    if docker build -t devsecops-app ./app; then
        print_success "Application image built successfully"
    else
        print_error "Failed to build application image"
        return 1
    fi
    
    # Pull other images
    print_status "Pulling external images..."
    IMAGES=(
        "prom/prometheus:v2.47.0"
        "grafana/grafana:10.1.0"
        "prom/node-exporter:v1.6.1"
        "gcr.io/cadvisor/cadvisor:v0.47.0"
        "falcosecurity/falco-no-driver:0.35.1"
        "fluent/fluentd:v1.16-1"
        "redis:7-alpine"
    )
    
    for image in "${IMAGES[@]}"; do
        print_status "Pulling $image..."
        if docker pull "$image"; then
            print_success "Pulled $image"
        else
            print_warning "Failed to pull $image"
        fi
    done
}

# Function to start services step by step
start_step_by_step() {
    print_status "Starting services step by step..."
    
    # Start basic services first
    print_status "Starting Redis..."
    docker-compose up -d redis
    sleep 5
    
    print_status "Starting application..."
    docker-compose up -d app
    sleep 10
    
    print_status "Starting Prometheus..."
    docker-compose up -d prometheus
    sleep 10
    
    print_status "Starting Grafana..."
    docker-compose up -d grafana
    sleep 10
    
    print_status "Starting monitoring services..."
    docker-compose up -d node-exporter cadvisor
    sleep 5
    
    print_status "Starting log aggregation..."
    docker-compose up -d fluentd
    sleep 5
    
    print_status "Starting Falco (requires privileges)..."
    docker-compose up -d falco
    sleep 5
    
    print_success "All services started"
}

# Function to check service health
check_services() {
    print_status "Checking service health..."
    
    # Show container status
    docker-compose ps
    
    # Check individual services
    SERVICES=(
        "redis-demo:6379"
        "demo-app:3000"
        "prometheus:9090"
        "grafana:3000"
        "node-exporter:9100"
        "cadvisor:8080"
    )
    
    for service in "${SERVICES[@]}"; do
        container=$(echo $service | cut -d: -f1)
        port=$(echo $service | cut -d: -f2)
        
        if docker exec $container nc -z localhost $port 2>/dev/null; then
            print_success "$container is responding on port $port"
        else
            print_warning "$container is not responding on port $port"
            print_status "Checking $container logs:"
            docker logs --tail 10 $container
        fi
    done
}

# Function to show logs
show_logs() {
    print_status "Showing recent logs for all services..."
    docker-compose logs --tail=20
}

# Main troubleshooting function
main() {
    echo "🔧 DevSecOps Dashboard Troubleshooting"
    echo "======================================"
    echo ""
    
    case "${1:-diagnose}" in
        "cleanup")
            cleanup_all
            ;;
        "check")
            check_docker_system
            validate_configs
            ;;
        "build")
            build_images
            ;;
        "start")
            start_step_by_step
            check_services
            ;;
        "logs")
            show_logs
            ;;
        "diagnose")
            print_status "Running full diagnosis..."
            check_docker_system
            validate_configs
            print_status "Checking current service status..."
            docker-compose ps 2>/dev/null || print_warning "No services running"
            ;;
        "fix")
            print_status "Attempting to fix common issues..."
            cleanup_all
            sleep 2
            check_docker_system
            validate_configs
            build_images
            start_step_by_step
            check_services
            ;;
        "help")
            echo "Usage: $0 [command]"
            echo ""
            echo "Commands:"
            echo "  diagnose  Run full diagnosis (default)"
            echo "  cleanup   Clean up all containers and volumes"
            echo "  check     Check Docker system and configs"
            echo "  build     Build images individually"
            echo "  start     Start services step by step"
            echo "  logs      Show recent logs"
            echo "  fix       Attempt to fix all issues"
            echo "  help      Show this help"
            ;;
        *)
            print_error "Unknown command: $1"
            echo "Use '$0 help' for usage information"
            exit 1
            ;;
    esac
}

main "$@"
