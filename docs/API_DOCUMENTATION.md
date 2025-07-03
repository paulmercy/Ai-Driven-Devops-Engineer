# API Documentation

## 📋 Overview

This document provides comprehensive API documentation for all three projects, including endpoint specifications, request/response formats, and usage examples.

## 🚀 Project 2: AI Text Analyzer API

### Base URL: `http://localhost:8000`

#### Authentication
No authentication required for demo purposes.

#### Content Type
All requests should use `Content-Type: application/json`

### Endpoints

#### 1. Home Page
```http
GET /
```
**Description**: Returns the interactive web interface
**Response**: HTML page with text analysis interface

#### 2. Health Check
```http
GET /health
```
**Description**: Service health status
**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-06-30T12:00:00Z",
  "uptime": 1234.56
}
```

#### 3. Text Analysis
```http
POST /analyze
```
**Description**: Analyze text using C++ engine and optional GPT enhancement

**Request Body**:
```json
{
  "text": "Your text to analyze here",
  "use_gpt": true
}
```

**Response**:
```json
{
  "cpp_analysis": {
    "character_count": 52,
    "word_count": 11,
    "sentence_count": 2,
    "paragraph_count": 1,
    "unique_words": 11,
    "readability_score": 85,
    "sentiment_score": 0
  },
  "gpt_suggestions": "AI-generated improvement suggestions...",
  "analysis_id": 1
}
```

**C++ Analysis Fields**:
- `character_count`: Total characters including spaces
- `word_count`: Number of words
- `sentence_count`: Number of sentences (based on punctuation)
- `paragraph_count`: Number of paragraphs
- `unique_words`: Count of unique words (case-insensitive)
- `readability_score`: Flesch-like readability score (0-100)
- `sentiment_score`: Basic sentiment analysis (-∞ to +∞)

#### 4. Store Analysis
```http
POST /store
```
**Description**: Store analysis result (alias for /analyze)

**Request/Response**: Same as `/analyze`

#### 5. Database Contents
```http
GET /database
```
**Description**: Retrieve stored analysis history

**Response**:
```json
[
  [
    1,
    "Sample text",
    "{\"word_count\": 2, \"character_count\": 11, ...}",
    "GPT suggestions...",
    "2025-06-30T12:00:00Z"
  ]
]
```

**Array Fields**: `[id, text, cpp_result_json, gpt_suggestions, timestamp]`

### Error Responses

#### 400 Bad Request
```json
{
  "detail": "Validation error message"
}
```

#### 500 Internal Server Error
```json
{
  "detail": "Internal server error description"
}
```

### Usage Examples

#### cURL Examples
```bash
# Basic analysis
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world!", "use_gpt": false}'

# With GPT enhancement
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{"text": "This is a sample text for analysis.", "use_gpt": true}'

# Get database contents
curl "http://localhost:8000/database"
```

#### Python Examples
```python
import requests

# Analyze text
response = requests.post(
    "http://localhost:8000/analyze",
    json={"text": "Sample text", "use_gpt": True}
)
result = response.json()

# Get analysis history
history = requests.get("http://localhost:8000/database").json()
```

#### JavaScript Examples
```javascript
// Analyze text
const response = await fetch('http://localhost:8000/analyze', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    text: 'Sample text for analysis',
    use_gpt: true
  })
});
const result = await response.json();

// Get database contents
const history = await fetch('http://localhost:8000/database');
const data = await history.json();
```

## 🔄 Project 3: React Application

### Base URL: `http://localhost:5173`

#### Application Features
The React application provides a web interface with:
- Interactive counter component
- Todo list with CRUD operations
- Deployment information display
- Local storage persistence

#### State Management
```typescript
interface Todo {
  id: number;
  text: string;
  completed: boolean;
}

interface DeploymentInfo {
  version: string;
  buildTime: string;
  commitHash: string;
}
```

#### Local Storage API
```javascript
// Save todos
localStorage.setItem('todos', JSON.stringify(todos));

// Load todos
const savedTodos = localStorage.getItem('todos');
const todos = savedTodos ? JSON.parse(savedTodos) : [];
```

## 🛡️ Project 5: DevSecOps Dashboard APIs

### Demo Application API

#### Base URL: `http://localhost:3000`

#### 1. Application Info
```http
GET /
```
**Response**:
```json
{
  "message": "DevSecOps Demo Microservice",
  "version": "1.0.0",
  "timestamp": "2025-06-30T12:00:00Z",
  "endpoints": ["/health", "/metrics", "/api/users", ...]
}
```

#### 2. Health Check
```http
GET /health
```
**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-06-30T12:00:00Z",
  "uptime": 1234.56
}
```

#### 3. Prometheus Metrics
```http
GET /metrics
```
**Response**: Prometheus format metrics
```
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET",endpoint="/health",status="200"} 42

