import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from database import get_db, Base
from models.user import User
from models.character import Character

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_characters.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Mock authentication for testing
def mock_get_current_user_id():
    return "test_character_user_123"

def mock_get_current_user():
    db = TestingSessionLocal()
    user = db.query(User).filter(User.id == "test_character_user_123").first()
    db.close()
    return user

# Override auth dependencies for testing
from auth import get_current_user_id, get_current_user
app.dependency_overrides[get_current_user_id] = mock_get_current_user_id
app.dependency_overrides[get_current_user] = mock_get_current_user

@pytest.fixture(scope="module")
def client():
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create test client
    with TestClient(app) as c:
        yield c
    
    # Clean up
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def test_user(client):
    """Create a test user for character tests"""
    db = TestingSessionLocal()
    
    # Create test user
    user = User(
        id="test_character_user_123",
        email="test_character@example.com",
        first_name="Test",
        last_name="Character User"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    yield user
    
    db.close()

class TestCharacterOptions:
    def test_get_character_options(self, client):
        """Test getting character creation options"""
        response = client.get("/api/characters/options")
        
        assert response.status_code == 200
        data = response.json()
        assert "races" in data
        assert "classes" in data
        assert "backgrounds" in data
        assert len(data["races"]) > 0
        assert len(data["classes"]) > 0
        assert len(data["backgrounds"]) > 0

class TestStatRolling:
    def test_roll_stats(self, client):
        """Test rolling character stats"""
        response = client.post("/api/characters/roll-stats")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check all ability scores are present
        abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        for ability in abilities:
            assert ability in data
            assert isinstance(data[ability], int)
            assert 3 <= data[ability] <= 18  # Valid D&D stat range
        
        # Check rolls are included
        assert "rolls" in data
        assert isinstance(data["rolls"], list)

class TestCharacterCreation:
    def test_quick_create_character_success(self, client, test_user):
        """Test successful quick character creation"""
        character_data = {
            "name": "Test Hero",
            "race": "Human",
            "character_class": "Fighter",
            "background": "Soldier",
            "backstory": "A brave warrior from the northern lands."
        }
        
        response = client.post("/api/characters/quick-create", json=character_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == character_data["name"]
        assert data["race"] == character_data["race"]
        assert data["character_class"] == character_data["character_class"]
        assert data["background"] == character_data["background"]
        assert data["backstory"] == character_data["backstory"]
        assert data["level"] == 1
        assert data["experience_points"] == 0
        assert data["user_id"] == test_user.id
        assert "id" in data
        
        # Store character ID for other tests
        TestCharacterCreation.character_id = data["id"]
    
    def test_quick_create_character_missing_fields(self, client, test_user):
        """Test character creation with missing required fields"""
        character_data = {
            "name": "Incomplete Hero",
            "race": "Elf"
            # Missing character_class and background
        }
        
        response = client.post("/api/characters/quick-create", json=character_data)
        
        assert response.status_code == 422  # Validation error

class TestCharacterRetrieval:
    def test_get_character_by_id(self, client, test_user):
        """Test getting a character by ID"""
        character_id = getattr(TestCharacterCreation, 'character_id', None)
        if not character_id:
            pytest.skip("No character created in previous test")
        
        response = client.get(f"/api/characters/{character_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == character_id
        assert data["name"] == "Test Hero"
        assert data["user_id"] == test_user.id
    
    def test_get_character_not_found(self, client):
        """Test getting a non-existent character"""
        response = client.get("/api/characters/99999")
        
        assert response.status_code == 404
    
    def test_get_user_characters(self, client, test_user):
        """Test getting all characters for a user"""
        response = client.get("/api/characters")
        
        assert response.status_code == 200
        data = response.json()
        assert "characters" in data
        assert "total" in data
        assert isinstance(data["characters"], list)
        
        # Should have at least the character we created
        if hasattr(TestCharacterCreation, 'character_id'):
            assert data["total"] >= 1
            character = next((c for c in data["characters"] if c["name"] == "Test Hero"), None)
            assert character is not None
            assert character["user_id"] == test_user.id

class TestCharacterUpdate:
    def test_update_character(self, client, test_user):
        """Test updating a character"""
        character_id = getattr(TestCharacterCreation, 'character_id', None)
        if not character_id:
            pytest.skip("No character created in previous test")
        
        update_data = {
            "name": "Updated Hero",
            "backstory": "An updated backstory for our hero."
        }
        
        response = client.put(f"/api/characters/{character_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["backstory"] == update_data["backstory"]
        assert data["id"] == character_id
    
    def test_update_character_not_found(self, client):
        """Test updating a non-existent character"""
        update_data = {"name": "Ghost Hero"}
        
        response = client.put("/api/characters/99999", json=update_data)
        
        assert response.status_code == 404

class TestCharacterDeletion:
    def test_delete_character(self, client, test_user):
        """Test deleting a character"""
        character_id = getattr(TestCharacterCreation, 'character_id', None)
        if not character_id:
            pytest.skip("No character created in previous test")
        
        response = client.delete(f"/api/characters/{character_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        
        # Verify character is soft deleted (still exists but inactive)
        get_response = client.get(f"/api/characters/{character_id}")
        # Character should still be retrievable but marked as inactive
        assert get_response.status_code == 200
    
    def test_delete_character_not_found(self, client):
        """Test deleting a non-existent character"""
        response = client.delete("/api/characters/99999")
        
        assert response.status_code == 404

class TestCharacterValidation:
    def test_create_character_with_invalid_race(self, client, test_user):
        """Test creating character with invalid race"""
        character_data = {
            "name": "Invalid Race Hero",
            "race": "InvalidRace",
            "character_class": "Fighter",
            "background": "Soldier"
        }
        
        response = client.post("/api/characters/quick-create", json=character_data)
        
        # Should still work as we don't validate against specific lists in the backend
        # The frontend handles the validation
        assert response.status_code == 201
    
    def test_create_character_with_empty_name(self, client, test_user):
        """Test creating character with empty name"""
        character_data = {
            "name": "",
            "race": "Human",
            "character_class": "Fighter",
            "background": "Soldier"
        }
        
        response = client.post("/api/characters/quick-create", json=character_data)
        
        assert response.status_code == 422  # Validation error

class TestCharacterStats:
    def test_character_has_default_stats(self, client, test_user):
        """Test that created characters have proper default stats"""
        character_data = {
            "name": "Stats Test Hero",
            "race": "Dwarf",
            "character_class": "Cleric",
            "background": "Acolyte"
        }
        
        response = client.post("/api/characters/quick-create", json=character_data)
        
        assert response.status_code == 201
        data = response.json()
        
        # Check that all stats are present and reasonable
        stats = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        for stat in stats:
            assert stat in data
            assert isinstance(data[stat], int)
            assert 3 <= data[stat] <= 18
        
        # Check combat stats (correct field names)
        assert data["current_hit_points"] > 0
        assert data["max_hit_points"] > 0
        assert data["armor_class"] >= 10
        assert data["level"] == 1
        assert data["experience_points"] == 0
        
        # Clean up
        client.delete(f"/api/characters/{data['id']}") 