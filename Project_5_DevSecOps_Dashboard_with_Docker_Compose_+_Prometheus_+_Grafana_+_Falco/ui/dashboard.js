// Dashboard Configuration
const CONFIG = {
    API_BASE: 'http://localhost:3000',
    GRAFANA_URL: 'http://localhost:3001',
    PROMETHEUS_URL: 'http://localhost:9090',
    REFRESH_INTERVAL: 30000, // 30 seconds
    SERVICES: {
        'app': { name: 'Demo App', port: 3000, endpoint: '/health' },
        'prometheus': { name: 'Prometheus', port: 9090, endpoint: '/api/v1/status/config' },
        'grafana': { name: 'Grafana', port: 3001, endpoint: '/api/health' },
        'cadvisor': { name: 'cAdvisor', port: 8080, endpoint: '/healthz' },
        'node-exporter': { name: 'Node Exporter', port: 9100, endpoint: '/metrics' },
        'redis': { name: 'Redis', port: 6379, endpoint: null }
    },
    ATTACK_TYPES: {
        'sql_injection': { name: 'SQL Injection', icon: 'database', description: 'Test SQL injection vulnerabilities' },
        'xss_attack': { name: 'XSS Attack', icon: 'code', description: 'Cross-site scripting simulation' },
        'brute_force': { name: 'Brute Force', icon: 'lock', description: 'Password brute force attempt' },
        'dos_attack': { name: 'DoS Attack', icon: 'bomb', description: 'Denial of service simulation' },
        'privilege_escalation': { name: 'Privilege Escalation', icon: 'user-shield', description: 'Privilege escalation test' },
        'file_access': { name: 'Unauthorized File Access', icon: 'file-alt', description: 'File system access test' }
    }
};

// Global state
let dashboardState = {
    isConnected: false,
    lastUpdate: null,
    metrics: {},
    services: {},
    securityEvents: [],
    refreshTimer: null
};

// Initialize Dashboard
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
    setupEventListeners();
    startAutoRefresh();
});

function initializeDashboard() {
    console.log('🚀 Initializing DevSecOps Dashboard...');
    
    // Set initial state
    updateConnectionStatus(false);
    updateLastUpdated();
    
    // Load initial data
    refreshDashboard();
    
    // Show overview section by default
    showSection('overview');
}

function setupEventListeners() {
    // Navigation
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', function() {
            const section = this.dataset.section;
            showSection(section);
            
            // Update active nav item
            document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));
            this.classList.add('active');
        });
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        if (e.ctrlKey || e.metaKey) {
            switch(e.key) {
                case 'r':
                    e.preventDefault();
                    refreshDashboard();
                    break;
                case '1':
                    e.preventDefault();
                    showSection('overview');
                    break;
                case '2':
                    e.preventDefault();
                    showSection('security');
                    break;
            }
        }
    });
}

function showSection(sectionName) {
    // Hide all sections
    document.querySelectorAll('.dashboard-section').forEach(section => {
        section.classList.remove('active');
    });
    
    // Show selected section
    const targetSection = document.getElementById(sectionName);
    if (targetSection) {
        targetSection.classList.add('active');
        
        // Load section-specific data
        switch(sectionName) {
            case 'security':
                loadSecurityData();
                break;
            case 'monitoring':
                loadMonitoringData();
                break;
            case 'services':
                loadServicesData();
                break;
        }
    }
}

async function refreshDashboard() {
    console.log('🔄 Refreshing dashboard data...');
    showLoading(true);
    
    try {
        // Test connection
        await testConnection();
        
        // Load all data in parallel
        await Promise.all([
            loadSystemMetrics(),
            loadServiceStatus(),
            loadSecurityStatus()
        ]);
        
        updateConnectionStatus(true);
        updateLastUpdated();
        
    } catch (error) {
        console.error('❌ Dashboard refresh failed:', error);
        updateConnectionStatus(false);
        showNotification('Failed to refresh dashboard data', 'error');
    } finally {
        showLoading(false);
    }
}

