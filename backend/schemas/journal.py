"""
Pydantic schemas for journal system including entries, discoveries, and timeline events.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
from enum import Enum


class EntryType(str, Enum):
    """Valid journal entry types."""
    adventure_log = "adventure_log"
    discovery = "discovery"
    personal_note = "personal_note"
    story_event = "story_event"
    character_interaction = "character_interaction"


class DiscoveryType(str, Enum):
    """Valid discovery types."""
    location = "location"
    person = "person"
    item = "item"
    lore = "lore"
    secret = "secret"


class EventType(str, Enum):
    """Valid timeline event types."""
    major_event = "major_event"
    combat = "combat"
    discovery = "discovery"
    story_progression = "story_progression"
    character_development = "character_development"


# Journal Entry Schemas
class JournalEntryBase(BaseModel):
    """Base schema for journal entries."""
    title: str = Field(..., min_length=1, max_length=255, description="Entry title")
    content: str = Field(..., min_length=1, description="Entry content")
    location: Optional[str] = Field(None, max_length=255, description="Location where entry was made")
    entry_type: EntryType = Field(..., description="Type of journal entry")
    tags: List[str] = Field(default=[], description="List of tags for categorization")
    important: bool = Field(default=False, description="Whether this entry is marked as important")

    @validator('tags')
    def validate_tags(cls, v):
        """Validate tags list."""
        if len(v) > 20:
            raise ValueError("Too many tags (maximum 20)")
        for tag in v:
            if len(tag.strip()) == 0:
                raise ValueError("Empty tags not allowed")
            if len(tag) > 50:
                raise ValueError("Tag too long (maximum 50 characters)")
        return [tag.strip().lower() for tag in v if tag.strip()]


class JournalEntryCreate(JournalEntryBase):
    """Schema for creating journal entries."""
    character_id: int = Field(..., gt=0, description="ID of the character who wrote this entry")
    # adventure_id: Optional[int] = Field(None, gt=0, description="ID of the adventure this entry relates to")  # TODO: Add when Adventure model exists


class JournalEntryUpdate(BaseModel):
    """Schema for updating journal entries."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = Field(None, min_length=1)
    location: Optional[str] = Field(None, max_length=255)
    entry_type: Optional[EntryType] = None
    tags: Optional[List[str]] = None
    important: Optional[bool] = None

    @validator('tags')
    def validate_tags(cls, v):
        """Validate tags list."""
        if v is not None:
            if len(v) > 20:
                raise ValueError("Too many tags (maximum 20)")
            for tag in v:
                if len(tag.strip()) == 0:
                    raise ValueError("Empty tags not allowed")
                if len(tag) > 50:
                    raise ValueError("Tag too long (maximum 50 characters)")
            return [tag.strip().lower() for tag in v if tag.strip()]
        return v


class JournalEntryResponse(JournalEntryBase):
    """Schema for journal entry responses."""
    id: int
    timestamp: datetime
    character_id: int
    # adventure_id: Optional[int]  # TODO: Add when Adventure model exists

    class Config:
        from_attributes = True


# Discovery Schemas
class DiscoveryBase(BaseModel):
    """Base schema for discoveries."""
    name: str = Field(..., min_length=1, max_length=255, description="Name of the discovery")
    description: str = Field(..., min_length=1, description="Description of the discovery")
    discovery_type: DiscoveryType = Field(..., description="Type of discovery")
    location: Optional[str] = Field(None, max_length=255, description="Where the discovery was made")
    notes: Optional[str] = Field(None, description="Additional notes about the discovery")


class DiscoveryCreate(DiscoveryBase):
    """Schema for creating discoveries."""
    character_id: int = Field(..., gt=0, description="ID of the character who made this discovery")
    # adventure_id: Optional[int] = Field(None, gt=0, description="ID of the adventure this discovery relates to")  # TODO: Add when Adventure model exists


