from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional, Dict, Any
import random
from ..models.character import Character
from ..schemas.character import (
    CharacterCreate, 
    CharacterUpdate, 
    CharacterWithRolledStats,
    StatRollResponse
)

class CharacterService:
    """Service for character operations including D&D 5e mechanics"""
    
    @staticmethod
    def roll_ability_score() -> tuple[int, List[int]]:
        """
        Roll 4d6, drop lowest die for D&D 5e ability score generation
        Returns: (final_score, list_of_individual_rolls)
        """
        rolls = [random.randint(1, 6) for _ in range(4)]
        rolls.sort(reverse=True)  # Sort in descending order
        final_score = sum(rolls[:3])  # Sum the highest 3
        return final_score, rolls
    
    @staticmethod
    def roll_all_stats() -> StatRollResponse:
        """Roll all six ability scores for a new character"""
        stats = {}
        all_rolls = {}
        
        abilities = ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma']
        
        for ability in abilities:
            score, rolls = CharacterService.roll_ability_score()
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
    
    @staticmethod
    def calculate_starting_hp(character_class: str, constitution_modifier: int) -> int:
        """Calculate starting HP based on class and constitution modifier"""
        # D&D 5e starting HP: max hit die + con modifier
        class_hit_dice = {
            'barbarian': 12,
            'fighter': 10, 'paladin': 10, 'ranger': 10,
            'bard': 8, 'cleric': 8, 'druid': 8, 'monk': 8, 'rogue': 8, 'warlock': 8,
            'artificer': 8, 'sorcerer': 6, 'wizard': 6
        }
        
        hit_die = class_hit_dice.get(character_class.lower(), 8)  # Default to d8
        return hit_die + max(0, constitution_modifier)  # Minimum 1 HP per level
    
    @staticmethod
    def get_class_proficiencies(character_class: str) -> Dict[str, List[str]]:
        """Get proficiencies based on character class"""
        # Simplified proficiencies - in a full implementation, this would be more detailed
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
            # Add more classes as needed
        }
        
        return class_proficiencies.get(character_class.lower(), {
            'armor': [], 'weapons': [], 'saving_throws': [], 'skills': []
        })
    
    @staticmethod
    def create_character(db: Session, character_data: CharacterCreate) -> Character:
        """Create a new character"""
        # Set current HP to max HP if not specified
        if character_data.current_hit_points is None:
            character_data.current_hit_points = character_data.max_hit_points
        
        # Create character instance
        db_character = Character(
            user_id=character_data.user_id,
            name=character_data.name,
            race=character_data.race,
            character_class=character_data.character_class,
            background=character_data.background,
            strength=character_data.strength,
            dexterity=character_data.dexterity,
            constitution=character_data.constitution,
            intelligence=character_data.intelligence,
            wisdom=character_data.wisdom,
            charisma=character_data.charisma,
            level=character_data.level,
            experience_points=character_data.experience_points,
            max_hit_points=character_data.max_hit_points,
            current_hit_points=character_data.current_hit_points,
            armor_class=character_data.armor_class,
            proficiencies=character_data.proficiencies,
            skill_proficiencies=character_data.skill_proficiencies,
            inventory=character_data.inventory,
            equipped_items=character_data.equipped_items,
            backstory=character_data.backstory,
            notes=character_data.notes
        )
        
        try:
            db.add(db_character)
            db.commit()
            db.refresh(db_character)
            return db_character
        except IntegrityError:
            db.rollback()
            raise ValueError("Character creation failed - database constraint violation")
    
    @staticmethod
    def create_character_with_rolled_stats(db: Session, character_data: CharacterWithRolledStats) -> Character:
        """Create a character with auto-rolled stats"""
        # Roll stats
        rolled_stats = CharacterService.roll_all_stats()
        
        # Get class proficiencies
        class_profs = CharacterService.get_class_proficiencies(character_data.character_class)
        
        # Calculate starting HP
        constitution_modifier = (rolled_stats.constitution - 10) // 2
        starting_hp = CharacterService.calculate_starting_hp(character_data.character_class, constitution_modifier)
        
        # Create character with rolled stats
        character_create = CharacterCreate(
            user_id=character_data.user_id,
            name=character_data.name,
            race=character_data.race,
            character_class=character_data.character_class,
            background=character_data.background,
            strength=rolled_stats.strength,
            dexterity=rolled_stats.dexterity,
            constitution=rolled_stats.constitution,
            intelligence=rolled_stats.intelligence,
            wisdom=rolled_stats.wisdom,
            charisma=rolled_stats.charisma,
            max_hit_points=starting_hp,
            current_hit_points=starting_hp,
            armor_class=10 + ((rolled_stats.dexterity - 10) // 2),  # Base AC + Dex modifier
            proficiencies=class_profs.get('saving_throws', []),
            skill_proficiencies=[],  # Would be selected during character creation
            inventory=[],
            equipped_items={},
            backstory=character_data.backstory
        )
        
        return CharacterService.create_character(db, character_create)
    
    @staticmethod
    def get_character(db: Session, character_id: int) -> Optional[Character]:
        """Get a character by ID"""
        return db.query(Character).filter(Character.id == character_id).first()
    
    @staticmethod
    def get_character_by_user(db: Session, user_id: str, character_id: int) -> Optional[Character]:
        """Get a character by ID, ensuring it belongs to the user"""
        return db.query(Character).filter(
            Character.id == character_id,
            Character.user_id == user_id
        ).first()
    
    @staticmethod
    def get_characters_by_user(db: Session, user_id: str, skip: int = 0, limit: int = 100) -> List[Character]:
        """Get all characters for a user"""
        return db.query(Character).filter(
            Character.user_id == user_id,
            Character.is_active == True
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_character(db: Session, character_id: int, character_update: CharacterUpdate) -> Optional[Character]:
        """Update a character"""
        db_character = db.query(Character).filter(Character.id == character_id).first()
        
        if not db_character:
            return None
        
        # Update only provided fields
        update_data = character_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_character, field, value)
        
        try:
            db.commit()
            db.refresh(db_character)
            return db_character
        except IntegrityError:
            db.rollback()
            raise ValueError("Character update failed - database constraint violation")
    
    @staticmethod
    def delete_character(db: Session, character_id: int, user_id: str) -> bool:
        """Soft delete a character (mark as inactive)"""
        db_character = db.query(Character).filter(
            Character.id == character_id,
            Character.user_id == user_id
        ).first()
        
        if not db_character:
            return False
        
        db_character.is_active = False
        db.commit()
        return True
    
    @staticmethod
    def hard_delete_character(db: Session, character_id: int, user_id: str) -> bool:
        """Permanently delete a character"""
        db_character = db.query(Character).filter(
            Character.id == character_id,
            Character.user_id == user_id
        ).first()
        
        if not db_character:
            return False
        
        db.delete(db_character)
        db.commit()
        return True
    
    @staticmethod
    def apply_damage(db: Session, character_id: int, damage: int) -> Optional[Character]:
        """Apply damage to a character"""
        db_character = db.query(Character).filter(Character.id == character_id).first()
        
        if not db_character:
            return None
        
        db_character.take_damage(damage)
        db.commit()
        db.refresh(db_character)
        return db_character
    
    @staticmethod
    def heal_character(db: Session, character_id: int, healing: int) -> Optional[Character]:
        """Heal a character"""
        db_character = db.query(Character).filter(Character.id == character_id).first()
        
        if not db_character:
            return None
        
        db_character.heal(healing)
        db.commit()
        db.refresh(db_character)
        return db_character
    
    @staticmethod
    def level_up_character(db: Session, character_id: int) -> Optional[Character]:
        """Level up a character"""
        db_character = db.query(Character).filter(Character.id == character_id).first()
        
        if not db_character:
            return None
        
        db_character.level_up()
        db.commit()
        db.refresh(db_character)
        return db_character
    
    @staticmethod
    def add_experience(db: Session, character_id: int, xp: int) -> Optional[Character]:
        """Add experience points to a character"""
        db_character = db.query(Character).filter(Character.id == character_id).first()
        
        if not db_character:
            return None
        
        db_character.experience_points += xp
        
        # Check for level up (simplified XP table)
        xp_thresholds = [0, 300, 900, 2700, 6500, 14000, 23000, 34000, 48000, 64000,
                        85000, 100000, 120000, 140000, 165000, 195000, 225000, 265000, 305000, 355000]
        
        current_level = db_character.level
        for level, threshold in enumerate(xp_thresholds, 1):
            if db_character.experience_points >= threshold and level > current_level:
                if level <= 20:  # Max level
                    db_character.level = level
        
        db.commit()
        db.refresh(db_character)
        return db_character 