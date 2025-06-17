"""
Game Orchestration API endpoints
Production-ready endpoints for coordinating all AI and game systems.
"""

from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
import asyncio
import json
from datetime import datetime

from database import get_db
from services.game_orchestrator import get_game_orchestrator, ActionResult, GamePhase
from services.dice_service import DiceRollResult
from models.character import Character

router = APIRouter(prefix="/orchestration", tags=["Game Orchestration"])


# Request/Response Models
class StartSessionRequest(BaseModel):
    user_id: str = Field(..., description="User ID")
    character_id: int = Field(..., description="Character ID")
    story_arc_id: Optional[int] = Field(None, description="Optional story arc ID")


class PlayerActionRequest(BaseModel):
    session_id: str = Field(..., description="Game session ID")
    action: str = Field(..., description="Player's action description")
    dice_results: Optional[List[Dict[str, Any]]] = Field(None, description="Dice roll results if any")


class OrchestrationResponse(BaseModel):
    success: bool
    result_type: str
    narrative_text: str
    state_changes: List[Dict[str, Any]]
    dice_required: List[Dict[str, Any]]
    next_actions: List[str]
    performance_metrics: Dict[str, Any]
    errors: List[str]


class SessionStatusResponse(BaseModel):
    active: bool
    session_id: Optional[str] = None
    character: Optional[Dict[str, Any]] = None
    story: Optional[Dict[str, Any]] = None
    current_turn: Optional[Dict[str, Any]] = None
    last_activity: Optional[str] = None
    error: Optional[str] = None


# WebSocket connection manager for real-time updates
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
    
    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
    
    async def send_personal_message(self, message: dict, session_id: str):
        if session_id in self.active_connections:
            try:
                await self.active_connections[session_id].send_text(json.dumps(message))
            except:
                # Connection might be closed, remove it
                self.disconnect(session_id)


manager = ConnectionManager()


