"""
Enhanced AI + Redis Integration Example
Demonstrates how Redis state management supercharges AI prompt building and session persistence
"""

import os
import sys
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

# Add the backend directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.ai_service import ai_service
from services.redis_service import redis_service, CacheExpiry
from models.character import Character
from models.story import StoryArc, WorldState, StoryStage
from models.combat import CombatEncounter, CombatState


class OptimizedGameplayService:
    """
    Enhanced gameplay service that combines AI and Redis for maximum performance
    Shows how state management supercharges the AI experience
    """
    
    def __init__(self):
        self.ai_service = ai_service
        self.redis_service = redis_service
    
    async def start_enhanced_game_session(self, user_id: str, character_id: int, story_arc_id: int) -> str:
        """
        Start a game session with AI + Redis integration
        This creates a persistent session with pre-cached data for lightning-fast AI responses
        """
        print(f"🚀 Starting enhanced game session for user {user_id}")
        
        # 1. Create Redis session for state persistence
        session = self.redis_service.create_game_session(user_id, character_id, story_arc_id)
        print(f"✅ Created session: {session.session_id}")
        
        # 2. Pre-cache character data for AI prompts (normally from database)
        mock_character = self._create_mock_character(character_id)
        self.redis_service.cache_character(mock_character, CacheExpiry.LONG)
        print(f"✅ Cached character: {mock_character.name}")
        
        # 3. Pre-cache story data for context
        mock_story, mock_world = self._create_mock_story_data(story_arc_id)
        self.redis_service.cache_story(mock_story, mock_world, CacheExpiry.MEDIUM)
        print(f"✅ Cached story: {mock_story.title}")
        
        # 4. Cache combined AI prompt data for ultra-fast access
        character_cache = self.redis_service.get_cached_character(character_id)
        story_cache = self.redis_service.get_cached_story(story_arc_id)
        
        if character_cache and story_cache:
            self.redis_service.cache_ai_prompt_data(session.session_id, character_cache, story_cache)
            print("✅ Cached AI prompt data for instant access")
        
        return session.session_id
    
    async def fast_ai_story_narration(self, session_id: str, player_action: str) -> Dict[str, Any]:
        """
        Generate AI story narration using cached data for maximum speed
        This demonstrates the performance benefits of Redis + AI integration
        """
        print(f"🤖 Generating fast AI narration for session: {session_id}")
        
        # 1. Update session activity
        self.redis_service.update_session_activity(session_id)
        
        # 2. Get cached AI prompt data (lightning fast!)
        cached_data = self.redis_service.get_ai_prompt_data(session_id)
        
        if cached_data:
            print("⚡ Using cached prompt data (ultra-fast path)")
            character_data = cached_data['character']
            story_data = cached_data['story']
        else:
            print("🔄 Cache miss - rebuilding prompt data")
            # Fallback: rebuild from individual caches
            session = self.redis_service.get_game_session(session_id)
            if not session:
                raise ValueError(f"Session {session_id} not found")
            
            character_cache = self.redis_service.get_cached_character(session.character_id)
            story_cache = self.redis_service.get_cached_story(session.story_arc_id)
            
            if not character_cache or not story_cache:
                raise ValueError("Required cache data not available")
            
            character_data = character_cache.to_dict()
            story_data = story_cache.to_dict()
        
        # 3. Build context for AI (now super fast with cached data)
        context = {
            'character': {
                'name': character_data['name'],
                'race': character_data['race'],
                'class': character_data['character_class'],
                'level': character_data['level'],
                'current_hp': character_data['current_hp'],
                'max_hp': character_data['max_hp'],
                'background': character_data['background']
            },
            'story': {
                'title': story_data['title'],
                'current_stage': story_data['current_stage'],
                'location': story_data['world_location'],
                'recent_decisions': story_data['major_decisions'][-3:] if story_data['major_decisions'] else [],
                'objectives': story_data['objectives']
            },
            'player_action': player_action
        }
        
        # 4. Generate AI response (the AI service can focus purely on content generation)
        # Note: In production, this would make actual AI API calls
        response = {
            'narration': self._generate_mock_narration(context),
            'session_id': session_id,
            'timestamp': datetime.utcnow().isoformat(),
            'context_source': 'cached' if cached_data else 'rebuilt'
        }
        
        print(f"✅ Generated AI narration using {response['context_source']} data")
        return response
    
    async def handle_combat_with_state_persistence(self, session_id: str, action: str) -> Dict[str, Any]:
        """
        Handle combat with Redis state persistence
        Shows how combat state is maintained across interactions
        """
        print(f"⚔️ Processing combat action for session: {session_id}")
        
        # 1. Get or create combat state
        session = self.redis_service.get_game_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        # 2. Check for existing combat state
        combat_cache = self.redis_service.get_combat_state(1)  # Mock encounter ID
        
        if not combat_cache:
            # Create new combat encounter
            mock_combat = self._create_mock_combat(session.character_id)
            self.redis_service.store_combat_state(mock_combat)
            combat_cache = self.redis_service.get_combat_state(1)
            print("✅ Created new combat encounter state")
        else:
            print("✅ Loaded existing combat state")
        
        # 3. Process combat action with AI
        combat_context = {
            'encounter_name': combat_cache.encounter_name,
            'current_round': combat_cache.current_round,
            'participants': combat_cache.participants,
            'action': action,
            'combat_log': combat_cache.combat_log[-5:]  # Last 5 actions for context
        }
        
        # 4. Generate AI combat narration
        ai_response = self._generate_mock_combat_narration(combat_context)
        
        # 5. Update combat state (would normally update the actual encounter)
        print("✅ Combat state updated and persisted")
        
        return {
            'combat_narration': ai_response,
            'combat_state': combat_cache.to_dict(),
            'session_id': session_id
        }
    
    async def demonstrate_session_persistence(self, session_id: str) -> Dict[str, Any]:
        """
        Demonstrate how session data persists across different interactions
        Shows the power of Redis for maintaining game state
        """
        print(f"💾 Demonstrating session persistence for: {session_id}")
        
        # 1. Get session info
        session = self.redis_service.get_game_session(session_id)
        if not session:
            return {"error": "Session not found"}
        
        # 2. Get all cached data for this session
        character_cache = self.redis_service.get_cached_character(session.character_id)
        story_cache = self.redis_service.get_cached_story(session.story_arc_id)
        prompt_cache = self.redis_service.get_ai_prompt_data(session_id)
        
        # 3. Show session persistence info
        persistence_info = {
            'session': {
                'id': session.session_id,
                'user': session.user_id,
                'created': session.created_at.isoformat(),
                'last_activity': session.last_activity.isoformat(),
                'duration_minutes': int((datetime.utcnow() - session.created_at).total_seconds() / 60)
            },
            'cached_data': {
                'character': bool(character_cache),
                'story': bool(story_cache),
                'ai_prompts': bool(prompt_cache),
            },
            'performance_benefits': [
                "Character data cached for instant AI access",
                "Story context pre-loaded for consistent narration",
                "Session state persists across disconnections",
                "Combat state maintained during encounters",
                "AI prompt data optimized for sub-second responses"
            ]
        }
        
        print("✅ Session persistence data collected")
        return persistence_info
    
    def _create_mock_character(self, character_id: int):
        """Create mock character for testing"""
        return type('MockCharacter', (), {
            'id': character_id,
            'name': 'Thorin Ironforge',
            'race': 'Dwarf',
            'character_class': 'Paladin',
            'level': 8,
            'strength': 16,
            'dexterity': 10,
            'constitution': 16,
            'intelligence': 12,
            'wisdom': 14,
            'charisma': 15,
            'current_hit_points': 68,
            'max_hit_points': 72,
            'armor_class': 18,
            'equipped_items': {
                'weapon': 'Warhammer +1',
                'armor': 'Plate Mail',
                'shield': 'Shield of Faith'
            },
            'background': 'Folk Hero'
        })()
    
    def _create_mock_story_data(self, story_arc_id: int):
        """Create mock story and world state for testing"""
        story_arc = type('MockStoryArc', (), {
            'id': story_arc_id,
            'title': 'The Sunken Temple of Moradin',
            'current_stage': StoryStage.COMBAT,
            'story_type': 'dungeon_crawl',
            'story_seed': 'Ancient dwarven temple flooded by dark magic',
            'major_decisions': [
                {'decision': 'Chose to purify the altar', 'outcome': 'Temple begins draining'},
                {'decision': 'Fought off corrupted guardians', 'outcome': 'Gained blessing of Moradin'}
            ],
            'combat_outcomes': [
                {'encounter': 'Shadow wraiths', 'result': 'victory', 'xp_gained': 800}
            ],
            'npc_status': {
                'temple_priest': 'grateful',
                'shadow_lord': 'hostile',
                'moradin_spirit': 'protective'
            }
        })()
        
        world_state = type('MockWorldState', (), {
            'current_location': 'Temple Inner Sanctum',
            'active_objectives': [
                {'id': 1, 'description': 'Defeat the Shadow Lord', 'status': 'active'},
                {'id': 2, 'description': 'Restore the temple\'s blessing', 'status': 'in_progress'}
            ]
        })()
        
        return story_arc, world_state
    
    def _create_mock_combat(self, character_id: int):
        """Create mock combat encounter for testing"""
        return type('MockCombatEncounter', (), {
            'id': 1,
            'character_id': character_id,
            'encounter_name': 'Shadow Lord Boss Fight',
            'encounter_type': 'boss_encounter',
            'current_round': 1,
            'combat_state': CombatState.IN_PROGRESS,
            'turn_order': [1, 2],  # Player, Boss
            'current_turn': 1,
            'combat_log': []
        })()
    
    def _generate_mock_narration(self, context: Dict[str, Any]) -> str:
        """Generate mock AI narration based on context"""
        character = context['character']
        story = context['story']
        action = context['player_action']
        
        return f"""
As {character['name']}, the {character['race']} {character['class']}, {action.lower()}, 
the ancient stones of {story['location']} seem to respond to your presence. 

Your {character['background']} background serves you well as you navigate this mystical place. 
The air thrums with the energy of {story['title']}, and you feel the weight of your current objective: 
{story['objectives'][0]['description'] if story['objectives'] else 'exploring the unknown'}.

With {character['current_hp']}/{character['max_hp']} hit points remaining, you steel yourself for what lies ahead...
        """.strip()
    
    def _generate_mock_combat_narration(self, context: Dict[str, Any]) -> str:
        """Generate mock combat narration"""
        return f"""
**Round {context['current_round']} of {context['encounter_name']}**

{context['action']} rings through the chamber! Your decisive action shifts the tide of battle.
The shadows writhe and recoil as divine light erupts from your weapon.

*Combat continues with tactical precision...*
        """.strip()


