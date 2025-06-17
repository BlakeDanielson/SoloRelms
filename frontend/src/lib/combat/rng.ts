import seedrandom from 'seedrandom';

/**
 * Deterministic Random Number Generator for Combat
 * Provides seeded random number generation for consistent, reproducible combat results
 */
export class CombatRNG {
  private rng: () => number;
  private seed: string;
  private callCount: number = 0;

  constructor(seed: string) {
    this.seed = seed;
    this.rng = seedrandom(seed);
  }

  /**
   * Get the current seed
   */
  getSeed(): string {
    return this.seed;
  }

  /**
   * Get the number of RNG calls made
   */
  getCallCount(): number {
    return this.callCount;
  }

  /**
   * Reset the RNG with the same seed
   */
  reset(): void {
    this.rng = seedrandom(this.seed);
    this.callCount = 0;
  }

  /**
   * Reset the RNG with a new seed
   */
  reseed(newSeed: string): void {
    this.seed = newSeed;
    this.rng = seedrandom(newSeed);
    this.callCount = 0;
  }

  /**
   * Generate a raw random number [0, 1)
   */
  random(): number {
    this.callCount++;
    return this.rng();
  }

  /**
   * Roll a single die (1 to sides)
   */
  rollDie(sides: number): number {
    if (sides <= 0) throw new Error('Die must have at least 1 side');
    return Math.floor(this.random() * sides) + 1;
  }

  /**
   * Roll a d20 with optional modifier
   */
  rollD20(modifier: number = 0): number {
    return this.rollDie(20) + modifier;
  }

  /**
   * Roll a d100 (percentile)
   */
  rollD100(): number {
    return this.rollDie(100);
  }

  /**
   * Roll multiple dice and sum them
   */
  rollMultipleDice(count: number, sides: number): number {
    if (count <= 0) throw new Error('Must roll at least 1 die');
    let total = 0;
    for (let i = 0; i < count; i++) {
      total += this.rollDie(sides);
    }
    return total;
  }

  /**
   * Parse and roll dice notation (e.g., "2d6+3", "1d8-1")
   */
  rollDiceNotation(notation: string): number {
    const match = notation.match(/^(\d+)d(\d+)(?:([+-])(\d+))?$/i);
    if (!match) {
      throw new Error(`Invalid dice notation: ${notation}`);
    }

    const [, numDiceStr, diceSizeStr, operator, modifierStr] = match;
    const numDice = parseInt(numDiceStr, 10);
    const diceSize = parseInt(diceSizeStr, 10);
    const modifier = modifierStr ? parseInt(modifierStr, 10) : 0;
    const sign = operator === '-' ? -1 : 1;

    const diceTotal = this.rollMultipleDice(numDice, diceSize);
    return diceTotal + (modifier * sign);
  }

  /**
   * Roll with advantage (roll twice, take higher)
   */
  rollWithAdvantage(sides: number, modifier: number = 0): {
    result: number;
    rolls: [number, number];
    modifier: number;
  } {
    const roll1 = this.rollDie(sides);
    const roll2 = this.rollDie(sides);
    const higherRoll = Math.max(roll1, roll2);
    
    return {
      result: higherRoll + modifier,
      rolls: [roll1, roll2],
      modifier
    };
  }

  /**
   * Roll with disadvantage (roll twice, take lower)
   */
  rollWithDisadvantage(sides: number, modifier: number = 0): {
    result: number;
    rolls: [number, number];
    modifier: number;
  } {
    const roll1 = this.rollDie(sides);
    const roll2 = this.rollDie(sides);
    const lowerRoll = Math.min(roll1, roll2);
    
    return {
      result: lowerRoll + modifier,
      rolls: [roll1, roll2],
      modifier
    };
  }

  /**
   * Random selection from an array
   */
  choice<T>(array: T[]): T {
    if (array.length === 0) throw new Error('Cannot choose from empty array');
    const index = Math.floor(this.random() * array.length);
    return array[index];
  }

