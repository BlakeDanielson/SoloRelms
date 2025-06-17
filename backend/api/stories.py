"""
API endpoints for story state management and progression
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import os

from database import get_db
from auth import get_current_user_id, get_current_user
from models.story import StoryArc, WorldState, StoryStage
from models.character import Character
from models.user import User

# Add AI service import
try:
    from services.ai_service import AIService
    ai_service = AIService()
except ImportError:
    ai_service = None

router = APIRouter()

# Pydantic models for request/response
class StoryCreateRequest(BaseModel):
    character_id: int
    story_seed: Optional[str] = None
    story_type: str = Field(default="short_form", pattern="^(short_form|campaign)$")

class DecisionRequest(BaseModel):
    decision: str
    description: str
    consequences: Optional[List[str]] = []

class NPCStatusRequest(BaseModel):
    npc_id: str
    status_data: Dict[str, Any]

class CombatOutcomeRequest(BaseModel):
    encounter_type: str
    result: str
    damage_taken: Optional[int] = 0
    loot_gained: Optional[List[str]] = []
    xp_gained: Optional[int] = 0

class UpdateTitleRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)

class StoryResponse(BaseModel):
    id: int
    character_id: int
    title: Optional[str]
    current_stage: str
    stages_completed: List[str]
    story_completed: bool
    completion_type: Optional[str]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    story_seed: Optional[str]

class StoryDetailResponse(StoryResponse):
    major_decisions: List[Dict[str, Any]]
    npc_status: Dict[str, Any]
    combat_outcomes: List[Dict[str, Any]]
    final_rewards: Dict[str, Any]
    story_seed: Optional[str]

class WorldStateResponse(BaseModel):
    id: int
    current_location: str
    explored_areas: List[Dict[str, Any]]
    active_objectives: List[Dict[str, Any]]
    completed_objectives: List[Dict[str, Any]]
    story_time_elapsed: int
    real_time_played: int

@router.post("/stories", response_model=StoryResponse, status_code=status.HTTP_201_CREATED)
async def create_story(
    story_request: StoryCreateRequest,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """Create a new story arc for a character with AI-generated opening narrative"""
    
    # Verify character belongs to user
    character = db.query(Character).filter(
        and_(Character.id == story_request.character_id, Character.user_id == current_user_id)
    ).first()
    
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found or not owned by user"
        )
    
    # Check if character already has an active story
    active_story = db.query(StoryArc).filter(
        and_(
            StoryArc.character_id == story_request.character_id,
            StoryArc.story_completed == False
        )
    ).first()
    
    if active_story:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Character already has an active story. Complete or abandon current story first."
        )
    
    # Create new story arc
    story_arc = StoryArc(
        character_id=story_request.character_id,
        user_id=current_user_id,
        story_type=story_request.story_type,
        story_seed=story_request.story_seed,
        started_at=datetime.utcnow()
    )
    
    db.add(story_arc)
    db.commit()
    db.refresh(story_arc)
    
    # Generate opening narrative using AI
    opening_narrative = None
    if ai_service and story_request.story_seed:
        try:
            opening_prompt = f"""Create an immersive opening scene for a D&D adventure based on the following story seed:

STORY SEED: {story_request.story_seed}

CHARACTER INFO:
- Name: {character.name}
- Race: {character.race}
- Class: {character.character_class}
- Level: {character.level}

REQUIREMENTS:
1. Welcome the character by name
2. Set the scene based on the story seed
3. Describe the environment, atmosphere, and immediate surroundings
4. Hint at the adventure ahead without giving everything away
5. End with what the character can see/do next
6. Keep it 2-3 paragraphs, immersive but not overwhelming
7. Make it feel like the start of an epic adventure

Format as a direct narrative to the player (use "you" and address them as their character)."""

            ai_result = ai_service.generate_response(opening_prompt, max_tokens=500, temperature=0.8)
            
            if ai_result.get('success') and ai_result.get('content'):
                opening_narrative = ai_result.get('content').strip()
                print(f"✅ Generated AI opening narrative for character {character.name}")
            else:
                print(f"⚠️ AI generation failed or returned empty content")
                raise Exception("AI returned empty content")
            
        except Exception as e:
            print(f"❌ Failed to generate opening narrative: {e}")
            # Fallback narrative
            opening_narrative = f"""Welcome to your adventure, {character.name}!

As a {character.race} {character.character_class}, you find yourself at the beginning of what promises to be an extraordinary journey. The world around you is filled with mystery and possibility, and your skills as a level {character.level} adventurer will be put to the test.

