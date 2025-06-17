"""
Quest API endpoints for managing quests, objectives, and rewards.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from schemas.quest import (
    QuestCreate, QuestUpdate, QuestResponse,
    QuestObjectiveCreate, QuestObjectiveUpdate, QuestObjectiveResponse,
    QuestRewardResponse, QuestAcceptResponse, QuestCompletionResponse
)
from models.quest import Quest, QuestObjective, QuestReward, CharacterQuest
from database import get_db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/quests", tags=["quests"])


# Quest Management
@router.post("/", response_model=QuestResponse)
async def create_quest(
    quest: QuestCreate,
    db: Session = Depends(get_db)
):
    """Create a new quest."""
    try:
        # Create the quest
        db_quest = Quest(
            title=quest.title,
            description=quest.description,
            quest_type=quest.quest_type,
            difficulty_level=quest.difficulty_level,
            required_level=quest.required_level,
            time_limit_hours=quest.time_limit_hours,
            prerequisite_quest_ids=quest.prerequisite_quest_ids,
            location=quest.location,
            giver_name=quest.giver_name,
            is_active=quest.is_active,
            is_repeatable=quest.is_repeatable
        )
        
        db.add(db_quest)
        db.flush()  # Get the quest ID
        
        # Create objectives
        for obj_data in quest.objectives:
            objective = QuestObjective(
                quest_id=db_quest.id,
                description=obj_data.description,
                objective_type=obj_data.objective_type,
                target_type=obj_data.target_type,
                target_id=obj_data.target_id,
                required_amount=obj_data.required_amount,
                order_index=obj_data.order_index
            )
            db.add(objective)
        
        # Create rewards
        for reward_data in quest.rewards:
            reward = QuestReward(
                quest_id=db_quest.id,
                reward_type=reward_data.reward_type,
                reward_id=reward_data.reward_id,
                amount=reward_data.amount,
                rarity=reward_data.rarity
            )
            db.add(reward)
        
        db.commit()
        db.refresh(db_quest)
        
        logger.info(f"Created quest: {db_quest.id} - {db_quest.title}")
        return db_quest
        
    except Exception as e:
        logger.error(f"Error creating quest: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create quest")


@router.get("/available/{character_id}", response_model=List[QuestResponse])
async def get_available_quests(
    character_id: int,
    quest_type: Optional[str] = None,
    difficulty_level: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get available quests for a character."""
    try:
        # Get character to check level and completed quests
        from models.character import Character
        character = db.query(Character).filter(Character.id == character_id).first()
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")
        
        # Get quests the character has already accepted or completed
        character_quest_ids = db.query(CharacterQuest.quest_id).filter(
            CharacterQuest.character_id == character_id
        ).subquery()
        
        # Build quest query
        query = db.query(Quest).filter(
            Quest.is_active == True,
            Quest.required_level <= character.level,
            ~Quest.id.in_(character_quest_ids)
        )
        
        if quest_type:
            query = query.filter(Quest.quest_type == quest_type)
        
        if difficulty_level:
            query = query.filter(Quest.difficulty_level == difficulty_level)
        
        quests = query.all()
        
        # Filter by prerequisites
        available_quests = []
        for quest in quests:
            if quest.prerequisite_quest_ids:
                # Check if all prerequisite quests are completed
                completed_quests = db.query(CharacterQuest.quest_id).filter(
                    CharacterQuest.character_id == character_id,
                    CharacterQuest.status == 'completed',
                    CharacterQuest.quest_id.in_(quest.prerequisite_quest_ids)
                ).count()
                
                if completed_quests == len(quest.prerequisite_quest_ids):
                    available_quests.append(quest)
            else:
                available_quests.append(quest)
        
        logger.info(f"Retrieved {len(available_quests)} available quests for character {character_id}")
        return available_quests
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving available quests: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve available quests")