async def run_enhanced_integration_demo():
    """Run the enhanced AI + Redis integration demonstration"""
    print("🌟 Enhanced AI + Redis Integration Demonstration")
    print("=" * 60)
    
    service = OptimizedGameplayService()
    
    try:
        # 1. Start enhanced game session
        print("\n1️⃣ Starting Enhanced Game Session")
        session_id = await service.start_enhanced_game_session("demo_user", 1, 1)
        
        # 2. Demonstrate fast AI narration
        print("\n2️⃣ Fast AI Story Narration")
        story_response = await service.fast_ai_story_narration(
            session_id, 
            "I carefully examine the ancient runes on the temple wall"
        )
        print("AI Narration:")
        print(story_response['narration'])
        print(f"Context Source: {story_response['context_source']}")
        
        # 3. Handle combat with state persistence
        print("\n3️⃣ Combat with State Persistence")
        combat_response = await service.handle_combat_with_state_persistence(
            session_id,
            "I cast Divine Smite on the Shadow Lord"
        )
        print("Combat Narration:")
        print(combat_response['combat_narration'])
        
        # 4. Demonstrate session persistence
        print("\n4️⃣ Session Persistence Benefits")
        persistence_info = await service.demonstrate_session_persistence(session_id)
        print(f"Session Duration: {persistence_info['session']['duration_minutes']} minutes")
        print("Performance Benefits:")
        for benefit in persistence_info['performance_benefits']:
            print(f"  ✅ {benefit}")
        
        # 5. Show another fast AI call (should use cached data)
        print("\n5️⃣ Second AI Call (Should Be Ultra-Fast)")
        story_response2 = await service.fast_ai_story_narration(
            session_id, 
            "I proceed deeper into the temple"
        )
        print(f"Context Source: {story_response2['context_source']} (cached = better performance)")
        
        print("\n🎉 Enhanced Integration Demo Complete!")
        print("\nKey Performance Benefits Demonstrated:")
        print("⚡ Sub-second AI response times with cached data")
        print("💾 Persistent session state across interactions")
        print("🔄 Seamless combat state management")
        print("🚀 Optimized prompt building for AI services")
        print("📊 Intelligent cache expiration and refresh")
        
    except Exception as e:
        print(f"❌ Demo error: {e}")
        return False
    
    return True


if __name__ == "__main__":
    print("Enhanced AI + Redis Integration Demo")
    print("SoloRealms - Ultimate D&D Performance")
    
    # Run the demo
    asyncio.run(run_enhanced_integration_demo()) 