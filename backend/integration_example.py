"""
Integration Example: AI Service with Game Systems
Demonstrates how the GPT-4o AI service integrates with existing story, character, and combat systems.
"""

from typing import Dict, Any
from sqlalchemy.orm import Session
from services.ai_service import ai_service
from services.story_service import StoryService  
from services.combat_service import CombatService
from models.character import Character
from models.story import StoryArc, WorldState
from models.combat import CombatEncounter


class EnhancedGameplayService:
    """
    Service that combines existing game logic with AI narration
    Shows how AI enhances rather than replaces existing systems
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.story_service = StoryService(db)
        self.combat_service = CombatService(db)
    
    async def handle_player_action(self, character_id: int, story_arc_id: int, 
                                  action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhanced player action handling with AI narration
        """
        character = self.db.query(Character).filter(Character.id == character_id).first()
        story_arc = self.db.query(StoryArc).filter(StoryArc.id == story_arc_id).first()
        
        if not character or not story_arc:
            return {'success': False, 'error': 'Character or story not found'}
        
        action_type = action.get('type')
        result = {'success': True, 'responses': []}
        
        # Handle different action types
        if action_type == 'story_action':
            result = await self._handle_story_action(character, story_arc, action)
        
        elif action_type == 'combat_action':
            result = await self._handle_combat_action(character, story_arc, action)
        
        elif action_type == 'npc_interaction':
            result = await self._handle_npc_interaction(character, story_arc, action)
        
        elif action_type == 'major_decision':
            result = await self._handle_major_decision(character, story_arc, action)
        
        else:
            # Generic action handling with AI narration
            result = await self._handle_generic_action(character, story_arc, action)
        
        return result
    
    async def _handle_story_action(self, character: Character, story_arc: StoryArc, 
                                  action: Dict[str, Any]) -> Dict[str, Any]:
        """Handle story-related actions with AI narration"""
        
        # Process the action through existing story service
        story_result = self.story_service.process_player_action(
            character_id=character.id,
            story_arc_id=story_arc.id,
            action=action.get('description', '')
        )
        
        if not story_result.get('success'):
            return story_result
        
        # Generate AI narration for the action
        ai_result = ai_service.narrate_story(
            db=self.db,
            character_id=character.id,
            story_arc_id=story_arc.id,
            player_action=action.get('description'),
            additional_context=action.get('context')
        )
        
        return {
            'success': True,
            'action_result': story_result,
            'ai_narration': ai_result.get('content') if ai_result.get('success') else None,
            'story_updates': story_result.get('updates', {}),
            'new_choices': story_result.get('choices', [])
        }
    
    async def _handle_combat_action(self, character: Character, story_arc: StoryArc, 
                                   action: Dict[str, Any]) -> Dict[str, Any]:
        """Handle combat actions with dramatic AI narration"""
        
        combat_encounter_id = action.get('combat_encounter_id')
        if not combat_encounter_id:
            return {'success': False, 'error': 'No combat encounter specified'}
        
        # Process combat through existing combat service
        combat_result = self.combat_service.process_combat_action(
            character_id=character.id,
            combat_encounter_id=combat_encounter_id,
            action=action.get('combat_action', {})
        )
        
        if not combat_result.get('success'):
            return combat_result
        
        # Generate AI narration for the combat action
        ai_result = ai_service.narrate_combat(
            db=self.db,
            character_id=character.id,
            story_arc_id=story_arc.id,
            combat_encounter_id=combat_encounter_id,
            combat_action=action.get('combat_action', {}),
            combat_result=combat_result.get('result', {})
        )
        
        return {
            'success': True,
            'combat_result': combat_result,
            'ai_narration': ai_result.get('content') if ai_result.get('success') else None,
            'damage_dealt': combat_result.get('damage_dealt', 0),
            'damage_taken': combat_result.get('damage_taken', 0),
            'combat_status': combat_result.get('status', 'ongoing')
        }
    
    async def _handle_npc_interaction(self, character: Character, story_arc: StoryArc, 
                                     action: Dict[str, Any]) -> Dict[str, Any]:
        """Handle NPC interactions with personality-driven responses"""
        
        npc_name = action.get('npc_name')
        interaction_type = action.get('interaction_type', 'dialogue')
        player_input = action.get('player_input', '')
        
        # Update NPC status in story if needed
        if story_arc.npc_status and npc_name in story_arc.npc_status:
            # Could add logic here to update NPC disposition based on interaction
            pass
        
        # Generate AI response for the NPC
        ai_result = ai_service.handle_npc_interaction(
            db=self.db,
            character_id=character.id,
            story_arc_id=story_arc.id,
            npc_name=npc_name,
            interaction_type=interaction_type,
            player_input=player_input
        )
        
        return {
            'success': True,
            'npc_response': ai_result.get('content') if ai_result.get('success') else 'The NPC doesn\'t respond.',
            'npc_name': npc_name,
            'interaction_type': interaction_type,
            'relationship_change': self._calculate_relationship_change(action)
        }
    
    async def _handle_major_decision(self, character: Character, story_arc: StoryArc, 
                                    action: Dict[str, Any]) -> Dict[str, Any]:
        """Handle major story decisions with consequence narration"""
        
        decision = action.get('decision', {})
        
        # Record the decision in the story arc
        story_arc.add_decision(decision)
        self.db.commit()
        
        # Generate AI narration for the decision consequences
        ai_result = ai_service.process_decision_outcome(
            db=self.db,
            character_id=character.id,
            story_arc_id=story_arc.id,
            decision=decision
        )
        
        # Check if this decision allows story progression
        can_advance = story_arc.can_advance_stage()
        
        return {
            'success': True,
            'decision_recorded': True,
            'ai_narration': ai_result.get('content') if ai_result.get('success') else None,
            'consequences': decision.get('consequences', []),
            'can_advance_story': can_advance,
            'current_stage': story_arc.current_stage.value
        }
    
    async def _handle_generic_action(self, character: Character, story_arc: StoryArc, 
                                    action: Dict[str, Any]) -> Dict[str, Any]:
        """Handle generic actions with AI narration"""
        
        # For any action not fitting specific categories, use general story narration
        ai_result = ai_service.narrate_story(
            db=self.db,
            character_id=character.id,
            story_arc_id=story_arc.id,
            player_action=action.get('description', 'The player takes an action'),
            additional_context=action.get('context')
        )
        
        return {
            'success': True,
            'ai_narration': ai_result.get('content') if ai_result.get('success') else None,
            'action_type': 'generic'
        }
    
    def _calculate_relationship_change(self, action: Dict[str, Any]) -> str:
        """Calculate how an interaction affects NPC relationships"""
        interaction_type = action.get('interaction_type', 'dialogue')
        player_input = action.get('player_input', '').lower()
        
        # Simple heuristics for relationship changes
        if interaction_type == 'persuasion' and ('please' in player_input or 'help' in player_input):
            return 'improved'
        elif interaction_type == 'intimidation' or 'threat' in player_input:
            return 'worsened'
        else:
            return 'unchanged'


