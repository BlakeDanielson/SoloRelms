"""
Response Parser Service for GPT-4o AI DM Outputs
Extracts structured game data from narrative text responses for state updates and game logic.
"""

import re
import json
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class ActionType(Enum):
    """Types of actions that can be extracted from AI responses"""
    MOVEMENT = "movement"
    COMBAT = "combat"
    SKILL_CHECK = "skill_check"
    INTERACTION = "interaction"
    DIALOGUE = "dialogue"
    INVENTORY = "inventory"
    STORY_PROGRESSION = "story_progression"
    ENVIRONMENTAL = "environmental"


class DamageType(Enum):
    """Types of damage in D&D"""
    SLASHING = "slashing"
    PIERCING = "piercing"
    BLUDGEONING = "bludgeoning"
    FIRE = "fire"
    COLD = "cold"
    LIGHTNING = "lightning"
    POISON = "poison"
    ACID = "acid"
    PSYCHIC = "psychic"
    NECROTIC = "necrotic"
    RADIANT = "radiant"
    FORCE = "force"


@dataclass
class DiceRoll:
    """Represents a dice roll requirement or result"""
    dice_expression: str  # e.g., "1d20+5", "2d6"
    purpose: str  # e.g., "attack roll", "damage", "saving throw"
    target_number: Optional[int] = None  # DC or AC to beat
    advantage: bool = False
    disadvantage: bool = False
    modifier: int = 0


@dataclass
class StateChange:
    """Represents a change to game state"""
    entity_type: str  # "character", "npc", "environment"
    entity_id: Optional[str] = None
    property_name: str = ""  # e.g., "current_hp", "location", "status"
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None
    change_amount: Optional[int] = None  # For numeric changes


@dataclass
class CombatEvent:
    """Represents a combat-related event"""
    event_type: str  # "attack", "damage", "heal", "status_effect", "initiative"
    attacker: Optional[str] = None
    target: Optional[str] = None
    damage_amount: Optional[int] = None
    damage_type: Optional[DamageType] = None
    healing_amount: Optional[int] = None
    status_effect: Optional[str] = None
    duration: Optional[int] = None


@dataclass
class StoryEvent:
    """Represents a story progression event"""
    event_type: str  # "decision", "discovery", "objective_complete", "location_change"
    description: str
    consequences: List[str]
    new_objective: Optional[str] = None
    completed_objective: Optional[str] = None


@dataclass
class ParsedResponse:
    """Complete parsed response from AI DM"""
    narrative_text: str
    actions: List[Dict[str, Any]]
    state_changes: List[StateChange]
    dice_rolls: List[DiceRoll]
    combat_events: List[CombatEvent]
    story_events: List[StoryEvent]
    confidence_score: float  # How confident we are in the parsing
    parsing_errors: List[str]
    raw_structured_data: Optional[Dict[str, Any]] = None


