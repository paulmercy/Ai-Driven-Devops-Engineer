from fastapi import FastAPI, HTTPException, BackgroundTasks
from contextlib import asynccontextmanager
from fastapi.responses import PlainTextResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST, CollectorRegistry
import time
import random
import logging
import os
import json
from datetime import datetime, timedelta
import asyncio
import psutil
import uvicorn

# Pydantic models
class AttackRequest(BaseModel):
    type: str
    description: str = ""

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create custom registry to avoid conflicts
registry = CollectorRegistry()

# Prometheus metrics with custom registry
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'], registry=registry)
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration', registry=registry)
ACTIVE_CONNECTIONS = Gauge('active_connections', 'Number of active connections', registry=registry)
CPU_USAGE = Gauge('cpu_usage_percent', 'CPU usage percentage', registry=registry)
MEMORY_USAGE = Gauge('memory_usage_bytes', 'Memory usage in bytes', registry=registry)
SUSPICIOUS_ACTIVITY = Counter('suspicious_activity_total', 'Total suspicious activities detected', ['type'], registry=registry)
ATTACK_COUNTER = Counter('attack_simulations_total', 'Total attack simulations performed', registry=registry)

# Background task for system metrics
async def update_system_metrics():
    """Background task to update system metrics"""
    while True:
        try:
            # Update CPU and memory metrics
            CPU_USAGE.set(psutil.cpu_percent())
            memory = psutil.virtual_memory()
            MEMORY_USAGE.set(memory.used)

            # Simulate active connections
            ACTIVE_CONNECTIONS.set(random.randint(10, 50))

            await asyncio.sleep(5)  # Update every 5 seconds
        except Exception as e:
            logger.error(f"Error updating system metrics: {e}")
            await asyncio.sleep(5)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("DevSecOps Demo Microservice starting up...")
    # Start background task for system metrics
    task = asyncio.create_task(update_system_metrics())
    yield
    # Shutdown
    task.cancel()
    logger.info("DevSecOps Demo Microservice shutting down...")

