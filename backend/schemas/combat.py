from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum

class CreatureTypeEnum(str, Enum):
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

class CombatStateEnum(str, Enum):
    """Combat encounter states"""
    NOT_STARTED = "not_started"
    INITIATIVE = "initiative"
    IN_PROGRESS = "in_progress"
    VICTORY = "victory"
    DEFEAT = "defeat"
    RETREAT = "retreat"

class ActionTypeEnum(str, Enum):
    """Types of combat actions"""
    ATTACK = "attack"
    SPELL = "spell"
    DEFEND = "defend"
    MOVE = "move"
    ITEM = "item"
    SPECIAL = "special"

class AttackSchema(BaseModel):
    """Schema for creature attacks"""
    name: str = Field(..., description="Name of the attack")
    type: str = Field(..., description="Type of attack (melee_weapon, ranged_weapon, spell)")
    attack_bonus: int = Field(..., description="Attack bonus to hit")
    damage: str = Field(..., description="Damage dice notation (e.g., '1d8+2')")
    damage_type: str = Field(..., description="Type of damage (slashing, piercing, etc.)")
    reach: str = Field(default="5 ft.", description="Reach of the attack")
    targets: int = Field(default=1, description="Number of targets")
    description: str = Field(..., description="Full attack description")

class SpecialAbilitySchema(BaseModel):
    """Schema for creature special abilities"""
    name: str = Field(..., description="Name of the ability")
    description: str = Field(..., description="Description of what the ability does")
    type: str = Field(..., description="Type of ability (passive, action, reaction)")
    usage: Optional[str] = Field(None, description="Usage limitation (e.g., 'recharge 5-6')")

class LootItemSchema(BaseModel):
    """Schema for loot items"""
    item: str = Field(..., description="Name of the item")
    amount: Optional[str] = Field(None, description="Amount if applicable (e.g., '2d6')")
    chance: Optional[float] = Field(None, description="Probability of dropping (0.0-1.0)")

class LootTableSchema(BaseModel):
    """Schema for creature loot tables"""
    guaranteed: List[LootItemSchema] = Field(default_factory=list, description="Items always dropped")
    possible: List[LootItemSchema] = Field(default_factory=list, description="Items with chance to drop")

# Enemy Template Schemas
class EnemyTemplateBase(BaseModel):
    """Base schema for enemy templates"""
    name: str = Field(..., max_length=100, description="Name of the creature")
    creature_type: CreatureTypeEnum = Field(..., description="Type of creature")
    size: str = Field(default="Medium", description="Size category")
    challenge_rating: float = Field(default=0.125, ge=0, description="Challenge rating for XP calculation")
    alignment: Optional[str] = Field(None, max_length=50, description="Creature alignment")
    
    # D&D 5e Ability Scores
    strength: int = Field(default=10, ge=1, le=30, description="Strength score")
    dexterity: int = Field(default=10, ge=1, le=30, description="Dexterity score")
    constitution: int = Field(default=10, ge=1, le=30, description="Constitution score")
    intelligence: int = Field(default=10, ge=1, le=30, description="Intelligence score")
    wisdom: int = Field(default=10, ge=1, le=30, description="Wisdom score")
    charisma: int = Field(default=10, ge=1, le=30, description="Charisma score")
    
    # Combat stats
    hit_points: int = Field(default=4, ge=1, description="Hit points")
    armor_class: int = Field(default=10, ge=1, description="Armor class")
    speed: str = Field(default="30 ft.", description="Movement speed")
    
    # Proficiencies
    proficiency_bonus: int = Field(default=2, ge=2, description="Proficiency bonus")
    saving_throws: Dict[str, int] = Field(default_factory=dict, description="Saving throw bonuses")
    skills: Dict[str, int] = Field(default_factory=dict, description="Skill bonuses")
    
    # Resistances and immunities
    damage_resistances: List[str] = Field(default_factory=list, description="Damage resistances")
    damage_immunities: List[str] = Field(default_factory=list, description="Damage immunities")
    condition_immunities: List[str] = Field(default_factory=list, description="Condition immunities")
    
    # Senses and languages
    senses: Dict[str, Any] = Field(default_factory=dict, description="Special senses")
    languages: List[str] = Field(default_factory=list, description="Languages known")
    
    # Combat abilities
    attacks: List[AttackSchema] = Field(default_factory=list, description="Available attacks")
    special_abilities: List[SpecialAbilitySchema] = Field(default_factory=list, description="Special abilities")
    
    # Loot and rewards
    loot_table: LootTableSchema = Field(default_factory=LootTableSchema, description="Loot table")
    xp_value: int = Field(default=25, ge=0, description="XP awarded for defeating")
    
    # AI hints
    tactics: Optional[str] = Field(None, description="AI behavior description")
    description: Optional[str] = Field(None, description="Flavor text")