# HELP http_request_duration_seconds HTTP request duration
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{le="0.1"} 35
```

#### 4. User Management
```http
POST /api/users
```
**Request**:
```json
{
  "username": "testuser",
  "email": "test@example.com"
}
```

**Response**:
```json
{
  "user_id": 1,
  "message": "User created successfully"
}
```

#### 5. Authentication
```http
POST /api/login
```
**Request**:
```json
{
  "username": "testuser",
  "password": "password123"
}
```

**Response**:
```json
{
  "session_id": "session_1234",
  "message": "Login successful"
}
```

#### 6. Data Endpoint
```http
GET /api/data
```
**Response**:
```json
{
  "data": [
    {"id": 1, "value": 42},
    {"id": 2, "value": 73}
  ],
  "processing_time": 0.15,
  "timestamp": "2025-06-30T12:00:00Z"
}
```

#### 7. Admin Endpoint
```http
GET /api/admin
```
**Response**:
```json
{
  "message": "Admin access granted",
  "users": [...],
  "sessions": {...}
}
```

#### 8. Attack Simulation
```http
POST /simulate/attack
```
**Request**:
```json
{
  "type": "sql_injection"
}
```

**Attack Types**:
- `sql_injection`: Simulate SQL injection attempt
- `privilege_escalation`: Simulate privilege escalation
- `file_access`: Simulate unauthorized file access
- `network_scan`: Simulate network reconnaissance

**Response**:
```json
{
  "message": "Simulated sql_injection attack",
  "timestamp": "2025-06-30T12:00:00Z",
  "alert_triggered": true
}
```

#### 9. Stress Testing
```http
GET /api/stress
```
**Description**: Generate CPU load for testing
**Response**:
```json
{
  "message": "Stress test completed",
  "duration": 1.023
}
```

### Monitoring APIs

#### Prometheus API
**Base URL**: `http://localhost:9090`

```http
# Query metrics
GET /api/v1/query?query=http_requests_total

# Query range
GET /api/v1/query_range?query=rate(http_requests_total[5m])&start=...&end=...&step=15s

# Get targets
GET /api/v1/targets

# Get alerts
GET /api/v1/alerts
```

#### Grafana API
**Base URL**: `http://localhost:3001`

```http
# Get dashboards (requires authentication)
GET /api/dashboards/home

# Get datasources
GET /api/datasources

# Health check
GET /api/health
```

### Security Event Format

#### Falco Events
```json
{
  "output": "Suspicious network activity detected (user=root command=curl http://example.com container=demo-app)",
  "priority": "Warning",
  "rule": "Suspicious Network Activity",
  "time": "2025-06-30T12:00:00.000000000Z",
  "output_fields": {
    "container.name": "demo-app",
    "proc.cmdline": "curl http://example.com",
    "user.name": "root"
  }
}
```

### Rate Limiting

#### Application Limits
- Default: 100 requests/minute per IP
- Burst: 10 requests/second
- Admin endpoints: 10 requests/minute

#### Monitoring Limits
- Prometheus scraping: 5-second intervals
- Grafana queries: No explicit limits
- Falco events: Real-time streaming

### Error Handling

#### Standard Error Response
```json
{
  "detail": "Error description",
  "timestamp": "2025-06-30T12:00:00Z",
  "path": "/api/endpoint",
  "status_code": 400
}
```

#### Common HTTP Status Codes
- `200`: Success
- `400`: Bad Request (validation error)
- `401`: Unauthorized
- `404`: Not Found
- `429`: Too Many Requests
- `500`: Internal Server Error

### SDK Examples

#### Python SDK Example
```python
import requests

class DevSecOpsClient:
    def __init__(self, base_url="http://localhost:3000"):
        self.base_url = base_url
    
    def analyze_text(self, text, use_gpt=True):
        response = requests.post(
            f"{self.base_url}/analyze",
            json={"text": text, "use_gpt": use_gpt}
        )
        return response.json()
    
    def simulate_attack(self, attack_type):
        response = requests.post(
            f"{self.base_url}/simulate/attack",
            json={"type": attack_type}
        )
        return response.json()
```

#### JavaScript SDK Example
```javascript
class DevSecOpsClient {
  constructor(baseUrl = 'http://localhost:3000') {
    this.baseUrl = baseUrl;
  }
  
  async analyzeText(text, useGpt = true) {
    const response = await fetch(`${this.baseUrl}/analyze`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({text, use_gpt: useGpt})
    });
    return response.json();
  }
  
  async simulateAttack(attackType) {
    const response = await fetch(`${this.baseUrl}/simulate/attack`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({type: attackType})
    });
    return response.json();
  }
}