  /**
   * Shuffle an array using Fisher-Yates algorithm
   */
  shuffle<T>(array: T[]): T[] {
    const shuffled = [...array];
    for (let i = shuffled.length - 1; i > 0; i--) {
      const j = Math.floor(this.random() * (i + 1));
      [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    return shuffled;
  }

  /**
   * Generate a random integer between min and max (inclusive)
   */
  randomInt(min: number, max: number): number {
    if (min > max) throw new Error('min cannot be greater than max');
    return Math.floor(this.random() * (max - min + 1)) + min;
  }

  /**
   * Check if a percentage chance succeeds (0-100)
   */
  chance(percentage: number): boolean {
    if (percentage < 0 || percentage > 100) {
      throw new Error('Percentage must be between 0 and 100');
    }
    return this.random() * 100 < percentage;
  }

  /**
   * Roll initiative for a combatant (d20 + dex modifier)
   */
  rollInitiative(dexterityModifier: number): number {
    return this.rollD20(dexterityModifier);
  }

  /**
   * Roll an attack roll (d20 + attack bonus)
   */
  rollAttack(attackBonus: number): number {
    return this.rollD20(attackBonus);
  }

  /**
   * Roll a saving throw (d20 + ability modifier)
   */
  rollSavingThrow(abilityModifier: number): number {
    return this.rollD20(abilityModifier);
  }

  /**
   * Roll damage with optional critical hit doubling
   */
  rollDamage(diceNotation: string, isCritical: boolean = false): number {
    if (isCritical) {
      // For critical hits, double the dice but not modifiers
      const match = diceNotation.match(/^(\d+)d(\d+)(?:([+-])(\d+))?$/i);
      if (match) {
        const [, numDiceStr, diceSizeStr, operator, modifierStr] = match;
        const numDice = parseInt(numDiceStr, 10);
        const diceSize = parseInt(diceSizeStr, 10);
        const modifier = modifierStr ? parseInt(modifierStr, 10) : 0;
        const sign = operator === '-' ? -1 : 1;

        // Double the dice, keep the same modifier
        const criticalDiceTotal = this.rollMultipleDice(numDice * 2, diceSize);
        return criticalDiceTotal + (modifier * sign);
      }
    }
    
    return this.rollDiceNotation(diceNotation);
  }

  /**
   * Get debug information about the RNG state
   */
  getDebugInfo(): {
    seed: string;
    callCount: number;
    nextPreview: number[];
  } {
    // Create a temporary RNG to preview next values without affecting state
    const tempRng = seedrandom(this.seed);
    
    // Skip to current position
    for (let i = 0; i < this.callCount; i++) {
      tempRng();
    }
    
    // Get next 5 values as preview
    const preview = [];
    for (let i = 0; i < 5; i++) {
      preview.push(Math.round(tempRng() * 100) / 100); // Round to 2 decimal places
    }

    return {
      seed: this.seed,
      callCount: this.callCount,
      nextPreview: preview
    };
  }
}

/**
 * Generate a random seed string
 */
export function generateRandomSeed(): string {
  return Math.random().toString(36).substring(2, 15) + 
         Math.random().toString(36).substring(2, 15);
}

/**
 * Generate a timestamp-based seed
 */
export function generateTimestampSeed(): string {
  return `${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
}

/**
 * Create a simple hash from a string (for deterministic seeds from user input)
 */
export function hashString(str: string): string {
  let hash = 0;
  if (str.length === 0) return hash.toString();
  
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // Convert to 32bit integer
  }
  
  return Math.abs(hash).toString(36);
}

/**
 * Validate that a seed produces consistent results
 */
export function validateSeedConsistency(seed: string, iterations: number = 100): boolean {
  const rng1 = new CombatRNG(seed);
  const rng2 = new CombatRNG(seed);
  
  for (let i = 0; i < iterations; i++) {
    const roll1 = rng1.rollD20();
    const roll2 = rng2.rollD20();
    
    if (roll1 !== roll2) {
      return false;
    }
  }
  
  return true;
} 