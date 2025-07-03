# Production Deployment Guide

## 🚀 Production-Ready DevSecOps Stack

This guide covers deploying the DevSecOps monitoring stack in a production environment with security, scalability, and reliability considerations.

## 📋 Prerequisites

### System Requirements
- **CPU**: 4+ cores recommended
- **Memory**: 8GB+ RAM
- **Storage**: 50GB+ available space
- **OS**: Linux (Ubuntu 20.04+ recommended)
- **Docker**: 20.10+
- **Docker Compose**: 2.0+

### Network Requirements
- Ports 3000, 3001, 9090, 8080, 9100 available
- Outbound internet access for container images
- Internal network connectivity between services

## 🔧 Production Configuration

### 1. Environment Variables

Create a `.env` file for production settings:

```bash
# Application Settings
NODE_ENV=production
METRICS_ENABLED=true
LOG_LEVEL=info

# Security Settings
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=your_secure_password_here
PROMETHEUS_RETENTION_TIME=720h

# Database Settings (if using external DB)
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Alert Manager Settings
ALERTMANAGER_WEBHOOK_URL=https://your-webhook-url.com/alerts
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK

# TLS/SSL Settings
TLS_CERT_PATH=/etc/ssl/certs/app.crt
TLS_KEY_PATH=/etc/ssl/private/app.key
```

### 2. Security Hardening

#### Container Security
```yaml
# Add to docker-compose.yml for production
security_opt:
  - no-new-privileges:true
read_only: true
tmpfs:
  - /tmp
  - /var/tmp
user: "1000:1000"
```

#### Network Security
```yaml
# Use custom networks with encryption
networks:
  monitoring:
    driver: overlay
    encrypted: true
  app:
    driver: overlay
    encrypted: true
```

### 3. Resource Limits

Add resource constraints to prevent resource exhaustion:

```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 2G
    reservations:
      cpus: '0.5'
      memory: 512M
```

### 4. Persistent Storage

Configure proper volume mounts for data persistence:

```yaml
volumes:
  prometheus_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /opt/monitoring/prometheus
  grafana_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /opt/monitoring/grafana
```

## 🔐 Security Best Practices

### 1. Secrets Management

Use Docker secrets or external secret management:

```yaml
secrets:
  grafana_admin_password:
    external: true
  prometheus_config:
    external: true

services:
  grafana:
    secrets:
      - grafana_admin_password
    environment:
      - GF_SECURITY_ADMIN_PASSWORD_FILE=/run/secrets/grafana_admin_password
```

### 2. TLS/SSL Configuration

Enable HTTPS for all web interfaces:

```yaml
# Nginx reverse proxy configuration
server {
    listen 443 ssl;
    server_name monitoring.yourdomain.com;
    
    ssl_certificate /etc/ssl/certs/monitoring.crt;
    ssl_certificate_key /etc/ssl/private/monitoring.key;
    
    location /grafana/ {
        proxy_pass http://grafana:3000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /prometheus/ {
        proxy_pass http://prometheus:9090/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. Access Control

Implement proper authentication and authorization:

```yaml
# Grafana LDAP/OAuth configuration
environment:
  - GF_AUTH_LDAP_ENABLED=true
  - GF_AUTH_LDAP_CONFIG_FILE=/etc/grafana/ldap.toml
  - GF_AUTH_OAUTH_AUTO_LOGIN=true
```

## 📊 Monitoring and Alerting

### 1. Alert Manager Configuration

Create `alertmanager.yml`:

```yaml
global:
  smtp_smarthost: 'localhost:587'
  smtp_from: 'alerts@yourdomain.com'

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'

receivers:
- name: 'web.hook'
  email_configs:
  - to: 'admin@yourdomain.com'
    subject: 'DevSecOps Alert: {{ .GroupLabels.alertname }}'
    body: |
      {{ range .Alerts }}
      Alert: {{ .Annotations.summary }}
      Description: {{ .Annotations.description }}
      {{ end }}
  
  slack_configs:
  - api_url: 'YOUR_SLACK_WEBHOOK_URL'
    channel: '#alerts'
    title: 'DevSecOps Alert'
    text: '{{ range .Alerts }}{{ .Annotations.summary }}{{ end }}'
```

### 2. Log Aggregation

Configure centralized logging:

```yaml
# Add to services for log forwarding
logging:
  driver: "fluentd"
  options:
    fluentd-address: "localhost:24224"
    tag: "docker.{{.Name}}"
