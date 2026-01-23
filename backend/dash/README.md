# Chemistry Dashboard

A real-time web dashboard for managing and monitoring the Chemistry API server.

## Features

- **Server Control**: Start, stop, and restart the API server with one click
- **Real-time Monitoring**: View CPU, memory usage, and uptime
- **Live Terminal**: See server logs in real-time via WebSocket
- **Command Execution**: Execute custom commands directly from the dashboard
- **Reverse Proxy Ready**: Configured for deployment at dash.salsoftware.online

## Setup

1. Install dependencies:
```bash
cd /workspaces/Chemistry/backend/dash
pip install -r requirements.txt
```

2. Run the dashboard server:
```bash
uvicorn dashboard_api:app --host 0.0.0.0 --port 8001 --reload
```

3. Access the dashboard at http://localhost:8001
   - Username: `admin`
   - Password: `chemistry2026`
   - ⚠️ Change these in production! See [CREDENTIALS.md](CREDENTIALS.md)

## Reverse Proxy Configuration

### Nginx Configuration

For deploying to dash.salsoftware.online, use this nginx configuration:

```nginx
server {
    listen 80;
    server_name dash.salsoftware.online;

    location / {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /ws {
        proxy_pass http://localhost:8001/ws;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;
    }
}
```

For HTTPS (recommended):
```bash
sudo certbot --nginx -d dash.salsoftware.online
```

### Apache Configuration

```apache
<VirtualHost *:80>
    ServerName dash.salsoftware.online
    
    ProxyPreserveHost On
    ProxyPass / http://localhost:8001/
    ProxyPassReverse / http://localhost:8001/
    
    # WebSocket support
    RewriteEngine on
    RewriteCond %{HTTP:Upgrade} websocket [NC]
    RewriteCond %{HTTP:Connection} upgrade [NC]
    RewriteRule ^/?(.*) "ws://localhost:8001/$1" [P,L]
</VirtualHost>
```

## API Endpoints

- `GET /` - Dashboard web interface
- `GET /api/status` - Get server status and process info
- `POST /api/start` - Start the API server
- `POST /api/stop` - Stop the API server
- `POST /api/restart` - Restart the API server
- `POST /api/command` - Execute custom command
- `GET /api/logs?lines=100` - Get recent log lines
- `WS /ws` - WebSocket for real-time logs
- `GET /health` - Health check endpoint

## Dashboard Features

### Server Controls
- **Start**: Launches the API server on port 8000
- **Stop**: Gracefully stops the running server
- **Restart**: Stops and restarts the server
- **Refresh**: Updates server status and metrics

### Process Information
Real-time monitoring of:
- Process ID (PID)
- CPU usage percentage
- Memory consumption
- Server uptime

### Live Terminal
- Real-time log streaming via WebSocket
- Command execution interface
- Terminal history (last 1000 lines)
- Auto-scroll and color-coded output

## Security Notes

When deploying to production:

1. Add authentication to the dashboard endpoints
2. Use HTTPS/WSS for all connections
3. Restrict access via firewall rules
4. Set up proper logging and monitoring
5. Use environment variables for sensitive configuration

## Troubleshooting

### WebSocket Not Connecting
- Ensure reverse proxy is configured for WebSocket upgrades
- Check firewall rules allow WebSocket connections
- Verify the dashboard server is running

### Server Won't Start
- Check if port 8000 is already in use
- Verify the API directory path in dashboard_api.py
- Ensure all dependencies are installed

### Commands Fail
- Verify the working directory is correct
- Check file permissions
- Review command syntax

## Running in Production

Use a process manager like systemd:

```ini
[Unit]
Description=Chemistry Dashboard
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/workspaces/Chemistry/backend/dash
Environment="PATH=/usr/bin"
ExecStart=/usr/bin/uvicorn dashboard_api:app --host 0.0.0.0 --port 8001
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable chemistry-dashboard
sudo systemctl start chemistry-dashboard
```
