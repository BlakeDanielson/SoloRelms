from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum

class AdvantageType(str, Enum):
    """Advantage/disadvantage types for D&D 5e"""
    NORMAL = "normal"
    ADVANTAGE = "advantage"
    DISADVANTAGE = "disadvantage"

class DiceRollRequest(BaseModel):
    """Request schema for rolling dice"""
    notation: str = Field(..., description="Dice notation (e.g., '2d6+3', '1d20', '4d6kh3')")
    advantage_type: AdvantageType = Field(default=AdvantageType.NORMAL, description="Advantage/disadvantage modifier")
    description: Optional[str] = Field(None, description="Optional description of the roll")

class DiceRollResponse(BaseModel):
    """Response schema for dice roll results"""
    total: int = Field(..., description="Total result of the dice roll")
    individual_rolls: List[int] = Field(..., description="Individual die results")
    dice_notation: str = Field(..., description="Original dice notation used")
    modifier: int = Field(default=0, description="Modifier applied to the roll")
    advantage_type: AdvantageType = Field(default=AdvantageType.NORMAL, description="Advantage/disadvantage type")
    dropped_dice: Optional[List[int]] = Field(None, description="Dice that were dropped (for advantage/keep highest/etc)")
    description: str = Field(default="", description="Description of the roll")

class AttackRollRequest(BaseModel):
    """Request schema for attack rolls"""
    attack_bonus: int = Field(..., description="Attack bonus to add to the roll")
    damage_notation: str = Field(..., description="Damage dice notation (e.g., '1d8+3')")
    target_ac: int = Field(..., description="Target's Armor Class")
    advantage_type: AdvantageType = Field(default=AdvantageType.NORMAL, description="Advantage/disadvantage modifier")
    critical_range: int = Field(default=20, description="Critical hit range (default 20, some weapons 19-20)")
    description: Optional[str] = Field(None, description="Optional description of the attack")

class AttackRollResponse(BaseModel):
    """Response schema for attack roll results"""
    attack_roll: DiceRollResponse = Field(..., description="The attack roll result")
    damage_roll: Optional[DiceRollResponse] = Field(None, description="Damage roll result (if hit)")
    is_critical: bool = Field(..., description="Whether this was a critical hit")
    is_hit: bool = Field(..., description="Whether the attack hit")
    target_ac: int = Field(..., description="Target's Armor Class")
    description: str = Field(default="", description="Description of the attack result")

class AbilityScoreRollResponse(BaseModel):
    """Response schema for ability score generation"""
    scores: Dict[str, DiceRollResponse] = Field(..., description="Ability scores with roll details")

class SavingThrowRequest(BaseModel):
    """Request schema for saving throws"""
    ability_modifier: int = Field(..., description="Ability modifier for the save")
    proficiency_bonus: int = Field(default=0, description="Proficiency bonus (if proficient)")
    advantage_type: AdvantageType = Field(default=AdvantageType.NORMAL, description="Advantage/disadvantage modifier")
    description: Optional[str] = Field(None, description="Description of the saving throw")

class SkillCheckRequest(BaseModel):
    """Request schema for skill checks"""
    ability_modifier: int = Field(..., description="Relevant ability modifier")
    proficiency_bonus: int = Field(default=0, description="Proficiency bonus (if proficient)")
    advantage_type: AdvantageType = Field(default=AdvantageType.NORMAL, description="Advantage/disadvantage modifier")
    skill_name: Optional[str] = Field(None, description="Name of the skill being checked")
    dc: Optional[int] = Field(None, description="Difficulty Class (optional)")

class SkillCheckResponse(BaseModel):
    """Response schema for skill check results"""
    roll_result: DiceRollResponse = Field(..., description="The skill check roll result")
    skill_name: Optional[str] = Field(None, description="Name of the skill checked")
    dc: Optional[int] = Field(None, description="Difficulty Class")
    success: Optional[bool] = Field(None, description="Whether the check succeeded (if DC provided)")

class InitiativeRollRequest(BaseModel):
    """Request schema for initiative rolls"""
    dexterity_modifier: int = Field(..., description="Dexterity modifier")
    advantage_type: AdvantageType = Field(default=AdvantageType.NORMAL, description="Advantage/disadvantage modifier")

class HitPointsRollRequest(BaseModel):
    """Request schema for rolling hit points"""
    hit_die: int = Field(..., description="Hit die size (4, 6, 8, 10, 12)")
    constitution_modifier: int = Field(..., description="Constitution modifier")
    level: int = Field(default=1, description="Character level (affects HP calculation)")

class MultipleDiceRollRequest(BaseModel):
    """Request schema for rolling multiple dice at once"""
    rolls: List[DiceRollRequest] = Field(..., description="List of dice rolls to perform")

class MultipleDiceRollResponse(BaseModel):
    """Response schema for multiple dice rolls"""
    results: List[DiceRollResponse] = Field(..., description="Results of all dice rolls")
    total_sum: int = Field(..., description="Sum of all roll totals")

class DicePoolRequest(BaseModel):
    """Request schema for dice pool systems (like Shadowrun, World of Darkness)"""
    num_dice: int = Field(..., description="Number of dice in the pool")
    die_size: int = Field(default=6, description="Size of each die")
    target_number: int = Field(..., description="Target number for success")
    exploding: bool = Field(default=False, description="Whether dice explode on max roll")

class DicePoolResponse(BaseModel):
    """Response schema for dice pool results"""
    individual_rolls: List[int] = Field(..., description="All individual die results")
    successes: int = Field(..., description="Number of successes")
    failures: int = Field(..., description="Number of failures")
    total_dice: int = Field(..., description="Total number of dice rolled")
    exploded_dice: List[int] = Field(default=[], description="Dice that exploded")

# Common dice roll shortcuts
class QuickRollRequest(BaseModel):
    """Request schema for common quick rolls"""
    roll_type: str = Field(..., description="Type of roll (d20, d6, d8, d10, d12, d100, percentile)")
    modifier: int = Field(default=0, description="Modifier to add to the roll")
    advantage_type: AdvantageType = Field(default=AdvantageType.NORMAL, description="Advantage/disadvantage modifier")

# Dice validation schemas
class DiceNotationValidationRequest(BaseModel):
    """Request to validate dice notation"""
    notation: str = Field(..., description="Dice notation to validate")

class DiceNotationValidationResponse(BaseModel):
    """Response for dice notation validation"""
    is_valid: bool = Field(..., description="Whether the notation is valid")
    parsed_notation: Optional[Dict] = Field(None, description="Parsed components if valid")
    error_message: Optional[str] = Field(None, description="Error message if invalid") 