#!/usr/bin/env python3
"""
Test script for Redis combat state storage and retrieval
Creates sample data and tests the full combat state management pipeline
"""

import asyncio
import json
from datetime import datetime
from sqlalchemy.orm import Session
from database import get_db, engine
from models.character import Character
from models.user import User
from models.story import StoryArc, StoryStage
from models.combat import CombatEncounter, CombatParticipant, EnemyTemplate, CombatState, CreatureType
from services.redis_service import redis_service

def create_sample_data():
    """Create sample character, story, and combat data for testing"""
    db = next(get_db())
    
    try:
        # Check if test user already exists
        existing_user = db.query(User).filter(User.id == "test_user_123").first()
        if not existing_user:
            # Create a test user
            user = User(
                id="test_user_123",
                email="test@example.com",
                first_name="Test",
                last_name="User",
                username="testuser",
                is_active=True,
                email_verified=True
            )
            db.add(user)
            db.flush()
            print("   ✅ Created test user")
        else:
            user = existing_user
            print("   ♻️  Using existing test user")
        
        # Check if test character already exists
        existing_character = db.query(Character).filter(Character.user_id == user.id, Character.name == "Test Hero").first()
        if not existing_character:
            # Create a test character
            character = Character(
                user_id=user.id,
                name="Test Hero",
                race="Human",
                character_class="Fighter",
                level=3,
                strength=16,
                dexterity=14,
                constitution=15,
                intelligence=10,
                wisdom=12,
                charisma=8,
                max_hit_points=28,
                current_hit_points=28,
                armor_class=16,
                background="Soldier",
                equipped_items={
                    "weapon": "Longsword",
                    "armor": "Chain Mail",
                    "shield": "Shield"
                }
            )
            db.add(character)
            db.flush()
            print("   ✅ Created test character")
        else:
            character = existing_character
            print("   ♻️  Using existing test character")
        
        # Check if test story arc already exists
        existing_story = db.query(StoryArc).filter(StoryArc.character_id == character.id, StoryArc.title == "The Goblin Cave").first()
        if not existing_story:
            # Create a test story arc
            story_arc = StoryArc(
                character_id=character.id,
                user_id=user.id,
                title="The Goblin Cave",
                story_type="short_form",
                current_stage=StoryStage.FIRST_COMBAT,
                story_seed="A group of goblins has been raiding the local village",
                major_decisions=[],
                combat_outcomes=[],
                npc_status={}
            )
            db.add(story_arc)
            db.flush()
            print("   ✅ Created test story arc")
        else:
            story_arc = existing_story
            print("   ♻️  Using existing test story arc")
        
        # Check if test combat encounter already exists
        existing_encounter = db.query(CombatEncounter).filter(CombatEncounter.story_arc_id == story_arc.id).first()
        if not existing_encounter:
            # Create a test combat encounter
            combat_encounter = CombatEncounter(
                story_arc_id=story_arc.id,
                encounter_type="combat",
                name="Goblin Ambush",
                description="A group of goblins attacks from the bushes",
                difficulty_rating=2,
                turn_order=[],
                combat_log=[],
                status=CombatState.SETUP,
                round_number=1,
                current_turn=0
            )
            db.add(combat_encounter)
            db.flush()
            print("   ✅ Created test combat encounter")
        else:
            combat_encounter = existing_encounter
            print("   ♻️  Using existing test combat encounter")
        
        db.commit()
        
        return {
            'user': user,
            'character': character, 
            'story_arc': story_arc,
            'combat_encounter': combat_encounter
        }
        
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def test_redis_combat_storage(encounter_id: int):
    """Test Redis combat state storage and retrieval"""
    print(f"\n🧪 Testing Redis combat state storage for encounter {encounter_id}")
    
    try:
        # Test storing combat state
        db = next(get_db())
        encounter = db.query(CombatEncounter).filter(CombatEncounter.id == encounter_id).first()
        participants = db.query(CombatParticipant).filter(CombatParticipant.combat_encounter_id == encounter_id).all()
        
        print(f"📦 Storing combat state in Redis...")
        success = redis_service.store_combat_state(encounter, participants)
        print(f"   Storage result: {'✅ Success' if success else '❌ Failed'}")
        
        # Test retrieving combat state
        print(f"📥 Retrieving combat state from Redis...")
        cached_combat = redis_service.get_combat_state(encounter_id)
        
        if cached_combat:
            print(f"   ✅ Retrieved combat state:")
            print(f"      Encounter: {cached_combat.encounter_name}")
            print(f"      State: {cached_combat.combat_state}")
            print(f"      Round: {cached_combat.current_round}")
            print(f"      Participants: {len(cached_combat.participants)}")
            print(f"      Turn Order: {cached_combat.turn_order}")
            print(f"      Combat Log: {len(cached_combat.combat_log)} entries")
            
            # Display participant details
            for i, participant in enumerate(cached_combat.participants):
                print(f"      Participant {i+1}: {participant['name']} ({participant['current_hit_points']}/{participant['max_hit_points']} HP)")
                if participant.get('active_conditions'):
                    print(f"         Conditions: {participant['active_conditions']}")
        else:
            print(f"   ❌ Failed to retrieve combat state")
            
        db.close()
        return cached_combat is not None
        
    except Exception as e:
        print(f"❌ Error testing Redis combat storage: {e}")
        return False

