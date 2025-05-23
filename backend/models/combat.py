from sqlalchemy import Column, Integer, String, JSON, DateTime, Boolean, ForeignKey, Text, Enum, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime
from enum import Enum as PyEnum
try:
    from ..database import Base
except ImportError:
    # Fallback for when running from alembic or direct execution
    from database import Base

class CreatureType(PyEnum):
    """D&D 5e creature types"""
    ABERRATION = "aberration"
    BEAST = "beast"
    CELESTIAL = "celestial"
    CONSTRUCT = "construct"
    DRAGON = "dragon"
    ELEMENTAL = "elemental"
    FEY = "fey"
    FIEND = "fiend"
    GIANT = "giant"
    HUMANOID = "humanoid"
    MONSTROSITY = "monstrosity"
    OOZE = "ooze"
    PLANT = "plant"
    UNDEAD = "undead"

class CombatState(PyEnum):
    """Combat encounter states"""
    NOT_STARTED = "not_started"
    INITIATIVE = "initiative"
    IN_PROGRESS = "in_progress"
    VICTORY = "victory"
    DEFEAT = "defeat"
    RETREAT = "retreat"

class ActionType(PyEnum):
    """Types of combat actions"""
    ATTACK = "attack"
    SPELL = "spell"
    DEFEND = "defend"
    MOVE = "move"
    ITEM = "item"
    SPECIAL = "special"

class EnemyTemplate(Base):
    """
    Template for enemy creatures with D&D 5e stats and abilities
    Used to spawn enemies in combat encounters
    """
    __tablename__ = "enemy_templates"
    
    # Primary identification
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    creature_type = Column(Enum(CreatureType), nullable=False)
    
    # Basic creature info
    size = Column(String(20), nullable=False, default="Medium")  # Tiny, Small, Medium, Large, etc.
    challenge_rating = Column(Float, nullable=False, default=0.125)  # CR for XP calculation
    alignment = Column(String(50), nullable=True)
    
    # D&D 5e Ability Scores
    strength = Column(Integer, nullable=False, default=10)
    dexterity = Column(Integer, nullable=False, default=10)
    constitution = Column(Integer, nullable=False, default=10)
    intelligence = Column(Integer, nullable=False, default=10)
    wisdom = Column(Integer, nullable=False, default=10)
    charisma = Column(Integer, nullable=False, default=10)
    
    # Combat stats
    hit_points = Column(Integer, nullable=False, default=4)
    armor_class = Column(Integer, nullable=False, default=10)
    speed = Column(String(50), nullable=False, default="30 ft.")
    
    # Proficiency and skills
    proficiency_bonus = Column(Integer, nullable=False, default=2)
    saving_throws = Column(JSON, default=dict)  # {"dexterity": 4, "constitution": 2}
    skills = Column(JSON, default=dict)  # {"stealth": 4, "perception": 2}
    
    # Resistances and immunities
    damage_resistances = Column(JSON, default=list)  # ["fire", "cold"]
    damage_immunities = Column(JSON, default=list)  # ["poison", "necrotic"]
    condition_immunities = Column(JSON, default=list)  # ["charmed", "frightened"]
    
    # Senses and languages
    senses = Column(JSON, default=dict)  # {"darkvision": 60, "passive_perception": 12}
    languages = Column(JSON, default=list)  # ["Common", "Orcish"]
    
    # Combat abilities and actions
    attacks = Column(JSON, default=list)
    """
    Example attacks structure:
    [
        {
            "name": "Longsword",
            "type": "melee_weapon",
            "attack_bonus": 4,
            "damage": "1d8+2",
            "damage_type": "slashing",
            "reach": "5 ft.",
            "targets": 1,
            "description": "Melee Weapon Attack: +4 to hit, reach 5 ft., one target."
        }
    ]
    """
    
    special_abilities = Column(JSON, default=list)
    """
    Example special_abilities structure:
    [
        {
            "name": "Pack Tactics",
            "description": "The wolf has advantage on attack rolls against a creature if at least one ally is within 5 feet of the target.",
            "type": "passive"
        }
    ]
    """
    
    # Loot and rewards
    loot_table = Column(JSON, default=dict)
    """
    Example loot_table structure:
    {
        "guaranteed": [
            {"item": "gold_pieces", "amount": "2d6"}
        ],
        "possible": [
            {"item": "leather_armor", "chance": 0.3},
            {"item": "shortsword", "chance": 0.2}
        ]
    }
    """
    
    xp_value = Column(Integer, nullable=False, default=25)  # XP awarded for defeating
    
    # AI behavior hints
    tactics = Column(Text, nullable=True)  # AI behavior description
    description = Column(Text, nullable=True)  # Flavor text for the creature
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    combat_participants = relationship("CombatParticipant", back_populates="enemy_template")
    
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
        if self.saving_throws and ability.lower() in self.saving_throws:
            return self.saving_throws[ability.lower()]
        return self.get_ability_modifier(ability)
    
    def get_skill_bonus(self, skill: str) -> int:
        """Get skill bonus for a specific skill"""
        if self.skills and skill.lower() in self.skills:
            return self.skills[skill.lower()]
        
        # Default skill to ability mapping
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
        if ability:
            return self.get_ability_modifier(ability)
        return 0

