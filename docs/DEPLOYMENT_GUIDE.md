# AI Agents System - Deployment Guide

## Table of Contents
1. [Deployment Overview](#deployment-overview)
2. [Replit Deployment](#replit-deployment)
3. [Local Development](#local-development)
4. [Docker Deployment](#docker-deployment)
5. [Production Deployment](#production-deployment)
6. [Environment Configuration](#environment-configuration)
7. [Monitoring & Maintenance](#monitoring--maintenance)
8. [Troubleshooting](#troubleshooting)

## Deployment Overview

The AI Agents System supports multiple deployment strategies depending on your use case:

- **Replit Hosting** (Recommended for development/prototyping)
- **Local Development** (For development and testing)
- **Docker Containerization** (For consistent environments)
- **Production Deployment** (For scalable production use)

## Replit Deployment

### Prerequisites

- Replit account
- OpenAI API key

### Quick Deployment

1. **Fork/Import Project**:
   - Import this repository into your Replit workspace
   - Or fork from the existing Replit project

2. **Configure Environment**:
   ```bash
   # Add to Replit Secrets (recommended)
   OPENAI_API_KEY=your_openai_api_key_here
   ```

3. **Configure Run Command**:
   ```bash
   python api_server.py
   ```

4. **Start the System**:
   - Click the "Run" button in Replit
   - The system will start on port 5000 automatically

5. **Verify Deployment**:
   ```bash
   # Check system status
   GET https://your-repl-name.your-username.repl.co/health
   
   # List available agents
   GET https://your-repl-name.your-username.repl.co/agents
   ```

### Replit Configuration

#### `.replit` File Configuration
```toml
run = "python api_server.py"
language = "python3"

[nix]
channel = "stable-24_05"

[deployment]
build = ["pip", "install", "-r", "requirements.txt"]
run = ["python", "api_server.py"]

[[ports]]
localPort = 5000
externalPort = 80
exposeLocalhost = true

[env]
PYTHONUNBUFFERED = "1"
```

#### Dependencies Management
```python
# pyproject.toml is automatically managed
# Key dependencies are pre-installed:
# - fastapi, uvicorn, openai, pydantic, aiohttp
```

### Replit Secrets Management

1. **Add Secrets in Replit UI**:
   - Go to Tools > Secrets
   - Add `OPENAI_API_KEY` with your OpenAI API key
   - Optional: Add `LOG_LEVEL=INFO` for production logging

2. **Access Secrets in Code**:
   ```python
   import os
   
   OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
   LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
   ```

### Replit Deployment Features

- **Always-On**: Upgrade to keep your service running 24/7
- **Custom Domains**: Connect your own domain name
- **Auto-scaling**: Automatic scaling based on traffic
- **HTTPS**: Automatic SSL certificate provisioning
- **Monitoring**: Built-in uptime and performance monitoring

## Local Development

### Prerequisites

- Python 3.11 or higher
- pip package manager
- OpenAI API key

### Setup Steps

1. **Clone Repository**:
   ```bash
   git clone <repository-url>
   cd ai-agents-system
   ```

2. **Create Virtual Environment**:
   ```bash
   python -m venv venv
   
   # Activate virtual environment
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment**:
   ```bash
   # Create .env file
   echo "OPENAI_API_KEY=your_api_key_here" > .env
   echo "LOG_LEVEL=DEBUG" >> .env
   echo "API_PORT=5000" >> .env
   ```

5. **Run Development Server**:
   ```bash
   python api_server.py
   ```

6. **Verify Installation**:
   ```bash
   curl http://localhost:5000/health
   ```

### Development Features

#### Hot Reload (Optional)
```bash
# Install uvicorn for hot reload during development
pip install uvicorn

# Run with hot reload
uvicorn api_server:app --reload --host 0.0.0.0 --port 5000
```

#### Debug Mode
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Or set in environment
export LOG_LEVEL=DEBUG
```

## Docker Deployment

### Prerequisites

- Docker and Docker Compose
- OpenAI API key

### Docker Configuration

#### Dockerfile
```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Run application
CMD ["python", "api_server.py"]
```

#### docker-compose.yml (Standalone)
```yaml
version: '3.8'

services:
  ai-agents-api:
    build: .
    ports:
      - "5000:5000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - LOG_LEVEL=INFO
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
```

#### docker-compose.yml (With Services)
```yaml
version: '3.8'

services:
  ai-agents-api:
    build: .
    ports:
      - "5000:5000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/agents_db
      - REDIS_URL=redis://redis:6379
      - LOG_LEVEL=INFO
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=agents_db
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-db:/docker-entrypoint-initdb.d
    ports:
      - "5432:5432"
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - ai-agents-api
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

### Docker Deployment Commands

```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f ai-agents-api

# Scale API servers
docker-compose up -d --scale ai-agents-api=3

# Stop services
docker-compose down

# Rebuild after code changes
docker-compose build --no-cache
docker-compose up -d
```

## Production Deployment

### Cloud Deployment Options

#### AWS Deployment
```yaml
# AWS ECS Task Definition
{
  "family": "ai-agents-api",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "ai-agents-api",
      "image": "your-account.dkr.ecr.region.amazonaws.com/ai-agents:latest",
      "portMappings": [
        {
          "containerPort": 5000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "OPENAI_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:openai-key"
        }
      ],
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:5000/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3
      }
    }
  ]
}
```

#### Google Cloud Run
```yaml
# cloudbuild.yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/ai-agents:$COMMIT_SHA', '.']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/ai-agents:$COMMIT_SHA']
  - name: 'gcr.io/cloud-builders/gcloud'
    args: ['run', 'deploy', 'ai-agents-api', 
           '--image', 'gcr.io/$PROJECT_ID/ai-agents:$COMMIT_SHA',
           '--platform', 'managed', 
           '--region', 'us-central1',
           '--allow-unauthenticated']
```

#### Azure Container Instances
```bash
# Create resource group
az group create --name ai-agents-rg --location eastus

# Deploy container
az container create \
  --resource-group ai-agents-rg \
  --name ai-agents-api \
  --image your-registry/ai-agents:latest \
  --ports 5000 \
  --environment-variables OPENAI_API_KEY=your-key \
  --restart-policy Always
```

### Kubernetes Deployment

#### Deployment Manifest
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-agents-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ai-agents-api
  template:
    metadata:
      labels:
        app: ai-agents-api
    spec:
      containers:
      - name: ai-agents-api
        image: your-registry/ai-agents:latest
        ports:
        - containerPort: 5000
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-secrets
              key: openai-key
        livenessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 60
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 10
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: ai-agents-service
spec:
  selector:
    app: ai-agents-api
  ports:
  - port: 80
    targetPort: 5000
  type: LoadBalancer
```

### Load Balancer Configuration

#### Nginx Configuration
```nginx
upstream ai_agents_backend {
    least_conn;
    server ai-agent-1:5000;
    server ai-agent-2:5000;
    server ai-agent-3:5000;
}

server {
    listen 80;
    server_name your-domain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    location / {
        proxy_pass http://ai_agents_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    location /health {
        proxy_pass http://ai_agents_backend/health;
        access_log off;
    }
}
```

## Environment Configuration

### Environment Variables

#### Required Variables
```bash
# OpenAI API Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here

# Optional Configuration
LOG_LEVEL=INFO                    # DEBUG, INFO, WARNING, ERROR
API_PORT=5000                     # Port for the API server
API_HOST=0.0.0.0                 # Host binding (0.0.0.0 for all interfaces)
```

#### Development Variables
```bash
# Development specific
DEBUG=true
RELOAD=true
LOG_FORMAT=detailed

# Testing
TEST_MODE=false
MOCK_OPENAI=false
```

#### Production Variables
```bash
# Production specific
ENVIRONMENT=production
LOG_LEVEL=INFO
ENABLE_METRICS=true
RATE_LIMIT_ENABLED=true

# Security
SECRET_KEY=your-secret-key-for-jwt
CORS_ORIGINS=https://your-frontend-domain.com
```

### Configuration Files

#### config/settings.py
```python
import os
from typing import List

class Settings:
    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "5000"))
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "json")
    
    # Security Configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "default-secret-key")
    CORS_ORIGINS: List[str] = os.getenv("CORS_ORIGINS", "*").split(",")
    
    # Feature Flags
    ENABLE_METRICS: bool = os.getenv("ENABLE_METRICS", "false").lower() == "true"
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "false").lower() == "true"
    
    @property
    def is_development(self) -> bool:
        return os.getenv("ENVIRONMENT", "development") == "development"
    
    @property
    def is_production(self) -> bool:
        return os.getenv("ENVIRONMENT", "development") == "production"
```

## Monitoring & Maintenance

### Health Monitoring

#### Health Check Endpoint
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "uptime": get_uptime(),
        "components": {
            "openai": check_openai_connection(),
            "memory": check_memory_usage(),
            "disk": check_disk_usage()
        }
    }
```

#### Metrics Collection
```python
# Prometheus metrics
from prometheus_client import Counter, Histogram, Gauge

request_count = Counter('requests_total', 'Total requests')
response_time = Histogram('response_time_seconds', 'Response time')
active_connections = Gauge('active_connections', 'Active connections')
```

### Logging Configuration

#### Structured Logging
```python
import structlog

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)
```

### Backup and Recovery

#### Data Backup (If using database)
```bash
# Automated backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"
DB_NAME="agents_db"

# Create backup
pg_dump $DB_NAME > "$BACKUP_DIR/backup_$DATE.sql"

# Compress backup
gzip "$BACKUP_DIR/backup_$DATE.sql"

# Remove old backups (keep last 7 days)
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete
```

#### Configuration Backup
```bash
# Backup critical configuration
tar -czf config_backup_$(date +%Y%m%d).tar.gz \
    config/ \
    docker-compose.yml \
    nginx.conf \
    .env
```

## Troubleshooting

### Common Deployment Issues

#### Port Already in Use
```bash
# Find process using port 5000
lsof -i :5000
netstat -tulpn | grep :5000

# Kill process
kill -9 <PID>

# Or use different port
export API_PORT=5001
python api_server.py
```

#### OpenAI API Issues
```bash
# Test API key
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     https://api.openai.com/v1/models

# Check API quota and usage
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     https://api.openai.com/v1/usage
```

#### Memory Issues
```bash
# Monitor memory usage
top -p $(pgrep -f api_server.py)
htop

# Check Python memory usage
python -c "
import psutil
import os
process = psutil.Process(os.getpid())
print(f'Memory usage: {process.memory_info().rss / 1024 / 1024:.2f} MB')
"
```

#### Docker Issues
```bash
# Check container logs
docker logs <container-name>

# Debug container
docker exec -it <container-name> /bin/bash

# Check resource usage
docker stats <container-name>

# Rebuild without cache
docker build --no-cache -t ai-agents .
```

### Performance Issues

#### Slow Response Times
1. **Check OpenAI API latency**:
   ```bash
   curl -w "@curl-format.txt" -H "Authorization: Bearer $OPENAI_API_KEY" \
        https://api.openai.com/v1/models
   ```

2. **Monitor system resources**:
   ```bash
   htop
   iotop
   nethogs
   ```

3. **Optimize OpenAI calls**:
   ```python
   # Reduce max_tokens for faster responses
   response = await openai.chat.completions.create(
       model="gpt-4o",
       messages=messages,
       max_tokens=500,  # Reduced from 1000
       temperature=0.7
   )
   ```

#### High Memory Usage
1. **Implement conversation cleanup**:
   ```python
   # Limit conversation history
   MAX_HISTORY = 10
   if len(conversation) > MAX_HISTORY:
       conversation = conversation[-MAX_HISTORY:]
   ```

2. **Add garbage collection**:
   ```python
   import gc
   gc.collect()
   ```

### Security Issues

#### SSL Certificate Issues
```bash
# Check certificate expiration
openssl x509 -in cert.pem -text -noout | grep "Not After"

# Renew Let's Encrypt certificate
certbot renew --nginx

# Test SSL configuration
curl -vI https://your-domain.com
```

#### Rate Limiting Setup
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/agents/{agent_id}/chat")
@limiter.limit("60/minute")
async def chat_endpoint(...):
    pass
```

---

*Deployment Guide last updated: August 4, 2025*