class EnemyTemplateCreate(EnemyTemplateBase):
    """Schema for creating enemy templates"""
    pass

class EnemyTemplateUpdate(BaseModel):
    """Schema for updating enemy templates"""
    name: Optional[str] = Field(None, max_length=100)
    creature_type: Optional[CreatureTypeEnum] = None
    size: Optional[str] = None
    challenge_rating: Optional[float] = Field(None, ge=0)
    alignment: Optional[str] = Field(None, max_length=50)
    
    strength: Optional[int] = Field(None, ge=1, le=30)
    dexterity: Optional[int] = Field(None, ge=1, le=30)
    constitution: Optional[int] = Field(None, ge=1, le=30)
    intelligence: Optional[int] = Field(None, ge=1, le=30)
    wisdom: Optional[int] = Field(None, ge=1, le=30)
    charisma: Optional[int] = Field(None, ge=1, le=30)
    
    hit_points: Optional[int] = Field(None, ge=1)
    armor_class: Optional[int] = Field(None, ge=1)
    speed: Optional[str] = None
    
    proficiency_bonus: Optional[int] = Field(None, ge=2)
    saving_throws: Optional[Dict[str, int]] = None
    skills: Optional[Dict[str, int]] = None
    
    damage_resistances: Optional[List[str]] = None
    damage_immunities: Optional[List[str]] = None
    condition_immunities: Optional[List[str]] = None
    
    senses: Optional[Dict[str, Any]] = None
    languages: Optional[List[str]] = None
    
    attacks: Optional[List[AttackSchema]] = None
    special_abilities: Optional[List[SpecialAbilitySchema]] = None
    
    loot_table: Optional[LootTableSchema] = None
    xp_value: Optional[int] = Field(None, ge=0)
    
    tactics: Optional[str] = None
    description: Optional[str] = None

class EnemyTemplate(EnemyTemplateBase):
    """Schema for enemy template responses"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Calculated properties
    strength_modifier: int
    dexterity_modifier: int
    constitution_modifier: int
    intelligence_modifier: int
    wisdom_modifier: int
    charisma_modifier: int

# Combat Encounter Schemas
class InitiativeParticipant(BaseModel):
    """Schema for initiative order participants"""
    participant_id: int
    initiative: int
    type: str  # "character" or "enemy"
    name: str

class CombatActionLog(BaseModel):
    """Schema for combat action logs"""
    round: int
    turn: int
    participant: str
    action: str
    target: Optional[str] = None
    roll: Optional[int] = None
    damage: Optional[int] = None
    description: str
    timestamp: datetime

class CombatEncounterBase(BaseModel):
    """Base schema for combat encounters"""
    encounter_name: Optional[str] = Field(None, max_length=200)
    encounter_type: str = Field(default="random", description="Type of encounter")
    victory_conditions: Dict[str, Any] = Field(default_factory=dict, description="Victory conditions")

class CombatEncounterCreate(CombatEncounterBase):
    """Schema for creating combat encounters"""
    story_arc_id: int = Field(..., description="Associated story arc ID")
    character_id: int = Field(..., description="Character participating in combat")

class CombatEncounterUpdate(BaseModel):
    """Schema for updating combat encounters"""
    encounter_name: Optional[str] = Field(None, max_length=200)
    encounter_type: Optional[str] = None
    combat_state: Optional[CombatStateEnum] = None
    current_round: Optional[int] = Field(None, ge=0)
    current_turn: Optional[int] = Field(None, ge=0)
    victory_conditions: Optional[Dict[str, Any]] = None
    result: Optional[str] = None
    xp_awarded: Optional[int] = Field(None, ge=0)
    loot_awarded: Optional[List[Dict[str, Any]]] = None

class CombatEncounter(CombatEncounterBase):
    """Schema for combat encounter responses"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    story_arc_id: int
    character_id: int
    
    combat_state: CombatStateEnum
    current_round: int
    current_turn: int
    
    initiative_order: List[InitiativeParticipant]
    result: Optional[str] = None
    xp_awarded: int
    loot_awarded: List[Dict[str, Any]]
    
    combat_log: List[CombatActionLog]
    
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

# Combat Participant Schemas
class ConditionSchema(BaseModel):
    """Schema for status conditions"""
    condition: str = Field(..., description="Name of the condition")
    duration: int = Field(..., description="Duration in rounds")
    source: str = Field(..., description="Source of the condition")
    save_dc: Optional[int] = Field(None, description="Save DC to remove")
    save_ability: Optional[str] = Field(None, description="Ability for saving throw")