class CombatEncounter(Base):
    """
    Individual combat encounter tracking initiative, participants, and state
    """
    __tablename__ = "combat_encounters"
    
    # Primary identification
    id = Column(Integer, primary_key=True, index=True)
    story_arc_id = Column(Integer, ForeignKey("story_arcs.id"), nullable=False, index=True)
    character_id = Column(Integer, ForeignKey("characters.id"), nullable=False, index=True)
    
    # Combat metadata
    encounter_name = Column(String(200), nullable=True)
    encounter_type = Column(String(50), nullable=False, default="random")  # "scripted", "random", "boss"
    
    # Combat state
    combat_state = Column(Enum(CombatState), default=CombatState.NOT_STARTED, nullable=False)
    current_round = Column(Integer, default=0)
    current_turn = Column(Integer, default=0)  # Index of current participant
    
    # Initiative order and participants
    initiative_order = Column(JSON, default=list)  # List of participant IDs in initiative order
    """
    Example initiative_order:
    [
        {"participant_id": 1, "initiative": 18, "type": "character"},
        {"participant_id": 2, "initiative": 12, "type": "enemy"},
        {"participant_id": 3, "initiative": 8, "type": "enemy"}
    ]
    """
    
    # Combat results and rewards
    victory_conditions = Column(JSON, default=dict)  # Conditions for victory/defeat
    result = Column(String(20), nullable=True)  # "victory", "defeat", "retreat", "stalemate"
    xp_awarded = Column(Integer, default=0)
    loot_awarded = Column(JSON, default=list)
    
    # Combat log for AI context and replay
    combat_log = Column(JSON, default=list)
    """
    Example combat_log:
    [
        {
            "round": 1,
            "turn": 1,
            "participant": "character",
            "action": "attack",
            "target": "goblin_1",
            "roll": 15,
            "damage": 6,
            "description": "Character swings sword at Goblin, hits for 6 damage"
        }
    ]
    """
    
    # Timing
    started_at = Column(DateTime(timezone=True), nullable=True)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    story_arc = relationship("StoryArc")
    character = relationship("Character")
    participants = relationship("CombatParticipant", back_populates="combat_encounter", cascade="all, delete-orphan")
    
    def start_combat(self):
        """Initialize combat encounter"""
        self.combat_state = CombatState.INITIATIVE
        self.started_at = datetime.utcnow()
        self.current_round = 1
        self.current_turn = 0
    
    def advance_turn(self):
        """Move to the next participant's turn"""
        if self.combat_state == CombatState.IN_PROGRESS:
            self.current_turn += 1
            if self.current_turn >= len(self.initiative_order):
                self.current_turn = 0
                self.current_round += 1
    
    def end_combat(self, result: str, xp_awarded: int = 0, loot: list = None):
        """End the combat encounter"""
        self.combat_state = CombatState.VICTORY if result == "victory" else CombatState.DEFEAT
        self.result = result
        self.xp_awarded = xp_awarded
        self.loot_awarded = loot or []
        self.ended_at = datetime.utcnow()
    
    def log_action(self, action_data: dict):
        """Add an action to the combat log"""
        if self.combat_log is None:
            self.combat_log = []
        
        action_data.update({
            "round": self.current_round,
            "turn": self.current_turn,
            "timestamp": datetime.utcnow().isoformat()
        })
        self.combat_log.append(action_data)

