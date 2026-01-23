from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from routes.cloud.CloudRoute import router as cloud_router
from routes.hybrid.cloud_localRoute import router as hybrid_router
from routes.local.LocalRoute1 import router as local_router

router = APIRouter(prefix="/api", tags=["main"])

# Include sub-routers
router.include_router(cloud_router, prefix="/cloud", tags=["cloud"])
router.include_router(hybrid_router, prefix="/hybrid", tags=["hybrid"])
router.include_router(local_router, prefix="/local", tags=["local"])

@router.post("/route")
async def route_request(request: Request):
    """
    Main routing endpoint that accepts requests and routes them to appropriate handlers.
    
    Expected request body format:
    {
        "route_type": "cloud" | "hybrid" | "local",
        "action": "specific_action",
        "data": {...}
    }
    """
    try:
        body = await request.json()
        route_type = body.get("route_type")
        
        if not route_type:
            raise HTTPException(
                status_code=400,
                detail="Missing 'route_type' in request body. Expected: 'cloud', 'hybrid', or 'local'"
            )
        
        # Return routing information
        routing_info = {
            "cloud": {
                "endpoint": "/api/cloud",
                "description": "Routes to cloud-based processing"
            },
            "hybrid": {
                "endpoint": "/api/hybrid",
                "description": "Routes to hybrid cloud-local processing"
            },
            "local": {
                "endpoint": "/api/local",
                "description": "Routes to local processing"
            }
        }
        
        if route_type not in routing_info:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid route_type '{route_type}'. Must be one of: cloud, hybrid, local"
            )
        
        return JSONResponse(
            status_code=200,
            content={
                "message": f"Request classified for {route_type} processing",
                "route_info": routing_info[route_type],
                "received_data": body
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/info")
async def get_routing_info():
    """
    Returns information about available routing endpoints.
    """
    return {
        "available_routes": {
            "cloud": {
                "endpoint": "/api/cloud",
                "methods": ["GET", "POST"],
                "description": "Cloud-based processing endpoints"
            },
            "hybrid": {
                "endpoint": "/api/hybrid",
                "methods": ["GET", "POST"],
                "description": "Hybrid cloud-local processing endpoints"
            },
            "local": {
                "endpoint": "/api/local",
                "methods": ["GET", "POST"],
                "description": "Local processing endpoints"
            }
        },
        "routing_endpoint": {
            "endpoint": "/api/route",
            "method": "POST",
            "description": "Main routing endpoint for classifying and routing requests"
        }
    }
