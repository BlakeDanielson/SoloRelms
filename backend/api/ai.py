"""
AI API endpoints for GPT-4o integration
Handles AI-powered story narration, combat descriptions, NPC interactions, and decision outcomes.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from database import get_db
from services.ai_service import ai_service
from models.character import Character
from models.story import StoryArc, WorldState
from models.combat import CombatEncounter


router = APIRouter(prefix="/ai", tags=["AI"])


# Request/Response Models
class StoryNarrationRequest(BaseModel):
    character_id: int = Field(..., description="Character ID")
    story_arc_id: int = Field(..., description="Story arc ID")
    player_action: Optional[str] = Field(None, description="Player action to narrate")
    additional_context: Optional[str] = Field(None, description="Additional context for narration")
    
    class Config:
        json_schema_extra = {
            "example": {
                "character_id": 1,
                "story_arc_id": 1,
                "player_action": "I carefully examine the mysterious door for traps",
                "additional_context": "The door has strange runic symbols glowing faintly"
            }
        }


class CombatNarrationRequest(BaseModel):
    character_id: int = Field(..., description="Character ID")
    story_arc_id: int = Field(..., description="Story arc ID")
    combat_encounter_id: int = Field(..., description="Combat encounter ID")
    combat_action: Dict[str, Any] = Field(..., description="Combat action taken")
    combat_result: Dict[str, Any] = Field(..., description="Result of the combat action")
    
    class Config:
        json_schema_extra = {
            "example": {
                "character_id": 1,
                "story_arc_id": 1,
                "combat_encounter_id": 1,
                "combat_action": {
                    "action_type": "attack",
                    "target": "goblin_warrior",
                    "weapon": "longsword",
                    "attack_roll": 18
                },
                "combat_result": {
                    "hit": True,
                    "damage": 8,
                    "damage_type": "slashing",
                    "critical": False
                }
            }
        }


class NPCInteractionRequest(BaseModel):
    character_id: int = Field(..., description="Character ID")
    story_arc_id: int = Field(..., description="Story arc ID")
    npc_name: str = Field(..., description="NPC name")
    interaction_type: str = Field(..., description="Type of interaction (dialogue, persuasion, etc.)")
    player_input: str = Field(..., description="What the player says or does")
    
    class Config:
        json_schema_extra = {
            "example": {
                "character_id": 1,
                "story_arc_id": 1,
                "npc_name": "tavern_keeper_aldric",
                "interaction_type": "dialogue",
                "player_input": "Good evening! I'm looking for information about the missing merchant caravan."
            }
        }


class DecisionOutcomeRequest(BaseModel):
    character_id: int = Field(..., description="Character ID")
    story_arc_id: int = Field(..., description="Story arc ID")
    decision: Dict[str, Any] = Field(..., description="Major decision data")
    
    class Config:
        json_schema_extra = {
            "example": {
                "character_id": 1,
                "story_arc_id": 1,
                "decision": {
                    "decision": "help_villager",
                    "description": "Chose to help the injured villager instead of pursuing the thief",
                    "consequences": ["villager_ally", "thief_escaped"]
                }
            }
        }


class CustomPromptRequest(BaseModel):
    prompt_type: str = Field(..., description="Type of prompt")
    custom_prompt: str = Field(..., description="Custom prompt text")
    max_tokens: Optional[int] = Field(1000, description="Maximum tokens for response")
    temperature: Optional[float] = Field(0.7, description="Temperature for response generation")
    
    class Config:
        json_schema_extra = {
            "example": {
                "prompt_type": "world_building",
                "custom_prompt": "Describe a mysterious ancient temple hidden in the forest",
                "max_tokens": 800,
                "temperature": 0.8
            }
        }


class AIResponse(BaseModel):
    success: bool = Field(..., description="Whether the AI request was successful")
    content: Optional[str] = Field(None, description="AI-generated content")
    usage: Optional[Dict[str, int]] = Field(None, description="Token usage information")
    model: Optional[str] = Field(None, description="AI model used")
    error: Optional[str] = Field(None, description="Error message if unsuccessful")


@router.post("/narrate-story", response_model=AIResponse, summary="Generate story narration")
async def narrate_story(
    request: StoryNarrationRequest,
    db: Session = Depends(get_db)
):
    """
    Generate AI-powered story narration based on character state, story arc, and optional player actions.
    
    This endpoint creates immersive narrative descriptions that:
    - Respond to player actions and choices
    - Maintain consistency with character and story state
    - Present new challenges and opportunities
    - Adapt to the current story stage
    """
    try:
        result = ai_service.narrate_story(
            db=db,
            character_id=request.character_id,
            story_arc_id=request.story_arc_id,
            player_action=request.player_action,
            additional_context=request.additional_context
        )
        
        if not result['success']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get('error', 'Failed to generate story narration')
            )
        
        return AIResponse(**result)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error generating story narration: {str(e)}"
        )


@router.post("/narrate-combat", response_model=AIResponse, summary="Generate combat narration")
async def narrate_combat(
    request: CombatNarrationRequest,
    db: Session = Depends(get_db)
):
    """
    Generate dynamic combat narration for actions and their results.
    
    This endpoint creates exciting combat descriptions that:
    - Vividly describe attacks, spells, and maneuvers
    - Show damage and effects with dramatic flair
    - Maintain combat pacing and tension
    - Describe enemy reactions and tactical changes
    """
    try:
        result = ai_service.narrate_combat(
            db=db,
            character_id=request.character_id,
            story_arc_id=request.story_arc_id,
            combat_encounter_id=request.combat_encounter_id,
            combat_action=request.combat_action,
            combat_result=request.combat_result
        )
        
        if not result['success']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get('error', 'Failed to generate combat narration')
            )
        
        return AIResponse(**result)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error generating combat narration: {str(e)}"
        )


@router.post("/npc-interaction", response_model=AIResponse, summary="Handle NPC interactions")
async def handle_npc_interaction(
    request: NPCInteractionRequest,
    db: Session = Depends(get_db)
):
    """
    Generate NPC dialogue and reactions to player interactions.
    
    This endpoint creates believable NPC responses that:
    - Match the NPC's personality and current disposition
    - React appropriately to player actions and dialogue
    - Provide information, quests, or story progression
    - Maintain character consistency across interactions
    """
    try:
        result = ai_service.handle_npc_interaction(
            db=db,
            character_id=request.character_id,
            story_arc_id=request.story_arc_id,
            npc_name=request.npc_name,
            interaction_type=request.interaction_type,
            player_input=request.player_input
        )
        
        if not result['success']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get('error', 'Failed to generate NPC interaction')
            )
        
        return AIResponse(**result)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error generating NPC interaction: {str(e)}"
        )


@router.post("/decision-outcome", response_model=AIResponse, summary="Process decision outcomes")
async def process_decision_outcome(
    request: DecisionOutcomeRequest,
    db: Session = Depends(get_db)
):
    """
    Generate narration for the consequences of major player decisions.
    
    This endpoint creates meaningful outcome descriptions that:
    - Show immediate and long-term consequences
    - Affect NPC relationships and world state
    - Create new story opportunities and challenges
    - Demonstrate the weight of player choices
    """
    try:
        result = ai_service.process_decision_outcome(
            db=db,
            character_id=request.character_id,
            story_arc_id=request.story_arc_id,
            decision=request.decision
        )
        
        if not result['success']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get('error', 'Failed to generate decision outcome')
            )
        
        return AIResponse(**result)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error generating decision outcome: {str(e)}"
        )


@router.post("/custom-prompt", response_model=AIResponse, summary="Generate custom AI content")
async def generate_custom_content(
    request: CustomPromptRequest
):
    """
    Generate AI content from a custom prompt.
    
    This endpoint allows for flexible content generation:
    - World building and location descriptions
    - Item and treasure descriptions
    - Quest and objective generation
    - Creative story elements
    """
    try:
        result = ai_service.generate_dynamic_content(
            prompt_type=request.prompt_type,
            custom_prompt=request.custom_prompt,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        
        if not result['success']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get('error', 'Failed to generate custom content')
            )
        
        return AIResponse(**result)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error generating custom content: {str(e)}"
        )


@router.get("/health", summary="Check AI service health")
async def check_ai_health():
    """
    Check if the AI service is properly configured and accessible.
    """
    try:
        # Test AI service with a simple prompt
        result = ai_service.generate_response(
            "Respond with 'AI service is working' if you can read this.",
            max_tokens=50,
            temperature=0.1
        )
        
        if result['success']:
            return {
                "status": "healthy",
                "model": result.get('model', 'unknown'),
                "message": "AI service is operational"
            }
        else:
            return {
                "status": "unhealthy",
                "error": result.get('error', 'Unknown error'),
                "message": "AI service is not responding properly"
            }
    
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "AI service health check failed"
        } 