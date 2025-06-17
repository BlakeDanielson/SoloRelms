import { produce } from 'immer';
import { CombatState, Combatant, CombatActionResult, CombatRound, StatusCondition } from './types';

/**
 * Producer function to initialize a new combat state
 */
export const initializeCombatState = produce((draft: CombatState, {
  id,
  participants,
  seed
}: {
  id: string;
  participants: Combatant[];
  seed: string;
}) => {
  draft.id = id;
  draft.participants = participants;
  draft.isActive = true;
  draft.seed = seed;
  draft.currentRound = {
    number: 1,
    turnOrder: [],
    currentTurnIndex: 0,
    actions: []
  };
  draft.history = [];
});

/**
 * Producer function to update participant initiative values
 */
export const updateInitiativeProducer = produce((draft: CombatState, initiativeUpdates: Array<{
  participantId: string;
  initiative: number;
}>) => {
  initiativeUpdates.forEach(({ participantId, initiative }) => {
    const participant = draft.participants.find(p => p.id === participantId);
    if (participant) {
      participant.initiative = initiative;
    }
  });
});

/**
 * Producer function to set turn order based on initiative
 */
export const setTurnOrderProducer = produce((draft: CombatState, turnOrder: string[]) => {
  draft.currentRound.turnOrder = turnOrder;
  draft.currentRound.currentTurnIndex = 0;
});

/**
 * Producer function to advance to the next turn
 */
export const advanceTurnProducer = produce((draft: CombatState) => {
  const { turnOrder, currentTurnIndex } = draft.currentRound;
  
  if (currentTurnIndex < turnOrder.length - 1) {
    // Move to next participant in current round
    draft.currentRound.currentTurnIndex = currentTurnIndex + 1;
  } else {
    // Start new round
    draft.currentRound.number += 1;
    draft.currentRound.currentTurnIndex = 0;
    draft.currentRound.actions = []; // Clear actions from previous round
  }
});

/**
 * Producer function to apply damage to a combatant
 */
export const applyDamageProducer = produce((draft: CombatState, {
  targetId,
  damage,
  damageType
}: {
  targetId: string;
  damage: number;
  damageType?: string;
}) => {
  const target = draft.participants.find(p => p.id === targetId);
  if (target) {
    const actualDamage = Math.max(0, damage);
    target.health.current = Math.max(0, target.health.current - actualDamage);
    
    // Track damage taken for combat log
    if (!target.combatStats) {
      target.combatStats = {
        damageTaken: 0,
        damageDealt: 0,
        healingReceived: 0,
        actionsTaken: 0
      };
    }
    target.combatStats.damageTaken += actualDamage;
  }
});

/**
 * Producer function to apply healing to a combatant
 */
export const applyHealingProducer = produce((draft: CombatState, {
  targetId,
  healing
}: {
  targetId: string;
  healing: number;
}) => {
  const target = draft.participants.find(p => p.id === targetId);
  if (target) {
    const actualHealing = Math.max(0, healing);
    const oldHealth = target.health.current;
    target.health.current = Math.min(target.health.max, target.health.current + actualHealing);
    const healingApplied = target.health.current - oldHealth;
    
    // Track healing received for combat log
    if (!target.combatStats) {
      target.combatStats = {
        damageTaken: 0,
        damageDealt: 0,
        healingReceived: 0,
        actionsTaken: 0
      };
    }
    target.combatStats.healingReceived += healingApplied;
  }
});

/**
 * Producer function to add a status condition to a combatant
 */
export const addStatusConditionProducer = produce((draft: CombatState, {
  targetId,
  condition
}: {
  targetId: string;
  condition: StatusCondition;
}) => {
  const target = draft.participants.find(p => p.id === targetId);
  if (target) {
    if (!target.conditions) {
      target.conditions = [];
    }
    
    // Remove existing condition of the same type if it exists
    target.conditions = target.conditions.filter(c => c.type !== condition.type);
    
    // Add the new condition
    target.conditions.push(condition);
  }
});

/**
 * Producer function to remove a status condition from a combatant
 */
export const removeStatusConditionProducer = produce((draft: CombatState, {
  targetId,
  conditionType
}: {
  targetId: string;
  conditionType: string;
}) => {
  const target = draft.participants.find(p => p.id === targetId);
  if (target && target.conditions) {
    target.conditions = target.conditions.filter(c => c.type !== conditionType);
  }
});

/**
 * Producer function to update status condition durations
 */
export const updateStatusConditionDurationsProducer = produce((draft: CombatState) => {
  draft.participants.forEach(participant => {
    if (participant.conditions) {
      participant.conditions = participant.conditions
        .map(condition => ({
          ...condition,
          duration: condition.duration > 0 ? condition.duration - 1 : 0
        }))
        .filter(condition => condition.duration > 0); // Remove expired conditions
    }
  });
});

/**
 * Producer function to record an action result in the combat round
 */
