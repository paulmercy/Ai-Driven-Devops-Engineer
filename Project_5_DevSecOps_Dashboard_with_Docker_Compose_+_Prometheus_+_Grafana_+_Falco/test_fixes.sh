#!/bin/bash

# Test script for the fixes applied to the DevSecOps stack

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

echo "🧪 Testing DevSecOps Stack Fixes"
echo "================================"
echo ""

# Test 1: Validate docker-compose configuration
print_status "Test 1: Validating docker-compose configuration..."
if docker-compose config > /dev/null 2>&1; then
    print_success "Docker Compose configuration is valid"
else
    print_error "Docker Compose configuration has errors"
    docker-compose config
    exit 1
fi

# Test 2: Check if all required files exist
print_status "Test 2: Checking required files..."
REQUIRED_FILES=(
    "app/main.py"
    "app/requirements.txt"
    "app/Dockerfile"
    "fluentd/fluent.conf"
    "prometheus/prometheus.yml"
    "grafana/provisioning/datasources/prometheus.yml"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        print_success "Found: $file"
    else
        print_error "Missing: $file"
        exit 1
    fi
done

# Test 3: Build the application image
print_status "Test 3: Building application image..."
if docker build -t devsecops-app-test ./app > /dev/null 2>&1; then
    print_success "Application image built successfully"
else
    print_error "Failed to build application image"
    exit 1
fi

# Test 4: Test the application container
print_status "Test 4: Testing application container..."
CONTAINER_ID=$(docker run -d -p 3001:3000 devsecops-app-test)
sleep 10

# Test health endpoint
if curl -f http://localhost:3001/health > /dev/null 2>&1; then
    print_success "Application health endpoint is working"
else
    print_warning "Application health endpoint is not responding"
fi

# Test metrics endpoint
if curl -f http://localhost:3001/metrics > /dev/null 2>&1; then
    print_success "Application metrics endpoint is working"
else
    print_warning "Application metrics endpoint is not responding"
fi

# Cleanup test container
docker stop $CONTAINER_ID > /dev/null 2>&1
docker rm $CONTAINER_ID > /dev/null 2>&1
print_status "Test container cleaned up"

# Test 5: Start core services
print_status "Test 5: Starting core services..."
docker-compose up -d redis app prometheus grafana

print_status "Waiting for services to start..."
sleep 30

# Check service status
print_status "Checking service status..."
docker-compose ps

# Test service endpoints
SERVICES=(
    "localhost:6379"  # Redis
    "localhost:3000"  # App
    "localhost:9090"  # Prometheus
    "localhost:3001"  # Grafana
)

for service in "${SERVICES[@]}"; do
    host=$(echo $service | cut -d: -f1)
    port=$(echo $service | cut -d: -f2)
    
    if nc -z $host $port 2>/dev/null; then
        print_success "$service is responding"
    else
        print_warning "$service is not responding"
    fi
done

# Test 6: Check logs for errors
print_status "Test 6: Checking logs for critical errors..."
if docker-compose logs | grep -i "error\|exception\|failed" | grep -v "INFO\|DEBUG"; then
    print_warning "Found some errors in logs (check above)"
else
    print_success "No critical errors found in logs"
fi

print_status "Test completed. Services are running."
print_status "You can now access:"
echo "  - Application: http://localhost:3000"
echo "  - Prometheus: http://localhost:9090"
echo "  - Grafana: http://localhost:3001 (admin/admin123)"
echo ""
print_status "To stop services: docker-compose down"
print_status "To view logs: docker-compose logs -f"
