from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from api.websocket.manager import manager
from api.security import get_current_user
import logging

logger = logging.getLogger("promptsentinel.websocket.routes")

router = APIRouter()

@router.websocket("/ws/dashboard")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

@router.post("/api/v1/test-broadcast")
async def test_broadcast(current_user = Depends(get_current_user)):
    await manager.broadcast({"event": "test", "message": "Broadcast works!"})
    return {"status": "ok", "broadcasted": True}
