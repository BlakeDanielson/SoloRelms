from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging
import json
from sqlalchemy.orm import Session
from sqlalchemy import and_
import os

from database import get_db
from auth import get_current_user_id, get_current_user
from models.story import StoryArc, WorldState, StoryStage
from models.character import Character
from models.user import User

# Add AI service import
try:
    from services.ai_service import AIService
    from services.response_parser import response_parser
    ai_service = AIService()
except ImportError:
    ai_service = None
    response_parser = None

# Setup logging
logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic models for request/response
class PlayerActionRequest(BaseModel):
    action_type: str = Field(..., pattern="^(action|speech|thought)$")
    content: str = Field(..., min_length=1, max_length=1000)
    metadata: Optional[Dict[str, Any]] = {}

class DiceRollRequest(BaseModel):
    dice_type: str = Field(..., pattern="^d(4|6|8|10|12|20|100)$")
    count: int = Field(default=1, ge=1, le=10)
    modifier: int = Field(default=0, ge=-20, le=20)
    label: Optional[str] = None

class GameActionResponse(BaseModel):
    success: bool
    message_id: str
    player_message: Dict[str, Any]
    ai_response: Optional[Dict[str, Any]] = None
    game_state_updates: Optional[Dict[str, Any]] = {}

class DiceRollResponse(BaseModel):
    dice_type: str
    count: int
    modifier: int
    rolls: List[int]
    total: int
    label: Optional[str] = None

class GameStateUpdate(BaseModel):
    current_scene: Optional[str] = None
    scene_image_url: Optional[str] = None
    scene_type: Optional[str] = None
    objectives: Optional[List[str]] = None
    recent_events: Optional[List[str]] = None
    current_location: Optional[str] = None

class CharacterUpdate(BaseModel):
    current_hp: Optional[int] = None
    max_hp: Optional[int] = None
    armor_class: Optional[int] = None
    location: Optional[str] = None
    status_effects: Optional[List[str]] = None

