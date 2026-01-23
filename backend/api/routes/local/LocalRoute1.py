from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

router = APIRouter()

class LocalRequest(BaseModel):
    action: str
    data: Optional[Dict[str, Any]] = None

@router.get("/")
async def local_root():
    """
    Local route root endpoint.
    """
    return {
        "route": "local",
        "status": "active",
        "description": "Local processing endpoints"
    }

@router.post("/process")
async def process_local_request(request: LocalRequest):
    """
    Process local requests.
    
    Example request:
    {
        "action": "calculate",
        "data": {"sample": "data"}
    }
    """
    try:
        return {
            "status": "success",
            "route": "local",
            "action": request.action,
            "result": f"Processed local action: {request.action}",
            "data": request.data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def local_status():
    """
    Check local service status.
    """
    return {
        "route": "local",
        "status": "operational",
        "resources": {
            "cpu": "available",
            "memory": "available",
            "storage": "available"
        }
    }
