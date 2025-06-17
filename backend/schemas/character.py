from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

# Base schema for character attributes
class CharacterBase(BaseModel):
    """Base character schema with common fields"""
    name: str = Field(..., min_length=1, max_length=100, description="Character name")
    race: str = Field(..., min_length=1, max_length=50, description="Character race")
    character_class: str = Field(..., min_length=1, max_length=50, description="Character class")
    background: Optional[str] = Field(None, max_length=50, description="Character background")
    
    # Ability scores (3-20 range for D&D 5e)
    strength: int = Field(..., ge=3, le=20, description="Strength ability score")
    dexterity: int = Field(..., ge=3, le=20, description="Dexterity ability score")
    constitution: int = Field(..., ge=3, le=20, description="Constitution ability score")
    intelligence: int = Field(..., ge=3, le=20, description="Intelligence ability score")
    wisdom: int = Field(..., ge=3, le=20, description="Wisdom ability score")
    charisma: int = Field(..., ge=3, le=20, description="Charisma ability score")
    
    backstory: Optional[str] = Field(None, description="Character backstory")
    notes: Optional[str] = Field(None, description="Character notes")

# Schema for creating a new character
class CharacterCreate(CharacterBase):
    """Schema for character creation"""
    user_id: str = Field(..., description="User ID from authentication system")
    
    # Optional fields with defaults
    level: int = Field(1, ge=1, le=20, description="Character level")
    experience_points: int = Field(0, ge=0, description="Experience points")
    max_hit_points: int = Field(8, ge=1, description="Maximum hit points")
    current_hit_points: Optional[int] = Field(None, ge=0, description="Current hit points")
    armor_class: int = Field(10, ge=1, description="Armor class")
    
    proficiencies: List[str] = Field(default_factory=list, description="Character proficiencies")
    skill_proficiencies: List[str] = Field(default_factory=list, description="Skill proficiencies")
    inventory: List[Dict[str, Any]] = Field(default_factory=list, description="Character inventory")
    equipped_items: Dict[str, Dict[str, Any]] = Field(default_factory=dict, description="Equipped items")

# Schema for updating a character
class CharacterUpdate(BaseModel):
    """Schema for character updates"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    race: Optional[str] = Field(None, min_length=1, max_length=50)
    character_class: Optional[str] = Field(None, min_length=1, max_length=50)
    background: Optional[str] = Field(None, max_length=50)
    
    # Ability scores
    strength: Optional[int] = Field(None, ge=3, le=20)
    dexterity: Optional[int] = Field(None, ge=3, le=20)
    constitution: Optional[int] = Field(None, ge=3, le=20)
    intelligence: Optional[int] = Field(None, ge=3, le=20)
    wisdom: Optional[int] = Field(None, ge=3, le=20)
    charisma: Optional[int] = Field(None, ge=3, le=20)
    
    # Progression
    level: Optional[int] = Field(None, ge=1, le=20)
    experience_points: Optional[int] = Field(None, ge=0)
    
    # Health
    max_hit_points: Optional[int] = Field(None, ge=1)
    current_hit_points: Optional[int] = Field(None, ge=0)
    armor_class: Optional[int] = Field(None, ge=1)
    
    # Lists and dicts
    proficiencies: Optional[List[str]] = None
    skill_proficiencies: Optional[List[str]] = None
    inventory: Optional[List[Dict[str, Any]]] = None
    equipped_items: Optional[Dict[str, Dict[str, Any]]] = None
    
    # Status
    is_active: Optional[bool] = None
    is_alive: Optional[bool] = None
    
    # Text fields
    backstory: Optional[str] = None
    notes: Optional[str] = None

# Schema for character response (includes all fields)
class Character(CharacterBase):
    """Complete character schema for responses"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="Character ID")
    user_id: str = Field(..., description="User ID from authentication system")
    
    # Progression
    level: int = Field(..., description="Character level")
    experience_points: int = Field(..., description="Experience points")
    
    # Health
    max_hit_points: int = Field(..., description="Maximum hit points")
    current_hit_points: int = Field(..., description="Current hit points")
    armor_class: int = Field(..., description="Armor class")
    
    # Lists and dicts
    proficiencies: List[str] = Field(..., description="Character proficiencies")
    skill_proficiencies: List[str] = Field(..., description="Skill proficiencies")
    inventory: List[Dict[str, Any]] = Field(..., description="Character inventory")
    equipped_items: Dict[str, Dict[str, Any]] = Field(..., description="Equipped items")
    
    # Status
    is_active: bool = Field(..., description="Whether character is active")
    is_alive: bool = Field(..., description="Whether character is alive")
    
    # Timestamps
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