class ActionsTrackerSchema(BaseModel):
    """Schema for tracking action economy"""
    action: bool = False
    bonus_action: bool = False
    reaction: bool = False
    movement: int = 0

class CombatParticipantBase(BaseModel):
    """Base schema for combat participants"""
    participant_type: str = Field(..., description="Type of participant (character/enemy)")
    name: str = Field(..., max_length=100, description="Display name")
    max_hit_points: int = Field(..., ge=1, description="Maximum hit points")
    current_hit_points: int = Field(..., ge=0, description="Current hit points")
    armor_class: int = Field(..., ge=1, description="Armor class")
    initiative: int = Field(default=10, description="Initiative roll")

class CombatParticipantCreate(CombatParticipantBase):
    """Schema for creating combat participants"""
    combat_encounter_id: int = Field(..., description="Combat encounter ID")
    character_id: Optional[int] = Field(None, description="Character ID if participant is PC")
    enemy_template_id: Optional[int] = Field(None, description="Enemy template ID if participant is enemy")

class CombatParticipantUpdate(BaseModel):
    """Schema for updating combat participants"""
    name: Optional[str] = Field(None, max_length=100)
    max_hit_points: Optional[int] = Field(None, ge=1)
    current_hit_points: Optional[int] = Field(None, ge=0)
    armor_class: Optional[int] = Field(None, ge=1)
    initiative: Optional[int] = None
    is_active: Optional[bool] = None
    active_conditions: Optional[List[ConditionSchema]] = None
    temporary_hp: Optional[int] = Field(None, ge=0)
    position_x: Optional[int] = None
    position_y: Optional[int] = None
    movement_remaining: Optional[int] = Field(None, ge=0)
    actions_taken: Optional[ActionsTrackerSchema] = None

class CombatParticipant(CombatParticipantBase):
    """Schema for combat participant responses"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    combat_encounter_id: int
    character_id: Optional[int] = None
    enemy_template_id: Optional[int] = None
    
    is_active: bool
    active_conditions: List[ConditionSchema]
    temporary_hp: int
    
    position_x: int
    position_y: int
    movement_remaining: int
    
    actions_taken: ActionsTrackerSchema
    
    joined_at: datetime
    eliminated_at: Optional[datetime] = None

# Request/Response Schemas
class DamageRequest(BaseModel):
    """Request schema for applying damage"""
    participant_id: int = Field(..., description="ID of participant taking damage")
    damage: int = Field(..., ge=0, description="Amount of damage")
    damage_type: Optional[str] = Field(None, description="Type of damage")

class HealingRequest(BaseModel):
    """Request schema for healing"""
    participant_id: int = Field(..., description="ID of participant being healed")
    amount: int = Field(..., ge=0, description="Amount of healing")

class AddConditionRequest(BaseModel):
    """Request schema for adding conditions"""
    participant_id: int = Field(..., description="ID of participant")
    condition: ConditionSchema = Field(..., description="Condition to add")

class CombatActionRequest(BaseModel):
    """Request schema for combat actions"""
    participant_id: int = Field(..., description="Acting participant ID")
    action_type: ActionTypeEnum = Field(..., description="Type of action")
    target_id: Optional[int] = Field(None, description="Target participant ID")
    details: Dict[str, Any] = Field(default_factory=dict, description="Action-specific details")

class InitiativeRollRequest(BaseModel):
    """Request schema for rolling initiative"""
    participants: List[int] = Field(..., description="List of participant IDs")

# Response Schemas
class CombatActionResponse(BaseModel):
    """Response schema for combat actions"""
    success: bool
    description: str
    damage_dealt: Optional[int] = None
    healing_done: Optional[int] = None
    conditions_applied: List[str] = Field(default_factory=list)
    participant_eliminated: bool = False

class InitiativeRollResponse(BaseModel):
    """Response schema for initiative rolls"""
    initiative_order: List[InitiativeParticipant]
    combat_state: CombatStateEnum

class CombatSummary(BaseModel):
    """Summary schema for combat encounters"""
    encounter_id: int
    encounter_name: Optional[str]
    state: CombatStateEnum
    current_round: int
    participants_active: int
    participants_total: int
    character_hp: int
    character_max_hp: int
    
class EnemyTemplateWithStats(EnemyTemplate):
    """Enemy template with calculated combat stats"""
    passive_perception: int
    initiative_bonus: int
    hit_dice: str
    
    class Config:
        from_attributes = True 