export const recordActionResultProducer = produce((draft: CombatState, actionResult: CombatActionResult) => {
  draft.currentRound.actions.push(actionResult);
  
  // Update actor's combat stats
  const actor = draft.participants.find(p => p.id === actionResult.actor);
  if (actor) {
    if (!actor.combatStats) {
      actor.combatStats = {
        damageTaken: 0,
        damageDealt: 0,
        healingReceived: 0,
        actionsTaken: 0
      };
    }
    
    actor.combatStats.actionsTaken += 1;
    
    // Track damage dealt if the action caused damage
    if (actionResult.result.damage && actionResult.result.damage > 0) {
      actor.combatStats.damageDealt += actionResult.result.damage;
    }
  }
});

/**
 * Producer function to end combat and set the winner
 */
export const endCombatProducer = produce((draft: CombatState, winner: 'players' | 'enemies' | 'draw') => {
  draft.isActive = false;
  draft.winner = winner;
  
  // Store final round in history
  draft.history.push({
    ...draft.currentRound
  });
});

/**
 * Producer function to reset combat state to initial values
 */
export const resetCombatProducer = produce((draft: CombatState) => {
  draft.id = '';
  draft.participants = [];
  draft.currentRound = {
    number: 0,
    turnOrder: [],
    currentTurnIndex: 0,
    actions: []
  };
  draft.history = [];
  draft.isActive = false;
  draft.seed = '';
});

/**
 * Producer function to update a combatant's temporary stats (like AC bonuses)
 */
export const updateCombatantStatsProducer = produce((draft: CombatState, {
  participantId,
  statUpdates
}: {
  participantId: string;
  statUpdates: Partial<{
    armorClass: number;
    temporaryHitPoints: number;
    speed: number;
  }>;
}) => {
  const participant = draft.participants.find(p => p.id === participantId);
  if (participant) {
    if (statUpdates.armorClass !== undefined) {
      participant.armorClass = statUpdates.armorClass;
    }
    if (statUpdates.temporaryHitPoints !== undefined) {
      participant.health.temporary = statUpdates.temporaryHitPoints;
    }
    if (statUpdates.speed !== undefined) {
      participant.speed = statUpdates.speed;
    }
  }
});

/**
 * Producer function to apply multiple state changes atomically
 */
export const batchUpdateProducer = produce((draft: CombatState, updates: Array<{
  type: 'damage' | 'healing' | 'status_add' | 'status_remove' | 'stat_update';
  payload: any;
}>) => {
  updates.forEach(update => {
    switch (update.type) {
      case 'damage':
        applyDamageProducer(draft, update.payload);
        break;
      case 'healing':
        applyHealingProducer(draft, update.payload);
        break;
      case 'status_add':
        addStatusConditionProducer(draft, update.payload);
        break;
      case 'status_remove':
        removeStatusConditionProducer(draft, update.payload);
        break;
      case 'stat_update':
        updateCombatantStatsProducer(draft, update.payload);
        break;
    }
  });
});

/**
 * Producer function to create a snapshot of the current state for undo/redo
 */
export const createStateSnapshotProducer = produce((draft: CombatState) => {
  // This producer doesn't modify the state, but returns a deep copy
  // The produce function will handle the immutable copy
  return draft;
});

/**
 * Producer function to restore state from a snapshot
 */
export const restoreStateSnapshotProducer = produce((draft: CombatState, snapshot: CombatState) => {
  // Replace all properties with snapshot values
  Object.assign(draft, snapshot);
});

/**
 * Utility function to create a state history entry
 */
export const createHistoryEntry = (state: CombatState, action: string, timestamp: number = Date.now()) => {
  return {
    state: createStateSnapshotProducer(state),
    action,
    timestamp,
    round: state.currentRound.number,
    turn: state.currentRound.currentTurnIndex
  };
};

/**
 * Producer function to validate state consistency
 */
export const validateStateConsistencyProducer = produce((draft: CombatState) => {
  // Ensure all participants have valid health values
  draft.participants.forEach(participant => {
    if (participant.health.current < 0) {
      participant.health.current = 0;
    }
    if (participant.health.current > participant.health.max) {
      participant.health.current = participant.health.max;
    }
    if (participant.health.temporary && participant.health.temporary < 0) {
      participant.health.temporary = 0;
    }
  });
  
  // Ensure turn index is within bounds
  if (draft.currentRound.currentTurnIndex >= draft.currentRound.turnOrder.length) {
    draft.currentRound.currentTurnIndex = 0;
  }
  
  // Ensure round number is at least 1 if combat is active
  if (draft.isActive && draft.currentRound.number < 1) {
    draft.currentRound.number = 1;
  }
});

/**
 * Higher-order producer that wraps any producer with validation
 */
export const withValidation = <T extends any[]>(producer: (...args: T) => (draft: CombatState) => void) => {
  return (...args: T) => produce((draft: CombatState) => {
    producer(...args)(draft);
    validateStateConsistencyProducer(draft);
  });
}; 