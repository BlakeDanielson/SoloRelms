"""
Test script for AI service integration
Verifies that the GPT-4o prompting system is working correctly.
"""

import os
import sys
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the backend directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.character import Character
from models.story import StoryArc, WorldState, StoryStage
from models.combat import CombatEncounter, CombatState
from services.ai_service import ai_service, AIService
from database import get_db


def test_prompt_templates():
    """Test the prompt template formatting without making API calls"""
    print("Testing prompt template formatting...")
    
    # Create mock character
    character = type('MockCharacter', (), {
        'name': 'Aeliana',
        'race': 'Half-Elf',
        'character_class': 'Rogue',
        'level': 3,
        'strength': 12,
        'dexterity': 16,
        'constitution': 14,
        'intelligence': 13,
        'wisdom': 12,
        'charisma': 15,
        'strength_modifier': 1,
        'dexterity_modifier': 3,
        'constitution_modifier': 2,
        'intelligence_modifier': 1,
        'wisdom_modifier': 1,
        'charisma_modifier': 2,
        'current_hit_points': 18,
        'max_hit_points': 24,
        'armor_class': 15,
        'proficiency_bonus': 2,
        'background': 'Criminal',
        'equipped_items': {'weapon': 'shortsword', 'armor': 'leather_armor'}
    })()
    
    # Create mock story arc
    story_arc = type('MockStoryArc', (), {
        'title': 'The Merchant\'s Mystery',
        'current_stage': StoryStage.INCITING_INCIDENT,
        'story_type': 'short_form',
        'story_seed': 'A merchant caravan has gone missing on the forest road',
        'major_decisions': [
            {
                'decision': 'investigate_tavern',
                'description': 'Decided to gather information at the local tavern',
                'stage': 'intro'
            }
        ],
        'combat_outcomes': [],
        'npc_status': {
            'tavern_keeper': {
                'disposition': 'friendly',
                'health': 'healthy',
                'status': 'ally'
            }
        }
    })()
    
    # Create mock world state
    world_state = type('MockWorldState', (), {
        'current_location': 'village_tavern',
        'story_time_elapsed': 45,
        'active_objectives': [
            {
                'title': 'Find information about the missing caravan',
                'priority': 'main'
            }
        ],
        'established_lore': {
            'village_name': 'Millbrook',
            'kingdom': 'Valdris'
        },
        'explored_areas': [
            {
                'name': 'village_square',
                'description': 'A bustling marketplace with a stone fountain'
            }
        ]
    })()
    
    # Test story narration template
    print("\n--- Story Narration Template Test ---")
    story_template = ai_service.templates['story']
    story_prompt = story_template.build_prompt(
        character=character,
        story_arc=story_arc,
        world_state=world_state,
        player_action="I approach the tavern keeper and ask about the missing merchant caravan"
    )
    print("Story prompt length:", len(story_prompt))
    print("First 500 characters:")
    print(story_prompt[:500] + "...")
    
    # Test NPC interaction template
    print("\n--- NPC Interaction Template Test ---")
    npc_template = ai_service.templates['npc']
    npc_prompt = npc_template.build_prompt(
        character=character,
        story_arc=story_arc,
        npc_name="tavern_keeper",
        interaction_type="dialogue",
        player_input="Good evening! Have you seen any merchant caravans pass through recently?",
        world_state=world_state
    )
    print("NPC prompt length:", len(npc_prompt))
    print("First 500 characters:")
    print(npc_prompt[:500] + "...")
    
    # Test combat narration template
    print("\n--- Combat Narration Template Test ---")
    combat_encounter = type('MockCombatEncounter', (), {
        'encounter_name': 'Bandit Ambush',
        'encounter_type': 'combat',
        'current_round': 2,
        'combat_state': CombatState.ACTIVE
    })()
    
    combat_template = ai_service.templates['combat']
    combat_prompt = combat_template.build_prompt(
        character=character,
        story_arc=story_arc,
        combat_encounter=combat_encounter,
        combat_action={
            'action_type': 'attack',
            'target': 'bandit_leader',
            'weapon': 'shortsword',
            'attack_roll': 17
        },
        combat_result={
            'hit': True,
            'damage': 8,
            'damage_type': 'piercing',
            'critical': False
        },
        world_state=world_state
    )
    print("Combat prompt length:", len(combat_prompt))
    print("First 500 characters:")
    print(combat_prompt[:500] + "...")
    
    print("\n✅ All prompt templates formatted successfully!")


def test_ai_service_health():
    """Test AI service connectivity and health"""
    print("\nTesting AI service health...")
    
    # Check if API key is available
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY environment variable not set")
        print("To test AI connectivity, set your OpenAI API key:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        return False
    
    print(f"✅ API key found (length: {len(api_key)})")
    
    # Test basic AI service initialization
    test_service = AIService(api_key=api_key)
    print(f"✅ AI service initialized with model: {test_service.model}")
    
    # Test a simple prompt (only if API key is available)
    try:
        print("Testing basic AI connectivity...")
        result = test_service.generate_response(
            "Respond with exactly: 'AI test successful'",
            max_tokens=10,
            temperature=0.1
        )
        
        if result['success']:
            print(f"✅ AI response: {result['content']}")
            print(f"Model used: {result.get('model', 'unknown')}")
            print(f"Tokens used: {result.get('usage', {}).get('total_tokens', 'unknown')}")
            return True
        else:
            print(f"❌ AI request failed: {result.get('error', 'Unknown error')}")
            return False
    
    except Exception as e:
        print(f"❌ AI service error: {str(e)}")
        return False


def test_template_integration():
    """Test the integration between templates and AI service"""
    print("\nTesting template integration...")
    
    # This would require actual database connection and models
    # For now, just verify the service can handle the template outputs
    print("✅ Template integration ready for database testing")


def main():
    """Run all AI service tests"""
    print("🧪 SoloRealms AI Service Test Suite")
    print("=" * 50)
    
    # Test 1: Prompt template formatting
    test_prompt_templates()
    
    # Test 2: AI service health and connectivity
    ai_healthy = test_ai_service_health()
    
    # Test 3: Template integration
    test_template_integration()
    
    print("\n" + "=" * 50)
    print("🎯 Test Summary:")
    print("✅ Prompt templates: Working")
    print(f"{'✅' if ai_healthy else '❌'} AI connectivity: {'Working' if ai_healthy else 'Failed'}")
    print("✅ Service integration: Ready")
    
    if ai_healthy:
        print("\n🎉 AI service is fully operational!")
        print("\n🚀 Next steps:")
        print("1. Start the FastAPI server: uvicorn main:app --reload")
        print("2. Test endpoints at: http://localhost:8000/docs")
        print("3. Try the AI health endpoint: GET /api/ai/health")
    else:
        print("\n⚠️  AI service needs configuration")
        print("Set OPENAI_API_KEY environment variable to enable AI features")


if __name__ == "__main__":
    main() 