class AIEnhancedStoryProgression:
    """
    Example of how AI enhances story progression and world building
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    async def advance_story_with_narration(self, story_arc_id: int, character_id: int) -> Dict[str, Any]:
        """Advance story stage with AI-generated transition narration"""
        
        story_arc = self.db.query(StoryArc).filter(StoryArc.id == story_arc_id).first()
        character = self.db.query(Character).filter(Character.id == character_id).first()
        
        if not story_arc or not character:
            return {'success': False, 'error': 'Story or character not found'}
        
        if not story_arc.can_advance_stage():
            return {'success': False, 'error': 'Conditions not met to advance story'}
        
        current_stage = story_arc.current_stage
        
        # Advance the story stage
        story_arc.advance_stage()
        self.db.commit()
        
        # Generate transition narration
        transition_context = f"The story is transitioning from {current_stage.value} to {story_arc.current_stage.value}"
        
        ai_result = ai_service.narrate_story(
            db=self.db,
            character_id=character_id,
            story_arc_id=story_arc_id,
            additional_context=transition_context
        )
        
        return {
            'success': True,
            'previous_stage': current_stage.value,
            'new_stage': story_arc.current_stage.value,
            'transition_narration': ai_result.get('content') if ai_result.get('success') else None,
            'story_completed': story_arc.story_completed
        }
    
    async def generate_dynamic_world_content(self, world_state: WorldState, content_type: str) -> Dict[str, Any]:
        """Generate dynamic world content based on current state"""
        
        if content_type == 'location_description':
            prompt = f"""
            Describe a new location the character might discover near {world_state.current_location}.
            Consider the established lore: {world_state.established_lore}
            Make it interesting and tied to the ongoing story.
            """
        
        elif content_type == 'random_encounter':
            prompt = f"""
            Create a random encounter appropriate for a character at {world_state.current_location}.
            It should be interesting but not derail the main story.
            Consider the world lore: {world_state.established_lore}
            """
        
        elif content_type == 'quest_hook':
            prompt = f"""
            Generate a side quest opportunity that could be discovered at {world_state.current_location}.
            It should complement the main story and feel natural in this world.
            """
        
        else:
            return {'success': False, 'error': 'Unknown content type'}
        
        ai_result = ai_service.generate_dynamic_content(
            prompt_type=content_type,
            custom_prompt=prompt,
            max_tokens=800,
            temperature=0.8
        )
        
        return {
            'success': ai_result.get('success', False),
            'content': ai_result.get('content'),
            'content_type': content_type,
            'location': world_state.current_location
        }


# Example usage patterns for frontend integration
EXAMPLE_API_CALLS = {
    "story_action": {
        "endpoint": "POST /api/ai/narrate-story",
        "payload": {
            "character_id": 1,
            "story_arc_id": 1,
            "player_action": "I search the room carefully for hidden doors or secret compartments",
            "additional_context": "The room seems ordinary but the character has high Investigation skill"
        }
    },
    
    "combat_narration": {
        "endpoint": "POST /api/ai/narrate-combat", 
        "payload": {
            "character_id": 1,
            "story_arc_id": 1,
            "combat_encounter_id": 1,
            "combat_action": {
                "action_type": "spell",
                "spell_name": "Fire Bolt",
                "target": "goblin_shaman",
                "attack_roll": 16
            },
            "combat_result": {
                "hit": True,
                "damage": 7,
                "damage_type": "fire",
                "special_effects": ["target_ignited"]
            }
        }
    },
    
    "npc_dialogue": {
        "endpoint": "POST /api/ai/npc-interaction",
        "payload": {
            "character_id": 1,
            "story_arc_id": 1,
            "npc_name": "merchant_elena",
            "interaction_type": "bargaining",
            "player_input": "These prices seem quite high. I'm sure we can work out something more reasonable for a fellow traveler?"
        }
    }
}


if __name__ == "__main__":
    print("🎮 SoloRealms AI Integration Examples")
    print("=" * 50)
    print("\nThis file demonstrates how the AI service enhances existing game systems:")
    print("\n1. 🎭 Story Actions: AI narrates consequences of player choices")
    print("2. ⚔️  Combat: Dynamic descriptions of attacks and abilities")
    print("3. 👥 NPCs: Personality-driven dialogue and reactions")
    print("4. 🌍 World Building: Dynamic content generation")
    print("\nSee EXAMPLE_API_CALLS for frontend integration patterns")
    print("\n📚 Key Benefits:")
    print("  • Existing game logic remains unchanged")
    print("  • AI enhances immersion without replacing mechanics")
    print("  • Consistent character and story state")
    print("  • Scalable to new content types") 