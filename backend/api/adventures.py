from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from database import get_db
from models.character import Character
from models.story import StoryArc
from schemas.adventure import (
    AdventureCreate, 
    AdventureResponse, 
    AdventureUpdate,
    AdventureProgress,
    AdventureListResponse
)
from services.auth import get_current_user
from services.adventure_generator import AdventureGeneratorService
from services.ai_dm import AIDMService

router = APIRouter()

@router.post("/", response_model=AdventureResponse)
async def create_adventure(
    adventure_data: AdventureCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new adventure for a character"""
    try:
        # Verify character ownership
        character = db.query(Character).filter(
            Character.id == adventure_data.character_id,
            Character.user_id == current_user['user_id']
        ).first()
        
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")

        # Generate adventure using AI service
        adventure_service = AdventureGeneratorService()
        story_content = await adventure_service.generate_adventure_story(
            character_data={
                "name": character.name,
                "race": character.race,
                "character_class": character.character_class,
                "level": character.level,
                "background": getattr(character, 'background', 'Unknown')
            },
            preferences={
                "story_type": adventure_data.story_type,
                "themes": adventure_data.themes,
                "difficulty": adventure_data.difficulty,
                "estimated_duration": adventure_data.estimated_duration
            }
        )

        # Create story record
        story = StoryArc(
            character_id=adventure_data.character_id,
            current_stage="intro",
            story_type=adventure_data.story_type,
            story_seed=adventure_data.story_seed,
            title=story_content.get("title", f"Adventure of {character.name}"),
            story_summary=story_content.get("summary", ""),
            world_state=story_content.get("world_state", {}),
            stage_data=story_content.get("stages", {}),
            created_at=datetime.utcnow(),
            started_at=datetime.utcnow()
        )
        
        db.add(story)
        db.commit()
        db.refresh(story)

        return AdventureResponse(
            id=story.id,
            character_id=story.character_id,
            title=story.title,
            story_type=story.story_type,
            current_stage=story.current_stage,
            stages_completed=[],
            story_completed=False,
            created_at=story.created_at,
            started_at=story.started_at,
            story_summary=story.story_summary,
            difficulty=adventure_data.difficulty,
            estimated_duration=adventure_data.estimated_duration,
            themes=adventure_data.themes
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create adventure: {str(e)}")

@router.get("/character/{character_id}", response_model=List[AdventureListResponse])
async def get_character_adventures(
    character_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    status: Optional[str] = Query(None, description="Filter by completion status"),
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0)
):
    """Get all adventures for a specific character"""
    try:
        # Verify character ownership
        character = db.query(Character).filter(
            Character.id == character_id,
            Character.user_id == current_user['user_id']
        ).first()
        
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")

        # Build query
        query = db.query(StoryArc).filter(StoryArc.character_id == character_id)
        
        if status == "completed":
            query = query.filter(StoryArc.story_completed == True)
        elif status == "active":
            query = query.filter(StoryArc.story_completed == False)

        stories = query.order_by(StoryArc.created_at.desc()).offset(offset).limit(limit).all()

        return [
            AdventureListResponse(
                id=story.id,
                character_id=story.character_id,
                title=story.title or f"Adventure {story.id}",
                story_type=story.story_type,
                current_stage=story.current_stage,
                story_completed=story.story_completed,
                created_at=story.created_at,
                completed_at=story.completed_at,
                stages_completed=story.stages_completed or [],
                progress_percentage=len(story.stages_completed or []) * 16.67 if story.stages_completed else 0  # 6 stages = 100%
            ) for story in stories
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get adventures: {str(e)}")

@router.get("/{adventure_id}", response_model=AdventureResponse)
async def get_adventure_details(
    adventure_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific adventure"""
    try:
        # Get story with character verification
        story = db.query(StoryArc).join(Character).filter(
            StoryArc.id == adventure_id,
            Character.user_id == current_user['user_id']
        ).first()
        
        if not story:
            raise HTTPException(status_code=404, detail="Adventure not found")

        return AdventureResponse(
            id=story.id,
            character_id=story.character_id,
            title=story.title,
            story_type=story.story_type,
            current_stage=story.current_stage,
            stages_completed=story.stages_completed or [],
            story_completed=story.story_completed,
            completion_type=story.completion_type,
            created_at=story.created_at,
            started_at=story.started_at,
            completed_at=story.completed_at,
            story_seed=story.story_seed,
            story_summary=story.story_summary,
            world_state=story.world_state,
            stage_data=story.stage_data,
            major_decisions=getattr(story, 'major_decisions', []),
            character_progression=getattr(story, 'character_progression', {}),
            total_play_time=getattr(story, 'total_play_time', 0)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get adventure: {str(e)}")

@router.put("/{adventure_id}/progress", response_model=AdventureResponse)
async def update_adventure_progress(
    adventure_id: int,
    progress_data: AdventureProgress,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update adventure progress and stage"""
    try:
        # Get story with character verification
        story = db.query(StoryArc).join(Character).filter(
            StoryArc.id == adventure_id,
            Character.user_id == current_user['user_id']
        ).first()
        
        if not story:
            raise HTTPException(status_code=404, detail="Adventure not found")

        # Update progress
        if progress_data.current_stage:
            story.current_stage = progress_data.current_stage
        
        if progress_data.stages_completed:
            story.stages_completed = progress_data.stages_completed
        
        if progress_data.story_completed is not None:
            story.story_completed = progress_data.story_completed
            if progress_data.story_completed and not story.completed_at:
                story.completed_at = datetime.utcnow()
        
        if progress_data.completion_type:
            story.completion_type = progress_data.completion_type

        if progress_data.world_state_updates:
            current_world_state = story.world_state or {}
            current_world_state.update(progress_data.world_state_updates)
            story.world_state = current_world_state

        story.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(story)

        return AdventureResponse(
            id=story.id,
            character_id=story.character_id,
            title=story.title,
            story_type=story.story_type,
            current_stage=story.current_stage,
            stages_completed=story.stages_completed or [],
            story_completed=story.story_completed,
            completion_type=story.completion_type,
            created_at=story.created_at,
            started_at=story.started_at,
            completed_at=story.completed_at,
            story_summary=story.story_summary,
            world_state=story.world_state,
            stage_data=story.stage_data
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update adventure: {str(e)}")

@router.put("/{adventure_id}", response_model=AdventureResponse)
async def update_adventure(
    adventure_id: int,
    adventure_update: AdventureUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update adventure metadata and settings"""
    try:
        # Get story with character verification
        story = db.query(StoryArc).join(Character).filter(
            StoryArc.id == adventure_id,
            Character.user_id == current_user['user_id']
        ).first()
        
        if not story:
            raise HTTPException(status_code=404, detail="Adventure not found")

        # Update fields
        if adventure_update.title:
            story.title = adventure_update.title
        if adventure_update.story_summary:
            story.story_summary = adventure_update.story_summary
        if adventure_update.story_seed:
            story.story_seed = adventure_update.story_seed

        story.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(story)

        return AdventureResponse(
            id=story.id,
            character_id=story.character_id,
            title=story.title,
            story_type=story.story_type,
            current_stage=story.current_stage,
            stages_completed=story.stages_completed or [],
            story_completed=story.story_completed,
            created_at=story.created_at,
            started_at=story.started_at,
            completed_at=story.completed_at,
            story_summary=story.story_summary,
            world_state=story.world_state
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update adventure: {str(e)}")

@router.delete("/{adventure_id}")
async def delete_adventure(
    adventure_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an adventure"""
    try:
        # Get story with character verification
        story = db.query(StoryArc).join(Character).filter(
            StoryArc.id == adventure_id,
            Character.user_id == current_user['user_id']
        ).first()
        
        if not story:
            raise HTTPException(status_code=404, detail="Adventure not found")

        db.delete(story)
        db.commit()

        return {"message": "Adventure deleted successfully"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete adventure: {str(e)}")

@router.post("/{adventure_id}/resume")
async def resume_adventure(
    adventure_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Resume an adventure and get current game state"""
    try:
        # Get story with character verification
        story = db.query(StoryArc).join(Character).filter(
            StoryArc.id == adventure_id,
            Character.user_id == current_user['user_id']
        ).first()
        
        if not story:
            raise HTTPException(status_code=404, detail="Adventure not found")

        if story.story_completed:
            raise HTTPException(status_code=400, detail="Cannot resume completed adventure")

        # Initialize AI DM service for the adventure
        ai_dm = AIDMService()
        current_scene = await ai_dm.get_current_scene(story.id, story.current_stage)
        
        return {
            "adventure_id": story.id,
            "current_stage": story.current_stage,
            "scene_description": current_scene.get("description", ""),
            "scene_image_url": current_scene.get("image_url", ""),
            "available_actions": current_scene.get("actions", []),
            "objectives": current_scene.get("objectives", []),
            "world_state": story.world_state or {}
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to resume adventure: {str(e)}") 