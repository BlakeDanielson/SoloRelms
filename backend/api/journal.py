"""
Journal API endpoints for managing adventure journals, discoveries, and timeline events.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging

from schemas.journal import (
    JournalEntryCreate, JournalEntryUpdate, JournalEntryResponse,
    DiscoveryCreate, DiscoveryUpdate, DiscoveryResponse,
    TimelineEventCreate, TimelineEventUpdate, TimelineEventResponse
)
from models.journal import JournalEntry, Discovery, TimelineEvent
from database import get_db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/journal", tags=["journal"])


# Journal Entries
@router.post("/entries", response_model=JournalEntryResponse)
async def create_journal_entry(
    entry: JournalEntryCreate,
    db: Session = Depends(get_db)
):
    """Create a new journal entry."""
    try:
        db_entry = JournalEntry(
            title=entry.title,
            content=entry.content,
            location=entry.location,
            entry_type=entry.entry_type,
            tags=entry.tags,
            important=entry.important,
            character_id=entry.character_id,
            # adventure_id=entry.adventure_id,  # TODO: Add when Adventure model exists
            timestamp=datetime.utcnow()
        )
        
        db.add(db_entry)
        db.commit()
        db.refresh(db_entry)
        
        logger.info(f"Created journal entry: {db_entry.id}")
        return db_entry
        
    except Exception as e:
        logger.error(f"Error creating journal entry: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create journal entry")


@router.get("/entries/{character_id}", response_model=List[JournalEntryResponse])
async def get_character_journal_entries(
    character_id: int,
    entry_type: Optional[str] = None,
    important_only: bool = False,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get journal entries for a character."""
    try:
        query = db.query(JournalEntry).filter(JournalEntry.character_id == character_id)
        
        if entry_type:
            query = query.filter(JournalEntry.entry_type == entry_type)
        
        if important_only:
            query = query.filter(JournalEntry.important == True)
        
        entries = query.order_by(JournalEntry.timestamp.desc()).limit(limit).all()
        
        logger.info(f"Retrieved {len(entries)} journal entries for character {character_id}")
        return entries
        
    except Exception as e:
        logger.error(f"Error retrieving journal entries: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve journal entries")


@router.get("/entries/entry/{entry_id}", response_model=JournalEntryResponse)
async def get_journal_entry(entry_id: int, db: Session = Depends(get_db)):
    """Get a specific journal entry."""
    try:
        entry = db.query(JournalEntry).filter(JournalEntry.id == entry_id).first()
        if not entry:
            raise HTTPException(status_code=404, detail="Journal entry not found")
        
        return entry
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving journal entry: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve journal entry")


@router.put("/entries/{entry_id}", response_model=JournalEntryResponse)
async def update_journal_entry(
    entry_id: int,
    entry_update: JournalEntryUpdate,
    db: Session = Depends(get_db)
):
    """Update a journal entry."""
    try:
        db_entry = db.query(JournalEntry).filter(JournalEntry.id == entry_id).first()
        if not db_entry:
            raise HTTPException(status_code=404, detail="Journal entry not found")
        
        update_data = entry_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_entry, field, value)
        
        db.commit()
        db.refresh(db_entry)
        
        logger.info(f"Updated journal entry: {entry_id}")
        return db_entry
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating journal entry: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update journal entry")


@router.delete("/entries/{entry_id}")
async def delete_journal_entry(entry_id: int, db: Session = Depends(get_db)):
    """Delete a journal entry."""
    try:
        db_entry = db.query(JournalEntry).filter(JournalEntry.id == entry_id).first()
        if not db_entry:
            raise HTTPException(status_code=404, detail="Journal entry not found")
        
        db.delete(db_entry)
        db.commit()
        
        logger.info(f"Deleted journal entry: {entry_id}")
        return {"message": "Journal entry deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting journal entry: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete journal entry")


