import { CombatAction, ActionType, DamageType } from './types';

// Basic combat actions available to all combatants
export const BASIC_ACTIONS: CombatAction[] = [
  {
    id: 'attack_melee',
    name: 'Melee Attack',
    actionType: 'action',
    category: 'attack',
    description: 'Make a melee weapon attack against a target within reach.',
    damage: {
      dice: '1d6',
      type: 'slashing',
      modifier: 0
    },
    attackBonus: 0,
    range: {
      normal: 5,
      maximum: 5
    }
  },
  {
    id: 'attack_ranged',
    name: 'Ranged Attack',
    actionType: 'action',
    category: 'attack',
    description: 'Make a ranged weapon attack against a target within range.',
    damage: {
      dice: '1d6',
      type: 'piercing',
      modifier: 0
    },
    attackBonus: 0,
    range: {
      normal: 80,
      maximum: 320
    }
  },
  {
    id: 'dodge',
    name: 'Dodge',
    actionType: 'action',
    category: 'dodge',
    description: 'Focus entirely on avoiding attacks. Until the start of your next turn, any attack roll made against you has disadvantage if you can see the attacker.',
    effects: {
      conditions: [{
        type: 'dodging',
        duration: 1,
        source: 'dodge_action',
        effect: 'Attacks against you have disadvantage'
      }]
    }
  },
  {
    id: 'dash',
    name: 'Dash',
    actionType: 'action',
    category: 'dash',
    description: 'Gain extra movement for the turn equal to your speed.',
    effects: {
      movement: 30 // This would be calculated based on character speed
    }
  },
  {
    id: 'help',
    name: 'Help',
    actionType: 'action',
    category: 'help',
    description: 'Help another creature with a task or give advantage on their next attack roll.',
    effects: {
      conditions: [{
        type: 'helped',
        duration: 1,
        source: 'help_action',
        effect: 'Advantage on next attack roll or ability check'
      }]
    }
  },
  {
    id: 'hide',
    name: 'Hide',
    actionType: 'action',
    category: 'hide',
    description: 'Make a Dexterity (Stealth) check to hide.',
    savingThrow: {
      ability: 'dexterity',
      dc: 15 // This would be calculated based on enemy perception
    }
  },
  {
    id: 'ready',
    name: 'Ready',
    actionType: 'action',
    category: 'ready',
    description: 'Prepare an action to trigger when a specific condition is met.',
    effects: {
      conditions: [{
        type: 'readied',
        duration: 1,
        source: 'ready_action',
        effect: 'Action prepared for specific trigger'
      }]
    }
  },
  {
    id: 'disengage',
    name: 'Disengage',
    actionType: 'action',
    category: 'disengage',
    description: 'Your movement doesn\'t provoke opportunity attacks for the rest of the turn.',
    effects: {
      conditions: [{
        type: 'disengaged',
        duration: 1,
        source: 'disengage_action',
        effect: 'Movement does not provoke opportunity attacks'
      }]
    }
  },
  {
    id: 'search',
    name: 'Search',
    actionType: 'action',
    category: 'search',
    description: 'Make a Wisdom (Perception) check to search for hidden creatures or objects.',
    savingThrow: {
      ability: 'wisdom',
      dc: 15
    }
  },
  {
    id: 'use_object',
    name: 'Use Object',
    actionType: 'action',
    category: 'use_object',
    description: 'Interact with an object or use a magic item.',
  }
];

// Bonus actions
export const BONUS_ACTIONS: CombatAction[] = [
  {
    id: 'offhand_attack',
    name: 'Off-hand Attack',
    actionType: 'bonus_action',
    category: 'attack',
    description: 'Make an attack with a light weapon in your off-hand.',
    damage: {
      dice: '1d6',
      type: 'slashing',
      modifier: 0
    },
    attackBonus: 0,
    range: {
      normal: 5,
      maximum: 5
    },
    requirements: {
      weaponType: 'light'
    }
  },
  {
    id: 'second_wind',
    name: 'Second Wind',
    actionType: 'bonus_action',
    category: 'spell',
    description: 'Regain hit points equal to 1d10 + your fighter level.',
    effects: {
      healing: '1d10+1'
    },
    requirements: {
      minimumLevel: 1
    }
  }
];

