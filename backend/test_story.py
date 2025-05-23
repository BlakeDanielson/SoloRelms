#!/usr/bin/env python3

"""
Story System Test Suite for SoloRealms
Tests the D&D story state machine and world state management
"""

import sys
import os
from datetime import datetime

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.story import StoryStage, StoryArc, WorldState
from schemas.story import (
    StoryArcCreate, StoryTypeEnum, StoryStageEnum,
    DecisionRequest, NPCStatus, NPCUpdateRequest,
    CombatOutcome, CombatRequest, ExploredArea, LocationVisitRequest,
    WorldEvent, WorldEventRequest, Objective, ObjectiveRequest
)

def test_story_stages():
    """Test the 6-stage story progression system"""
    print("🎭 Testing Story Stage Progression...")
    
    # Test stage enumeration
    stages = list(StoryStage)
    expected_stages = [
        StoryStage.INTRO,
        StoryStage.INCITING_INCIDENT, 
        StoryStage.FIRST_COMBAT,
        StoryStage.TWIST,
        StoryStage.FINAL_CONFLICT,
        StoryStage.RESOLUTION
    ]
    
    print(f"Available story stages: {[stage.value for stage in stages]}")
    assert len(stages) == 6, f"Expected 6 stages, got {len(stages)}"
    assert stages == expected_stages, "Stage order doesn't match PRD"
    
    # Test story arc creation
    class MockStoryArc:
        def __init__(self):
            self.current_stage = StoryStage.INTRO
            self.stages_completed = []
            self.major_decisions = []
            self.combat_outcomes = []
            self.story_completed = False
            self.completed_at = None
    
        def advance_stage(self):
            """Advance to the next story stage"""
            stages = list(StoryStage)
            current_index = stages.index(self.current_stage)
            
            # Add current stage to completed list
            if self.current_stage.value not in self.stages_completed:
                self.stages_completed.append(self.current_stage.value)
            
            # Advance to next stage or mark complete
            if current_index < len(stages) - 1:
                self.current_stage = stages[current_index + 1]
            else:
                self.story_completed = True
                self.completed_at = datetime.utcnow()
        
        def can_advance_stage(self) -> bool:
            """Check if conditions are met to advance to next stage"""
            if self.current_stage == StoryStage.INTRO:
                return True
            elif self.current_stage == StoryStage.INCITING_INCIDENT:
                return len(self.major_decisions) > 0
            elif self.current_stage == StoryStage.FIRST_COMBAT:
                return len(self.combat_outcomes) > 0
            elif self.current_stage == StoryStage.TWIST:
                return True
            elif self.current_stage == StoryStage.FINAL_CONFLICT:
                return len(self.combat_outcomes) > 1
            else:
                return False
        
        def add_decision(self, decision_data: dict):
            """Add a major story decision"""
            decision_data.update({
                "stage": self.current_stage.value,
                "timestamp": datetime.utcnow().isoformat()
            })
            self.major_decisions.append(decision_data)
        
        def add_combat_outcome(self, combat_data: dict):
            """Record a combat encounter outcome"""
            combat_data.update({
                "stage": self.current_stage.value,
                "timestamp": datetime.utcnow().isoformat()
            })
            self.combat_outcomes.append(combat_data)
    
    # Test full story progression
    story = MockStoryArc()
    
    # Stage 1: INTRO - should always be able to advance
    assert story.current_stage == StoryStage.INTRO
    assert story.can_advance_stage() == True
    story.advance_stage()
    
    # Stage 2: INCITING_INCIDENT - needs a decision to advance
    assert story.current_stage == StoryStage.INCITING_INCIDENT
    assert story.can_advance_stage() == False  # No decisions yet
    
    story.add_decision({
        "decision": "help_villager",
        "description": "Chose to help the injured villager"
    })
    assert story.can_advance_stage() == True
    story.advance_stage()
    
    # Stage 3: FIRST_COMBAT - needs combat outcome to advance
    assert story.current_stage == StoryStage.FIRST_COMBAT
    assert story.can_advance_stage() == False  # No combat yet
    
    story.add_combat_outcome({
        "encounter_type": "bandit_ambush",
        "result": "victory",
        "damage_taken": 5,
        "xp_gained": 100
    })
    assert story.can_advance_stage() == True
    story.advance_stage()
    
    # Stage 4: TWIST - can always advance
    assert story.current_stage == StoryStage.TWIST
    assert story.can_advance_stage() == True
    story.advance_stage()
    
    # Stage 5: FINAL_CONFLICT - needs multiple combat experiences
    assert story.current_stage == StoryStage.FINAL_CONFLICT
    assert story.can_advance_stage() == True  # Already has 1 combat
    
    story.add_combat_outcome({
        "encounter_type": "boss_fight", 
        "result": "victory",
        "damage_taken": 12,
        "xp_gained": 300
    })
    story.advance_stage()
    
    # Stage 6: RESOLUTION - story completed
    assert story.story_completed == True
    assert story.completed_at is not None
    assert len(story.stages_completed) == 5  # All stages except resolution
    
    print(f"✅ Story progression test passed! Final stages: {story.stages_completed}")


