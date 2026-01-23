# Chemistry API - Deployment Guide

## Overview

This repository contains two main components:

1. **Chemistry API** (`/backend/api`) - Main FastAPI application with routing
2. **Dashboard** (`/backend/dash`) - Web-based management interface

## Architecture

```
┌─────────────────────────────────────────────┐
│  dash.salsoftware.online                    │
│  ┌──────────────────────────────────┐       │
│  │   Dashboard (Port 8001)          │       │
│  │   - Start/Stop/Restart           │       │
│  │   - Monitor (CPU, Memory, Logs)  │       │
│  │   - Execute Commands             │       │
│  └──────────────┬───────────────────┘       │
│                 │ Controls                  │
│                 ▼                           │
│  ┌──────────────────────────────────┐       │
│  │   Chemistry API (Port 8000)      │       │
│  │   - /api/cloud                   │       │
│  │   - /api/hybrid                  │       │
│  │   - /api/local                   │       │
│  └──────────────────────────────────┘       │
└─────────────────────────────────────────────┘
```

## Quick Start

### 1. API Server

```bash
cd /workspaces/Chemistry/backend/api
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

Access: http://localhost:8000/docs

### 2. Dashboard

```bash
cd /workspaces/Chemistry/backend/dash
pip install -r requirements.txt
uvicorn dashboard_api:app --host 0.0.0.0 --port 8001
```

Access: http://localhost:8001

## Production Deployment

### Step 1: Set up Nginx Reverse Proxy

```bash
# Copy nginx configuration
sudo cp /workspaces/Chemistry/backend/dash/nginx.conf /etc/nginx/sites-available/dash.salsoftware.online

# Create symlink
sudo ln -s /etc/nginx/sites-available/dash.salsoftware.online /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx
```

### Step 2: Configure SSL with Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d dash.salsoftware.online
```

### Step 3: Set up Systemd Services

**Dashboard Service** (`/etc/systemd/system/chemistry-dashboard.service`):
```ini
[Unit]
Description=Chemistry Dashboard
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/workspaces/Chemistry/backend/dash
Environment="PATH=/usr/bin"
ExecStart=/usr/bin/uvicorn dashboard_api:app --host 127.0.0.1 --port 8001
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**API Service** (`/etc/systemd/system/chemistry-api.service`):
```ini
[Unit]
Description=Chemistry API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/workspaces/Chemistry/backend/api
Environment="PATH=/usr/bin"
ExecStart=/usr/bin/uvicorn main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start services:
```bash
sudo systemctl daemon-reload
sudo systemctl enable chemistry-dashboard
sudo systemctl enable chemistry-api
sudo systemctl start chemistry-dashboard
sudo systemctl start chemistry-api
```

### Step 4: DNS Configuration

Point your domain to the server:
```
Type: A
Name: dash.salsoftware.online
Value: YOUR_SERVER_IP
TTL: 300
```

## Dashboard Features

### Server Control
- **Start**: Launch the API server
- **Stop**: Gracefully shutdown the API server
- **Restart**: Stop and start the API server
- **Refresh**: Update status metrics

### Real-time Monitoring
- Process ID (PID)
- CPU Usage (%)
- Memory Usage (MB)
- Server Uptime

### Live Terminal
- Real-time log streaming via WebSocket
- Command execution interface
- Terminal history (1000 lines)
- Auto-scrolling output

### Custom Commands
Execute commands directly:
- `pip list` - List installed packages
- `ls -la` - List files
- `cat main.py` - View file contents
- `git status` - Check git status

## API Endpoints

### Main API (Port 8000)
- `GET /` - API information
- `GET /health` - Health check
- `GET /api/info` - Routing information
- `POST /api/route` - Main routing endpoint
- `GET|POST /api/cloud/*` - Cloud endpoints
- `GET|POST /api/hybrid/*` - Hybrid endpoints
- `GET|POST /api/local/*` - Local endpoints

### Dashboard API (Port 8001)
- `GET /` - Dashboard web interface
- `GET /api/status` - Server status
- `POST /api/start` - Start server
- `POST /api/stop` - Stop server
- `POST /api/restart` - Restart server
- `POST /api/command` - Execute command
- `WS /ws` - WebSocket for logs

## Security Considerations

1. **Authentication**: Add authentication middleware to protect dashboard
2. **Firewall**: Only expose ports 80/443, block 8000/8001 directly
3. **SSL/TLS**: Always use HTTPS in production
4. **Command Execution**: Restrict allowed commands or disable in production
5. **CORS**: Update allowed origins in both apps
6. **Rate Limiting**: Add rate limiting to prevent abuse

## Monitoring & Logs

View service logs:
```bash
sudo journalctl -u chemistry-dashboard -f
sudo journalctl -u chemistry-api -f
```

Check service status:
```bash
sudo systemctl status chemistry-dashboard
sudo systemctl status chemistry-api
```

## Troubleshooting

### Dashboard won't start
```bash
# Check if port is in use
sudo lsof -i :8001

# Check logs
sudo journalctl -u chemistry-dashboard -n 50
```

### API server won't start from dashboard
- Verify paths in dashboard_api.py
- Check file permissions
- Review dashboard logs

### WebSocket not connecting
- Verify nginx WebSocket configuration
- Check browser console for errors
- Ensure firewall allows WebSocket connections

## File Structure

```
/workspaces/Chemistry/
├── backend/
│   ├── api/
│   │   ├── main.py                 # Main API application
│   │   ├── routes/
│   │   │   ├── MainRoute.py        # Main router
│   │   │   ├── cloud/CloudRoute.py
│   │   │   ├── hybrid/cloud_localRoute.py
│   │   │   └── local/LocalRoute1.py
│   │   ├── requirements.txt
│   │   └── README.md
│   └── dash/
│       ├── dashboard_api.py        # Dashboard backend
│       ├── index.html              # Dashboard frontend
│       ├── nginx.conf              # Nginx configuration
│       ├── requirements.txt
│       └── README.md
└── README.md
```

## Updates & Maintenance

Pull latest changes:
```bash
cd /workspaces/Chemistry
git pull origin main
sudo systemctl restart chemistry-dashboard
sudo systemctl restart chemistry-api
```

Update dependencies:
```bash
cd /workspaces/Chemistry/backend/api && pip install -r requirements.txt --upgrade
cd /workspaces/Chemistry/backend/dash && pip install -r requirements.txt --upgrade
```