// Movement actions
export const MOVEMENT_ACTIONS: CombatAction[] = [
  {
    id: 'move',
    name: 'Move',
    actionType: 'movement',
    category: 'move',
    description: 'Move up to your speed.',
    effects: {
      movement: 30 // This would be calculated based on character speed
    }
  },
  {
    id: 'stand_up',
    name: 'Stand Up',
    actionType: 'movement',
    category: 'move',
    description: 'Stand up from prone. Costs half your movement speed.',
    effects: {
      movement: -15 // Half movement cost
    }
  }
];

// Reaction actions
export const REACTION_ACTIONS: CombatAction[] = [
  {
    id: 'opportunity_attack',
    name: 'Opportunity Attack',
    actionType: 'reaction',
    category: 'attack',
    description: 'Make a melee attack against a creature that leaves your reach.',
    damage: {
      dice: '1d6',
      type: 'slashing',
      modifier: 0
    },
    attackBonus: 0,
    range: {
      normal: 5,
      maximum: 5
    }
  }
];

// Spell actions (basic examples)
export const SPELL_ACTIONS: CombatAction[] = [
  {
    id: 'fire_bolt',
    name: 'Fire Bolt',
    actionType: 'action',
    category: 'spell',
    description: 'A mote of fire streaks toward a creature or object within range.',
    damage: {
      dice: '1d10',
      type: 'fire',
      modifier: 0
    },
    attackBonus: 0,
    range: {
      normal: 120,
      maximum: 120
    },
    requirements: {
      spellSlot: 0 // Cantrip
    }
  },
  {
    id: 'cure_wounds',
    name: 'Cure Wounds',
    actionType: 'action',
    category: 'spell',
    description: 'Touch a creature to restore hit points.',
    effects: {
      healing: '1d8+3'
    },
    range: {
      normal: 5,
      maximum: 5
    },
    requirements: {
      spellSlot: 1
    }
  },
  {
    id: 'healing_word',
    name: 'Healing Word',
    actionType: 'bonus_action',
    category: 'spell',
    description: 'Speak a word of healing to restore hit points at range.',
    effects: {
      healing: '1d4+3'
    },
    range: {
      normal: 60,
      maximum: 60
    },
    requirements: {
      spellSlot: 1
    }
  }
];

// Combine all actions
export const ALL_ACTIONS = [
  ...BASIC_ACTIONS,
  ...BONUS_ACTIONS,
  ...MOVEMENT_ACTIONS,
  ...REACTION_ACTIONS,
  ...SPELL_ACTIONS
];

// Helper functions to get actions by type
export function getActionsByType(actionType: ActionType): CombatAction[] {
  return ALL_ACTIONS.filter(action => action.actionType === actionType);
}

export function getActionsByCategory(category: CombatAction['category']): CombatAction[] {
  return ALL_ACTIONS.filter(action => action.category === category);
}

export function getActionById(id: string): CombatAction | undefined {
  return ALL_ACTIONS.find(action => action.id === id);
}

// Get available actions for a combatant based on their current state
export function getAvailableActions(
  combatant: any, // Would be Combatant type but avoiding circular import
  actionType?: ActionType
): CombatAction[] {
  let availableActions = ALL_ACTIONS;

  // Filter by action type if specified
  if (actionType) {
    availableActions = availableActions.filter(action => action.actionType === actionType);
  }

  // Filter based on requirements
  availableActions = availableActions.filter(action => {
    if (!action.requirements) return true;

    // Check level requirement
    if (action.requirements.minimumLevel && combatant.level < action.requirements.minimumLevel) {
      return false;
    }

    // Check spell slot requirement
    if (action.requirements.spellSlot && !combatant.spellSlots?.[action.requirements.spellSlot]) {
      return false;
    }

    // Check weapon type requirement
    if (action.requirements.weaponType && !combatant.equipment?.weapon?.type?.includes(action.requirements.weaponType)) {
      return false;
    }

    return true;
  });

  return availableActions;
} 