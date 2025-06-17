"""
Tests for story state machine API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from main import app
from models.user import User
from models.character import Character
from models.story import StoryArc, WorldState, StoryStage
import json
from datetime import datetime

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_stories.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def client(setup_database):
    return TestClient(app)

@pytest.fixture(scope="module")
def test_user_and_character(client):
    """Create a test user and character for story testing"""
    db = TestingSessionLocal()
    
    # Create test user
    user = User(
        id="test_story_user_123",
        email="storytest@example.com",
        first_name="Story",
        last_name="Tester",
        username="storytester"
    )
    db.add(user)
    db.commit()
    
    # Create test character
    character = Character(
        user_id="test_story_user_123",
        name="Thorin Stormhammer",
        race="Dwarf",
        character_class="Fighter",
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
        armor_class=16,
        proficiencies=[],
        skill_proficiencies=["athletics", "intimidation"],
        inventory=[],
        equipped_items={},
        is_active=True,
        is_alive=True
    )
    db.add(character)
    db.commit()
    db.refresh(character)
    
    db.close()
    return {"user_id": "test_story_user_123", "character_id": character.id}

# Mock authentication for testing
def mock_get_current_user_id():
    return "test_story_user_123"

def mock_get_current_user():
    db = TestingSessionLocal()
    user = db.query(User).filter(User.id == "test_story_user_123").first()
    db.close()
    return user

# Override auth dependencies for testing
from auth import get_current_user_id, get_current_user
app.dependency_overrides[get_current_user_id] = mock_get_current_user_id
app.dependency_overrides[get_current_user] = mock_get_current_user

# Global variable to store story ID for testing
CREATED_STORY_ID = None

class TestStoryCreation:
    """Test story creation and basic operations"""
    
    def test_create_story_success(self, client, test_user_and_character):
        """Test successful story creation"""
        global CREATED_STORY_ID
        response = client.post(
            "/api/stories",
            json={
                "character_id": test_user_and_character["character_id"],
                "story_seed": "A mysterious fog rolls into the village",
                "story_type": "short_form"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["character_id"] == test_user_and_character["character_id"]
        assert data["current_stage"] == "intro"
        assert data["story_completed"] == False
        assert data["story_seed"] is not None
        assert "id" in data
        
        # Store story ID for other tests
        CREATED_STORY_ID = data["id"]
    
    def test_create_story_invalid_character(self, client):
        """Test story creation with invalid character ID"""
        response = client.post(
            "/api/stories",
            json={
                "character_id": 999,
                "story_seed": "Test story",
                "story_type": "short_form"
            }
        )
        
        assert response.status_code == 404
        assert "Character not found" in response.json()["detail"]
    
    def test_create_duplicate_active_story(self, client, test_user_and_character):
        """Test that only one active story per character is allowed"""
        response = client.post(
            "/api/stories",
            json={
                "character_id": test_user_and_character["character_id"],
                "story_seed": "Another story attempt",
                "story_type": "short_form"
            }
        )
        
        assert response.status_code == 409
        assert "already has an active story" in response.json()["detail"]

class TestStoryRetrieval:
    """Test story listing and detail retrieval"""
    
    def test_get_user_stories(self, client):
        """Test retrieving all user stories"""
        response = client.get("/api/stories")
        
        assert response.status_code == 200
        stories = response.json()
        assert len(stories) >= 1
        assert stories[0]["current_stage"] == "intro"
    
    def test_get_user_stories_active_only(self, client):
        """Test retrieving only active stories"""
        response = client.get("/api/stories?active_only=true")
        
        assert response.status_code == 200
        stories = response.json()
        assert len(stories) >= 1
        assert all(not story["story_completed"] for story in stories)
    
    def test_get_story_details(self, client):
        """Test retrieving detailed story information"""
        story_id = CREATED_STORY_ID
        response = client.get(f"/api/stories/{story_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert "major_decisions" in data
        assert "npc_status" in data
        assert "combat_outcomes" in data
        assert "final_rewards" in data
        assert data["current_stage"] == "intro"
    
    def test_get_story_details_not_found(self, client):
        """Test retrieving non-existent story"""
        response = client.get("/api/stories/999")
        
        assert response.status_code == 404
        assert "Story not found" in response.json()["detail"]

class TestStoryProgression:
    """Test story state transitions and progression"""
    
    def test_advance_story_stage_from_intro(self, client):
        """Test advancing from intro stage"""
        story_id = CREATED_STORY_ID
        response = client.post(f"/api/stories/{story_id}/advance")
        
        assert response.status_code == 200
        data = response.json()
        assert data["current_stage"] == "inciting_incident"
        assert "intro" in data["stages_completed"]
    
    def test_advance_story_stage_requirements_not_met(self, client):
        """Test advancing when requirements are not met"""
        story_id = CREATED_STORY_ID
        # Try to advance from inciting_incident without making decisions
        response = client.post(f"/api/stories/{story_id}/advance")
        
        assert response.status_code == 409
        assert "Requirements not met" in response.json()["detail"]
    
    def test_add_story_decision(self, client):
        """Test adding a major story decision"""
        story_id = CREATED_STORY_ID
        response = client.post(
            f"/api/stories/{story_id}/decisions",
            json={
                "decision": "help_villager",
                "description": "Chose to help the injured villager instead of pursuing the thief",
                "consequences": ["villager_ally", "thief_escaped"]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Decision added successfully"
        assert data["decision"]["decision"] == "help_villager"
    
    def test_advance_after_decision(self, client):
        """Test advancing after making required decisions"""
        story_id = CREATED_STORY_ID
        response = client.post(f"/api/stories/{story_id}/advance")
        
        assert response.status_code == 200
        data = response.json()
        assert data["current_stage"] == "first_combat"
    
    def test_add_combat_outcome(self, client):
        """Test recording a combat encounter"""
        story_id = CREATED_STORY_ID
        response = client.post(
            f"/api/stories/{story_id}/combat",
            json={
                "encounter_type": "bandit_ambush",
                "result": "victory",
                "damage_taken": 8,
                "loot_gained": ["gold_pieces_15", "iron_sword"],
                "xp_gained": 150
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Combat outcome recorded successfully"
        assert data["combat"]["result"] == "victory"
    
    def test_update_npc_status(self, client):
        """Test updating NPC status"""
        story_id = CREATED_STORY_ID
        response = client.post(
            f"/api/stories/{story_id}/npcs",
            json={
                "npc_id": "villager_tom",
                "status_data": {
                    "status": "ally",
                    "health": "recovered",
                    "location": "tavern",
                    "disposition": "grateful"
                }
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "NPC status updated successfully"
        assert data["npc_id"] == "villager_tom"

class TestWorldState:
    """Test world state management"""
    
    def test_get_world_state(self, client):
        """Test retrieving world state"""
        story_id = CREATED_STORY_ID
        response = client.get(f"/api/stories/{story_id}/world")
        
        assert response.status_code == 200
        data = response.json()
        assert "current_location" in data
        assert "explored_areas" in data
        assert "active_objectives" in data
        assert "completed_objectives" in data
        assert data["current_location"] == "starting_area"

class TestStoryManagement:
    """Test story title updates and abandonment"""
    
    def test_update_story_title(self, client):
        """Test updating story title"""
        story_id = CREATED_STORY_ID
        response = client.put(
            f"/api/stories/{story_id}/title",
            json={"title": "The Mysterious Fog of Millbrook"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Story title updated successfully"
        assert data["title"] == "The Mysterious Fog of Millbrook"
    
    def test_abandon_story(self, client):
        """Test abandoning a story"""
        story_id = CREATED_STORY_ID
        response = client.delete(f"/api/stories/{story_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Story abandoned successfully"
        
        # Verify story is marked as completed
        response = client.get(f"/api/stories/{story_id}")
        assert response.status_code == 200
        story_data = response.json()
        assert story_data["story_completed"] == True
        assert story_data["completion_type"] == "abandoned"

class TestStoryValidation:
    """Test story validation and error handling"""
    
    def test_add_decision_to_completed_story(self, client):
        """Test adding decision to completed story"""
        story_id = CREATED_STORY_ID
        response = client.post(
            f"/api/stories/{story_id}/decisions",
            json={
                "decision": "test_decision",
                "description": "This should fail",
                "consequences": []
            }
        )
        
        assert response.status_code == 409
        assert "Cannot add decisions to completed story" in response.json()["detail"]
    
    def test_advance_completed_story(self, client):
        """Test advancing completed story"""
        story_id = CREATED_STORY_ID
        response = client.post(f"/api/stories/{story_id}/advance")
        
        assert response.status_code == 409
        assert "Story is already completed" in response.json()["detail"]
    
    def test_invalid_story_type(self, client, test_user_and_character):
        """Test creating story with invalid type"""
        response = client.post(
            "/api/stories",
            json={
                "character_id": test_user_and_character["character_id"],
                "story_seed": "Test story",
                "story_type": "invalid_type"
            }
        )
        
        assert response.status_code == 422  # Validation error 