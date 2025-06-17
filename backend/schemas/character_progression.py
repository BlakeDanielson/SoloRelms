from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class ExperienceGainRequest(BaseModel):
    amount: int = Field(..., description="Amount of XP to add", ge=1)
    reason: str = Field(..., description="Reason for XP gain")

class LevelUpRequest(BaseModel):
    chosen_features: List[str] = Field(default=[], description="Class features chosen during level up")

class SkillUpgradeRequest(BaseModel):
    skill_id: str = Field(..., description="ID of the skill to upgrade")

class AttributeUpgradeRequest(BaseModel):
    attribute_name: str = Field(..., description="Name of the attribute to upgrade")

class Skill(BaseModel):
    id: str
    name: str
    current_level: int
    max_level: int
    xp_current: int
    xp_required: int
    description: str
    bonuses: List[str] = []
    icon: Optional[str] = None

class Achievement(BaseModel):
    id: str
    name: str
    description: str
    icon: str
    category: str
    unlocked: bool = False
    unlocked_at: Optional[datetime] = None
    xp_reward: int = 0
    progress_current: int = 0
    progress_required: int = 1
    hidden: bool = False

class LevelProgression(BaseModel):
    level: int
    xp_required: int
    hit_points_gained: int
    proficiency_bonus: int
    features_gained: List[str] = []
    spell_slots: Optional[Dict[int, int]] = None

class CharacterProgressionResponse(BaseModel):
    character_id: int
    current_level: int
    current_xp: int
    xp_to_next_level: int
    available_attribute_points: int = 0
    available_skill_points: int = 0
    skills: List[Skill] = []
    achievements: List[Achievement] = []
    level_progression: List[LevelProgression] = []
    abilities: Dict[str, int] = {
        "strength": 10,
        "dexterity": 10, 
        "constitution": 10,
        "intelligence": 10,
        "wisdom": 10,
        "charisma": 10
    }

    class Config:
        from_attributes = True

class AchievementResponse(BaseModel):
    id: str
    name: str
    description: str
    icon: str
    category: str
    unlocked: bool = False
    unlocked_at: Optional[datetime] = None
    xp_reward: int = 0
    progress_current: int = 0
    progress_required: int = 1

    class Config:
        from_attributes = True 