# Troubleshooting Guide

## 🔧 General Issues

### System Requirements
- **RAM**: Minimum 8GB (16GB recommended for Project 5)
- **Disk Space**: 20GB free space
- **CPU**: Multi-core processor recommended
- **OS**: Windows 10/11, macOS, or Linux

### Common Environment Issues

#### Python Environment
```bash
# Check Python version
python --version  # Should be 3.11+

# Virtual environment issues
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Package conflicts
pip install --upgrade pip
pip install --force-reinstall -r requirements.txt
```

#### Node.js Environment
```bash
# Check Node version
node --version  # Should be 18+

# Clear npm cache
npm cache clean --force

# Reset node_modules
rm -rf node_modules package-lock.json
npm install
```

#### Docker Environment
```bash
# Check Docker status
docker --version
docker compose version

# Docker daemon issues
# Windows: Restart Docker Desktop
# Linux: sudo systemctl restart docker

# Clean Docker resources
docker system prune -a
docker volume prune
```

## 🚀 Project 2 Troubleshooting

### C++ Compilation Issues

#### Windows - Visual Studio Build Tools
```bash
# Error: Microsoft Visual C++ 14.0 is required
# Solution: Install Visual Studio Build Tools 2019 or later
# Download from: https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2019

# Verify installation
cl.exe  # Should show MSVC compiler version
```

#### Pybind11 Compilation Errors
```bash
# Error: pybind11/pybind11.h: No such file or directory
pip install pybind11[global]
python setup.py build_ext --inplace

# Error: Python.h not found
# Windows: Ensure Python development headers are installed
# Linux: sudo apt-get install python3-dev
```

#### Module Import Issues
```bash
# Error: ImportError: No module named 'text_analyzer'
# Solution: Rebuild the module
python setup.py clean --all
python setup.py build_ext --inplace

# Check if module was created
ls *.pyd  # Windows
ls *.so   # Linux/macOS
```

### FastAPI Issues

#### Port Already in Use
```bash
# Error: [Errno 10048] Only one usage of each socket address
# Solution: Kill existing process
netstat -ano | findstr :8000  # Windows
lsof -ti:8000 | xargs kill    # macOS/Linux

# Or use different port
uvicorn main:app --port 8001
```

#### Database Lock Issues
```bash
# Error: database is locked
# Solution: Close all connections and reset
rm analyzer.db
python main.py  # Will recreate database
```

### OpenAI API Issues
```bash
# Error: Invalid API key
# Solution: Check .env file
cat .env  # Verify OPENAI_API_KEY is set

# Error: Rate limit exceeded
# Solution: Implement retry logic or use mock responses
# The app includes fallback for API failures
```

## 🔄 Project 3 Troubleshooting

### Dependency Issues

#### React 19 Compatibility
```bash
# Error: peer dependency warnings
# Solution: Use legacy peer deps
npm install --legacy-peer-deps

# Alternative: Use exact versions
npm install react@19.1.0 react-dom@19.1.0 --exact
```

#### TypeScript Compilation Errors
```bash
# Error: Cannot find module or its type declarations
# Solution: Install missing types
npm install @types/node --save-dev

# Check TypeScript configuration
npx tsc --noEmit  # Type check without compilation
```

#### Testing Issues
```bash
# Error: Tests not running
# Solution: Check test configuration
npm run test -- --reporter=verbose

# Error: jsdom not found
npm install jsdom --save-dev

# Error: React Testing Library issues
npm install @testing-library/react@latest --save-dev
```

### Build Issues

#### Vite Build Failures
```bash
# Error: Build failed with errors
# Solution: Check for TypeScript errors
npm run build -- --mode development

# Clear Vite cache
rm -rf node_modules/.vite
npm run build
```

#### GitHub Actions Failures
```yaml
# Common issues in CI/CD pipeline:

# 1. Node version mismatch
# Solution: Ensure workflow uses Node 18+
- uses: actions/setup-node@v4
  with:
    node-version: '18'

# 2. Cache issues
# Solution: Clear cache or update cache key
- uses: actions/cache@v3
  with:
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}

# 3. Permission issues
# Solution: Add proper permissions
permissions:
  contents: read
  pages: write
  id-token: write
```

## 🛡️ Project 5 Troubleshooting

### Docker Compose Issues

