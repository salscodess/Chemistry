# 🧪 Chemistry

AI-powered command execution system with intelligent routing between cloud and local processing.

## Overview

Chemistry is a hybrid AI system that accepts commands via a Windows hotkey (ALT+0), processes them through intelligent routing, and executes them either locally or in the cloud based on task requirements.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│  Windows Client (ALT+0)                             │
│  └─> GUI → Prompt → POST to API                    │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│  api.salsoftware.online                             │
│  ├─> MainRoute (Classify Request)                   │
│  ├─> /api/cloud    (Cloud Processing)              │
│  ├─> /api/hybrid   (Hybrid Processing)             │
│  └─> /api/local    (Local Processing)              │
└─────────────────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│  dash.salsoftware.online                            │
│  └─> Server Management Dashboard                    │
│      • Start/Stop/Restart API                       │
│      • Monitor Resources (CPU, Memory)              │
│      • Live Terminal Output                         │
│      • Execute Commands                             │
└─────────────────────────────────────────────────────┘
```

## ✅ Completed Features

### Backend API (Port 8000)
- ✅ FastAPI routing system
- ✅ CORS configured for api.salsoftware.online
- ✅ Main routing endpoint (`/api/route`)
- ✅ Cloud processing route (`/api/cloud`)
- ✅ Hybrid processing route (`/api/hybrid`)
- ✅ Local processing route (`/api/local`)
- ✅ Health check and status endpoints

### Dashboard (Port 8001)
- ✅ Real-time server management
- ✅ Start/Stop/Restart controls
- ✅ Process monitoring (PID, CPU, Memory, Uptime)
- ✅ Live terminal with WebSocket streaming
- ✅ Command execution interface
- ✅ CORS configured for dash.salsoftware.online
- ✅ Reverse proxy ready (nginx config included)

## Quick Start

### 🚀 Start Everything

```bash
cd /workspaces/Chemistry
./start.sh
```

Then visit: http://localhost:8001

### 📦 Manual Installation

**Dashboard:**
```bash
cd /workspaces/Chemistry/backend/dash
pip install -r requirements.txt
uvicorn dashboard_api:app --host 0.0.0.0 --port 8001
```

**Default Login:**
- Username: `admin`
- Password: `chemistry2026`

⚠️ Change these credentials in production! See [backend/dash/CREDENTIALS.md](backend/dash/CREDENTIALS.md)

**API Server** (start from dashboard or manually):
```bash
cd /workspaces/Chemistry/backend/api
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

## API Usage

### Route a Request
```bash
curl -X POST http://localhost:8000/api/route \
  -H "Content-Type: application/json" \
  -d '{
    "route_type": "cloud",
    "action": "analyze",
    "data": {"sample": "test"}
  }'
```

### Get Routing Information
```bash
curl http://localhost:8000/api/info
```

### Cloud Processing
```bash
curl -X POST http://localhost:8000/api/cloud/process \
  -H "Content-Type: application/json" \
  -d '{"action": "analyze", "data": {}}'
```

### Hybrid Processing
```bash
curl -X POST http://localhost:8000/api/hybrid/process \
  -H "Content-Type: application/json" \
  -d '{"action": "compute", "data": {}, "prefer_cloud": true}'
```

## Dashboard Features

- **Server Control**: Start, stop, restart the API server with one click
- **Real-time Monitoring**: View CPU, memory usage, and uptime
- **Live Terminal**: Stream server logs in real-time via WebSocket
- **Command Execution**: Run custom commands directly from the dashboard
- **Auto-refresh**: Status updates every 5 seconds

## Production Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete deployment instructions including:
- Nginx reverse proxy configuration
- SSL/TLS setup with Let's Encrypt
- Systemd service configuration
- DNS configuration
- Security considerations

## Project Structure