@router.post("/games/{story_id}/actions", response_model=GameActionResponse)
async def handle_player_action(
    story_id: int,
    action_request: PlayerActionRequest,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """Handle a player action and generate AI DM response"""
    
    # Verify story belongs to user
    story = db.query(StoryArc).filter(
        and_(StoryArc.id == story_id, StoryArc.user_id == current_user_id)
    ).first()
    
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Story not found or not owned by user"
        )
    
    if story.story_completed:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot perform actions in completed story"
        )
    
    # Get character
    character = db.query(Character).filter(Character.id == story.character_id).first()
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found"
        )
    
    # Get world state
    world_state = db.query(WorldState).filter(WorldState.story_arc_id == story_id).first()
    if not world_state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="World state not found"
        )
    
    # CHECK: Are we waiting for a dice roll?
    if world_state.waiting_for_dice and world_state.pending_dice_requirement:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot perform new action while waiting for dice roll. Please roll dice first.",
            headers={"X-Dice-Required": "true"}
        )
    
    # Create player message
    player_message = {
        "id": f"player_{datetime.utcnow().timestamp()}",
        "type": f"player_{action_request.action_type}",
        "content": action_request.content,
        "timestamp": datetime.utcnow().isoformat(),
        "character_name": character.name,
        "metadata": action_request.metadata
    }
    
    # Generate AI response if AI service is available
    ai_response = None
    combat_detected = False
    state_changes = {}
    
    if ai_service:
        try:
            print(f"🤖 Generating AI response for {action_request.action_type} action: {action_request.content}")
            
            # Generate AI response using the story template
            ai_result = ai_service.narrate_story(
                db=db,
                character_id=character.id,
                story_arc_id=story_id,
                player_action=action_request.content,
                additional_context=f"Player action type: {action_request.action_type}"
            )
            
            if ai_result.get('success') and ai_result.get('content'):
                ai_content = ai_result.get('content').strip()
                
                # Debug: log the AI response for combat detection testing
                print(f"📄 AI Response Content (first 200 chars): {ai_content[:200]}...")
                
                # Parse the AI response for structured data and combat events
                if response_parser:
                    try:
                        parsed_response = response_parser.parse_response(ai_content)
                        
                        # Check for combat initiation
                        combat_events = parsed_response.combat_events
                        combat_detected = any(event.event_type == "combat_initiated" for event in combat_events)
                        
                        # Debug: log combat events found
                        if combat_events:
                            print(f"⚔️ Combat events found: {[event.event_type for event in combat_events]}")
                        else:
                            print(f"ℹ️ No combat events detected in response")
                        
                        if combat_detected:
                            print(f"🎯 Combat initiated successfully!")
                            state_changes['combat_initiated'] = True
                        else:
                            # Check if response contains combat-related keywords manually
                            combat_keywords = ['combat', 'fight', 'attack', 'battle', 'initiative', 'hostile', 'aggressive']
                            found_keywords = [kw for kw in combat_keywords if kw.lower() in ai_content.lower()]
                            if found_keywords:
                                print(f"🔍 Combat keywords found but not detected by parser: {found_keywords}")
                        
                        # Extract other important events
                        if parsed_response.dice_rolls:
                            dice_requirements = []
                            for roll in parsed_response.dice_rolls:
                                dice_requirements.append({
                                    'expression': roll.dice_expression,
                                    'purpose': roll.purpose,
                                    'modifier': roll.modifier,
                                    'dc': roll.target_number,
                                    'advantage': roll.advantage,
                                    'disadvantage': roll.disadvantage
                                })
                            state_changes['dice_required'] = dice_requirements
                            
                            # NEW: Set the first dice requirement as pending and pause the narrative
                            if dice_requirements:
                                primary_roll = dice_requirements[0]
                                world_state.set_dice_requirement(
                                    dice_expression=primary_roll['expression'],
                                    purpose=primary_roll['purpose'],
                                    dc=primary_roll.get('dc'),
                                    ability_modifier=primary_roll.get('modifier', 0),
                                    advantage=primary_roll.get('advantage', False)
                                )
                                
                                # Modify AI content to indicate we're waiting for dice
                                ai_content += f"\n\n🎲 **DICE ROLL REQUIRED**: {primary_roll['expression']} for {primary_roll['purpose']}"
                                if primary_roll.get('dc'):
                                    ai_content += f" (DC {primary_roll['dc']})"
                                ai_content += f"\n\nPlease roll your dice before I can continue the story!"
                                
                                print(f"🎲 Set dice requirement: {primary_roll['expression']} for {primary_roll['purpose']}")
                        
                        # Extract state changes
                        if parsed_response.state_changes:
                            hp_changes = []
                            for change in parsed_response.state_changes:
                                if change.property_name == 'current_hp':
                                    hp_changes.append({
                                        'amount': change.change_amount,
                                        'new_value': change.new_value
                                    })
                            if hp_changes:
                                state_changes['hp_changes'] = hp_changes
                        
                        # Add parsing metadata
                        state_changes['parsing_confidence'] = parsed_response.confidence_score
                        state_changes['combat_events_count'] = len(combat_events)
                        
                        print(f"✅ Response parsed successfully. Combat: {combat_detected}, Events: {len(combat_events)}, Confidence: {parsed_response.confidence_score:.2f}")
                        
                    except Exception as parse_error:
                        print(f"⚠️ Response parsing failed: {parse_error}")
                        import traceback
                        traceback.print_exc()
                
                ai_response = {
                    "id": f"dm_{datetime.utcnow().timestamp()}",
                    "type": "dm_narration",
                    "content": ai_content,
                    "timestamp": datetime.utcnow().isoformat(),
                    "metadata": {
                        "generated_by": "ai",
                        "response_to": player_message["id"],
                        "combat_detected": combat_detected,
                        "model_used": ai_result.get('model', 'unknown'),
                        "token_usage": ai_result.get('usage', {})
                    }
                }
                
                print(f"✅ Generated AI response for {action_request.action_type} action")
            else:
                print(f"⚠️ AI generation failed or returned empty content")
                
        except Exception as e:
            print(f"❌ Failed to generate AI response: {e}")
    
    # If no AI response, create a fallback
    if not ai_response:
        fallback_responses = {
            "action": f"You attempt to {action_request.content.lower()}. The DM considers the outcome...",
            "speech": f'{character.name} says: "{action_request.content}" The words echo in the air...',
            "thought": f"As {character.name} contemplates, the situation becomes clearer..."
        }
        
        ai_response = {
            "id": f"dm_{datetime.utcnow().timestamp()}",
            "type": "dm_narration", 
            "content": fallback_responses.get(action_request.action_type, "The DM processes your action..."),
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": {
                "generated_by": "fallback",
                "response_to": player_message["id"],
                "combat_detected": False
            }
        }
    
    # Update world state real time played
    world_state.real_time_played += 1
    
    # Prepare game state updates
    game_state_updates = {
        "real_time_played": world_state.real_time_played,
        **state_changes
    }
    
    db.commit()
    
    return GameActionResponse(
        success=True,
        message_id=player_message["id"],
        player_message=player_message,
        ai_response=ai_response,
        game_state_updates=game_state_updates
    )

