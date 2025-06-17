from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Optional
import traceback
import random
from datetime import datetime
import logging

from services.dice_service import DiceService, AdvantageType as ServiceAdvantageType, DiceRollResult, AttackRollResult
from schemas.dice import (
    DiceRollRequest, DiceRollResponse, AttackRollRequest, AttackRollResponse,
    AbilityScoreRollResponse, SavingThrowRequest, SkillCheckRequest, SkillCheckResponse,
    InitiativeRollRequest, HitPointsRollRequest, MultipleDiceRollRequest, MultipleDiceRollResponse,
    QuickRollRequest, DiceNotationValidationRequest, DiceNotationValidationResponse,
    AdvantageType
)
from auth import get_current_user
from pydantic import BaseModel

# Setup logging
logger = logging.getLogger(__name__)

# Additional Pydantic models for new endpoints
class SimpleDiceRollRequest(BaseModel):
    dice_type: str  # 'd4', 'd6', 'd8', 'd10', 'd12', 'd20', 'd100'
    count: Optional[int] = 1
    modifier: Optional[int] = 0
    label: Optional[str] = None

class SimpleDiceRollResponse(BaseModel):
    roll_type: str
    dice: str
    result: int
    modifier: int
    total: int
    breakdown: str
    timestamp: str
    individual_rolls: List[int]
    critical: bool

router = APIRouter(prefix="/api/dice", tags=["dice"])

def convert_service_result_to_response(result: DiceRollResult) -> DiceRollResponse:
    """Convert service DiceRollResult to API response schema"""
    return DiceRollResponse(
        total=result.total,
        individual_rolls=result.individual_rolls,
        dice_notation=result.dice_notation,
        modifier=result.modifier,
        advantage_type=AdvantageType(result.advantage_type.value),
        dropped_dice=result.dropped_dice,
        description=result.description
    )

def convert_advantage_type(advantage_type: AdvantageType) -> ServiceAdvantageType:
    """Convert API advantage type to service advantage type"""
    return ServiceAdvantageType(advantage_type.value)