@router.get("/character/{character_id}", response_model=List[QuestResponse])
async def get_character_quests(
    character_id: int,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get quests for a character, optionally filtered by status."""
    try:
        query = db.query(Quest).join(CharacterQuest).filter(
            CharacterQuest.character_id == character_id
        )
        
        if status:
            query = query.filter(CharacterQuest.status == status)
        
        quests = query.all()
        
        # Add character quest status to each quest
        for quest in quests:
            character_quest = db.query(CharacterQuest).filter(
                CharacterQuest.character_id == character_id,
                CharacterQuest.quest_id == quest.id
            ).first()
            quest.character_status = character_quest.status if character_quest else None
            quest.accepted_at = character_quest.accepted_at if character_quest else None
            quest.completed_at = character_quest.completed_at if character_quest else None
        
        logger.info(f"Retrieved {len(quests)} quests for character {character_id}")
        return quests
        
    except Exception as e:
        logger.error(f"Error retrieving character quests: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve character quests")


@router.post("/accept/{quest_id}", response_model=QuestAcceptResponse)
async def accept_quest(
    quest_id: int,
    character_id: int,
    db: Session = Depends(get_db)
):
    """Accept a quest for a character."""
    try:
        # Check if quest exists and is available
        quest = db.query(Quest).filter(Quest.id == quest_id, Quest.is_active == True).first()
        if not quest:
            raise HTTPException(status_code=404, detail="Quest not found or not available")
        
        # Check if character exists
        from models.character import Character
        character = db.query(Character).filter(Character.id == character_id).first()
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")
        
        # Check if character meets requirements
        if character.level < quest.required_level:
            raise HTTPException(status_code=400, detail="Character level too low")
        
        # Check if quest is already accepted
        existing = db.query(CharacterQuest).filter(
            CharacterQuest.character_id == character_id,
            CharacterQuest.quest_id == quest_id
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail="Quest already accepted")
        
        # Check prerequisites
        if quest.prerequisite_quest_ids:
            completed_quests = db.query(CharacterQuest.quest_id).filter(
                CharacterQuest.character_id == character_id,
                CharacterQuest.status == 'completed',
                CharacterQuest.quest_id.in_(quest.prerequisite_quest_ids)
            ).count()
            
            if completed_quests < len(quest.prerequisite_quest_ids):
                raise HTTPException(status_code=400, detail="Prerequisites not met")
        
        # Create character quest
        character_quest = CharacterQuest(
            character_id=character_id,
            quest_id=quest_id,
            status='active',
            accepted_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=quest.time_limit_hours) if quest.time_limit_hours else None
        )
        
        db.add(character_quest)
        db.commit()
        
        logger.info(f"Character {character_id} accepted quest {quest_id}")
        return QuestAcceptResponse(
            quest_id=quest_id,
            character_id=character_id,
            accepted_at=character_quest.accepted_at,
            expires_at=character_quest.expires_at,
            message="Quest accepted successfully!"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error accepting quest: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to accept quest")


@router.post("/progress/{quest_id}")
async def update_quest_progress(
    quest_id: int,
    character_id: int,
    objective_id: int,
    progress_amount: int = 1,
    db: Session = Depends(get_db)
):
    """Update progress on a quest objective."""
    try:
        # Check if character has this quest
        character_quest = db.query(CharacterQuest).filter(
            CharacterQuest.character_id == character_id,
            CharacterQuest.quest_id == quest_id,
            CharacterQuest.status == 'active'
        ).first()
        
        if not character_quest:
            raise HTTPException(status_code=404, detail="Active quest not found for character")
        
        # Get or create objective progress
        from models.quest import QuestObjectiveProgress
        progress = db.query(QuestObjectiveProgress).filter(
            QuestObjectiveProgress.character_quest_id == character_quest.id,
            QuestObjectiveProgress.objective_id == objective_id
        ).first()
        
        if not progress:
            progress = QuestObjectiveProgress(
                character_quest_id=character_quest.id,
                objective_id=objective_id,
                current_amount=0
            )
            db.add(progress)
        
        # Update progress
        progress.current_amount = min(
            progress.current_amount + progress_amount,
            progress.objective.required_amount
        )
        
        # Check if objective is completed
        if progress.current_amount >= progress.objective.required_amount:
            progress.completed_at = datetime.utcnow()
        
        db.commit()
        
        # Check if all objectives are completed
        quest = db.query(Quest).filter(Quest.id == quest_id).first()
        total_objectives = len(quest.objectives)
        completed_objectives = db.query(QuestObjectiveProgress).filter(
            QuestObjectiveProgress.character_quest_id == character_quest.id,
            QuestObjectiveProgress.completed_at.isnot(None)
        ).count()
        
        if completed_objectives == total_objectives:
            # Quest completed!
            character_quest.status = 'completed'
            character_quest.completed_at = datetime.utcnow()
            db.commit()
            
            logger.info(f"Quest {quest_id} completed by character {character_id}")
            return {"message": "Quest completed!", "quest_completed": True}
        
        logger.info(f"Updated quest {quest_id} objective {objective_id} progress for character {character_id}")
        return {"message": "Progress updated", "quest_completed": False}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating quest progress: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update quest progress")


@router.get("/{quest_id}", response_model=QuestResponse)
async def get_quest(quest_id: int, db: Session = Depends(get_db)):
    """Get a specific quest by ID."""
    try:
        quest = db.query(Quest).filter(Quest.id == quest_id).first()
        if not quest:
            raise HTTPException(status_code=404, detail="Quest not found")
        
        return quest
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving quest: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve quest")


@router.put("/{quest_id}", response_model=QuestResponse)
async def update_quest(
    quest_id: int,
    quest_update: QuestUpdate,
    db: Session = Depends(get_db)
):
    """Update a quest."""
    try:
        db_quest = db.query(Quest).filter(Quest.id == quest_id).first()
        if not db_quest:
            raise HTTPException(status_code=404, detail="Quest not found")
        
        update_data = quest_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_quest, field, value)
        
        db.commit()
        db.refresh(db_quest)
        
        logger.info(f"Updated quest: {quest_id}")
        return db_quest
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating quest: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update quest")


@router.delete("/{quest_id}")
async def delete_quest(quest_id: int, db: Session = Depends(get_db)):
    """Delete a quest."""
    try:
        db_quest = db.query(Quest).filter(Quest.id == quest_id).first()
        if not db_quest:
            raise HTTPException(status_code=404, detail="Quest not found")
        
        # Check if quest is in use
        active_character_quests = db.query(CharacterQuest).filter(
            CharacterQuest.quest_id == quest_id,
            CharacterQuest.status == 'active'
        ).count()
        
        if active_character_quests > 0:
            raise HTTPException(status_code=400, detail="Cannot delete quest with active assignments")
        
        db.delete(db_quest)
        db.commit()
        
        logger.info(f"Deleted quest: {quest_id}")
        return {"message": "Quest deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting quest: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete quest")


@router.post("/daily/generate/{character_id}")
async def generate_daily_quests(
    character_id: int,
    count: int = 3,
    db: Session = Depends(get_db)
):
    """Generate daily quests for a character."""
    try:
        from services.quest_generator import QuestGenerator
        
        # Check if character exists
        from models.character import Character
        character = db.query(Character).filter(Character.id == character_id).first()
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")
        
        # Generate daily quests
        quest_generator = QuestGenerator()
        daily_quests = quest_generator.generate_daily_quests(character, count, db)
        
        logger.info(f"Generated {len(daily_quests)} daily quests for character {character_id}")
        return {"message": f"Generated {len(daily_quests)} daily quests", "quests": daily_quests}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating daily quests: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate daily quests") 