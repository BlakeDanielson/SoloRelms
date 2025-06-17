export interface Combatant {
  id: string;
  name: string;
  type: 'player' | 'npc' | 'enemy';
  health: {
    current: number;
    max: number;
    temporary: number;
  };
  armorClass: number;
  stats: {
    strength: number;
    dexterity: number;
    constitution: number;
    intelligence: number;
    wisdom: number;
    charisma: number;
  };
  modifiers: {
    [key in keyof Combatant['stats']]: number;
  };
  initiative: number;
  speed: number;
  conditions: StatusCondition[];
  position?: {
    x: number;
    y: number;
  };
  combatStats?: {
    damageTaken: number;
    damageDealt: number;
    healingReceived: number;
    actionsTaken: number;
  };
}

export interface StatusCondition {
  type: string;
  duration: number;
  source: string;
  effect: string;
}

export type ActionType = 'action' | 'bonus_action' | 'movement' | 'reaction' | 'free';

export type DamageType = 'slashing' | 'piercing' | 'bludgeoning' | 'fire' | 'cold' | 'lightning' | 'acid' | 'poison' | 'psychic' | 'necrotic' | 'radiant' | 'force' | 'thunder';

export interface CombatAction {
  id: string;
  name: string;
  actionType: ActionType; // What type of action economy this uses
  category: 'attack' | 'spell' | 'move' | 'dodge' | 'dash' | 'help' | 'ready' | 'hide' | 'disengage' | 'search' | 'use_object';
  target?: string; // combatant ID
  description: string;
  damage?: {
    dice: string; // e.g., "1d8+3"
    type: DamageType;
    modifier?: number;
  };
  attackBonus?: number;
  range?: {
    normal: number;
    maximum?: number;
  };
  savingThrow?: {
    ability: keyof Combatant['stats'];
    dc: number;
  };
  requirements?: {
    minimumLevel?: number;
    spellSlot?: number;
    weaponType?: string;
  };
  effects?: {
    healing?: string;
    conditions?: StatusCondition[];
    movement?: number;
  };
}

export interface CombatRound {
  number: number;
  turnOrder: string[]; // combatant IDs in initiative order
  currentTurnIndex: number;
  actions: CombatActionResult[];
}

export interface CombatActionResult {
  actor: string; // combatant ID
  action: CombatAction;
  result: {
    hit?: boolean;
    damage?: number;
    effect?: string;
    criticalHit?: boolean;
    criticalMiss?: boolean;
  };
  timestamp: number;
}

export interface CombatState {
  id: string;
  participants: Combatant[];
  currentRound: CombatRound;
  history: CombatRound[];
  isActive: boolean;
  winner?: 'players' | 'enemies' | 'draw';
  seed: string; // for deterministic RNG
}

export type CombatEvent = 
  | { type: 'START_COMBAT'; participants: Combatant[]; seed: string }
  | { type: 'ROLL_INITIATIVE' }
  | { type: 'START_TURN'; combatantId: string }
  | { type: 'SELECT_ACTION'; action: CombatAction }
  | { type: 'RESOLVE_ACTION'; result: CombatActionResult }
  | { type: 'END_TURN' }
  | { type: 'END_ROUND' }
  | { type: 'END_COMBAT'; winner: CombatState['winner'] }
  | { type: 'RESET_COMBAT' };

export interface CombatContext {
  state: CombatState;
  rng: () => number; // seeded random number generator (legacy)
  combatRNG?: any; // CombatRNG instance for deterministic rolls
  selectedAction?: CombatAction; // currently selected action for resolution
} 