{story_request.story_seed if story_request.story_seed else "Your adventure awaits, filled with danger and discovery."}

What would you like to do?"""
    else:
        # Generate fallback when no AI service or story seed
        opening_narrative = f"""Welcome to your adventure, {character.name}!

As a {character.race} {character.character_class}, you find yourself at the beginning of what promises to be an extraordinary journey. Your skills as a level {character.level} adventurer will be put to the test.

{story_request.story_seed if story_request.story_seed else "Your adventure awaits, filled with danger and discovery."}

What would you like to do?"""
    
    # Create initial world state
    world_state = WorldState(
        story_arc_id=story_arc.id,
        current_location="Adventure Starting Point"
    )
    db.add(world_state)
    
    # Store opening narrative in story arc for easy access
    if opening_narrative:
        story_arc.ai_context_summary = opening_narrative
    
    db.commit()
    db.refresh(story_arc)
    
    return StoryResponse(
        id=story_arc.id,
        character_id=story_arc.character_id,
        title=story_arc.title,
        current_stage=story_arc.current_stage.value,
        stages_completed=story_arc.stages_completed or [],
        story_completed=story_arc.story_completed,
        completion_type=story_arc.completion_type,
        created_at=story_arc.created_at,
        started_at=story_arc.started_at,
        completed_at=story_arc.completed_at,
        story_seed=story_arc.story_seed
    )

@router.get("/stories", response_model=List[StoryResponse])
async def get_user_stories(
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
    active_only: bool = False
):
    """Get all stories for the current user"""
    
    query = db.query(StoryArc).filter(StoryArc.user_id == current_user_id)
    
    if active_only:
        query = query.filter(StoryArc.story_completed == False)
    
    stories = query.order_by(StoryArc.created_at.desc()).all()
    
    return [
        StoryResponse(
            id=story.id,
            character_id=story.character_id,
            title=story.title,
            current_stage=story.current_stage.value,
            stages_completed=story.stages_completed or [],
            story_completed=story.story_completed,
            completion_type=story.completion_type,
            created_at=story.created_at,
            started_at=story.started_at,
            completed_at=story.completed_at,
            story_seed=story.story_seed
        )
        for story in stories
    ]

@router.get("/stories/{story_id}", response_model=StoryDetailResponse)
async def get_story_details(
    story_id: int,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """Get detailed information about a specific story"""
    
    story = db.query(StoryArc).filter(
        and_(StoryArc.id == story_id, StoryArc.user_id == current_user_id)
    ).first()
    
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Story not found"
        )
    
    return StoryDetailResponse(
        id=story.id,
        character_id=story.character_id,
        title=story.title,
        current_stage=story.current_stage.value,
        stages_completed=story.stages_completed or [],
        story_completed=story.story_completed,
        completion_type=story.completion_type,
        created_at=story.created_at,
        started_at=story.started_at,
        completed_at=story.completed_at,
        major_decisions=story.major_decisions or [],
        npc_status=story.npc_status or {},
        combat_outcomes=story.combat_outcomes or [],
        final_rewards=story.final_rewards or {},
        story_seed=story.story_seed
    )

@router.post("/stories/{story_id}/advance", response_model=StoryResponse)
async def advance_story_stage(
    story_id: int,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """Advance story to the next stage"""
    
    story = db.query(StoryArc).filter(
        and_(StoryArc.id == story_id, StoryArc.user_id == current_user_id)
    ).first()
    
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Story not found"
        )
    
    if story.story_completed:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Story is already completed"
        )
    
    if not story.can_advance_stage():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot advance from {story.current_stage.value}. Requirements not met."
        )
    
    story.advance_stage()
    db.commit()
    db.refresh(story)
    
    return StoryResponse(
        id=story.id,
        character_id=story.character_id,
        title=story.title,
        current_stage=story.current_stage.value,
        stages_completed=story.stages_completed or [],
        story_completed=story.story_completed,
        completion_type=story.completion_type,
        created_at=story.created_at,
        started_at=story.started_at,
        completed_at=story.completed_at,
        story_seed=story.story_seed
    )

@router.post("/stories/{story_id}/decisions")
async def add_story_decision(
    story_id: int,
    decision_request: DecisionRequest,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """Add a major story decision"""
    
    story = db.query(StoryArc).filter(
        and_(StoryArc.id == story_id, StoryArc.user_id == current_user_id)
    ).first()
    
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Story not found"
        )
    
    if story.story_completed:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot add decisions to completed story"
        )
    
    decision_data = {
        "decision": decision_request.decision,
        "description": decision_request.description,
        "consequences": decision_request.consequences
    }
    
    story.add_decision(decision_data)
    db.commit()
    
    return {"message": "Decision added successfully", "decision": decision_data}

@router.post("/stories/{story_id}/npcs")
async def update_npc_status(
    story_id: int,
    npc_request: NPCStatusRequest,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """Update NPC status in a story"""
    
    story = db.query(StoryArc).filter(
        and_(StoryArc.id == story_id, StoryArc.user_id == current_user_id)
    ).first()
    
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Story not found"
        )
    
    story.update_npc_status(npc_request.npc_id, npc_request.status_data)
    db.commit()
    
    return {
        "message": "NPC status updated successfully",
        "npc_id": npc_request.npc_id,
        "status": npc_request.status_data
    }

@router.post("/stories/{story_id}/combat")
async def add_combat_outcome(
    story_id: int,
    combat_request: CombatOutcomeRequest,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """Record a combat encounter outcome"""
    
    story = db.query(StoryArc).filter(
        and_(StoryArc.id == story_id, StoryArc.user_id == current_user_id)
    ).first()
    
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Story not found"
        )
    
    if story.story_completed:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot add combat to completed story"
        )
    
    combat_data = {
        "encounter_type": combat_request.encounter_type,
        "result": combat_request.result,
        "damage_taken": combat_request.damage_taken,
        "loot_gained": combat_request.loot_gained,
        "xp_gained": combat_request.xp_gained
    }
    
    story.add_combat_outcome(combat_data)
    db.commit()
    
    return {"message": "Combat outcome recorded successfully", "combat": combat_data}

@router.get("/stories/{story_id}/world", response_model=WorldStateResponse)
async def get_world_state(
    story_id: int,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """Get the world state for a story"""
    
    # Verify story ownership
    story = db.query(StoryArc).filter(
        and_(StoryArc.id == story_id, StoryArc.user_id == current_user_id)
    ).first()
    
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Story not found"
        )
    
    world_state = db.query(WorldState).filter(WorldState.story_arc_id == story_id).first()
    
    if not world_state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="World state not found"
        )
    
    return WorldStateResponse(
        id=world_state.id,
        current_location=world_state.current_location,
        explored_areas=world_state.explored_areas or [],
        active_objectives=world_state.active_objectives or [],
        completed_objectives=world_state.completed_objectives or [],
        story_time_elapsed=world_state.story_time_elapsed,
        real_time_played=world_state.real_time_played
    )

@router.put("/stories/{story_id}/title")
async def update_story_title(
    story_id: int,
    title_request: UpdateTitleRequest,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """Update story title"""
    
    story = db.query(StoryArc).filter(
        and_(StoryArc.id == story_id, StoryArc.user_id == current_user_id)
    ).first()
    
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Story not found"
        )
    
    story.title = title_request.title
    db.commit()
    
    return {"message": "Story title updated successfully", "title": title_request.title}

@router.delete("/stories/{story_id}")
async def abandon_story(
    story_id: int,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """Abandon/delete a story arc"""
    
    story = db.query(StoryArc).filter(
        and_(StoryArc.id == story_id, StoryArc.user_id == current_user_id)
    ).first()
    
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Story not found"
        )
    
    # Mark as completed with failure type rather than deleting
    story.story_completed = True
    story.completion_type = "abandoned"
    story.completed_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Story abandoned successfully"}

# Add new endpoint to get opening narrative
@router.get("/stories/{story_id}/opening", response_model=Dict[str, Any])
async def get_opening_narrative(
    story_id: int,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """Get the opening narrative for a story"""
    
    story = db.query(StoryArc).filter(
        and_(StoryArc.id == story_id, StoryArc.user_id == current_user_id)
    ).first()
    
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Story not found"
        )
    
    # Get character for fallback
    character = db.query(Character).filter(Character.id == story.character_id).first()
    
    opening_narrative = story.ai_context_summary
    
    # Generate fallback if no opening narrative exists
    if not opening_narrative and character:
        opening_narrative = f"""Welcome to your adventure, {character.name}!

As a {character.race} {character.character_class}, you find yourself at the beginning of what promises to be an extraordinary journey. Your skills as a level {character.level} adventurer will be put to the test.

What would you like to do?"""
    
    return {
        "opening_narrative": opening_narrative,
        "character_name": character.name if character else "Unknown",
        "story_id": story_id
    } 