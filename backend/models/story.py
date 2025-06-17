from sqlalchemy import Column, Integer, String, JSON, DateTime, Boolean, ForeignKey, Text, Enum, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.attributes import flag_modified
from datetime import datetime
from enum import Enum as PyEnum
try:
    from ..database import Base
except ImportError:
    # Fallback for when running from alembic or direct execution
    from database import Base

class StoryStage(PyEnum):
    """Story progression stages as defined in PRD"""
    INTRO = "intro"
    INCITING_INCIDENT = "inciting_incident"
    FIRST_COMBAT = "first_combat"
    TWIST = "twist"
    FINAL_CONFLICT = "final_conflict"
    RESOLUTION = "resolution"

class StoryArc(Base):
    """
    Story arc model tracking narrative progression through the 6-stage state machine
    Supports short-form (~30 min) adventures and future campaign-length stories
    """
    __tablename__ = "story_arcs"
    
    # Primary identification
    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("characters.id"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)  # Clerk user ID
    
    # Story metadata
    title = Column(String(200), nullable=True)  # AI-generated or user-set story title
    story_type = Column(String(20), default="short_form")  # "short_form" or "campaign"
    
    # Story progression state
    current_stage = Column(Enum(StoryStage), default=StoryStage.INTRO, nullable=False)
    stages_completed = Column(JSON, default=list)  # List of completed stages for validation
    
    # Narrative tracking
    major_decisions = Column(JSON, default=list)  # Player choices that affect story
    """
    Example major_decisions structure:
    [
        {
            "stage": "inciting_incident",
            "decision": "helped_villager",
            "description": "Chose to help the injured villager instead of pursuing the thief",
            "timestamp": "2025-05-22T10:30:00Z",
            "consequences": ["villager_ally", "thief_escaped"]
        }
    ]
    """
    
    # NPC and story state tracking
    npc_status = Column(JSON, default=dict)
    """
    Example npc_status structure:
    {
        "villager_tom": {
            "status": "ally",
            "health": "injured",
            "location": "tavern",
            "disposition": "grateful"
        },
        "bandit_leader": {
            "status": "hostile",
            "health": "unknown",
            "location": "forest_hideout",
            "disposition": "vengeful"
        }
    }
    """
    
    # Combat and encounter tracking
    combat_outcomes = Column(JSON, default=list)
    """
    Example combat_outcomes structure:
    [
        {
            "stage": "first_combat",
            "encounter_type": "bandit_ambush", 
            "result": "victory",
            "damage_taken": 8,
            "loot_gained": ["gold_pieces_15", "iron_sword"],
            "xp_gained": 150,
            "timestamp": "2025-05-22T10:45:00Z"
        }
    ]
    """
    
    # Story completion and rewards
    story_completed = Column(Boolean, default=False)
    completion_type = Column(String(50), nullable=True)  # "success", "failure", "partial"
    final_rewards = Column(JSON, default=dict)  # XP, items, story unlocks
    
    # Story seeds and AI context
    story_seed = Column(Text, nullable=True)  # Initial story prompt or theme
    ai_context_summary = Column(Text, nullable=True)  # Compressed story context for AI
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)  # When story actually began
    completed_at = Column(DateTime(timezone=True), nullable=True)
    last_updated = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="story_arcs")
    character = relationship("Character", back_populates="story_arcs")
    world_states = relationship("WorldState", back_populates="story_arc", cascade="all, delete-orphan")
    combat_encounters = relationship("CombatEncounter", back_populates="story_arc", cascade="all, delete-orphan")
    
    def advance_stage(self):
        """Advance to the next story stage"""
        stages = list(StoryStage)
        current_index = stages.index(self.current_stage)
        
        # Add current stage to completed list
        if self.stages_completed is None:
            self.stages_completed = []
        if self.current_stage.value not in self.stages_completed:
            self.stages_completed.append(self.current_stage.value)
            # Tell SQLAlchemy that the JSON field has been modified
            flag_modified(self, 'stages_completed')
        
        # Advance to next stage or mark complete
        if current_index < len(stages) - 1:
            self.current_stage = stages[current_index + 1]
        else:
            self.story_completed = True
            self.completed_at = datetime.utcnow()
    
    def can_advance_stage(self) -> bool:
        """Check if conditions are met to advance to next stage"""
        # Basic progression rules - can be extended with more complex logic
        if self.current_stage == StoryStage.INTRO:
            return True  # Can always advance from intro
        elif self.current_stage == StoryStage.INCITING_INCIDENT:
            return self.major_decisions is not None and len(self.major_decisions) > 0  # Must make at least one decision
        elif self.current_stage == StoryStage.FIRST_COMBAT:
            return self.combat_outcomes is not None and len(self.combat_outcomes) > 0  # Must complete at least one combat
        elif self.current_stage == StoryStage.TWIST:
            return True  # Story revelation can always happen
        elif self.current_stage == StoryStage.FINAL_CONFLICT:
            return self.combat_outcomes is not None and len(self.combat_outcomes) > 1  # Must have combat experience
        else:
            return False  # Resolution is the final stage
    
    def add_decision(self, decision_data: dict):
        """Add a major story decision"""
        if self.major_decisions is None:
            self.major_decisions = []
        
        decision_data.update({
            "stage": self.current_stage.value,
            "timestamp": datetime.utcnow().isoformat()
        })
        self.major_decisions.append(decision_data)
        flag_modified(self, 'major_decisions')
    
    def update_npc_status(self, npc_id: str, status_data: dict):
        """Update the status of an NPC"""
        if self.npc_status is None:
            self.npc_status = {}
        
        if npc_id in self.npc_status:
            self.npc_status[npc_id].update(status_data)
        else:
            self.npc_status[npc_id] = status_data
        flag_modified(self, 'npc_status')
    
    def add_combat_outcome(self, combat_data: dict):
        """Record a combat encounter outcome"""
        if self.combat_outcomes is None:
            self.combat_outcomes = []
        
        combat_data.update({
            "stage": self.current_stage.value,
            "timestamp": datetime.utcnow().isoformat()
        })
        self.combat_outcomes.append(combat_data)
        flag_modified(self, 'combat_outcomes')