@router.post("/roll", response_model=DiceRollResponse)
async def roll_dice(request: DiceRollRequest):
    """
    Roll dice using standard D&D notation
    
    Examples:
    - "1d20+5" - Roll a d20 and add 5
    - "2d6" - Roll two d6 dice
    - "4d6kh3" - Roll 4d6 and keep the highest 3
    - "1d20" with advantage - Roll twice, take higher
    """
    try:
        advantage_type = convert_advantage_type(request.advantage_type)
        result = DiceService.roll_dice_notation(request.notation, advantage_type)
        
        if request.description:
            result.description = request.description
            
        return convert_service_result_to_response(result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dice roll failed: {str(e)}")

@router.post("/attack", response_model=AttackRollResponse)
async def roll_attack(request: AttackRollRequest):
    """
    Roll a complete attack including damage calculation
    
    Returns attack roll, damage roll (if hit), critical hit status, and hit determination
    """
    try:
        advantage_type = convert_advantage_type(request.advantage_type)
        result = DiceService.make_attack_roll(
            attack_bonus=request.attack_bonus,
            damage_notation=request.damage_notation,
            target_ac=request.target_ac,
            advantage_type=advantage_type,
            critical_range=request.critical_range
        )
        
        response = AttackRollResponse(
            attack_roll=convert_service_result_to_response(result.attack_roll),
            damage_roll=convert_service_result_to_response(result.damage_roll) if result.damage_roll else None,
            is_critical=result.is_critical,
            is_hit=result.is_hit,
            target_ac=result.target_ac,
            description=request.description or ""
        )
        
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Attack roll failed: {str(e)}")

@router.post("/ability-scores", response_model=AbilityScoreRollResponse)
async def roll_ability_scores():
    """
    Roll all six ability scores using 4d6 drop lowest method
    
    Returns: strength, dexterity, constitution, intelligence, wisdom, charisma
    """
    try:
        results = DiceService.roll_all_ability_scores()
        converted_results = {
            ability: convert_service_result_to_response(result) 
            for ability, result in results.items()
        }
        return AbilityScoreRollResponse(scores=converted_results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ability score generation failed: {str(e)}")

@router.post("/saving-throw", response_model=DiceRollResponse)
async def roll_saving_throw(request: SavingThrowRequest):
    """
    Roll a saving throw with ability modifier and optional proficiency
    """
    try:
        advantage_type = convert_advantage_type(request.advantage_type)
        result = DiceService.roll_saving_throw(
            ability_modifier=request.ability_modifier,
            proficiency_bonus=request.proficiency_bonus,
            advantage_type=advantage_type
        )
        
        if request.description:
            result.description = request.description
            
        return convert_service_result_to_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Saving throw failed: {str(e)}")

@router.post("/skill-check", response_model=SkillCheckResponse)
async def roll_skill_check(request: SkillCheckRequest):
    """
    Roll a skill check with ability modifier and optional proficiency
    """
    try:
        advantage_type = convert_advantage_type(request.advantage_type)
        result = DiceService.roll_skill_check(
            ability_modifier=request.ability_modifier,
            proficiency_bonus=request.proficiency_bonus,
            advantage_type=advantage_type
        )
        
        success = None
        if request.dc is not None:
            success = result.total >= request.dc
            
        return SkillCheckResponse(
            roll_result=convert_service_result_to_response(result),
            skill_name=request.skill_name,
            dc=request.dc,
            success=success
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Skill check failed: {str(e)}")

@router.post("/initiative", response_model=DiceRollResponse)
async def roll_initiative(request: InitiativeRollRequest):
    """
    Roll initiative with dexterity modifier
    """
    try:
        advantage_type = convert_advantage_type(request.advantage_type)
        result = DiceService.roll_initiative(
            dexterity_modifier=request.dexterity_modifier,
            advantage_type=advantage_type
        )
        result.description = "Initiative roll"
        return convert_service_result_to_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Initiative roll failed: {str(e)}")

@router.post("/hit-points", response_model=DiceRollResponse)
async def roll_hit_points(request: HitPointsRollRequest):
    """
    Roll hit points for a character level-up
    """
    try:
        result = DiceService.roll_hit_points(
            hit_die=request.hit_die,
            constitution_modifier=request.constitution_modifier,
            level=request.level
        )
        return convert_service_result_to_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hit points roll failed: {str(e)}")

@router.post("/multiple", response_model=MultipleDiceRollResponse)
async def roll_multiple_dice(request: MultipleDiceRollRequest):
    """
    Roll multiple dice expressions at once
    """
    try:
        results = []
        total_sum = 0
        
        for roll_request in request.rolls:
            advantage_type = convert_advantage_type(roll_request.advantage_type)
            result = DiceService.roll_dice_notation(roll_request.notation, advantage_type)
            
            if roll_request.description:
                result.description = roll_request.description
                
            converted_result = convert_service_result_to_response(result)
            results.append(converted_result)
            total_sum += result.total
            
        return MultipleDiceRollResponse(
            results=results,
            total_sum=total_sum
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Multiple dice roll failed: {str(e)}")

@router.post("/quick-roll", response_model=DiceRollResponse)
async def quick_roll(request: QuickRollRequest):
    """
    Quick roll for common dice types
    
    Supported roll_types: d4, d6, d8, d10, d12, d20, d100, percentile
    """
    try:
        # Map roll types to dice notation
        roll_type_map = {
            "d4": "1d4",
            "d6": "1d6", 
            "d8": "1d8",
            "d10": "1d10",
            "d12": "1d12",
            "d20": "1d20",
            "d100": "1d100",
            "percentile": "1d100"
        }
        
        if request.roll_type.lower() not in roll_type_map:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported roll type: {request.roll_type}. Supported types: {list(roll_type_map.keys())}"
            )
        
        base_notation = roll_type_map[request.roll_type.lower()]
        
        # Add modifier if provided
        if request.modifier != 0:
            if request.modifier > 0:
                notation = f"{base_notation}+{request.modifier}"
            else:
                notation = f"{base_notation}{request.modifier}"
        else:
            notation = base_notation
            
        advantage_type = convert_advantage_type(request.advantage_type)
        result = DiceService.roll_dice_notation(notation, advantage_type)
        result.description = f"Quick {request.roll_type} roll"
        
        return convert_service_result_to_response(result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quick roll failed: {str(e)}")

@router.post("/validate", response_model=DiceNotationValidationResponse)
async def validate_dice_notation(request: DiceNotationValidationRequest):
    """
    Validate dice notation without rolling
    """
    try:
        num_dice, die_sides, modifier = DiceService.parse_dice_notation(request.notation)
        
        parsed_notation = {
            "num_dice": num_dice,
            "die_sides": die_sides,
            "modifier": modifier,
            "original_notation": request.notation
        }
        
        return DiceNotationValidationResponse(
            is_valid=True,
            parsed_notation=parsed_notation,
            error_message=None
        )
    except ValueError as e:
        return DiceNotationValidationResponse(
            is_valid=False,
            parsed_notation=None,
            error_message=str(e)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")

# Convenience endpoints for common rolls
@router.post("/d20", response_model=DiceRollResponse)
async def roll_d20(modifier: int = 0, advantage_type: AdvantageType = AdvantageType.NORMAL):
    """Quick d20 roll with optional modifier"""
    notation = f"1d20+{modifier}" if modifier >= 0 else f"1d20{modifier}"
    service_advantage = convert_advantage_type(advantage_type)
    result = DiceService.roll_dice_notation(notation, service_advantage)
    result.description = "d20 roll"
    return convert_service_result_to_response(result)

@router.post("/d6", response_model=DiceRollResponse)
async def roll_d6(num_dice: int = 1, modifier: int = 0):
    """Quick d6 roll"""
    notation = f"{num_dice}d6"
    if modifier != 0:
        notation += f"+{modifier}" if modifier > 0 else str(modifier)
    result = DiceService.roll_dice_notation(notation)
    result.description = f"{num_dice}d6 roll"
    return convert_service_result_to_response(result)

@router.post("/percentile", response_model=DiceRollResponse)
async def roll_percentile():
    """Roll percentile dice (d100)"""
    result = DiceService.roll_dice_notation("1d100")
    result.description = "Percentile roll"
    return convert_service_result_to_response(result)

@router.post("/simple")
async def roll_dice_simple(dice_request: SimpleDiceRollRequest):
    """Roll dice and return detailed results"""
    try:
        dice_type = dice_request.dice_type.lower()
        count = max(1, dice_request.count or 1)
        modifier = dice_request.modifier or 0
        
        # Validate dice type
        valid_dice = ['d4', 'd6', 'd8', 'd10', 'd12', 'd20', 'd100']
        if dice_type not in valid_dice:
            raise HTTPException(status_code=400, detail=f"Invalid dice type. Must be one of: {valid_dice}")
        
        # Get dice sides
        sides = int(dice_type[1:])
        
        # Roll the dice
        rolls = []
        for _ in range(count):
            roll = random.randint(1, sides)
            rolls.append(roll)
        
        # Calculate results
        roll_sum = sum(rolls)
        total = roll_sum + modifier
        
        # Check for critical (only on d20 single rolls)
        is_critical = (dice_type == 'd20' and count == 1 and (rolls[0] == 20 or rolls[0] == 1))
        
        # Create breakdown string
        if count == 1:
            breakdown = f"{dice_type}: {rolls[0]}"
        else:
            breakdown = f"{count}{dice_type}: [{', '.join(map(str, rolls))}] = {roll_sum}"
        
        if modifier != 0:
            breakdown += f" {'+' if modifier > 0 else ''}{modifier} = {total}"
        else:
            breakdown += f" = {total}"
        
        logger.info(f"🎲 Dice roll: {breakdown} (Critical: {is_critical})")
        
        response = SimpleDiceRollResponse(
            roll_type=dice_request.label or f"{count}{dice_type} roll",
            dice=dice_type,
            result=roll_sum,
            modifier=modifier,
            total=total,
            breakdown=breakdown,
            timestamp=datetime.utcnow().isoformat(),
            individual_rolls=rolls,
            critical=is_critical
        )
        
        return {
            "success": True,
            "data": response
        }
        
    except ValueError as e:
        logger.error(f"❌ Invalid dice format: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid dice format: {str(e)}")
    except Exception as e:
        logger.error(f"❌ Error rolling dice: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to roll dice: {str(e)}")

@router.get("/simple/types")
async def get_dice_types():
    """Get available dice types and their descriptions"""
    dice_types = {
        "d4": {"sides": 4, "description": "Four-sided die (tetrahedron)", "common_uses": ["Damage for small weapons"]},
        "d6": {"sides": 6, "description": "Six-sided die (cube)", "common_uses": ["Damage, basic rolls"]},
        "d8": {"sides": 8, "description": "Eight-sided die (octahedron)", "common_uses": ["Damage for medium weapons"]},
        "d10": {"sides": 10, "description": "Ten-sided die", "common_uses": ["Damage, percentile (with d100)"]},
        "d12": {"sides": 12, "description": "Twelve-sided die (dodecahedron)", "common_uses": ["Damage for large weapons"]},
        "d20": {"sides": 20, "description": "Twenty-sided die (icosahedron)", "common_uses": ["Attack rolls, ability checks, saving throws"]},
        "d100": {"sides": 100, "description": "Percentile die", "common_uses": ["Percentage rolls, random tables"]}
    }
    
    return {
        "success": True,
        "data": dice_types
    }

@router.post("/simple/quick/{dice_type}")
async def quick_roll_endpoint(dice_type: str, modifier: Optional[int] = 0):
    """Quick single dice roll endpoint"""
    dice_request = SimpleDiceRollRequest(
        dice_type=dice_type,
        count=1,
        modifier=modifier,
        label=f"Quick {dice_type} roll"
    )
    
    return await roll_dice_simple(dice_request) 