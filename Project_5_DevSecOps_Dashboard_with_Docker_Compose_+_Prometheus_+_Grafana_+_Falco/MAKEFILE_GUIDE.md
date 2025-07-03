# 🛡️ DevSecOps Dashboard - Makefile Guide

This comprehensive Makefile provides easy-to-use commands for managing and presenting the DevSecOps Dashboard with Docker Compose + Prometheus + Grafana + Falco.

## 🚀 Quick Start

### For Presentations (Recommended)
```bash
# Full automated demo
make demo

# Quick 2-minute demo
make quick-demo

# Presentation mode with browser opening
make presentation
```

### For Development
```bash
# Start with Mock Falco (WSL2 compatible)
make mock

# Development mode with live logs
make dev

# Monitor security events
make monitor
```

## 📋 Command Categories

### 🎬 Demo & Presentation Commands

| Command | Description |
|---------|-------------|
| `make demo` | Full presentation demo with all features |
| `make quick-demo` | Quick 2-minute demo |
| `make presentation` | Presentation mode - optimized for demos |
| `make demo-script` | Show demo script commands |

### 🚀 Stack Management

| Command | Description |
|---------|-------------|
| `make start` | Start complete DevSecOps stack |
| `make start-mock` | Start stack with Mock Falco (WSL2 compatible) |
| `make mock` | Alias for start-mock |
| `make start-minimal` | Start minimal stack (Prometheus + Grafana only) |
| `make stop` | Stop all services |
| `make restart` | Restart complete stack |
| `make restart-mock` | Restart with Mock Falco |
| `make build` | Build all custom containers |
| `make clean` | Clean up containers and volumes |
| `make reset` | Complete reset and restart with Mock Falco |

### 📋 Logging & Monitoring

| Command | Description |
|---------|-------------|
| `make logs` | Show logs from all services |
| `make logs-falco` | Show Falco security logs |
| `make logs-mock` | Show Mock Falco security logs |
| `make logs-follow` | Follow logs in real-time |
| `make logs-follow-mock` | Follow Mock Falco logs in real-time |
| `make logs-all` | Show logs from all running stacks |
| `make logs-security` | Show only security-related logs |
| `make monitor` | Monitor security events in real-time |
| `make export-logs` | Export all logs to files |

### 🧪 Testing & Validation

| Command | Description |
|---------|-------------|
| `make test-security` | Run security tests |
| `make test-stack` | Test complete stack functionality |
| `make simulate-attacks` | Simulate security attacks |
| `make generate-traffic` | Generate test traffic and security events |
| `make stress-test` | Run stress test on the application |
| `make validate-compose` | Validate all Docker Compose files |

### 🔧 Maintenance & Troubleshooting

| Command | Description |
|---------|-------------|
| `make status` | Show status of all services |
| `make health` | Check health of all services |
| `make fix-falco` | Fix Falco issues (auto-detect WSL2) |
| `make force-mock` | Force switch to Mock Falco |
| `make troubleshoot` | Run troubleshooting diagnostics |
| `make update-images` | Update all Docker images |
| `make security-scan` | Run security scan on containers |

### 🌐 Access & Navigation

| Command | Description |
|---------|-------------|
| `make show-urls` | Show all service URLs |
| `make open-dashboards` | Open all dashboards in browser |
| `make ports` | Show all exposed ports |

### 🐚 Interactive Commands

| Command | Description |
|---------|-------------|
| `make shell-app` | Open shell in demo app container |
| `make shell-falco` | Open shell in Falco container |

### 💾 Backup & Utilities

| Command | Description |
|---------|-------------|
| `make backup` | Backup Grafana dashboards and Prometheus data |
| `make install-deps` | Install Python dependencies for testing |

## 🎯 Common Usage Scenarios

### 1. **First Time Setup**
```bash
# Install dependencies and start
make install-deps
make build
make mock
```

### 2. **Quick Demo for Stakeholders**
```bash
# One command for full demo
make demo
```

### 3. **Development Workflow**
```bash
# Start development environment
make dev

# In another terminal, run tests
make test-security

# Generate some traffic
make generate-traffic
```

### 4. **Troubleshooting Issues**
```bash
# Check system health
make health

# Run diagnostics
make troubleshoot

# Check logs
make logs-mock

# Fix Falco if needed
make fix-falco
```

### 5. **Presentation Setup**
```bash
# Complete presentation setup
make presentation

# Or step by step
make clean
make build
make start-mock
make open-dashboards
make test-security
```

## 🌐 Service Access Points

After running `make start-mock` or `make demo`, access:

- **📊 Grafana Dashboard**: http://localhost:3000 (admin/admin)
- **🔍 Prometheus**: http://localhost:9090
- **🚀 Demo App**: http://localhost:8000
- **📱 UI Dashboard**: http://localhost:8080
- **📋 App Logs**: http://localhost:8000/logs
- **🛡️ Security Events**: http://localhost:8000/security

## 🔧 Windows Users

Use the provided batch wrapper:
```cmd
# Show help
make.bat

# Run demo
make.bat demo

# Start mock Falco
make.bat mock
```

## 🛡️ Mock Falco Features

The Mock Falco service provides:
- ✅ **Real-time security monitoring** of Docker containers
- 🚨 **Realistic security alerts** in Falco format
- 📊 **Compatible logging** with Grafana dashboards
- 🔍 **Pattern detection** for:
  - System information gathering
  - Sensitive file access
  - Network activity
  - Package management
  - Privilege escalation attempts
  - Container escape attempts

## 📝 Tips for Presentations

1. **Pre-demo setup**: Run `make presentation` 5 minutes before presenting
2. **Live monitoring**: Use `make monitor` in a separate terminal during demo
3. **Generate activity**: Use `make generate-traffic` and `make simulate-attacks`
4. **Show logs**: Use `make logs-mock` to display security events
5. **Health checks**: Use `make health` to verify all services

## 🔍 Troubleshooting

If you encounter issues:

1. **Check service status**: `make status`
2. **Run health checks**: `make health`
3. **View logs**: `make logs-mock`
4. **Fix Falco**: `make fix-falco`
5. **Complete reset**: `make reset`
6. **Run diagnostics**: `make troubleshoot`

## 🎨 Color-Coded Output

The Makefile uses color-coded output for better readability:
- 🔴 **Red**: Errors, stopping services
- 🟢 **Green**: Success, starting services
- 🟡 **Yellow**: Warnings, in-progress actions
- 🔵 **Blue**: Information, building
- 🟣 **Magenta**: Demo/presentation mode
- 🔵 **Cyan**: Logs, monitoring

## 📚 Additional Resources

- **Main README**: `README.md`
- **Presentation Guide**: `PRESENTATION_GUIDE.md`
- **Production Guide**: `PRODUCTION_GUIDE.md`
- **Falco Fix Tool**: `fix_falco.py`
- **Security Tests**: `test_falco.py`
