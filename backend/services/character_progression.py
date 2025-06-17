from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
import math

from models.character import Character
from schemas.character_progression import (
    CharacterProgressionResponse,
    Skill,
    Achievement,
    LevelProgression
)

class CharacterProgressionService:
    """Service for managing character progression, XP, leveling, and achievements"""
    
    def __init__(self):
        # D&D 5e XP progression table
        self.xp_thresholds = {
            1: 0, 2: 300, 3: 900, 4: 2700, 5: 6500,
            6: 14000, 7: 23000, 8: 34000, 9: 48000, 10: 64000,
            11: 85000, 12: 100000, 13: 120000, 14: 140000, 15: 165000,
            16: 195000, 17: 225000, 18: 265000, 19: 305000, 20: 355000
        }
        
        # Base skills system
        self.base_skills = {
            "combat_mastery": {
                "name": "Combat Mastery",
                "max_level": 10,
                "description": "Improves attack accuracy and damage",
                "xp_per_level": 100,
                "bonuses": ["+1 to attack rolls", "+1 damage per 2 levels"]
            },
            "arcane_knowledge": {
                "name": "Arcane Knowledge", 
                "max_level": 10,
                "description": "Enhances magical abilities and spell power",
                "xp_per_level": 120,
                "bonuses": ["+1 to spell attack rolls", "+1 spell damage per 2 levels"]
            },
            "stealth_mastery": {
                "name": "Stealth Mastery",
                "max_level": 8,
                "description": "Improves stealth and sneaking abilities",
                "xp_per_level": 80,
                "bonuses": ["+2 to stealth checks", "Advantage on first attack from hiding"]
            },
            "survival_instinct": {
                "name": "Survival Instinct",
                "max_level": 8, 
                "description": "Increases health and survivability",
                "xp_per_level": 90,
                "bonuses": ["+2 HP per level", "+1 to saving throws"]
            },
            "social_influence": {
                "name": "Social Influence",
                "max_level": 6,
                "description": "Enhances charisma and persuasion",
                "xp_per_level": 70,
                "bonuses": ["+2 to persuasion/deception", "Better NPC reactions"]
            },
            "lore_master": {
                "name": "Lore Master",
                "max_level": 8,
                "description": "Increases knowledge and investigation abilities", 
                "xp_per_level": 85,
                "bonuses": ["+3 to investigation/history", "Extra information from lore"]
            }
        }
        
        # Achievement templates
        self.achievement_templates = {
            "first_steps": {
                "name": "First Steps",
                "description": "Complete your first adventure",
                "icon": "🚀",
                "category": "Adventure",
                "xp_reward": 50,
                "progress_required": 1
            },
            "monster_slayer": {
                "name": "Monster Slayer",
                "description": "Defeat 10 monsters in combat",
                "icon": "⚔️",
                "category": "Combat",
                "xp_reward": 100,
                "progress_required": 10
            },
            "treasure_hunter": {
                "name": "Treasure Hunter", 
                "description": "Find 5 rare or better items",
                "icon": "💎",
                "category": "Exploration",
                "xp_reward": 75,
                "progress_required": 5
            },
            "social_butterfly": {
                "name": "Social Butterfly",
                "description": "Successfully negotiate with 10 NPCs",
                "icon": "🗣️",
                "category": "Social",
                "xp_reward": 80,
                "progress_required": 10
            },
            "level_milestone": {
                "name": "Growing Stronger",
                "description": "Reach level 5",
                "icon": "⭐",
                "category": "Progression",
                "xp_reward": 200,
                "progress_required": 5
            },
            "spell_caster": {
                "name": "Spell Caster",
                "description": "Cast 25 spells successfully",
                "icon": "🔮",
                "category": "Magic",
                "xp_reward": 120,
                "progress_required": 25
            },
            "explorer": {
                "name": "Explorer",
                "description": "Discover 15 new locations",
                "icon": "🗺️",
                "category": "Exploration", 
                "xp_reward": 150,
                "progress_required": 15
            },
            "survivor": {
                "name": "Survivor",
                "description": "Survive 3 deadly encounters",
                "icon": "🛡️",
                "category": "Combat",
                "xp_reward": 180,
                "progress_required": 3
            }
        }

    async def get_character_progression(self, character_id: int, db: Session) -> CharacterProgressionResponse:
        """Get complete character progression data"""
        character = db.query(Character).filter(Character.id == character_id).first()
        if not character:
            raise ValueError(f"Character {character_id} not found")
        
        # Calculate progression data
        current_level = character.level
        current_xp = getattr(character, 'experience_points', 0)
        next_level_xp = self.xp_thresholds.get(current_level + 1, 999999)
        xp_to_next = max(0, next_level_xp - current_xp)
        
        # Generate skills
        skills = self._generate_character_skills(character)
        
        # Generate achievements
        achievements = self._generate_character_achievements(character)
        
        # Generate level progression data
        level_progression = self._generate_level_progression(character.character_class)
        
        return CharacterProgressionResponse(
            character_id=character_id,
            current_level=current_level,
            current_xp=current_xp,
            xp_to_next_level=xp_to_next,
            available_attribute_points=getattr(character, 'attribute_points', 0),
            available_skill_points=getattr(character, 'skill_points', 0),
            skills=skills,
            achievements=achievements,
            level_progression=level_progression,
            abilities={
                "strength": character.strength,
                "dexterity": character.dexterity,
                "constitution": character.constitution,
                "intelligence": character.intelligence,
                "wisdom": character.wisdom,
                "charisma": character.charisma
            }
        )

    async def add_experience(self, character_id: int, amount: int, reason: str, db: Session) -> Dict[str, Any]:
        """Add experience points to a character"""
        character = db.query(Character).filter(Character.id == character_id).first()
        if not character:
            raise ValueError(f"Character {character_id} not found")
        
        # Add XP
        old_xp = getattr(character, 'experience_points', 0)
        new_xp = old_xp + amount
        
        # Update character
        if hasattr(character, 'experience_points'):
            character.experience_points = new_xp
        else:
            # If the column doesn't exist in the model yet, we'll store it as metadata
            pass
        
        # Check for level up
        old_level = character.level
        new_level = self._calculate_level_from_xp(new_xp)
        level_up = new_level > old_level
        
        if level_up:
            character.level = new_level
            # Award attribute and skill points
            points_gained = new_level - old_level
            # Add logic to give points based on level difference
        
        db.commit()
        db.refresh(character)
        
        return {
            "xp_gained": amount,
            "new_total_xp": new_xp,
            "old_level": old_level,
            "new_level": new_level,
            "level_up": level_up,
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def level_up_character(self, character_id: int, chosen_features: List[str], db: Session) -> Dict[str, Any]:
        """Handle character level up process"""
        character = db.query(Character).filter(Character.id == character_id).first()
        if not character:
            raise ValueError(f"Character {character_id} not found")
        
        current_xp = getattr(character, 'experience_points', 0)
        calculated_level = self._calculate_level_from_xp(current_xp)
        
        if calculated_level <= character.level:
            raise ValueError("Character does not have enough XP to level up")
        
        # Apply level up benefits
        old_level = character.level
        character.level = calculated_level
        
        # Calculate HP gain (class-based)
        hp_gain = self._calculate_hp_gain(character.character_class)
        character.max_hit_points += hp_gain
        character.current_hit_points += hp_gain
        
        # Award points
        attribute_points_gained = 1 if calculated_level % 4 == 0 else 0
        skill_points_gained = 2
        
        db.commit()
        db.refresh(character)
        
        return {
            "old_level": old_level,
            "new_level": calculated_level,
            "hp_gained": hp_gain,
            "attribute_points_gained": attribute_points_gained,
            "skill_points_gained": skill_points_gained,
            "chosen_features": chosen_features,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def upgrade_skill(self, character_id: int, skill_id: str, db: Session) -> Dict[str, Any]:
        """Upgrade a character skill"""
        character = db.query(Character).filter(Character.id == character_id).first()
        if not character:
            raise ValueError(f"Character {character_id} not found")
        
        if skill_id not in self.base_skills:
            raise ValueError(f"Invalid skill ID: {skill_id}")
        
        # This would typically load from a character_skills table
        # For now, we'll simulate skill progression
        skill_info = self.base_skills[skill_id]
        current_level = 1  # Would be loaded from database
        
        if current_level >= skill_info["max_level"]:
            raise ValueError(f"Skill {skill_id} is already at maximum level")
        
        # Check if character has enough skill points
        available_points = getattr(character, 'skill_points', 0)
        if available_points < 1:
            raise ValueError("Not enough skill points to upgrade")
        
        # Apply upgrade
        new_level = current_level + 1
        
        return {
            "skill_id": skill_id,
            "skill_name": skill_info["name"],
            "old_level": current_level,
            "new_level": new_level,
            "bonuses_gained": skill_info["bonuses"],
            "timestamp": datetime.utcnow().isoformat()
        }

    async def upgrade_attribute(self, character_id: int, attribute_name: str, db: Session) -> Dict[str, Any]:
        """Upgrade a character attribute"""
        character = db.query(Character).filter(Character.id == character_id).first()
        if not character:
            raise ValueError(f"Character {character_id} not found")
        
        valid_attributes = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        if attribute_name not in valid_attributes:
            raise ValueError(f"Invalid attribute: {attribute_name}")
        
        # Check if character has enough attribute points
        available_points = getattr(character, 'attribute_points', 0)
        if available_points < 1:
            raise ValueError("Not enough attribute points to upgrade")
        
        # Get current value
        current_value = getattr(character, attribute_name)
        if current_value >= 20:  # D&D 5e cap
            raise ValueError(f"{attribute_name} is already at maximum value (20)")
        
        # Apply upgrade
        setattr(character, attribute_name, current_value + 1)
        
        # Update dependent stats if needed
        if attribute_name == "constitution":
            # Increase HP retroactively
            con_modifier_increase = 1 if (current_value + 1) % 2 == 0 else 0
            if con_modifier_increase:
                hp_increase = character.level * con_modifier_increase
                character.max_hit_points += hp_increase
                character.current_hit_points += hp_increase
        
        db.commit()
        db.refresh(character)
        
        return {
            "attribute": attribute_name,
            "old_value": current_value,
            "new_value": current_value + 1,
            "modifier": self._calculate_modifier(current_value + 1),
            "timestamp": datetime.utcnow().isoformat()
        }

    def _generate_character_skills(self, character: Character) -> List[Skill]:
        """Generate skill progression data for a character"""
        skills = []
        
        for skill_id, skill_info in self.base_skills.items():
            # In a real implementation, this would load from character_skills table
            current_level = min(character.level // 2, skill_info["max_level"])  # Simulate progression
            current_xp = current_level * skill_info["xp_per_level"]
            xp_required = (current_level + 1) * skill_info["xp_per_level"]
            
            skill = Skill(
                id=skill_id,
                name=skill_info["name"],
                current_level=current_level,
                max_level=skill_info["max_level"],
                xp_current=current_xp,
                xp_required=xp_required,
                description=skill_info["description"],
                bonuses=skill_info["bonuses"]
            )
            skills.append(skill)
        
        return skills

    def _generate_character_achievements(self, character: Character) -> List[Achievement]:
        """Generate achievement data for a character"""
        achievements = []
        
        for achievement_id, achievement_info in self.achievement_templates.items():
            # Simulate progress based on character level and data
            progress = self._calculate_achievement_progress(character, achievement_id)
            unlocked = progress >= achievement_info["progress_required"]
            
            achievement = Achievement(
                id=achievement_id,
                name=achievement_info["name"],
                description=achievement_info["description"],
                icon=achievement_info["icon"],
                category=achievement_info["category"],
                unlocked=unlocked,
                unlocked_at=datetime.utcnow() if unlocked else None,
                xp_reward=achievement_info["xp_reward"],
                progress_current=progress,
                progress_required=achievement_info["progress_required"]
            )
            achievements.append(achievement)
        
        return achievements

    def _generate_level_progression(self, character_class: str) -> List[LevelProgression]:
        """Generate level progression data"""
        progression = []
        
        # Class-specific HP per level
        hp_per_level = {
            "fighter": 10, "ranger": 10, "paladin": 10,
            "barbarian": 12, "rogue": 8, "bard": 8,
            "wizard": 6, "sorcerer": 6, "warlock": 8,
            "cleric": 8, "druid": 8, "monk": 8
        }
        
        base_hp = hp_per_level.get(character_class.lower(), 8)
        
        for level in range(1, 21):
            features = self._get_class_features_for_level(character_class, level)
            proficiency_bonus = math.ceil(level / 4) + 1
            
            progression_item = LevelProgression(
                level=level,
                xp_required=self.xp_thresholds.get(level, 0),
                hit_points_gained=base_hp,
                proficiency_bonus=proficiency_bonus,
                features_gained=features,
                spell_slots=self._get_spell_slots_for_level(character_class, level) if self._is_spellcaster(character_class) else None
            )
            progression.append(progression_item)
        
        return progression

    def _calculate_level_from_xp(self, xp: int) -> int:
        """Calculate character level based on XP"""
        for level in range(20, 0, -1):
            if xp >= self.xp_thresholds[level]:
                return level
        return 1

    def _calculate_hp_gain(self, character_class: str) -> int:
        """Calculate HP gain on level up"""
        hp_die = {
            "fighter": 10, "ranger": 10, "paladin": 10,
            "barbarian": 12, "rogue": 8, "bard": 8,
            "wizard": 6, "sorcerer": 6, "warlock": 8,
            "cleric": 8, "druid": 8, "monk": 8
        }
        
        die_size = hp_die.get(character_class.lower(), 8)
        return (die_size // 2) + 1  # Average roll

    def _calculate_modifier(self, ability_score: int) -> int:
        """Calculate D&D 5e ability modifier"""
        return (ability_score - 10) // 2

    def _calculate_achievement_progress(self, character: Character, achievement_id: str) -> int:
        """Calculate progress toward an achievement"""
        # Simulate progress based on character level
        if achievement_id == "level_milestone":
            return character.level
        elif achievement_id == "first_steps":
            return 1 if character.level > 1 else 0
        else:
            # Simulate progress based on level
            return min(character.level * 2, self.achievement_templates[achievement_id]["progress_required"])

    def _get_class_features_for_level(self, character_class: str, level: int) -> List[str]:
        """Get class features gained at a specific level"""
        # Simplified feature list
        common_features = {
            1: ["Base class features"],
            2: ["Class feature improvement"],
            3: ["Subclass choice"],
            4: ["Ability Score Improvement"],
            5: ["Extra Attack or spell improvement"],
            6: ["Class feature"],
            8: ["Ability Score Improvement"],
            10: ["Class feature"],
            12: ["Ability Score Improvement"],
            16: ["Ability Score Improvement"],
            19: ["Ability Score Improvement"],
            20: ["Capstone ability"]
        }
        
        return common_features.get(level, [])

    def _get_spell_slots_for_level(self, character_class: str, level: int) -> Dict[int, int]:
        """Get spell slots for spellcasting classes"""
        # Simplified spell slot progression for full casters
        if not self._is_spellcaster(character_class):
            return {}
        
        # Basic spell slot progression (simplified)
        slots = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0}
        
        if level >= 1:
            slots[1] = min(4, level + 1)
        if level >= 3:
            slots[2] = min(3, level - 1)
        if level >= 5:
            slots[3] = min(3, level - 3)
        if level >= 7:
            slots[4] = min(3, level - 5)
        if level >= 9:
            slots[5] = min(2, level - 7)
        
        return {k: v for k, v in slots.items() if v > 0}

    def _is_spellcaster(self, character_class: str) -> bool:
        """Check if class is a spellcaster"""
        spellcasters = ["wizard", "sorcerer", "warlock", "cleric", "druid", "bard", "ranger", "paladin"]
        return character_class.lower() in spellcasters 