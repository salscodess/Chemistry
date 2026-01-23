# Chemistry API

FastAPI-based routing application that accepts requests from `api.salsoftware.online` and routes them to appropriate handlers.

## Setup

1. Install dependencies:
```bash
cd /workspaces/Chemistry/backend/api
pip install -r requirements.txt
```

2. Run the server:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Main Endpoints

- `GET /` - Root endpoint with API info
- `GET /health` - Health check endpoint
- `GET /api/info` - Information about available routes

### Routing Endpoint

- `POST /api/route` - Main routing endpoint that classifies requests

**Request Format:**
```json
{
  "route_type": "cloud",
  "action": "analyze",
  "data": {...}
}
```

### Cloud Routes

- `GET /api/cloud/` - Cloud service info
- `POST /api/cloud/process` - Process cloud requests
- `GET /api/cloud/status` - Cloud service status

### Hybrid Routes

- `GET /api/hybrid/` - Hybrid service info
- `POST /api/hybrid/process` - Process hybrid requests
- `GET /api/hybrid/status` - Hybrid service status

### Local Routes

- `GET /api/local/` - Local service info
- `POST /api/local/process` - Process local requests
- `GET /api/local/status` - Local service status

## Example Usage

### Check routing info:
```bash
curl http://localhost:8000/api/info
```

### Route a request:
```bash
curl -X POST http://localhost:8000/api/route \
  -H "Content-Type: application/json" \
  -d '{
    "route_type": "cloud",
    "action": "analyze",
    "data": {"sample": "test"}
  }'
```

### Process directly on a specific route:
```bash
curl -X POST http://localhost:8000/api/cloud/process \
  -H "Content-Type: application/json" \
  -d '{
    "action": "analyze",
    "data": {"sample": "test"}
  }'
```

## CORS Configuration

The API is configured to accept requests from:
- `https://api.salsoftware.online`
- `http://api.salsoftware.online`
- `http://localhost:3000` (for local development)

## Interactive Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
