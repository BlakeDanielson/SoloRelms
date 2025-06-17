import { v4 as uuidv4 } from 'uuid';
import { Combatant, CombatAction, CombatActionResult } from './types';

/**
 * Generate a unique combat ID
 */
export function generateCombatId(): string {
  return `combat_${uuidv4()}`;
}

/**
 * Calculate ability modifier based on D&D 5e rules
 */
export function calculateModifier(abilityScore: number): number {
  return Math.floor((abilityScore - 10) / 2);
}

/**
 * Roll a d20 with modifier
 */
export function rollD20(modifier: number = 0, rng: () => number = Math.random): number {
  return Math.floor(rng() * 20) + 1 + modifier;
}

/**
 * Parse dice notation (e.g., "2d6+3") and roll
 */
export function rollDice(diceNotation: string, rng: () => number = Math.random): number {
  const match = diceNotation.match(/^(\d+)d(\d+)(?:([+-])(\d+))?$/);
  if (!match) {
    throw new Error(`Invalid dice notation: ${diceNotation}`);
  }

  const [, numDiceStr, diceSizeStr, operator, modifierStr] = match;
  const numDice = parseInt(numDiceStr, 10);
  const diceSize = parseInt(diceSizeStr, 10);
  const modifier = modifierStr ? parseInt(modifierStr, 10) : 0;
  const sign = operator === '-' ? -1 : 1;

  let total = 0;
  for (let i = 0; i < numDice; i++) {
    total += Math.floor(rng() * diceSize) + 1;
  }

  return total + (modifier * sign);
}

/**
 * Calculate AC with modifiers
 */
export function calculateAC(baseDex: number, armor: number = 10): number {
  return armor + calculateModifier(baseDex);
}

/**
 * Check if an attack hits
 */
export function isAttackHit(
  attackRoll: number,
  attackBonus: number,
  targetAC: number
): boolean {
  return (attackRoll + attackBonus) >= targetAC;
}

/**
 * Check for critical hit (natural 20)
 */
export function isCriticalHit(roll: number): boolean {
  return roll === 20;
}

/**
 * Check for critical miss (natural 1)
 */
export function isCriticalMiss(roll: number): boolean {
  return roll === 1;
}

/**
 * Apply damage to a combatant
 */
export function applyDamage(combatant: Combatant, damage: number): Combatant {
  const newHealth = Math.max(0, combatant.health.current - damage);
  return {
    ...combatant,
    health: {
      ...combatant.health,
      current: newHealth
    }
  };
}

/**
 * Apply healing to a combatant
 */
export function applyHealing(combatant: Combatant, healing: number): Combatant {
  const newHealth = Math.min(combatant.health.max, combatant.health.current + healing);
  return {
    ...combatant,
    health: {
      ...combatant.health,
      current: newHealth
    }
  };
}

/**
 * Check if combatant is alive
 */
export function isAlive(combatant: Combatant): boolean {
  return combatant.health.current > 0;
}

/**
 * Calculate saving throw DC for spells
 */
export function calculateSpellSaveDC(casterLevel: number, spellcastingAbility: number): number {
  const proficiencyBonus = Math.ceil(casterLevel / 4) + 1; // Simplified proficiency calculation
  return 8 + proficiencyBonus + calculateModifier(spellcastingAbility);
}

/**
 * Make a saving throw
 */
export function makeSavingThrow(
  target: Combatant,
  ability: keyof Combatant['stats'],
  dc: number,
  rng: () => number = Math.random
): { success: boolean; roll: number; total: number } {
  const roll = Math.floor(rng() * 20) + 1;
  const modifier = calculateModifier(target.stats[ability]);
  const total = roll + modifier;
  
  return {
    success: total >= dc,
    roll,
    total
  };
}

/**
 * Calculate attack bonus based on ability and proficiency
 */
export function calculateAttackBonus(
  abilityScore: number,
  proficiencyBonus: number = 2
): number {
  return calculateModifier(abilityScore) + proficiencyBonus;
}

/**
 * Calculate damage with ability modifier
 */
export function calculateDamageWithModifier(
  baseDamage: number,
  abilityModifier: number,
  isCritical: boolean = false
): number {
  let damage = baseDamage + abilityModifier;
  
  // Critical hits double the dice damage (not the modifier)
  if (isCritical) {
    damage = (baseDamage * 2) + abilityModifier;
  }
  
  return Math.max(1, damage); // Minimum 1 damage
}

/**
 * Resolve an attack action
 */
export function resolveAttackAction(
  attacker: Combatant,
  target: Combatant,
  action: CombatAction,
  rng: () => number = Math.random
): CombatActionResult {
  const attackRoll = Math.floor(rng() * 20) + 1;
  const attackBonus = action.attackBonus || calculateAttackBonus(attacker.stats.strength);
  const isCrit = isCriticalHit(attackRoll);
  const isMiss = isCriticalMiss(attackRoll);
  const hit = !isMiss && (isCrit || isAttackHit(attackRoll, attackBonus, target.armorClass));

  let damage = 0;
  if (hit && action.damage) {
    const baseDamage = rollDice(action.damage.dice, rng);
    const abilityModifier = calculateModifier(attacker.stats.strength);
    damage = calculateDamageWithModifier(baseDamage, abilityModifier, isCrit);
  }

  return {
    actor: attacker.id,
    action,
    result: {
      hit,
      damage,
      criticalHit: isCrit,
      criticalMiss: isMiss,
      effect: hit ? `${damage} damage` : 'Miss'
    },
    timestamp: Date.now()
  };
}

