"""
Test script for Redis State Management Integration
Verifies that Redis services, caching, and session management are working correctly.
"""

import os
import sys
import asyncio
import time
from datetime import datetime, timedelta

# Add the backend directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from services.redis_service import (
        redis_service, GameSession, CharacterCache, StoryCache, CombatCache, CacheExpiry
    )
    from models.character import Character
    from models.story import StoryArc, WorldState, StoryStage
    from models.combat import CombatEncounter, CombatState
    print("✅ Successfully imported Redis services and models")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


def test_redis_connection():
    """Test basic Redis connection and health check"""
    print("\n🔍 Testing Redis Connection...")
    
    try:
        health = redis_service.health_check()
        
        if health.get('healthy'):
            print(f"✅ Redis is healthy!")
            print(f"   Version: {health.get('redis_version', 'unknown')}")
            print(f"   Memory used: {health.get('used_memory_human', 'unknown')}")
            print(f"   Connected clients: {health.get('connected_clients', 0)}")
            return True
        else:
            print(f"❌ Redis health check failed: {health.get('error', 'Unknown error')}")
            return False
    
    except Exception as e:
        print(f"❌ Redis connection test failed: {e}")
        return False


def test_session_management():
    """Test game session creation, retrieval, and management"""
    print("\n🎮 Testing Session Management...")
    
    try:
        # Create a mock session
        user_id = "test_user_123"
        character_id = 1
        story_arc_id = 1
        
        print(f"Creating session for user {user_id}...")
        session = redis_service.create_game_session(user_id, character_id, story_arc_id)
        
        print(f"✅ Session created: {session.session_id}")
        print(f"   User: {session.user_id}")
        print(f"   Character: {session.character_id}")
        print(f"   Story Arc: {session.story_arc_id}")
        print(f"   Created: {session.created_at}")
        
        # Test session retrieval
        retrieved_session = redis_service.get_game_session(session.session_id)
        if retrieved_session and retrieved_session.session_id == session.session_id:
            print("✅ Session retrieval successful")
        else:
            print("❌ Session retrieval failed")
            return False
        
        # Test session activity update
        time.sleep(1)  # Wait a moment
        if redis_service.update_session_activity(session.session_id):
            print("✅ Session activity update successful")
        else:
            print("❌ Session activity update failed")
            return False
        
        # Test user session listing
        user_sessions = redis_service.get_user_sessions(user_id)
        if user_sessions and len(user_sessions) >= 1:
            print(f"✅ User session listing successful ({len(user_sessions)} sessions)")
        else:
            print("❌ User session listing failed")
            return False
        
        # Test session ending
        if redis_service.end_game_session(session.session_id):
            print("✅ Session ending successful")
        else:
            print("❌ Session ending failed")
            return False
        
        return True
    
    except Exception as e:
        print(f"❌ Session management test failed: {e}")
        return False


def test_character_caching():
    """Test character data caching and retrieval"""
    print("\n👤 Testing Character Caching...")
    
    try:
        # Create a mock character (normally would come from database)
        mock_character = type('MockCharacter', (), {
            'id': 1,
            'name': 'Test Hero',
            'race': 'Human',
            'character_class': 'Fighter',
            'level': 5,
            'strength': 16,
            'dexterity': 14,
            'constitution': 15,
            'intelligence': 12,
            'wisdom': 13,
            'charisma': 10,
            'current_hit_points': 45,
            'max_hit_points': 50,
            'armor_class': 16,
            'equipped_items': {'weapon': 'Longsword', 'armor': 'Chain Mail'},
            'background': 'Soldier'
        })()
        
        print(f"Caching character: {mock_character.name}")
        
        # Test caching
        if redis_service.cache_character(mock_character, CacheExpiry.SHORT):
            print("✅ Character caching successful")
        else:
            print("❌ Character caching failed")
            return False
        
        # Test retrieval
        cached_character = redis_service.get_cached_character(mock_character.id)
        if cached_character and cached_character.name == mock_character.name:
            print("✅ Character retrieval successful")
            print(f"   Name: {cached_character.name}")
            print(f"   Class: {cached_character.character_class}")
            print(f"   Level: {cached_character.level}")
            print(f"   HP: {cached_character.current_hp}/{cached_character.max_hp}")
            print(f"   AC: {cached_character.armor_class}")
        else:
            print("❌ Character retrieval failed")
            return False
        
        return True
    
    except Exception as e:
        print(f"❌ Character caching test failed: {e}")
        return False


