from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class StoryStageEnum(str, Enum):
    """Story progression stages for API responses"""
    INTRO = "intro"
    INCITING_INCIDENT = "inciting_incident"
    FIRST_COMBAT = "first_combat"
    TWIST = "twist"
    FINAL_CONFLICT = "final_conflict"
    RESOLUTION = "resolution"

class StoryTypeEnum(str, Enum):
    """Story type options"""
    SHORT_FORM = "short_form"
    CAMPAIGN = "campaign"

class CompletionTypeEnum(str, Enum):
    """Story completion types"""
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"

# Base schemas
class StoryArcBase(BaseModel):
    """Base schema for StoryArc with common fields"""
    character_id: int = Field(..., description="ID of the character this story belongs to")
    title: Optional[str] = Field(None, max_length=200, description="Story title")
    story_type: StoryTypeEnum = Field(StoryTypeEnum.SHORT_FORM, description="Type of story")
    story_seed: Optional[str] = Field(None, description="Initial story prompt or theme")

class WorldStateBase(BaseModel):
    """Base schema for WorldState with common fields"""
    story_arc_id: int = Field(..., description="ID of the story arc this world state belongs to")
    current_location: str = Field(..., max_length=100, description="Current player location")

# Creation schemas (for POST requests)
class StoryArcCreate(StoryArcBase):
    """Schema for creating a new story arc"""
    pass

class WorldStateCreate(WorldStateBase):
    """Schema for creating a new world state"""
    pass

# Update schemas (for PUT/PATCH requests)
class StoryArcUpdate(BaseModel):
    """Schema for updating a story arc"""
    title: Optional[str] = Field(None, max_length=200)
    current_stage: Optional[StoryStageEnum] = None
    story_completed: Optional[bool] = None
    completion_type: Optional[CompletionTypeEnum] = None
    ai_context_summary: Optional[str] = None

class WorldStateUpdate(BaseModel):
    """Schema for updating world state"""
    current_location: Optional[str] = Field(None, max_length=100)
    story_time_elapsed: Optional[int] = Field(None, ge=0)
    real_time_played: Optional[int] = Field(None, ge=0)

# Nested schemas for complex data structures
class StoryDecision(BaseModel):
    """Schema for a story decision"""
    decision: str = Field(..., description="Key identifier for the decision")
    description: str = Field(..., description="Human-readable description")
    consequences: List[str] = Field(default_factory=list, description="Effects of this decision")
    stage: StoryStageEnum = Field(..., description="Story stage when decision was made")
    timestamp: datetime = Field(..., description="When the decision was made")

class NPCStatus(BaseModel):
    """Schema for NPC status information"""
    status: str = Field(..., description="NPC relationship status (ally, hostile, neutral)")
    health: Optional[str] = Field(None, description="NPC health status")
    location: Optional[str] = Field(None, description="NPC current location")
    disposition: Optional[str] = Field(None, description="NPC attitude toward player")

class CombatOutcome(BaseModel):
    """Schema for combat encounter results"""
    encounter_type: str = Field(..., description="Type of combat encounter")
    result: str = Field(..., description="Combat result (victory, defeat, escape)")
    damage_taken: int = Field(0, ge=0, description="Damage taken by player")
    loot_gained: List[str] = Field(default_factory=list, description="Items gained from combat")
    xp_gained: int = Field(0, ge=0, description="Experience points gained")
    stage: StoryStageEnum = Field(..., description="Story stage when combat occurred")
    timestamp: datetime = Field(..., description="When the combat occurred")

class ExploredArea(BaseModel):
    """Schema for an explored location"""
    name: str = Field(..., description="Location name")
    description: str = Field(..., description="Location description")
    notable_features: List[str] = Field(default_factory=list, description="Interesting features")
    npcs_encountered: List[str] = Field(default_factory=list, description="NPCs met here")
    first_visited: datetime = Field(..., description="When first discovered")

class WorldEvent(BaseModel):
    """Schema for a world event"""
    event: str = Field(..., description="Event identifier")
    location: str = Field(..., description="Where the event occurred")
    description: str = Field(..., description="Event description")
    player_involved: bool = Field(False, description="Whether player was involved")
    consequences: List[str] = Field(default_factory=list, description="Event consequences")
    timestamp: datetime = Field(..., description="When the event occurred")