app = FastAPI(
    title="DevSecOps Demo Microservice",
    description="A demo microservice with Prometheus metrics and security monitoring",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware for UI integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for UI
ui_path = "/app/ui"  # Direct path since we mount it in docker-compose
if os.path.exists(ui_path):
    app.mount("/ui", StaticFiles(directory=ui_path), name="ui")
    logger.info(f"UI mounted at /ui from {ui_path}")
else:
    logger.warning(f"UI directory not found at {ui_path}")

# In-memory storage for demo
users_db = {}
sessions = {}

@app.middleware("http")
async def metrics_middleware(request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    # Record metrics
    duration = time.time() - start_time
    REQUEST_DURATION.observe(duration)
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    # Log request
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {duration:.3f}s")
    
    return response



@app.get("/")
async def root():
    return {
        "message": "DevSecOps Demo Microservice",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "endpoints": [
            "/health",
            "/metrics",
            "/api/users",
            "/api/login",
            "/api/data",
            "/api/admin",
            "/simulate/attack",
            "/dashboard"
        ]
    }

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """Serve the DevSecOps Dashboard UI"""
    ui_path = "/app/ui/index.html"  # Direct path since we mount it in docker-compose
    if os.path.exists(ui_path):
        with open(ui_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    else:
        return HTMLResponse(content="""
        <html>
            <head><title>DevSecOps Dashboard</title></head>
            <body>
                <h1>DevSecOps Dashboard</h1>
                <p>Dashboard UI files not found. Please ensure the UI directory exists.</p>
                <p>Available endpoints:</p>
                <ul>
                    <li><a href="/health">Health Check</a></li>
                    <li><a href="/metrics">Prometheus Metrics</a></li>
                    <li><a href="/api/security-status">Security Status</a></li>
                </ul>
            </body>
        </html>
        """, status_code=404)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime": time.time()
    }

@app.get("/metrics", response_class=PlainTextResponse)
async def metrics():
    return generate_latest(registry)

@app.post("/api/users")
async def create_user(user_data: dict):
    user_id = len(users_db) + 1
    users_db[user_id] = {
        "id": user_id,
        "username": user_data.get("username"),
        "email": user_data.get("email"),
        "created_at": datetime.now().isoformat()
    }
    logger.info(f"User created: {user_id}")
    return {"user_id": user_id, "message": "User created successfully"}

@app.post("/api/login")
async def login(credentials: dict):
    username = credentials.get("username")
    password = credentials.get("password")
    
    # Simulate authentication
    if username and password:
        session_id = f"session_{random.randint(1000, 9999)}"
        sessions[session_id] = {
            "username": username,
            "login_time": datetime.now().isoformat()
        }
        logger.info(f"User logged in: {username}")
        return {"session_id": session_id, "message": "Login successful"}
    else:
        SUSPICIOUS_ACTIVITY.labels(type="failed_login").inc()
        logger.warning(f"Failed login attempt for username: {username}")
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/api/data")
async def get_data():
    # Simulate data processing
    processing_time = random.uniform(0.1, 2.0)
    await asyncio.sleep(processing_time)
    
    return {
        "data": [{"id": i, "value": random.randint(1, 100)} for i in range(10)],
        "processing_time": processing_time,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/admin")
async def admin_endpoint():
    # This endpoint simulates admin access
    logger.warning("Admin endpoint accessed - potential security concern")
    SUSPICIOUS_ACTIVITY.labels(type="admin_access").inc()
    
    return {
        "message": "Admin access granted",
        "users": list(users_db.values()),
        "sessions": sessions
    }

@app.post("/simulate/attack")
async def simulate_attack(attack_data: dict):
    """Simulate various attack scenarios for demo purposes"""
    attack = attack_data.get("type", "generic")
    
    if attack == "sql_injection":
        SUSPICIOUS_ACTIVITY.labels(type="sql_injection").inc()
        logger.critical("SQL injection attempt detected!")
        
    elif attack == "privilege_escalation":
        SUSPICIOUS_ACTIVITY.labels(type="privilege_escalation").inc()
        logger.critical("Privilege escalation attempt detected!")
        
    elif attack == "file_access":
        SUSPICIOUS_ACTIVITY.labels(type="unauthorized_file_access").inc()
        logger.critical("Unauthorized file access attempt detected!")
        
    elif attack == "network_scan":
        SUSPICIOUS_ACTIVITY.labels(type="network_scan").inc()
        logger.warning("Network scanning activity detected!")
        
    else:
        SUSPICIOUS_ACTIVITY.labels(type="unknown").inc()
        logger.warning(f"Unknown suspicious activity: {attack}")
    
    return {
        "message": f"Simulated {attack} attack",
        "timestamp": datetime.now().isoformat(),
        "alert_triggered": True
    }

@app.get("/api/stress")
async def stress_test():
    """Endpoint to generate load for testing"""
    # Simulate CPU intensive task
    start = time.time()
    while time.time() - start < 1:
        _ = sum(i * i for i in range(1000))

    return {"message": "Stress test completed", "duration": time.time() - start}

@app.post("/webhook/alerts")
async def receive_alerts(alert_data: dict):
    """Webhook endpoint for receiving Prometheus alerts"""
    logger.info(f"Received alert: {alert_data}")

    # Process alerts and potentially trigger responses
    if alert_data.get("status") == "firing":
        alert_name = alert_data.get("groupLabels", {}).get("alertname", "Unknown")
        logger.warning(f"Alert firing: {alert_name}")

        # Increment suspicious activity counter for security alerts
        if "security" in alert_data.get("commonLabels", {}).get("category", ""):
            SUSPICIOUS_ACTIVITY.labels(type="alert_triggered").inc()

    return {"status": "received", "timestamp": datetime.now().isoformat()}

@app.get("/api/container-info")
async def get_container_info():
    """Get container and system information"""
    try:
        import socket
        hostname = socket.gethostname()

        # Get basic system info
        cpu_count = psutil.cpu_count()
        memory_info = psutil.virtual_memory()
        disk_info = psutil.disk_usage('/')

        return {
            "hostname": hostname,
            "cpu_count": cpu_count,
            "memory_total_gb": round(memory_info.total / (1024**3), 2),
            "memory_available_gb": round(memory_info.available / (1024**3), 2),
            "disk_total_gb": round(disk_info.total / (1024**3), 2),
            "disk_free_gb": round(disk_info.free / (1024**3), 2),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting container info: {e}")
        raise HTTPException(status_code=500, detail="Failed to get container info")

@app.get("/api/security-status")
async def get_security_status():
    """Get current security status and metrics"""
    try:
        # Get recent suspicious activity counts
        current_time = time.time()

        return {
            "status": "monitoring",
            "active_sessions": len(sessions),
            "total_users": len(users_db),
            "monitoring_enabled": True,
            "last_check": datetime.now().isoformat(),
            "security_features": [
                "Falco runtime monitoring",
                "Prometheus metrics collection",
                "Real-time alerting",
                "Container security scanning",
                "Network monitoring"
            ]
        }
    except Exception as e:
        logger.error(f"Error getting security status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get security status")

# Enhanced API endpoints for dashboard functionality

@app.get("/api/simulate/attack/test")
async def test_attack_simple():
    """Simple test endpoint"""
    return {"status": "test_works", "message": "API is working"}

@app.get("/api/simulate/attack")
async def simulate_attack_get(attack_type: str = "generic", description: str = ""):
    """GET endpoint for attack simulation (fallback)"""
    if not description:
        description = f"{attack_type} simulation"

    # Log the attack simulation
    logger.warning(f"Attack simulation: {attack_type} - {description}")

    # Update metrics based on attack type
    if attack_type == "sql_injection":
        SUSPICIOUS_ACTIVITY.labels(type="sql_injection").inc()
    elif attack_type == "xss":
        SUSPICIOUS_ACTIVITY.labels(type="xss_attack").inc()
    elif attack_type == "brute_force":
        SUSPICIOUS_ACTIVITY.labels(type="brute_force").inc()
    else:
        SUSPICIOUS_ACTIVITY.labels(type="other").inc()

    # Simulate different severity levels
    severity = "high" if attack_type in ["sql_injection", "brute_force"] else "medium"

    return {
        "status": "success",
        "attack_type": attack_type,
        "description": description,
        "message": f"Successfully simulated {attack_type} attack",
        "timestamp": datetime.now().isoformat(),
        "alert_triggered": True,
        "severity": severity
    }

@app.post("/api/simulate/attack")
async def simulate_attack_enhanced(attack_data: dict):
    """Enhanced attack simulation endpoint for dashboard"""
    attack_type = attack_data.get("type", "generic")
    description = attack_data.get("description", f"{attack_type} simulation")

    # Log the attack simulation
    logger.warning(f"Attack simulation: {attack_type} - {description}")

    # Update metrics based on attack type
    if attack_type == "sql_injection":
        SUSPICIOUS_ACTIVITY.labels(type="sql_injection").inc()
    elif attack_type == "xss_attack":
        SUSPICIOUS_ACTIVITY.labels(type="xss_attack").inc()
    elif attack_type == "brute_force":
        SUSPICIOUS_ACTIVITY.labels(type="brute_force").inc()
    elif attack_type == "dos_attack":
        SUSPICIOUS_ACTIVITY.labels(type="dos_attack").inc()
    elif attack_type == "privilege_escalation":
        SUSPICIOUS_ACTIVITY.labels(type="privilege_escalation").inc()
    elif attack_type == "file_access":
        SUSPICIOUS_ACTIVITY.labels(type="unauthorized_file_access").inc()
    else:
        SUSPICIOUS_ACTIVITY.labels(type="unknown").inc()

    # Increment general attack counter
    ATTACK_COUNTER.inc()

    return {
        "status": "success",
        "attack_type": attack_type,
        "description": description,
        "message": f"Successfully simulated {attack_type} attack",
        "timestamp": datetime.now().isoformat(),
        "alert_triggered": True,
        "severity": "high" if attack_type in ["privilege_escalation", "dos_attack"] else "medium"
    }

@app.post("/api/services/start-all")
async def start_all_services():
    """Start all Docker Compose services"""
    try:
        # In a real implementation, this would call docker-compose up
        logger.info("Starting all services via Docker Compose")

        # Simulate service startup
        await asyncio.sleep(1)

        return {
            "status": "success",
            "message": "All services started successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to start services: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start services: {str(e)}")

@app.post("/api/services/stop-all")
async def stop_all_services():
    """Stop all Docker Compose services"""
    try:
        # In a real implementation, this would call docker-compose down
        logger.info("Stopping all services via Docker Compose")

        # Simulate service shutdown
        await asyncio.sleep(1)

        return {
            "status": "success",
            "message": "All services stopped successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to stop services: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to stop services: {str(e)}")

@app.post("/api/services/restart-all")
async def restart_all_services():
    """Restart all Docker Compose services"""
    try:
        # In a real implementation, this would call docker-compose restart
        logger.info("Restarting all services via Docker Compose")

        # Simulate service restart
        await asyncio.sleep(2)

        return {
            "status": "success",
            "message": "All services restarted successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to restart services: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to restart services: {str(e)}")

@app.post("/api/services/{service_name}/restart")
async def restart_service(service_name: str):
    """Restart a specific service"""
    try:
        # In a real implementation, this would call docker-compose restart <service>
        logger.info(f"Restarting service: {service_name}")

        # Simulate service restart
        await asyncio.sleep(1)

        return {
            "status": "success",
            "message": f"Service {service_name} restarted successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to restart service {service_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to restart service: {str(e)}")

@app.get("/api/logs")
async def get_system_logs():
    """Get system logs from all services"""
    try:
        # In a real implementation, this would fetch logs from Docker containers
        # For now, return mock logs with recent timestamps
        logs = [
            {
                "timestamp": datetime.now().isoformat(),
                "level": "info",
                "source": "demo-app",
                "message": "Health check endpoint accessed"
            },
            {
                "timestamp": (datetime.now() - timedelta(minutes=1)).isoformat(),
                "level": "info",
                "source": "prometheus",
                "message": "Metrics scraped successfully"
            },
            {
                "timestamp": (datetime.now() - timedelta(minutes=2)).isoformat(),
                "level": "warning",
                "source": "falco",
                "message": "Suspicious file access detected"
            },
            {
                "timestamp": (datetime.now() - timedelta(minutes=3)).isoformat(),
                "level": "info",
                "source": "grafana",
                "message": "Dashboard server running"
            },
            {
                "timestamp": (datetime.now() - timedelta(minutes=5)).isoformat(),
                "level": "alert",
                "source": "security",
                "message": "Attack simulation detected and blocked"
            }
        ]

        return {
            "status": "success",
            "logs": logs,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get logs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get logs: {str(e)}")

if __name__ == "__main__":
    # Ensure logs directory exists
    os.makedirs("/app/logs", exist_ok=True)

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=3000,
        log_level="info",
        access_log=True
    )
