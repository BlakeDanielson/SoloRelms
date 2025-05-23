import pytest
import sys
import os
from datetime import datetime

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base
from models.character import Character
from models.story import StoryArc, StoryStage
from models.combat import EnemyTemplate, CombatEncounter, CombatParticipant, CreatureType, CombatState
from services.combat import CombatService
from schemas.combat import (
    EnemyTemplateCreate, CombatEncounterCreate, CombatParticipantCreate,
    DamageRequest, HealingRequest, AddConditionRequest, ConditionData
)

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_combat.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def setup_test_db():
    """Create test database and tables"""
    Base.metadata.create_all(bind=engine)

def teardown_test_db():
    """Clean up test database"""
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("./test_combat.db"):
        os.remove("./test_combat.db")

def create_test_character(db):
    """Create a test character"""
    character = Character(
        user_id="test_user_123",
        name="Test Hero",
        race="Human",
        character_class="Fighter",
        strength=16,
        dexterity=14,
        constitution=15,
        intelligence=10,
        wisdom=12,
        charisma=8,
        level=3,
        max_hit_points=28,
        current_hit_points=28,
        armor_class=16
    )
    db.add(character)
    db.commit()
    db.refresh(character)
    return character

def create_test_story_arc(db, character_id):
    """Create a test story arc"""
    story_arc = StoryArc(
        character_id=character_id,
        title="Test Adventure",
        current_stage=StoryStage.FIRST_COMBAT
    )
    db.add(story_arc)
    db.commit()
    db.refresh(story_arc)
    return story_arc

def test_enemy_template_creation():
    """Test creating enemy templates"""
    setup_test_db()
    db = TestingSessionLocal()
    combat_service = CombatService(db)
    
    try:
        # Create a goblin template
        goblin_data = EnemyTemplateCreate(
            name="Goblin",
            creature_type=CreatureType.HUMANOID,
            challenge_rating=0.25,
            hit_points=7,
            armor_class=15,
            speed=30,
            strength=8,
            dexterity=14,
            constitution=10,
            intelligence=10,
            wisdom=8,
            charisma=8,
            abilities=[
                {
                    "name": "Scimitar",
                    "type": "melee_attack",
                    "attack_bonus": 4,
                    "damage": "1d6+2",
                    "damage_type": "slashing"
                },
                {
                    "name": "Shortbow",
                    "type": "ranged_attack",
                    "attack_bonus": 4,
                    "damage": "1d6+2",
                    "damage_type": "piercing",
                    "range": "80/320"
                }
            ],
            xp_value=50,
            loot_table={
                "guaranteed": [{"name": "Scimitar", "type": "weapon"}],
                "possible": [
                    {"name": "Gold Pieces", "amount": "1d6", "chance": 0.5},
                    {"name": "Leather Armor", "type": "armor", "chance": 0.2}
                ]
            }
        )
        
        goblin = combat_service.create_enemy_template(goblin_data)
        
        assert goblin.name == "Goblin"
        assert goblin.creature_type == CreatureType.HUMANOID
        assert goblin.challenge_rating == 0.25
        assert goblin.hit_points == 7
        assert goblin.dexterity_modifier == 2  # (14-10)//2
        assert len(goblin.abilities) == 2
        assert goblin.xp_value == 50
        
        print("✅ Enemy template creation test passed")
        
    finally:
        db.close()
        teardown_test_db()

def test_combat_encounter_creation():
    """Test creating combat encounters"""
    setup_test_db()
    db = TestingSessionLocal()
    combat_service = CombatService(db)
    
    try:
        # Create test character and story arc
        character = create_test_character(db)
        story_arc = create_test_story_arc(db, character.id)
        
        # Create combat encounter
        encounter_data = CombatEncounterCreate(
            character_id=character.id,
            story_arc_id=story_arc.id,
            encounter_name="Goblin Ambush",
            encounter_type="ambush",
            difficulty="easy"
        )
        
        encounter = combat_service.create_combat_encounter(encounter_data)
        
        assert encounter.encounter_name == "Goblin Ambush"
        assert encounter.character_id == character.id
        assert encounter.story_arc_id == story_arc.id
        assert encounter.combat_state == CombatState.NOT_STARTED
        assert encounter.current_round == 0
        
        print("✅ Combat encounter creation test passed")
        
    finally:
        db.close()
        teardown_test_db()

