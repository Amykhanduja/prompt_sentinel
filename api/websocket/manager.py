import logging
from typing import List
from fastapi import WebSocket

logger = logging.getLogger("promptsentinel.websocket")

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Total clients: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket client disconnected. Total clients: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        dead_connections = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Failed to broadcast message: {e}")
                dead_connections.append(connection)
        
        for dead in dead_connections:
            self.disconnect(dead)

async def broadcast_scan_event(result: dict):
    try:
        event = {
            "event": "scan_completed",
            "data": {
                "status": "completed",
                "timestamp": result.get("timestamp"),
                "risk_score": result.get("risk_score"),
                "severity": result.get("severity"),
                "action": result.get("action"),
                "source": result.get("source"),
                "detections_count": len(result.get("detections", [])),
                "obfuscation_detected": result.get("detection_context", {}).get("obfuscation_detected", False),
                "obfuscation_adjustment": result.get("detection_context", {}).get("obfuscation_adjustment", 0)
            }
        }
        await manager.broadcast(event)
    except Exception as e:
        logger.error(f"Failed to broadcast scan event: {e}")

manager = ConnectionManager()
