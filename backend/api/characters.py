"""
API endpoints for character management and creation
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional

from database import get_db
from auth import get_current_user_id, get_current_user
from models.character import Character
from models.user import User
from schemas.character import (
    Character as CharacterSchema,
    CharacterCreate,
    CharacterUpdate,
    CharacterWithRolledStats,
    CharacterList,
    StatRollResponse,
    CharacterWithStats,
    CharacterStatsSummary,
    QuickCharacterCreate
)
from services.character_service import CharacterService

router = APIRouter()

# D&D 5e race and class data for character creation
D5E_RACES = [
    "Human", "Elf", "Dwarf", "Halfling", "Dragonborn", "Gnome", "Half-Elf", 
    "Half-Orc", "Tiefling", "Aasimar", "Genasi", "Goliath", "Tabaxi", "Firbolg"
]

D5E_CLASSES = [
    "Barbarian", "Bard", "Cleric", "Druid", "Fighter", "Monk", "Paladin", 
    "Ranger", "Rogue", "Sorcerer", "Warlock", "Wizard", "Artificer"
]

D5E_BACKGROUNDS = [
    "Acolyte", "Criminal", "Folk Hero", "Noble", "Sage", "Soldier", "Charlatan",
    "Entertainer", "Guild Artisan", "Hermit", "Outlander", "Sailor"
]

@router.get("/characters/options")
async def get_character_options():
    """Get available races, classes, and backgrounds for character creation"""
    return {
        "races": D5E_RACES,
        "classes": D5E_CLASSES,
        "backgrounds": D5E_BACKGROUNDS
    }

@router.post("/characters/roll-stats", response_model=StatRollResponse)
async def roll_character_stats():
    """Roll ability scores for character creation (4d6 drop lowest)"""
    return CharacterService.roll_all_stats()

@router.post("/characters", response_model=CharacterSchema, status_code=status.HTTP_201_CREATED)
async def create_character(
    character_data: CharacterCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new character with specified stats"""
    # Ensure the character belongs to the current user
    character_data.user_id = current_user.id
    
    # Validate race and class
    if character_data.race not in D5E_RACES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid race. Must be one of: {', '.join(D5E_RACES)}"
        )
    
    if character_data.character_class not in D5E_CLASSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid class. Must be one of: {', '.join(D5E_CLASSES)}"
        )
    
    try:
        character = CharacterService.create_character(db, character_data)
        return character
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/characters/quick-create", response_model=CharacterSchema, status_code=status.HTTP_201_CREATED)
async def quick_create_character(
    character_data: QuickCharacterCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Quick character creation with auto-generated stats
    """
    try:
        character = CharacterService.quick_create_character(
            db=db,
            user_id=current_user.id,
            character_data=character_data
        )
        return character
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to create character")

@router.get("/characters", response_model=CharacterList)
async def get_user_characters(
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
    skip: int = Query(0, ge=0, description="Number of characters to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of characters to return"),
    active_only: bool = Query(True, description="Return only active characters")
):
    """Get all characters for the current user"""
    query = db.query(Character).filter(Character.user_id == current_user_id)
    
    if active_only:
        query = query.filter(Character.is_active == True)
    
    total = query.count()
    characters = query.offset(skip).limit(limit).all()
    
    return CharacterList(characters=characters, total=total)

@router.get("/characters/{character_id}", response_model=CharacterWithStats)
async def get_character(
    character_id: int,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """Get a specific character with calculated stats"""
    character = CharacterService.get_character_by_user(db, current_user_id, character_id)
    
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found"
        )
    
    # Add calculated stats
    character_dict = {
        **character.__dict__,
        "strength_modifier": character.strength_modifier,
        "dexterity_modifier": character.dexterity_modifier,
        "constitution_modifier": character.constitution_modifier,
        "intelligence_modifier": character.intelligence_modifier,
        "wisdom_modifier": character.wisdom_modifier,
        "charisma_modifier": character.charisma_modifier,
        "proficiency_bonus": character.proficiency_bonus
    }
    
    return CharacterWithStats(**character_dict)

@router.get("/characters/{character_id}/summary", response_model=CharacterStatsSummary)
async def get_character_summary(
    character_id: int,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """Get a character summary with key stats"""
    character = CharacterService.get_character_by_user(db, current_user_id, character_id)
    
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found"
        )
    
    # Build abilities dict
    abilities = {
        "strength": f"{character.strength} ({character.strength_modifier:+d})",
        "dexterity": f"{character.dexterity} ({character.dexterity_modifier:+d})",
        "constitution": f"{character.constitution} ({character.constitution_modifier:+d})",
        "intelligence": f"{character.intelligence} ({character.intelligence_modifier:+d})",
        "wisdom": f"{character.wisdom} ({character.wisdom_modifier:+d})",
        "charisma": f"{character.charisma} ({character.charisma_modifier:+d})"
    }
    
    # Build saving throws dict
    saving_throws = {}
    for ability in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
        saving_throws[ability] = character.get_saving_throw_bonus(ability)
    
    # Build skills dict
    skills = {}
    skill_list = [
        "acrobatics", "animal_handling", "arcana", "athletics", "deception",
        "history", "insight", "intimidation", "investigation", "medicine",
        "nature", "perception", "performance", "persuasion", "religion",
        "sleight_of_hand", "stealth", "survival"
    ]
    for skill in skill_list:
        skills[skill] = character.get_skill_bonus(skill)
    
    return CharacterStatsSummary(
        name=character.name,
        level=character.level,
        character_class=character.character_class,
        race=character.race,
        hit_points=f"{character.current_hit_points}/{character.max_hit_points}",
        armor_class=character.armor_class,
        proficiency_bonus=character.proficiency_bonus,
        abilities=abilities,
        saving_throws=saving_throws,
        skills=skills
    )

@router.put("/characters/{character_id}", response_model=CharacterSchema)
async def update_character(
    character_id: int,
    character_update: CharacterUpdate,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """Update a character"""
    # Verify character belongs to user
    character = CharacterService.get_character_by_user(db, current_user_id, character_id)
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found"
        )
    
    # Validate race and class if being updated
    if character_update.race and character_update.race not in D5E_RACES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid race. Must be one of: {', '.join(D5E_RACES)}"
        )
    
    if character_update.character_class and character_update.character_class not in D5E_CLASSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid class. Must be one of: {', '.join(D5E_CLASSES)}"
        )
    
    updated_character = CharacterService.update_character(db, character_id, character_update)
    if not updated_character:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Character update failed"
        )
    
    return updated_character

@router.delete("/characters/{character_id}")
async def delete_character(
    character_id: int,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
    hard_delete: bool = Query(False, description="Permanently delete character")
):
    """Delete a character (soft delete by default)"""
    # Verify character belongs to user
    character = CharacterService.get_character_by_user(db, current_user_id, character_id)
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found"
        )
    
    if hard_delete:
        success = CharacterService.hard_delete_character(db, character_id, current_user_id)
    else:
        success = CharacterService.delete_character(db, character_id, current_user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Character deletion failed"
        )
    
    return {"message": "Character deleted successfully"}

@router.post("/characters/{character_id}/damage")
async def apply_damage(
    character_id: int,
    damage: int = Query(..., ge=0, description="Damage amount"),
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """Apply damage to a character"""
    character = CharacterService.apply_damage(db, character_id, damage)
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found"
        )
    
    return {
        "message": f"Applied {damage} damage to {character.name}",
        "current_hp": character.current_hit_points,
        "max_hp": character.max_hit_points,
        "is_alive": character.is_alive
    }

@router.post("/characters/{character_id}/heal")
async def heal_character(
    character_id: int,
    healing: int = Query(..., ge=0, description="Healing amount"),
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """Heal a character"""
    character = CharacterService.heal_character(db, character_id, healing)
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found"
        )
    
    return {
        "message": f"Healed {character.name} for {healing} HP",
        "current_hp": character.current_hit_points,
        "max_hp": character.max_hit_points
    }

@router.post("/characters/{character_id}/level-up")
async def level_up_character(
    character_id: int,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """Level up a character"""
    character = CharacterService.level_up_character(db, character_id)
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found"
        )
    
    return {
        "message": f"{character.name} leveled up to level {character.level}!",
        "level": character.level,
        "current_hp": character.current_hit_points,
        "max_hp": character.max_hit_points
    }

@router.post("/characters/{character_id}/experience")
async def add_experience(
    character_id: int,
    xp: int = Query(..., ge=0, description="Experience points to add"),
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """Add experience points to a character"""
    character = CharacterService.add_experience(db, character_id, xp)
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found"
        )
    
    return {
        "message": f"Added {xp} XP to {character.name}",
        "experience_points": character.experience_points,
        "level": character.level
    } 