/**
 * Resolve a spell action with saving throw
 */
export function resolveSpellAction(
  caster: Combatant,
  target: Combatant,
  action: CombatAction,
  rng: () => number = Math.random
): CombatActionResult {
  let effect = '';
  let damage = 0;

  if (action.savingThrow) {
    const saveResult = makeSavingThrow(target, action.savingThrow.ability, action.savingThrow.dc, rng);
    
    if (action.damage) {
      const spellDamage = rollDice(action.damage.dice, rng);
      damage = saveResult.success ? Math.floor(spellDamage / 2) : spellDamage;
      effect = `${damage} damage (${saveResult.success ? 'saved' : 'failed save'})`;
    } else {
      effect = saveResult.success ? 'Save successful' : 'Save failed';
    }
  } else if (action.damage) {
    // Direct damage spell (like Magic Missile)
    damage = rollDice(action.damage.dice, rng);
    effect = `${damage} damage`;
  } else if (action.effects?.healing) {
    // Healing spell
    const healing = rollDice(action.effects.healing, rng);
    effect = `${healing} healing`;
    damage = -healing; // Negative damage for healing
  }

  return {
    actor: caster.id,
    action,
    result: {
      hit: true, // Spells generally "hit" unless saved against
      damage,
      effect
    },
    timestamp: Date.now()
  };
}

/**
 * Resolve a utility action (dodge, dash, help, etc.)
 */
export function resolveUtilityAction(
  actor: Combatant,
  action: CombatAction
): CombatActionResult {
  let effect = '';

  switch (action.category) {
    case 'dodge':
      effect = 'Dodging - attacks have disadvantage';
      break;
    case 'dash':
      effect = `Gained extra ${action.effects?.movement || 30}ft movement`;
      break;
    case 'help':
      effect = 'Helped ally - they gain advantage on next action';
      break;
    case 'hide':
      effect = 'Attempting to hide';
      break;
    case 'disengage':
      effect = 'Disengaged - movement does not provoke opportunity attacks';
      break;
    case 'search':
      effect = 'Searching for hidden creatures or objects';
      break;
    case 'ready':
      effect = 'Readied an action for a specific trigger';
      break;
    default:
      effect = `Used ${action.name}`;
  }

  return {
    actor: actor.id,
    action,
    result: {
      hit: true,
      effect
    },
    timestamp: Date.now()
  };
}

/**
 * Main action resolution function
 */
export function resolveAction(
  actor: Combatant,
  target: Combatant | null,
  action: CombatAction,
  rng: () => number = Math.random
): CombatActionResult {
  switch (action.category) {
    case 'attack':
      if (!target) {
        throw new Error('Attack action requires a target');
      }
      return resolveAttackAction(actor, target, action, rng);
    
    case 'spell':
      if (action.savingThrow || action.damage) {
        if (!target) {
          throw new Error('Offensive spell requires a target');
        }
        return resolveSpellAction(actor, target, action, rng);
      } else {
        // Utility spell or self-targeting spell
        return resolveUtilityAction(actor, action);
      }
    
    default:
      return resolveUtilityAction(actor, action);
  }
}

/**
 * Apply action result to combat state
 */
export function applyActionResult(
  combatants: Combatant[],
  result: CombatActionResult
): Combatant[] {
  return combatants.map(combatant => {
    // Apply damage to target
    if (result.action.target === combatant.id && result.result.damage) {
      if (result.result.damage > 0) {
        return applyDamage(combatant, result.result.damage);
      } else if (result.result.damage < 0) {
        // Negative damage is healing
        return applyHealing(combatant, Math.abs(result.result.damage));
      }
    }
    
    // Apply conditions or other effects would go here
    // For now, just return the combatant unchanged
    return combatant;
  });
}

/**
 * Get all valid targets for an action
 */
export function getValidTargets(
  actor: Combatant,
  action: CombatAction,
  allCombatants: Combatant[]
): Combatant[] {
  switch (action.category) {
    case 'attack':
      // Can attack enemies
      return allCombatants.filter(c => 
        c.id !== actor.id && 
        c.type !== actor.type && 
        isAlive(c)
      );
    case 'help':
      // Can help allies
      return allCombatants.filter(c => 
        c.id !== actor.id && 
        c.type === actor.type && 
        isAlive(c)
      );
    default:
      return [];
  }
}

/**
 * Generate a random seed for deterministic combat
 */
export function generateSeed(): string {
  return Math.random().toString(36).substring(2, 15);
}

/**
 * Roll initiative for a combatant
 */
export function rollInitiative(combatant: Combatant, rng: () => number = Math.random): number {
  return rollD20(calculateModifier(combatant.stats.dexterity), rng);
}

/**
 * Create a turn order based on initiative rolls
 */
export function createTurnOrder(combatants: Combatant[]): string[] {
  return sortByInitiative(combatants).map(c => c.id);
}

/**
 * Sort combatants by initiative (highest first)
 */
export function sortByInitiative(combatants: Combatant[]): Combatant[] {
  return [...combatants].sort((a, b) => {
    // Higher initiative goes first
    if (b.initiative !== a.initiative) {
      return b.initiative - a.initiative;
    }
    // Tie-breaker: higher dexterity goes first
    if (b.stats.dexterity !== a.stats.dexterity) {
      return b.stats.dexterity - a.stats.dexterity;
    }
    // Final tie-breaker: alphabetical by name
    return a.name.localeCompare(b.name);
  });
} 