@router.post("/games/{story_id}/dice", response_model=DiceRollResponse)
async def roll_dice(
    story_id: int,
    dice_request: DiceRollRequest,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """Handle dice rolling for a game"""
    
    # Verify story belongs to user
    story = db.query(StoryArc).filter(
        and_(StoryArc.id == story_id, StoryArc.user_id == current_user_id)
    ).first()
    
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Story not found or not owned by user"
        )
    
    # Extract dice size from dice_type (e.g., "d20" -> 20)
    dice_size = int(dice_request.dice_type[1:])
    
    # Roll the dice
    import random
    rolls = [random.randint(1, dice_size) for _ in range(dice_request.count)]
    total = sum(rolls) + dice_request.modifier
    
    return DiceRollResponse(
        dice_type=dice_request.dice_type,
        count=dice_request.count,
        modifier=dice_request.modifier,
        rolls=rolls,
        total=total,
        label=dice_request.label
    )


# NEW: Dice fulfillment models
class DiceFulfillmentRequest(BaseModel):
    dice_type: str = Field(..., pattern="^d(4|6|8|10|12|20|100)$") 
    rolls: List[int] = Field(..., min_items=1, max_items=10)
    modifier: int = Field(default=0, ge=-20, le=20)
    total: int
    advantage: bool = False
    disadvantage: bool = False


class DiceFulfillmentResponse(BaseModel):
    success: bool
    dice_result: Dict[str, Any]
    ai_response: Optional[Dict[str, Any]] = None
    game_state_updates: Optional[Dict[str, Any]] = {}


@router.post("/games/{story_id}/fulfill-dice", response_model=DiceFulfillmentResponse)
async def fulfill_dice_requirement(
    story_id: int,
    dice_result: DiceFulfillmentRequest,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """Fulfill a pending dice requirement and continue the narrative"""
    
    # Verify story belongs to user
    story = db.query(StoryArc).filter(
        and_(StoryArc.id == story_id, StoryArc.user_id == current_user_id)
    ).first()
    
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Story not found or not owned by user"
        )
    
    # Get character and world state
    character = db.query(Character).filter(Character.id == story.character_id).first()
    world_state = db.query(WorldState).filter(WorldState.story_arc_id == story_id).first()
    
    if not world_state or not world_state.waiting_for_dice:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No pending dice requirement found"
        )
    
    # Prepare dice result data
    dice_result_data = {
        "dice_type": dice_result.dice_type,
        "rolls": dice_result.rolls,
        "modifier": dice_result.modifier,
        "total": dice_result.total,
        "advantage": dice_result.advantage,
        "disadvantage": dice_result.disadvantage
    }
    
    # Fulfill the dice requirement
    if not world_state.fulfill_dice_requirement(dice_result_data):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Failed to fulfill dice requirement"
        )
    
    # Determine success/failure based on DC
    requirement = world_state.last_dice_result["requirement"]
    success = True
    if requirement.get("dc"):
        success = dice_result.total >= requirement["dc"]
    
    # Generate AI continuation based on dice result
    ai_response = None
    state_changes = {}
    
    try:
        if ai_service:
            print(f"🎲 Generating AI continuation for dice result: {dice_result.total} (Success: {success})")
            
            # Build context for AI
            context_messages = []
            
            # Add character context
            context_messages.append({
                "role": "system",
                "content": f"CHARACTER: {character.name} (Level {character.level})\n"
                          f"HP: {character.current_hit_points}/{character.max_hit_points}\n"
                          f"Location: {world_state.current_location}\n"
                          f"Story Stage: {story.current_stage.value}"
            })
            
            # Add dice result context
            dice_context = (
                f"DICE ROLL RESULT:\n"
                f"Purpose: {requirement['purpose']}\n"
                f"Roll: {dice_result.dice_type} = {dice_result.rolls[0]}"
            )
            if dice_result.modifier:
                dice_context += f" + {dice_result.modifier} (modifier)"
            dice_context += f" = {dice_result.total} total\n"
            if requirement.get("dc"):
                dice_context += f"DC: {requirement['dc']} - {'SUCCESS' if success else 'FAILURE'}\n"
            
            context_messages.append({
                "role": "system", 
                "content": dice_context
            })
            
            # Add continuation prompt
            continuation_prompt = (
                f"Continue the narrative based on the dice roll result. "
                f"The player rolled {dice_result.total} for {requirement['purpose']}. "
                f"{'This succeeds' if success else 'This fails'}"
                f"{' against DC ' + str(requirement['dc']) if requirement.get('dc') else ''}. "
                f"Describe the outcome and what happens next. Keep the response engaging and continue the story flow."
            )
            
            context_messages.append({
                "role": "user",
                "content": continuation_prompt
            })
            
            # Generate AI response
            ai_result = await ai_service.generate_response(
                messages=context_messages,
                max_tokens=500,
                temperature=0.8
            )
            
            if ai_result and ai_result.get('choices'):
                ai_content = ai_result['choices'][0]['message']['content'].strip()
                
                if ai_content:
                    ai_response = {
                        "id": f"dm_dice_{datetime.utcnow().timestamp()}",
                        "type": "dm_narration",
                        "content": ai_content,
                        "timestamp": datetime.utcnow().isoformat(),
                        "metadata": {
                            "generated_by": "ai",
                            "dice_continuation": True,
                            "dice_success": success,
                            "model_used": ai_result.get('model', 'unknown'),
                            "token_usage": ai_result.get('usage', {})
                        }
                    }
                    print(f"✅ Generated AI dice continuation")
    
    except Exception as e:
        print(f"❌ Failed to generate AI continuation: {e}")
    
    # If no AI response, create a fallback
    if not ai_response:
        outcome = "succeeds" if success else "fails"
        ai_response = {
            "id": f"dm_dice_{datetime.utcnow().timestamp()}",
            "type": "dm_narration",
            "content": f"Your {requirement['purpose']} {outcome}! The story continues...",
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": {
                "generated_by": "fallback",
                "dice_continuation": True,
                "dice_success": success
            }
        }
    
    # Update state
    state_changes['dice_fulfilled'] = {
        "requirement": requirement,
        "result": dice_result_data,
        "success": success
    }
    
    db.commit()
    
    return DiceFulfillmentResponse(
        success=True,
        dice_result=dice_result_data,
        ai_response=ai_response,
        game_state_updates=state_changes
    )

