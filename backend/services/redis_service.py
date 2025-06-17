"""
Redis Service for SoloRealms State Management
Provides persistent state management, caching, and session handling for the D&D game.
"""

import os
import json
import redis
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from sqlalchemy.orm import Session

from models.character import Character
from models.story import StoryArc, WorldState, StoryStage
from models.combat import CombatEncounter, CombatState, CombatParticipant


logger = logging.getLogger(__name__)


class CacheExpiry(Enum):
    """Cache expiration times in seconds"""
    SHORT = 300  # 5 minutes
    MEDIUM = 1800  # 30 minutes  
    LONG = 3600  # 1 hour
    SESSION = 86400  # 24 hours
    PERSISTENT = 604800  # 1 week


@dataclass
class GameSession:
    """Game session data structure"""
    session_id: str
    user_id: str
    character_id: int
    story_arc_id: int
    created_at: datetime
    last_activity: datetime
    active: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Redis storage"""
        return {
            'session_id': self.session_id,
            'user_id': self.user_id,
            'character_id': self.character_id,
            'story_arc_id': self.story_arc_id,
            'created_at': self.created_at.isoformat(),
            'last_activity': self.last_activity.isoformat(),
            'active': self.active
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameSession':
        """Create from dictionary"""
        return cls(
            session_id=data['session_id'],
            user_id=data['user_id'],
            character_id=data['character_id'],
            story_arc_id=data['story_arc_id'],
            created_at=datetime.fromisoformat(data['created_at']),
            last_activity=datetime.fromisoformat(data['last_activity']),
            active=data.get('active', True)
        )


@dataclass
class CharacterCache:
    """Cached character data for fast AI prompt building"""
    character_id: int
    name: str
    race: str
    character_class: str
    level: int
    stats: Dict[str, int]
    current_hp: int
    max_hp: int
    armor_class: int
    equipped_items: Dict[str, Any]
    background: str
    cached_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Redis storage"""
        return {
            'character_id': self.character_id,
            'name': self.name,
            'race': self.race,
            'character_class': self.character_class,
            'level': self.level,
            'stats': self.stats,
            'current_hp': self.current_hp,
            'max_hp': self.max_hp,
            'armor_class': self.armor_class,
            'equipped_items': self.equipped_items,
            'background': self.background,
            'cached_at': self.cached_at.isoformat()
        }
    
    @classmethod
    def from_character(cls, character: Character) -> 'CharacterCache':
        """Create from Character model"""
        return cls(
            character_id=character.id,
            name=character.name,
            race=character.race,
            character_class=character.character_class,
            level=character.level,
            stats={
                'strength': character.strength,
                'dexterity': character.dexterity,
                'constitution': character.constitution,
                'intelligence': character.intelligence,
                'wisdom': character.wisdom,
                'charisma': character.charisma
            },
            current_hp=character.current_hit_points,
            max_hp=character.max_hit_points,
            armor_class=character.armor_class,
            equipped_items=character.equipped_items or {},
            background=character.background or '',
            cached_at=datetime.utcnow()
        )


@dataclass
class StoryCache:
    """Cached story data for AI context"""
    story_arc_id: int
    title: str
    current_stage: str
    story_type: str
    story_seed: str
    major_decisions: List[Dict[str, Any]]
    combat_outcomes: List[Dict[str, Any]]
    npc_status: Dict[str, Any]
    world_location: str
    objectives: List[Dict[str, Any]]
    cached_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Redis storage"""
        return {
            'story_arc_id': self.story_arc_id,
            'title': self.title,
            'current_stage': self.current_stage,
            'story_type': self.story_type,
            'story_seed': self.story_seed,
            'major_decisions': self.major_decisions,
            'combat_outcomes': self.combat_outcomes,
            'npc_status': self.npc_status,
            'world_location': self.world_location,
            'objectives': self.objectives,
            'cached_at': self.cached_at.isoformat()
        }
    
    @classmethod
    def from_story_arc(cls, story_arc: StoryArc, world_state: WorldState = None) -> 'StoryCache':
        """Create from StoryArc and WorldState models"""
        return cls(
            story_arc_id=story_arc.id,
            title=story_arc.title or '',
            current_stage=story_arc.current_stage.value,
            story_type=story_arc.story_type,
            story_seed=story_arc.story_seed or '',
            major_decisions=story_arc.major_decisions or [],
            combat_outcomes=story_arc.combat_outcomes or [],
            npc_status=story_arc.npc_status or {},
            world_location=world_state.current_location if world_state else '',
            objectives=world_state.active_objectives if world_state else [],
            cached_at=datetime.utcnow()
        )


@dataclass
class CombatCache:
    """Cached combat encounter data"""
    encounter_id: int
    character_id: int
    encounter_name: str
    encounter_type: str
    current_round: int
    combat_state: str
    participants: List[Dict[str, Any]]
    turn_order: List[int]
    current_turn: int
    combat_log: List[Dict[str, Any]]
    cached_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Redis storage"""
        return {
            'encounter_id': self.encounter_id,
            'character_id': self.character_id,
            'encounter_name': self.encounter_name,
            'encounter_type': self.encounter_type,
            'current_round': self.current_round,
            'combat_state': self.combat_state,
            'participants': self.participants,
            'turn_order': self.turn_order,
            'current_turn': self.current_turn,
            'combat_log': self.combat_log,
            'cached_at': self.cached_at.isoformat()
        }


