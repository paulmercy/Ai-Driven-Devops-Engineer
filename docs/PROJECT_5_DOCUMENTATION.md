# Project 5: DevSecOps Dashboard Documentation

## 📋 Overview

A comprehensive security monitoring and observability stack demonstrating runtime security monitoring, metrics collection, and threat detection. Showcases enterprise-grade DevSecOps practices with Docker orchestration.

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │    │   Prometheus    │    │    Grafana      │
│                 │───►│                 │───►│                 │
│ Metrics Export  │    │ Metrics Store   │    │ Visualization   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Falco       │    │  Node Exporter  │    │    cAdvisor     │
│                 │    │                 │    │                 │
│ Security Events │    │ System Metrics  │    │Container Metrics│
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │
         ▼
┌─────────────────┐
│ Attack Simulator│
│                 │
│ Security Testing│
└─────────────────┘
```

## 🛠️ Technology Stack

- **Application**: FastAPI 0.104.1, Python 3.11
- **Monitoring**: Prometheus 2.47.0, Grafana 10.1.0
- **Security**: Falco 0.35.1, Custom rules
- **Metrics**: Node Exporter 1.6.1, cAdvisor 0.47.0
- **Orchestration**: Docker Compose 3.8
- **Logging**: Fluentd 1.16, JSON structured logs
- **Testing**: Custom attack simulation tools

## 📁 Code Structure

```
Project 5/
├── docker-compose.yml         # Service orchestration
├── app/
│   ├── main.py               # FastAPI microservice
│   ├── requirements.txt      # Python dependencies
│   └── Dockerfile           # Application container
├── prometheus/
│   ├── prometheus.yml       # Prometheus configuration
│   └── rules/
│       └── alerts.yml       # Alerting rules
├── grafana/
│   ├── provisioning/        # Auto-configuration
│   │   ├── datasources/     # Data source setup
│   │   └── dashboards/      # Dashboard provisioning
│   └── dashboards/
│       └── devsecops-dashboard.json  # Main dashboard
├── falco/
│   ├── falco.yaml          # Falco configuration
│   └── rules/
│       └── custom_rules.yaml  # Security rules
├── attack-sim/
│   ├── simulate_attacks.py  # Attack simulation
│   └── Dockerfile          # Simulator container
└── README.md               # Project documentation
```

### Key Components

#### 1. FastAPI Microservice (`app/main.py`)
- **Purpose**: Demo application with comprehensive metrics
- **Features**:
  - Prometheus metrics export
  - Security event simulation
  - System resource monitoring
  - API endpoints for testing

#### 2. Prometheus Configuration (`prometheus/`)
- **Purpose**: Metrics collection and alerting
- **Features**:
  - Multi-target scraping
  - Custom alerting rules
  - Service discovery

#### 3. Grafana Dashboards (`grafana/`)
- **Purpose**: Visualization and monitoring
- **Features**:
  - Pre-configured dashboards
  - Real-time metrics display
  - Alert visualization

#### 4. Falco Security (`falco/`)
- **Purpose**: Runtime security monitoring
- **Features**:
  - Container behavior monitoring
  - Custom security rules
  - Real-time threat detection

## 🚀 Setup Instructions

### Prerequisites
```bash
# Required software
- Docker 20.10+
- Docker Compose 2.0+
- 8GB RAM minimum
- 20GB disk space