# Discoveries
@router.post("/discoveries", response_model=DiscoveryResponse)
async def create_discovery(
    discovery: DiscoveryCreate,
    db: Session = Depends(get_db)
):
    """Create a new discovery."""
    try:
        db_discovery = Discovery(
            name=discovery.name,
            description=discovery.description,
            discovery_type=discovery.discovery_type,
            location=discovery.location,
            notes=discovery.notes,
            character_id=discovery.character_id,
            # adventure_id=discovery.adventure_id,  # TODO: Add when Adventure model exists
            discovered_at=datetime.utcnow()
        )
        
        db.add(db_discovery)
        db.commit()
        db.refresh(db_discovery)
        
        logger.info(f"Created discovery: {db_discovery.id}")
        return db_discovery
        
    except Exception as e:
        logger.error(f"Error creating discovery: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create discovery")


@router.get("/discoveries/{character_id}", response_model=List[DiscoveryResponse])
async def get_character_discoveries(
    character_id: int,
    discovery_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get discoveries for a character."""
    try:
        query = db.query(Discovery).filter(Discovery.character_id == character_id)
        
        if discovery_type:
            query = query.filter(Discovery.discovery_type == discovery_type)
        
        discoveries = query.order_by(Discovery.discovered_at.desc()).all()
        
        logger.info(f"Retrieved {len(discoveries)} discoveries for character {character_id}")
        return discoveries
        
    except Exception as e:
        logger.error(f"Error retrieving discoveries: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve discoveries")


# Timeline Events
@router.post("/timeline", response_model=TimelineEventResponse)
async def create_timeline_event(
    event: TimelineEventCreate,
    db: Session = Depends(get_db)
):
    """Create a new timeline event."""
    try:
        db_event = TimelineEvent(
            title=event.title,
            description=event.description,
            location=event.location,
            event_type=event.event_type,
            participants=event.participants,
            consequences=event.consequences,
            character_id=event.character_id,
            # adventure_id=event.adventure_id,  # TODO: Add when Adventure model exists
            timestamp=datetime.utcnow()
        )
        
        db.add(db_event)
        db.commit()
        db.refresh(db_event)
        
        logger.info(f"Created timeline event: {db_event.id}")
        return db_event
        
    except Exception as e:
        logger.error(f"Error creating timeline event: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create timeline event")


@router.get("/timeline/{character_id}", response_model=List[TimelineEventResponse])
async def get_character_timeline(
    character_id: int,
    event_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get timeline events for a character."""
    try:
        query = db.query(TimelineEvent).filter(TimelineEvent.character_id == character_id)
        
        if event_type:
            query = query.filter(TimelineEvent.event_type == event_type)
        
        events = query.order_by(TimelineEvent.timestamp.asc()).all()
        
        logger.info(f"Retrieved {len(events)} timeline events for character {character_id}")
        return events
        
    except Exception as e:
        logger.error(f"Error retrieving timeline events: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve timeline events")


@router.get("/search/{character_id}")
async def search_journal_content(
    character_id: int,
    query: str,
    content_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Search journal content for a character."""
    try:
        results = {
            "entries": [],
            "discoveries": [],
            "timeline": []
        }
        
        if not content_type or content_type == "entries":
            entry_results = db.query(JournalEntry).filter(
                JournalEntry.character_id == character_id,
                (JournalEntry.title.ilike(f"%{query}%") | 
                 JournalEntry.content.ilike(f"%{query}%"))
            ).all()
            results["entries"] = entry_results
        
        if not content_type or content_type == "discoveries":
            discovery_results = db.query(Discovery).filter(
                Discovery.character_id == character_id,
                (Discovery.name.ilike(f"%{query}%") | 
                 Discovery.description.ilike(f"%{query}%"))
            ).all()
            results["discoveries"] = discovery_results
        
        if not content_type or content_type == "timeline":
            timeline_results = db.query(TimelineEvent).filter(
                TimelineEvent.character_id == character_id,
                (TimelineEvent.title.ilike(f"%{query}%") | 
                 TimelineEvent.description.ilike(f"%{query}%"))
            ).all()
            results["timeline"] = timeline_results
        
        logger.info(f"Search completed for character {character_id}")
        return results
        
    except Exception as e:
        logger.error(f"Error searching journal content: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to search journal content") 