def test_story_caching():
    """Test story arc and world state caching"""
    print("\n📖 Testing Story Caching...")
    
    try:
        # Create mock story arc
        mock_story_arc = type('MockStoryArc', (), {
            'id': 1,
            'title': 'The Dragon\'s Lair',
            'current_stage': StoryStage.EXPLORATION,
            'story_type': 'dungeon_crawl',
            'story_seed': 'Ancient dragon threatens the kingdom',
            'major_decisions': [
                {'decision': 'Chose to enter the cave', 'outcome': 'Found hidden passage'}
            ],
            'combat_outcomes': [
                {'encounter': 'Goblin patrol', 'result': 'victory', 'xp_gained': 200}
            ],
            'npc_status': {
                'village_elder': 'grateful',
                'dragon': 'hostile'
            }
        })()
        
        # Create mock world state
        mock_world_state = type('MockWorldState', (), {
            'current_location': 'Dragon\'s Cave Entrance',
            'active_objectives': [
                {'id': 1, 'description': 'Defeat the ancient dragon', 'status': 'active'}
            ]
        })()
        
        print(f"Caching story: {mock_story_arc.title}")
        
        # Test caching
        if redis_service.cache_story(mock_story_arc, mock_world_state, CacheExpiry.SHORT):
            print("✅ Story caching successful")
        else:
            print("❌ Story caching failed")
            return False
        
        # Test retrieval
        cached_story = redis_service.get_cached_story(mock_story_arc.id)
        if cached_story and cached_story.title == mock_story_arc.title:
            print("✅ Story retrieval successful")
            print(f"   Title: {cached_story.title}")
            print(f"   Stage: {cached_story.current_stage}")
            print(f"   Location: {cached_story.world_location}")
            print(f"   Decisions: {len(cached_story.major_decisions)}")
            print(f"   Objectives: {len(cached_story.objectives)}")
        else:
            print("❌ Story retrieval failed")
            return False
        
        return True
    
    except Exception as e:
        print(f"❌ Story caching test failed: {e}")
        return False


def test_combat_state_management():
    """Test combat encounter state storage and retrieval"""
    print("\n⚔️ Testing Combat State Management...")
    
    try:
        # Create mock combat encounter
        mock_combat = type('MockCombatEncounter', (), {
            'id': 1,
            'character_id': 1,
            'encounter_name': 'Goblin Ambush',
            'encounter_type': 'random_encounter',
            'current_round': 3,
            'combat_state': CombatState.IN_PROGRESS,
            'turn_order': [1, 2, 3],
            'current_turn': 1,
            'combat_log': [
                {'round': 1, 'action': 'Fighter attacks goblin', 'result': 'hit for 8 damage'},
                {'round': 2, 'action': 'Goblin attacks fighter', 'result': 'miss'}
            ]
        })()
        
        print(f"Storing combat state: {mock_combat.encounter_name}")
        
        # Test storing combat state
        if redis_service.store_combat_state(mock_combat):
            print("✅ Combat state storage successful")
        else:
            print("❌ Combat state storage failed")
            return False
        
        # Test retrieval
        cached_combat = redis_service.get_combat_state(mock_combat.id)
        if cached_combat and cached_combat.encounter_name == mock_combat.encounter_name:
            print("✅ Combat state retrieval successful")
            print(f"   Encounter: {cached_combat.encounter_name}")
            print(f"   Round: {cached_combat.current_round}")
            print(f"   State: {cached_combat.combat_state}")
            print(f"   Log entries: {len(cached_combat.combat_log)}")
        else:
            print("❌ Combat state retrieval failed")
            return False
        
        # Test clearing combat state
        if redis_service.clear_combat_state(mock_combat.id):
            print("✅ Combat state clearing successful")
        else:
            print("❌ Combat state clearing failed")
            return False
        
        return True
    
    except Exception as e:
        print(f"❌ Combat state management test failed: {e}")
        return False


