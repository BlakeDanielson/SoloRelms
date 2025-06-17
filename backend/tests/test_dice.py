import pytest
import json
from fastapi.testclient import TestClient
from unittest.mock import patch
import random

from main import app
from services.dice_service import DiceService, AdvantageType, DiceRollResult, AttackRollResult
from schemas.dice import DiceRollRequest, AttackRollRequest

client = TestClient(app)

class TestDiceService:
    """Test the DiceService class"""
    
    def test_roll_single_die(self):
        """Test rolling a single die"""
        for _ in range(10):  # Test multiple times for randomness
            result = DiceService.roll_die(6)
            assert 1 <= result <= 6
            
        for _ in range(10):
            result = DiceService.roll_die(20)
            assert 1 <= result <= 20
    
    def test_roll_multiple_dice(self):
        """Test rolling multiple dice"""
        rolls = DiceService.roll_multiple_dice(3, 6)
        assert len(rolls) == 3
        for roll in rolls:
            assert 1 <= roll <= 6
    
    def test_parse_dice_notation(self):
        """Test parsing dice notation"""
        # Basic notation
        num_dice, die_sides, modifier = DiceService.parse_dice_notation("2d6+3")
        assert num_dice == 2
        assert die_sides == 6
        assert modifier == 3
        
        # Single die with negative modifier
        num_dice, die_sides, modifier = DiceService.parse_dice_notation("1d20-1")
        assert num_dice == 1
        assert die_sides == 20
        assert modifier == -1
        
        # No modifier
        num_dice, die_sides, modifier = DiceService.parse_dice_notation("3d8")
        assert num_dice == 3
        assert die_sides == 8
        assert modifier == 0
        
        # Single die notation (d20)
        num_dice, die_sides, modifier = DiceService.parse_dice_notation("d20")
        assert num_dice == 1
        assert die_sides == 20
        assert modifier == 0
    
    def test_parse_invalid_notation(self):
        """Test parsing invalid dice notation"""
        with pytest.raises(ValueError):
            DiceService.parse_dice_notation("invalid")
        
        with pytest.raises(ValueError):
            DiceService.parse_dice_notation("2x6")
        
        with pytest.raises(ValueError):
            DiceService.parse_dice_notation("")
    
    def test_roll_dice_notation_basic(self):
        """Test rolling dice with basic notation"""
        result = DiceService.roll_dice_notation("2d6")
        assert isinstance(result, DiceRollResult)
        assert len(result.individual_rolls) == 2
        assert 2 <= result.total <= 12
        assert result.dice_notation == "2d6"
        assert result.modifier == 0
        
        # Test with modifier
        result = DiceService.roll_dice_notation("1d20+5")
        assert 6 <= result.total <= 25
        assert result.modifier == 5
    
    def test_roll_with_advantage(self):
        """Test rolling with advantage/disadvantage"""
        # Mock random to control the outcome
        with patch('random.randint') as mock_random:
            # First roll: 15, Second roll: 10
            mock_random.side_effect = [15, 10]
            
            result = DiceService.roll_dice_notation("1d20", AdvantageType.ADVANTAGE)
            assert result.total == 15  # Should pick the higher roll
            assert result.dropped_dice == [10]
            assert result.advantage_type == AdvantageType.ADVANTAGE
            
        with patch('random.randint') as mock_random:
            # First roll: 15, Second roll: 10
            mock_random.side_effect = [15, 10]
            
            result = DiceService.roll_dice_notation("1d20", AdvantageType.DISADVANTAGE)
            assert result.total == 10  # Should pick the lower roll
            assert result.dropped_dice == [15]
            assert result.advantage_type == AdvantageType.DISADVANTAGE
    
    def test_roll_with_keep_drop(self):
        """Test rolling with keep highest/lowest notation"""
        with patch('random.randint') as mock_random:
            # Mock rolls: 6, 4, 3, 2
            mock_random.side_effect = [6, 4, 3, 2]
            
            result = DiceService.roll_dice_notation("4d6kh3")
            assert len(result.individual_rolls) == 3  # Should keep 3 dice
            assert result.total == 13  # 6 + 4 + 3 = 13
            assert result.dropped_dice == [2]  # Should drop the lowest
            
        with patch('random.randint') as mock_random:
            # Mock rolls: 6, 4, 3, 2
            mock_random.side_effect = [6, 4, 3, 2]
            
            result = DiceService.roll_dice_notation("4d6dl1")
            assert len(result.individual_rolls) == 3  # Should keep 3 dice after dropping 1
            assert result.total == 13  # 6 + 4 + 3 = 13
            assert result.dropped_dice == [2]  # Should drop the lowest
    
    def test_roll_ability_score(self):
        """Test rolling ability scores"""
        result = DiceService.roll_ability_score()
        assert isinstance(result, DiceRollResult)
        assert 3 <= result.total <= 18  # Ability scores range from 3-18
        assert len(result.individual_rolls) == 3  # Should keep 3 of 4 dice
    
    def test_roll_all_ability_scores(self):
        """Test rolling all ability scores"""
        results = DiceService.roll_all_ability_scores()
        expected_abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        
        assert len(results) == 6
        for ability in expected_abilities:
            assert ability in results
            assert isinstance(results[ability], DiceRollResult)
            assert 3 <= results[ability].total <= 18
    
    def test_roll_hit_points(self):
        """Test rolling hit points"""
        # Level 1 should get max hit die
        result = DiceService.roll_hit_points(8, 2, level=1)
        assert result.total == 10  # 8 (max hit die) + 2 (con mod) = 10
        assert result.description == "Level 1 HP (max hit die + CON modifier)"
        
        # Higher levels should roll
        result = DiceService.roll_hit_points(8, 2, level=2)
        assert 3 <= result.total <= 10  # 1d8+2 = 3-10
    
    def test_roll_attack(self):
        """Test rolling attack rolls"""
        result = DiceService.roll_attack(5)
        assert 6 <= result.total <= 25  # 1d20+5
        assert result.modifier == 5
    
    def test_roll_damage(self):
        """Test rolling damage"""
        result = DiceService.roll_damage("1d8+3")
        assert 4 <= result.total <= 11  # 1d8+3
        assert result.modifier == 3
    
    def test_make_attack_roll(self):
        """Test making complete attack rolls"""
        with patch('random.randint') as mock_random:
            # Mock: attack roll 15, damage roll 6
            mock_random.side_effect = [15, 6]
            
            result = DiceService.make_attack_roll(
                attack_bonus=5,
                damage_notation="1d8+3",
                target_ac=12
            )
            
            assert isinstance(result, AttackRollResult)
            assert result.attack_roll.total == 20  # 15 + 5
            assert result.is_hit == True  # 20 >= 12
            assert result.is_critical == False  # 15 is not a natural 20
            assert result.damage_roll.total == 9  # 6 + 3
            assert result.target_ac == 12
    
    def test_critical_hit(self):
        """Test critical hit mechanics"""
        with patch('random.randint') as mock_random:
            # Mock: natural 20 attack, damage rolls 6, 4 (for crit)
            mock_random.side_effect = [20, 6, 4]
            
            result = DiceService.make_attack_roll(
                attack_bonus=5,
                damage_notation="1d8+3",
                target_ac=15
            )
            
            assert result.is_critical == True
            assert result.is_hit == True
            assert result.attack_roll.total == 25
            # Critical damage should be: (6+3) + 4 = 13 (doubled dice, not modifier)
            assert result.damage_roll.total == 13
    
    def test_miss_attack(self):
        """Test missed attacks"""
        with patch('random.randint') as mock_random:
            # Mock: low attack roll
            mock_random.side_effect = [5]
            
            result = DiceService.make_attack_roll(
                attack_bonus=2,
                damage_notation="1d8+3",
                target_ac=15
            )
            
            assert result.is_hit == False  # 7 < 15
            assert result.is_critical == False
            assert result.damage_roll is None  # No damage on miss

