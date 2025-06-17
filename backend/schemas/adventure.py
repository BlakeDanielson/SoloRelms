from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class AdventureCreate(BaseModel):
    character_id: int = Field(..., description="ID of the character for this adventure")
    story_type: str = Field(..., description="Type of story (mystery, combat, exploration, etc.)")
    themes: List[str] = Field(default=[], description="Story themes and elements")
    difficulty: str = Field(default="medium", description="Adventure difficulty level")
    estimated_duration: str = Field(default="medium", description="Expected play time")
    story_seed: Optional[str] = Field(None, description="Custom story prompt or seed")

class AdventureUpdate(BaseModel):
    title: Optional[str] = Field(None, description="Adventure title")
    story_summary: Optional[str] = Field(None, description="Adventure summary")
    story_seed: Optional[str] = Field(None, description="Story seed/prompt")

class AdventureProgress(BaseModel):
    current_stage: Optional[str] = Field(None, description="Current story stage")
    stages_completed: Optional[List[str]] = Field(None, description="List of completed stages")
    story_completed: Optional[bool] = Field(None, description="Whether the story is finished")
    completion_type: Optional[str] = Field(None, description="How the story ended")
    world_state_updates: Optional[Dict[str, Any]] = Field(None, description="Updates to world state")

class AdventureResponse(BaseModel):
    id: int
    character_id: int
    title: Optional[str]
    story_type: str
    current_stage: str
    stages_completed: List[str] = []
    story_completed: bool = False
    completion_type: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    story_seed: Optional[str] = None
    story_summary: Optional[str] = None
    world_state: Optional[Dict[str, Any]] = None
    stage_data: Optional[Dict[str, Any]] = None
    major_decisions: Optional[List[Dict[str, Any]]] = []
    character_progression: Optional[Dict[str, Any]] = {}
    total_play_time: Optional[int] = 0
    difficulty: Optional[str] = None
    estimated_duration: Optional[str] = None
    themes: Optional[List[str]] = []

    class Config:
        from_attributes = True

class AdventureListResponse(BaseModel):
    id: int
    character_id: int
    title: str
    story_type: str
    current_stage: str
    story_completed: bool
    created_at: datetime
    completed_at: Optional[datetime] = None
    stages_completed: List[str] = []
    progress_percentage: float = 0.0

    class Config:
        from_attributes = True

class CharacterSummary(BaseModel):
    id: int
    name: str
    race: str
    character_class: str
    level: int

class AdventureListWithCharacter(BaseModel):
    adventure: AdventureListResponse
    character: CharacterSummary

    class Config:
        from_attributes = True 