```
Chemistry/
├── backend/
│   ├── api/                      # Main API Server
│   │   ├── main.py              # FastAPI application
│   │   ├── routes/
│   │   │   ├── MainRoute.py     # Main router with routing logic
│   │   │   ├── cloud/           # Cloud processing endpoints
│   │   │   ├── hybrid/          # Hybrid processing endpoints
│   │   │   └── local/           # Local processing endpoints
│   │   ├── requirements.txt
│   │   └── README.md
│   └── dash/                     # Management Dashboard
│       ├── dashboard_api.py     # Dashboard backend API
│       ├── index.html           # Dashboard frontend
│       ├── nginx.conf           # Nginx configuration
│       ├── requirements.txt
│       └── README.md
├── frontend/                     # Desktop client (Windows + Linux)
│   ├── chemistry_desktop/       # Desktop app package
│   ├── scripts/                 # OS launch/install scripts
│   ├── build/                   # PyInstaller build scripts
│   ├── desktop_client.py        # Python entrypoint
│   ├── requirements.txt
│   └── setup.md
├── start.sh                     # Quick start script
├── DEPLOYMENT.md                # Production deployment guide
└── README.md
```

## Planned Features

### Frontend (Desktop Client)
- [x] Cross-platform desktop GUI client (Tkinter)
- [x] ALT+0 shortcut to trigger routed requests
- [x] POST requests to `/api/route` and route `/process` endpoints
- [x] Response display with JSON formatting
- [x] Windows launcher and PyInstaller build support
- [x] Linux launcher script and desktop entry installer
- [x] Always-on-top mode with compact mini-bar and animated status UI

### Backend Enhancements
- [ ] User authentication with password protection
- [ ] MySQL database for data storage
- [ ] Local AI for prompt interpretation (llama-models)
- [ ] Advanced hybrid routing logic
- [ ] Command/script management via dashboard
- [ ] User management system

## Desktop Workflow

```
User Input (ALT+0 or button)
    ↓
Desktop GUI (Windows/Linux)
    ↓
POST to api.salsoftware.online/api/route
    ↓
AI Task Classification
    ↓
Hybrid Decision (Local vs Cloud)
    ↓
Execute Task
    ↓
Return Response to GUI
```

## Environment URLs

- **Dashboard**: dash.salsoftware.online (reverse proxy)
- **API**: api.salsoftware.online/api/route
- **Response**: api.salsoftware.online/answ

## Technologies

- **Backend**: FastAPI, Python 3.12
- **Frontend**: HTML/CSS/JavaScript (Dashboard), Python Tkinter desktop client (Windows + Linux)
- **Server**: Uvicorn, WebSockets
- **Reverse Proxy**: Nginx
- **AI**: llama-models (planned)
- **Database**: MySQL (planned)
- **Deployment**: Linux, Systemd

## Development

### Backend Shortcuts

For faster local backend setup and startup:

```bash
cd backend
./build.sh   # create venv + install API and dashboard requirements
./start.sh   # launch API on :8000 and dashboard on :8001
```

Logs are written to:
- `/tmp/chemistry-api.log`
- `/tmp/chemistry-dashboard.log`

### Adding New Routes

1. Create route file in appropriate directory:
   - `backend/api/routes/cloud/` for cloud routes
   - `backend/api/routes/hybrid/` for hybrid routes
   - `backend/api/routes/local/` for local routes

2. Import and include in [backend/api/routes/MainRoute.py](backend/api/routes/MainRoute.py)

3. Update routing logic if needed

### Testing

API Documentation (Swagger):
- API: http://localhost:8000/docs
- Dashboard: http://localhost:8001/docs

## Links & Resources

- [PyInstaller](https://pypi.org/project/pyinstaller/) - Windows .exe creation
- [Cloudflare Dash](https://dash.cloudflare.com)
- [llama-models](https://pypi.org/project/llama-models/) - Local AI

## License

See [LICENSE](LICENSE)

## Contributing

Contributions welcome! Please open an issue or submit a pull request.


