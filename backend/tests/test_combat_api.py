import pytest
import json
from fastapi.testclient import TestClient
from unittest.mock import patch

from main import app
from services.combat import CombatService
from schemas.combat import EnemyTemplateCreate, CombatEncounterCreate

client = TestClient(app)

class TestCombatAPI:
    """Test suite for Combat API endpoints"""

    def test_list_enemy_templates_empty(self):
        """Test listing enemy templates when none exist"""
        # Clear any existing templates first
        response = client.get("/api/combat/enemy-templates")
        assert response.status_code == 200
        # Should return a list (might be empty or have existing templates)
        data = response.json()
        assert isinstance(data, list)

    def test_create_enemy_template(self):
        """Test creating a new enemy template"""
        template_data = {
            "name": "Test Orc",
            "creature_type": "HUMANOID",
            "size": "Medium",
            "challenge_rating": 0.5,
            "alignment": "Chaotic Evil",
            "strength": 16,
            "dexterity": 12,
            "constitution": 16,
            "intelligence": 7,
            "wisdom": 11,
            "charisma": 10,
            "hit_points": 15,
            "armor_class": 13,
            "speed": "30 ft.",
            "proficiency_bonus": 2,
            "attacks": [
                {
                    "name": "Greataxe",
                    "type": "melee_weapon",
                    "attack_bonus": 5,
                    "damage": "1d12+3",
                    "damage_type": "slashing",
                    "reach": "5 ft.",
                    "targets": 1,
                    "description": "Melee Weapon Attack: +5 to hit, reach 5 ft., one target."
                }
            ],
            "xp_value": 100
        }
        
        response = client.post("/api/combat/enemy-templates", json=template_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["name"] == "Test Orc"
        assert data["creature_type"] == "HUMANOID"
        assert data["challenge_rating"] == 0.5
        assert data["hit_points"] == 15
        assert data["armor_class"] == 13
        assert len(data["attacks"]) == 1
        assert data["attacks"][0]["name"] == "Greataxe"
        assert "id" in data
        assert "created_at" in data

    def test_get_enemy_template(self):
        """Test getting a specific enemy template"""
        # First create a template
        template_data = {
            "name": "Test Skeleton",
            "creature_type": "UNDEAD",
            "size": "Medium",
            "challenge_rating": 0.25,
            "hit_points": 13,
            "armor_class": 13,
            "xp_value": 50
        }
        
        create_response = client.post("/api/combat/enemy-templates", json=template_data)
        assert create_response.status_code == 201
        created_template = create_response.json()
        template_id = created_template["id"]
        
        # Now get the template
        response = client.get(f"/api/combat/enemy-templates/{template_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == template_id
        assert data["name"] == "Test Skeleton"
        assert data["creature_type"] == "UNDEAD"

    def test_get_nonexistent_enemy_template(self):
        """Test getting a template that doesn't exist"""
        response = client.get("/api/combat/enemy-templates/99999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_update_enemy_template(self):
        """Test updating an enemy template"""
        # First create a template
        template_data = {
            "name": "Test Zombie",
            "creature_type": "UNDEAD",
            "size": "Medium",
            "challenge_rating": 0.25,
            "hit_points": 22,
            "armor_class": 8,
            "xp_value": 50
        }
        
        create_response = client.post("/api/combat/enemy-templates", json=template_data)
        assert create_response.status_code == 201
        created_template = create_response.json()
        template_id = created_template["id"]
        
        # Update the template
        update_data = {
            "name": "Updated Zombie",
            "hit_points": 25,
            "armor_class": 9
        }
        
        response = client.put(f"/api/combat/enemy-templates/{template_id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "Updated Zombie"
        assert data["hit_points"] == 25
        assert data["armor_class"] == 9
        assert data["creature_type"] == "UNDEAD"  # Should remain unchanged

    def test_delete_enemy_template(self):
        """Test deleting an enemy template"""
        # First create a template
        template_data = {
            "name": "Test Goblin",
            "creature_type": "HUMANOID",
            "size": "Small",
            "challenge_rating": 0.25,
            "hit_points": 7,
            "armor_class": 15,
            "xp_value": 50
        }
        
        create_response = client.post("/api/combat/enemy-templates", json=template_data)
        assert create_response.status_code == 201
        created_template = create_response.json()
        template_id = created_template["id"]
        
        # Delete the template
        response = client.delete(f"/api/combat/enemy-templates/{template_id}")
        assert response.status_code == 204
        
        # Verify it's deleted
        get_response = client.get(f"/api/combat/enemy-templates/{template_id}")
        assert get_response.status_code == 404

    def test_list_enemy_templates_with_filters(self):
        """Test listing enemy templates with filters"""
        # Create a few templates with different creature types
        templates = [
            {
                "name": "Filter Test Orc",
                "creature_type": "HUMANOID",
                "challenge_rating": 0.5,
                "hit_points": 15,
                "armor_class": 13,
                "xp_value": 100
            },
            {
                "name": "Filter Test Dragon",
                "creature_type": "DRAGON",
                "challenge_rating": 2.0,
                "hit_points": 50,
                "armor_class": 17,
                "xp_value": 450
            }
        ]
        
        for template_data in templates:
            response = client.post("/api/combat/enemy-templates", json=template_data)
            assert response.status_code == 201
        
        # Test filtering by creature type
        response = client.get("/api/combat/enemy-templates?creature_type=HUMANOID")
        assert response.status_code == 200
        data = response.json()
        humanoid_templates = [t for t in data if t["creature_type"] == "HUMANOID"]
        assert len(humanoid_templates) >= 1
        
        # Test filtering by challenge rating
        response = client.get("/api/combat/enemy-templates?challenge_rating_min=1.0")
        assert response.status_code == 200
        data = response.json()
        high_cr_templates = [t for t in data if t["challenge_rating"] >= 1.0]
        assert len(high_cr_templates) >= 1

    def test_invalid_creature_type(self):
        """Test creating template with invalid creature type"""
        template_data = {
            "name": "Invalid Creature",
            "creature_type": "INVALID_TYPE",
            "hit_points": 10,
            "armor_class": 10,
            "xp_value": 25
        }
        
        response = client.post("/api/combat/enemy-templates", json=template_data)
        assert response.status_code == 422  # Validation error

    def test_missing_required_fields(self):
        """Test creating template with missing required fields"""
        template_data = {
            "name": "Incomplete Creature"
            # Missing required fields like hit_points, armor_class, etc.
        }
        
        response = client.post("/api/combat/enemy-templates", json=template_data)
        assert response.status_code == 422  # Validation error

class TestCombatService:
    """Test suite for CombatService functionality"""

    def test_create_enemy_template_service(self):
        """Test creating enemy template through service"""
        from database import SessionLocal
        
        db = SessionLocal()
        try:
            combat_service = CombatService(db)
            
            template_data = EnemyTemplateCreate(
                name="Service Test Orc",
                creature_type="HUMANOID",
                hit_points=15,
                armor_class=13,
                xp_value=100
            )
            
            template = combat_service.create_enemy_template(template_data)
            assert template.name == "Service Test Orc"
            assert template.creature_type.value == "HUMANOID"
            assert template.hit_points == 15
            assert template.id is not None
            
        finally:
            db.close()

    def test_get_enemy_templates_service(self):
        """Test getting enemy templates through service"""
        from database import SessionLocal
        
        db = SessionLocal()
        try:
            combat_service = CombatService(db)
            templates = combat_service.get_enemy_templates()
            assert isinstance(templates, list)
            # Should have at least the templates we created in previous tests
            
        finally:
            db.close() 