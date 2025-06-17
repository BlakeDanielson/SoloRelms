from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import traceback

from database import get_db
from services.combat import CombatService
from services.dice_service import DiceService, AdvantageType as ServiceAdvantageType
from schemas.combat import (
    EnemyTemplateCreate, EnemyTemplateUpdate, EnemyTemplate as EnemyTemplateResponse,
    CombatEncounterCreate, CombatEncounterUpdate, CombatEncounter as CombatEncounterResponse,
    CombatParticipantCreate, CombatParticipantUpdate, CombatParticipant as CombatParticipantResponse,
    DamageRequest, HealingRequest, AddConditionRequest, CombatActionRequest,
    CombatActionResponse, InitiativeRollRequest, InitiativeRollResponse,
    CombatSummary, InitiativeParticipant
)
from schemas.dice import AttackRollRequest, AttackRollResponse, AdvantageType
from auth import get_current_user

router = APIRouter(prefix="/api/combat", tags=["combat"])

def get_combat_service(db: Session = Depends(get_db)) -> CombatService:
    """Dependency to get CombatService instance"""
    return CombatService(db)

# Enemy Template Endpoints
@router.post("/enemy-templates", response_model=EnemyTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_enemy_template(
    template_data: EnemyTemplateCreate,
    combat_service: CombatService = Depends(get_combat_service)
):
    """Create a new enemy template"""
    try:
        template = combat_service.create_enemy_template(template_data)
        return template
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create enemy template: {str(e)}")

@router.get("/enemy-templates/{template_id}", response_model=EnemyTemplateResponse)
async def get_enemy_template(
    template_id: int,
    combat_service: CombatService = Depends(get_combat_service)
):
    """Get enemy template by ID"""
    template = combat_service.get_enemy_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Enemy template not found")
    return template

@router.get("/enemy-templates", response_model=List[EnemyTemplateResponse])
async def list_enemy_templates(
    skip: int = 0,
    limit: int = 100,
    creature_type: Optional[str] = None,
    challenge_rating_min: Optional[float] = None,
    challenge_rating_max: Optional[float] = None,
    combat_service: CombatService = Depends(get_combat_service)
):
    """List enemy templates with optional filtering"""
    templates = combat_service.get_enemy_templates(
        skip=skip,
        limit=limit,
        creature_type=creature_type,
        challenge_rating_min=challenge_rating_min,
        challenge_rating_max=challenge_rating_max
    )
    return templates

@router.put("/enemy-templates/{template_id}", response_model=EnemyTemplateResponse)
async def update_enemy_template(
    template_id: int,
    template_data: EnemyTemplateUpdate,
    combat_service: CombatService = Depends(get_combat_service)
):
    """Update an enemy template"""
    template = combat_service.update_enemy_template(template_id, template_data)
    if not template:
        raise HTTPException(status_code=404, detail="Enemy template not found")
    return template

@router.delete("/enemy-templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_enemy_template(
    template_id: int,
    combat_service: CombatService = Depends(get_combat_service)
):
    """Delete an enemy template"""
    success = combat_service.delete_enemy_template(template_id)
    if not success:
        raise HTTPException(status_code=404, detail="Enemy template not found")

# Combat Encounter Endpoints
@router.post("/encounters", response_model=CombatEncounterResponse, status_code=status.HTTP_201_CREATED)
async def create_combat_encounter(
    encounter_data: CombatEncounterCreate,
    combat_service: CombatService = Depends(get_combat_service)
):
    """Create a new combat encounter"""
    try:
        encounter = combat_service.create_combat_encounter(encounter_data)
        return encounter
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create combat encounter: {str(e)}")

@router.get("/encounters/{encounter_id}", response_model=CombatEncounterResponse)
async def get_combat_encounter(
    encounter_id: int,
    combat_service: CombatService = Depends(get_combat_service)
):
    """Get combat encounter by ID"""
    encounter = combat_service.get_combat_encounter(encounter_id)
    if not encounter:
        raise HTTPException(status_code=404, detail="Combat encounter not found")
    return encounter

@router.get("/characters/{character_id}/encounters", response_model=List[CombatEncounterResponse])
async def get_character_encounters(
    character_id: int,
    combat_service: CombatService = Depends(get_combat_service)
):
    """Get all combat encounters for a character"""
    encounters = combat_service.get_combat_encounters_by_character(character_id)
    return encounters

@router.get("/characters/{character_id}/encounters/active", response_model=Optional[CombatEncounterResponse])
async def get_active_encounter(
    character_id: int,
    combat_service: CombatService = Depends(get_combat_service)
):
    """Get the active combat encounter for a character"""
    encounter = combat_service.get_active_combat_encounter(character_id)
    return encounter

@router.post("/encounters/{encounter_id}/start", response_model=CombatEncounterResponse)
async def start_combat_encounter(
    encounter_id: int,
    combat_service: CombatService = Depends(get_combat_service)
):
    """Start a combat encounter"""
    encounter = combat_service.start_combat_encounter(encounter_id)
    if not encounter:
        raise HTTPException(status_code=404, detail="Combat encounter not found")
    return encounter

@router.post("/encounters/{encounter_id}/end", response_model=CombatEncounterResponse)
async def end_combat_encounter(
    encounter_id: int,
    result: str,
    xp_awarded: int = 0,
    loot: List[Dict[str, Any]] = None,
    combat_service: CombatService = Depends(get_combat_service)
):
    """End a combat encounter"""
    encounter = combat_service.end_combat_encounter(encounter_id, result, xp_awarded, loot or [])
    if not encounter:
        raise HTTPException(status_code=404, detail="Combat encounter not found")
    return encounter

@router.put("/encounters/{encounter_id}", response_model=CombatEncounterResponse)
async def update_combat_encounter(
    encounter_id: int,
    encounter_data: CombatEncounterUpdate,
    combat_service: CombatService = Depends(get_combat_service)
):
    """Update a combat encounter"""
    encounter = combat_service.update_combat_encounter(encounter_id, encounter_data)
    if not encounter:
        raise HTTPException(status_code=404, detail="Combat encounter not found")
    return encounter

# Combat Participant Endpoints
@router.post("/encounters/{encounter_id}/participants", response_model=CombatParticipantResponse, status_code=status.HTTP_201_CREATED)
async def create_combat_participant(
    encounter_id: int,
    participant_data: CombatParticipantCreate,
    combat_service: CombatService = Depends(get_combat_service)
):
    """Create a new combat participant"""
    try:
        participant_data.combat_encounter_id = encounter_id
        participant = combat_service.create_combat_participant(participant_data)
        return participant
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create combat participant: {str(e)}")

@router.post("/encounters/{encounter_id}/participants/character/{character_id}", response_model=CombatParticipantResponse, status_code=status.HTTP_201_CREATED)
async def add_character_to_encounter(
    encounter_id: int,
    character_id: int,
    initiative: Optional[int] = None,
    combat_service: CombatService = Depends(get_combat_service)
):
    """Add a character to a combat encounter"""
    try:
        participant = combat_service.create_character_participant(encounter_id, character_id, initiative)
        return participant
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add character to encounter: {str(e)}")

@router.post("/encounters/{encounter_id}/participants/enemy/{template_id}", response_model=CombatParticipantResponse, status_code=status.HTTP_201_CREATED)
async def add_enemy_to_encounter(
    encounter_id: int,
    template_id: int,
    name_suffix: str = "",
    initiative: Optional[int] = None,
    combat_service: CombatService = Depends(get_combat_service)
):
    """Add an enemy to a combat encounter"""
    try:
        participant = combat_service.create_enemy_participant(encounter_id, template_id, name_suffix, initiative)
        return participant
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add enemy to encounter: {str(e)}")

@router.get("/encounters/{encounter_id}/participants", response_model=List[CombatParticipantResponse])
async def get_encounter_participants(
    encounter_id: int,
    combat_service: CombatService = Depends(get_combat_service)
):
    """Get all participants in a combat encounter"""
    participants = combat_service.get_combat_participants_by_encounter(encounter_id)
    return participants

@router.get("/participants/{participant_id}", response_model=CombatParticipantResponse)
async def get_combat_participant(
    participant_id: int,
    combat_service: CombatService = Depends(get_combat_service)
):
    """Get combat participant by ID"""
    participant = combat_service.get_combat_participant(participant_id)
    if not participant:
        raise HTTPException(status_code=404, detail="Combat participant not found")
    return participant

@router.put("/participants/{participant_id}", response_model=CombatParticipantResponse)
async def update_combat_participant(
    participant_id: int,
    participant_data: CombatParticipantUpdate,
    combat_service: CombatService = Depends(get_combat_service)
):
    """Update a combat participant"""
    participant = combat_service.update_combat_participant(participant_id, participant_data)
    if not participant:
        raise HTTPException(status_code=404, detail="Combat participant not found")
    return participant

# Combat Action Endpoints
@router.post("/participants/{participant_id}/damage", response_model=CombatActionResponse)
async def apply_damage(
    participant_id: int,
    damage_request: DamageRequest,
    combat_service: CombatService = Depends(get_combat_service)
):
    """Apply damage to a combat participant"""
    damage_request.participant_id = participant_id
    response = combat_service.apply_damage(damage_request)
    if not response.success:
        raise HTTPException(status_code=404, detail=response.description)
    return response

@router.post("/participants/{participant_id}/heal", response_model=CombatActionResponse)
async def apply_healing(
    participant_id: int,
    healing_request: HealingRequest,
    combat_service: CombatService = Depends(get_combat_service)
):
    """Apply healing to a combat participant"""
    healing_request.participant_id = participant_id
    response = combat_service.apply_healing(healing_request)
    if not response.success:
        raise HTTPException(status_code=404, detail=response.description)
    return response

@router.post("/participants/{participant_id}/conditions", response_model=CombatActionResponse)
async def add_condition(
    participant_id: int,
    condition_request: AddConditionRequest,
    combat_service: CombatService = Depends(get_combat_service)
):
    """Add a condition to a combat participant"""
    condition_request.participant_id = participant_id
    response = combat_service.add_condition(condition_request)
    if not response.success:
        raise HTTPException(status_code=404, detail=response.description)
    return response

@router.delete("/participants/{participant_id}/conditions/{condition_name}", response_model=CombatActionResponse)
async def remove_condition(
    participant_id: int,
    condition_name: str,
    combat_service: CombatService = Depends(get_combat_service)
):
    """Remove a condition from a combat participant"""
    response = combat_service.remove_condition(participant_id, condition_name)
    if not response.success:
        raise HTTPException(status_code=404, detail=response.description)
    return response

# Attack Action with Dice Integration
@router.post("/participants/{attacker_id}/attack/{target_id}", response_model=Dict[str, Any])
async def perform_attack(
    attacker_id: int,
    target_id: int,
    attack_bonus: int,
    damage_notation: str,
    advantage_type: AdvantageType = AdvantageType.NORMAL,
    critical_range: int = 20,
    description: str = "",
    combat_service: CombatService = Depends(get_combat_service)
):
    """Perform a complete attack action with dice rolling and damage resolution"""
    try:
        # Get participants
        attacker = combat_service.get_combat_participant(attacker_id)
        target = combat_service.get_combat_participant(target_id)
        
        if not attacker:
            raise HTTPException(status_code=404, detail="Attacker not found")
        if not target:
            raise HTTPException(status_code=404, detail="Target not found")
        
        # Convert advantage type
        service_advantage = ServiceAdvantageType.NORMAL
        if advantage_type == AdvantageType.ADVANTAGE:
            service_advantage = ServiceAdvantageType.ADVANTAGE
        elif advantage_type == AdvantageType.DISADVANTAGE:
            service_advantage = ServiceAdvantageType.DISADVANTAGE
        
        # Make attack roll using dice service
        attack_result = DiceService.make_attack_roll(
            attack_bonus=attack_bonus,
            damage_notation=damage_notation,
            target_ac=target.armor_class,
            advantage_type=service_advantage,
            critical_range=critical_range
        )
        
        # Apply damage if hit
        damage_response = None
        if attack_result.is_hit and attack_result.damage_roll:
            damage_request = DamageRequest(
                participant_id=target_id,
                damage=attack_result.damage_roll.total
            )
            damage_response = combat_service.apply_damage(damage_request)
        
        # Log the combat action
        action_data = {
            "attacker_id": attacker_id,
            "target_id": target_id,
            "action_type": "attack",
            "attack_roll": attack_result.attack_roll.total,
            "damage": attack_result.damage_roll.total if attack_result.damage_roll else 0,
            "is_hit": attack_result.is_hit,
            "is_critical": attack_result.is_critical,
            "description": description or f"{attacker.name} attacks {target.name}"
        }
        combat_service.log_combat_action(attacker.combat_encounter_id, action_data)
        
        return {
            "attack_result": {
                "attack_roll": {
                    "total": attack_result.attack_roll.total,
                    "individual_rolls": attack_result.attack_roll.individual_rolls,
                    "dice_notation": attack_result.attack_roll.dice_notation,
                    "modifier": attack_result.attack_roll.modifier,
                    "advantage_type": attack_result.attack_roll.advantage_type.value,
                    "description": attack_result.attack_roll.description
                },
                "damage_roll": {
                    "total": attack_result.damage_roll.total,
                    "individual_rolls": attack_result.damage_roll.individual_rolls,
                    "dice_notation": attack_result.damage_roll.dice_notation,
                    "modifier": attack_result.damage_roll.modifier,
                    "description": attack_result.damage_roll.description
                } if attack_result.damage_roll else None,
                "is_critical": attack_result.is_critical,
                "is_hit": attack_result.is_hit,
                "target_ac": attack_result.target_ac
            },
            "damage_response": damage_response.model_dump() if damage_response else None,
            "attacker": attacker.name,
            "target": target.name,
            "description": action_data["description"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Attack failed: {str(e)}")

# Initiative and Turn Management
@router.post("/encounters/{encounter_id}/initiative", response_model=InitiativeRollResponse)
async def roll_initiative(
    encounter_id: int,
    initiative_request: InitiativeRollRequest,
    combat_service: CombatService = Depends(get_combat_service)
):
    """Roll initiative for combat participants"""
    try:
        response = combat_service.roll_initiative(encounter_id, initiative_request.participant_ids)
        return response
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Initiative roll failed: {str(e)}")

@router.post("/encounters/{encounter_id}/advance-turn", response_model=CombatEncounterResponse)
async def advance_turn(
    encounter_id: int,
    combat_service: CombatService = Depends(get_combat_service)
):
    """Advance to the next participant's turn"""
    encounter = combat_service.advance_turn(encounter_id)
    if not encounter:
        raise HTTPException(status_code=404, detail="Combat encounter not found")
    return encounter

# Combat Summary and Status
@router.get("/encounters/{encounter_id}/summary", response_model=CombatSummary)
async def get_combat_summary(
    encounter_id: int,
    combat_service: CombatService = Depends(get_combat_service)
):
    """Get a summary of the combat encounter"""
    summary = combat_service.get_combat_summary(encounter_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Combat encounter not found")
    return summary

@router.get("/encounters/{encounter_id}/xp-reward")
async def calculate_xp_reward(
    encounter_id: int,
    combat_service: CombatService = Depends(get_combat_service)
):
    """Calculate XP reward for the encounter"""
    xp = combat_service.calculate_xp_reward(encounter_id)
    return {"encounter_id": encounter_id, "xp_reward": xp}

@router.get("/encounters/{encounter_id}/loot")
async def generate_loot(
    encounter_id: int,
    combat_service: CombatService = Depends(get_combat_service)
):
    """Generate loot for the encounter"""
    loot = combat_service.generate_loot(encounter_id)
    return {"encounter_id": encounter_id, "loot": loot}

# Utility Endpoints
@router.post("/encounters/{encounter_id}/log", status_code=status.HTTP_201_CREATED)
async def log_combat_action(
    encounter_id: int,
    action_data: Dict[str, Any],
    combat_service: CombatService = Depends(get_combat_service)
):
    """Log a combat action"""
    success = combat_service.log_combat_action(encounter_id, action_data)
    if not success:
        raise HTTPException(status_code=404, detail="Combat encounter not found")
    return {"message": "Action logged successfully"} 