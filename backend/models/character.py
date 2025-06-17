from sqlalchemy import Column, Integer, String, JSON, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime
try:
    from ..database import Base
except ImportError:
    # Fallback for when running from alembic or direct execution
    from database import Base
import json

class Character(Base):
    """Character model with D&D 5e stats and progression"""
    __tablename__ = "characters"
    
    # Primary key and identification
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)  # Clerk user ID
    name = Column(String(100), nullable=False)
    
    # Character creation details
    race = Column(String(50), nullable=False)
    character_class = Column(String(50), nullable=False)
    background = Column(String(50), nullable=True)
    
    # Core D&D 5e Ability Scores (3-20 range)
    strength = Column(Integer, nullable=False, default=10)
    dexterity = Column(Integer, nullable=False, default=10)
    constitution = Column(Integer, nullable=False, default=10)
    intelligence = Column(Integer, nullable=False, default=10)
    wisdom = Column(Integer, nullable=False, default=10)
    charisma = Column(Integer, nullable=False, default=10)
    
    # Character progression
    level = Column(Integer, nullable=False, default=1)
    experience_points = Column(Integer, nullable=False, default=0)
    
    # Health and resources
    max_hit_points = Column(Integer, nullable=False, default=8)
    current_hit_points = Column(Integer, nullable=False, default=8)
    armor_class = Column(Integer, nullable=False, default=10)
    
    # Proficiency and skills (stored as JSON for flexibility)
    proficiencies = Column(JSON, nullable=False, default=list)
    skill_proficiencies = Column(JSON, nullable=False, default=list)
    
    # Equipment and inventory (stored as JSON)
    inventory = Column(JSON, nullable=False, default=list)
    equipped_items = Column(JSON, nullable=False, default=dict)
    
    # Character status
    is_active = Column(Boolean, nullable=False, default=True)
    is_alive = Column(Boolean, nullable=False, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Character notes and backstory
    backstory = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="characters")
    story_arcs = relationship("StoryArc", back_populates="character")
    combat_encounters = relationship("CombatEncounter", back_populates="character")
    combat_participants = relationship("CombatParticipant", back_populates="character")
    character_quests = relationship("CharacterQuest", back_populates="character")
    journal_entries = relationship("JournalEntry", back_populates="character")
    discoveries = relationship("Discovery", back_populates="character")
    timeline_events = relationship("TimelineEvent", back_populates="character")
    
    @hybrid_property
    def strength_modifier(self):
        """Calculate strength modifier"""
        return (self.strength - 10) // 2
    
    @hybrid_property
    def dexterity_modifier(self):
        """Calculate dexterity modifier"""
        return (self.dexterity - 10) // 2
    
    @hybrid_property
    def constitution_modifier(self):
        """Calculate constitution modifier"""
        return (self.constitution - 10) // 2
    
    @hybrid_property
    def intelligence_modifier(self):
        """Calculate intelligence modifier"""
        return (self.intelligence - 10) // 2
    
    @hybrid_property
    def wisdom_modifier(self):
        """Calculate wisdom modifier"""
        return (self.wisdom - 10) // 2
    
    @hybrid_property
    def charisma_modifier(self):
        """Calculate charisma modifier"""
        return (self.charisma - 10) // 2
    
    @hybrid_property
    def proficiency_bonus(self):
        """Calculate proficiency bonus based on level"""
        return (self.level - 1) // 4 + 2
    
    def get_ability_modifier(self, ability: str) -> int:
        """Get modifier for a specific ability"""
        ability_map = {
            'strength': self.strength_modifier,
            'dexterity': self.dexterity_modifier,
            'constitution': self.constitution_modifier,
            'intelligence': self.intelligence_modifier,
            'wisdom': self.wisdom_modifier,
            'charisma': self.charisma_modifier
        }
        return ability_map.get(ability.lower(), 0)
    
    def get_saving_throw_bonus(self, ability: str) -> int:
        """Get saving throw bonus for an ability"""
        modifier = self.get_ability_modifier(ability)
        # Add proficiency bonus if proficient in this saving throw
        if f"{ability.lower()}_save" in self.proficiencies:
            modifier += self.proficiency_bonus
        return modifier
    
    def get_skill_bonus(self, skill: str) -> int:
        """Get skill bonus for a specific skill"""
        # Skill to ability mapping
        skill_abilities = {
            'acrobatics': 'dexterity',
            'animal_handling': 'wisdom',
            'arcana': 'intelligence',
            'athletics': 'strength',
            'deception': 'charisma',
            'history': 'intelligence',
            'insight': 'wisdom',
            'intimidation': 'charisma',
            'investigation': 'intelligence',
            'medicine': 'wisdom',
            'nature': 'intelligence',
            'perception': 'wisdom',
            'performance': 'charisma',
            'persuasion': 'charisma',
            'religion': 'intelligence',
            'sleight_of_hand': 'dexterity',
            'stealth': 'dexterity',
            'survival': 'wisdom'
        }
        
        ability = skill_abilities.get(skill.lower())
        if not ability:
            return 0
            
        modifier = self.get_ability_modifier(ability)
        # Add proficiency bonus if proficient in this skill
        if skill.lower() in self.skill_proficiencies:
            modifier += self.proficiency_bonus
        return modifier
    
    def level_up(self):
        """Handle character level up"""
        if self.level < 20:  # D&D 5e max level
            self.level += 1
            # Recalculate max HP (simplified - would need class-specific logic)
            hit_die = 8  # Default, should be class-specific
            hp_gain = max(1, hit_die // 2 + 1 + self.constitution_modifier)
            self.max_hit_points += hp_gain
            self.current_hit_points = self.max_hit_points  # Full heal on level up
    
    def take_damage(self, damage: int):
        """Apply damage to character"""
        self.current_hit_points = max(0, self.current_hit_points - damage)
        if self.current_hit_points == 0:
            self.is_alive = False
    
    def heal(self, amount: int):
        """Heal character"""
        if self.is_alive:
            self.current_hit_points = min(self.max_hit_points, self.current_hit_points + amount)
    
    def add_item(self, item: dict):
        """Add item to inventory"""
        if not isinstance(self.inventory, list):
            self.inventory = []
        self.inventory.append(item)
    
    def remove_item(self, item_name: str) -> bool:
        """Remove item from inventory"""
        if not isinstance(self.inventory, list):
            return False
        for i, item in enumerate(self.inventory):
            if item.get('name') == item_name:
                self.inventory.pop(i)
                return True
        return False
    
    def equip_item(self, item_name: str, slot: str):
        """Equip an item to a specific slot"""
        if not isinstance(self.equipped_items, dict):
            self.equipped_items = {}
        
        # Find item in inventory
        item = None
        for inv_item in self.inventory:
            if inv_item.get('name') == item_name:
                item = inv_item
                break
        
        if item:
            self.equipped_items[slot] = item
            return True
        return False
    
    def get_equipped_item(self, slot: str):
        """Get equipped item in a specific slot"""
        if not isinstance(self.equipped_items, dict):
            return None
        return self.equipped_items.get(slot)
    
    def __repr__(self):
        return f"<Character(id={self.id}, name='{self.name}', level={self.level}, class='{self.character_class}')>" 