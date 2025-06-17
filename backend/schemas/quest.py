"""
Pydantic schemas for quest system including quests, objectives, rewards, and progress tracking.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
from enum import Enum


class QuestType(str, Enum):
    """Valid quest types."""
    main = "main"
    side = "side"
    daily = "daily"
    hidden = "hidden"


class DifficultyLevel(str, Enum):
    """Valid difficulty levels."""
    easy = "easy"
    medium = "medium"
    hard = "hard"
    legendary = "legendary"


class ObjectiveType(str, Enum):
    """Valid objective types."""
    kill = "kill"
    collect = "collect"
    visit = "visit"
    talk = "talk"
    deliver = "deliver"
    explore = "explore"
    survive = "survive"


class RewardType(str, Enum):
    """Valid reward types."""
    xp = "xp"
    gold = "gold"
    item = "item"
    ability = "ability"


class QuestStatus(str, Enum):
    """Valid quest status values."""
    active = "active"
    completed = "completed"
    failed = "failed"
    abandoned = "abandoned"


# Quest Objective Schemas
class QuestObjectiveBase(BaseModel):
    """Base schema for quest objectives."""
    description: str = Field(..., min_length=1, max_length=500, description="Objective description")
    objective_type: ObjectiveType = Field(..., description="Type of objective")
    target_type: Optional[str] = Field(None, max_length=100, description="Type of target (monster, item, etc.)")
    target_id: Optional[str] = Field(None, max_length=100, description="ID or name of target")
    required_amount: int = Field(default=1, ge=1, le=1000, description="Required amount to complete")
    order_index: int = Field(default=0, ge=0, description="Order in quest")


class QuestObjectiveCreate(QuestObjectiveBase):
    """Schema for creating quest objectives."""
    pass


class QuestObjectiveUpdate(BaseModel):
    """Schema for updating quest objectives."""
    description: Optional[str] = Field(None, min_length=1, max_length=500)
    objective_type: Optional[ObjectiveType] = None
    target_type: Optional[str] = Field(None, max_length=100)
    target_id: Optional[str] = Field(None, max_length=100)
    required_amount: Optional[int] = Field(None, ge=1, le=1000)
    order_index: Optional[int] = Field(None, ge=0)


class QuestObjectiveResponse(QuestObjectiveBase):
    """Schema for quest objective responses."""
    id: int
    quest_id: int

    class Config:
        from_attributes = True


# Quest Reward Schemas
class QuestRewardBase(BaseModel):
    """Base schema for quest rewards."""
    reward_type: RewardType = Field(..., description="Type of reward")
    reward_id: Optional[str] = Field(None, max_length=100, description="ID of specific reward item/ability")
    amount: int = Field(default=1, ge=1, description="Amount of reward")
    rarity: str = Field(default="common", max_length=50, description="Rarity of reward")

    @validator('rarity')
    def validate_rarity(cls, v):
        """Validate rarity values."""
        valid_rarities = ['common', 'uncommon', 'rare', 'epic', 'legendary']
        if v.lower() not in valid_rarities:
            raise ValueError(f"Rarity must be one of: {valid_rarities}")
        return v.lower()


class QuestRewardCreate(QuestRewardBase):
    """Schema for creating quest rewards."""
    pass


class QuestRewardResponse(QuestRewardBase):
    """Schema for quest reward responses."""
    id: int
    quest_id: int

    class Config:
        from_attributes = True


# Quest Schemas
class QuestBase(BaseModel):
    """Base schema for quests."""
    title: str = Field(..., min_length=1, max_length=255, description="Quest title")
    description: str = Field(..., min_length=1, description="Quest description")
    quest_type: QuestType = Field(..., description="Type of quest")
    difficulty_level: DifficultyLevel = Field(..., description="Difficulty level")
    required_level: int = Field(default=1, ge=1, le=100, description="Required character level")
    time_limit_hours: Optional[int] = Field(None, ge=1, le=8760, description="Time limit in hours (None = no limit)")
    prerequisite_quest_ids: List[int] = Field(default=[], description="List of prerequisite quest IDs")
    location: Optional[str] = Field(None, max_length=255, description="Quest location")
    giver_name: Optional[str] = Field(None, max_length=255, description="Name of quest giver")
    is_active: bool = Field(default=True, description="Whether quest is active")
    is_repeatable: bool = Field(default=False, description="Whether quest can be repeated")

    @validator('prerequisite_quest_ids')
    def validate_prerequisites(cls, v):
        """Validate prerequisite quest IDs."""
        if len(v) > 10:
            raise ValueError("Too many prerequisite quests (maximum 10)")
        if len(set(v)) != len(v):
            raise ValueError("Duplicate prerequisite quest IDs not allowed")
        return v


class QuestCreate(QuestBase):
    """Schema for creating quests."""
    objectives: List[QuestObjectiveCreate] = Field(..., min_items=1, description="Quest objectives")
    rewards: List[QuestRewardCreate] = Field(default=[], description="Quest rewards")

    @validator('objectives')
    def validate_objectives(cls, v):
        """Validate quest objectives."""
        if len(v) > 20:
            raise ValueError("Too many objectives (maximum 20)")
        return v

    @validator('rewards')
    def validate_rewards(cls, v):
        """Validate quest rewards."""
        if len(v) > 10:
            raise ValueError("Too many rewards (maximum 10)")
        return v


class QuestUpdate(BaseModel):
    """Schema for updating quests."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    quest_type: Optional[QuestType] = None
    difficulty_level: Optional[DifficultyLevel] = None
    required_level: Optional[int] = Field(None, ge=1, le=100)
    time_limit_hours: Optional[int] = Field(None, ge=1, le=8760)
    prerequisite_quest_ids: Optional[List[int]] = None
    location: Optional[str] = Field(None, max_length=255)
    giver_name: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = None
    is_repeatable: Optional[bool] = None

    @validator('prerequisite_quest_ids')
    def validate_prerequisites(cls, v):
        """Validate prerequisite quest IDs."""
        if v is not None:
            if len(v) > 10:
                raise ValueError("Too many prerequisite quests (maximum 10)")
            if len(set(v)) != len(v):
                raise ValueError("Duplicate prerequisite quest IDs not allowed")
        return v