@router.post("/sessions/start", response_model=Dict[str, Any])
async def start_game_session(
    request: StartSessionRequest,
    db: Session = Depends(get_db)
):
    """Start a new game session with full AI integration"""
    try:
        orchestrator = get_game_orchestrator(db)
        
        # Validate character exists
        character = db.query(Character).filter_by(id=request.character_id).first()
        if not character:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Character {request.character_id} not found"
            )
        
        session_id, result = await orchestrator.start_game_session(
            user_id=request.user_id,
            character_id=request.character_id,
            story_arc_id=request.story_arc_id
        )
        
        return {
            "session_id": session_id,
            "success": result.success,
            "result_type": result.result_type.value,
            "narrative_text": result.narrative_text,
            "state_changes": result.state_changes,
            "dice_required": result.dice_required,
            "next_actions": result.next_actions,
            "performance_metrics": result.performance_metrics,
            "errors": result.errors,
            "character": {
                "id": character.id,
                "name": character.name,
                "class": character.character_class,
                "level": character.level
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start session: {str(e)}"
        )


@router.post("/actions/process", response_model=OrchestrationResponse)
async def process_player_action(
    request: PlayerActionRequest,
    db: Session = Depends(get_db)
):
    """Process a player action through the complete AI pipeline"""
    try:
        orchestrator = get_game_orchestrator(db)
        
        # Convert dice results if provided
        dice_rolls = None
        if request.dice_results:
            dice_rolls = []
            for dice_data in request.dice_results:
                dice_roll = DiceRollResult(
                    expression=dice_data.get('expression', '1d20'),
                    result=dice_data.get('result', 0),
                    modifier=dice_data.get('modifier', 0),
                    roll_type=dice_data.get('roll_type', 'skill')
                )
                dice_rolls.append(dice_roll)
        
        result = await orchestrator.process_player_action(
            session_id=request.session_id,
            player_action=request.action,
            dice_results=dice_rolls
        )
        
        # Send real-time update via WebSocket
        if request.session_id in manager.active_connections:
            await manager.send_personal_message({
                "type": "action_result",
                "data": {
                    "success": result.success,
                    "result_type": result.result_type.value,
                    "narrative": result.narrative_text,
                    "state_changes": result.state_changes,
                    "dice_required": result.dice_required,
                    "next_actions": result.next_actions
                }
            }, request.session_id)
        
        return OrchestrationResponse(
            success=result.success,
            result_type=result.result_type.value,
            narrative_text=result.narrative_text,
            state_changes=result.state_changes,
            dice_required=result.dice_required,
            next_actions=result.next_actions,
            performance_metrics=result.performance_metrics,
            errors=result.errors
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process action: {str(e)}"
        )


@router.get("/sessions/{session_id}/status", response_model=SessionStatusResponse)
async def get_session_status(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Get comprehensive status of a game session"""
    try:
        orchestrator = get_game_orchestrator(db)
        status_data = await orchestrator.get_session_status(session_id)
        
        return SessionStatusResponse(**status_data)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get session status: {str(e)}"
        )


@router.post("/sessions/{session_id}/continue")
async def continue_session_with_dice(
    session_id: str,
    dice_results: List[Dict[str, Any]],
    db: Session = Depends(get_db)
):
    """Continue a session that was waiting for dice results"""
    try:
        orchestrator = get_game_orchestrator(db)
        
        # Convert dice results
        dice_rolls = []
        for dice_data in dice_results:
            dice_roll = DiceRollResult(
                expression=dice_data.get('expression', '1d20'),
                result=dice_data.get('result', 0),
                modifier=dice_data.get('modifier', 0),
                roll_type=dice_data.get('roll_type', 'skill')
            )
            dice_rolls.append(dice_roll)
        
        # Continue with the last action but now with dice results
        result = await orchestrator.process_player_action(
            session_id=session_id,
            player_action="[Continuing with dice results]",
            dice_results=dice_rolls
        )
        
        return {
            "success": result.success,
            "result_type": result.result_type.value,
            "narrative_text": result.narrative_text,
            "state_changes": result.state_changes,
            "next_actions": result.next_actions
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to continue session: {str(e)}"
        )


@router.get("/health")
async def orchestrator_health_check(db: Session = Depends(get_db)):
    """Health check for the orchestration service"""
    try:
        orchestrator = get_game_orchestrator(db)
        health_data = orchestrator.health_check()
        
        return {
            **health_data,
            "active_websocket_connections": len(manager.active_connections),
            "endpoints_available": [
                "POST /orchestration/sessions/start",
                "POST /orchestration/actions/process", 
                "GET /orchestration/sessions/{session_id}/status",
                "POST /orchestration/sessions/{session_id}/continue",
                "WS /orchestration/sessions/{session_id}/ws"
            ]
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@router.websocket("/sessions/{session_id}/ws")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time game updates"""
    await manager.connect(websocket, session_id)
    
    try:
        # Send initial connection confirmation
        await websocket.send_text(json.dumps({
            "type": "connection_established",
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        }))
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Wait for messages from client (heartbeat, etc.)
                data = await websocket.receive_text()
                message = json.loads(data)
                
                if message.get("type") == "heartbeat":
                    await websocket.send_text(json.dumps({
                        "type": "heartbeat_response",
                        "timestamp": datetime.now().isoformat()
                    }))
                    
            except WebSocketDisconnect:
                break
            except asyncio.TimeoutError:
                # Send heartbeat to check if connection is still alive
                try:
                    await websocket.send_text(json.dumps({
                        "type": "heartbeat",
                        "timestamp": datetime.now().isoformat()
                    }))
                except:
                    break
                    
    except Exception as e:
        print(f"WebSocket error for session {session_id}: {str(e)}")
    finally:
        manager.disconnect(session_id)


# Utility endpoints for development and debugging
@router.get("/sessions/{session_id}/debug")
async def debug_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Debug endpoint to get detailed session information"""
    try:
        orchestrator = get_game_orchestrator(db)
        
        # Get current turn info
        current_turn = orchestrator.active_turns.get(session_id)
        
        debug_info = {
            "session_id": session_id,
            "has_active_turn": current_turn is not None,
            "turn_info": {
                "turn_id": current_turn.turn_id if current_turn else None,
                "phase": current_turn.phase.value if current_turn else None,
                "player_action": current_turn.player_action if current_turn else None,
                "result": current_turn.result.value if current_turn and current_turn.result else None,
                "errors": current_turn.error_messages if current_turn else []
            } if current_turn else None,
            "orchestrator_metrics": orchestrator.performance_metrics,
            "websocket_connected": session_id in manager.active_connections
        }
        
        return debug_info
        
    except Exception as e:
        return {
            "error": str(e),
            "session_id": session_id
        }


@router.post("/test/scenario")
async def test_complete_scenario(db: Session = Depends(get_db)):
    """Test endpoint to run a complete game scenario for validation"""
    try:
        orchestrator = get_game_orchestrator(db)
        
        # Create a test character if needed
        test_character = db.query(Character).first()
        if not test_character:
            return {"error": "No characters available for testing"}
        
        # Start session
        session_id, start_result = await orchestrator.start_game_session(
            user_id="test_user",
            character_id=test_character.id
        )
        
        # Process a test action
        action_result = await orchestrator.process_player_action(
            session_id=session_id,
            player_action="I look around the room carefully for any hidden doors or treasures."
        )
        
        # Get final status
        final_status = await orchestrator.get_session_status(session_id)
        
        return {
            "test_completed": True,
            "session_id": session_id,
            "start_result": start_result.result_type.value,
            "action_result": action_result.result_type.value,
            "final_status": final_status,
            "all_systems_working": (
                start_result.success and 
                action_result.success and 
                final_status.get('active', False)
            )
        }
        
    except Exception as e:
        return {
            "test_completed": False,
            "error": str(e)
        } 