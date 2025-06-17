"""
Database models for journal system including entries, discoveries, and timeline events.
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class JournalEntry(Base):
    """Journal entry model for player adventure logs and notes."""
    __tablename__ = "journal_entries"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    location = Column(String(255), nullable=True)
    entry_type = Column(String(50), nullable=False)  # adventure_log, discovery, personal_note, story_event, character_interaction
    tags = Column(JSON, default=list)  # List of string tags
    important = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    character_id = Column(Integer, ForeignKey("characters.id"), nullable=False)
    # adventure_id = Column(Integer, ForeignKey("adventures.id"), nullable=True)  # TODO: Add when Adventure model exists
    
    character = relationship("Character", back_populates="journal_entries")
    # adventure = relationship("Adventure", back_populates="journal_entries")  # TODO: Add when Adventure model exists

    def __repr__(self):
        return f"<JournalEntry(id={self.id}, title='{self.title}', type='{self.entry_type}')>"


class Discovery(Base):
    """Discovery model for tracking found locations, people, items, and lore."""
    __tablename__ = "discoveries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    discovery_type = Column(String(50), nullable=False)  # location, person, item, lore, secret
    location = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    discovered_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    character_id = Column(Integer, ForeignKey("characters.id"), nullable=False)
    # adventure_id = Column(Integer, ForeignKey("adventures.id"), nullable=True)  # TODO: Add when Adventure model exists
    
    character = relationship("Character", back_populates="discoveries")
    # adventure = relationship("Adventure", back_populates="discoveries")  # TODO: Add when Adventure model exists

    def __repr__(self):
        return f"<Discovery(id={self.id}, name='{self.name}', type='{self.discovery_type}')>"


class TimelineEvent(Base):
    """Timeline event model for tracking major story events and character development."""
    __tablename__ = "timeline_events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    location = Column(String(255), nullable=True)
    event_type = Column(String(50), nullable=False)  # major_event, combat, discovery, story_progression, character_development
    participants = Column(JSON, default=list)  # List of participant names
    consequences = Column(JSON, default=list)  # List of event consequences
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    character_id = Column(Integer, ForeignKey("characters.id"), nullable=False)
    # adventure_id = Column(Integer, ForeignKey("adventures.id"), nullable=True)  # TODO: Add when Adventure model exists
    
    character = relationship("Character", back_populates="timeline_events")
    # adventure = relationship("Adventure", back_populates="timeline_events")  # TODO: Add when Adventure model exists

    def __repr__(self):
        return f"<TimelineEvent(id={self.id}, title='{self.title}', type='{self.event_type}')>" 