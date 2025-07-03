# DevSecOps Dashboard with Docker Compose + Prometheus + Grafana + Falco

This project demonstrates a comprehensive DevSecOps monitoring stack with security monitoring, metrics collection, and visualization.

## 🏗️ Architecture

- **FastAPI Microservice** - Demo application with Prometheus metrics
- **Prometheus** - Metrics collection and alerting
- **Grafana** - Visualization and dashboards
- **Falco** - Runtime security monitoring
- **Node Exporter** - System metrics
- **cAdvisor** - Container metrics
- **Attack Simulator** - Security testing tool

## 🚀 Quick Start

### Start the complete stack:
```bash
docker-compose up -d
```

### Start with attack simulation:
```bash
docker-compose --profile attack up -d
```

## 📊 Access Points

- **Demo Application**: http://localhost:3000
- **Grafana Dashboard**: http://localhost:3001 (admin/admin123)
- **Prometheus**: http://localhost:9090
- **cAdvisor**: http://localhost:8080
- **Node Exporter**: http://localhost:9100

## 🔍 Monitoring Features

### Application Metrics
- HTTP request rates and response times
- Error rates and status codes
- Active connections
- CPU and memory usage
- Custom business metrics

### Security Monitoring
- Suspicious activity detection
- Container runtime security
- File access monitoring
- Network activity tracking
- Privilege escalation attempts

### Infrastructure Metrics
- System resource usage
- Container performance
- Network statistics
- Disk I/O metrics

## 🛡️ Security Features

### Falco Rules
- Container drift detection
- Privilege escalation monitoring
- Sensitive file access alerts
- Unexpected shell spawning
- Package management tracking

### Attack Simulation
The attack simulator demonstrates:
- SQL injection attempts
- Privilege escalation
- Unauthorized file access
- Network reconnaissance
- Container escape attempts

## 📈 Grafana Dashboards

Pre-configured dashboards include:
- Application performance metrics
- Security event monitoring
- Infrastructure overview
- Container resource usage

## 🔧 Configuration

### Prometheus Configuration
- Scrapes metrics from all services
- Custom alerting rules
- Service discovery

### Grafana Setup
- Auto-provisioned datasources
- Pre-built dashboards
- Alert notifications

### Falco Rules
- Custom security rules
- Real-time threat detection
- JSON output for integration

## 🎯 Demo Scenarios

### 1. Normal Operations
```bash
# Generate normal traffic
curl http://localhost:3000/api/data
curl http://localhost:3000/health
```

### 2. Trigger Security Alerts
```bash
# Simulate attacks via API
curl -X POST http://localhost:3000/simulate/attack \
  -H "Content-Type: application/json" \
  -d '{"type": "sql_injection"}'
```

### 3. Run Attack Simulation
```bash
# Start attack simulator
docker-compose --profile attack up attack-sim
```

### 4. Monitor in Grafana
1. Open http://localhost:3001
2. Login with admin/admin123
3. View the DevSecOps Dashboard
4. Observe metrics and security events

## 📋 Monitoring Checklist

- [ ] Application metrics are being collected
- [ ] Grafana dashboard shows live data
- [ ] Falco is detecting security events
- [ ] Prometheus alerts are configured
- [ ] Attack simulation triggers alerts
- [ ] All containers are healthy

## 🔍 Troubleshooting

### Check service status:
```bash
docker-compose ps
```

### View logs:
```bash
docker-compose logs -f [service-name]
```

### Restart services:
```bash
docker-compose restart [service-name]
```

## 🧪 Testing Security Monitoring

### Quick Demo
```bash
# Start the complete stack
docker-compose up -d

# Wait for services to initialize (2-3 minutes)
docker-compose ps

# Run the interactive demo
python3 demo.py

# Or run attack simulation manually
docker-compose --profile attack up attack-sim
```

### Manual Testing Steps
1. **Start the stack**: `docker-compose up -d`
2. **Wait for services**: Allow 2-3 minutes for initialization
3. **Access Grafana**: http://localhost:3001 (admin/admin123)
4. **Run demo script**: `python3 demo.py`
5. **Observe alerts**: Check Grafana dashboard and Falco logs
6. **Review metrics**: Verify security events are captured

### Verification Checklist
- [ ] All containers are running: `docker-compose ps`
- [ ] Application is accessible: `curl http://localhost:3000/health`
- [ ] Grafana shows data: Check dashboard panels
- [ ] Prometheus has targets: http://localhost:9090/targets
- [ ] Falco is detecting events: `docker-compose logs falco`
- [ ] Alerts are configured: http://localhost:9090/alerts

## 📊 Key Metrics to Monitor

### Application Metrics
- `http_requests_total` - Total HTTP requests by method, endpoint, status
- `http_request_duration_seconds` - Request latency histogram
- `active_connections` - Current active connections
- `cpu_usage_percent` - Application CPU utilization
- `memory_usage_bytes` - Application memory consumption

### Security Metrics
- `suspicious_activity_total` - Security events by type
- `failed_login_attempts` - Authentication failures
- `admin_access_attempts` - Administrative endpoint access
- `container_drift_events` - Unexpected container changes

### Infrastructure Metrics
- `container_cpu_usage_seconds_total` - Container CPU usage
- `container_memory_usage_bytes` - Container memory usage
- `node_cpu_seconds_total` - Host CPU metrics
- `node_memory_MemAvailable_bytes` - Host memory availability

## 🔐 Security Features Demonstrated

### Runtime Security Monitoring
- **Falco Rules**: Custom security rules for threat detection
- **Container Drift**: Detection of unauthorized changes
- **Privilege Escalation**: Monitoring for privilege abuse
- **File Access**: Sensitive file access monitoring
- **Network Activity**: Suspicious network connections

### Application Security
- **Attack Simulation**: SQL injection, privilege escalation
- **Authentication Monitoring**: Failed login tracking
- **Admin Access Control**: Administrative endpoint monitoring
- **Input Validation**: Security event logging

### Infrastructure Security
- **Container Security**: Runtime container monitoring
- **Network Monitoring**: Inter-service communication tracking
- **Resource Monitoring**: Anomaly detection via metrics
- **Log Aggregation**: Centralized security event collection

## 🚀 Production Deployment

For production deployment, see [PRODUCTION_GUIDE.md](PRODUCTION_GUIDE.md) which covers:

- Security hardening
- TLS/SSL configuration
- Secrets management
- High availability setup
- Backup and recovery
- Performance tuning
- Monitoring best practices

## 🎯 Demo Scenarios Explained

### Normal Operations Demo
```bash
# Generate normal traffic
for i in {1..10}; do
  curl http://localhost:3000/api/data
  curl http://localhost:3000/health
  sleep 1
done
```

### Security Attack Simulation
```bash
# SQL Injection
curl -X POST http://localhost:3000/simulate/attack \
  -H "Content-Type: application/json" \
  -d '{"type": "sql_injection"}'

# Privilege Escalation
curl -X POST http://localhost:3000/simulate/attack \
  -H "Content-Type: application/json" \
  -d '{"type": "privilege_escalation"}'
```

### Load Testing
```bash
# Generate high load
for i in {1..50}; do
  curl http://localhost:3000/api/stress &
done
wait
```
