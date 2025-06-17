"""
Game Orchestrator Service for SoloRealms
Central coordinator that integrates all AI and game systems into seamless gameplay.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from .ai_service import ai_service, AIService
from .redis_service import redis_service, CacheExpiry, GameSession
from .response_parser import response_parser, ParsedResponse
from .story_service import StoryService
from .combat import CombatService
from models.character import Character
from models.story import StoryArc, WorldState, StoryStage
from models.combat import CombatEncounter, CombatState, CombatParticipant
from services.dice_service import DiceRollResult

logger = logging.getLogger(__name__)


class GamePhase(Enum):
    """Different phases of gameplay"""
    INITIALIZATION = "initialization"
    STORY_NARRATION = "story_narration"
    PLAYER_INPUT = "player_input"
    DICE_RESOLUTION = "dice_resolution"
    AI_PROCESSING = "ai_processing"
    STATE_UPDATE = "state_update"
    COMBAT_ROUND = "combat_round"
    STORY_PROGRESSION = "story_progression"
    ERROR_RECOVERY = "error_recovery"


class ActionResult(Enum):
    """Results of orchestrated actions"""
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILURE = "failure"
    REQUIRES_DICE = "requires_dice"
    REQUIRES_INPUT = "requires_input"
    COMBAT_INITIATED = "combat_initiated"
    STORY_ADVANCED = "story_advanced"


@dataclass
class GameTurn:
    """Represents a complete game turn with all phases"""
    turn_id: str
    session_id: str
    character_id: int
    phase: GamePhase
    player_action: Optional[str] = None
    dice_rolls: List[DiceRollResult] = None
    ai_response: Optional[str] = None
    parsed_response: Optional[ParsedResponse] = None
    state_changes: List[Dict[str, Any]] = None
    result: Optional[ActionResult] = None
    timestamp: datetime = None
    error_messages: List[str] = None
    
    def __post_init__(self):
        if self.dice_rolls is None:
            self.dice_rolls = []
        if self.state_changes is None:
            self.state_changes = []
        if self.error_messages is None:
            self.error_messages = []
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class OrchestrationResult:
    """Result of a complete orchestrated action"""
    success: bool
    result_type: ActionResult
    narrative_text: str
    state_changes: List[Dict[str, Any]]
    dice_required: List[Dict[str, Any]]
    next_actions: List[str]
    performance_metrics: Dict[str, Any]
    errors: List[str]


class GameOrchestrator:
    """
    Central orchestrator for all game systems.
    Manages the complete flow from player action to AI response to state updates.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.story_service = StoryService
        self.combat_service = CombatService(db)
        self.active_turns: Dict[str, GameTurn] = {}
        
        # Performance tracking
        self.performance_metrics = {
            'total_turns': 0,
            'successful_turns': 0,
            'average_response_time': 0.0,
            'cache_hit_rate': 0.0
        }
    
    async def start_game_session(
        self, 
        user_id: str, 
        character_id: int, 
        story_arc_id: Optional[int] = None
    ) -> Tuple[str, OrchestrationResult]:
        """Initialize a new game session with full state setup"""
        start_time = datetime.now()
        session_id = f"session_{user_id}_{int(start_time.timestamp())}"
        
        try:
            # Create Redis session  
            session = redis_service.create_game_session(
                user_id=user_id,
                character_id=character_id,
                story_arc_id=story_arc_id or 0
            )
            session_id = session.session_id
            
            # Load and cache character data
            character = self.db.query(Character).filter_by(id=character_id).first()
            if not character:
                raise ValueError(f"Character {character_id} not found")
            
            character_cache = {
                'id': character.id,
                'name': character.name,
                'class_name': character.character_class,
                'level': character.level,
                'race': character.race,
                'current_hp': character.current_hit_points,
                'max_hp': character.max_hit_points,
                'armor_class': character.armor_class,
                'location': getattr(character, 'location', 'Starting Area'),
                'inventory': getattr(character, 'inventory', [])
            }
            
            redis_service.cache_character(character, CacheExpiry.LONG)
            
            # Load story context if provided
            story_cache = None
            if story_arc_id:
                story_arc = self.db.query(StoryArc).filter_by(id=story_arc_id).first()
                if story_arc:
                    story_cache = {
                        'arc_id': story_arc.id,
                        'title': story_arc.title,
                        'current_scene': getattr(story_arc, 'current_scene', 'Introduction'),
                        'objectives': getattr(story_arc, 'objectives', []),
                        'recent_events': []
                    }
                    redis_service.cache_story(story_arc, None, CacheExpiry.MEDIUM)
            
            # Generate opening narration
            opening_prompt_context = {
                'character': character_cache,
                'story': story_cache,
                'scene_type': 'introduction',
                'action': 'start_adventure'
            }
            
            # Simplified placeholder for now
            ai_response = "Welcome to your adventure! You find yourself at the beginning of an epic journey."
            parsed_response = ParsedResponse(
                narrative_text=ai_response,
                actions=[],
                state_changes=[],
                dice_rolls=[],
                combat_events=[],
                story_events=[],
                confidence_score=1.0,
                parsing_errors=[]
            )
            
            # Create initial turn record
            initial_turn = GameTurn(
                turn_id=f"{session_id}_turn_0",
                session_id=session_id,
                character_id=character_id,
                phase=GamePhase.INITIALIZATION,
                ai_response=ai_response,
                parsed_response=parsed_response,
                result=ActionResult.SUCCESS
            )
            
            self.active_turns[session_id] = initial_turn
            
            result = OrchestrationResult(
                success=True,
                result_type=ActionResult.SUCCESS,
                narrative_text=parsed_response.narrative_text,
                state_changes=[],
                dice_required=[],
                next_actions=["Describe what you want to do next"],
                performance_metrics={
                    'session_setup_time': (datetime.now() - start_time).total_seconds(),
                    'cache_operations': 2
                },
                errors=[]
            )
            
            logger.info(f"Game session {session_id} started successfully for character {character_id}")
            return session_id, result
            
        except Exception as e:
            logger.error(f"Failed to start game session: {str(e)}")
            raise
    
    async def process_player_action(
        self, 
        session_id: str, 
        player_action: str, 
        dice_results: Optional[List[DiceRollResult]] = None
    ) -> OrchestrationResult:
        """
        Process a complete player action through the full AI pipeline.
        This is the main orchestration method that handles the entire turn flow.
        """
        start_time = datetime.now()
        turn_id = f"{session_id}_turn_{int(start_time.timestamp())}"
        
        try:
            # Initialize turn tracking
            current_turn = GameTurn(
                turn_id=turn_id,
                session_id=session_id,
                character_id=await self._get_character_id_from_session(session_id),
                phase=GamePhase.PLAYER_INPUT,
                player_action=player_action,
                dice_rolls=dice_results or []
            )
            
            self.active_turns[session_id] = current_turn
            
            # Phase 1: Gather context from cache
            current_turn.phase = GamePhase.AI_PROCESSING
            context = await self._gather_game_context(session_id, current_turn.character_id)
            
            # Phase 2: Build AI prompt with action and context
            prompt_context = {
                'character': context['character'],
                'story': context['story'],
                'combat': context.get('combat'),
                'player_action': player_action,
                'dice_results': dice_results,
                'scene_type': self._determine_scene_type(context)
            }
            
            # Phase 3: Generate AI response
            ai_response = await self._generate_contextual_ai_response(prompt_context)
            current_turn.ai_response = ai_response
            
            # Phase 4: Parse AI response for structured data
            current_turn.phase = GamePhase.STATE_UPDATE
            parsed_response = response_parser.parse_response(ai_response)
            current_turn.parsed_response = parsed_response
            
            # Phase 5: Check if dice rolls are required
            if parsed_response.dice_rolls and not dice_results:
                current_turn.result = ActionResult.REQUIRES_DICE
                return OrchestrationResult(
                    success=True,
                    result_type=ActionResult.REQUIRES_DICE,
                    narrative_text=parsed_response.narrative_text,
                    state_changes=[],
                    dice_required=[asdict(roll) for roll in parsed_response.dice_rolls],
                    next_actions=["Roll the required dice and continue"],
                    performance_metrics=self._calculate_performance_metrics(start_time),
                    errors=[]
                )
            
            # Phase 6: Apply state changes
            applied_changes = await self._apply_state_changes(
                session_id, 
                current_turn.character_id, 
                parsed_response
            )
            current_turn.state_changes = applied_changes
            
            # Phase 7: Check for combat initiation
            combat_status = await self._handle_combat_events(session_id, parsed_response)
            
            # Phase 8: Update story progression
            await self._update_story_progression(session_id, parsed_response)
            
            # Phase 9: Determine result and next actions
            result_type, next_actions = self._determine_turn_result(parsed_response, combat_status)
            current_turn.result = result_type
            
            # Update performance metrics
            self.performance_metrics['total_turns'] += 1
            if result_type in [ActionResult.SUCCESS, ActionResult.STORY_ADVANCED]:
                self.performance_metrics['successful_turns'] += 1
            
            # Cache turn for potential replay/analysis
            await self._cache_turn_data(current_turn)
            
            final_result = OrchestrationResult(
                success=True,
                result_type=result_type,
                narrative_text=parsed_response.narrative_text,
                state_changes=applied_changes,
                dice_required=[],
                next_actions=next_actions,
                performance_metrics=self._calculate_performance_metrics(start_time),
                errors=[]
            )
            
            logger.info(f"Successfully processed player action for session {session_id}")
            return final_result
            
        except Exception as e:
            error_msg = f"Failed to process player action: {str(e)}"
            logger.error(error_msg)
            
            # Error recovery - try to maintain session state
            await self._handle_orchestration_error(session_id, current_turn, str(e))
            
            return OrchestrationResult(
                success=False,
                result_type=ActionResult.FAILURE,
                narrative_text="The magical forces seem unstable. Please try again.",
                state_changes=[],
                dice_required=[],
                next_actions=["Try a different action"],
                performance_metrics=self._calculate_performance_metrics(start_time),
                errors=[error_msg]
            )
    
    async def _gather_game_context(self, session_id: str, character_id: int) -> Dict[str, Any]:
        """Efficiently gather all game context from cache and database"""
        context = {}
        
        # Get character data (prioritize cache)
        character_cache = await redis_service.get_character_cache(character_id)
        if character_cache:
            context['character'] = character_cache
        else:
            # Fallback to database
            character = self.db.query(Character).filter_by(id=character_id).first()
            if character:
                context['character'] = {
                    'id': character.id,
                    'name': character.name,
                    'class_name': character.character_class,
                    'level': character.level,
                    'current_hp': character.current_hit_points,
                    'max_hp': character.max_hit_points,
                    'armor_class': character.armor_class
                }
        
        # Get session data
        session = await redis_service.get_game_session(session_id)
        if session and session.story_arc_id:
            story_cache = await redis_service.get_story_cache(session.story_arc_id)
            if story_cache:
                context['story'] = story_cache
        
        # Check for active combat
        combat_cache = await redis_service.get_combat_cache(f"character_{character_id}")
        if combat_cache:
            context['combat'] = combat_cache
        
        return context
    
    def _determine_scene_type(self, context: Dict[str, Any]) -> str:
        """Determine the current scene type based on context"""
        if context.get('combat'):
            return 'combat'
        elif context.get('story', {}).get('current_scene', '').lower().find('dialogue') != -1:
            return 'npc_interaction'
        elif context.get('story', {}).get('current_scene', '').lower().find('exploration') != -1:
            return 'exploration'
        else:
            return 'story_narration'
    
    async def _generate_contextual_ai_response(self, context: Dict[str, Any]) -> str:
        """Generate AI response based on scene type and context"""
        scene_type = context.get('scene_type', 'story_narration')
        
        # This method is not currently used but would need to be implemented
        # For now, return a simple placeholder response
        return "The adventure continues as you explore the world around you."
    
    async def _apply_state_changes(
        self, 
        session_id: str, 
        character_id: int, 
        parsed_response: ParsedResponse
    ) -> List[Dict[str, Any]]:
        """Apply all state changes from parsed AI response"""
        applied_changes = []
        
        try:
            # Apply character state changes
            character_changes = [
                change for change in parsed_response.state_changes 
                if change.entity_type == 'character'
            ]
            
            if character_changes:
                current_char = await redis_service.get_character_cache(character_id)
                for change in character_changes:
                    if change.property_name == 'current_hp':
                        old_hp = current_char.get('current_hp', 0)
                        new_hp = max(0, min(
                            current_char.get('max_hp', 100), 
                            change.new_value if change.new_value is not None else old_hp + (change.change_amount or 0)
                        ))
                        current_char['current_hp'] = new_hp
                        
                        applied_changes.append({
                            'type': 'hp_change',
                            'old_value': old_hp,
                            'new_value': new_hp,
                            'change_amount': new_hp - old_hp
                        })
                    
                    elif change.property_name == 'location':
                        old_location = current_char.get('location', 'Unknown')
                        current_char['location'] = change.new_value
                        
                        applied_changes.append({
                            'type': 'location_change',
                            'old_value': old_location,
                            'new_value': change.new_value
                        })
                
                # Update character cache - would need to implement this properly
                # await redis_service.cache_character_data(character_id, current_char, CacheExpiry.LONG)
            
            # Apply story state changes
            session = await redis_service.get_game_session(session_id)
            if session and session.story_arc_id:
                story_changes = [
                    change for change in parsed_response.state_changes 
                    if change.entity_type == 'story'
                ]
                
                if story_changes:
                    story_cache = await redis_service.get_story_cache(session.story_arc_id)
                    for change in story_changes:
                        if change.property_name == 'current_scene':
                            old_scene = story_cache.get('current_scene', 'Unknown')
                            story_cache['current_scene'] = change.new_value
                            
                            applied_changes.append({
                                'type': 'scene_change',
                                'old_value': old_scene,
                                'new_value': change.new_value
                            })
                    
                    # await redis_service.cache_story_data(session.story_arc_id, story_cache, CacheExpiry.MEDIUM)
            
            return applied_changes
            
        except Exception as e:
            logger.error(f"Failed to apply state changes: {str(e)}")
            return []
    
    async def _handle_combat_events(self, session_id: str, parsed_response: ParsedResponse) -> Dict[str, Any]:
        """Handle combat-related events from AI response"""
        combat_events = parsed_response.combat_events
        
        if not combat_events:
            return {'active': False}
        
        # Check if combat is being initiated
        initiative_events = [event for event in combat_events if event.event_type == 'initiative']
        if initiative_events:
            # Start new combat encounter
            # This would integrate with the existing combat service
            return {'active': True, 'phase': 'initiative', 'new_combat': True}
        
        return {'active': True, 'phase': 'ongoing'}
    
    async def _update_story_progression(self, session_id: str, parsed_response: ParsedResponse) -> None:
        """Update story progression based on parsed events"""
        story_events = parsed_response.story_events
        
        if story_events:
            session = await redis_service.get_game_session(session_id)
            if session and session.story_arc_id:
                story_cache = await redis_service.get_story_cache(session.story_arc_id)
                
                # Add new events to story history
                if 'recent_events' not in story_cache:
                    story_cache['recent_events'] = []
                
                for event in story_events[-3:]:  # Keep last 3 events
                    story_cache['recent_events'].append({
                        'event_type': event.event_type,
                        'description': event.description,
                        'timestamp': datetime.now().isoformat()
                    })
                
                # await redis_service.cache_story_data(session.story_arc_id, story_cache, CacheExpiry.MEDIUM)
    
    def _determine_turn_result(
        self, 
        parsed_response: ParsedResponse, 
        combat_status: Dict[str, Any]
    ) -> Tuple[ActionResult, List[str]]:
        """Determine the result of the turn and suggest next actions"""
        
        if combat_status.get('new_combat'):
            return ActionResult.COMBAT_INITIATED, [
                "Roll for initiative",
                "Choose your first combat action"
            ]
        
        if parsed_response.dice_rolls:
            return ActionResult.REQUIRES_DICE, [
                f"Roll {roll.dice_expression} for {roll.purpose}"
                for roll in parsed_response.dice_rolls
            ]
        
        if parsed_response.story_events:
            return ActionResult.STORY_ADVANCED, [
                "Continue the adventure",
                "Explore your surroundings",
                "Interact with characters or objects"
            ]
        
        return ActionResult.SUCCESS, [
            "Describe your next action",
            "Look around for more details",
            "Continue exploring"
        ]
    
    async def _cache_turn_data(self, turn: GameTurn) -> None:
        """Cache turn data for analysis and potential replay"""
        cache_key = f"turn_data:{turn.session_id}:{turn.turn_id}"
        turn_data = {
            'turn_id': turn.turn_id,
            'phase': turn.phase.value,
            'player_action': turn.player_action,
            'result': turn.result.value if turn.result else None,
            'timestamp': turn.timestamp.isoformat(),
            'performance': len(turn.ai_response) if turn.ai_response else 0
        }
        
        await redis_service.cache_data(cache_key, turn_data, CacheExpiry.SHORT)
    
    async def _handle_orchestration_error(
        self, 
        session_id: str, 
        current_turn: GameTurn, 
        error_msg: str
    ) -> None:
        """Handle errors during orchestration and attempt recovery"""
        current_turn.phase = GamePhase.ERROR_RECOVERY
        current_turn.error_messages.append(error_msg)
        
        # Log error for monitoring
        logger.error(f"Orchestration error in session {session_id}: {error_msg}")
        
        # Try to maintain session state
        try:
            session = await redis_service.get_game_session(session_id)
            if session:
                # Update session with error info but keep it active
                await redis_service.update_session_activity(session_id)
        except Exception as e:
            logger.error(f"Failed to update session during error recovery: {str(e)}")
    
    def _calculate_performance_metrics(self, start_time: datetime) -> Dict[str, Any]:
        """Calculate performance metrics for the current operation"""
        end_time = datetime.now()
        response_time = (end_time - start_time).total_seconds()
        
        return {
            'response_time_seconds': response_time,
            'timestamp': end_time.isoformat(),
            'total_turns_processed': self.performance_metrics['total_turns'],
            'success_rate': (
                self.performance_metrics['successful_turns'] / max(1, self.performance_metrics['total_turns'])
            ) * 100
        }
    
    async def _get_character_id_from_session(self, session_id: str) -> int:
        """Get character ID from session data"""
        session = await redis_service.get_game_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        return session.character_id
    
    async def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Get comprehensive status of a game session"""
        try:
            session = await redis_service.get_game_session(session_id)
            if not session:
                return {'active': False, 'error': 'Session not found'}
            
            character_cache = await redis_service.get_character_cache(session.character_id)
            story_cache = await redis_service.get_story_cache(session.story_arc_id) if session.story_arc_id else None
            
            current_turn = self.active_turns.get(session_id)
            
            return {
                'active': True,
                'session_id': session_id,
                'character': character_cache,
                'story': story_cache,
                'current_turn': {
                    'phase': current_turn.phase.value if current_turn else 'waiting',
                    'turn_id': current_turn.turn_id if current_turn else None
                },
                'last_activity': session.last_activity.isoformat() if session.last_activity else None
            }
            
        except Exception as e:
            logger.error(f"Failed to get session status: {str(e)}")
            return {'active': False, 'error': str(e)}
    
    def health_check(self) -> Dict[str, Any]:
        """Health check for the orchestrator service"""
        return {
            'status': 'healthy',
            'active_sessions': len(self.active_turns),
            'total_turns_processed': self.performance_metrics['total_turns'],
            'success_rate': (
                self.performance_metrics['successful_turns'] / max(1, self.performance_metrics['total_turns'])
            ) * 100,
            'timestamp': datetime.now().isoformat()
        }


# Global orchestrator instance
game_orchestrator: Optional[GameOrchestrator] = None


def get_game_orchestrator(db: Session) -> GameOrchestrator:
    """Get or create the global game orchestrator instance"""
    global game_orchestrator
    if game_orchestrator is None:
        game_orchestrator = GameOrchestrator(db)
    return game_orchestrator 