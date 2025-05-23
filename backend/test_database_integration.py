"""
Database Integration Tests
Tests the complete database schema with all models and relationships
"""
import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base
from models.character import Character
from models.story import StoryArc, WorldState, StoryStage
from models.combat import EnemyTemplate, CombatEncounter, CombatParticipant, CreatureType, CombatState
from datetime import datetime

# Test database URL
TEST_DATABASE_URL = "sqlite:///./test_solorelms.db"

@pytest.fixture(scope="function")
def db_session():
    """Create a test database session"""
    engine = create_engine(TEST_DATABASE_URL, echo=False)
    Base.metadata.create_all(engine)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    yield session
    
    session.close()
    # Clean up test database
    if os.path.exists("test_solorelms.db"):
        os.remove("test_solorelms.db")

def test_character_creation_and_crud(db_session):
    """Test character creation and basic CRUD operations"""
    # Create a character
    character = Character(
        user_id="test_user_123",
        name="Thorin Ironforge",
        race="Dwarf",
        character_class="Fighter",
        background="Soldier",
        strength=16,
        dexterity=12,
        constitution=15,
        intelligence=10,
        wisdom=13,
        charisma=8,
        level=1,
        experience_points=0,
        max_hit_points=12,
        current_hit_points=12,
        armor_class=16
    )
    
    db_session.add(character)
    db_session.commit()
    
    # Test retrieval
    retrieved = db_session.query(Character).filter_by(name="Thorin Ironforge").first()
    assert retrieved is not None
    assert retrieved.user_id == "test_user_123"
    assert retrieved.strength_modifier == 3  # (16-10)//2
    assert retrieved.proficiency_bonus == 2  # Level 1
    
    # Test character methods
    retrieved.take_damage(5)
    assert retrieved.current_hit_points == 7
    
    retrieved.heal(3)
    assert retrieved.current_hit_points == 10
    
    # Test inventory
    retrieved.add_item({"name": "Longsword", "type": "weapon", "damage": "1d8"})
    assert len(retrieved.inventory) == 1
    
    # Test equipment
    equipped = retrieved.equip_item("Longsword", "main_hand")
    assert equipped is True
    assert retrieved.get_equipped_item("main_hand")["name"] == "Longsword"

def test_story_arc_progression(db_session):
    """Test story arc creation and progression"""
    # Create character first
    character = Character(
        user_id="test_user_456",
        name="Elara Moonwhisper",
        race="Elf",
        character_class="Wizard",
        strength=8,
        dexterity=14,
        constitution=12,
        intelligence=16,
        wisdom=13,
        charisma=11
    )
    db_session.add(character)
    db_session.commit()
    
    # Create story arc
    story_arc = StoryArc(
        character_id=character.id,
        title="The Goblin Threat",
        story_type="short_form",
        current_stage=StoryStage.INTRO,
        story_seed="A peaceful village is threatened by goblin raiders"
    )
    db_session.add(story_arc)
    db_session.commit()
    
    # Test stage progression
    assert story_arc.can_advance_stage() is True
    story_arc.advance_stage()
    assert story_arc.current_stage == StoryStage.INCITING_INCIDENT
    assert StoryStage.INTRO.value in story_arc.stages_completed
    
    # Test decision tracking
    story_arc.add_decision({
        "decision": "help_villager",
        "description": "Chose to help the injured villager",
        "consequences": ["villager_ally"]
    })
    assert len(story_arc.major_decisions) == 1
    assert story_arc.major_decisions[0]["decision"] == "help_villager"
    
    # Test NPC status
    story_arc.update_npc_status("villager_tom", {
        "status": "ally",
        "health": "injured",
        "disposition": "grateful"
    })
    assert story_arc.npc_status["villager_tom"]["status"] == "ally"

def test_world_state_tracking(db_session):
    """Test world state and exploration tracking"""
    # Create character and story arc
    character = Character(
        user_id="test_user_789",
        name="Gareth Stormwind",
        race="Human",
        character_class="Paladin"
    )
    db_session.add(character)
    db_session.commit()
    
    story_arc = StoryArc(
        character_id=character.id,
        title="The Lost Temple"
    )
    db_session.add(story_arc)
    db_session.commit()
    
    # Create world state
    world_state = WorldState(
        story_arc_id=story_arc.id,
        current_location="village_square"
    )
    db_session.add(world_state)
    db_session.commit()
    
    # Test location tracking
    world_state.visit_location({
        "name": "ancient_forest",
        "description": "A dark forest with twisted trees",
        "notable_features": ["mysterious_shrine", "goblin_tracks"]
    })
    assert len(world_state.explored_areas) == 1
    assert world_state.explored_areas[0]["name"] == "ancient_forest"
    
    # Test objective management
    world_state.add_objective({
        "title": "Find the Lost Temple",
        "description": "Locate the ancient temple in the forest",
        "priority": "main"
    })
    assert len(world_state.active_objectives) == 1
    
    objective_id = world_state.active_objectives[0]["id"]
    world_state.complete_objective(objective_id)
    assert len(world_state.active_objectives) == 0
    assert len(world_state.completed_objectives) == 1