def test_ai_prompt_caching():
    """Test AI prompt data caching for fast prompt building"""
    print("\n🤖 Testing AI Prompt Caching...")
    
    try:
        session_id = "test_session_ai_123"
        
        # Create mock cached data
        character_cache = CharacterCache(
            character_id=1,
            name="Test Wizard",
            race="Elf",
            character_class="Wizard",
            level=3,
            stats={'strength': 10, 'dexterity': 14, 'constitution': 12, 'intelligence': 16, 'wisdom': 13, 'charisma': 11},
            current_hp=18,
            max_hp=20,
            armor_class=12,
            equipped_items={'weapon': 'Staff', 'armor': 'Robes'},
            background='Scholar',
            cached_at=datetime.utcnow()
        )
        
        story_cache = StoryCache(
            story_arc_id=1,
            title="The Mysterious Tower",
            current_stage="exploration",
            story_type="mystery",
            story_seed="Strange lights from abandoned tower",
            major_decisions=[],
            combat_outcomes=[],
            npc_status={},
            world_location="Tower Base",
            objectives=[{'id': 1, 'description': 'Investigate the tower'}],
            cached_at=datetime.utcnow()
        )
        
        print(f"Caching AI prompt data for session: {session_id}")
        
        # Test caching AI prompt data
        if redis_service.cache_ai_prompt_data(session_id, character_cache, story_cache):
            print("✅ AI prompt data caching successful")
        else:
            print("❌ AI prompt data caching failed")
            return False
        
        # Test retrieval
        cached_prompt_data = redis_service.get_ai_prompt_data(session_id)
        if cached_prompt_data and 'character' in cached_prompt_data and 'story' in cached_prompt_data:
            print("✅ AI prompt data retrieval successful")
            print(f"   Character: {cached_prompt_data['character']['name']}")
            print(f"   Story: {cached_prompt_data['story']['title']}")
            print(f"   Cache timestamp: {cached_prompt_data['cached_at']}")
        else:
            print("❌ AI prompt data retrieval failed")
            return False
        
        return True
    
    except Exception as e:
        print(f"❌ AI prompt caching test failed: {e}")
        return False


def test_cleanup_operations():
    """Test cache cleanup and maintenance operations"""
    print("\n🧹 Testing Cleanup Operations...")
    
    try:
        # Test cleanup expired sessions (should be safe even if no expired sessions)
        cleaned_count = redis_service.cleanup_expired_sessions()
        print(f"✅ Cleanup operation completed ({cleaned_count} sessions cleaned)")
        
        # Note: We won't test clear_all_cache() as it's destructive
        print("ℹ️  Skipping clear_all_cache() test (destructive operation)")
        
        return True
    
    except Exception as e:
        print(f"❌ Cleanup operations test failed: {e}")
        return False


def run_all_tests():
    """Run all Redis integration tests"""
    print("🚀 Starting Redis State Management Integration Tests")
    print("=" * 60)
    
    tests = [
        ("Redis Connection", test_redis_connection),
        ("Session Management", test_session_management),
        ("Character Caching", test_character_caching),
        ("Story Caching", test_story_caching),
        ("Combat State Management", test_combat_state_management),
        ("AI Prompt Caching", test_ai_prompt_caching),
        ("Cleanup Operations", test_cleanup_operations),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                failed += 1
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            failed += 1
            print(f"❌ {test_name}: ERROR - {e}")
    
    print("\n" + "=" * 60)
    print("🏁 Test Results:")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total:  {passed + failed}")
    
    if failed == 0:
        print("\n🎉 All Redis integration tests passed!")
        print("Redis state management is ready for production!")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please check Redis configuration.")
        print("Make sure Redis server is running on redis://localhost:6379/0")
    
    return failed == 0


if __name__ == "__main__":
    print("Redis State Management Integration Test Suite")
    print("Testing SoloRealms Redis services...")
    
    success = run_all_tests()
    sys.exit(0 if success else 1) 