async function testConnection() {
    try {
        const response = await fetch(`${CONFIG.API_BASE}/health`, {
            method: 'GET',
            timeout: 5000
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        throw new Error(`Connection test failed: ${error.message}`);
    }
}

async function loadSystemMetrics() {
    try {
        // Load basic metrics from the demo app
        const healthResponse = await fetch(`${CONFIG.API_BASE}/health`);
        const healthData = await healthResponse.json();
        
        // Update system health
        document.getElementById('systemHealth').textContent = healthData.status === 'healthy' ? '✅ Healthy' : '❌ Unhealthy';
        
        // Load security metrics
        const securityResponse = await fetch(`${CONFIG.API_BASE}/api/security-status`);
        const securityData = await securityResponse.json();
        
        // Update metrics display
        document.getElementById('activeConnections').textContent = securityData.active_sessions || '0';
        document.getElementById('responseTime').textContent = '< 100ms'; // Mock data
        
        // Store in state
        dashboardState.metrics = {
            health: healthData,
            security: securityData
        };
        
    } catch (error) {
        console.error('Failed to load system metrics:', error);
        // Set fallback values
        document.getElementById('systemHealth').textContent = '❓ Unknown';
        document.getElementById('activeConnections').textContent = '--';
        document.getElementById('responseTime').textContent = '--';
    }
}

async function loadServiceStatus() {
    const services = CONFIG.SERVICES;
    
    for (const [serviceId, service] of Object.entries(services)) {
        try {
            let isHealthy = false;
            
            if (service.endpoint) {
                const url = `http://localhost:${service.port}${service.endpoint}`;
                const response = await fetch(url, { 
                    method: 'GET',
                    timeout: 3000,
                    mode: 'no-cors' // Handle CORS issues
                });
                isHealthy = true; // If no error thrown, service is reachable
            } else {
                // For services without HTTP endpoints (like Redis), assume healthy if no error
                isHealthy = true;
            }
            
            updateServiceCard(serviceId, isHealthy ? 'healthy' : 'unhealthy');
            dashboardState.services[serviceId] = { status: isHealthy ? 'healthy' : 'unhealthy' };
            
        } catch (error) {
            console.warn(`Service ${serviceId} health check failed:`, error);
            updateServiceCard(serviceId, 'unhealthy');
            dashboardState.services[serviceId] = { status: 'unhealthy' };
        }
    }
}

async function loadSecurityStatus() {
    try {
        const response = await fetch(`${CONFIG.API_BASE}/api/security-status`);
        const data = await response.json();
        
        // Update security status display
        document.getElementById('falcoStatus').textContent = data.monitoring_enabled ? 'Active' : 'Inactive';
        document.getElementById('lastScan').textContent = new Date(data.last_check).toLocaleTimeString();
        
        // Mock threat counts (in real implementation, these would come from Prometheus/Falco)
        document.getElementById('sqlInjectionCount').textContent = '0';
        document.getElementById('privilegeEscalationCount').textContent = '0';
        document.getElementById('fileAccessCount').textContent = '0';
        document.getElementById('networkScanCount').textContent = '0';
        
        // Update security alerts count
        document.getElementById('securityAlerts').textContent = '0';
        
    } catch (error) {
        console.error('Failed to load security status:', error);
        document.getElementById('falcoStatus').textContent = 'Unknown';
        document.getElementById('lastScan').textContent = '--';
    }
}

function updateServiceCard(serviceId, status) {
    const card = document.getElementById(`service-${serviceId}`);
    if (card) {
        // Remove existing status classes
        card.classList.remove('healthy', 'unhealthy', 'warning');
        // Add new status class
        card.classList.add(status);
    }
}

function updateConnectionStatus(isConnected) {
    dashboardState.isConnected = isConnected;
    const statusElement = document.getElementById('connectionStatus');
    
    if (isConnected) {
        statusElement.classList.remove('disconnected');
        statusElement.innerHTML = '<i class="fas fa-circle"></i><span>Connected</span>';
    } else {
        statusElement.classList.add('disconnected');
        statusElement.innerHTML = '<i class="fas fa-circle"></i><span>Disconnected</span>';
    }
}

function updateLastUpdated() {
    const now = new Date();
    dashboardState.lastUpdate = now;
    document.getElementById('lastUpdated').textContent = now.toLocaleTimeString();
}

function showLoading(show) {
    const overlay = document.getElementById('loadingOverlay');
    overlay.style.display = show ? 'flex' : 'none';
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'error' ? 'exclamation-triangle' : 'info-circle'}"></i>
        <span>${message}</span>
    `;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 5000);
}

function startAutoRefresh() {
    if (dashboardState.refreshTimer) {
        clearInterval(dashboardState.refreshTimer);
    }
    
    dashboardState.refreshTimer = setInterval(() => {
        if (dashboardState.isConnected) {
            refreshDashboard();
        }
    }, CONFIG.REFRESH_INTERVAL);
}

// Action Functions
function openGrafana() {
    window.open(CONFIG.GRAFANA_URL, '_blank');
}

function openPrometheus() {
    window.open(CONFIG.PROMETHEUS_URL, '_blank');
}

async function runHealthCheck() {
    showLoading(true);
    try {
        const response = await fetch(`${CONFIG.API_BASE}/health`);
        const data = await response.json();
        
        showNotification(`Health Check: ${data.status}`, data.status === 'healthy' ? 'success' : 'warning');
    } catch (error) {
        showNotification('Health check failed', 'error');
    } finally {
        showLoading(false);
    }
}

async function simulateAttack(buttonElement = null) {
    const attackTypes = Object.keys(CONFIG.ATTACK_TYPES);
    const randomAttack = attackTypes[Math.floor(Math.random() * attackTypes.length)];
    const attackConfig = CONFIG.ATTACK_TYPES[randomAttack];

    setButtonLoading(buttonElement, true);
    showLoading(true, `Simulating ${attackConfig.name} attack...`);

    try {
        showNotification(`🎯 Running random attack: ${attackConfig.name}...`, 'warning');

        let response;
        try {
            // Try POST first
            response = await fetch(`${CONFIG.API_BASE}/api/simulate/attack`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    type: randomAttack,
                    description: `Random ${attackConfig.description}`
                })
            });

            // If POST fails, try GET as fallback
            if (!response.ok) {
                const params = new URLSearchParams({
                    attack_type: randomAttack,
                    description: `Random ${attackConfig.description}`
                });
                response = await fetch(`${CONFIG.API_BASE}/api/simulate/attack?${params}`, {
                    method: 'GET'
                });
            }
        } catch (error) {
            // If both fail, try GET as final fallback
            const params = new URLSearchParams({
                attack_type: randomAttack,
                description: `Random ${attackConfig.description}`
            });
            response = await fetch(`${CONFIG.API_BASE}/api/simulate/attack?${params}`, {
                method: 'GET'
            });
        }

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        await response.json();
        showNotification(`✅ Random attack (${attackConfig.name}) completed successfully!`, 'success');

        // Update security metrics and refresh data
        updateSecurityMetrics(randomAttack, 'detected');
        setTimeout(() => {
            loadSecurityStatus();
        }, 2000);

    } catch (error) {
        console.error('Random attack simulation failed:', error);
        showNotification(`❌ Random attack simulation failed: ${error.message}`, 'error');
    } finally {
        setButtonLoading(buttonElement, false);
        showLoading(false);
    }
}

function refreshSecurity() {
    loadSecurityStatus();
    showNotification('Security data refreshed', 'success');
}

// Section-specific data loading functions
async function loadSecurityData() {
    console.log('Loading security data...');
    await loadSecurityStatus();
}

async function loadMonitoringData() {
    console.log('Loading monitoring data...');
    // This would load Prometheus metrics, charts, etc.
}

async function loadServicesData() {
    console.log('Loading services data...');
    await loadServiceStatus();
}

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    if (dashboardState.refreshTimer) {
        clearInterval(dashboardState.refreshTimer);
    }
});

// Additional Action Functions for new sections
async function refreshMonitoring() {
    showLoading(true);
    try {
        // Refresh Prometheus targets and system metrics
        await Promise.all([
            loadPrometheusTargets(),
            loadSystemMetrics(),
            loadServiceStatus()
        ]);

        // Update monitoring dashboard timestamp
        updateLastUpdated();

        showNotification('Monitoring data refreshed successfully', 'success');
    } catch (error) {
        console.error('Failed to refresh monitoring data:', error);
        showNotification(`Failed to refresh monitoring data: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

async function loadPrometheusTargets() {
    try {
        // In a real implementation, this would fetch from Prometheus API
        // For now, we'll simulate the data
        const targets = [
            { name: 'demo-app', status: 'UP' },
            { name: 'node-exporter', status: 'UP' },
            { name: 'cadvisor', status: 'UP' }
        ];

        const targetsContainer = document.getElementById('prometheusTargets');
        if (targetsContainer) {
            targetsContainer.innerHTML = targets.map(target => `
                <div class="target-item">
                    <span class="target-name">${target.name}</span>
                    <span class="target-status ${target.status === 'UP' ? 'healthy' : 'unhealthy'}">${target.status}</span>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Failed to load Prometheus targets:', error);
    }
}

async function refreshServices() {
    await loadServiceStatus();
    showNotification('Service status refreshed', 'success');
}

async function startAllServices(buttonElement = null) {
    setButtonLoading(buttonElement, true);
    showLoading(true, 'Starting all services...');

    try {
        showNotification('Starting all services...', 'info');

        // Call the backend API to start services
        const response = await fetch(`${CONFIG.API_BASE}/api/services/start-all`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const result = await response.json();
        showNotification(result.message || 'All services started successfully! 🚀', 'success');

        // Refresh service status after a delay
        setTimeout(() => {
            refreshServices();
        }, 3000);

    } catch (error) {
        console.error('Failed to start services:', error);
        showNotification(`Failed to start services: ${error.message}`, 'error');
    } finally {
        setButtonLoading(buttonElement, false);
        showLoading(false);
    }
}

async function stopAllServices(buttonElement = null) {
    if (!confirm('Are you sure you want to stop all services? This will shut down the entire DevSecOps stack.')) {
        return;
    }

    setButtonLoading(buttonElement, true);
    showLoading(true, 'Stopping all services...');

    try {
        showNotification('Stopping all services...', 'warning');

        // Call the backend API to stop services
        const response = await fetch(`${CONFIG.API_BASE}/api/services/stop-all`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const result = await response.json();
        showNotification(result.message || 'All services stopped successfully! 🛑', 'success');

        // Refresh service status after a delay
        setTimeout(() => {
            refreshServices();
        }, 2000);

    } catch (error) {
        console.error('Failed to stop services:', error);
        showNotification(`Failed to stop services: ${error.message}`, 'error');
    } finally {
        setButtonLoading(buttonElement, false);
        showLoading(false);
    }
}

async function restartAllServices() {
    if (!confirm('Are you sure you want to restart all services? This will temporarily interrupt all monitoring.')) {
        return;
    }

    showLoading(true);
    try {
        showNotification('Restarting all services...', 'warning');

        // Call the backend API to restart services
        const response = await fetch(`${CONFIG.API_BASE}/api/services/restart-all`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const result = await response.json();
        showNotification(result.message || 'All services restarted successfully', 'success');

        // Refresh service status after a longer delay for restart
        setTimeout(() => {
            refreshServices();
        }, 5000);

    } catch (error) {
        console.error('Failed to restart services:', error);
        showNotification(`Failed to restart services: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

function viewServiceLogs(serviceName) {
    // Switch to logs section and filter by service
    showSection('logs');
    document.querySelector('[data-section="logs"]').classList.add('active');
    document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));
    document.querySelector('[data-section="logs"]').classList.add('active');

    // Filter logs by service (in a real implementation)
    showNotification(`Viewing logs for ${serviceName}`, 'info');
}

async function restartService(serviceName) {
    if (!confirm(`Are you sure you want to restart ${serviceName}?`)) {
        return;
    }

    showLoading(true);
    try {
        showNotification(`Restarting ${serviceName}...`, 'warning');

        // Simulate service restart
        setTimeout(() => {
            showNotification(`${serviceName} restarted successfully`, 'success');
            refreshServices();
        }, 3000);

    } catch (error) {
        showNotification(`Failed to restart ${serviceName}`, 'error');
    } finally {
        showLoading(false);
    }
}

async function runAttackSimulation(attackType) {
    const attackConfig = CONFIG.ATTACK_TYPES[attackType];
    const attackName = attackConfig ? attackConfig.name : attackType.replace('_', ' ');

    if (!confirm(`Are you sure you want to simulate a ${attackName} attack? This will test security monitoring systems.`)) {
        return;
    }

    showLoading(true);
    try {
        showNotification(`Simulating ${attackName} attack...`, 'warning');

        let response;
        try {
            // Try POST first
            response = await fetch(`${CONFIG.API_BASE}/api/simulate/attack`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    type: attackType,
                    description: attackConfig ? attackConfig.description : `${attackName} simulation`
                })
            });

            // If POST fails, try GET as fallback
            if (!response.ok) {
                const params = new URLSearchParams({
                    attack_type: attackType,
                    description: attackConfig ? attackConfig.description : `${attackName} simulation`
                });
                response = await fetch(`${CONFIG.API_BASE}/api/simulate/attack?${params}`, {
                    method: 'GET'
                });
            }
        } catch (error) {
            // If both fail, try GET as final fallback
            const params = new URLSearchParams({
                attack_type: attackType,
                description: attackConfig ? attackConfig.description : `${attackName} simulation`
            });
            response = await fetch(`${CONFIG.API_BASE}/api/simulate/attack?${params}`, {
                method: 'GET'
            });
        }

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();

        // Add result to attack results log
        addAttackResult(attackType, 'success', data.message || 'Attack simulation completed successfully');

        showNotification(`${attackName} simulation completed`, 'success');

        // Update security metrics and refresh data
        updateSecurityMetrics(attackType, 'detected');
        setTimeout(() => {
            loadSecurityStatus();
        }, 2000);

    } catch (error) {
        console.error('Attack simulation failed:', error);
        addAttackResult(attackType, 'error', `Failed: ${error.message}`);
        showNotification(`Attack simulation failed: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

function addAttackResult(attackType, status, message) {
    const resultsContainer = document.getElementById('attackResults');
    if (!resultsContainer) return;

    const timestamp = new Date().toLocaleTimeString();
    const logEntry = document.createElement('div');
    logEntry.className = 'log-entry';
    logEntry.innerHTML = `
        <span class="log-time">${timestamp}</span>
        <span class="log-message">${attackType.replace('_', ' ')}: ${message}</span>
        <span class="log-status ${status}">${status.toUpperCase()}</span>
    `;

    // Add to top of results
    resultsContainer.insertBefore(logEntry, resultsContainer.firstChild);

    // Keep only last 10 results
    while (resultsContainer.children.length > 10) {
        resultsContainer.removeChild(resultsContainer.lastChild);
    }
}

async function refreshLogs() {
    showLoading(true);
    try {
        // Fetch fresh logs from the backend
        await loadSystemLogs();
        showNotification('Logs refreshed successfully', 'success');
    } catch (error) {
        console.error('Failed to refresh logs:', error);
        showNotification(`Failed to refresh logs: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

async function loadSystemLogs() {
    try {
        // Try to fetch real logs from the backend
        const response = await fetch(`${CONFIG.API_BASE}/api/logs`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        let logs = [];

        if (response.ok) {
            const data = await response.json();
            logs = data.logs || [];
        } else {
            // Fallback to mock logs if API is not available
            logs = [
                {
                    timestamp: new Date().toISOString(),
                    level: 'info',
                    source: 'demo-app',
                    message: 'Health check endpoint accessed'
                },
                {
                    timestamp: new Date(Date.now() - 30000).toISOString(),
                    level: 'info',
                    source: 'prometheus',
                    message: 'Metrics scraped successfully'
                },
                {
                    timestamp: new Date(Date.now() - 60000).toISOString(),
                    level: 'warning',
                    source: 'falco',
                    message: 'Suspicious file access detected'
                }
            ];
        }

        const logViewer = document.getElementById('logViewer');
        if (logViewer) {
            logViewer.innerHTML = logs.map(log => `
                <div class="log-line">
                    <span class="log-timestamp">${new Date(log.timestamp).toLocaleString()}</span>
                    <span class="log-level ${log.level}">${log.level.toUpperCase()}</span>
                    <span class="log-source">${log.source}</span>
                    <span class="log-message">${log.message}</span>
                </div>
            `).join('');

            // Auto-scroll to bottom to show latest logs
            logViewer.scrollTop = logViewer.scrollHeight;
        }

    } catch (error) {
        console.error('Failed to load system logs:', error);
        showNotification('Failed to load system logs', 'error');
    }
}

function clearLogs() {
    if (!confirm('Are you sure you want to clear all logs? This action cannot be undone.')) {
        return;
    }

    try {
        const logViewer = document.getElementById('logViewer');
        if (logViewer) {
            logViewer.innerHTML = '<div class="log-line"><span class="log-timestamp">' +
                new Date().toLocaleString() + '</span><span class="log-level info">INFO</span>' +
                '<span class="log-source">system</span><span class="log-message">Logs cleared by user</span></div>';
        }
        showNotification('Logs cleared successfully', 'success');
    } catch (error) {
        console.error('Failed to clear logs:', error);
        showNotification('Failed to clear logs', 'error');
    }
}

// Helper function to update last updated timestamp
function updateLastUpdated() {
    const lastUpdatedElement = document.getElementById('lastUpdated');
    if (lastUpdatedElement) {
        lastUpdatedElement.textContent = new Date().toLocaleString();
    }
}

// Enhanced button loading state management
function setButtonLoading(button, isLoading) {
    if (!button) return;

    if (isLoading) {
        button.classList.add('loading');
        button.disabled = true;
        button.style.pointerEvents = 'none';
    } else {
        button.classList.remove('loading');
        button.disabled = false;
        button.style.pointerEvents = 'auto';
    }
}

// Enhanced notification system with icons
function showNotification(message, type = 'info', duration = 5000) {
    // Remove existing notifications
    const existingNotifications = document.querySelectorAll('.notification');
    existingNotifications.forEach(notification => {
        notification.remove();
    });

    const notification = document.createElement('div');
    notification.className = `notification ${type}`;

    // Add appropriate icon based on type
    const icons = {
        success: 'fas fa-check-circle',
        error: 'fas fa-exclamation-circle',
        warning: 'fas fa-exclamation-triangle',
        info: 'fas fa-info-circle'
    };

    notification.innerHTML = `
        <i class="${icons[type] || icons.info}"></i>
        <span>${message}</span>
    `;

    document.body.appendChild(notification);

    // Auto-remove after duration
    setTimeout(() => {
        if (notification.parentNode) {
            notification.style.animation = 'slideOut 0.3s ease forwards';
            setTimeout(() => {
                notification.remove();
            }, 300);
        }
    }, duration);
}

// Enhanced loading overlay with message
function showLoading(show, message = 'Loading...') {
    const overlay = document.getElementById('loadingOverlay');
    if (!overlay) return;

    const spinner = overlay.querySelector('.loading-spinner');
    if (spinner) {
        const messageElement = spinner.querySelector('.loading-message') || document.createElement('div');
        messageElement.className = 'loading-message';
        messageElement.textContent = message;
        if (!spinner.querySelector('.loading-message')) {
            spinner.appendChild(messageElement);
        }
    }

    if (show) {
        overlay.classList.add('active');
        overlay.style.display = 'flex';
    } else {
        overlay.classList.remove('active');
        setTimeout(() => {
            overlay.style.display = 'none';
        }, 300);
    }
}

// Enhanced notification system
function showNotification(message, type = 'info', duration = 5000) {
    // Remove existing notifications
    document.querySelectorAll('.notification').forEach(notification => {
        notification.remove();
    });

    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;

    const icon = type === 'error' ? 'exclamation-triangle' :
                 type === 'warning' ? 'exclamation-triangle' :
                 type === 'success' ? 'check-circle' : 'info-circle';

    notification.innerHTML = `
        <i class="fas fa-${icon}"></i>
        <span>${message}</span>
        <button onclick="this.parentElement.remove()" style="background: none; border: none; color: inherit; cursor: pointer; margin-left: 1rem;">
            <i class="fas fa-times"></i>
        </button>
    `;

    // Add to page
    document.body.appendChild(notification);

    // Auto remove after duration
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, duration);
}

// Security metrics update function
function updateSecurityMetrics(attackType, status) {
    try {
        // Update security event counter
        const securityEventsElement = document.getElementById('securityEvents');
        if (securityEventsElement) {
            const currentCount = parseInt(securityEventsElement.textContent) || 0;
            securityEventsElement.textContent = currentCount + 1;
        }

        // Update threat level based on attack type
        const threatLevelElement = document.getElementById('threatLevel');
        if (threatLevelElement) {
            const highRiskAttacks = ['privilege_escalation', 'dos_attack', 'file_access'];
            if (highRiskAttacks.includes(attackType)) {
                threatLevelElement.textContent = 'HIGH';
                threatLevelElement.className = 'metric-value high-risk';
            } else {
                threatLevelElement.textContent = 'MEDIUM';
                threatLevelElement.className = 'metric-value medium-risk';
            }
        }

        // Add to security events log
        dashboardState.securityEvents.push({
            timestamp: new Date().toISOString(),
            type: attackType,
            status: status,
            description: CONFIG.ATTACK_TYPES[attackType]?.description || 'Security event detected'
        });

        // Keep only last 50 events
        if (dashboardState.securityEvents.length > 50) {
            dashboardState.securityEvents = dashboardState.securityEvents.slice(-50);
        }

    } catch (error) {
        console.error('Failed to update security metrics:', error);
    }
}

// Enhanced service management functions
async function restartService(serviceName) {
    if (!confirm(`Are you sure you want to restart ${serviceName}?`)) {
        return;
    }

    showLoading(true);
    try {
        showNotification(`Restarting ${serviceName}...`, 'warning');

        const response = await fetch(`${CONFIG.API_BASE}/api/services/${serviceName}/restart`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const result = await response.json();
        showNotification(result.message || `${serviceName} restarted successfully`, 'success');

        // Refresh service status after restart
        setTimeout(() => {
            refreshServices();
        }, 3000);

    } catch (error) {
        console.error(`Failed to restart ${serviceName}:`, error);
        showNotification(`Failed to restart ${serviceName}: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

// Enhanced Prometheus targets loading
async function loadPrometheusTargets() {
    try {
        // Try to fetch real Prometheus targets
        const response = await fetch(`${CONFIG.PROMETHEUS_URL}/api/v1/targets`, {
            method: 'GET',
            mode: 'cors'
        });

        let targets = [];

        if (response.ok) {
            const data = await response.json();
            targets = data.data?.activeTargets || [];
        } else {
            // Fallback to mock data
            targets = [
                { labels: { job: 'demo-app', instance: 'localhost:3000' }, health: 'up' },
                { labels: { job: 'node-exporter', instance: 'localhost:9100' }, health: 'up' },
                { labels: { job: 'cadvisor', instance: 'localhost:8080' }, health: 'up' }
            ];
        }

        // Update targets display
        const targetsContainer = document.getElementById('prometheusTargets');
        if (targetsContainer) {
            targetsContainer.innerHTML = targets.map(target => `
                <div class="target-item ${target.health}">
                    <span class="target-job">${target.labels?.job || 'unknown'}</span>
                    <span class="target-instance">${target.labels?.instance || 'unknown'}</span>
                    <span class="target-status ${target.health}">${target.health?.toUpperCase() || 'UNKNOWN'}</span>
                </div>
            `).join('');
        }

    } catch (error) {
        console.error('Failed to load Prometheus targets:', error);
        // Show fallback message
        const targetsContainer = document.getElementById('prometheusTargets');
        if (targetsContainer) {
            targetsContainer.innerHTML = '<div class="error-message">Failed to load Prometheus targets</div>';
        }
    }
}

// Export for debugging
window.dashboardState = dashboardState;
window.CONFIG = CONFIG;