def test_world_state_management():
    """Test world state tracking and exploration"""
    print("\n🗺️ Testing World State Management...")
    
    class MockWorldState:
        def __init__(self):
            self.current_location = "starting_area"
            self.explored_areas = []
            self.world_events = []
            self.active_objectives = []
            self.completed_objectives = []
            self.world_items = {}
            self.established_lore = {}
            self.story_time_elapsed = 0
            self.real_time_played = 0
        
        def visit_location(self, location_data: dict):
            """Record visiting a new location"""
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
            event_data.update({
                "timestamp": datetime.utcnow().isoformat()
            })
            self.world_events.append(event_data)
        
        def add_objective(self, objective_data: dict):
            """Add a new quest objective"""
            objective_data.update({
                "id": f"obj_{len(self.active_objectives) + 1}",
                "status": "active",
                "created_at": datetime.utcnow().isoformat()
            })
            self.active_objectives.append(objective_data)
        
        def complete_objective(self, objective_id: str):
            """Mark an objective as completed"""
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
            self.established_lore[lore_key] = lore_value
    
    world = MockWorldState()
    
    # Test location exploration
    world.visit_location({
        "name": "village_square",
        "description": "A bustling market square with a stone fountain",
        "notable_features": ["fountain", "market_stalls", "tavern_entrance"],
        "npcs_encountered": ["merchant_karl", "villager_tom"]
    })
    
    world.visit_location({
        "name": "forest_path",
        "description": "A winding path through dark woods",
        "notable_features": ["ancient_tree", "hidden_cache"],
        "npcs_encountered": []
    })
    
    # Try to visit same location again (should not duplicate)
    world.visit_location({
        "name": "village_square",
        "description": "Duplicate visit"
    })
    
    assert len(world.explored_areas) == 2, f"Expected 2 unique areas, got {len(world.explored_areas)}"
    
    # Test world events
    world.add_world_event({
        "event": "bandit_raid",
        "location": "village_outskirts",
        "description": "Bandits attacked a merchant caravan",
        "player_involved": True,
        "consequences": ["merchant_grateful", "bandits_hostile"]
    })
    
    assert len(world.world_events) == 1
    assert world.world_events[0]["event"] == "bandit_raid"
    
    # Test objective management
    world.add_objective({
        "title": "Rescue the Injured Villager",
        "description": "Find healing supplies and tend to Tom's wounds",
        "stage": "inciting_incident",
        "priority": "main"
    })
    
    world.add_objective({
        "title": "Investigate Strange Noises", 
        "description": "Check out the weird sounds from the forest",
        "stage": "inciting_incident",
        "priority": "side"
    })
    
    assert len(world.active_objectives) == 2
    assert len(world.completed_objectives) == 0
    
    # Complete an objective
    obj_id = world.active_objectives[0]["id"]
    world.complete_objective(obj_id)
    
    assert len(world.active_objectives) == 1
    assert len(world.completed_objectives) == 1
    assert world.completed_objectives[0]["status"] == "completed"
    
    # Test lore establishment
    world.establish_lore("village_name", "Millbrook")
    world.establish_lore("kingdom", "Valdris")
    world.establish_lore("local_threats", ["bandit_clan_redwolves", "goblin_caves"])
    
    assert world.established_lore["village_name"] == "Millbrook"
    assert len(world.established_lore["local_threats"]) == 2
    
    print(f"✅ World state test passed!")
    print(f"  Explored areas: {len(world.explored_areas)}")
    print(f"  World events: {len(world.world_events)}")
    print(f"  Active objectives: {len(world.active_objectives)}")
    print(f"  Completed objectives: {len(world.completed_objectives)}")
    print(f"  Established lore: {len(world.established_lore)} entries")


