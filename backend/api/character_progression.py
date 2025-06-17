from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime

from database import get_db
from models.character import Character
from schemas.character_progression import (
    CharacterProgressionResponse,
    LevelUpRequest,
    SkillUpgradeRequest,
    AttributeUpgradeRequest,
    AchievementResponse,
    ExperienceGainRequest
)
from services.auth import get_current_user
from services.character_progression import CharacterProgressionService

router = APIRouter()

@router.get("/{character_id}", response_model=CharacterProgressionResponse)
async def get_character_progression(
    character_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get character progression data including XP, skills, and achievements"""
    try:
        # Verify character ownership
        character = db.query(Character).filter(
            Character.id == character_id,
            Character.user_id == current_user['user_id']
        ).first()
        
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")

        progression_service = CharacterProgressionService()
        progression_data = await progression_service.get_character_progression(character)

        return CharacterProgressionResponse(
            character_id=character.id,
            current_level=character.level,
            current_xp=progression_data.get("current_xp", 0),
            xp_to_next_level=progression_data.get("xp_to_next_level", 1000),
            available_attribute_points=progression_data.get("available_attribute_points", 0),
            available_skill_points=progression_data.get("available_skill_points", 0),
            skills=progression_data.get("skills", []),
            achievements=progression_data.get("achievements", []),
            level_progression=progression_data.get("level_progression", []),
            abilities={
                "strength": character.strength,
                "dexterity": character.dexterity,
                "constitution": character.constitution,
                "intelligence": character.intelligence,
                "wisdom": character.wisdom,
                "charisma": character.charisma
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get character progression: {str(e)}")

@router.post("/{character_id}/experience", response_model=CharacterProgressionResponse)
async def add_experience(
    character_id: int,
    experience_data: ExperienceGainRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add experience points to a character"""
    try:
        # Verify character ownership
        character = db.query(Character).filter(
            Character.id == character_id,
            Character.user_id == current_user['user_id']
        ).first()
        
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")

        progression_service = CharacterProgressionService()
        updated_progression = await progression_service.add_experience(
            character, 
            experience_data.amount, 
            experience_data.reason
        )

        # Update character in database if level changed
        if updated_progression.get("level_up_occurred"):
            character.level = updated_progression["new_level"]
            character.max_hit_points = updated_progression["new_max_hp"]
            db.commit()

        return CharacterProgressionResponse(
            character_id=character.id,
            current_level=character.level,
            current_xp=updated_progression.get("current_xp", 0),
            xp_to_next_level=updated_progression.get("xp_to_next_level", 1000),
            available_attribute_points=updated_progression.get("available_attribute_points", 0),
            available_skill_points=updated_progression.get("available_skill_points", 0),
            skills=updated_progression.get("skills", []),
            achievements=updated_progression.get("achievements", []),
            level_progression=updated_progression.get("level_progression", []),
            abilities={
                "strength": character.strength,
                "dexterity": character.dexterity,
                "constitution": character.constitution,
                "intelligence": character.intelligence,
                "wisdom": character.wisdom,
                "charisma": character.charisma
            }
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to add experience: {str(e)}")

@router.post("/{character_id}/level-up", response_model=CharacterProgressionResponse)
async def level_up_character(
    character_id: int,
    level_up_data: LevelUpRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Level up a character"""
    try:
        # Verify character ownership
        character = db.query(Character).filter(
            Character.id == character_id,
            Character.user_id == current_user['user_id']
        ).first()
        
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")

        progression_service = CharacterProgressionService()
        level_up_result = await progression_service.level_up_character(
            character,
            level_up_data.chosen_features
        )

        if not level_up_result.get("success"):
            raise HTTPException(status_code=400, detail=level_up_result.get("message", "Cannot level up"))

        # Update character stats
        character.level = level_up_result["new_level"]
        character.max_hit_points = level_up_result["new_max_hp"]
        character.current_hit_points = min(character.current_hit_points + level_up_result.get("hp_gained", 0), character.max_hit_points)
        
        db.commit()
        db.refresh(character)

        return CharacterProgressionResponse(
            character_id=character.id,
            current_level=character.level,
            current_xp=level_up_result.get("current_xp", 0),
            xp_to_next_level=level_up_result.get("xp_to_next_level", 1000),
            available_attribute_points=level_up_result.get("available_attribute_points", 0),
            available_skill_points=level_up_result.get("available_skill_points", 0),
            skills=level_up_result.get("skills", []),
            achievements=level_up_result.get("achievements", []),
            level_progression=level_up_result.get("level_progression", []),
            abilities={
                "strength": character.strength,
                "dexterity": character.dexterity,
                "constitution": character.constitution,
                "intelligence": character.intelligence,
                "wisdom": character.wisdom,
                "charisma": character.charisma
            }
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to level up character: {str(e)}")

@router.post("/{character_id}/upgrade-skill")
async def upgrade_skill(
    character_id: int,
    skill_data: SkillUpgradeRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upgrade a character skill"""
    try:
        # Verify character ownership
        character = db.query(Character).filter(
            Character.id == character_id,
            Character.user_id == current_user['user_id']
        ).first()
        
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")

        progression_service = CharacterProgressionService()
        upgrade_result = await progression_service.upgrade_skill(
            character,
            skill_data.skill_id
        )

        if not upgrade_result.get("success"):
            raise HTTPException(status_code=400, detail=upgrade_result.get("message", "Cannot upgrade skill"))

        return {
            "success": True,
            "message": f"Skill {skill_data.skill_id} upgraded successfully",
            "new_level": upgrade_result.get("new_level"),
            "bonuses_gained": upgrade_result.get("bonuses_gained", [])
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upgrade skill: {str(e)}")

@router.post("/{character_id}/upgrade-attribute")
async def upgrade_attribute(
    character_id: int,
    attribute_data: AttributeUpgradeRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upgrade a character attribute"""
    try:
        # Verify character ownership
        character = db.query(Character).filter(
            Character.id == character_id,
            Character.user_id == current_user['user_id']
        ).first()
        
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")

        progression_service = CharacterProgressionService()
        upgrade_result = await progression_service.upgrade_attribute(
            character,
            attribute_data.attribute_name
        )

        if not upgrade_result.get("success"):
            raise HTTPException(status_code=400, detail=upgrade_result.get("message", "Cannot upgrade attribute"))

        # Update character attribute
        current_value = getattr(character, attribute_data.attribute_name, 10)
        setattr(character, attribute_data.attribute_name, current_value + 1)
        
        # Update derived stats if constitution was upgraded
        if attribute_data.attribute_name == "constitution":
            hp_increase = 1  # +1 HP per constitution modifier increase
            character.max_hit_points += hp_increase
            character.current_hit_points = min(character.current_hit_points + hp_increase, character.max_hit_points)

        db.commit()
        db.refresh(character)

        return {
            "success": True,
            "message": f"{attribute_data.attribute_name.title()} increased to {getattr(character, attribute_data.attribute_name)}",
            "new_value": getattr(character, attribute_data.attribute_name),
            "modifier": (getattr(character, attribute_data.attribute_name) - 10) // 2
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to upgrade attribute: {str(e)}")

@router.get("/{character_id}/achievements", response_model=List[AchievementResponse])
async def get_character_achievements(
    character_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all achievements for a character"""
    try:
        # Verify character ownership
        character = db.query(Character).filter(
            Character.id == character_id,
            Character.user_id == current_user['user_id']
        ).first()
        
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")

        progression_service = CharacterProgressionService()
        achievements = await progression_service.get_achievements(character)

        return achievements

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get achievements: {str(e)}")

@router.post("/{character_id}/achievements/{achievement_id}/unlock")
async def unlock_achievement(
    character_id: int,
    achievement_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Unlock an achievement for a character"""
    try:
        # Verify character ownership
        character = db.query(Character).filter(
            Character.id == character_id,
            Character.user_id == current_user['user_id']
        ).first()
        
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")

        progression_service = CharacterProgressionService()
        unlock_result = await progression_service.unlock_achievement(
            character,
            achievement_id
        )

        if not unlock_result.get("success"):
            raise HTTPException(status_code=400, detail=unlock_result.get("message", "Cannot unlock achievement"))

        return {
            "success": True,
            "message": f"Achievement {achievement_id} unlocked!",
            "xp_gained": unlock_result.get("xp_reward", 0),
            "achievement": unlock_result.get("achievement")
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to unlock achievement: {str(e)}") 