class ResponseParser:
    """
    Main response parser service that extracts structured game data from AI narratives
    """
    
    def __init__(self):
        self.dice_pattern = re.compile(r'(\d+)d(\d+)(?:\+(\d+))?(?:\-(\d+))?')
        self.damage_pattern = re.compile(r'(\d+)\s*(slashing|piercing|bludgeoning|fire|cold|lightning|poison|acid|psychic|necrotic|radiant|force)?\s*damage', re.IGNORECASE)
        self.hp_change_pattern = re.compile(r'(gains?|loses?|takes?)\s*(\d+)\s*(hit\s*points?|hp|health)', re.IGNORECASE)
        self.location_pattern = re.compile(r'(moves?|travels?|goes?)\s*to\s*([a-zA-Z\s]+)', re.IGNORECASE)
        self.skill_check_pattern = re.compile(r'(make|roll)\s*a?\s*([a-zA-Z\s]+)\s*(check|save|saving throw)', re.IGNORECASE)
    
    def parse_response(self, ai_response: str, context: Optional[Dict[str, Any]] = None) -> ParsedResponse:
        """
        Main parsing method that extracts all structured data from AI response
        """
        logger.info("Starting response parsing...")
        
        parsing_errors = []
        confidence_score = 1.0
        
        try:
            # 1. Try to extract structured data sections first
            structured_data = self._extract_structured_sections(ai_response)
            
            # 2. Parse different types of events
            actions = self._parse_actions(ai_response, structured_data)
            state_changes = self._parse_state_changes(ai_response, structured_data)
            dice_rolls = self._parse_dice_rolls(ai_response, structured_data)
            combat_events = self._parse_combat_events(ai_response, structured_data)
            story_events = self._parse_story_events(ai_response, structured_data)
            
            # 3. Clean up narrative text (remove structured sections)
            narrative_text = self._clean_narrative_text(ai_response)
            
            # 4. Validate parsed data
            confidence_score, validation_errors = self._validate_parsed_data(
                actions, state_changes, dice_rolls, combat_events, story_events
            )
            parsing_errors.extend(validation_errors)
            
            return ParsedResponse(
                narrative_text=narrative_text,
                actions=actions,
                state_changes=state_changes,
                dice_rolls=dice_rolls,
                combat_events=combat_events,
                story_events=story_events,
                confidence_score=confidence_score,
                parsing_errors=parsing_errors,
                raw_structured_data=structured_data
            )
            
        except Exception as e:
            logger.error(f"Error parsing AI response: {e}")
            parsing_errors.append(f"Parse error: {str(e)}")
            
            # Return basic fallback parsing
            return ParsedResponse(
                narrative_text=ai_response,
                actions=[],
                state_changes=[],
                dice_rolls=[],
                combat_events=[],
                story_events=[],
                confidence_score=0.1,
                parsing_errors=parsing_errors
            )
    
    def _extract_structured_sections(self, response: str) -> Dict[str, Any]:
        """
        Extract JSON or structured sections from AI response
        """
        structured_data = {}
        
        # Look for JSON blocks
        json_pattern = re.compile(r'```json\s*(\{.*?\})\s*```', re.DOTALL | re.IGNORECASE)
        json_matches = json_pattern.findall(response)
        
        for match in json_matches:
            try:
                data = json.loads(match)
                structured_data.update(data)
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse JSON section: {match[:100]}...")
        
        # Look for structured sections with headers
        sections = {
            'ACTIONS': r'(?:ACTIONS?|GAME ACTIONS?):\s*(.*?)(?=\n[A-Z\s]+:|$)',
            'STATE_CHANGES': r'(?:STATE CHANGES?|UPDATES?):\s*(.*?)(?=\n[A-Z\s]+:|$)',
            'DICE_ROLLS': r'(?:DICE ROLLS?|ROLLS?):\s*(.*?)(?=\n[A-Z\s]+:|$)',
            'COMBAT': r'(?:COMBAT|COMBAT EVENTS?):\s*(.*?)(?=\n[A-Z\s]+:|$)',
            'STORY': r'(?:STORY|STORY EVENTS?):\s*(.*?)(?=\n[A-Z\s]+:|$)'
        }
        
        for section_name, pattern in sections.items():
            matches = re.findall(pattern, response, re.DOTALL | re.IGNORECASE)
            if matches:
                structured_data[section_name.lower()] = matches[0].strip()
        
        return structured_data
    
    def _parse_actions(self, response: str, structured_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse player and NPC actions from the response
        """
        actions = []
        
        # Check structured data first
        if 'actions' in structured_data:
            actions_text = structured_data['actions']
            actions.extend(self._parse_action_list(actions_text))
        
        # Parse common action patterns from narrative
        action_patterns = [
            (r'(attacks?|strikes?|hits?)\s*([a-zA-Z\s]+)', ActionType.COMBAT),
            (r'(moves?|walks?|runs?)\s*to\s*([a-zA-Z\s]+)', ActionType.MOVEMENT),
            (r'(casts?|uses?)\s*([a-zA-Z\s]+)', ActionType.COMBAT),
            (r'(talks?|speaks?|says?)\s*to\s*([a-zA-Z\s]+)', ActionType.DIALOGUE),
            (r'(searches?|examines?|investigates?)\s*([a-zA-Z\s]+)', ActionType.INTERACTION),
            (r'(picks? up|takes?|grabs?)\s*([a-zA-Z\s]+)', ActionType.INVENTORY)
        ]
        
        for pattern, action_type in action_patterns:
            matches = re.findall(pattern, response, re.IGNORECASE)
            for match in matches:
                action = {
                    'type': action_type.value,
                    'verb': match[0],
                    'object': match[1].strip(),
                    'raw_text': ' '.join(match)
                }
                actions.append(action)
        
        return actions
    
    def _parse_action_list(self, actions_text: str) -> List[Dict[str, Any]]:
        """
        Parse a structured list of actions
        """
        actions = []
        lines = actions_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Try to parse structured action format
            if ':' in line:
                parts = line.split(':', 1)
                action_type = parts[0].strip().lower()
                description = parts[1].strip()
                
                action = {
                    'type': action_type,
                    'description': description,
                    'raw_text': line
                }
                actions.append(action)
        
        return actions
    
    def _parse_state_changes(self, response: str, structured_data: Dict[str, Any]) -> List[StateChange]:
        """
        Parse state changes (HP, location, status effects, etc.)
        """
        state_changes = []
        
        # Parse HP changes
        hp_matches = self.hp_change_pattern.findall(response)
        for match in hp_matches:
            action_verb = match[0].lower()
            amount = int(match[1])
            
            if action_verb in ['gains', 'heals']:
                change_amount = amount
            else:  # loses, takes damage
                change_amount = -amount
            
            state_change = StateChange(
                entity_type="character",
                property_name="current_hp",
                change_amount=change_amount
            )
            state_changes.append(state_change)
        
        # Parse location changes
        location_matches = self.location_pattern.findall(response)
        for match in location_matches:
            new_location = match[1].strip()
            
            state_change = StateChange(
                entity_type="character",
                property_name="location",
                new_value=new_location
            )
            state_changes.append(state_change)
        
        # Parse structured state changes
        if 'state_changes' in structured_data:
            changes_text = structured_data['state_changes']
            state_changes.extend(self._parse_structured_state_changes(changes_text))
        
        return state_changes
    
    def _parse_structured_state_changes(self, changes_text: str) -> List[StateChange]:
        """
        Parse structured state change format
        """
        changes = []
        lines = changes_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Format: "entity.property: old_value -> new_value"
            if '->' in line:
                parts = line.split('->')
                if len(parts) == 2:
                    left = parts[0].strip()
                    new_value = parts[1].strip()
                    
                    if '.' in left:
                        entity_prop, old_value = left.split(':', 1) if ':' in left else (left, None)
                        entity_parts = entity_prop.split('.')
                        
                        change = StateChange(
                            entity_type=entity_parts[0],
                            entity_id=entity_parts[1] if len(entity_parts) > 2 else None,
                            property_name=entity_parts[-1],
                            old_value=old_value.strip() if old_value else None,
                            new_value=new_value
                        )
                        changes.append(change)
        
        return changes
    
    def _parse_dice_rolls(self, response: str, structured_data: Dict[str, Any]) -> List[DiceRoll]:
        """
        Parse dice roll requirements and results
        """
        dice_rolls = []
        
        # Parse dice expressions
        dice_matches = self.dice_pattern.findall(response)
        for match in dice_matches:
            num_dice = int(match[0])
            die_size = int(match[1])
            plus_mod = int(match[2]) if match[2] else 0
            minus_mod = int(match[3]) if match[3] else 0
            
            modifier = plus_mod - minus_mod
            dice_expression = f"{num_dice}d{die_size}"
            if modifier > 0:
                dice_expression += f"+{modifier}"
            elif modifier < 0:
                dice_expression += str(modifier)
            
            # Try to determine purpose from context
            purpose = self._determine_dice_purpose(response, dice_expression)
            
            dice_roll = DiceRoll(
                dice_expression=dice_expression,
                purpose=purpose,
                modifier=modifier
            )
            dice_rolls.append(dice_roll)
        
        # Parse skill checks
        skill_matches = self.skill_check_pattern.findall(response)
        for match in skill_matches:
            skill_name = match[1].strip()
            check_type = match[2].strip()
            
            dice_roll = DiceRoll(
                dice_expression="1d20",
                purpose=f"{skill_name} {check_type}"
            )
            dice_rolls.append(dice_roll)
        
        return dice_rolls
    
    def _determine_dice_purpose(self, response: str, dice_expression: str) -> str:
        """
        Determine the purpose of a dice roll from context
        """
        # Find the sentence containing the dice expression
        sentences = response.split('.')
        for sentence in sentences:
            if dice_expression in sentence:
                sentence_lower = sentence.lower()
                
                if 'attack' in sentence_lower:
                    return 'attack roll'
                elif 'damage' in sentence_lower:
                    return 'damage'
                elif 'save' in sentence_lower or 'saving' in sentence_lower:
                    return 'saving throw'
                elif 'check' in sentence_lower:
                    return 'ability check'
                elif 'initiative' in sentence_lower:
                    return 'initiative'
        
        return 'unknown'
    
    def _parse_combat_events(self, response: str, structured_data: Dict[str, Any]) -> List[CombatEvent]:
        """
        Parse combat-specific events
        """
        combat_events = []
        
        # Enhanced combat detection keywords and phrases
        combat_initiation_keywords = [
            'combat begins', 'initiative', 'roll for initiative', 'the fight starts',
            'battle commences', 'combat starts', 'enters combat', 'combat encounter',
            'hostile', 'aggressive', 'attacks you', 'draws weapon', 'brandishes',
            'combat mode', 'turn order', 'combat round', 'attack roll', 'initiative time',
            'battle begins', 'fight begins', 'combat initiated', 'enter combat'
        ]
        
        # Enhanced combat action phrases that strongly indicate combat has started
        combat_action_phrases = [
            'raises his weapon', 'draws his sword', 'prepares to attack', 'lunges forward',
            'swings at you', 'charges toward', 'defensive stance', 'battle cry',
            'weapon gleams', 'ready for battle', 'combat stance', 'initiative roll'
        ]
        
        # Check for combat initiation
        response_lower = response.lower()
        
        # Strong combat initiation indicators
        combat_initiation_found = False
        for keyword in combat_initiation_keywords:
            if keyword in response_lower:
                combat_initiation_found = True
                break
        
        # Additional check for combat action phrases
        if not combat_initiation_found:
            for phrase in combat_action_phrases:
                if phrase in response_lower:
                    combat_initiation_found = True
                    break
        
        # Enhanced pattern matching for combat scenarios
        combat_patterns = [
            r'combat\s+(begins|starts|commences)',
            r'roll\s+for\s+initiative',
            r'initiative\s+(roll|time|order)',
            r'battle\s+(begins|starts|commences)',
            r'fight\s+(begins|starts)',
            r'(attack|swing|lunge|charge)\s+(at|toward|forward)',
            r'(draws?|raise[sd]?|brandish)\s+(weapon|sword|axe|bow)',
            r'turn\s+order',
            r'(defensive|combat)\s+stance'
        ]
        
        import re
        for pattern in combat_patterns:
            if re.search(pattern, response_lower):
                combat_initiation_found = True
                break
        
        # If combat initiation is detected, create combat_initiated event
        if combat_initiation_found:
            combat_events.append(CombatEvent(
                event_type="combat_initiated"
            ))
        
        # Parse attack events
        attack_patterns = [
            r'(attacks?|strikes?|hits?|swings?)\s+(?:at\s+)?(?:you|the)',
            r'deals?\s+(\d+)\s+damage',
            r'takes?\s+(\d+)\s+damage',
            r'(slashes?|stabs?|shoots?|casts?)'
        ]
        
        for pattern in attack_patterns:
            matches = re.finditer(pattern, response_lower)
            for match in matches:
                combat_events.append(CombatEvent(
                    event_type="attack"
                ))
        
        # Parse damage events using the existing damage pattern
        damage_matches = self.damage_pattern.findall(response)
        for match in damage_matches:
            damage_amount = int(match[0])
            damage_type_str = match[1].lower() if match[1] else None
            
            damage_type = None
            if damage_type_str:
                try:
                    damage_type = DamageType(damage_type_str)
                except ValueError:
                    pass
            
            combat_events.append(CombatEvent(
                event_type="damage",
                damage_amount=damage_amount,
                damage_type=damage_type
            ))
        
        return combat_events
    
    def _parse_story_events(self, response: str, structured_data: Dict[str, Any]) -> List[StoryEvent]:
        """
        Parse story progression events
        """
        story_events = []
        
        # Parse structured story events
        if 'story' in structured_data:
            story_text = structured_data['story']
            story_events.extend(self._parse_structured_story(story_text))
        
        # Parse narrative for story events
        story_patterns = [
            r'(discovers?|finds?|uncovers?)\s*([a-zA-Z\s]+)',
            r'(completes?|finishes?)\s*([a-zA-Z\s]+)',
            r'(decides?|chooses?)\s*to\s*([a-zA-Z\s]+)'
        ]
        
        for pattern in story_patterns:
            matches = re.findall(pattern, response, re.IGNORECASE)
            for match in matches:
                event = StoryEvent(
                    event_type="discovery" if "discover" in match[0] else "decision",
                    description=f"{match[0]} {match[1]}",
                    consequences=[]
                )
                story_events.append(event)
        
        return story_events
    
    def _parse_structured_story(self, story_text: str) -> List[StoryEvent]:
        """
        Parse structured story event format
        """
        events = []
        lines = story_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Simple story event parsing
            if ':' in line:
                event_type, description = line.split(':', 1)
                
                event = StoryEvent(
                    event_type=event_type.strip().lower(),
                    description=description.strip(),
                    consequences=[]
                )
                events.append(event)
        
        return events
    
    def _clean_narrative_text(self, response: str) -> str:
        """
        Remove structured sections and return clean narrative text
        """
        # Remove JSON blocks
        response = re.sub(r'```json\s*\{.*?\}\s*```', '', response, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove structured sections
        section_patterns = [
            r'(?:ACTIONS?|GAME ACTIONS?):\s*.*?(?=\n[A-Z\s]+:|$)',
            r'(?:STATE CHANGES?|UPDATES?):\s*.*?(?=\n[A-Z\s]+:|$)',
            r'(?:DICE ROLLS?|ROLLS?):\s*.*?(?=\n[A-Z\s]+:|$)',
            r'(?:COMBAT|COMBAT EVENTS?):\s*.*?(?=\n[A-Z\s]+:|$)',
            r'(?:STORY|STORY EVENTS?):\s*.*?(?=\n[A-Z\s]+:|$)'
        ]
        
        for pattern in section_patterns:
            response = re.sub(pattern, '', response, flags=re.DOTALL | re.IGNORECASE)
        
        # Clean up extra whitespace
        response = re.sub(r'\n\s*\n', '\n\n', response)
        response = response.strip()
        
        return response
    
    def _validate_parsed_data(self, actions: List[Dict], state_changes: List[StateChange], 
                            dice_rolls: List[DiceRoll], combat_events: List[CombatEvent],
                            story_events: List[StoryEvent]) -> Tuple[float, List[str]]:
        """
        Validate parsed data and return confidence score and errors
        """
        errors = []
        confidence = 1.0
        
        # Check for reasonable data amounts
        total_events = len(actions) + len(state_changes) + len(dice_rolls) + len(combat_events) + len(story_events)
        
        if total_events == 0:
            confidence = 0.3
            errors.append("No structured events extracted")
        elif total_events > 20:
            confidence = 0.7
            errors.append("Unusually large number of events extracted")
        
        # Validate state changes
        for change in state_changes:
            if change.property_name == "current_hp" and change.change_amount:
                if abs(change.change_amount) > 100:  # Reasonable HP change limit
                    confidence = min(confidence, 0.8)
                    errors.append(f"Unusually large HP change: {change.change_amount}")
        
        # Validate dice rolls
        for roll in dice_rolls:
            if not self.dice_pattern.match(roll.dice_expression.replace('+', '').replace('-', '')):
                confidence = min(confidence, 0.7)
                errors.append(f"Invalid dice expression: {roll.dice_expression}")
        
        return confidence, errors
    
    def extract_quick_summary(self, parsed_response: ParsedResponse) -> Dict[str, Any]:
        """
        Extract a quick summary of the most important parsed elements
        """
        summary = {
            'has_combat': len(parsed_response.combat_events) > 0,
            'has_state_changes': len(parsed_response.state_changes) > 0,
            'requires_dice_rolls': len(parsed_response.dice_rolls) > 0,
            'story_progression': len(parsed_response.story_events) > 0,
            'confidence': parsed_response.confidence_score,
            'key_actions': [action.get('type', 'unknown') for action in parsed_response.actions[:3]],
            'hp_changes': sum(change.change_amount or 0 for change in parsed_response.state_changes 
                             if change.property_name == 'current_hp'),
            'parsing_quality': 'good' if parsed_response.confidence_score > 0.8 else 
                              'fair' if parsed_response.confidence_score > 0.5 else 'poor'
        }
        
        return summary


# Global instance
response_parser = ResponseParser() 