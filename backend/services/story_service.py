from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional, Dict, Any
from datetime import datetime
from models.story import StoryArc, WorldState, StoryStage
from models.character import Character
from schemas.story import (
    StoryArcCreate, StoryArcUpdate, WorldStateCreate, WorldStateUpdate,
    StoryProgressSummary, DecisionRequest, NPCUpdateRequest, CombatRequest,
    LocationVisitRequest, WorldEventRequest, ObjectiveRequest, LoreRequest
)

class StoryService:
    """Service for story and world state operations"""
    
    @staticmethod
    def create_story_arc(db: Session, story_data: StoryArcCreate) -> StoryArc:
        """Create a new story arc for a character"""
        # Verify character exists
        character = db.query(Character).filter(Character.id == story_data.character_id).first()
        if not character:
            raise ValueError(f"Character with ID {story_data.character_id} not found")
        
        story_arc = StoryArc(
            character_id=story_data.character_id,
            title=story_data.title,
            story_type=story_data.story_type,
            story_seed=story_data.story_seed,
            current_stage=StoryStage.INTRO,
            started_at=datetime.utcnow()
        )
        
        db.add(story_arc)
        db.commit()
        db.refresh(story_arc)
        
        # Create initial world state
        initial_world_state = WorldState(
            story_arc_id=story_arc.id,
            current_location="starting_area"
        )
        db.add(initial_world_state)
        db.commit()
        
        return story_arc
    
    @staticmethod
    def get_story_arc(db: Session, story_arc_id: int) -> Optional[StoryArc]:
        """Get a story arc by ID"""
        return db.query(StoryArc).filter(StoryArc.id == story_arc_id).first()
    
    @staticmethod
    def get_character_story_arcs(db: Session, character_id: int, include_completed: bool = True) -> List[StoryArc]:
        """Get all story arcs for a character"""
        query = db.query(StoryArc).filter(StoryArc.character_id == character_id)
        
        if not include_completed:
            query = query.filter(StoryArc.story_completed == False)
        
        return query.order_by(StoryArc.created_at.desc()).all()
    
    @staticmethod
    def get_active_story_arc(db: Session, character_id: int) -> Optional[StoryArc]:
        """Get the currently active story arc for a character"""
        return db.query(StoryArc).filter(
            StoryArc.character_id == character_id,
            StoryArc.story_completed == False
        ).order_by(StoryArc.created_at.desc()).first()
    
    @staticmethod
    def update_story_arc(db: Session, story_arc_id: int, update_data: StoryArcUpdate) -> Optional[StoryArc]:
        """Update a story arc"""
        story_arc = db.query(StoryArc).filter(StoryArc.id == story_arc_id).first()
        if not story_arc:
            return None
        
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(story_arc, field, value)
        
        db.commit()
        db.refresh(story_arc)
        return story_arc
    
    @staticmethod
    def delete_story_arc(db: Session, story_arc_id: int) -> bool:
        """Delete a story arc and all related world states"""
        story_arc = db.query(StoryArc).filter(StoryArc.id == story_arc_id).first()
        if not story_arc:
            return False
        
        db.delete(story_arc)
        db.commit()
        return True
    
    # Story progression methods
    @staticmethod
    def advance_story_stage(db: Session, story_arc_id: int, force: bool = False) -> Optional[StoryArc]:
        """Advance story to the next stage"""
        story_arc = db.query(StoryArc).filter(StoryArc.id == story_arc_id).first()
        if not story_arc:
            return None
        
        if not force and not story_arc.can_advance_stage():
            raise ValueError(f"Cannot advance from {story_arc.current_stage.value}. Prerequisites not met.")
        
        story_arc.advance_stage()
        db.commit()
        db.refresh(story_arc)
        return story_arc
    
    @staticmethod
    def add_story_decision(db: Session, story_arc_id: int, decision_data: DecisionRequest) -> Optional[StoryArc]:
        """Add a major story decision"""
        story_arc = db.query(StoryArc).filter(StoryArc.id == story_arc_id).first()
        if not story_arc:
            return None
        
        decision_dict = decision_data.model_dump()
        story_arc.add_decision(decision_dict)
        
        db.commit()
        db.refresh(story_arc)
        return story_arc
    
    @staticmethod
    def update_npc_status(db: Session, story_arc_id: int, npc_request: NPCUpdateRequest) -> Optional[StoryArc]:
        """Update NPC status in the story"""
        story_arc = db.query(StoryArc).filter(StoryArc.id == story_arc_id).first()
        if not story_arc:
            return None
        
        story_arc.update_npc_status(npc_request.npc_id, npc_request.status_data.model_dump())
        
        db.commit()
        db.refresh(story_arc)
        return story_arc
    
    @staticmethod
    def add_combat_outcome(db: Session, story_arc_id: int, combat_request: CombatRequest) -> Optional[StoryArc]:
        """Record a combat outcome"""
        story_arc = db.query(StoryArc).filter(StoryArc.id == story_arc_id).first()
        if not story_arc:
            return None
        
        combat_dict = combat_request.combat_data.model_dump()
        # Convert datetime to ISO string if needed
        if isinstance(combat_dict.get('timestamp'), datetime):
            combat_dict['timestamp'] = combat_dict['timestamp'].isoformat()
        
        story_arc.add_combat_outcome(combat_dict)
        
        db.commit()
        db.refresh(story_arc)
        return story_arc
    
    # World state methods
    @staticmethod
    def get_world_state(db: Session, story_arc_id: int) -> Optional[WorldState]:
        """Get the world state for a story arc"""
        return db.query(WorldState).filter(WorldState.story_arc_id == story_arc_id).first()
    
    @staticmethod
    def update_world_state(db: Session, world_state_id: int, update_data: WorldStateUpdate) -> Optional[WorldState]:
        """Update world state"""
        world_state = db.query(WorldState).filter(WorldState.id == world_state_id).first()
        if not world_state:
            return None
        
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(world_state, field, value)
        
        db.commit()
        db.refresh(world_state)
        return world_state
    
    @staticmethod
    def visit_location(db: Session, story_arc_id: int, location_request: LocationVisitRequest) -> Optional[WorldState]:
        """Record visiting a location"""
        world_state = db.query(WorldState).filter(WorldState.story_arc_id == story_arc_id).first()
        if not world_state:
            return None
        
        location_dict = location_request.location_data.model_dump()
        # Convert datetime to ISO string if needed
        if isinstance(location_dict.get('first_visited'), datetime):
            location_dict['first_visited'] = location_dict['first_visited'].isoformat()
        
        world_state.visit_location(location_dict)
        world_state.current_location = location_dict.get('name', world_state.current_location)
        
        db.commit()
        db.refresh(world_state)
        return world_state
    
    @staticmethod
    def add_world_event(db: Session, story_arc_id: int, event_request: WorldEventRequest) -> Optional[WorldState]:
        """Add a world event"""
        world_state = db.query(WorldState).filter(WorldState.story_arc_id == story_arc_id).first()
        if not world_state:
            return None
        
        event_dict = event_request.event_data.model_dump()
        # Convert datetime to ISO string if needed
        if isinstance(event_dict.get('timestamp'), datetime):
            event_dict['timestamp'] = event_dict['timestamp'].isoformat()
        
        world_state.add_world_event(event_dict)
        
        db.commit()
        db.refresh(world_state)
        return world_state
    
    @staticmethod
    def add_objective(db: Session, story_arc_id: int, objective_request: ObjectiveRequest) -> Optional[WorldState]:
        """Add a quest objective"""
        world_state = db.query(WorldState).filter(WorldState.story_arc_id == story_arc_id).first()
        if not world_state:
            return None
        
        objective_dict = objective_request.objective_data.model_dump()
        world_state.add_objective(objective_dict)
        
        db.commit()
        db.refresh(world_state)
        return world_state
    
    @staticmethod
    def complete_objective(db: Session, story_arc_id: int, objective_id: str) -> Optional[WorldState]:
        """Complete a quest objective"""
        world_state = db.query(WorldState).filter(WorldState.story_arc_id == story_arc_id).first()
        if not world_state:
            return None
        
        world_state.complete_objective(objective_id)
        
        db.commit()
        db.refresh(world_state)
        return world_state
    
    @staticmethod
    def establish_lore(db: Session, story_arc_id: int, lore_request: LoreRequest) -> Optional[WorldState]:
        """Establish world lore for AI consistency"""
        world_state = db.query(WorldState).filter(WorldState.story_arc_id == story_arc_id).first()
        if not world_state:
            return None
        
        world_state.establish_lore(lore_request.lore_key, lore_request.lore_value)
        
        db.commit()
        db.refresh(world_state)
        return world_state
    
    # Utility methods for AI context
    @staticmethod
    def get_story_progress_summary(db: Session, story_arc_id: int) -> Optional[Dict[str, Any]]:
        """Get a summary of story progress for AI context"""
        story_arc = db.query(StoryArc).filter(StoryArc.id == story_arc_id).first()
        world_state = db.query(WorldState).filter(WorldState.story_arc_id == story_arc_id).first()
        
        if not story_arc or not world_state:
            return None
        
        # Get recent decisions (last 5)
        recent_decisions = (story_arc.major_decisions or [])[-5:]
        
        # Get active NPCs (those with recent interactions)
        active_npcs = story_arc.npc_status or {}
        
        # Get recent events (last 5)
        recent_events = (world_state.world_events or [])[-5:]
        
        return {
            "current_stage": story_arc.current_stage.value,
            "stages_completed": story_arc.stages_completed or [],
            "recent_decisions": recent_decisions,
            "active_npcs": active_npcs,
            "current_location": world_state.current_location,
            "active_objectives": world_state.active_objectives or [],
            "recent_events": recent_events,
            "established_lore": world_state.established_lore or {},
            "story_time_elapsed": world_state.story_time_elapsed,
            "combat_history": story_arc.combat_outcomes or []
        }
    
    @staticmethod
    def update_play_time(db: Session, story_arc_id: int, minutes_played: int) -> Optional[WorldState]:
        """Update the real-time played for analytics"""
        world_state = db.query(WorldState).filter(WorldState.story_arc_id == story_arc_id).first()
        if not world_state:
            return None
        
        world_state.real_time_played += minutes_played
        
        db.commit()
        db.refresh(world_state)
        return world_state
    
    @staticmethod
    def get_completion_stats(db: Session, character_id: int) -> Dict[str, Any]:
        """Get completion statistics for a character"""
        story_arcs = db.query(StoryArc).filter(StoryArc.character_id == character_id).all()
        
        total_stories = len(story_arcs)
        completed_stories = len([arc for arc in story_arcs if arc.story_completed])
        
        completion_types = {}
        total_playtime = 0
        
        for arc in story_arcs:
            if arc.completion_type:
                completion_types[arc.completion_type] = completion_types.get(arc.completion_type, 0) + 1
            
            # Get playtime from world state
            world_state = db.query(WorldState).filter(WorldState.story_arc_id == arc.id).first()
            if world_state:
                total_playtime += world_state.real_time_played
        
        return {
            "total_stories": total_stories,
            "completed_stories": completed_stories,
            "completion_rate": completed_stories / total_stories if total_stories > 0 else 0,
            "completion_types": completion_types,
            "total_playtime_minutes": total_playtime
        } 