@router.get("/games/{story_id}/status")
async def get_game_status(
    story_id: int,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """Get current game status and state"""
    
    # Verify story belongs to user
    story = db.query(StoryArc).filter(
        and_(StoryArc.id == story_id, StoryArc.user_id == current_user_id)
    ).first()
    
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Story not found or not owned by user"
        )
    
    # Get character and world state
    character = db.query(Character).filter(Character.id == story.character_id).first()
    world_state = db.query(WorldState).filter(WorldState.story_arc_id == story_id).first()
    
    return {
        "story_id": story_id,
        "story_completed": story.story_completed,
        "current_stage": story.current_stage.value,
        "character": {
            "id": character.id,
            "name": character.name,
            "level": character.level,
            "current_hp": character.current_hit_points,
            "max_hp": character.max_hit_points
        } if character else None,
        "world_state": {
            "current_location": world_state.current_location,
            "real_time_played": world_state.real_time_played,
            "story_time_elapsed": world_state.story_time_elapsed,
            "waiting_for_dice": world_state.waiting_for_dice if world_state else False,
            "pending_dice_requirement": world_state.pending_dice_requirement if world_state else None
        } if world_state else None,
        "ai_available": ai_service is not None
    }

@router.get("/games/{game_id}/state")
async def get_game_state(
    game_id: str,
    db: Session = Depends(get_db)
):
    """Get the current game state"""
    try:
        # In a real implementation, fetch from database
        game_state = {
            "game_id": game_id,
            "current_scene": "Ancient Forest Clearing",
            "scene_image_url": "/api/placeholder/600/300",
            "scene_type": "exploration",
            "objectives": [
                "Find the lost artifact",
                "Rescue the trapped villagers",
                "Defeat the shadow cultists"
            ],
            "recent_events": [
                "Discovered ancient ruins",
                "Met a mysterious elf ranger",
                "Found tracks of the missing caravan"
            ],
            "current_location": "The Whispering Woods - Ancient Clearing",
            "party_members": [],
            "session_id": f"session_{game_id}_{datetime.utcnow().timestamp()}",
            "last_updated": datetime.utcnow().isoformat()
        }
        
        return {
            "success": True,
            "data": game_state
        }
        
    except Exception as e:
        logger.error(f"❌ Error fetching game state: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch game state: {str(e)}")