def test_enemy_template_and_combat(db_session):
    """Test enemy templates and combat system"""
    # Create enemy template
    goblin_template = EnemyTemplate(
        name="Goblin Warrior",
        creature_type=CreatureType.HUMANOID,
        size="Small",
        challenge_rating=0.25,
        alignment="Neutral Evil",
        strength=8,
        dexterity=14,
        constitution=10,
        intelligence=10,
        wisdom=8,
        charisma=8,
        hit_points=7,
        armor_class=15,
        speed="30 ft.",
        proficiency_bonus=2,
        xp_value=50
    )
    
    # Add attacks
    goblin_template.attacks = [{
        "name": "Scimitar",
        "type": "melee_weapon",
        "attack_bonus": 4,
        "damage": "1d6+2",
        "damage_type": "slashing"
    }]
    
    db_session.add(goblin_template)
    db_session.commit()
    
    # Test ability calculations
    assert goblin_template.dexterity_modifier == 2
    assert goblin_template.strength_modifier == -1
    
    # Create character for combat
    character = Character(
        user_id="test_user_combat",
        name="Combat Tester",
        race="Human",
        character_class="Fighter"
    )
    db_session.add(character)
    db_session.commit()
    
    # Create story arc
    story_arc = StoryArc(character_id=character.id)
    db_session.add(story_arc)
    db_session.commit()
    
    # Create combat encounter
    encounter = CombatEncounter(
        story_arc_id=story_arc.id,
        character_id=character.id,
        encounter_name="Goblin Ambush",
        encounter_type="random",
        combat_state=CombatState.NOT_STARTED
    )
    db_session.add(encounter)
    db_session.commit()
    
    # Create combat participants
    player_participant = CombatParticipant(
        combat_encounter_id=encounter.id,
        participant_type="character",
        character_id=character.id,
        name=character.name,
        max_hit_points=character.max_hit_points,
        current_hit_points=character.current_hit_points,
        armor_class=character.armor_class,
        initiative=15
    )
    
    enemy_participant = CombatParticipant(
        combat_encounter_id=encounter.id,
        participant_type="enemy",
        enemy_template_id=goblin_template.id,
        name="Goblin Warrior #1",
        max_hit_points=goblin_template.hit_points,
        current_hit_points=goblin_template.hit_points,
        armor_class=goblin_template.armor_class,
        initiative=12
    )
    
    db_session.add_all([player_participant, enemy_participant])
    db_session.commit()
    
    # Test combat mechanics
    encounter.start_combat()
    assert encounter.combat_state == CombatState.INITIATIVE
    assert encounter.current_round == 1
    
    # Test damage
    enemy_participant.take_damage(4)
    assert enemy_participant.current_hit_points == 3
    assert enemy_participant.is_active is True
    
    enemy_participant.take_damage(3)
    assert enemy_participant.current_hit_points == 0
    assert enemy_participant.is_active is False

def test_relationships_and_foreign_keys(db_session):
    """Test that all relationships work correctly"""
    # Create character
    character = Character(
        user_id="test_relationships",
        name="Relationship Tester",
        race="Human",
        character_class="Rogue"
    )
    db_session.add(character)
    db_session.commit()
    
    # Create story arc
    story_arc = StoryArc(
        character_id=character.id,
        title="Relationship Test Story"
    )
    db_session.add(story_arc)
    db_session.commit()
    
    # Create world state
    world_state = WorldState(
        story_arc_id=story_arc.id,
        current_location="test_location"
    )
    db_session.add(world_state)
    db_session.commit()
    
    # Create combat encounter
    encounter = CombatEncounter(
        story_arc_id=story_arc.id,
        character_id=character.id,
        encounter_name="Test Combat"
    )
    db_session.add(encounter)
    db_session.commit()
    
    # Test relationships
    assert character.story_arcs[0].id == story_arc.id
    assert story_arc.character.id == character.id
    assert story_arc.world_states[0].id == world_state.id
    assert story_arc.combat_encounters[0].id == encounter.id
    assert world_state.story_arc.id == story_arc.id

def test_complex_queries(db_session):
    """Test complex database queries for game mechanics"""
    # Create test data
    character = Character(
        user_id="test_queries",
        name="Query Tester",
        race="Elf",
        character_class="Ranger",
        level=3,
        experience_points=900
    )
    db_session.add(character)
    db_session.commit()
    
    # Create multiple story arcs
    for i in range(3):
        story_arc = StoryArc(
            character_id=character.id,
            title=f"Adventure {i+1}",
            story_completed=(i < 2)  # First two are completed
        )
        db_session.add(story_arc)
    db_session.commit()
    
    # Query active story arcs
    active_stories = db_session.query(StoryArc).filter(
        StoryArc.character_id == character.id,
        StoryArc.story_completed == False
    ).all()
    assert len(active_stories) == 1
    assert active_stories[0].title == "Adventure 3"
    
    # Query completed stories
    completed_stories = db_session.query(StoryArc).filter(
        StoryArc.character_id == character.id,
        StoryArc.story_completed == True
    ).count()
    assert completed_stories == 2

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 