```

## 🔄 Backup and Recovery

### 1. Data Backup Strategy

```bash
#!/bin/bash
# backup.sh - Backup monitoring data

BACKUP_DIR="/backup/monitoring/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# Backup Prometheus data
docker run --rm -v prometheus_data:/data -v $BACKUP_DIR:/backup alpine tar czf /backup/prometheus.tar.gz -C /data .

# Backup Grafana data
docker run --rm -v grafana_data:/data -v $BACKUP_DIR:/backup alpine tar czf /backup/grafana.tar.gz -C /data .

# Backup configurations
cp -r ./prometheus $BACKUP_DIR/
cp -r ./grafana $BACKUP_DIR/
cp -r ./falco $BACKUP_DIR/
```

### 2. Disaster Recovery

```bash
#!/bin/bash
# restore.sh - Restore monitoring data

BACKUP_DIR="/backup/monitoring/$1"

if [ ! -d "$BACKUP_DIR" ]; then
    echo "Backup directory not found: $BACKUP_DIR"
    exit 1
fi

# Stop services
docker-compose down

# Restore data
docker run --rm -v prometheus_data:/data -v $BACKUP_DIR:/backup alpine tar xzf /backup/prometheus.tar.gz -C /data
docker run --rm -v grafana_data:/data -v $BACKUP_DIR:/backup alpine tar xzf /backup/grafana.tar.gz -C /data

# Start services
docker-compose up -d
```

## 🚀 Deployment Steps

### 1. Initial Setup

```bash
# Clone repository
git clone <repository-url>
cd Project_5_DevSecOps_Dashboard

# Create production directories
sudo mkdir -p /opt/monitoring/{prometheus,grafana,logs}
sudo chown -R 1000:1000 /opt/monitoring

# Set up environment
cp .env.example .env
# Edit .env with production values
```

### 2. Deploy Stack

```bash
# Pull latest images
docker-compose pull

# Deploy in production mode
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Verify deployment
docker-compose ps
docker-compose logs
```

### 3. Post-Deployment Verification

```bash
# Run health checks
python3 demo.py --health-check

# Verify metrics collection
curl http://localhost:9090/api/v1/targets

# Check Grafana dashboards
curl -u admin:password http://localhost:3001/api/health
```

## 📈 Performance Tuning

### 1. Prometheus Optimization

```yaml
# prometheus.yml optimizations
global:
  scrape_interval: 30s
  evaluation_interval: 30s
  external_labels:
    monitor: 'production'

# Storage optimization
command:
  - '--storage.tsdb.retention.time=720h'
  - '--storage.tsdb.retention.size=50GB'
  - '--storage.tsdb.wal-compression'
```

### 2. Grafana Performance

```yaml
environment:
  - GF_DATABASE_TYPE=postgres
  - GF_DATABASE_HOST=postgres:5432
  - GF_DATABASE_NAME=grafana
  - GF_DATABASE_USER=grafana
  - GF_DATABASE_PASSWORD=password
  - GF_SESSION_PROVIDER=redis
  - GF_SESSION_PROVIDER_CONFIG=addr=redis:6379,pool_size=100
```

## 🔍 Troubleshooting

### Common Issues

1. **High Memory Usage**
   - Adjust Prometheus retention settings
   - Increase container memory limits
   - Optimize query performance

2. **Missing Metrics**
   - Check service discovery configuration
   - Verify network connectivity
   - Review firewall rules

3. **Alert Fatigue**
   - Tune alert thresholds
   - Implement alert grouping
   - Add alert suppression rules

### Monitoring Commands

```bash
# Check service health
docker-compose ps
docker-compose logs -f [service]

# Monitor resource usage
docker stats

# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Verify Grafana datasources
curl -u admin:password http://localhost:3001/api/datasources
```

## 📞 Support and Maintenance

### Regular Maintenance Tasks

1. **Weekly**
   - Review alert notifications
   - Check disk space usage
   - Verify backup completion

2. **Monthly**
   - Update container images
   - Review security logs
   - Performance optimization

3. **Quarterly**
   - Security audit
   - Capacity planning
   - Disaster recovery testing

### Monitoring Checklist

- [ ] All services are healthy
- [ ] Metrics are being collected
- [ ] Alerts are configured and working
- [ ] Dashboards are displaying data
- [ ] Backups are running successfully
- [ ] Security monitoring is active
- [ ] Log aggregation is working
- [ ] Performance is within acceptable limits
