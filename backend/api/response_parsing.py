"""
Response Parsing API endpoints
Handles parsing of AI DM responses and extraction of structured game data.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
import re

from database import get_db
from services.response_parser import response_parser, ParsedResponse
from services.redis_service import redis_service
from models.character import Character
from models.story import StoryArc
from models.combat import CombatEncounter

router = APIRouter(prefix="/parsing", tags=["Response Parsing"])


# Request/Response Models
class ParseAIResponseRequest(BaseModel):
    ai_response: str = Field(..., description="The AI DM response text to parse")
    session_id: Optional[str] = Field(None, description="Game session ID for context")
    character_id: Optional[int] = Field(None, description="Character ID for context")
    story_arc_id: Optional[int] = Field(None, description="Story arc ID for context")
    include_context: bool = Field(True, description="Whether to include game context in parsing")


class ParsedResponseModel(BaseModel):
    narrative_text: str
    actions: List[Dict[str, Any]]
    state_changes: List[Dict[str, Any]]
    dice_rolls: List[Dict[str, Any]]
    combat_events: List[Dict[str, Any]]
    story_events: List[Dict[str, Any]]
    confidence_score: float
    parsing_errors: List[str]
    summary: Dict[str, Any]


class ApplyStateChangesRequest(BaseModel):
    session_id: str = Field(..., description="Game session ID")
    parsed_response: Dict[str, Any] = Field(..., description="Parsed response data")
    auto_apply: bool = Field(False, description="Automatically apply valid state changes")
    dry_run: bool = Field(False, description="Preview changes without applying them")


class StateChangeResult(BaseModel):
    applied_changes: List[Dict[str, Any]]
    failed_changes: List[Dict[str, Any]]
    warnings: List[str]
    summary: Dict[str, Any]


class ValidationRequest(BaseModel):
    parsed_data: Dict[str, Any] = Field(..., description="Parsed response data to validate")
    game_context: Optional[Dict[str, Any]] = Field(None, description="Current game context")


class ValidationResult(BaseModel):
    is_valid: bool
    confidence_score: float
    validation_errors: List[str]
    suggestions: List[str]


@router.post("/parse", response_model=ParsedResponseModel)
async def parse_ai_response(
    request: ParseAIResponseRequest,
    db: Session = Depends(get_db)
):
    """
    Parse an AI DM response and extract structured game data
    """
    try:
        # Build context if needed
        context = {}
        if request.include_context:
            if request.session_id:
                # Get session context from Redis
                session = redis_service.get_game_session(request.session_id)
                if session:
                    context['session'] = {
                        'user_id': session.user_id,
                        'character_id': session.character_id,
                        'story_arc_id': session.story_arc_id
                    }
            
            if request.character_id:
                # Get character context
                character = db.query(Character).filter(Character.id == request.character_id).first()
                if character:
                    context['character'] = {
                        'id': character.id,
                        'name': character.name,
                        'level': character.level,
                        'current_hp': character.current_hit_points,
                        'max_hp': character.max_hit_points
                    }
        
        # Parse the AI response
        parsed_response = response_parser.parse_response(request.ai_response, context)
        
        # Convert dataclasses to dictionaries for JSON serialization
        def convert_dataclass(obj):
            if hasattr(obj, '__dataclass_fields__'):
                result = {}
                for field_name, field_value in obj.__dict__.items():
                    if hasattr(field_value, '__dataclass_fields__'):
                        result[field_name] = convert_dataclass(field_value)
                    elif isinstance(field_value, list):
                        result[field_name] = [convert_dataclass(item) if hasattr(item, '__dataclass_fields__') else item for item in field_value]
                    elif hasattr(field_value, 'value'):  # Enum
                        result[field_name] = field_value.value
                    else:
                        result[field_name] = field_value
                return result
            return obj
        
        # Convert parsed response to dictionary format
        response_dict = {
            'narrative_text': parsed_response.narrative_text,
            'actions': parsed_response.actions,
            'state_changes': [convert_dataclass(change) for change in parsed_response.state_changes],
            'dice_rolls': [convert_dataclass(roll) for roll in parsed_response.dice_rolls],
            'combat_events': [convert_dataclass(event) for event in parsed_response.combat_events],
            'story_events': [convert_dataclass(event) for event in parsed_response.story_events],
            'confidence_score': parsed_response.confidence_score,
            'parsing_errors': parsed_response.parsing_errors,
            'summary': response_parser.extract_quick_summary(parsed_response)
        }
        
        # Cache parsed response if session provided
        if request.session_id:
            cache_key = f"parsed_response:{request.session_id}:{hash(request.ai_response)}"
            redis_service.redis_client.setex(
                cache_key, 
                300,  # 5 minutes
                str(response_dict)
            )
        
        return response_dict
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse AI response: {str(e)}"
        )


@router.post("/apply-changes", response_model=StateChangeResult)
async def apply_state_changes(
    request: ApplyStateChangesRequest,
    db: Session = Depends(get_db)
):
    """
    Apply parsed state changes to the game state
    """
    try:
        # Get session context
        session = redis_service.get_game_session(request.session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Game session not found"
            )
        
        # Get character
        character = db.query(Character).filter(Character.id == session.character_id).first()
        if not character:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Character not found"
            )
        
        applied_changes = []
        failed_changes = []
        warnings = []
        
        # Process state changes from parsed response
        state_changes = request.parsed_response.get('state_changes', [])
        
        for change_data in state_changes:
            try:
                entity_type = change_data.get('entity_type')
                property_name = change_data.get('property_name')
                new_value = change_data.get('new_value')
                change_amount = change_data.get('change_amount')
                
                if entity_type == 'character' and not request.dry_run:
                    # Apply character state changes
                    if property_name == 'current_hp' and change_amount is not None:
                        old_hp = character.current_hit_points
                        new_hp = max(0, min(character.max_hit_points, old_hp + change_amount))
                        
                        if not request.dry_run:
                            character.current_hit_points = new_hp
                            db.commit()
                        
                        applied_changes.append({
                            'type': 'hp_change',
                            'old_value': old_hp,
                            'new_value': new_hp,
                            'change_amount': change_amount,
                            'property': property_name
                        })
                    
                    elif property_name == 'location' and new_value:
                        old_location = getattr(character, 'current_location', 'Unknown')
                        
                        if not request.dry_run:
                            # Update character location (assuming we add this field)
                            # character.current_location = new_value
                            # db.commit()
                            pass  # For now, just track the change
                        
                        applied_changes.append({
                            'type': 'location_change',
                            'old_value': old_location,
                            'new_value': new_value,
                            'property': property_name
                        })
                
                else:
                    # Preview mode or unsupported entity type
                    applied_changes.append({
                        'type': 'preview',
                        'entity_type': entity_type,
                        'property': property_name,
                        'new_value': new_value,
                        'change_amount': change_amount
                    })
                
            except Exception as e:
                failed_changes.append({
                    'change_data': change_data,
                    'error': str(e)
                })
        
        # Update Redis cache with new character state
        if applied_changes and not request.dry_run:
            redis_service.cache_character(character)
        
        # Generate summary
        summary = {
            'total_changes': len(state_changes),
            'applied_count': len(applied_changes),
            'failed_count': len(failed_changes),
            'dry_run': request.dry_run,
            'character_id': character.id,
            'session_id': request.session_id
        }
        
        return StateChangeResult(
            applied_changes=applied_changes,
            failed_changes=failed_changes,
            warnings=warnings,
            summary=summary
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to apply state changes: {str(e)}"
        )


@router.post("/validate", response_model=ValidationResult)
async def validate_parsed_data(request: ValidationRequest):
    """
    Validate parsed response data for consistency and reasonableness
    """
    try:
        validation_errors = []
        suggestions = []
        confidence_score = 1.0
        
        # Validate dice rolls
        dice_rolls = request.parsed_data.get('dice_rolls', [])
        for roll in dice_rolls:
            dice_expr = roll.get('dice_expression', '')
            if not re.match(r'\d+d\d+([+-]\d+)?', dice_expr):
                validation_errors.append(f"Invalid dice expression: {dice_expr}")
                confidence_score = min(confidence_score, 0.7)
        
        # Validate state changes
        state_changes = request.parsed_data.get('state_changes', [])
        for change in state_changes:
            entity_type = change.get('entity_type')
            property_name = change.get('property_name')
            change_amount = change.get('change_amount')
            
            if entity_type == 'character' and property_name == 'current_hp':
                if change_amount and abs(change_amount) > 100:
                    validation_errors.append(f"Unusually large HP change: {change_amount}")
                    confidence_score = min(confidence_score, 0.8)
                    suggestions.append("Consider verifying the HP change amount")
        
        # Validate combat events
        combat_events = request.parsed_data.get('combat_events', [])
        for event in combat_events:
            damage_amount = event.get('damage_amount')
            if damage_amount and damage_amount > 200:
                validation_errors.append(f"Extremely high damage amount: {damage_amount}")
                confidence_score = min(confidence_score, 0.6)
        
        # Check for missing critical data
        if not any([
            request.parsed_data.get('actions'),
            request.parsed_data.get('state_changes'),
            request.parsed_data.get('dice_rolls'),
            request.parsed_data.get('combat_events'),
            request.parsed_data.get('story_events')
        ]):
            validation_errors.append("No structured data extracted from response")
            confidence_score = min(confidence_score, 0.3)
            suggestions.append("Consider improving AI prompt structure")
        
        # Game context validation
        if request.game_context:
            character_context = request.game_context.get('character', {})
            current_hp = character_context.get('current_hp', 0)
            max_hp = character_context.get('max_hp', 1)
            
            # Check for healing beyond max HP
            hp_changes = sum(
                change.get('change_amount', 0) 
                for change in state_changes 
                if change.get('property_name') == 'current_hp'
            )
            
            if current_hp + hp_changes > max_hp:
                suggestions.append("HP change would exceed maximum - will be capped")
            elif current_hp + hp_changes < 0:
                suggestions.append("HP change would go below 0 - character may be unconscious")
        
        is_valid = len(validation_errors) == 0 and confidence_score > 0.5
        
        return ValidationResult(
            is_valid=is_valid,
            confidence_score=confidence_score,
            validation_errors=validation_errors,
            suggestions=suggestions
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate parsed data: {str(e)}"
        )


@router.get("/patterns")
async def get_parsing_patterns():
    """
    Get the current parsing patterns and their descriptions
    """
    patterns = {
        'dice_patterns': {
            'description': 'Patterns for detecting dice roll expressions',
            'examples': ['1d20+5', '2d6', '1d8-1'],
            'regex': r'(\d+)d(\d+)(?:\+(\d+))?(?:\-(\d+))?'
        },
        'damage_patterns': {
            'description': 'Patterns for detecting damage amounts and types',
            'examples': ['8 slashing damage', '12 fire damage', '5 damage'],
            'regex': r'(\d+)\s*(slashing|piercing|bludgeoning|fire|cold|lightning|poison|acid|psychic|necrotic|radiant|force)?\s*damage'
        },
        'hp_change_patterns': {
            'description': 'Patterns for detecting hit point changes',
            'examples': ['gains 8 hit points', 'loses 5 hp', 'takes 12 damage'],
            'regex': r'(gains?|loses?|takes?)\s*(\d+)\s*(hit\s*points?|hp|health)'
        },
        'location_patterns': {
            'description': 'Patterns for detecting movement and location changes',
            'examples': ['moves to the tavern', 'travels to the forest', 'goes to the dungeon'],
            'regex': r'(moves?|travels?|goes?)\s*to\s*([a-zA-Z\s]+)'
        },
        'skill_check_patterns': {
            'description': 'Patterns for detecting skill checks and saving throws',
            'examples': ['make a perception check', 'roll a dexterity save', 'constitution saving throw'],
            'regex': r'(make|roll)\s*a?\s*([a-zA-Z\s]+)\s*(check|save|saving throw)'
        }
    }
    
    return patterns


@router.get("/health")
async def parsing_health_check():
    """
    Health check for the response parsing service
    """
    try:
        # Test basic parsing functionality
        test_response = "The hero attacks the goblin and deals 8 slashing damage. The goblin loses 8 hit points."
        parsed = response_parser.parse_response(test_response)
        
        health_status = {
            'status': 'healthy',
            'service': 'Response Parsing',
            'patterns_loaded': True,
            'test_parse_successful': parsed.confidence_score > 0.5,
            'parsing_confidence': parsed.confidence_score,
            'extracted_events': {
                'actions': len(parsed.actions),
                'state_changes': len(parsed.state_changes),
                'dice_rolls': len(parsed.dice_rolls),
                'combat_events': len(parsed.combat_events),
                'story_events': len(parsed.story_events)
            }
        }
        
        return health_status
        
    except Exception as e:
        return {
            'status': 'unhealthy',
            'service': 'Response Parsing',
            'error': str(e)
        } 