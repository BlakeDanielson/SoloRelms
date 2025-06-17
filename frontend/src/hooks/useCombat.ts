import { useMachine } from '@xstate/react';
import { useCallback } from 'react';
import { combatMachine } from '../lib/combat/stateMachine';
import { Combatant, CombatAction, CombatContext } from '../lib/combat/types';
import { generateRandomSeed } from '../lib/combat/rng';

export function useCombat() {
  const [state, send] = useMachine(combatMachine);

  const startCombat = useCallback((participants: Combatant[], seed?: string) => {
    const combatSeed = seed || generateRandomSeed();
    send({
      type: 'START_COMBAT',
      participants,
      seed: combatSeed
    });
  }, [send]);

  const rollInitiative = useCallback(() => {
    send({ type: 'ROLL_INITIATIVE' });
  }, [send]);

  const selectAction = useCallback((action: CombatAction) => {
    send({
      type: 'SELECT_ACTION',
      action
    });
  }, [send]);

  const endTurn = useCallback(() => {
    send({ type: 'END_TURN' });
  }, [send]);

  const endCombat = useCallback((winner: 'players' | 'enemies' | 'draw') => {
    send({
      type: 'END_COMBAT',
      winner
    });
  }, [send]);

  const resetCombat = useCallback(() => {
    send({ type: 'RESET_COMBAT' });
  }, [send]);

  // Helper getters
  const isIdle = state.matches('idle');
  const isRollingInitiative = state.matches('initiative');
  const isInCombat = state.matches('combat');
  const isPlayerTurn = state.matches({ combat: 'playerTurn' });
  const isEnemyTurn = state.matches({ combat: 'enemyTurn' });
  const isResolvingAction = state.matches({ combat: 'resolvingAction' });
  const isEnded = state.matches('ended');

  const combatState = (state.context as CombatContext).state;
  const combatRNG = (state.context as CombatContext).combatRNG;
  const currentCombatant = combatState.participants.find(
    p => p.id === combatState.currentRound.turnOrder[combatState.currentRound.currentTurnIndex]
  );

  return {
    // State checks
    isIdle,
    isRollingInitiative,
    isInCombat,
    isPlayerTurn,
    isEnemyTurn,
    isResolvingAction,
    isEnded,
    
    // Combat data
    combatState,
    currentCombatant,
    combatRNG,
    
    // Actions
    startCombat,
    rollInitiative,
    selectAction,
    endTurn,
    endCombat,
    resetCombat,
    
    // Raw state machine state for debugging
    machineState: state
  };
} 