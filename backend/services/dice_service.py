import random
import re
from typing import List, Tuple, Dict, Optional, Union
from dataclasses import dataclass
from enum import Enum

class DiceType(Enum):
    """Standard D&D dice types"""
    D4 = 4
    D6 = 6
    D8 = 8
    D10 = 10
    D12 = 12
    D20 = 20
    D100 = 100

class AdvantageType(Enum):
    """Advantage/disadvantage types for D&D 5e"""
    NORMAL = "normal"
    ADVANTAGE = "advantage"
    DISADVANTAGE = "disadvantage"

@dataclass
class DiceRollResult:
    """Result of a dice roll operation"""
    total: int
    individual_rolls: List[int]
    dice_notation: str
    modifier: int = 0
    advantage_type: AdvantageType = AdvantageType.NORMAL
    dropped_dice: List[int] = None
    description: str = ""

@dataclass
class AttackRollResult:
    """Result of an attack roll"""
    attack_roll: DiceRollResult
    damage_roll: Optional[DiceRollResult] = None
    is_critical: bool = False
    is_hit: bool = False
    target_ac: Optional[int] = None

class DiceService:
    """Service for handling all dice mechanics in D&D 5e"""
    
    @staticmethod
    def roll_die(sides: int) -> int:
        """Roll a single die with the specified number of sides"""
        return random.randint(1, sides)
    
    @staticmethod
    def roll_multiple_dice(num_dice: int, sides: int) -> List[int]:
        """Roll multiple dice of the same type"""
        return [DiceService.roll_die(sides) for _ in range(num_dice)]
    
    @staticmethod
    def parse_dice_notation(notation: str) -> Tuple[int, int, int]:
        """
        Parse dice notation like '2d6+3' or '1d20-1'
        Returns: (num_dice, die_sides, modifier)
        """
        # Remove spaces and convert to lowercase
        notation = notation.replace(" ", "").lower()
        
        # Match patterns like 2d6+3, 1d20-1, d20, 3d8
        pattern = r'^(\d*)d(\d+)([+-]\d+)?$'
        match = re.match(pattern, notation)
        
        if not match:
            raise ValueError(f"Invalid dice notation: {notation}")
        
        num_dice = int(match.group(1)) if match.group(1) else 1
        die_sides = int(match.group(2))
        modifier = int(match.group(3)) if match.group(3) else 0
        
        return num_dice, die_sides, modifier
    
    @staticmethod
    def roll_dice_notation(notation: str, advantage_type: AdvantageType = AdvantageType.NORMAL) -> DiceRollResult:
        """
        Roll dice using standard notation (e.g., '2d6+3', '1d20', '4d6kh3')
        """
        # Handle advantage/disadvantage for d20 rolls
        if advantage_type != AdvantageType.NORMAL and "d20" in notation:
            return DiceService._roll_with_advantage(notation, advantage_type)
        
        # Handle special notation like 4d6kh3 (keep highest 3)
        if "kh" in notation or "kl" in notation or "dh" in notation or "dl" in notation:
            return DiceService._roll_with_keep_drop(notation)
        
        # Standard dice roll
        num_dice, die_sides, modifier = DiceService.parse_dice_notation(notation)
        rolls = DiceService.roll_multiple_dice(num_dice, die_sides)
        total = sum(rolls) + modifier
        
        return DiceRollResult(
            total=total,
            individual_rolls=rolls,
            dice_notation=notation,
            modifier=modifier,
            advantage_type=advantage_type
        )
    
    @staticmethod
    def _roll_with_advantage(notation: str, advantage_type: AdvantageType) -> DiceRollResult:
        """Handle advantage/disadvantage rolls (roll twice, take higher/lower)"""
        num_dice, die_sides, modifier = DiceService.parse_dice_notation(notation)
        
        # Roll twice
        rolls1 = DiceService.roll_multiple_dice(num_dice, die_sides)
        rolls2 = DiceService.roll_multiple_dice(num_dice, die_sides)
        
        total1 = sum(rolls1)
        total2 = sum(rolls2)
        
        if advantage_type == AdvantageType.ADVANTAGE:
            chosen_rolls = rolls1 if total1 >= total2 else rolls2
            chosen_total = max(total1, total2)
            dropped_rolls = rolls2 if total1 >= total2 else rolls1
        else:  # DISADVANTAGE
            chosen_rolls = rolls1 if total1 <= total2 else rolls2
            chosen_total = min(total1, total2)
            dropped_rolls = rolls2 if total1 <= total2 else rolls1
        
        return DiceRollResult(
            total=chosen_total + modifier,
            individual_rolls=chosen_rolls,
            dice_notation=notation,
            modifier=modifier,
            advantage_type=advantage_type,
            dropped_dice=dropped_rolls
        )
    
    @staticmethod
    def _roll_with_keep_drop(notation: str) -> DiceRollResult:
        """Handle keep highest/lowest or drop highest/lowest notation"""
        # Parse special notation like 4d6kh3 or 4d6dl1
        base_notation = re.sub(r'[kd][hl]\d+', '', notation)
        num_dice, die_sides, modifier = DiceService.parse_dice_notation(base_notation)
        
        # Extract keep/drop instruction
        keep_drop_match = re.search(r'([kd])([hl])(\d+)', notation)
        if not keep_drop_match:
            raise ValueError(f"Invalid keep/drop notation: {notation}")
        
        action = keep_drop_match.group(1)  # 'k' or 'd'
        direction = keep_drop_match.group(2)  # 'h' or 'l'
        count = int(keep_drop_match.group(3))
        
        rolls = DiceService.roll_multiple_dice(num_dice, die_sides)
        sorted_rolls = sorted(rolls, reverse=(direction == 'h'))
        
        if action == 'k':  # keep
            kept_rolls = sorted_rolls[:count]
            dropped_rolls = sorted_rolls[count:]
        else:  # drop
            kept_rolls = sorted_rolls[count:]
            dropped_rolls = sorted_rolls[:count]
        
        total = sum(kept_rolls) + modifier
        
        return DiceRollResult(
            total=total,
            individual_rolls=kept_rolls,
            dice_notation=notation,
            modifier=modifier,
            dropped_dice=dropped_rolls
        )
    
    @staticmethod
    def roll_ability_score() -> DiceRollResult:
        """Roll ability score using 4d6 drop lowest method"""
        return DiceService.roll_dice_notation("4d6dh1")
    
    @staticmethod
    def roll_all_ability_scores() -> Dict[str, DiceRollResult]:
        """Roll all six ability scores"""
        abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        return {ability: DiceService.roll_ability_score() for ability in abilities}
    
    @staticmethod
    def roll_hit_points(hit_die: int, constitution_modifier: int, level: int = 1) -> DiceRollResult:
        """Roll hit points for a character"""
        if level == 1:
            # Level 1 gets max hit die + con modifier
            total = hit_die + constitution_modifier
            return DiceRollResult(
                total=max(1, total),  # Minimum 1 HP
                individual_rolls=[hit_die],
                dice_notation=f"1d{hit_die}+{constitution_modifier}",
                modifier=constitution_modifier,
                description="Level 1 HP (max hit die + CON modifier)"
            )
        else:
            # Higher levels roll hit die + con modifier
            notation = f"1d{hit_die}+{constitution_modifier}"
            result = DiceService.roll_dice_notation(notation)
            result.total = max(1, result.total)  # Minimum 1 HP
            return result
    
    @staticmethod
    def roll_attack(attack_bonus: int, advantage_type: AdvantageType = AdvantageType.NORMAL) -> DiceRollResult:
        """Roll an attack roll"""
        notation = f"1d20+{attack_bonus}" if attack_bonus >= 0 else f"1d20{attack_bonus}"
        return DiceService.roll_dice_notation(notation, advantage_type)
    
    @staticmethod
    def roll_damage(damage_notation: str) -> DiceRollResult:
        """Roll damage using dice notation"""
        return DiceService.roll_dice_notation(damage_notation)
    
    @staticmethod
    def roll_saving_throw(ability_modifier: int, proficiency_bonus: int = 0, advantage_type: AdvantageType = AdvantageType.NORMAL) -> DiceRollResult:
        """Roll a saving throw"""
        total_bonus = ability_modifier + proficiency_bonus
        notation = f"1d20+{total_bonus}" if total_bonus >= 0 else f"1d20{total_bonus}"
        return DiceService.roll_dice_notation(notation, advantage_type)
    
    @staticmethod
    def roll_skill_check(ability_modifier: int, proficiency_bonus: int = 0, advantage_type: AdvantageType = AdvantageType.NORMAL) -> DiceRollResult:
        """Roll a skill check"""
        return DiceService.roll_saving_throw(ability_modifier, proficiency_bonus, advantage_type)
    
    @staticmethod
    def roll_initiative(dexterity_modifier: int, advantage_type: AdvantageType = AdvantageType.NORMAL) -> DiceRollResult:
        """Roll initiative"""
        notation = f"1d20+{dexterity_modifier}" if dexterity_modifier >= 0 else f"1d20{dexterity_modifier}"
        return DiceService.roll_dice_notation(notation, advantage_type)
    
    @staticmethod
    def make_attack_roll(attack_bonus: int, damage_notation: str, target_ac: int, 
                        advantage_type: AdvantageType = AdvantageType.NORMAL, 
                        critical_range: int = 20) -> AttackRollResult:
        """
        Make a complete attack roll including damage
        """
        attack_roll = DiceService.roll_attack(attack_bonus, advantage_type)
        
        # Check for critical hit (natural 20 or within critical range)
        natural_roll = max(attack_roll.individual_rolls) if advantage_type != AdvantageType.NORMAL else attack_roll.individual_rolls[0]
        is_critical = natural_roll >= critical_range
        
        # Check if attack hits
        is_hit = attack_roll.total >= target_ac or is_critical
        
        damage_roll = None
        if is_hit:
            damage_roll = DiceService.roll_damage(damage_notation)
            if is_critical:
                # Critical hit: double the damage dice (not the modifier)
                base_damage, modifier = DiceService._parse_damage_for_crit(damage_notation)
                crit_damage = DiceService.roll_damage(base_damage)
                damage_roll.total += crit_damage.total
                damage_roll.individual_rolls.extend(crit_damage.individual_rolls)
                damage_roll.description = "Critical hit damage"
        
        return AttackRollResult(
            attack_roll=attack_roll,
            damage_roll=damage_roll,
            is_critical=is_critical,
            is_hit=is_hit,
            target_ac=target_ac
        )
    
    @staticmethod
    def _parse_damage_for_crit(damage_notation: str) -> Tuple[str, int]:
        """Parse damage notation to separate dice from modifier for critical hits"""
        num_dice, die_sides, modifier = DiceService.parse_dice_notation(damage_notation)
        base_damage = f"{num_dice}d{die_sides}"
        return base_damage, modifier
    
    @staticmethod
    def roll_percentile() -> int:
        """Roll percentile dice (d100)"""
        return DiceService.roll_die(100)
    
    @staticmethod
    def roll_d4() -> int:
        """Roll a d4"""
        return DiceService.roll_die(4)
    
    @staticmethod
    def roll_d6() -> int:
        """Roll a d6"""
        return DiceService.roll_die(6)
    
    @staticmethod
    def roll_d8() -> int:
        """Roll a d8"""
        return DiceService.roll_die(8)
    
    @staticmethod
    def roll_d10() -> int:
        """Roll a d10"""
        return DiceService.roll_die(10)
    
    @staticmethod
    def roll_d12() -> int:
        """Roll a d12"""
        return DiceService.roll_die(12)
    
    @staticmethod
    def roll_d20() -> int:
        """Roll a d20"""
        return DiceService.roll_die(20)
    
    @staticmethod
    def roll_d100() -> int:
        """Roll a d100"""
        return DiceService.roll_die(100) 