class RedisService:
    """Redis service for state management and caching"""
    
    def __init__(self, redis_url: str = None, decode_responses: bool = True):
        self.redis_url = redis_url or os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        self.client = redis.from_url(self.redis_url, decode_responses=decode_responses)
        
        # Key prefixes for organization
        self.PREFIXES = {
            'session': 'game:session:',
            'character': 'cache:character:',
            'story': 'cache:story:',
            'combat': 'cache:combat:',
            'user_sessions': 'user:sessions:',
            'ai_prompt': 'ai:prompt:',
            'game_state': 'game:state:'
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Check Redis connection health"""
        try:
            ping_result = self.client.ping()
            info = self.client.info()
            
            return {
                'healthy': ping_result,
                'connected_clients': info.get('connected_clients', 0),
                'used_memory_human': info.get('used_memory_human', 'unknown'),
                'redis_version': info.get('redis_version', 'unknown'),
                'uptime_in_seconds': info.get('uptime_in_seconds', 0)
            }
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return {'healthy': False, 'error': str(e)}
    
    # Session Management
    def create_game_session(self, user_id: str, character_id: int, story_arc_id: int) -> GameSession:
        """Create a new game session"""
        session_id = f"{user_id}:{character_id}:{story_arc_id}:{datetime.utcnow().timestamp()}"
        
        session = GameSession(
            session_id=session_id,
            user_id=user_id,
            character_id=character_id,
            story_arc_id=story_arc_id,
            created_at=datetime.utcnow(),
            last_activity=datetime.utcnow()
        )
        
        # Store session
        self.client.setex(
            self.PREFIXES['session'] + session_id,
            CacheExpiry.SESSION.value,
            json.dumps(session.to_dict())
        )
        
        # Add to user's session list
        user_sessions_key = self.PREFIXES['user_sessions'] + user_id
        self.client.sadd(user_sessions_key, session_id)
        self.client.expire(user_sessions_key, CacheExpiry.SESSION.value)
        
        logger.info(f"Created game session {session_id} for user {user_id}")
        return session
    
    def get_game_session(self, session_id: str) -> Optional[GameSession]:
        """Get game session by ID"""
        session_data = self.client.get(self.PREFIXES['session'] + session_id)
        if session_data:
            return GameSession.from_dict(json.loads(session_data))
        return None
    
    def update_session_activity(self, session_id: str) -> bool:
        """Update session last activity timestamp"""
        session = self.get_game_session(session_id)
        if session:
            session.last_activity = datetime.utcnow()
            self.client.setex(
                self.PREFIXES['session'] + session_id,
                CacheExpiry.SESSION.value,
                json.dumps(session.to_dict())
            )
            return True
        return False
    
    def get_user_sessions(self, user_id: str) -> List[GameSession]:
        """Get all active sessions for a user"""
        user_sessions_key = self.PREFIXES['user_sessions'] + user_id
        session_ids = self.client.smembers(user_sessions_key)
        
        sessions = []
        for session_id in session_ids:
            session = self.get_game_session(session_id)
            if session and session.active:
                sessions.append(session)
        
        return sessions
    
    def end_game_session(self, session_id: str) -> bool:
        """End a game session"""
        session = self.get_game_session(session_id)
        if session:
            session.active = False
            self.client.setex(
                self.PREFIXES['session'] + session_id,
                CacheExpiry.MEDIUM.value,  # Keep for a bit longer for reference
                json.dumps(session.to_dict())
            )
            
            # Remove from user's active sessions
            user_sessions_key = self.PREFIXES['user_sessions'] + session.user_id
            self.client.srem(user_sessions_key, session_id)
            
            logger.info(f"Ended game session {session_id}")
            return True
        return False
    
    # Character Caching
    def cache_character(self, character: Character, expiry: CacheExpiry = CacheExpiry.LONG) -> bool:
        """Cache character data for fast access"""
        try:
            character_cache = CharacterCache.from_character(character)
            self.client.setex(
                self.PREFIXES['character'] + str(character.id),
                expiry.value,
                json.dumps(character_cache.to_dict())
            )
            logger.debug(f"Cached character {character.id}")
            return True
        except Exception as e:
            logger.error(f"Failed to cache character {character.id}: {e}")
            return False
    
    def get_cached_character(self, character_id: int) -> Optional[CharacterCache]:
        """Get cached character data"""
        try:
            data = self.client.get(self.PREFIXES['character'] + str(character_id))
            if data:
                char_data = json.loads(data)
                char_data['cached_at'] = datetime.fromisoformat(char_data['cached_at'])
                return CharacterCache(**char_data)
        except Exception as e:
            logger.error(f"Failed to get cached character {character_id}: {e}")
        return None
    
    def refresh_character_cache(self, db: Session, character_id: int) -> Optional[CharacterCache]:
        """Refresh character cache from database"""
        character = db.query(Character).filter(Character.id == character_id).first()
        if character:
            self.cache_character(character)
            return self.get_cached_character(character_id)
        return None
    
    # Story Caching
    def cache_story(self, story_arc: StoryArc, world_state: WorldState = None, 
                   expiry: CacheExpiry = CacheExpiry.MEDIUM) -> bool:
        """Cache story arc and world state data"""
        try:
            story_cache = StoryCache.from_story_arc(story_arc, world_state)
            self.client.setex(
                self.PREFIXES['story'] + str(story_arc.id),
                expiry.value,
                json.dumps(story_cache.to_dict())
            )
            logger.debug(f"Cached story arc {story_arc.id}")
            return True
        except Exception as e:
            logger.error(f"Failed to cache story arc {story_arc.id}: {e}")
            return False
    
    def get_cached_story(self, story_arc_id: int) -> Optional[StoryCache]:
        """Get cached story data"""
        try:
            data = self.client.get(self.PREFIXES['story'] + str(story_arc_id))
            if data:
                story_data = json.loads(data)
                story_data['cached_at'] = datetime.fromisoformat(story_data['cached_at'])
                return StoryCache(**story_data)
        except Exception as e:
            logger.error(f"Failed to get cached story {story_arc_id}: {e}")
        return None
    
    # Combat State Management
    def store_combat_state(self, combat_encounter: CombatEncounter, 
                          participants: List[CombatParticipant] = None) -> bool:
        """Store combat encounter state"""
        try:
            participant_data = []
            if participants:
                for p in participants:
                    participant_data.append({
                        'id': p.id,
                        'name': p.name,
                        'character_id': p.character_id,
                        'participant_type': p.participant_type,
                        'current_hit_points': p.current_hit_points,
                        'max_hit_points': p.max_hit_points,
                        'armor_class': p.armor_class,
                        'initiative': p.initiative,
                        'is_active': p.is_active,
                        'active_conditions': p.active_conditions or [],
                        'temporary_hp': p.temporary_hp,
                        'position_x': p.position_x,
                        'position_y': p.position_y,
                        'movement_remaining': p.movement_remaining,
                        'actions_taken': p.actions_taken or {}
                    })
            
            combat_cache = CombatCache(
                encounter_id=combat_encounter.id,
                character_id=combat_encounter.character_id,
                encounter_name=combat_encounter.encounter_name,
                encounter_type=combat_encounter.encounter_type,
                current_round=combat_encounter.current_round,
                combat_state=combat_encounter.combat_state.value,
                participants=participant_data,
                turn_order=combat_encounter.initiative_order or [],
                current_turn=combat_encounter.current_turn,
                combat_log=combat_encounter.combat_log or [],
                cached_at=datetime.utcnow()
            )
            
            self.client.setex(
                self.PREFIXES['combat'] + str(combat_encounter.id),
                CacheExpiry.LONG.value,
                json.dumps(combat_cache.to_dict())
            )
            logger.debug(f"Stored combat state {combat_encounter.id}")
            return True
        except Exception as e:
            logger.error(f"Failed to store combat state {combat_encounter.id}: {e}")
            return False
    
    def get_combat_state(self, encounter_id: int) -> Optional[CombatCache]:
        """Get combat encounter state"""
        try:
            data = self.client.get(self.PREFIXES['combat'] + str(encounter_id))
            if data:
                combat_data = json.loads(data)
                combat_data['cached_at'] = datetime.fromisoformat(combat_data['cached_at'])
                return CombatCache(**combat_data)
        except Exception as e:
            logger.error(f"Failed to get combat state {encounter_id}: {e}")
        return None
    
    def clear_combat_state(self, encounter_id: int) -> bool:
        """Clear combat encounter state"""
        try:
            self.client.delete(self.PREFIXES['combat'] + str(encounter_id))
            logger.debug(f"Cleared combat state {encounter_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to clear combat state {encounter_id}: {e}")
            return False
    
    # AI Prompt Caching
    def cache_ai_prompt_data(self, session_id: str, character_cache: CharacterCache, 
                           story_cache: StoryCache, expiry: CacheExpiry = CacheExpiry.SHORT) -> bool:
        """Cache formatted data for AI prompts"""
        try:
            prompt_data = {
                'character': character_cache.to_dict(),
                'story': story_cache.to_dict(),
                'cached_at': datetime.utcnow().isoformat()
            }
            
            self.client.setex(
                self.PREFIXES['ai_prompt'] + session_id,
                expiry.value,
                json.dumps(prompt_data)
            )
            return True
        except Exception as e:
            logger.error(f"Failed to cache AI prompt data for session {session_id}: {e}")
            return False
    
    def get_ai_prompt_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get cached AI prompt data"""
        try:
            data = self.client.get(self.PREFIXES['ai_prompt'] + session_id)
            if data:
                return json.loads(data)
        except Exception as e:
            logger.error(f"Failed to get AI prompt data for session {session_id}: {e}")
        return None
    
    # Cleanup Operations
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions and related data"""
        cleaned = 0
        try:
            # Get all session keys
            session_keys = self.client.keys(self.PREFIXES['session'] + '*')
            
            for key in session_keys:
                ttl = self.client.ttl(key)
                if ttl == -1:  # No expiration set, this shouldn't happen
                    self.client.expire(key, CacheExpiry.MEDIUM.value)
                elif ttl <= 0:  # Expired
                    self.client.delete(key)
                    cleaned += 1
            
            logger.info(f"Cleaned up {cleaned} expired sessions")
        except Exception as e:
            logger.error(f"Failed to cleanup expired sessions: {e}")
        
        return cleaned
    
    def invalidate_character_cache(self, character_id: int) -> bool:
        """Invalidate all cache entries related to a character"""
        try:
            keys_to_delete = []
            
            # Character cache
            char_key = self.PREFIXES['character'] + str(character_id)
            keys_to_delete.append(char_key)
            
            # Find sessions for this character
            session_keys = self.client.keys(self.PREFIXES['session'] + '*')
            for key in session_keys:
                session_data = self.client.get(key)
                if session_data:
                    session = json.loads(session_data)
                    if session.get('character_id') == character_id:
                        keys_to_delete.append(key)
                        
                        # Also invalidate AI prompt cache for this session
                        session_id = session.get('session_id')
                        if session_id:
                            ai_key = self.PREFIXES['ai_prompt'] + session_id
                            keys_to_delete.append(ai_key)
            
            # Find combat states for this character
            combat_keys = self.client.keys(self.PREFIXES['combat'] + '*')
            for key in combat_keys:
                combat_data = self.client.get(key)
                if combat_data:
                    combat = json.loads(combat_data)
                    if combat.get('character_id') == character_id:
                        keys_to_delete.append(key)
            
            # Delete all related keys
            if keys_to_delete:
                self.client.delete(*keys_to_delete)
                logger.info(f"Invalidated {len(keys_to_delete)} cache entries for character {character_id}")
            
            return True
        except Exception as e:
            logger.error(f"Failed to invalidate character cache {character_id}: {e}")
            return False
    
    def invalidate_story_cache(self, story_arc_id: int) -> bool:
        """Invalidate all cache entries related to a story arc"""
        try:
            keys_to_delete = []
            
            # Story cache
            story_key = self.PREFIXES['story'] + str(story_arc_id)
            keys_to_delete.append(story_key)
            
            # Find sessions for this story arc
            session_keys = self.client.keys(self.PREFIXES['session'] + '*')
            for key in session_keys:
                session_data = self.client.get(key)
                if session_data:
                    session = json.loads(session_data)
                    if session.get('story_arc_id') == story_arc_id:
                        # Invalidate AI prompt cache for this session
                        session_id = session.get('session_id')
                        if session_id:
                            ai_key = self.PREFIXES['ai_prompt'] + session_id
                            keys_to_delete.append(ai_key)
            
            # Delete all related keys
            if keys_to_delete:
                self.client.delete(*keys_to_delete)
                logger.info(f"Invalidated {len(keys_to_delete)} cache entries for story arc {story_arc_id}")
            
            return True
        except Exception as e:
            logger.error(f"Failed to invalidate story cache {story_arc_id}: {e}")
            return False
    
    def invalidate_user_cache(self, user_id: str) -> bool:
        """Invalidate all cache entries related to a user"""
        try:
            keys_to_delete = []
            
            # Find all user sessions
            user_sessions_key = self.PREFIXES['user_sessions'] + user_id
            session_ids = self.client.smembers(user_sessions_key)
            
            for session_id in session_ids:
                # Session cache
                session_key = self.PREFIXES['session'] + session_id
                keys_to_delete.append(session_key)
                
                # AI prompt cache
                ai_key = self.PREFIXES['ai_prompt'] + session_id
                keys_to_delete.append(ai_key)
            
            # User sessions set
            keys_to_delete.append(user_sessions_key)
            
            # Delete all related keys
            if keys_to_delete:
                self.client.delete(*keys_to_delete)
                logger.info(f"Invalidated {len(keys_to_delete)} cache entries for user {user_id}")
            
            return True
        except Exception as e:
            logger.error(f"Failed to invalidate user cache {user_id}: {e}")
            return False
    
    def cleanup_stale_cache(self, max_age_hours: int = 24) -> Dict[str, int]:
        """Clean up stale cache entries older than specified hours"""
        cleanup_stats = {
            'character': 0,
            'story': 0,
            'combat': 0,
            'ai_prompt': 0,
            'total': 0
        }
        
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
            
            # Check each cache type
            for cache_type, prefix in self.PREFIXES.items():
                if cache_type in ['session', 'user_sessions', 'game_state']:
                    continue  # Skip session-related caches
                
                keys = self.client.keys(prefix + '*')
                for key in keys:
                    try:
                        data = self.client.get(key)
                        if data:
                            cache_data = json.loads(data)
                            cached_at_str = cache_data.get('cached_at')
                            if cached_at_str:
                                cached_at = datetime.fromisoformat(cached_at_str)
                                if cached_at < cutoff_time:
                                    self.client.delete(key)
                                    cleanup_stats[cache_type] += 1
                                    cleanup_stats['total'] += 1
                    except (json.JSONDecodeError, ValueError, KeyError):
                        # Invalid cache entry, delete it
                        self.client.delete(key)
                        cleanup_stats[cache_type] += 1
                        cleanup_stats['total'] += 1
            
            logger.info(f"Cleaned up {cleanup_stats['total']} stale cache entries: {cleanup_stats}")
        except Exception as e:
            logger.error(f"Failed to cleanup stale cache: {e}")
        
        return cleanup_stats
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        stats = {
            'redis_info': {},
            'cache_counts': {},
            'memory_usage': {},
            'expiration_info': {}
        }
        
        try:
            # Redis server info
            info = self.client.info()
            stats['redis_info'] = {
                'version': info.get('redis_version'),
                'connected_clients': info.get('connected_clients'),
                'used_memory_human': info.get('used_memory_human'),
                'total_commands_processed': info.get('total_commands_processed'),
                'keyspace_hits': info.get('keyspace_hits'),
                'keyspace_misses': info.get('keyspace_misses')
            }
            
            # Cache counts by type
            for cache_type, prefix in self.PREFIXES.items():
                keys = self.client.keys(prefix + '*')
                stats['cache_counts'][cache_type] = len(keys)
                
                # Sample memory usage for this cache type
                if keys:
                    sample_key = keys[0]
                    memory_usage = self.client.memory_usage(sample_key)
                    stats['memory_usage'][cache_type] = memory_usage
                
                # Expiration info
                expired_count = 0
                no_expiry_count = 0
                for key in keys[:10]:  # Sample first 10 keys
                    ttl = self.client.ttl(key)
                    if ttl == -1:
                        no_expiry_count += 1
                    elif ttl <= 0:
                        expired_count += 1
                
                stats['expiration_info'][cache_type] = {
                    'sample_size': min(len(keys), 10),
                    'expired_keys': expired_count,
                    'no_expiry_keys': no_expiry_count
                }
            
        except Exception as e:
            logger.error(f"Failed to get cache statistics: {e}")
            stats['error'] = str(e)
        
        return stats
    
    def clear_all_cache(self) -> bool:
        """Clear all cached data (use with caution)"""
        try:
            for prefix in self.PREFIXES.values():
                keys = self.client.keys(prefix + '*')
                if keys:
                    self.client.delete(*keys)
            logger.warning("Cleared all cached data")
            return True
        except Exception as e:
            logger.error(f"Failed to clear all cache: {e}")
            return False


# Global Redis service instance
redis_service = RedisService() 