class WorldState(Base):
    """
    World state model for tracking environmental and exploration state
    Supports dynamic world building and location-based storytelling
    """
    __tablename__ = "world_states"
    
    # Primary identification
    id = Column(Integer, primary_key=True, index=True)
    story_arc_id = Column(Integer, ForeignKey("story_arcs.id"), nullable=False, index=True)
    
    # Location and exploration
    current_location = Column(String(100), nullable=False, default="starting_area")
    explored_areas = Column(JSON, default=list)  # List of discovered locations
    """
    Example explored_areas:
    [
        {
            "name": "village_square",
            "first_visited": "2025-05-22T10:00:00Z",
            "description": "A bustling market square with a stone fountain",
            "notable_features": ["fountain", "market_stalls", "tavern_entrance"],
            "npcs_encountered": ["merchant_karl", "villager_tom"]
        }
    ]
    """
    
    # Environmental state
    world_events = Column(JSON, default=list)  # Major world events that have occurred
    """
    Example world_events:
    [
        {
            "event": "bandit_raid",
            "location": "village_outskirts", 
            "description": "Bandits attacked a merchant caravan",
            "timestamp": "2025-05-22T09:30:00Z",
            "player_involved": true,
            "consequences": ["merchant_grateful", "bandits_hostile"]
        }
    ]
    """
    
    # Quest and objective tracking
    active_objectives = Column(JSON, default=list)  # Current quest objectives
    completed_objectives = Column(JSON, default=list)  # Finished objectives
    """
    Example objectives:
    [
        {
            "id": "rescue_villager",
            "title": "Rescue the Injured Villager",
            "description": "Find healing supplies and tend to Tom's wounds",
            "stage": "inciting_incident",
            "priority": "main",
            "status": "active"
        }
    ]
    """
    
    # Item and loot tracking
    world_items = Column(JSON, default=dict)  # Items discovered in the world
    """
    Example world_items:
    {
        "village_square_fountain": {
            "item": "mysterious_coin",
            "description": "An old coin found at the bottom of the fountain",
            "discovered": false,
            "requires": "investigation_check"
        }
    }
    """
    
    # Time and progression
    story_time_elapsed = Column(Integer, default=0)  # In-game time in minutes
    real_time_played = Column(Integer, default=0)  # Actual play time in minutes
    
    # AI world building context
    established_lore = Column(JSON, default=dict)  # Consistent world details for AI
    """
    Example established_lore:
    {
        "village_name": "Millbrook",
        "kingdom": "Valdris",
        "local_threats": ["bandit_clan_redwolves", "goblin_caves"],
        "notable_figures": ["mayor_helena", "blacksmith_gareth"],
        "economic_base": "farming_and_trade"
    }
    """
    
    # NEW: Dice requirement tracking
    pending_dice_requirement = Column(JSON, default=None)  # Stores required dice roll info
    last_dice_result = Column(JSON, default=None)  # Stores the last dice roll result
    waiting_for_dice = Column(Boolean, default=False)  # Flag indicating if we're waiting for a dice roll
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_updated = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    story_arc = relationship("StoryArc", back_populates="world_states")
    
    def visit_location(self, location_data: dict):
        """Record visiting a new location"""
        if self.explored_areas is None:
            self.explored_areas = []
        
        # Check if already visited
        for area in self.explored_areas:
            if area.get("name") == location_data.get("name"):
                return  # Already explored
        
        location_data.update({
            "first_visited": datetime.utcnow().isoformat()
        })
        self.explored_areas.append(location_data)
    
    def add_world_event(self, event_data: dict):
        """Record a significant world event"""
        if self.world_events is None:
            self.world_events = []
        
        event_data.update({
            "timestamp": datetime.utcnow().isoformat()
        })
        self.world_events.append(event_data)
    
    def add_objective(self, objective_data: dict):
        """Add a new quest objective"""
        if self.active_objectives is None:
            self.active_objectives = []
        
        objective_data.update({
            "id": f"obj_{len(self.active_objectives) + 1}",
            "status": "active",
            "created_at": datetime.utcnow().isoformat()
        })
        self.active_objectives.append(objective_data)
    
    def complete_objective(self, objective_id: str):
        """Mark an objective as completed"""
        if self.active_objectives is None:
            return
        
        if self.completed_objectives is None:
            self.completed_objectives = []
        
        # Find and remove from active
        for i, obj in enumerate(self.active_objectives):
            if obj.get("id") == objective_id:
                obj.update({
                    "status": "completed",
                    "completed_at": datetime.utcnow().isoformat()
                })
                self.completed_objectives.append(obj)
                del self.active_objectives[i]
                break
    
    def establish_lore(self, lore_key: str, lore_value):
        """Add consistent world lore for AI context"""
        if self.established_lore is None:
            self.established_lore = {}
        
        self.established_lore[lore_key] = lore_value
    
    def set_dice_requirement(self, dice_expression: str, purpose: str, dc: int = None, 
                           ability_modifier: int = 0, advantage: bool = False):
        """Set a dice requirement that must be fulfilled before continuing"""
        self.pending_dice_requirement = {
            "dice_expression": dice_expression,
            "purpose": purpose,
            "dc": dc,
            "ability_modifier": ability_modifier,
            "advantage": advantage,
            "created_at": datetime.utcnow().isoformat()
        }
        self.waiting_for_dice = True
        self.last_updated = datetime.utcnow()
    
    def fulfill_dice_requirement(self, dice_result: dict):
        """Fulfill the pending dice requirement with a roll result"""
        if not self.waiting_for_dice or not self.pending_dice_requirement:
            return False
        
        self.last_dice_result = {
            **dice_result,
            "fulfilled_at": datetime.utcnow().isoformat(),
            "requirement": self.pending_dice_requirement
        }
        
        # Clear the requirement
        self.pending_dice_requirement = None
        self.waiting_for_dice = False
        self.last_updated = datetime.utcnow()
        return True
    
    def clear_dice_requirement(self):
        """Clear any pending dice requirement (for error recovery)"""
        self.pending_dice_requirement = None
        self.waiting_for_dice = False
        self.last_updated = datetime.utcnow()
    
    def enter_combat(self, participants: list):
        """Enter combat mode"""
        self.combat_participants = participants
        self.last_updated = datetime.utcnow()
    
    def exit_combat(self):
        """Exit combat mode"""
        self.combat_participants = []
        self.last_updated = datetime.utcnow()
    
    def add_npc(self, npc_name: str, npc_data: dict = None):
        """Add an NPC to the current location"""
        if self.npcs_present is None:
            self.npcs_present = []
        
        npc_entry = {
            "name": npc_name,
            "data": npc_data or {},
            "added_at": datetime.utcnow().isoformat()
        }
        
        # Remove existing entry for same NPC
        self.npcs_present = [npc for npc in self.npcs_present if npc.get("name") != npc_name]
        self.npcs_present.append(npc_entry)
        self.last_updated = datetime.utcnow()
    
    def remove_npc(self, npc_name: str):
        """Remove an NPC from the current location"""
        if self.npcs_present is None:
            return
        
        self.npcs_present = [npc for npc in self.npcs_present if npc.get("name") != npc_name]
        self.last_updated = datetime.utcnow()
    
    def add_item(self, item_name: str, item_data: dict = None):
        """Add an item to the current location"""
        if self.items_available is None:
            self.items_available = []
        
        item_entry = {
            "name": item_name,
            "data": item_data or {},
            "added_at": datetime.utcnow().isoformat()
        }
        
        self.items_available.append(item_entry)
        self.last_updated = datetime.utcnow()
    
    def remove_item(self, item_name: str):
        """Remove an item from the current location"""
        if self.items_available is None:
            return
        
        self.items_available = [item for item in self.items_available if item.get("name") != item_name]
        self.last_updated = datetime.utcnow()
    
    def set_flag(self, flag_name: str, value: any):
        """Set a location-specific flag"""
        if self.location_flags is None:
            self.location_flags = {}
        
        self.location_flags[flag_name] = value
        self.last_updated = datetime.utcnow()
    
    def get_flag(self, flag_name: str, default_value: any = None):
        """Get a location-specific flag value"""
        if self.location_flags is None:
            return default_value
        
        return self.location_flags.get(flag_name, default_value) 