@router.put("/games/{game_id}/state")
async def update_game_state(
    game_id: str,
    updates: GameStateUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Update the game state"""
    try:
        # Apply updates (in a real implementation, update database)
        update_data = {k: v for k, v in updates.dict().items() if v is not None}
        
        logger.info(f"🔄 Updating game {game_id} state: {update_data}")
        
        # Broadcast updates to all players via WebSocket
        background_tasks.add_task(
            notify_game_players,
            game_id,
            "game_state_update",
            update_data
        )
        
        return {
            "success": True,
            "data": update_data,
            "message": "Game state updated successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Error updating game state: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update game state: {str(e)}")

@router.get("/characters/{character_id}")
async def get_character(
    character_id: int,
    db: Session = Depends(get_db)
):
    """Get character data"""
    try:
        # In a real implementation, fetch from database
        character_data = {
            "id": character_id,
            "name": "Elara Brightblade",
            "class": "Paladin",
            "race": "Half-Elf",
            "level": 5,
            "current_hp": 42,
            "max_hp": 55,
            "armor_class": 18,
            "location": "The Whispering Woods",
            "status_effects": ["Blessed", "Alert"],
            "inventory": [
                {
                    "id": 1,
                    "name": "Longsword +1",
                    "description": "A magical blade that glows faintly",
                    "quantity": 1,
                    "type": "weapon"
                },
                {
                    "id": 2,
                    "name": "Healing Potion",
                    "description": "Restores 2d4+2 HP",
                    "quantity": 3,
                    "type": "consumable"
                }
            ]
        }
        
        return {
            "success": True,
            "data": character_data
        }
        
    except Exception as e:
        logger.error(f"❌ Error fetching character: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch character: {str(e)}")

@router.put("/characters/{character_id}")
async def update_character(
    character_id: int,
    updates: CharacterUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Update character data"""
    try:
        # Apply updates (in a real implementation, update database)
        update_data = {k: v for k, v in updates.dict().items() if v is not None}
        
        logger.info(f"👤 Updating character {character_id}: {update_data}")
        
        # Broadcast updates to relevant game sessions via WebSocket
        # For now, we'll assume the character is in a default game
        background_tasks.add_task(
            notify_game_players,
            "default",  # In real implementation, get actual game_id
            "character_update",
            {
                "character_id": character_id,
                "updates": update_data
            }
        )
        
        return {
            "success": True,
            "data": update_data,
            "message": "Character updated successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Error updating character: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update character: {str(e)}")

async def generate_ai_response(action: PlayerActionRequest, game_id: str) -> GameActionResponse:
    """Generate AI response to player action (placeholder implementation)"""
    
    # This is a placeholder - in a real implementation, this would:
    # 1. Integrate with your AI service (OpenAI, Anthropic, etc.)
    # 2. Consider game context, character stats, current scene
    # 3. Generate appropriate narrative responses
    # 4. Determine if scene changes or character updates are needed
    
    response_templates = {
        "action": f"You {action.content}. The world responds to your actions...",
        "speech": f'You say: "{action.content}". Your words echo in the current scene...',
        "thought": f"You think to yourself: {action.content}. Your contemplation reveals new insights..."
    }
    
    base_response = response_templates.get(action.action_type, "The game continues...")
    
    return GameActionResponse(
        success=True,
        message_id=f"dm_{datetime.utcnow().timestamp()}",
        player_message={
            "id": f"player_{datetime.utcnow().timestamp()}",
            "type": f"player_{action.action_type}",
            "content": action.content,
            "timestamp": datetime.utcnow().isoformat(),
            "character_name": "Elara Brightblade",
            "metadata": action.metadata
        },
        ai_response={
            "id": f"dm_{datetime.utcnow().timestamp()}",
            "type": "dm_narration",
            "content": base_response,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": {
                "generated_by": "fallback",
                "response_to": f"player_{datetime.utcnow().timestamp()}"
            }
        },
        game_state_updates={
            "real_time_played": 1
        }
    )

@router.get("/games/{game_id}/debug/connections")
async def debug_game_connections(game_id: str):
    """Debug endpoint to see active connections for a game"""
    from api.websocket import get_game_rooms, get_active_connections
    
    game_rooms = get_game_rooms()
    active_connections = get_active_connections()
    
    return {
        "game_id": game_id,
        "connections_in_game": game_rooms.get(game_id, []),
        "total_active_connections": len(active_connections),
        "all_game_rooms": list(game_rooms.keys())
    } 