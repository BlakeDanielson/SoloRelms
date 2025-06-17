"""
Redis State Management API endpoints
Handles game sessions, state caching, and Redis health monitoring.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from database import get_db
from services.redis_service import redis_service, GameSession, CacheExpiry
from models.character import Character
from models.story import StoryArc, WorldState
from models.combat import CombatEncounter


router = APIRouter(prefix="/redis", tags=["Redis State"])


# Request/Response Models
class CreateSessionRequest(BaseModel):
    user_id: str = Field(..., description="User ID")
    character_id: int = Field(..., description="Character ID")
    story_arc_id: int = Field(..., description="Story arc ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_12345",
                "character_id": 1,
                "story_arc_id": 1
            }
        }


class SessionResponse(BaseModel):
    session_id: str
    user_id: str
    character_id: int
    story_arc_id: int
    created_at: datetime
    last_activity: datetime
    active: bool


class CacheCharacterRequest(BaseModel):
    character_id: int = Field(..., description="Character ID to cache")
    expiry_minutes: Optional[int] = Field(60, description="Cache expiry in minutes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "character_id": 1,
                "expiry_minutes": 60
            }
        }


class CacheStoryRequest(BaseModel):
    story_arc_id: int = Field(..., description="Story arc ID to cache")
    expiry_minutes: Optional[int] = Field(30, description="Cache expiry in minutes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "story_arc_id": 1,
                "expiry_minutes": 30
            }
        }


class CombatStateRequest(BaseModel):
    encounter_id: int = Field(..., description="Combat encounter ID")
    include_participants: bool = Field(True, description="Include participant data")
    
    class Config:
        json_schema_extra = {
            "example": {
                "encounter_id": 1,
                "include_participants": True
            }
        }


# Session Management Endpoints
@router.post("/session/create", response_model=SessionResponse, summary="Create game session")
async def create_game_session(
    request: CreateSessionRequest,
    db: Session = Depends(get_db)
):
    """
    Create a new game session for state management.
    
    This establishes a persistent session that can be used to:
    - Track player progress across interactions
    - Cache character and story data for fast AI prompts
    - Maintain combat state during encounters
    - Store session-specific game data
    """
    try:
        # Verify character and story exist
        character = db.query(Character).filter(Character.id == request.character_id).first()
        if not character:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Character {request.character_id} not found"
            )
        
        story_arc = db.query(StoryArc).filter(StoryArc.id == request.story_arc_id).first()
        if not story_arc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Story arc {request.story_arc_id} not found"
            )
        
        # Create session
        session = redis_service.create_game_session(
            user_id=request.user_id,
            character_id=request.character_id,
            story_arc_id=request.story_arc_id
        )
        
        # Pre-cache character and story data for performance
        redis_service.cache_character(character)
        world_state = db.query(WorldState).filter(WorldState.story_arc_id == request.story_arc_id).first()
        redis_service.cache_story(story_arc, world_state)
        
        return SessionResponse(
            session_id=session.session_id,
            user_id=session.user_id,
            character_id=session.character_id,
            story_arc_id=session.story_arc_id,
            created_at=session.created_at,
            last_activity=session.last_activity,
            active=session.active
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create game session: {str(e)}"
        )


@router.get("/session/{session_id}", response_model=SessionResponse, summary="Get session details")
async def get_game_session(session_id: str):
    """
    Get details for a specific game session.
    """
    try:
        session = redis_service.get_game_session(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )
        
        return SessionResponse(
            session_id=session.session_id,
            user_id=session.user_id,
            character_id=session.character_id,
            story_arc_id=session.story_arc_id,
            created_at=session.created_at,
            last_activity=session.last_activity,
            active=session.active
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get session: {str(e)}"
        )


@router.post("/session/{session_id}/update-activity", summary="Update session activity")
async def update_session_activity(session_id: str):
    """
    Update the last activity timestamp for a session.
    Should be called periodically during gameplay to keep session active.
    """
    try:
        success = redis_service.update_session_activity(session_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )
        
        return {"message": "Session activity updated", "session_id": session_id}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update session activity: {str(e)}"
        )


@router.get("/session/user/{user_id}", response_model=List[SessionResponse], summary="Get user sessions")
async def get_user_sessions(user_id: str):
    """
    Get all active sessions for a user.
    """
    try:
        sessions = redis_service.get_user_sessions(user_id)
        return [
            SessionResponse(
                session_id=session.session_id,
                user_id=session.user_id,
                character_id=session.character_id,
                story_arc_id=session.story_arc_id,
                created_at=session.created_at,
                last_activity=session.last_activity,
                active=session.active
            )
            for session in sessions
        ]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user sessions: {str(e)}"
        )


@router.delete("/session/{session_id}", summary="End game session")
async def end_game_session(session_id: str):
    """
    End a game session and clean up associated state.
    """
    try:
        success = redis_service.end_game_session(session_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )
        
        return {"message": "Session ended", "session_id": session_id}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to end session: {str(e)}"
        )


# Cache Management Endpoints
@router.post("/cache/character", summary="Cache character data")
async def cache_character(
    request: CacheCharacterRequest,
    db: Session = Depends(get_db)
):
    """
    Cache character data for fast AI prompt building.
    """
    try:
        character = db.query(Character).filter(Character.id == request.character_id).first()
        if not character:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Character {request.character_id} not found"
            )
        
        # Determine cache expiry
        expiry = CacheExpiry.LONG
        if request.expiry_minutes:
            if request.expiry_minutes <= 5:
                expiry = CacheExpiry.SHORT
            elif request.expiry_minutes <= 30:
                expiry = CacheExpiry.MEDIUM
            elif request.expiry_minutes <= 60:
                expiry = CacheExpiry.LONG
        
        success = redis_service.cache_character(character, expiry)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to cache character data"
            )
        
        return {
            "message": "Character cached successfully",
            "character_id": request.character_id,
            "expiry_minutes": request.expiry_minutes
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cache character: {str(e)}"
        )


@router.post("/cache/story", summary="Cache story data")
async def cache_story(
    request: CacheStoryRequest,
    db: Session = Depends(get_db)
):
    """
    Cache story arc and world state data for AI context.
    """
    try:
        story_arc = db.query(StoryArc).filter(StoryArc.id == request.story_arc_id).first()
        if not story_arc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Story arc {request.story_arc_id} not found"
            )
        
        world_state = db.query(WorldState).filter(WorldState.story_arc_id == request.story_arc_id).first()
        
        # Determine cache expiry
        expiry = CacheExpiry.MEDIUM
        if request.expiry_minutes:
            if request.expiry_minutes <= 5:
                expiry = CacheExpiry.SHORT
            elif request.expiry_minutes <= 30:
                expiry = CacheExpiry.MEDIUM
            elif request.expiry_minutes <= 60:
                expiry = CacheExpiry.LONG
        
        success = redis_service.cache_story(story_arc, world_state, expiry)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to cache story data"
            )
        
        return {
            "message": "Story cached successfully",
            "story_arc_id": request.story_arc_id,
            "expiry_minutes": request.expiry_minutes
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cache story: {str(e)}"
        )


@router.post("/cache/combat", summary="Store combat state")
async def store_combat_state(
    request: CombatStateRequest,
    db: Session = Depends(get_db)
):
    """
    Store combat encounter state in Redis for fast access.
    """
    try:
        combat_encounter = db.query(CombatEncounter).filter(CombatEncounter.id == request.encounter_id).first()
        if not combat_encounter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Combat encounter {request.encounter_id} not found"
            )
        
        participants = None
        if request.include_participants:
            # In a real implementation, you'd query CombatParticipant model
            # For now, we'll pass None and let the service handle it
            pass
        
        success = redis_service.store_combat_state(combat_encounter, participants)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to store combat state"
            )
        
        return {
            "message": "Combat state stored successfully",
            "encounter_id": request.encounter_id
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to store combat state: {str(e)}"
        )


@router.get("/cache/combat/{encounter_id}", summary="Get combat state")
async def get_combat_state(encounter_id: int):
    """
    Get cached combat encounter state.
    """
    try:
        combat_cache = redis_service.get_combat_state(encounter_id)
        if not combat_cache:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Combat state for encounter {encounter_id} not found"
            )
        
        return combat_cache.to_dict()
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get combat state: {str(e)}"
        )


@router.delete("/cache/combat/{encounter_id}", summary="Clear combat state")
async def clear_combat_state(encounter_id: int):
    """
    Clear combat encounter state from Redis.
    """
    try:
        success = redis_service.clear_combat_state(encounter_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to clear combat state"
            )
        
        return {
            "message": "Combat state cleared successfully",
            "encounter_id": encounter_id
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear combat state: {str(e)}"
        )


# Health and Monitoring Endpoints
@router.get("/health", summary="Redis health check")
async def redis_health_check():
    """
    Check Redis connection and get system information.
    """
    try:
        health_info = redis_service.health_check()
        
        if not health_info.get('healthy'):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Redis is not healthy: {health_info.get('error', 'Unknown error')}"
            )
        
        return {
            "status": "healthy",
            "redis_info": health_info
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Redis health check failed: {str(e)}"
        )


@router.post("/maintenance/cleanup", summary="Cleanup expired sessions")
async def cleanup_expired_sessions():
    """
    Clean up expired sessions and related cached data.
    This should be called periodically for maintenance.
    """
    try:
        cleaned_count = redis_service.cleanup_expired_sessions()
        
        return {
            "message": "Cleanup completed",
            "expired_sessions_cleaned": cleaned_count
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Cleanup failed: {str(e)}"
        )


@router.delete("/maintenance/clear-all", summary="Clear all cache (DANGER)")
async def clear_all_cache():
    """
    ⚠️ DANGER: Clear all cached data from Redis.
    Use only for development/testing or emergency maintenance.
    """
    try:
        success = redis_service.clear_all_cache()
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to clear all cache"
            )
        
        return {
            "message": "⚠️ All cached data has been cleared",
            "warning": "This action cannot be undone"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear cache: {str(e)}"
        )


# Cache Management and Cleanup Endpoints
@router.post("/cleanup/expired-sessions")
async def cleanup_expired_sessions():
    """Clean up expired sessions and return count of cleaned items"""
    try:
        cleaned_count = redis_service.cleanup_expired_sessions()
        return {
            "success": True,
            "cleaned_sessions": cleaned_count,
            "message": f"Successfully cleaned up {cleaned_count} expired sessions"
        }
    except Exception as e:
        logger.error(f"Failed to cleanup expired sessions: {e}")
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")

@router.post("/cleanup/stale-cache")
async def cleanup_stale_cache(max_age_hours: int = 24):
    """Clean up stale cache entries older than specified hours"""
    try:
        if max_age_hours < 1 or max_age_hours > 168:  # 1 hour to 1 week
            raise HTTPException(status_code=400, detail="max_age_hours must be between 1 and 168")
        
        cleanup_results = redis_service.cleanup_stale_cache(max_age_hours)
        return {
            "success": True,
            "cleanup_results": cleanup_results,
            "message": f"Successfully cleaned up {cleanup_results['total']} stale cache entries"
        }
    except Exception as e:
        logger.error(f"Failed to cleanup stale cache: {e}")
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")

@router.delete("/cache/character/{character_id}")
async def invalidate_character_cache(character_id: int):
    """Invalidate all cache entries related to a character"""
    try:
        success = redis_service.invalidate_character_cache(character_id)
        if success:
            return {
                "success": True,
                "message": f"Successfully invalidated cache for character {character_id}"
            }
        else:
            raise HTTPException(status_code=500, detail="Cache invalidation failed")
    except Exception as e:
        logger.error(f"Failed to invalidate character cache {character_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Cache invalidation failed: {str(e)}")

@router.delete("/cache/story/{story_arc_id}")
async def invalidate_story_cache(story_arc_id: int):
    """Invalidate all cache entries related to a story arc"""
    try:
        success = redis_service.invalidate_story_cache(story_arc_id)
        if success:
            return {
                "success": True,
                "message": f"Successfully invalidated cache for story arc {story_arc_id}"
            }
        else:
            raise HTTPException(status_code=500, detail="Cache invalidation failed")
    except Exception as e:
        logger.error(f"Failed to invalidate story cache {story_arc_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Cache invalidation failed: {str(e)}")

@router.delete("/cache/user/{user_id}")
async def invalidate_user_cache(user_id: str):
    """Invalidate all cache entries related to a user"""
    try:
        success = redis_service.invalidate_user_cache(user_id)
        if success:
            return {
                "success": True,
                "message": f"Successfully invalidated cache for user {user_id}"
            }
        else:
            raise HTTPException(status_code=500, detail="Cache invalidation failed")
    except Exception as e:
        logger.error(f"Failed to invalidate user cache {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Cache invalidation failed: {str(e)}")

@router.delete("/cache/combat/{encounter_id}")
async def clear_combat_cache(encounter_id: int):
    """Clear combat encounter cache"""
    try:
        success = redis_service.clear_combat_state(encounter_id)
        if success:
            return {
                "success": True,
                "message": f"Successfully cleared combat cache for encounter {encounter_id}"
            }
        else:
            raise HTTPException(status_code=404, detail="Combat encounter not found in cache")
    except Exception as e:
        logger.error(f"Failed to clear combat cache {encounter_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Cache clearing failed: {str(e)}")

@router.get("/statistics")
async def get_cache_statistics():
    """Get comprehensive cache statistics and health metrics"""
    try:
        stats = redis_service.get_cache_statistics()
        return {
            "success": True,
            "statistics": stats,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get cache statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Statistics retrieval failed: {str(e)}")

@router.post("/cleanup/all")
async def cleanup_all_cache():
    """
    DANGER: Clear all cached data. Use with extreme caution.
    This will remove all sessions, cached data, and combat states.
    """
    try:
        success = redis_service.clear_all_cache()
        if success:
            return {
                "success": True,
                "message": "⚠️ WARNING: ALL cached data has been cleared",
                "warning": "This action cannot be undone. All active sessions have been terminated."
            }
        else:
            raise HTTPException(status_code=500, detail="Cache clearing failed")
    except Exception as e:
        logger.error(f"Failed to clear all cache: {e}")
        raise HTTPException(status_code=500, detail=f"Cache clearing failed: {str(e)}") 