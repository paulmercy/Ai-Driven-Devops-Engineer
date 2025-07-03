# DevSecOps Dashboard with Docker Compose + Prometheus + Grafana + Falco
# Comprehensive Makefile for easy presentation and demonstration

# Docker Compose files
COMPOSE_FILE := docker-compose.yml
COMPOSE_FALCO_MOCK := docker-compose.falco-mock.yml
COMPOSE_MINIMAL := docker-compose.minimal.yml
COMPOSE_ATTACK := docker-compose.attack.yml

# Colors for output
RED := \033[31m
GREEN := \033[32m
YELLOW := \033[33m
BLUE := \033[34m
MAGENTA := \033[35m
CYAN := \033[36m
WHITE := \033[37m
RESET := \033[0m

# Python command (use python3 for WSL/Linux)
PYTHON := $(shell which python3 2>/dev/null || which python 2>/dev/null || echo python3)

# Default target
.PHONY: help
help: ## Show this help message
	@echo "$(CYAN)🛡️  DevSecOps Dashboard - Make Commands$(RESET)"
	@echo "$(CYAN)================================================$(RESET)"
	@echo ""
	@echo "$(GREEN)📋 QUICK START:$(RESET)"
	@echo "  make demo          - Full demo presentation"
	@echo "  make start         - Start complete stack"
	@echo "  make mock          - Start with Mock Falco (WSL2 compatible)"
	@echo ""
	@echo "$(GREEN)🚀 STACK MANAGEMENT:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(CYAN)%-15s$(RESET) %s\n", $$1, $$2}'

.PHONY: check
check: ## 🔍 Check system requirements and configuration
	@echo "$(CYAN)🔍 Checking system requirements...$(RESET)"
	@echo ""
	@echo "$(YELLOW)Python version:$(RESET)"
	@$(PYTHON) --version || echo "$(RED)❌ Python not found$(RESET)"
	@echo ""
	@echo "$(YELLOW)Docker version:$(RESET)"
	@docker --version || echo "$(RED)❌ Docker not found$(RESET)"
	@echo ""
	@echo "$(YELLOW)Docker Compose version:$(RESET)"
	@docker-compose --version || echo "$(RED)❌ Docker Compose not found$(RESET)"
	@echo ""
	@echo "$(YELLOW)Validating compose files:$(RESET)"
	@$(MAKE) validate-compose
	@echo ""
	@echo "$(GREEN)✅ System check completed$(RESET)"

.PHONY: demo
demo: ## 🎬 Full presentation demo with all features
	@echo "$(MAGENTA)🎬 Starting DevSecOps Dashboard Demo$(RESET)"
	@echo "$(MAGENTA)=====================================$(RESET)"
	@echo ""
	@echo "$(YELLOW)Step 1: Starting complete monitoring stack...$(RESET)"
	@$(MAKE) start-mock
	@echo ""
	@echo "$(YELLOW)Step 2: Waiting for services to initialize...$(RESET)"
	@sleep 15
	@echo ""
	@echo "$(YELLOW)Step 3: Running security tests...$(RESET)"
	@$(MAKE) test-security
	@echo ""
	@echo "$(YELLOW)Step 4: Simulating attacks...$(RESET)"
	@$(MAKE) simulate-attacks
	@echo ""
	@echo "$(GREEN)✅ Demo complete! Access points:$(RESET)"
	@$(MAKE) show-urls

.PHONY: start
start: ## 🚀 Start complete DevSecOps stack
	@echo "$(GREEN)🚀 Starting DevSecOps Dashboard...$(RESET)"
	@docker-compose -f $(COMPOSE_FILE) up -d
	@echo "$(GREEN)✅ Stack started!$(RESET)"
	@$(MAKE) show-urls

.PHONY: start-mock
start-mock: ## 🛡️ Start stack with Mock Falco (WSL2 compatible)
	@echo "$(GREEN)🛡️  Starting DevSecOps Dashboard with Mock Falco...$(RESET)"
	@docker-compose -f $(COMPOSE_FALCO_MOCK) up -d
	@echo "$(GREEN)✅ Stack with Mock Falco started!$(RESET)"
	@$(MAKE) show-urls

.PHONY: mock
mock: start-mock ## 🛡️ Alias for start-mock

.PHONY: start-minimal
start-minimal: ## ⚡ Start minimal stack (Prometheus + Grafana only)
	@echo "$(GREEN)⚡ Starting minimal monitoring stack...$(RESET)"
	@docker-compose -f $(COMPOSE_MINIMAL) up -d
	@echo "$(GREEN)✅ Minimal stack started!$(RESET)"
	@$(MAKE) show-urls

.PHONY: stop
stop: ## 🛑 Stop all services
	@echo "$(RED)🛑 Stopping all services...$(RESET)"
	@docker-compose -f $(COMPOSE_FILE) down
	@docker-compose -f $(COMPOSE_FALCO_MOCK) down
	@docker-compose -f $(COMPOSE_MINIMAL) down
	@docker-compose -f $(COMPOSE_ATTACK) down
	@echo "$(RED)✅ All services stopped$(RESET)"

.PHONY: restart
restart: stop start ## 🔄 Restart complete stack

.PHONY: restart-mock
restart-mock: stop start-mock ## 🔄 Restart with Mock Falco

.PHONY: build
build: ## 🔨 Build all custom containers
	@echo "$(BLUE)🔨 Building custom containers...$(RESET)"
	@docker-compose -f $(COMPOSE_FILE) build
	@docker-compose -f $(COMPOSE_FALCO_MOCK) build
	@docker-compose -f $(COMPOSE_ATTACK) build
	@echo "$(BLUE)✅ Build complete!$(RESET)"

.PHONY: logs
logs: ## 📋 Show logs from all services
	@echo "$(CYAN)📋 Showing logs from all services...$(RESET)"
	@docker-compose -f $(COMPOSE_FILE) logs --tail=50

.PHONY: logs-falco
logs-falco: ## 🛡️ Show Falco security logs
	@echo "$(CYAN)🛡️  Showing Falco security logs...$(RESET)"
	@docker-compose -f $(COMPOSE_FILE) logs falco --tail=50

.PHONY: logs-mock
logs-mock: ## 🛡️ Show Mock Falco security logs
	@echo "$(CYAN)🛡️  Showing Mock Falco security logs...$(RESET)"
	@docker-compose -f $(COMPOSE_FALCO_MOCK) logs falco-mock --tail=50

.PHONY: logs-follow
logs-follow: ## 📋 Follow logs in real-time
	@echo "$(CYAN)📋 Following logs in real-time (Ctrl+C to stop)...$(RESET)"
	@docker-compose -f $(COMPOSE_FILE) logs -f

.PHONY: logs-follow-mock
logs-follow-mock: ## 🛡️ Follow Mock Falco logs in real-time
	@echo "$(CYAN)🛡️  Following Mock Falco logs in real-time (Ctrl+C to stop)...$(RESET)"
	@docker-compose -f $(COMPOSE_FALCO_MOCK) logs -f falco-mock

.PHONY: status
status: ## 📊 Show status of all services
	@echo "$(CYAN)📊 Service Status:$(RESET)"
	@echo "$(CYAN)=================$(RESET)"
	@docker-compose -f $(COMPOSE_FILE) ps 2>/dev/null || echo "Main stack not running"
	@echo ""
	@docker-compose -f $(COMPOSE_FALCO_MOCK) ps 2>/dev/null || echo "Mock Falco stack not running"

.PHONY: test-security
test-security: ## 🧪 Run security tests
	@echo "$(YELLOW)🧪 Running security tests...$(RESET)"
	@$(PYTHON) test_falco.py
	@echo "$(GREEN)✅ Security tests completed$(RESET)"

.PHONY: test-stack
test-stack: ## 🧪 Test complete stack functionality
	@echo "$(YELLOW)🧪 Testing complete stack...$(RESET)"
	@$(PYTHON) test_stack.py
	@echo "$(GREEN)✅ Stack tests completed$(RESET)"

.PHONY: test-grafana
test-grafana: ## 📊 Test Grafana dashboard configuration
	@echo "$(YELLOW)📊 Testing Grafana dashboard...$(RESET)"
	@$(PYTHON) test_grafana_dashboard.py
	@echo "$(GREEN)✅ Grafana tests completed$(RESET)"

.PHONY: simulate-attacks
simulate-attacks: ## ⚔️ Simulate security attacks
	@echo "$(RED)⚔️  Simulating security attacks...$(RESET)"
	@docker-compose -f $(COMPOSE_ATTACK) up -d attack-simulator
	@echo "$(RED)✅ Attack simulation started$(RESET)"

.PHONY: fix-falco
fix-falco: ## 🔧 Fix Falco issues (auto-detect WSL2)
	@echo "$(YELLOW)🔧 Running Falco diagnostic and fix...$(RESET)"
	@$(PYTHON) fix_falco.py
	@echo "$(GREEN)✅ Falco fix completed$(RESET)"

.PHONY: force-mock
force-mock: ## 🛡️ Force switch to Mock Falco
	@echo "$(YELLOW)🛡️  Forcing switch to Mock Falco...$(RESET)"
	@$(PYTHON) fix_falco.py --mock
	@echo "$(GREEN)✅ Switched to Mock Falco$(RESET)"

.PHONY: show-urls
show-urls: ## 🌐 Show all service URLs
	@echo ""
	@echo "$(GREEN)🌐 Service Access Points:$(RESET)"
	@echo "$(GREEN)========================$(RESET)"
	@echo "$(CYAN)📊 Grafana Dashboard:$(RESET)    http://localhost:3000 (admin/admin)"
	@echo "$(CYAN)🔍 Prometheus:$(RESET)           http://localhost:9090"
	@echo "$(CYAN)🚀 Demo App:$(RESET)             http://localhost:8000"
	@echo "$(CYAN)📱 UI Dashboard:$(RESET)         http://localhost:8080"
	@echo "$(CYAN)📋 App Logs:$(RESET)             http://localhost:8000/logs"
	@echo "$(CYAN)🛡️  Security Events:$(RESET)     http://localhost:8000/security"
	@echo ""

.PHONY: open-dashboards
open-dashboards: ## 🌐 Open all dashboards in browser
	@echo "$(GREEN)🌐 Opening dashboards in browser...$(RESET)"
	@$(PYTHON) -c "import webbrowser; webbrowser.open('http://localhost:3000')" 2>/dev/null || echo "Could not open browser"
	@$(PYTHON) -c "import webbrowser; webbrowser.open('http://localhost:9090')" 2>/dev/null || echo "Could not open browser"
	@$(PYTHON) -c "import webbrowser; webbrowser.open('http://localhost:8000')" 2>/dev/null || echo "Could not open browser"
	@$(PYTHON) -c "import webbrowser; webbrowser.open('http://localhost:8080')" 2>/dev/null || echo "Could not open browser"

.PHONY: clean
clean: ## 🧹 Clean up containers and volumes
	@echo "$(RED)🧹 Cleaning up containers and volumes...$(RESET)"
	@docker-compose -f $(COMPOSE_FILE) down -v --remove-orphans
	@docker-compose -f $(COMPOSE_FALCO_MOCK) down -v --remove-orphans
	@docker-compose -f $(COMPOSE_MINIMAL) down -v --remove-orphans
	@docker-compose -f $(COMPOSE_ATTACK) down -v --remove-orphans
	@docker system prune -f
	@echo "$(RED)✅ Cleanup completed$(RESET)"

.PHONY: reset
reset: clean build start-mock ## 🔄 Complete reset and restart with Mock Falco

.PHONY: presentation
presentation: ## 🎯 Presentation mode - optimized for demos
	@echo "$(MAGENTA)🎯 Starting Presentation Mode$(RESET)"
	@echo "$(MAGENTA)=============================$(RESET)"
	@$(MAKE) clean
	@$(MAKE) build
	@$(MAKE) start-mock
	@echo ""
	@echo "$(YELLOW)⏳ Waiting for services to stabilize...$(RESET)"
	@sleep 20
	@echo ""
	@$(MAKE) test-security
	@$(MAKE) simulate-attacks
	@echo ""
	@echo "$(GREEN)🎉 Presentation ready!$(RESET)"
	@$(MAKE) show-urls
	@$(MAKE) open-dashboards

.PHONY: dev
dev: ## 👨‍💻 Development mode - start with live logs
	@$(MAKE) start-mock
	@echo "$(CYAN)👨‍💻 Development mode - showing live logs...$(RESET)"
	@$(MAKE) logs-follow-mock

.PHONY: monitor
monitor: ## 📊 Monitor security events in real-time
	@echo "$(CYAN)📊 Monitoring security events in real-time...$(RESET)"
	@echo "$(CYAN)Press Ctrl+C to stop monitoring$(RESET)"
	@echo ""
	@$(MAKE) logs-follow-mock

.PHONY: health
health: ## 🏥 Check health of all services
	@echo "$(CYAN)🏥 Health Check:$(RESET)"
	@echo "$(CYAN)===============$(RESET)"
	@echo ""
	@echo "$(YELLOW)Checking Grafana...$(RESET)"
	@curl -s http://localhost:3000/api/health > /dev/null && echo "$(GREEN)✅ Grafana: Healthy$(RESET)" || echo "$(RED)❌ Grafana: Unhealthy$(RESET)"
	@echo "$(YELLOW)Checking Prometheus...$(RESET)"
	@curl -s http://localhost:9090/-/healthy > /dev/null && echo "$(GREEN)✅ Prometheus: Healthy$(RESET)" || echo "$(RED)❌ Prometheus: Unhealthy$(RESET)"
	@echo "$(YELLOW)Checking Demo App...$(RESET)"
	@curl -s http://localhost:8000/health > /dev/null && echo "$(GREEN)✅ Demo App: Healthy$(RESET)" || echo "$(RED)❌ Demo App: Unhealthy$(RESET)"
	@echo ""

.PHONY: backup
backup: ## 💾 Backup Grafana dashboards and Prometheus data
	@echo "$(BLUE)💾 Creating backup...$(RESET)"
	@mkdir -p backups/$(shell date +%Y%m%d_%H%M%S)
	@docker cp $$(docker-compose ps -q grafana):/var/lib/grafana backups/$(shell date +%Y%m%d_%H%M%S)/grafana 2>/dev/null || echo "Grafana not running"
	@docker cp $$(docker-compose ps -q prometheus):/prometheus backups/$(shell date +%Y%m%d_%H%M%S)/prometheus 2>/dev/null || echo "Prometheus not running"
	@echo "$(BLUE)✅ Backup completed$(RESET)"

.PHONY: quick-demo
quick-demo: ## ⚡ Quick 2-minute demo
	@echo "$(MAGENTA)⚡ Quick Demo (2 minutes)$(RESET)"
	@echo "$(MAGENTA)========================$(RESET)"
	@$(MAKE) start-mock
	@sleep 10
	@$(MAKE) test-security
	@echo "$(GREEN)✅ Quick demo complete!$(RESET)"
	@$(MAKE) show-urls

.PHONY: logs-all
logs-all: ## 📋 Show logs from all running stacks
	@echo "$(CYAN)📋 All Stack Logs:$(RESET)"
	@echo "$(CYAN)==================$(RESET)"
	@echo ""
	@echo "$(YELLOW)Main Stack Logs:$(RESET)"
	@docker-compose -f $(COMPOSE_FILE) logs --tail=20 2>/dev/null || echo "Main stack not running"
	@echo ""
	@echo "$(YELLOW)Mock Falco Stack Logs:$(RESET)"
	@docker-compose -f $(COMPOSE_FALCO_MOCK) logs --tail=20 2>/dev/null || echo "Mock Falco stack not running"

.PHONY: logs-security
logs-security: ## 🛡️ Show only security-related logs
	@echo "$(CYAN)🛡️  Security Logs:$(RESET)"
	@echo "$(CYAN)==================$(RESET)"
	@docker-compose -f $(COMPOSE_FILE) logs falco --tail=30 2>/dev/null || echo "Real Falco not running"
	@docker-compose -f $(COMPOSE_FALCO_MOCK) logs falco-mock --tail=30 2>/dev/null || echo "Mock Falco not running"

.PHONY: shell-app
shell-app: ## 🐚 Open shell in demo app container
	@echo "$(CYAN)🐚 Opening shell in demo app...$(RESET)"
	@docker-compose -f $(COMPOSE_FALCO_MOCK) exec demo-app /bin/bash 2>/dev/null || \
	 docker-compose -f $(COMPOSE_FILE) exec demo-app /bin/bash 2>/dev/null || \
	 echo "$(RED)❌ No demo app container running. Try: make start-mock$(RESET)"

.PHONY: shell-falco
shell-falco: ## 🐚 Open shell in Falco container
	@echo "$(CYAN)🐚 Opening shell in Falco container...$(RESET)"
	@docker-compose -f $(COMPOSE_FALCO_MOCK) exec falco-mock /bin/bash 2>/dev/null || \
	 docker-compose -f $(COMPOSE_FILE) exec falco /bin/bash 2>/dev/null || \
	 echo "$(RED)❌ No Falco container running. Try: make start-mock$(RESET)"

.PHONY: generate-traffic
generate-traffic: ## 🚦 Generate test traffic and security events
	@echo "$(YELLOW)🚦 Generating test traffic...$(RESET)"
	@for i in {1..5}; do \
		curl -s http://localhost:8000/health > /dev/null; \
		curl -s http://localhost:8000/metrics > /dev/null; \
		curl -s http://localhost:8000/logs > /dev/null; \
		sleep 2; \
	done
	@echo "$(GREEN)✅ Test traffic generated$(RESET)"

.PHONY: stress-test
stress-test: ## 💪 Run stress test on the application
	@echo "$(RED)💪 Running stress test...$(RESET)"
	@for i in {1..20}; do \
		curl -s http://localhost:8000/health & \
		curl -s http://localhost:8000/metrics & \
		curl -s http://localhost:8000/security & \
	done; wait
	@echo "$(GREEN)✅ Stress test completed$(RESET)"

.PHONY: install-deps
install-deps: ## 📦 Install Python dependencies for testing
	@echo "$(BLUE)📦 Installing Python dependencies...$(RESET)"
	@pip3 install docker requests prometheus-client 2>/dev/null || pip install docker requests prometheus-client
	@echo "$(GREEN)✅ Dependencies installed$(RESET)"

.PHONY: validate-compose
validate-compose: ## ✅ Validate all Docker Compose files
	@echo "$(YELLOW)✅ Validating Docker Compose files...$(RESET)"
	@docker-compose -f $(COMPOSE_FILE) config > /dev/null && echo "$(GREEN)✅ Main compose file valid$(RESET)" || echo "$(RED)❌ Main compose file invalid$(RESET)"
	@docker-compose -f $(COMPOSE_FALCO_MOCK) config > /dev/null && echo "$(GREEN)✅ Mock Falco compose file valid$(RESET)" || echo "$(RED)❌ Mock Falco compose file invalid$(RESET)"
	@docker-compose -f $(COMPOSE_MINIMAL) config > /dev/null && echo "$(GREEN)✅ Minimal compose file valid$(RESET)" || echo "$(RED)❌ Minimal compose file invalid$(RESET)"
	@docker-compose -f $(COMPOSE_ATTACK) config > /dev/null && echo "$(GREEN)✅ Attack compose file valid$(RESET)" || echo "$(RED)❌ Attack compose file invalid$(RESET)"

.PHONY: ports
ports: ## 🔌 Show all exposed ports
	@echo "$(CYAN)🔌 Exposed Ports:$(RESET)"
	@echo "$(CYAN)=================$(RESET)"
	@echo "$(GREEN)3000$(RESET) - Grafana Dashboard"
	@echo "$(GREEN)9090$(RESET) - Prometheus"
	@echo "$(GREEN)8000$(RESET) - Demo Application"
	@echo "$(GREEN)8080$(RESET) - UI Dashboard"
	@echo "$(GREEN)24224$(RESET) - Fluentd"
	@echo ""

.PHONY: troubleshoot
troubleshoot: ## 🔍 Run troubleshooting diagnostics
	@echo "$(YELLOW)🔍 Running troubleshooting diagnostics...$(RESET)"
	@echo ""
	@$(MAKE) status
	@echo ""
	@$(MAKE) health
	@echo ""
	@$(MAKE) ports
	@echo ""
	@echo "$(YELLOW)Docker System Info:$(RESET)"
	@docker system df
	@echo ""
	@echo "$(YELLOW)Recent Docker Events:$(RESET)"
	@docker events --since 5m --until now 2>/dev/null | tail -10 || echo "No recent events"

.PHONY: update-images
update-images: ## 🔄 Update all Docker images
	@echo "$(BLUE)🔄 Updating Docker images...$(RESET)"
	@docker-compose -f $(COMPOSE_FILE) pull
	@docker-compose -f $(COMPOSE_FALCO_MOCK) pull
	@docker-compose -f $(COMPOSE_MINIMAL) pull
	@docker-compose -f $(COMPOSE_ATTACK) pull
	@echo "$(GREEN)✅ Images updated$(RESET)"

.PHONY: security-scan
security-scan: ## 🔒 Run security scan on containers
	@echo "$(RED)🔒 Running security scan...$(RESET)"
	@docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
		aquasec/trivy image --severity HIGH,CRITICAL \
		grafana/grafana:latest || echo "Trivy not available"
	@echo "$(GREEN)✅ Security scan completed$(RESET)"

.PHONY: export-logs
export-logs: ## 📤 Export all logs to files
	@echo "$(BLUE)📤 Exporting logs...$(RESET)"
	@mkdir -p logs/export/$(shell date +%Y%m%d_%H%M%S)
	@docker-compose -f $(COMPOSE_FILE) logs > logs/export/$(shell date +%Y%m%d_%H%M%S)/main-stack.log 2>/dev/null || echo "Main stack not running"
	@docker-compose -f $(COMPOSE_FALCO_MOCK) logs > logs/export/$(shell date +%Y%m%d_%H%M%S)/mock-falco.log 2>/dev/null || echo "Mock Falco not running"
	@echo "$(GREEN)✅ Logs exported to logs/export/$(RESET)"

.PHONY: demo-script
demo-script: ## 📜 Show demo script commands
	@echo "$(MAGENTA)📜 Demo Script Commands:$(RESET)"
	@echo "$(MAGENTA)========================$(RESET)"
	@echo ""
	@echo "$(GREEN)1. Start the stack:$(RESET)"
	@echo "   make start-mock"
	@echo ""
	@echo "$(GREEN)2. Open dashboards:$(RESET)"
	@echo "   make open-dashboards"
	@echo ""
	@echo "$(GREEN)3. Run security tests:$(RESET)"
	@echo "   make test-security"
	@echo ""
	@echo "$(GREEN)4. Monitor security events:$(RESET)"
	@echo "   make monitor"
	@echo ""
	@echo "$(GREEN)5. Simulate attacks:$(RESET)"
	@echo "   make simulate-attacks"
	@echo ""
	@echo "$(GREEN)6. Generate traffic:$(RESET)"
	@echo "   make generate-traffic"
	@echo ""
	@echo "$(GREEN)7. Check health:$(RESET)"
	@echo "   make health"
	@echo ""
	@echo "$(GREEN)8. Clean up:$(RESET)"
	@echo "   make stop"