class QuestResponse(QuestBase):
    """Schema for quest responses."""
    id: int
    created_at: datetime
    objectives: List[QuestObjectiveResponse] = []
    rewards: List[QuestRewardResponse] = []
    
    # Dynamic fields for character-specific data
    character_status: Optional[str] = None
    accepted_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Quest Progress Schemas
class QuestObjectiveProgressResponse(BaseModel):
    """Schema for quest objective progress responses."""
    id: int
    objective_id: int
    current_amount: int
    completed_at: Optional[datetime]
    objective: QuestObjectiveResponse

    class Config:
        from_attributes = True


class CharacterQuestResponse(BaseModel):
    """Schema for character quest responses."""
    id: int
    character_id: int
    quest_id: int
    status: QuestStatus
    accepted_at: datetime
    completed_at: Optional[datetime]
    expires_at: Optional[datetime]
    quest: QuestResponse
    objective_progress: List[QuestObjectiveProgressResponse] = []

    class Config:
        from_attributes = True


# Quest Action Schemas
class QuestAcceptResponse(BaseModel):
    """Schema for quest acceptance responses."""
    quest_id: int
    character_id: int
    accepted_at: datetime
    expires_at: Optional[datetime]
    message: str


class QuestCompletionResponse(BaseModel):
    """Schema for quest completion responses."""
    quest_id: int
    character_id: int
    completed_at: datetime
    rewards_granted: List[QuestRewardResponse]
    xp_gained: int
    message: str


class QuestProgressUpdate(BaseModel):
    """Schema for updating quest progress."""
    objective_id: int
    progress_amount: int = Field(default=1, ge=1, description="Amount of progress to add")


# Quest Generation Schemas
class DailyQuestRequest(BaseModel):
    """Schema for daily quest generation requests."""
    character_id: int = Field(..., gt=0, description="Character ID")
    count: int = Field(default=3, ge=1, le=10, description="Number of daily quests to generate")
    difficulty_preference: Optional[DifficultyLevel] = Field(None, description="Preferred difficulty level")


class QuestSearchFilters(BaseModel):
    """Schema for quest search and filtering."""
    quest_type: Optional[QuestType] = None
    difficulty_level: Optional[DifficultyLevel] = None
    min_level: Optional[int] = Field(None, ge=1, le=100)
    max_level: Optional[int] = Field(None, ge=1, le=100)
    location: Optional[str] = None
    is_repeatable: Optional[bool] = None
    has_time_limit: Optional[bool] = None

    @validator('max_level')
    def validate_level_range(cls, v, values):
        """Validate level range."""
        if v is not None and 'min_level' in values and values['min_level'] is not None:
            if v < values['min_level']:
                raise ValueError("max_level must be greater than or equal to min_level")
        return v 