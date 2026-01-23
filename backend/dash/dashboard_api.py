from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, status, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import psutil
import asyncio
import os
import signal
from datetime import datetime
from typing import Optional, List
import json
import secrets

app = FastAPI(title="Chemistry Dashboard API", version="1.0.0")

# Security
security = HTTPBasic()

# Dashboard credentials (change these!)
DASHBOARD_USERNAME = "admin"
DASHBOARD_PASSWORD = "chemistry"  # Change this in production!

# Store credentials in a mutable dict for runtime changes
credentials_store = {
    "username": DASHBOARD_USERNAME,
    "password": DASHBOARD_PASSWORD
}

# Configure CORS for reverse proxy
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://dash.salsoftware.online",
        "http://dash.salsoftware.online",
        "http://localhost:3000",
        "http://localhost:8001"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store server process information
server_state = {
    "pid": None,
    "status": "stopped",
    "started_at": None,
    "log_lines": [],
    "max_log_lines": 1000
}

# WebSocket connections
active_connections: List[WebSocket] = []

def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    """Verify username and password"""
    correct_username = secrets.compare_digest(credentials.username, credentials_store["username"])
    correct_password = secrets.compare_digest(credentials.password, credentials_store["password"])
    
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

class ServerManager:
    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self.api_path = "/workspaces/Chemistry/backend/api"
        
    def get_process_info(self):
        """Get information about the running server process"""
        if server_state["pid"]:
            try:
                proc = psutil.Process(server_state["pid"])
                return {
                    "pid": server_state["pid"],
                    "status": proc.status(),
                    "cpu_percent": proc.cpu_percent(),
                    "memory_mb": proc.memory_info().rss / 1024 / 1024,
                    "started_at": server_state["started_at"]
                }
            except psutil.NoSuchProcess:
                server_state["pid"] = None
                server_state["status"] = "stopped"
                return None
        return None
    
    async def start_server(self, host="0.0.0.0", port=8000):
        """Start the FastAPI server"""
        if server_state["pid"]:
            # Check if process is actually running
            try:
                proc = psutil.Process(server_state["pid"])
                if proc.is_running():
                    raise HTTPException(status_code=400, detail="Server is already running")
            except psutil.NoSuchProcess:
                server_state["pid"] = None
        
        try:
            cmd = ["uvicorn", "main:app", "--host", host, "--port", str(port)]
            self.process = subprocess.Popen(
                cmd,
                cwd=self.api_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            server_state["pid"] = self.process.pid
            server_state["status"] = "running"
            server_state["started_at"] = datetime.now().isoformat()
            
            # Start background task to read output
            asyncio.create_task(self.read_output())
            
            return {
                "status": "success",
                "message": "Server started",
                "pid": self.process.pid
            }
        except Exception as e:
            server_state["pid"] = None
            server_state["status"] = "stopped"
            raise HTTPException(status_code=500, detail=str(e))
    
    async def stop_server(self):
        """Stop the FastAPI server"""
        if not server_state["pid"]:
            raise HTTPException(status_code=400, detail="Server is not running")
        
        try:
            # Try graceful shutdown first
            try:
                proc = psutil.Process(server_state["pid"])
                proc.terminate()
                # Wait up to 5 seconds for graceful shutdown
                proc.wait(timeout=5)
            except psutil.TimeoutExpired:
                # Force kill if graceful shutdown fails
                proc.kill()
            except psutil.NoSuchProcess:
                pass
            
            server_state["pid"] = None
            server_state["status"] = "stopped"
            
            return {
                "status": "success",
                "message": "Server stopped"
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    async def restart_server(self, host="0.0.0.0", port=8000):
        """Restart the FastAPI server"""
        try:
            if server_state["pid"]:
                await self.stop_server()
                await asyncio.sleep(2)  # Wait for cleanup
            return await self.start_server(host, port)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    async def read_output(self):
        """Read server output and broadcast to WebSocket clients"""
        if not self.process:
            return
            
        try:
            while self.process and self.process.poll() is None:
                line = self.process.stdout.readline()
                if line:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    log_entry = f"[{timestamp}] {line.strip()}"
                    
                    # Store in memory
                    server_state["log_lines"].append(log_entry)
                    if len(server_state["log_lines"]) > server_state["max_log_lines"]:
                        server_state["log_lines"].pop(0)
                    
                    # Broadcast to WebSocket clients
                    await self.broadcast_log(log_entry)
                    
                await asyncio.sleep(0.1)
        except Exception as e:
            print(f"Error reading output: {e}")
        finally:
            # Mark as stopped when process ends
            if self.process and self.process.poll() is not None:
                server_state["status"] = "stopped"
                server_state["pid"] = None
    
    async def broadcast_log(self, message: str):
        """Broadcast log message to all connected WebSocket clients"""
        disconnected = []
        for connection in active_connections:
            try:
                await connection.send_json({
                    "type": "log",
                    "data": message
                })
            except:
                disconnected.append(connection)
        
        # Remove disconnected clients
        for conn in disconnected:
            if conn in active_connections:
                active_connections.remove(conn)

manager = ServerManager()

@app.get("/")
async def root(username: str = Depends(verify_credentials)):
    """Serve the dashboard HTML (password protected)"""
    with open("/workspaces/Chemistry/backend/dash/index.html", "r") as f:
        return HTMLResponse(content=f.read())

@app.get("/api/status")
async def get_status(username: str = Depends(verify_credentials)):
    """Get current server status"""
    process_info = manager.get_process_info()
    return {
        "status": server_state["status"],
        "process": process_info,
        "log_count": len(server_state["log_lines"])
    }

@app.post("/api/start")
async def start_server(username: str = Depends(verify_credentials), host: str = "0.0.0.0", port: int = 8000):
    """Start the server"""
    return await manager.start_server(host, port)

@app.post("/api/stop")
async def stop_server(username: str = Depends(verify_credentials)):
    """Stop the server"""
    return await manager.stop_server()

@app.post("/api/restart")
async def restart_server(username: str = Depends(verify_credentials), host: str = "0.0.0.0", port: int = 8000):
    """Restart the server"""
    return await manager.restart_server(host, port)

@app.get("/api/logs")
async def get_logs(username: str = Depends(verify_credentials), lines: int = 100):
    """Get recent log lines"""
    return {
        "logs": server_state["log_lines"][-lines:]
    }

@app.post("/api/command")
async def execute_command(request: Request, username: str = Depends(verify_credentials)):
    """Execute a custom command in the API directory"""
    try:
        body = await request.json()
        command = body.get("command", "")
        
        if not command:
            raise HTTPException(status_code=400, detail="No command provided")
        
        result = subprocess.run(
            command,
            shell=True,
            cwd="/workspaces/Chemistry/backend/api",
            capture_output=True,
            text=True,
            timeout=30
        )
        return {
            "status": "success",
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="Command timeout")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time logs"""
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        # Send existing logs
        await websocket.send_json({
            "type": "history",
            "data": server_state["log_lines"][-50:]
        })
        
        # Keep connection alive
        while True:
            data = await websocket.receive_text()
            # Echo back for keep-alive
            await websocket.send_json({
                "type": "pong",
                "data": "alive"
            })
    except WebSocketDisconnect:
        if websocket in active_connections:
            active_connections.remove(websocket)

@app.post("/api/change-password")
async def change_password(request: Request, username: str = Depends(verify_credentials)):
    """Change dashboard password"""
    try:
        body = await request.json()
        current_password = body.get("current_password", "")
        new_password = body.get("new_password", "")
        confirm_password = body.get("confirm_password", "")
        
        if not current_password or not new_password or not confirm_password:
            raise HTTPException(status_code=400, detail="All password fields are required")
        
        # Verify current password
        if not secrets.compare_digest(current_password, credentials_store["password"]):
            raise HTTPException(status_code=401, detail="Current password is incorrect")
        
        # Check new passwords match
        if new_password != confirm_password:
            raise HTTPException(status_code=400, detail="New passwords do not match")
        
        # Validate new password strength
        if len(new_password) < 8:
            raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
        
        # Update password
        credentials_store["password"] = new_password
        
        # Write to file for persistence
        try:
            with open("/workspaces/Chemistry/backend/dash/dashboard_api.py", "r") as f:
                content = f.read()
            
            # Update the password in the file
            import re
            pattern = r'DASHBOARD_PASSWORD = "chemistry"]*"'
            replacement = f'DASHBOARD_PASSWORD = "chemistry"'
            new_content = re.sub(pattern, replacement, content)
            
            with open("/workspaces/Chemistry/backend/dash/dashboard_api.py", "w") as f:
                f.write(new_content)
        except Exception as e:
            print(f"Warning: Could not persist password to file: {e}")
        
        return {
            "status": "success",
            "message": "Password changed successfully. Please restart dashboard for changes to persist."
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/restart-dashboard")
async def restart_dashboard(username: str = Depends(verify_credentials)):
    """Restart the dashboard server by triggering uvicorn reload"""
    try:
        # Touch this file to trigger uvicorn's auto-reload
        async def do_restart():
            await asyncio.sleep(0.5)
            try:
                # Update the modification time of this file to trigger reload
                file_path = __file__
                os.utime(file_path, None)
            except Exception as e:
                print(f"Error during restart: {e}")
        
        asyncio.create_task(do_restart())
        
        return {
            "status": "success",
            "message": "Dashboard is restarting... (requires --reload flag)"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint (no auth required)"""
    return {"status": "healthy", "service": "dashboard"}

@app.get("/health")
async def health_check():
    """Health check endpoint (no auth required)"""
    return {"status": "healthy", "service": "dashboard"}
