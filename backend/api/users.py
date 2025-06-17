"""
User API endpoints for SoloRealms
Handles user authentication, profile management, and user statistics
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models.user import User
from models.character import Character
from auth import get_current_user, get_optional_user
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.get("/me", response_model=dict)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """Get the current user's profile and statistics"""
    return current_user.to_dict()

@router.patch("/me", response_model=dict)
async def update_user_profile(
    preferences: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user preferences and profile settings"""
    if preferences is not None:
        current_user.preferences = preferences
    
    current_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(current_user)
    
    return current_user.to_dict()

@router.get("/me/characters", response_model=List[dict])
async def get_user_characters(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all characters belonging to the current user"""
    characters = db.query(Character).filter(Character.user_id == current_user.id).all()
    
    character_list = []
    for char in characters:
        character_list.append({
            "id": char.id,
            "name": char.name,
            "race": char.race,
            "character_class": char.character_class,
            "level": char.level,
            "experience_points": char.experience_points,
            "is_active": char.is_active,
            "is_alive": char.is_alive,
            "created_at": char.created_at.isoformat() if char.created_at else None,
            "current_hit_points": char.current_hit_points,
            "max_hit_points": char.max_hit_points,
            "armor_class": char.armor_class
        })
    
    return character_list

@router.get("/me/stats", response_model=dict)
async def get_user_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed user statistics and achievements"""
    # Get character count
    character_count = db.query(Character).filter(Character.user_id == current_user.id).count()
    active_characters = db.query(Character).filter(
        Character.user_id == current_user.id,
        Character.is_active == True,
        Character.is_alive == True
    ).count()
    
    # Get character levels and XP
    characters = db.query(Character).filter(Character.user_id == current_user.id).all()
    total_character_levels = sum(char.level for char in characters)
    total_xp = sum(char.experience_points for char in characters)
    highest_level = max((char.level for char in characters), default=0)
    
    return {
        "user_id": current_user.id,
        "display_name": current_user.display_name,
        "member_since": current_user.created_at.isoformat() if current_user.created_at else None,
        "last_login": current_user.last_login.isoformat() if current_user.last_login else None,
        "characters": {
            "total": character_count,
            "active": active_characters,
            "highest_level": highest_level,
            "total_levels": total_character_levels,
            "total_xp": total_xp
        },
        "game_stats": {
            "total_adventures": current_user.total_adventures,
            "total_playtime_minutes": current_user.total_playtime_minutes,
            "total_xp_earned": current_user.total_xp_earned
        }
    }

@router.post("/me/login", response_model=dict)
async def record_user_login(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Record user login timestamp for analytics"""
    current_user.last_login = datetime.utcnow()
    db.commit()
    
    return {"message": "Login recorded", "last_login": current_user.last_login.isoformat()}

@router.delete("/me", response_model=dict)
async def delete_user_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete user account and all associated data (GDPR compliance)"""
    # This will cascade delete all characters, story arcs, etc. due to our relationships
    db.delete(current_user)
    db.commit()
    
    return {"message": "Account successfully deleted"}

@router.get("/profile/{user_id}", response_model=dict)
async def get_public_user_profile(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """Get public profile information for a user"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Return limited public information
    return {
        "id": user.id,
        "display_name": user.display_name,
        "username": user.username,
        "image_url": user.image_url,
        "member_since": user.created_at.isoformat() if user.created_at else None,
        "public_stats": {
            "total_characters": user.total_characters,
            "total_adventures": user.total_adventures,
            # Don't expose playtime to other users for privacy
        }
    } 