class TestDiceAPI:
    """Test the dice API endpoints"""
    
    def test_roll_dice_endpoint(self):
        """Test the basic dice rolling endpoint"""
        request_data = {
            "notation": "2d6+3",
            "advantage_type": "normal"
        }
        
        response = client.post("/api/dice/roll", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "total" in data
        assert "individual_rolls" in data
        assert len(data["individual_rolls"]) == 2
        assert 5 <= data["total"] <= 15  # 2d6+3 = 5-15
        assert data["dice_notation"] == "2d6+3"
        assert data["modifier"] == 3
    
    def test_roll_dice_with_advantage(self):
        """Test dice rolling with advantage"""
        request_data = {
            "notation": "1d20+5",
            "advantage_type": "advantage"
        }
        
        response = client.post("/api/dice/roll", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["advantage_type"] == "advantage"
        assert data["dropped_dice"] is not None
        assert len(data["dropped_dice"]) == 1
    
    def test_roll_invalid_notation(self):
        """Test rolling with invalid dice notation"""
        request_data = {
            "notation": "invalid",
            "advantage_type": "normal"
        }
        
        response = client.post("/api/dice/roll", json=request_data)
        assert response.status_code == 400
        assert "Invalid dice notation" in response.json()["detail"]
    
    def test_attack_roll_endpoint(self):
        """Test the attack roll endpoint"""
        request_data = {
            "attack_bonus": 7,
            "damage_notation": "1d8+4",
            "target_ac": 15,
            "advantage_type": "normal"
        }
        
        response = client.post("/api/dice/attack", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "attack_roll" in data
        assert "is_critical" in data
        assert "is_hit" in data
        assert "target_ac" in data
        assert data["target_ac"] == 15
        
        # Check attack roll structure
        attack_roll = data["attack_roll"]
        assert 8 <= attack_roll["total"] <= 27  # 1d20+7
        
        # If hit, should have damage roll
        if data["is_hit"]:
            assert data["damage_roll"] is not None
            damage_roll = data["damage_roll"]
            # Normal damage: 1d8+4 = 5-12
            # Critical damage: 2d8+4 = 6-20
            max_damage = 20 if data["is_critical"] else 12
            assert 5 <= damage_roll["total"] <= max_damage
    
    def test_ability_scores_endpoint(self):
        """Test the ability score generation endpoint"""
        response = client.post("/api/dice/ability-scores")
        assert response.status_code == 200
        
        data = response.json()
        assert "scores" in data
        
        expected_abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        scores = data["scores"]
        
        for ability in expected_abilities:
            assert ability in scores
            score_data = scores[ability]
            assert 3 <= score_data["total"] <= 18
            assert len(score_data["individual_rolls"]) == 3  # 4d6 keep highest 3
    
    def test_saving_throw_endpoint(self):
        """Test the saving throw endpoint"""
        request_data = {
            "ability_modifier": 3,
            "proficiency_bonus": 2,
            "advantage_type": "normal",
            "description": "Constitution saving throw"
        }
        
        response = client.post("/api/dice/saving-throw", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert 6 <= data["total"] <= 25  # 1d20+5
        assert data["modifier"] == 5  # 3 + 2
        assert data["description"] == "Constitution saving throw"
    
    def test_skill_check_endpoint(self):
        """Test the skill check endpoint"""
        request_data = {
            "ability_modifier": 4,
            "proficiency_bonus": 3,
            "skill_name": "Stealth",
            "dc": 15
        }
        
        response = client.post("/api/dice/skill-check", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "roll_result" in data
        assert data["skill_name"] == "Stealth"
        assert data["dc"] == 15
        assert "success" in data
        
        roll_result = data["roll_result"]
        assert 8 <= roll_result["total"] <= 27  # 1d20+7
        
        # Check success determination
        expected_success = roll_result["total"] >= 15
        assert data["success"] == expected_success
    
    def test_initiative_endpoint(self):
        """Test the initiative roll endpoint"""
        request_data = {
            "dexterity_modifier": 3,
            "advantage_type": "normal"
        }
        
        response = client.post("/api/dice/initiative", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert 4 <= data["total"] <= 23  # 1d20+3
        assert data["modifier"] == 3
        assert data["description"] == "Initiative roll"
    
    def test_hit_points_endpoint(self):
        """Test the hit points roll endpoint"""
        request_data = {
            "hit_die": 10,
            "constitution_modifier": 2,
            "level": 1
        }
        
        response = client.post("/api/dice/hit-points", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["total"] == 12  # Level 1: max hit die + con mod
        
        # Test higher level
        request_data["level"] = 3
        response = client.post("/api/dice/hit-points", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert 3 <= data["total"] <= 12  # 1d10+2
    
    def test_multiple_dice_endpoint(self):
        """Test rolling multiple dice at once"""
        request_data = {
            "rolls": [
                {"notation": "1d20+5", "description": "Attack roll"},
                {"notation": "1d8+3", "description": "Damage roll"},
                {"notation": "1d6", "description": "Sneak attack"}
            ]
        }
        
        response = client.post("/api/dice/multiple", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "results" in data
        assert "total_sum" in data
        assert len(data["results"]) == 3
        
        # Check individual results
        assert data["results"][0]["description"] == "Attack roll"
        assert data["results"][1]["description"] == "Damage roll"
        assert data["results"][2]["description"] == "Sneak attack"
        
        # Verify total sum
        expected_sum = sum(result["total"] for result in data["results"])
        assert data["total_sum"] == expected_sum
    
    def test_quick_roll_endpoint(self):
        """Test the quick roll endpoint"""
        request_data = {
            "roll_type": "d20",
            "modifier": 5,
            "advantage_type": "normal"
        }
        
        response = client.post("/api/dice/quick-roll", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert 6 <= data["total"] <= 25  # 1d20+5
        assert data["modifier"] == 5
        assert "Quick d20 roll" in data["description"]
    
    def test_quick_roll_invalid_type(self):
        """Test quick roll with invalid dice type"""
        request_data = {
            "roll_type": "d7",  # Invalid type
            "modifier": 0
        }
        
        response = client.post("/api/dice/quick-roll", json=request_data)
        assert response.status_code == 400
        assert "Unsupported roll type" in response.json()["detail"]
    
    def test_validate_notation_endpoint(self):
        """Test the dice notation validation endpoint"""
        # Valid notation
        request_data = {"notation": "2d6+3"}
        response = client.post("/api/dice/validate", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["is_valid"] == True
        assert data["parsed_notation"]["num_dice"] == 2
        assert data["parsed_notation"]["die_sides"] == 6
        assert data["parsed_notation"]["modifier"] == 3
        
        # Invalid notation
        request_data = {"notation": "invalid"}
        response = client.post("/api/dice/validate", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["is_valid"] == False
        assert data["error_message"] is not None
    
    def test_convenience_endpoints(self):
        """Test convenience endpoints for common rolls"""
        # Test d20 endpoint
        response = client.post("/api/dice/d20?modifier=3")
        assert response.status_code == 200
        data = response.json()
        assert 4 <= data["total"] <= 23
        
        # Test d6 endpoint
        response = client.post("/api/dice/d6?num_dice=2&modifier=1")
        assert response.status_code == 200
        data = response.json()
        assert 3 <= data["total"] <= 13  # 2d6+1
        
        # Test percentile endpoint
        response = client.post("/api/dice/percentile")
        assert response.status_code == 200
        data = response.json()
        assert 1 <= data["total"] <= 100 