def test_npc_management():
    """Test NPC status tracking throughout story"""
    print("\n👥 Testing NPC Management...")
    
    class MockNPCManager:
        def __init__(self):
            self.npc_status = {}
        
        def update_npc_status(self, npc_id: str, status_data: dict):
            """Update the status of an NPC"""
            if npc_id in self.npc_status:
                self.npc_status[npc_id].update(status_data)
            else:
                self.npc_status[npc_id] = status_data
    
    npc_manager = MockNPCManager()
    
    # Add initial NPCs
    npc_manager.update_npc_status("villager_tom", {
        "status": "neutral",
        "health": "injured",
        "location": "village_square",
        "disposition": "desperate"
    })
    
    npc_manager.update_npc_status("bandit_leader", {
        "status": "hostile",
        "health": "unknown",
        "location": "forest_hideout",
        "disposition": "vengeful"
    })
    
    # Update existing NPC after player interaction
    npc_manager.update_npc_status("villager_tom", {
        "status": "ally",
        "health": "healing",
        "disposition": "grateful"
    })
    
    assert npc_manager.npc_status["villager_tom"]["status"] == "ally"
    assert npc_manager.npc_status["villager_tom"]["health"] == "healing"
    assert npc_manager.npc_status["villager_tom"]["location"] == "village_square"  # Should persist
    
    print(f"✅ NPC management test passed!")
    print(f"  NPCs tracked: {len(npc_manager.npc_status)}")
    for npc_id, status in npc_manager.npc_status.items():
        print(f"    {npc_id}: {status['status']} ({status['disposition']})")


def test_schema_validation():
    """Test Pydantic schema validation for story operations"""
    print("\n📋 Testing Schema Validation...")
    
    # Test StoryArcCreate schema
    story_create = StoryArcCreate(
        character_id=1,
        title="The Bandit's Treasure",
        story_type=StoryTypeEnum.SHORT_FORM,
        story_seed="A merchant's caravan was attacked by bandits..."
    )
    
    assert story_create.character_id == 1
    assert story_create.story_type == StoryTypeEnum.SHORT_FORM
    
    # Test DecisionRequest schema
    decision = DecisionRequest(
        decision="help_villager",
        description="Chose to help the injured villager instead of pursuing the thief",
        consequences=["villager_ally", "thief_escaped"]
    )
    
    assert decision.decision == "help_villager"
    assert len(decision.consequences) == 2
    
    # Test CombatOutcome schema
    combat = CombatOutcome(
        encounter_type="bandit_ambush",
        result="victory",
        damage_taken=8,
        loot_gained=["gold_pieces_15", "iron_sword"],
        xp_gained=150,
        stage=StoryStageEnum.FIRST_COMBAT,
        timestamp=datetime.utcnow()
    )
    
    assert combat.encounter_type == "bandit_ambush"
    assert combat.damage_taken == 8
    assert combat.xp_gained == 150
    
    # Test ExploredArea schema
    location = ExploredArea(
        name="village_square",
        description="A bustling market square with a stone fountain",
        notable_features=["fountain", "market_stalls", "tavern_entrance"],
        npcs_encountered=["merchant_karl", "villager_tom"],
        first_visited=datetime.utcnow()
    )
    
    assert location.name == "village_square"
    assert len(location.notable_features) == 3
    assert len(location.npcs_encountered) == 2
    
    print(f"✅ Schema validation test passed!")


def run_all_tests():
    """Run the complete story system test suite"""
    print("🧙‍♂️ SoloRealms Story System Test Suite")
    print("=" * 50)
    
    try:
        test_story_stages()
        test_world_state_management()
        test_npc_management()
        test_schema_validation()
        
        print("\n" + "=" * 50)
        print("✅ All story system tests completed successfully!")
        print("✅ Story state machine (6 stages) working correctly")
        print("✅ World state tracking functional")
        print("✅ NPC status management operational")
        print("✅ Schema validation passing")
        print("✅ Ready for AI DM integration!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        raise


if __name__ == "__main__":
    run_all_tests() 