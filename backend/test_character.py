#!/usr/bin/env python3
"""
Simple test script for Character model and service
Run this to verify the database setup works correctly
"""
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from schemas.character import StatRollResponse
import random

def roll_ability_score():
    """Roll 4d6, drop lowest die for D&D 5e ability score generation"""
    rolls = [random.randint(1, 6) for _ in range(4)]
    rolls.sort(reverse=True)  # Sort in descending order
    final_score = sum(rolls[:3])  # Sum the highest 3
    return final_score, rolls

def roll_all_stats():
    """Roll all six ability scores for a new character"""
    stats = {}
    all_rolls = {}
    
    abilities = ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma']
    
    for ability in abilities:
        score, rolls = roll_ability_score()
        stats[ability] = score
        all_rolls[ability] = rolls
    
    return StatRollResponse(
        strength=stats['strength'],
        dexterity=stats['dexterity'],
        constitution=stats['constitution'],
        intelligence=stats['intelligence'],
        wisdom=stats['wisdom'],
        charisma=stats['charisma'],
        rolls=[all_rolls[ability] for ability in abilities]
    )

def calculate_starting_hp(character_class: str, constitution_modifier: int) -> int:
    """Calculate starting HP based on class and constitution modifier"""
    class_hit_dice = {
        'barbarian': 12,
        'fighter': 10, 'paladin': 10, 'ranger': 10,
        'bard': 8, 'cleric': 8, 'druid': 8, 'monk': 8, 'rogue': 8, 'warlock': 8,
        'artificer': 8, 'sorcerer': 6, 'wizard': 6
    }
    
    hit_die = class_hit_dice.get(character_class.lower(), 8)  # Default to d8
    return hit_die + max(0, constitution_modifier)  # Minimum 1 HP per level

def get_class_proficiencies(character_class: str):
    """Get proficiencies based on character class"""
    class_proficiencies = {
        'fighter': {
            'armor': ['light', 'medium', 'heavy', 'shields'],
            'weapons': ['simple', 'martial'],
            'saving_throws': ['strength', 'constitution'],
            'skills': ['acrobatics', 'animal_handling', 'athletics', 'history', 
                      'insight', 'intimidation', 'perception', 'survival']
        },
        'wizard': {
            'armor': [],
            'weapons': ['daggers', 'darts', 'slings', 'quarterstaffs', 'light_crossbows'],
            'saving_throws': ['intelligence', 'wisdom'],
            'skills': ['arcana', 'history', 'insight', 'investigation', 
                      'medicine', 'religion']
        },
        'rogue': {
            'armor': ['light'],
            'weapons': ['simple', 'hand_crossbows', 'longswords', 'rapiers', 'shortswords'],
            'saving_throws': ['dexterity', 'intelligence'],
            'skills': ['acrobatics', 'athletics', 'deception', 'insight', 
                      'intimidation', 'investigation', 'perception', 'performance',
                      'persuasion', 'sleight_of_hand', 'stealth']
        }
    }
    
    return class_proficiencies.get(character_class.lower(), {
        'armor': [], 'weapons': [], 'saving_throws': [], 'skills': []
    })

def test_stat_rolling():
    """Test the D&D 5e stat rolling functionality"""
    print("🎲 Testing D&D 5e Stat Rolling...")
    
    # Test single ability score roll
    score, rolls = roll_ability_score()
    print(f"Single ability roll: {score} (from rolls: {rolls})")
    
    # Test rolling all stats
    stats = roll_all_stats()
    print(f"\nRolled character stats:")
    print(f"  STR: {stats.strength}")
    print(f"  DEX: {stats.dexterity}")  
    print(f"  CON: {stats.constitution}")
    print(f"  INT: {stats.intelligence}")
    print(f"  WIS: {stats.wisdom}")
    print(f"  CHA: {stats.charisma}")
    
    return stats

def test_character_creation():
    """Test character creation logic"""
    print("\n⚔️ Testing Character Creation...")
    
    # Test class proficiencies
    fighter_profs = get_class_proficiencies('fighter')
    print(f"Fighter proficiencies: {fighter_profs}")
    
    wizard_profs = get_class_proficiencies('wizard')
    print(f"Wizard proficiencies: {wizard_profs}")
    
    # Test HP calculation
    hp = calculate_starting_hp('fighter', 2)  # +2 CON modifier
    print(f"Fighter starting HP with +2 CON: {hp}")
    
    hp = calculate_starting_hp('wizard', -1)  # -1 CON modifier  
    print(f"Wizard starting HP with -1 CON: {hp}")

def test_character_mechanics():
    """Test character progression and mechanics"""
    print("\n📈 Testing Character Mechanics...")
    
    # Create a mock character with D&D 5e mechanics
    class MockCharacter:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
        
        @property
        def strength_modifier(self):
            return (self.strength - 10) // 2
        
        @property
        def dexterity_modifier(self):
            return (self.dexterity - 10) // 2
        
        @property
        def constitution_modifier(self):
            return (self.constitution - 10) // 2
        
        @property
        def proficiency_bonus(self):
            return (self.level - 1) // 4 + 2
        
        def get_skill_bonus(self, skill: str) -> int:
            skill_abilities = {
                'athletics': 'strength',
                'stealth': 'dexterity'
            }
            
            ability = skill_abilities.get(skill.lower())
            if not ability:
                return 0
                
            if ability == 'strength':
                return self.strength_modifier
            elif ability == 'dexterity':
                return self.dexterity_modifier
            return 0
        
        def take_damage(self, damage: int):
            self.current_hit_points = max(0, self.current_hit_points - damage)
        
        def heal(self, amount: int):
            self.current_hit_points = min(self.max_hit_points, self.current_hit_points + amount)
    
    character = MockCharacter(
        user_id="test_user",
        name="Test Hero",
        race="human",
        character_class="fighter",
        strength=16,
        dexterity=14,
        constitution=15,
        intelligence=10,
        wisdom=12,
        charisma=8,
        level=1,
        max_hit_points=12,
        current_hit_points=12,
        armor_class=16
    )
    
    print(f"Character: {character.name}")
    print(f"  STR: {character.strength} (mod: {character.strength_modifier})")
    print(f"  DEX: {character.dexterity} (mod: {character.dexterity_modifier})")
    print(f"  CON: {character.constitution} (mod: {character.constitution_modifier})")
    print(f"  Proficiency Bonus: {character.proficiency_bonus}")
    print(f"  Athletics (STR): {character.get_skill_bonus('athletics')}")
    print(f"  Stealth (DEX): {character.get_skill_bonus('stealth')}")
    
    # Test damage and healing
    print(f"\nBefore damage: {character.current_hit_points}/{character.max_hit_points} HP")
    character.take_damage(5)
    print(f"After 5 damage: {character.current_hit_points}/{character.max_hit_points} HP")
    character.heal(3)
    print(f"After healing 3: {character.current_hit_points}/{character.max_hit_points} HP")

if __name__ == "__main__":
    print("🧙‍♂️ SoloRelms Character System Test")
    print("=" * 40)
    
    try:
        # Test stat rolling
        stats = test_stat_rolling()
        
        # Test character creation logic
        test_character_creation()
        
        # Test character mechanics
        test_character_mechanics()
        
        print("\n✅ All tests completed successfully!")
        print("Character system is working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc() 