class DiscoveryUpdate(BaseModel):
    """Schema for updating discoveries."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    discovery_type: Optional[DiscoveryType] = None
    location: Optional[str] = Field(None, max_length=255)
    notes: Optional[str] = None


class DiscoveryResponse(DiscoveryBase):
    """Schema for discovery responses."""
    id: int
    discovered_at: datetime
    character_id: int
    # adventure_id: Optional[int]  # TODO: Add when Adventure model exists

    class Config:
        from_attributes = True


# Timeline Event Schemas
class TimelineEventBase(BaseModel):
    """Base schema for timeline events."""
    title: str = Field(..., min_length=1, max_length=255, description="Event title")
    description: str = Field(..., min_length=1, description="Event description")
    location: Optional[str] = Field(None, max_length=255, description="Where the event occurred")
    event_type: EventType = Field(..., description="Type of timeline event")
    participants: List[str] = Field(default=[], description="List of event participants")
    consequences: List[str] = Field(default=[], description="List of event consequences")

    @validator('participants')
    def validate_participants(cls, v):
        """Validate participants list."""
        if len(v) > 50:
            raise ValueError("Too many participants (maximum 50)")
        for participant in v:
            if len(participant.strip()) == 0:
                raise ValueError("Empty participant names not allowed")
            if len(participant) > 100:
                raise ValueError("Participant name too long (maximum 100 characters)")
        return [p.strip() for p in v if p.strip()]

    @validator('consequences')
    def validate_consequences(cls, v):
        """Validate consequences list."""
        if len(v) > 20:
            raise ValueError("Too many consequences (maximum 20)")
        for consequence in v:
            if len(consequence.strip()) == 0:
                raise ValueError("Empty consequences not allowed")
            if len(consequence) > 500:
                raise ValueError("Consequence too long (maximum 500 characters)")
        return [c.strip() for c in v if c.strip()]


class TimelineEventCreate(TimelineEventBase):
    """Schema for creating timeline events."""
    character_id: int = Field(..., gt=0, description="ID of the character this event relates to")
    # adventure_id: Optional[int] = Field(None, gt=0, description="ID of the adventure this event relates to")  # TODO: Add when Adventure model exists


class TimelineEventUpdate(BaseModel):
    """Schema for updating timeline events."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    location: Optional[str] = Field(None, max_length=255)
    event_type: Optional[EventType] = None
    participants: Optional[List[str]] = None
    consequences: Optional[List[str]] = None

    @validator('participants')
    def validate_participants(cls, v):
        """Validate participants list."""
        if v is not None:
            if len(v) > 50:
                raise ValueError("Too many participants (maximum 50)")
            for participant in v:
                if len(participant.strip()) == 0:
                    raise ValueError("Empty participant names not allowed")
                if len(participant) > 100:
                    raise ValueError("Participant name too long (maximum 100 characters)")
            return [p.strip() for p in v if p.strip()]
        return v

    @validator('consequences')
    def validate_consequences(cls, v):
        """Validate consequences list."""
        if v is not None:
            if len(v) > 20:
                raise ValueError("Too many consequences (maximum 20)")
            for consequence in v:
                if len(consequence.strip()) == 0:
                    raise ValueError("Empty consequences not allowed")
                if len(consequence) > 500:
                    raise ValueError("Consequence too long (maximum 500 characters)")
            return [c.strip() for c in v if c.strip()]
        return v


class TimelineEventResponse(TimelineEventBase):
    """Schema for timeline event responses."""
    id: int
    timestamp: datetime
    character_id: int
    # adventure_id: Optional[int]  # TODO: Add when Adventure model exists

    class Config:
        from_attributes = True


# Combined Schemas
class JournalSearchResults(BaseModel):
    """Schema for journal search results."""
    entries: List[JournalEntryResponse] = Field(default=[], description="Matching journal entries")
    discoveries: List[DiscoveryResponse] = Field(default=[], description="Matching discoveries")
    timeline: List[TimelineEventResponse] = Field(default=[], description="Matching timeline events")

    class Config:
        from_attributes = True 