# Verify installations
docker --version
docker compose version
```

### Quick Start

1. **Navigate to Project Directory**
```bash
cd "Project 5 DevSecOps Dashboard with Docker Compose + Prometheus + Grafana + Falco"
```

2. **Start Core Services**
```bash
docker compose up -d
```

3. **Wait for Initialization**
```bash
# Services need 2-3 minutes to fully initialize
docker compose ps  # Check service status
```

4. **Access Dashboards**
- Grafana: http://localhost:3001 (admin/admin123)
- Prometheus: http://localhost:9090
- Demo App: http://localhost:3000

### Advanced Setup

#### Start with Attack Simulation
```bash
docker compose --profile attack up -d
```

#### View Service Logs
```bash
docker compose logs -f [service-name]
```

#### Scale Services
```bash
docker compose up -d --scale app=3
```

## 📊 Monitoring Stack

### Service Endpoints

| Service | Port | Purpose | URL |
|---------|------|---------|-----|
| Demo App | 3000 | Application metrics | http://localhost:3000 |
| Grafana | 3001 | Visualization | http://localhost:3001 |
| Prometheus | 9090 | Metrics storage | http://localhost:9090 |
| cAdvisor | 8080 | Container metrics | http://localhost:8080 |
| Node Exporter | 9100 | System metrics | http://localhost:9100 |

### Prometheus Metrics

#### Application Metrics
```python
# Custom metrics in FastAPI app
REQUEST_COUNT = Counter('http_requests_total', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds')
SUSPICIOUS_ACTIVITY = Counter('suspicious_activity_total', ['type'])
CPU_USAGE = Gauge('cpu_usage_percent')
MEMORY_USAGE = Gauge('memory_usage_bytes')
```

#### System Metrics
- CPU utilization per core
- Memory usage and availability
- Disk I/O statistics
- Network traffic metrics
- Container resource usage

### Grafana Dashboards

#### DevSecOps Dashboard Features
- **HTTP Request Metrics**: Rate, latency, error rate
- **Security Events**: Suspicious activity tracking
- **System Resources**: CPU, memory, disk usage
- **Container Metrics**: Resource consumption per container
- **Alert Status**: Current alert states

## 🛡️ Security Monitoring

### Falco Rules

#### Container Security
```yaml
- rule: Suspicious Network Activity
  desc: Detect suspicious network connections
  condition: >
    spawned_process and
    (proc.name in (curl, wget, nc, ncat, netcat))
  output: >
    Suspicious network activity detected
  priority: WARNING
```

#### Privilege Escalation
```yaml
- rule: Privilege Escalation Attempt
  desc: Detect potential privilege escalation
  condition: >
    spawned_process and
    (proc.name in (sudo, su, passwd))
  priority: CRITICAL
```

#### File Access Monitoring
```yaml
- rule: Sensitive File Access
  desc: Detect access to sensitive files
  condition: >
    open_read and
    (fd.name startswith /etc/passwd or
     fd.name startswith /etc/shadow)
  priority: CRITICAL
```

### Security Event Types

1. **Container Drift**: New executables in containers
2. **Privilege Escalation**: Attempts to gain elevated privileges
3. **Sensitive File Access**: Access to critical system files
4. **Network Reconnaissance**: Port scanning and network probing
5. **Package Installation**: Runtime package management

## 🧪 Testing Guide

### 1. Basic Functionality Test
```bash
# Check all services are running
docker compose ps

# Test application endpoint
curl http://localhost:3000/health

# Check Prometheus targets
curl http://localhost:9090/api/v1/targets
```

### 2. Security Event Testing
```bash
# Trigger security events via API
curl -X POST http://localhost:3000/simulate/attack \
  -H "Content-Type: application/json" \
  -d '{"type": "sql_injection"}'

curl -X POST http://localhost:3000/simulate/attack \
  -H "Content-Type: application/json" \
  -d '{"type": "privilege_escalation"}'
```

### 3. Attack Simulation
```bash
# Run comprehensive attack simulation
docker compose --profile attack up attack-sim

# Monitor Falco logs
docker compose logs -f falco

# Check Grafana for security events
# Navigate to http://localhost:3001
```

### 4. Load Testing
```bash
# Generate application load
for i in {1..100}; do
  curl http://localhost:3000/api/data &
done
```

## 📈 Performance Metrics

### Expected Benchmarks

#### Application Performance
- **API Response Time**: < 200ms (95th percentile)
- **Throughput**: > 1000 requests/second
- **Memory Usage**: < 200MB per container
- **CPU Usage**: < 50% under normal load

#### Monitoring Performance
- **Metrics Collection**: 5-second intervals
- **Dashboard Load Time**: < 3 seconds
- **Alert Response Time**: < 1 minute
- **Log Processing**: < 100ms latency

### Key Performance Indicators

```promql
# Request rate
rate(http_requests_total[5m])

# Error rate
rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])

# Response time percentiles
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Security events rate
rate(suspicious_activity_total[5m])
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Services Not Starting
```bash
# Check Docker resources
docker system df
docker system prune  # Clean up if needed

# Check service logs
docker compose logs [service-name]
```

#### 2. Grafana Dashboard Issues
```bash
# Reset Grafana data
docker compose down
docker volume rm project5_grafana_data
docker compose up -d grafana
```

#### 3. Falco Not Detecting Events
```bash
# Check Falco configuration
docker compose exec falco cat /etc/falco/falco.yaml

# Verify rule loading
docker compose logs falco | grep "Loading rules"
```

#### 4. Prometheus Scraping Issues
```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Verify service discovery
docker compose exec prometheus cat /etc/prometheus/prometheus.yml
```

## 🎯 Demo Scenarios

### 1. Normal Operations Demo
```bash
# Show healthy system
docker compose ps
curl http://localhost:3000/health
# Navigate to Grafana dashboard
```

### 2. Security Event Demo
```bash
# Trigger various attacks
curl -X POST http://localhost:3000/simulate/attack \
  -d '{"type": "sql_injection"}'
# Show alerts in Grafana
```

### 3. Attack Simulation Demo
```bash
# Run full attack simulation
docker compose --profile attack up attack-sim
# Monitor real-time in Grafana
# Show Falco alerts
```

### 4. Performance Monitoring Demo
```bash
# Generate load
./load_test.sh
# Show metrics in Grafana
# Demonstrate alerting
```

## 📈 Key Technical Achievements

1. **Comprehensive Monitoring**: Full observability stack
2. **Runtime Security**: Real-time threat detection with Falco
3. **Container Orchestration**: Multi-service Docker Compose setup
4. **Security Testing**: Automated attack simulation
5. **Production Ready**: Scalable, configurable, maintainable
6. **DevSecOps Integration**: Security built into the development lifecycle
