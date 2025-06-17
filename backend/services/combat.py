from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Dict, Any
import random
from datetime import datetime

from models.combat import EnemyTemplate, CombatEncounter, CombatParticipant, CombatState, ActionType
from models.character import Character
from models.story import StoryArc
from schemas.combat import (
    EnemyTemplateCreate, EnemyTemplateUpdate, EnemyTemplate as EnemyTemplateSchema,
    CombatEncounterCreate, CombatEncounterUpdate, CombatEncounter as CombatEncounterSchema,
    CombatParticipantCreate, CombatParticipantUpdate, CombatParticipant as CombatParticipantSchema,
    DamageRequest, HealingRequest, AddConditionRequest, CombatActionRequest,
    CombatActionResponse, InitiativeRollRequest, InitiativeRollResponse,
    CombatSummary, InitiativeParticipant
)

class CombatService:
    """Service for managing combat encounters, enemy templates, and combat participants"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # Enemy Template Management
    def create_enemy_template(self, template_data: EnemyTemplateCreate) -> EnemyTemplate:
        """Create a new enemy template"""
        db_template = EnemyTemplate(**template_data.model_dump())
        self.db.add(db_template)
        self.db.commit()
        self.db.refresh(db_template)
        return db_template
    
    def get_enemy_template(self, template_id: int) -> Optional[EnemyTemplate]:
        """Get enemy template by ID"""
        return self.db.query(EnemyTemplate).filter(EnemyTemplate.id == template_id).first()
    
    def get_enemy_templates(
        self, 
        skip: int = 0, 
        limit: int = 100,
        creature_type: Optional[str] = None,
        challenge_rating_min: Optional[float] = None,
        challenge_rating_max: Optional[float] = None
    ) -> List[EnemyTemplate]:
        """Get enemy templates with optional filtering"""
        query = self.db.query(EnemyTemplate)
        
        if creature_type:
            query = query.filter(EnemyTemplate.creature_type == creature_type)
        if challenge_rating_min is not None:
            query = query.filter(EnemyTemplate.challenge_rating >= challenge_rating_min)
        if challenge_rating_max is not None:
            query = query.filter(EnemyTemplate.challenge_rating <= challenge_rating_max)
        
        return query.offset(skip).limit(limit).all()
    
    def update_enemy_template(self, template_id: int, template_data: EnemyTemplateUpdate) -> Optional[EnemyTemplate]:
        """Update an enemy template"""
        db_template = self.get_enemy_template(template_id)
        if not db_template:
            return None
        
        update_data = template_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_template, field, value)
        
        self.db.commit()
        self.db.refresh(db_template)
        return db_template
    
    def delete_enemy_template(self, template_id: int) -> bool:
        """Delete an enemy template"""
        db_template = self.get_enemy_template(template_id)
        if not db_template:
            return False
        
        self.db.delete(db_template)
        self.db.commit()
        return True
    
    # Combat Encounter Management
    def create_combat_encounter(self, encounter_data: CombatEncounterCreate) -> CombatEncounter:
        """Create a new combat encounter"""
        db_encounter = CombatEncounter(**encounter_data.model_dump())
        self.db.add(db_encounter)
        self.db.commit()
        self.db.refresh(db_encounter)
        return db_encounter
    
    def get_combat_encounter(self, encounter_id: int) -> Optional[CombatEncounter]:
        """Get combat encounter by ID"""
        return self.db.query(CombatEncounter).filter(CombatEncounter.id == encounter_id).first()
    
    def get_combat_encounters_by_character(self, character_id: int) -> List[CombatEncounter]:
        """Get all combat encounters for a character"""
        return self.db.query(CombatEncounter).filter(CombatEncounter.character_id == character_id).all()
    
    def get_active_combat_encounter(self, character_id: int) -> Optional[CombatEncounter]:
        """Get the active combat encounter for a character"""
        return self.db.query(CombatEncounter).filter(
            and_(
                CombatEncounter.character_id == character_id,
                CombatEncounter.combat_state.in_([CombatState.INITIATIVE, CombatState.IN_PROGRESS])
            )
        ).first()
    
    def update_combat_encounter(self, encounter_id: int, encounter_data: CombatEncounterUpdate) -> Optional[CombatEncounter]:
        """Update a combat encounter"""
        db_encounter = self.get_combat_encounter(encounter_id)
        if not db_encounter:
            return None
        
        update_data = encounter_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_encounter, field, value)
        
        self.db.commit()
        self.db.refresh(db_encounter)
        return db_encounter
    
    def start_combat_encounter(self, encounter_id: int) -> Optional[CombatEncounter]:
        """Start a combat encounter"""
        db_encounter = self.get_combat_encounter(encounter_id)
        if not db_encounter:
            return None
        
        db_encounter.start_combat()
        self.db.commit()
        self.db.refresh(db_encounter)
        return db_encounter
    
    def end_combat_encounter(self, encounter_id: int, result: str, xp_awarded: int = 0, loot: List[Dict] = None) -> Optional[CombatEncounter]:
        """End a combat encounter"""
        db_encounter = self.get_combat_encounter(encounter_id)
        if not db_encounter:
            return None
        
        db_encounter.end_combat(result, xp_awarded, loot or [])
        self.db.commit()
        self.db.refresh(db_encounter)
        return db_encounter
    
    # Combat Participant Management
    def create_combat_participant(self, participant_data: CombatParticipantCreate) -> CombatParticipant:
        """Create a new combat participant"""
        db_participant = CombatParticipant(**participant_data.model_dump())
        self.db.add(db_participant)
        self.db.commit()
        self.db.refresh(db_participant)
        return db_participant
    
    def get_combat_participant(self, participant_id: int) -> Optional[CombatParticipant]:
        """Get combat participant by ID"""
        return self.db.query(CombatParticipant).filter(CombatParticipant.id == participant_id).first()
    
    def get_combat_participants_by_encounter(self, encounter_id: int) -> List[CombatParticipant]:
        """Get all participants in a combat encounter"""
        return self.db.query(CombatParticipant).filter(CombatParticipant.combat_encounter_id == encounter_id).all()
    
    def update_combat_participant(self, participant_id: int, participant_data: CombatParticipantUpdate) -> Optional[CombatParticipant]:
        """Update a combat participant"""
        db_participant = self.get_combat_participant(participant_id)
        if not db_participant:
            return None
        
        update_data = participant_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_participant, field, value)
        
        self.db.commit()
        self.db.refresh(db_participant)
        return db_participant
    
    def create_character_participant(self, encounter_id: int, character_id: int, initiative: int = None) -> CombatParticipant:
        """Create a combat participant from a character"""
        character = self.db.query(Character).filter(Character.id == character_id).first()
        if not character:
            raise ValueError(f"Character with ID {character_id} not found")
        
        if initiative is None:
            initiative = random.randint(1, 20) + character.dexterity_modifier
        
        participant_data = CombatParticipantCreate(
            combat_encounter_id=encounter_id,
            participant_type="character",
            character_id=character_id,
            name=character.name,
            max_hit_points=character.max_hit_points,
            current_hit_points=character.current_hit_points,
            armor_class=character.armor_class,
            initiative=initiative
        )
        
        return self.create_combat_participant(participant_data)
    
    def create_enemy_participant(self, encounter_id: int, template_id: int, name_suffix: str = "", initiative: int = None) -> CombatParticipant:
        """Create a combat participant from an enemy template"""
        template = self.get_enemy_template(template_id)
        if not template:
            raise ValueError(f"Enemy template with ID {template_id} not found")
        
        if initiative is None:
            initiative = random.randint(1, 20) + template.dexterity_modifier
        
        display_name = f"{template.name}{' ' + name_suffix if name_suffix else ''}"
        
        participant_data = CombatParticipantCreate(
            combat_encounter_id=encounter_id,
            participant_type="enemy",
            enemy_template_id=template_id,
            name=display_name,
            max_hit_points=template.hit_points,
            current_hit_points=template.hit_points,
            armor_class=template.armor_class,
            initiative=initiative
        )
        
        return self.create_combat_participant(participant_data)
    
    # Combat Actions
    def apply_damage(self, damage_request: DamageRequest) -> CombatActionResponse:
        """Apply damage to a combat participant"""
        participant = self.get_combat_participant(damage_request.participant_id)
        if not participant:
            return CombatActionResponse(
                success=False,
                description=f"Participant {damage_request.participant_id} not found"
            )
        
        old_hp = participant.current_hit_points
        participant.take_damage(damage_request.damage)
        self.db.commit()
        
        response = CombatActionResponse(
            success=True,
            description=f"{participant.name} takes {damage_request.damage} damage",
            damage_dealt=damage_request.damage,
            participant_eliminated=not participant.is_active
        )
        
        if not participant.is_active:
            response.description += f" and is eliminated!"
        
        return response
    
    def apply_healing(self, healing_request: HealingRequest) -> CombatActionResponse:
        """Apply healing to a combat participant"""
        participant = self.get_combat_participant(healing_request.participant_id)
        if not participant:
            return CombatActionResponse(
                success=False,
                description=f"Participant {healing_request.participant_id} not found"
            )
        
        old_hp = participant.current_hit_points
        participant.heal(healing_request.amount)
        actual_healing = participant.current_hit_points - old_hp
        self.db.commit()
        
        return CombatActionResponse(
            success=True,
            description=f"{participant.name} heals {actual_healing} hit points",
            healing_done=actual_healing
        )
    
    def add_condition(self, condition_request: AddConditionRequest) -> CombatActionResponse:
        """Add a condition to a combat participant"""
        participant = self.get_combat_participant(condition_request.participant_id)
        if not participant:
            return CombatActionResponse(
                success=False,
                description=f"Participant {condition_request.participant_id} not found"
            )
        
        condition_data = condition_request.condition.model_dump()
        participant.add_condition(condition_data)
        self.db.commit()
        
        return CombatActionResponse(
            success=True,
            description=f"{participant.name} is now {condition_data['condition']}",
            conditions_applied=[condition_data['condition']]
        )
    
    def remove_condition(self, participant_id: int, condition_name: str) -> CombatActionResponse:
        """Remove a condition from a combat participant"""
        participant = self.get_combat_participant(participant_id)
        if not participant:
            return CombatActionResponse(
                success=False,
                description=f"Participant {participant_id} not found"
            )
        
        participant.remove_condition(condition_name)
        self.db.commit()
        
        return CombatActionResponse(
            success=True,
            description=f"{participant.name} is no longer {condition_name}"
        )
    
    # Initiative and Turn Management
    def roll_initiative(self, encounter_id: int, participant_ids: List[int] = None) -> InitiativeRollResponse:
        """Roll initiative for combat participants"""
        encounter = self.get_combat_encounter(encounter_id)
        if not encounter:
            raise ValueError(f"Combat encounter {encounter_id} not found")
        
        if participant_ids:
            participants = [self.get_combat_participant(pid) for pid in participant_ids]
            participants = [p for p in participants if p is not None]
        else:
            participants = self.get_combat_participants_by_encounter(encounter_id)
        
        # Roll initiative for each participant
        initiative_order = []
        for participant in participants:
            if participant.participant_type == "character":
                character = self.db.query(Character).filter(Character.id == participant.character_id).first()
                dex_mod = character.dexterity_modifier if character else 0
            else:
                template = self.get_enemy_template(participant.enemy_template_id)
                dex_mod = template.dexterity_modifier if template else 0
            
            # Roll initiative if not already set
            if participant.initiative == 10:  # Default value
                participant.initiative = random.randint(1, 20) + dex_mod
                self.db.commit()
            
            initiative_order.append(InitiativeParticipant(
                participant_id=participant.id,
                initiative=participant.initiative,
                type=participant.participant_type,
                name=participant.name
            ))
        
        # Sort by initiative (highest first)
        initiative_order.sort(key=lambda x: x.initiative, reverse=True)
        
        # Update encounter with initiative order
        encounter.initiative_order = [p.model_dump() for p in initiative_order]
        encounter.combat_state = CombatState.IN_PROGRESS
        encounter.current_round = 1
        encounter.current_turn = 0
        self.db.commit()
        
        return InitiativeRollResponse(
            initiative_order=initiative_order,
            combat_state=encounter.combat_state
        )
    
    def advance_turn(self, encounter_id: int) -> Optional[CombatEncounter]:
        """Advance to the next participant's turn"""
        encounter = self.get_combat_encounter(encounter_id)
        if not encounter:
            return None
        
        encounter.advance_turn()
        
        # Reset actions for the current participant
        if encounter.initiative_order and encounter.current_turn < len(encounter.initiative_order):
            current_participant_data = encounter.initiative_order[encounter.current_turn]
            participant = self.get_combat_participant(current_participant_data['participant_id'])
            if participant:
                participant.reset_turn_actions()
        
        self.db.commit()
        self.db.refresh(encounter)
        return encounter
    
    def log_combat_action(self, encounter_id: int, action_data: Dict[str, Any]) -> bool:
        """Log a combat action"""
        encounter = self.get_combat_encounter(encounter_id)
        if not encounter:
            return False
        
        encounter.log_action(action_data)
        self.db.commit()
        return True
    
    # Utility Methods
    def get_combat_summary(self, encounter_id: int) -> Optional[CombatSummary]:
        """Get a summary of the combat encounter"""
        encounter = self.get_combat_encounter(encounter_id)
        if not encounter:
            return None
        
        participants = self.get_combat_participants_by_encounter(encounter_id)
        active_participants = [p for p in participants if p.is_active]
        
        # Find character participant
        character_participant = next((p for p in participants if p.participant_type == "character"), None)
        
        return CombatSummary(
            encounter_id=encounter.id,
            encounter_name=encounter.encounter_name,
            state=encounter.combat_state,
            current_round=encounter.current_round,
            participants_active=len(active_participants),
            participants_total=len(participants),
            character_hp=character_participant.current_hit_points if character_participant else 0,
            character_max_hp=character_participant.max_hit_points if character_participant else 0
        )
    
    def calculate_xp_reward(self, encounter_id: int) -> int:
        """Calculate XP reward for defeating enemies in encounter"""
        participants = self.get_combat_participants_by_encounter(encounter_id)
        total_xp = 0
        
        for participant in participants:
            if participant.participant_type == "enemy" and not participant.is_active:
                template = self.get_enemy_template(participant.enemy_template_id)
                if template:
                    total_xp += template.xp_value
        
        return total_xp
    
    def generate_loot(self, encounter_id: int) -> List[Dict[str, Any]]:
        """Generate loot from defeated enemies"""
        participants = self.get_combat_participants_by_encounter(encounter_id)
        loot = []
        
        for participant in participants:
            if participant.participant_type == "enemy" and not participant.is_active:
                template = self.get_enemy_template(participant.enemy_template_id)
                if template and template.loot_table:
                    # Add guaranteed loot
                    for item in template.loot_table.get('guaranteed', []):
                        loot.append(item)
                    
                    # Roll for possible loot
                    for item in template.loot_table.get('possible', []):
                        if random.random() < item.get('chance', 0):
                            loot.append({k: v for k, v in item.items() if k != 'chance'})
        
        return loot 