# Schema for character with calculated stats
class CharacterWithStats(Character):
    """Character schema with calculated modifiers and bonuses"""
    
    # Ability modifiers
    strength_modifier: int = Field(..., description="Strength modifier")
    dexterity_modifier: int = Field(..., description="Dexterity modifier")
    constitution_modifier: int = Field(..., description="Constitution modifier")
    intelligence_modifier: int = Field(..., description="Intelligence modifier")
    wisdom_modifier: int = Field(..., description="Wisdom modifier")
    charisma_modifier: int = Field(..., description="Charisma modifier")
    
    # Derived stats
    proficiency_bonus: int = Field(..., description="Proficiency bonus based on level")

# Schema for character list responses
class CharacterList(BaseModel):
    """Schema for character list responses"""
    characters: List[Character] = Field(..., description="List of characters")
    total: int = Field(..., description="Total number of characters")

# Schema for character creation with rolled stats
class CharacterWithRolledStats(BaseModel):
    """Schema for character creation with auto-rolled stats"""
    user_id: str = Field(..., description="User ID from authentication system")
    name: str = Field(..., min_length=1, max_length=100, description="Character name")
    race: str = Field(..., min_length=1, max_length=50, description="Character race")
    character_class: str = Field(..., min_length=1, max_length=50, description="Character class")
    background: Optional[str] = Field(None, max_length=50, description="Character background")
    backstory: Optional[str] = Field(None, description="Character backstory")
    
    # Stats will be auto-rolled by the backend

# Schema for stat rolling response
class StatRollResponse(BaseModel):
    """Schema for stat rolling response"""
    strength: int = Field(..., description="Rolled strength score")
    dexterity: int = Field(..., description="Rolled dexterity score")
    constitution: int = Field(..., description="Rolled constitution score")
    intelligence: int = Field(..., description="Rolled intelligence score")
    wisdom: int = Field(..., description="Rolled wisdom score")
    charisma: int = Field(..., description="Rolled charisma score")
    rolls: List[List[int]] = Field(..., description="Individual dice rolls for each stat")

# Schema for inventory item
class InventoryItem(BaseModel):
    """Schema for inventory items"""
    name: str = Field(..., description="Item name")
    description: Optional[str] = Field(None, description="Item description")
    type: str = Field(..., description="Item type (weapon, armor, tool, etc.)")
    quantity: int = Field(1, ge=1, description="Item quantity")
    weight: Optional[float] = Field(None, ge=0, description="Item weight")
    value: Optional[int] = Field(None, ge=0, description="Item value in gold pieces")
    properties: Optional[Dict[str, Any]] = Field(None, description="Item properties")

# Schema for equipment slot
class EquipmentSlot(BaseModel):
    """Schema for equipment slots"""
    slot: str = Field(..., description="Equipment slot name")
    item: Optional[InventoryItem] = Field(None, description="Equipped item")

# Schema for character stats summary
class CharacterStatsSummary(BaseModel):
    """Schema for character stats summary"""
    name: str = Field(..., description="Character name")
    level: int = Field(..., description="Character level")
    character_class: str = Field(..., description="Character class")
    race: str = Field(..., description="Character race")
    hit_points: str = Field(..., description="Current/Max HP")
    armor_class: int = Field(..., description="Armor class")
    proficiency_bonus: int = Field(..., description="Proficiency bonus")
    
    abilities: Dict[str, int] = Field(..., description="Ability scores and modifiers")
    saving_throws: Dict[str, int] = Field(..., description="Saving throw bonuses")
    skills: Dict[str, int] = Field(..., description="Skill bonuses")

# Schema for quick character creation (auto-generates stats)
class QuickCharacterCreate(BaseModel):
    """Schema for quick character creation with auto-generated stats"""
    name: str = Field(..., min_length=1, max_length=100, description="Character name")
    race: str = Field(..., min_length=1, max_length=50, description="Character race")
    character_class: str = Field(..., min_length=1, max_length=50, description="Character class")
    background: Optional[str] = Field(None, max_length=50, description="Character background")
    backstory: Optional[str] = Field(None, description="Character backstory")
    
    # Optional fields with defaults
    level: int = Field(1, ge=1, le=20, description="Character level")
    experience_points: int = Field(0, ge=0, description="Experience points")

# Schema for creating a new character 