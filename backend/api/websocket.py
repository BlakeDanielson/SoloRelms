from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Dict, List, Any
import json
import asyncio
from datetime import datetime
import logging
from sqlalchemy.orm import Session
from database import get_db

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

class ConnectionManager:
    """Manages WebSocket connections for real-time communication"""
    
    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.game_rooms: Dict[str, List[str]] = {}  # game_id -> [connection_ids]
        
    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"🔗 WebSocket connected. Total connections: {len(self.active_connections)}")
        
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"🔗 WebSocket disconnected. Total connections: {len(self.active_connections)}")
        
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send a message to a specific connection"""
        await websocket.send_text(message)
        
    async def broadcast(self, message: str):
        """Broadcast a message to all active connections"""
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remove broken connections
                self.active_connections.remove(connection)

# Global connection manager instance
manager = ConnectionManager()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Basic WebSocket endpoint for game communication.
    This is a placeholder implementation for the MVP.
    """
    await manager.connect(websocket)
    
    try:
        # Send welcome message
        await manager.send_personal_message(
            json.dumps({
                "type": "connection",
                "status": "connected",
                "message": "Connected to SoloRealms game server"
            }), 
            websocket
        )
        
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                logger.info(f"📨 Received WebSocket message: {message.get('type', 'unknown')}")
                
                # Echo back for now (placeholder behavior)
                response = {
                    "type": "echo",
                    "original_message": message,
                    "timestamp": str(datetime.now()),
                    "status": "received"
                }
                
                await manager.send_personal_message(
                    json.dumps(response), 
                    websocket
                )
                
            except json.JSONDecodeError:
                await manager.send_personal_message(
                    json.dumps({
                        "type": "error",
                        "message": "Invalid JSON format"
                    }), 
                    websocket
                )
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"❌ WebSocket error: {e}")
        manager.disconnect(websocket)

# Utility functions for sending messages from other parts of the application
async def notify_game_players(game_id: str, message_type: str, data: dict):
    """Send a notification to all players in a game"""
    message = {
        "type": message_type,
        "data": data,
        "timestamp": datetime.utcnow().isoformat()
    }
    await manager.broadcast(json.dumps(message))

async def notify_player(connection_id: str, message_type: str, data: dict):
    """Send a notification to a specific player"""
    message = {
        "type": message_type,
        "data": data,
        "timestamp": datetime.utcnow().isoformat()
    }
    await manager.send_personal_message(json.dumps(message), connection_id)

def get_active_connections() -> list[WebSocket]:
    """Get all active connections (for debugging/admin purposes)"""
    return manager.active_connections

def get_game_rooms() -> Dict[str, List[str]]:
    """Get all game rooms (for debugging/admin purposes)"""
    return manager.game_rooms 