#### Services Not Starting
```bash
# Check service status
docker compose ps

# View service logs
docker compose logs [service-name]

# Common issues:
# 1. Port conflicts
netstat -tulpn | grep :3000  # Check if port is in use

# 2. Resource constraints
docker system df  # Check disk usage
docker stats      # Check resource usage

# 3. Image pull failures
docker compose pull  # Pre-pull images
```

#### Volume Mount Issues
```bash
# Error: Volume mount failed
# Windows: Ensure drive sharing is enabled in Docker Desktop
# Linux: Check file permissions

# Fix permission issues
sudo chown -R $USER:$USER ./grafana/
sudo chown -R $USER:$USER ./prometheus/
```

### Prometheus Issues

#### Scraping Failures
```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Common issues:
# 1. Service discovery
docker compose exec prometheus cat /etc/prometheus/prometheus.yml

# 2. Network connectivity
docker compose exec prometheus ping app

# 3. Metrics endpoint
curl http://localhost:3000/metrics
```

#### Configuration Errors
```bash
# Validate Prometheus config
docker compose exec prometheus promtool check config /etc/prometheus/prometheus.yml

# Reload configuration
curl -X POST http://localhost:9090/-/reload
```

### Grafana Issues

#### Dashboard Not Loading
```bash
# Check Grafana logs
docker compose logs grafana

# Reset Grafana data
docker compose down
docker volume rm project5_grafana_data
docker compose up -d grafana

# Manual dashboard import
# Navigate to http://localhost:3001
# Settings > Data Sources > Add Prometheus
# URL: http://prometheus:9090
```

#### Authentication Issues
```bash
# Default credentials
Username: admin
Password: admin123

# Reset admin password
docker compose exec grafana grafana-cli admin reset-admin-password newpassword
```

### Falco Issues

#### Security Events Not Detected
```bash
# Check Falco status
docker compose logs falco

# Verify rule loading
docker compose logs falco | grep "Loading rules"

# Test rule triggering
docker compose exec app curl http://localhost:3000/simulate/attack

# Check Falco configuration
docker compose exec falco cat /etc/falco/falco.yaml
```

#### Permission Issues
```bash
# Falco requires privileged access
# Ensure docker-compose.yml has:
privileged: true
pid: host

# Check host compatibility
# Some systems may not support all Falco features
```

### Attack Simulation Issues

#### Simulator Not Running
```bash
# Check attack simulator logs
docker compose logs attack-sim

# Manual simulation
docker compose exec app python -c "
import requests
requests.post('http://localhost:3000/simulate/attack', 
              json={'type': 'sql_injection'})
"

# Network connectivity
docker compose exec attack-sim ping demo-app
```

## 🔍 Debugging Techniques

### Log Analysis
```bash
# Project 2 - FastAPI logs
tail -f logs/app.log

# Project 3 - Browser console
# Open Developer Tools > Console

# Project 5 - Docker logs
docker compose logs -f --tail=100 [service-name]
```

### Network Debugging
```bash
# Check port availability
netstat -tulpn | grep :PORT

# Test connectivity
curl -v http://localhost:PORT/health

# Docker network inspection
docker network ls
docker network inspect project5_monitoring
```

### Performance Debugging
```bash
# System resources
top
htop
docker stats

# Application performance
# Use browser Developer Tools > Performance tab
# Monitor Grafana dashboards for metrics
```

## 🆘 Emergency Recovery

### Complete Reset
```bash
# Project 2
rm analyzer.db
pip install --force-reinstall -r requirements.txt
python setup.py build_ext --inplace

# Project 3
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps

# Project 5
docker compose down -v
docker system prune -a
docker compose up -d
```

### Backup Important Data
```bash
# Before major changes, backup:
cp analyzer.db analyzer.db.backup  # Project 2 database
cp -r node_modules node_modules.backup  # Project 3 dependencies
docker compose down  # Project 5 - ensure clean state
```

## 📞 Getting Help

### Documentation Resources
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Falco Documentation](https://falco.org/docs/)

### Community Support
- Stack Overflow with relevant tags
- GitHub Issues for specific tools
- Docker Community Forums
- Reddit DevOps communities

### Professional Support
- Consider professional consulting for production deployments
- Cloud provider support for managed services
- Enterprise support for critical applications