class CombatParticipant(Base):
    """
    Individual participant in a combat encounter (character or enemy instance)
    """
    __tablename__ = "combat_participants"
    
    # Primary identification
    id = Column(Integer, primary_key=True, index=True)
    combat_encounter_id = Column(Integer, ForeignKey("combat_encounters.id"), nullable=False, index=True)
    
    # Participant identification
    participant_type = Column(String(20), nullable=False)  # "character" or "enemy"
    character_id = Column(Integer, ForeignKey("characters.id"), nullable=True)  # If participant is player character
    enemy_template_id = Column(Integer, ForeignKey("enemy_templates.id"), nullable=True)  # If participant is enemy
    
    # Instance-specific data (can differ from template)
    name = Column(String(100), nullable=False)  # "Goblin Warrior #1"
    max_hit_points = Column(Integer, nullable=False)
    current_hit_points = Column(Integer, nullable=False)
    armor_class = Column(Integer, nullable=False)
    
    # Combat state
    initiative = Column(Integer, nullable=False, default=10)
    is_active = Column(Boolean, default=True)  # False if unconscious/dead
    
    # Temporary effects and conditions
    active_conditions = Column(JSON, default=list)  # ["poisoned", "grappled"]
    temporary_hp = Column(Integer, default=0)
    """
    Example active_conditions:
    [
        {
            "condition": "poisoned",
            "duration": 3,
            "source": "poison_dart",
            "save_dc": 12,
            "save_ability": "constitution"
        }
    ]
    """
    
    # Position and movement
    position_x = Column(Integer, default=0)  # For tactical combat if needed
    position_y = Column(Integer, default=0)
    movement_remaining = Column(Integer, default=30)  # Feet of movement left this turn
    
    # Actions taken this turn
    actions_taken = Column(JSON, default=dict)  # Track action economy
    """
    Example actions_taken:
    {
        "action": true,
        "bonus_action": false,
        "reaction": false,
        "movement": 15
    }
    """
    
    # Timestamps
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    eliminated_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    combat_encounter = relationship("CombatEncounter", back_populates="participants")
    character = relationship("Character")
    enemy_template = relationship("EnemyTemplate", back_populates="combat_participants")
    
    def take_damage(self, damage: int):
        """Apply damage to participant"""
        # Apply temporary HP first
        if self.temporary_hp > 0:
            temp_damage = min(damage, self.temporary_hp)
            self.temporary_hp -= temp_damage
            damage -= temp_damage
        
        # Apply remaining damage to current HP
        self.current_hit_points = max(0, self.current_hit_points - damage)
        
        # Check if eliminated
        if self.current_hit_points == 0:
            self.is_active = False
            self.eliminated_at = datetime.utcnow()
    
    def heal(self, amount: int):
        """Heal the participant"""
        if self.is_active:
            self.current_hit_points = min(self.max_hit_points, self.current_hit_points + amount)
    
    def add_condition(self, condition_data: dict):
        """Add a status condition"""
        if self.active_conditions is None:
            self.active_conditions = []
        self.active_conditions.append(condition_data)
    
    def remove_condition(self, condition_name: str):
        """Remove a status condition"""
        if self.active_conditions:
            self.active_conditions = [
                cond for cond in self.active_conditions 
                if cond.get("condition") != condition_name
            ]
    
    def reset_turn_actions(self):
        """Reset action economy for new turn"""
        self.actions_taken = {
            "action": False,
            "bonus_action": False,
            "reaction": False,
            "movement": 0
        }
        self.movement_remaining = 30  # Default movement speed
    
    def use_action(self, action_type: str) -> bool:
        """Use an action if available"""
        if self.actions_taken is None:
            self.reset_turn_actions()
        
        if action_type in self.actions_taken and not self.actions_taken[action_type]:
            self.actions_taken[action_type] = True
            return True
        return False 