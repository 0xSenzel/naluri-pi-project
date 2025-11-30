from fastapi import APIRouter, Response, Depends, Request, status, Cookie
from fastapi.responses import JSONResponse, StreamingResponse
from uuid import uuid4
import redis.asyncio as aredis # Use async Redis client for FastAPI
import json
from src.config import *
from src.api.services import session_manager, get_current_pi_data
from typing import Optional
from pydantic import BaseModel

router = APIRouter()

# ========== Response Models ==========
class PiDataResponse(BaseModel):
    """Response model for Pi calculation data."""
    pi: str
    circumference: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "pi": "3.14159265358979323846...",
                "circumference": "40075.017"
            }
        }

# ========== End Response Models ==========""
async_r = aredis.StrictRedis(host=REDIS_HOST, port=6379, decode_responses=True)

# Dependency for Redis connection
async def get_redis():
    yield async_r

# Dependency for Throttling/Session Management
def get_session_id(
    response: Response, 
    # This tells FastAPI: "Look for a cookie named 'session_id', but if it's not there, 
    # assign the variable session_id the value None."
    session_id: Optional[str] = Cookie(None) 
):
    # Rename parameter to session_id for clarity
    if not session_id:
        # If the cookie is not present (first request)
        session_id = str(uuid4())
        response.set_cookie(key="session_id", value=session_id, httponly=True)
    
    # Return the session_id (whether new or existing)
    return session_id

@router.get(
    "/status",
    response_model=PiDataResponse,
    summary="Get Current Pi and Circumference Data",
    tags=["Pi Calculation"],
    responses={
        200: {
            "description": "Successfully retrieved current Pi and circumference values",
            "content": {
                "application/json": {
                    "example": {
                        "pi": "3.14159265358979323846...",
                        "circumference": "40075.017"
                    }
                }
            }
        }
    }
)
async def get_pi_status(r: aredis.Redis = Depends(get_redis)):
    """
    Retrieve the current Pi value and circumference data.
    
    This endpoint returns the current calculated value of Pi and the corresponding 
    circumference value stored in Redis. Perfect for initial data load.
    
    **Returns:**
    - `pi`: The calculated Pi value as a string (e.g., "3.14159265358979323846...")
    - `circumference`: The circumference value in kilometers as a string
    """
    data = await get_current_pi_data(r)
    return JSONResponse(content=data)

@router.get(
    "/pi-stream",
    summary="Stream Pi and Circumference Updates",
    tags=["Pi Calculation"],
    responses={
        200: {
            "description": "Server-Sent Events stream of Pi and circumference data updates",
            "content": {
                "text/event-stream": {
                    "example": "data: {\"pi\": \"3.14159265358979323846...\", \"circumference\": \"40075.017\"}\n\ndata: {\"pi\": \"3.1415926535897932384626433832795...\", \"circumference\": \"40075.017\"}\n\n"
                }
            }
        },
        429: {
            "description": "Too many concurrent connections from this session. Connection limit reached.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Connection limit reached for this session."
                    }
                }
            }
        }
    }
)
async def pi_stream(request: Request, r: aredis.Redis = Depends(get_redis), session_id: str = Depends(get_session_id)):
    """
    Stream real-time Pi and circumference data updates via Server-Sent Events (SSE).
    
    This endpoint establishes a persistent connection that sends updated Pi calculation 
    data and circumference values whenever the worker computes new Pi digits. It includes 
    session-based throttling to prevent resource exhaustion.
    
    **Features:**
    - Real-time updates via Server-Sent Events protocol
    - Cookie-based session tracking for throttling
    - Automatic cleanup on connection close
    - Initial data push on connection establishment
    
    **Cookies:**
    - `session_id`: Automatically set to track concurrent connections per session
    
    **Throttling:**
    - Returns HTTP 429 if session exceeds connection limits
    - Each client session has a limited number of concurrent stream connections
    
    **Data Format:**
    Each event contains JSON with:
    - `pi`: The current calculated Pi value as a string
    - `circumference`: The circumference value in kilometers as a string
    
    **Example Data:**
    ```
    data: {"pi": "3.14159265358979323846...", "circumference": "40075.017"}
    ```
    """

    # 1. Throttling Check
    if not session_manager.connect(session_id):
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"detail": "Connection limit reached for this session."}
        )
    
    # 2. SSE Generator Function
    async def event_generator():
        # Start Pub/Sub listener
        pubsub = r.pubsub()
        await pubsub.subscribe(REDIS_PUBSUB_CHANNEL)
        
        # Initial push of current data
        initial_data = await get_current_pi_data(r)
        yield f"data: {json.dumps(initial_data)}\n\n"

        try:
            # Loop waits for new messages from the worker
            while await request.is_connected():
                message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1)
                if message and message.get("data") == "UPDATE":
                    # When signal received, read new data and push
                    data = await get_current_pi_data(r)
                    yield f"data: {json.dumps(data)}\n\n"
        except Exception:
            pass # Connection likely dropped
        finally:
            # 3. Teardown: Clean up resources
            await pubsub.unsubscribe(REDIS_PUBSUB_CHANNEL)
            session_manager.disconnect(session_id)
            print(f"SSE stream closed for session: {session_id}")

    # Set headers for SSE
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )