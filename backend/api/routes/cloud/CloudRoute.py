from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

router = APIRouter()

class CloudRequest(BaseModel):
    action: str
    data: Optional[Dict[str, Any]] = None

@router.get("/")
async def cloud_root():
    """
    Cloud route root endpoint.
    """
    return {
        "route": "cloud",
        "status": "active",
        "description": "Cloud-based processing endpoints"
    }

@router.post("/process")
async def process_cloud_request(request: CloudRequest):
    """
    Process cloud-based requests.
    
    Example request:
    {
        "action": "analyze",
        "data": {"sample": "data"}
    }
    """
    try:
        return {
            "status": "success",
            "route": "cloud",
            "action": request.action,
            "result": f"Processed cloud action: {request.action}",
            "data": request.data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def cloud_status():
    """
    Check cloud service status.
    """
    return {
        "route": "cloud",
        "status": "operational",
        "services": ["compute", "storage", "analysis"]
    }
@router.get("/calc")
async def cloud_calc(num1: float, num2: float, operation: str = "add"):
    """
    Cloud calculation endpoint.
    """
    try:
        if operation == "add":
            result = num1 + num2
            status = "Success"
        elif operation == "subtract":
            result = num1 - num2
            status = "Success"
        elif operation == "multiply":
            result = num1 * num2
            status = "Success"
        elif operation == "divide":
            if num2 == 0:
                raise ValueError("Cannot divide by zero")
            result = num1 / num2
            status = "Success"
        else:
            raise ValueError(f"Unknown operation: {operation}")
        
        return {
            "status": status,
            "route": "cloud",
            "calculation_result": result,
            "num1": num1,
            "num2": num2,
            "operation": operation
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
@router.get("/time")
async def cloud_time(country: Optional[str] = None, until_time: Optional[str] = None):
    """
    Cloud time endpoint.
    
    Parameters:
    - country: Optional country name to get time in that timezone
    - until_time: Optional time in HH:MM format to calculate time until that time
    
    Examples:
    - /time -> Current UTC time
    - /time?country=US/Eastern -> Current time in Eastern timezone
    - /time?until_time=15:00 -> Time until 3 PM UTC
    - /time?country=US/Pacific&until_time=18:30 -> Time until 6:30 PM Pacific
    """
    from datetime import datetime
    import pytz
    
    try:
        # Default to UTC
        tz = pytz.UTC
        if country:
            tz = pytz.timezone(country)
        
        current_time = datetime.now(tz)
        
        response = {
            "route": "cloud",
            "timezone": str(tz),
            "current_time": current_time.isoformat()
        }
        
        # Calculate time until specified time
        if until_time:
            target_hour, target_minute = map(int, until_time.split(":"))
            target_time = current_time.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
            
            # If target time is in the past, add a day
            if target_time <= current_time:
                target_time = target_time.replace(day=target_time.day + 1)
            
            time_diff = target_time - current_time
            hours, remainder = divmod(int(time_diff.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            
            response["until_time"] = until_time
            response["time_remaining"] = f"{hours}h {minutes}m {seconds}s"
        
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