def test_redis_health():
    """Test Redis connection and health"""
    print("🏥 Testing Redis health...")
    
    try:
        health = redis_service.health_check()
        print(f"   Status: {'✅ Healthy' if health['healthy'] else '❌ Unhealthy'}")
        if health['healthy']:
            print(f"   Connected clients: {health['connected_clients']}")
            print(f"   Memory usage: {health['used_memory_human']}")
            print(f"   Redis version: {health['redis_version']}")
        else:
            print(f"   Error: {health.get('error', 'Unknown error')}")
        return health['healthy']
    except Exception as e:
        print(f"❌ Redis health check failed: {e}")
        return False

def test_session_management(character_id: int, story_arc_id: int):
    """Test Redis session management"""
    print(f"\n🎮 Testing Redis session management...")
    
    try:
        # Create a game session
        session = redis_service.create_game_session(
            user_id="test_user_123",
            character_id=character_id,
            story_arc_id=story_arc_id
        )
        
        print(f"   ✅ Created session: {session.session_id}")
        print(f"      User: {session.user_id}")
        print(f"      Character: {session.character_id}")
        print(f"      Story Arc: {session.story_arc_id}")
        
        # Test session retrieval
        retrieved_session = redis_service.get_game_session(session.session_id)
        if retrieved_session:
            print(f"   ✅ Retrieved session successfully")
            print(f"      Active: {retrieved_session.active}")
            print(f"      Created: {retrieved_session.created_at}")
        else:
            print(f"   ❌ Failed to retrieve session")
            
        # Test session activity update
        success = redis_service.update_session_activity(session.session_id)
        print(f"   Activity update: {'✅ Success' if success else '❌ Failed'}")
        
        return session.session_id
        
    except Exception as e:
        print(f"❌ Error testing session management: {e}")
        return None

def main():
    """Main test function"""
    print("🚀 Starting Redis Combat State Integration Tests")
    print("=" * 60)
    
    # Test Redis health first
    if not test_redis_health():
        print("❌ Redis health check failed. Exiting.")
        return
    
    # Create sample data
    sample_data = create_sample_data()
    
    # Test session management
    session_id = test_session_management(
        sample_data["character"].id, 
        sample_data["story_arc"].id
    )
    
    # Test combat state storage
    combat_success = test_redis_combat_storage(sample_data["combat_encounter"].id)
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print(f"   Redis Health: ✅")
    print(f"   Session Management: {'✅' if session_id else '❌'}")
    print(f"   Combat State Storage: {'✅' if combat_success else '❌'}")
    
    if session_id and combat_success:
        print("\n🎉 All tests passed! Redis combat state integration is working perfectly!")
        print(f"\nYou can now test the API endpoints:")
        print(f"   GET  /api/redis/health")
        print(f"   GET  /api/redis/session/{session_id}")
        print(f"   GET  /api/redis/cache/combat/{sample_data['combat_encounter'].id}")
        print(f"   POST /api/redis/cache/combat (with encounter_id: {sample_data['combat_encounter'].id})")
    else:
        print("\n❌ Some tests failed. Check the logs above for details.")

if __name__ == "__main__":
    main() 