class Objective(BaseModel):
    """Schema for quest objectives"""
    id: str = Field(..., description="Objective identifier")
    title: str = Field(..., description="Objective title")
    description: str = Field(..., description="Objective description")
    stage: StoryStageEnum = Field(..., description="Story stage for this objective")
    priority: str = Field("main", description="Objective priority (main, side, optional)")
    status: str = Field("active", description="Objective status")
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class WorldItem(BaseModel):
    """Schema for discoverable world items"""
    item: str = Field(..., description="Item name")
    description: str = Field(..., description="Item description")
    discovered: bool = Field(False, description="Whether item has been found")
    requires: Optional[str] = Field(None, description="What's needed to discover this item")

# Response schemas (for API responses)
class StoryArc(StoryArcBase):
    """Complete StoryArc schema for API responses"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    current_stage: StoryStageEnum
    stages_completed: List[str] = Field(default_factory=list)
    major_decisions: List[Dict[str, Any]] = Field(default_factory=list)
    npc_status: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    combat_outcomes: List[Dict[str, Any]] = Field(default_factory=list)
    story_completed: bool = False
    completion_type: Optional[CompletionTypeEnum] = None
    final_rewards: Dict[str, Any] = Field(default_factory=dict)
    ai_context_summary: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    last_updated: Optional[datetime] = None

class WorldState(WorldStateBase):
    """Complete WorldState schema for API responses"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    explored_areas: List[Dict[str, Any]] = Field(default_factory=list)
    world_events: List[Dict[str, Any]] = Field(default_factory=list)
    active_objectives: List[Dict[str, Any]] = Field(default_factory=list)
    completed_objectives: List[Dict[str, Any]] = Field(default_factory=list)
    world_items: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    story_time_elapsed: int = 0
    real_time_played: int = 0
    established_lore: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    last_updated: Optional[datetime] = None

# Specialized schemas for specific operations
class StoryAdvanceRequest(BaseModel):
    """Schema for advancing story stage"""
    force_advance: bool = Field(False, description="Force advance even if conditions not met")

class DecisionRequest(BaseModel):
    """Schema for making a story decision"""
    decision: str = Field(..., description="Decision identifier")
    description: str = Field(..., description="Human-readable description")
    consequences: List[str] = Field(default_factory=list, description="Expected consequences")

class NPCUpdateRequest(BaseModel):
    """Schema for updating NPC status"""
    npc_id: str = Field(..., description="NPC identifier")
    status_data: NPCStatus = Field(..., description="Updated NPC status")

class CombatRequest(BaseModel):
    """Schema for recording combat outcome"""
    combat_data: CombatOutcome = Field(..., description="Combat result data")

class LocationVisitRequest(BaseModel):
    """Schema for visiting a location"""
    location_data: ExploredArea = Field(..., description="Location information")

class WorldEventRequest(BaseModel):
    """Schema for adding a world event"""
    event_data: WorldEvent = Field(..., description="Event information")

class ObjectiveRequest(BaseModel):
    """Schema for adding an objective"""
    objective_data: Objective = Field(..., description="Objective information")

class ObjectiveCompleteRequest(BaseModel):
    """Schema for completing an objective"""
    objective_id: str = Field(..., description="ID of objective to complete")

class LoreRequest(BaseModel):
    """Schema for establishing world lore"""
    lore_key: str = Field(..., description="Lore identifier")
    lore_value: Any = Field(..., description="Lore content")

# Response schemas with relationships
class StoryArcWithWorldState(StoryArc):
    """StoryArc with related WorldState"""
    world_states: List[WorldState] = Field(default_factory=list)

class StoryProgressSummary(BaseModel):
    """Summary of story progress for AI context"""
    current_stage: StoryStageEnum
    stages_completed: List[str]
    recent_decisions: List[StoryDecision]
    active_npcs: Dict[str, NPCStatus]
    current_location: str
    active_objectives: List[Objective]
    recent_events: List[WorldEvent] 