def test_combat_participants():
    """Test creating and managing combat participants"""
    setup_test_db()
    db = TestingSessionLocal()
    combat_service = CombatService(db)
    
    try:
        # Create test data
        character = create_test_character(db)
        story_arc = create_test_story_arc(db, character.id)
        
        # Create enemy template
        goblin_data = EnemyTemplateCreate(
            name="Goblin",
            creature_type=CreatureType.HUMANOID,
            challenge_rating=0.25,
            hit_points=7,
            armor_class=15,
            speed=30,
            strength=8,
            dexterity=14,
            constitution=10,
            intelligence=10,
            wisdom=8,
            charisma=8,
            xp_value=50
        )
        goblin_template = combat_service.create_enemy_template(goblin_data)
        
        # Create combat encounter
        encounter_data = CombatEncounterCreate(
            character_id=character.id,
            story_arc_id=story_arc.id,
            encounter_name="Goblin Fight",
            encounter_type="standard"
        )
        encounter = combat_service.create_combat_encounter(encounter_data)
        
        # Create character participant
        char_participant = combat_service.create_character_participant(
            encounter.id, character.id, initiative=15
        )
        
        assert char_participant.participant_type == "character"
        assert char_participant.character_id == character.id
        assert char_participant.name == character.name
        assert char_participant.max_hit_points == character.max_hit_points
        assert char_participant.initiative == 15
        
        # Create enemy participant
        enemy_participant = combat_service.create_enemy_participant(
            encounter.id, goblin_template.id, name_suffix="1", initiative=12
        )
        
        assert enemy_participant.participant_type == "enemy"
        assert enemy_participant.enemy_template_id == goblin_template.id
        assert enemy_participant.name == "Goblin 1"
        assert enemy_participant.max_hit_points == goblin_template.hit_points
        assert enemy_participant.initiative == 12
        
        print("✅ Combat participants test passed")
        
    finally:
        db.close()
        teardown_test_db()

def test_combat_actions():
    """Test combat actions like damage, healing, and conditions"""
    setup_test_db()
    db = TestingSessionLocal()
    combat_service = CombatService(db)
    
    try:
        # Create test setup
        character = create_test_character(db)
        story_arc = create_test_story_arc(db, character.id)
        
        goblin_data = EnemyTemplateCreate(
            name="Goblin",
            creature_type=CreatureType.HUMANOID,
            challenge_rating=0.25,
            hit_points=7,
            armor_class=15,
            speed=30,
            strength=8,
            dexterity=14,
            constitution=10,
            intelligence=10,
            wisdom=8,
            charisma=8,
            xp_value=50
        )
        goblin_template = combat_service.create_enemy_template(goblin_data)
        
        encounter_data = CombatEncounterCreate(
            character_id=character.id,
            story_arc_id=story_arc.id,
            encounter_name="Combat Test"
        )
        encounter = combat_service.create_combat_encounter(encounter_data)
        
        char_participant = combat_service.create_character_participant(encounter.id, character.id)
        enemy_participant = combat_service.create_enemy_participant(encounter.id, goblin_template.id)
        
        # Test damage
        damage_request = DamageRequest(
            participant_id=enemy_participant.id,
            damage=5
        )
        damage_response = combat_service.apply_damage(damage_request)
        
        assert damage_response.success == True
        assert damage_response.damage_dealt == 5
        assert "takes 5 damage" in damage_response.description
        
        # Refresh participant to check HP
        db.refresh(enemy_participant)
        assert enemy_participant.current_hit_points == 2  # 7 - 5
        
        # Test healing
        healing_request = HealingRequest(
            participant_id=enemy_participant.id,
            amount=3
        )
        healing_response = combat_service.apply_healing(healing_request)
        
        assert healing_response.success == True
        assert healing_response.healing_done == 3
        
        db.refresh(enemy_participant)
        assert enemy_participant.current_hit_points == 5  # 2 + 3
        
        # Test adding condition
        condition_request = AddConditionRequest(
            participant_id=char_participant.id,
            condition=ConditionData(
                condition="poisoned",
                duration=3,
                source="goblin_attack"
            )
        )
        condition_response = combat_service.add_condition(condition_request)
        
        assert condition_response.success == True
        assert "poisoned" in condition_response.conditions_applied
        
        print("✅ Combat actions test passed")
        
    finally:
        db.close()
        teardown_test_db()

