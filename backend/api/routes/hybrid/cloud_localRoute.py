from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

router = APIRouter()

class HybridRequest(BaseModel):
    action: str
    data: Optional[Dict[str, Any]] = None
    prefer_cloud: Optional[bool] = False

@router.get("/")
async def hybrid_root():
    """
    Hybrid route root endpoint.
    """
    return {
        "route": "hybrid",
        "status": "active",
        "description": "Hybrid cloud-local processing endpoints"
    }

@router.post("/process")
async def process_hybrid_request(request: HybridRequest):
    """
    Process hybrid cloud-local requests.
    
    Example request:
    {
        "action": "compute",
        "data": {"sample": "data"},
        "prefer_cloud": true
    }
    """
    try:
        processing_location = "cloud" if request.prefer_cloud else "local"
        
        return {
            "status": "success",
            "route": "hybrid",
            "action": request.action,
            "processing_location": processing_location,
            "result": f"Processed hybrid action: {request.action} on {processing_location}",
            "data": request.data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def hybrid_status():
    """
    Check hybrid service status.
    """
    return {
        "route": "hybrid",
        "status": "operational",
        "cloud_available": True,
        "local_available": True,
        "load_balancing": "active"
    }