def test_initiative_and_turn_management():
    """Test initiative rolling and turn management"""
    setup_test_db()
    db = TestingSessionLocal()
    combat_service = CombatService(db)
    
    try:
        # Create test setup
        character = create_test_character(db)
        story_arc = create_test_story_arc(db, character.id)
        
        goblin_data = EnemyTemplateCreate(
            name="Goblin",
            creature_type=CreatureType.HUMANOID,
            challenge_rating=0.25,
            hit_points=7,
            armor_class=15,
            speed=30,
            strength=8,
            dexterity=14,
            constitution=10,
            intelligence=10,
            wisdom=8,
            charisma=8,
            xp_value=50
        )
        goblin_template = combat_service.create_enemy_template(goblin_data)
        
        encounter_data = CombatEncounterCreate(
            character_id=character.id,
            story_arc_id=story_arc.id,
            encounter_name="Initiative Test"
        )
        encounter = combat_service.create_combat_encounter(encounter_data)
        
        # Create participants with specific initiative
        char_participant = combat_service.create_character_participant(
            encounter.id, character.id, initiative=18
        )
        enemy_participant = combat_service.create_enemy_participant(
            encounter.id, goblin_template.id, initiative=12
        )
        
        # Roll initiative
        initiative_response = combat_service.roll_initiative(encounter.id)
        
        assert len(initiative_response.initiative_order) == 2
        assert initiative_response.combat_state == CombatState.IN_PROGRESS
        
        # Check initiative order (highest first)
        assert initiative_response.initiative_order[0].initiative == 18  # Character first
        assert initiative_response.initiative_order[1].initiative == 12  # Goblin second
        
        # Test advancing turns
        db.refresh(encounter)
        assert encounter.current_round == 1
        assert encounter.current_turn == 0
        
        # Advance to next turn
        updated_encounter = combat_service.advance_turn(encounter.id)
        assert updated_encounter.current_turn == 1
        
        # Advance to next round
        updated_encounter = combat_service.advance_turn(encounter.id)
        assert updated_encounter.current_round == 2
        assert updated_encounter.current_turn == 0
        
        print("✅ Initiative and turn management test passed")
        
    finally:
        db.close()
        teardown_test_db()

def test_combat_summary_and_rewards():
    """Test combat summary and XP/loot calculation"""
    setup_test_db()
    db = TestingSessionLocal()
    combat_service = CombatService(db)
    
    try:
        # Create test setup
        character = create_test_character(db)
        story_arc = create_test_story_arc(db, character.id)
        
        goblin_data = EnemyTemplateCreate(
            name="Goblin",
            creature_type=CreatureType.HUMANOID,
            challenge_rating=0.25,
            hit_points=7,
            armor_class=15,
            speed=30,
            strength=8,
            dexterity=14,
            constitution=10,
            intelligence=10,
            wisdom=8,
            charisma=8,
            xp_value=50,
            loot_table={
                "guaranteed": [{"name": "Scimitar", "type": "weapon"}],
                "possible": [{"name": "Gold", "amount": "1d6", "chance": 1.0}]  # 100% chance for testing
            }
        )
        goblin_template = combat_service.create_enemy_template(goblin_data)
        
        encounter_data = CombatEncounterCreate(
            character_id=character.id,
            story_arc_id=story_arc.id,
            encounter_name="Reward Test"
        )
        encounter = combat_service.create_combat_encounter(encounter_data)
        
        char_participant = combat_service.create_character_participant(encounter.id, character.id)
        enemy_participant = combat_service.create_enemy_participant(encounter.id, goblin_template.id)
        
        # Get initial summary
        summary = combat_service.get_combat_summary(encounter.id)
        assert summary.participants_active == 2
        assert summary.participants_total == 2
        assert summary.character_hp == character.max_hit_points
        
        # "Defeat" the enemy
        damage_request = DamageRequest(
            participant_id=enemy_participant.id,
            damage=10  # More than goblin's HP
        )
        combat_service.apply_damage(damage_request)
        
        # Check XP calculation
        xp_reward = combat_service.calculate_xp_reward(encounter.id)
        assert xp_reward == 50  # Goblin's XP value
        
        # Check loot generation
        loot = combat_service.generate_loot(encounter.id)
        assert len(loot) >= 1  # At least guaranteed loot
        assert any(item.get("name") == "Scimitar" for item in loot)
        
        # End combat
        ended_encounter = combat_service.end_combat_encounter(
            encounter.id, "victory", xp_reward, loot
        )
        assert ended_encounter.combat_state == CombatState.VICTORY
        assert ended_encounter.xp_awarded == 50
        
        print("✅ Combat summary and rewards test passed")
        
    finally:
        db.close()
        teardown_test_db()

if __name__ == "__main__":
    print("🧪 Running Combat System Tests...")
    
    try:
        test_enemy_template_creation()
        test_combat_encounter_creation()
        test_combat_participants()
        test_combat_actions()
        test_initiative_and_turn_management()
        test_combat_summary_and_rewards()
        
        print("\n🎉 All combat system tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up any remaining test files
        if os.path.exists("./test_combat.db"):
            os.remove("./test_combat.db") 