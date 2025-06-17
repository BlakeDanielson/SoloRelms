import { assign, setup } from 'xstate';
import { CombatContext, CombatEvent, CombatState, Combatant, CombatActionResult } from './types';
import { generateCombatId, calculateModifier, resolveAction, applyActionResult } from './utils';
import { CombatRNG, generateRandomSeed } from './rng';
import { 
  initializeCombatState, 
  updateInitiativeProducer, 
  setTurnOrderProducer,
  advanceTurnProducer,
  recordActionResultProducer,
  endCombatProducer,
  resetCombatProducer,
  withValidation
} from './stateProducers';
import seedrandom from 'seedrandom';

export const combatMachine = setup({
  types: {
    context: {} as CombatContext,
    events: {} as CombatEvent
  },
  actions: {
    initializeCombat: assign(({ context, event }) => {
      if (event.type !== 'START_COMBAT') return context;
      
      const combatState: CombatState = {
        id: generateCombatId(),
        participants: event.participants.map(p => ({ ...p, initiative: 0 })),
        currentRound: {
          number: 1,
          turnOrder: [],
          currentTurnIndex: 0,
          actions: []
        },
        history: [],
        isActive: true,
        seed: event.seed
      };
      
      const combatRNG = new CombatRNG(event.seed);
      
      return {
        state: combatState,
        rng: seedrandom(event.seed), // Keep legacy for compatibility
        combatRNG
      };
    }),

    rollInitiative: assign(({ context }) => {
      const { state, combatRNG } = context;
      const participantsWithInitiative = state.participants.map(participant => ({
        ...participant,
        initiative: combatRNG ? 
          combatRNG.rollInitiative(calculateModifier(participant.stats.dexterity)) :
          Math.floor(Math.random() * 20) + 1 + calculateModifier(participant.stats.dexterity)
      }));

      // Sort by initiative (highest first)
      const turnOrder = participantsWithInitiative
        .sort((a, b) => b.initiative - a.initiative)
        .map(p => p.id);

      return {
        ...context,
        state: {
          ...state,
          participants: participantsWithInitiative,
          currentRound: {
            ...state.currentRound,
            turnOrder,
            currentTurnIndex: 0
          }
        }
      };
    }),

    startRound: assign(({ context }) => ({
      ...context,
      state: {
        ...context.state,
        currentRound: {
          ...context.state.currentRound,
          actions: []
        }
      }
    })),

    startPlayerTurn: assign(({ context }) => {
      const currentCombatant = getCurrentCombatant(context.state);
      console.log(`Starting turn for: ${currentCombatant?.name} (Player)`);
      return context;
    }),

    startEnemyTurn: assign(({ context }) => {
      const currentCombatant = getCurrentCombatant(context.state);
      console.log(`Starting turn for: ${currentCombatant?.name} (Enemy)`);
      return context;
    }),

    storeSelectedAction: assign(({ context, event }) => {
      if (event.type !== 'SELECT_ACTION') return context;
      
      return {
        ...context,
        selectedAction: event.action
      };
    }),

    selectEnemyAction: assign(({ context }) => {
      // For now, select a basic attack action for enemies
      // This would be more sophisticated in a real implementation
      const basicAttack = {
        id: 'enemy_attack',
        name: 'Basic Attack',
        actionType: 'action' as const,
        category: 'attack' as const,
        description: 'Enemy makes a basic attack',
        damage: { dice: '1d6+2', type: 'slashing' as const },
        attackBonus: 4
      };
      
      return {
        ...context,
        selectedAction: basicAttack
      };
    }),

    resolveAction: assign(({ context }) => {
      const { state, rng, selectedAction } = context;
      
      if (!selectedAction) return context;
      
      const currentCombatant = getCurrentCombatant(state);
      if (!currentCombatant) return context;
      
      // Determine target for attack actions
      let target = null;
      if (selectedAction.category === 'attack') {
        // Find first available enemy target
        const validTargets = state.participants.filter(p => 
          p.id !== currentCombatant.id && 
          p.type !== currentCombatant.type && 
          p.health.current > 0
        );
        target = validTargets[0] || null;
        
        if (target) {
          selectedAction.target = target.id;
        }
      }
      
      try {
        // Resolve the action
        const actionResult = resolveAction(currentCombatant, target, selectedAction, rng);
        
        // Apply the result to update combatant states
        const updatedParticipants = applyActionResult(state.participants, actionResult);
        
        // Add result to current round actions
        const updatedRound = {
          ...state.currentRound,
          actions: [...state.currentRound.actions, actionResult]
        };
        
        return {
          ...context,
          state: {
            ...state,
            participants: updatedParticipants,
            currentRound: updatedRound
          },
          selectedAction: undefined
        };
      } catch (error) {
        console.error('Error resolving action:', error);
        return {
          ...context,
          selectedAction: undefined
        };
      }
    }),

    nextTurn: assign(({ context }) => ({
      ...context,
      state: {
        ...context.state,
        currentRound: {
          ...context.state.currentRound,
          currentTurnIndex: (context.state.currentRound.currentTurnIndex + 1) % context.state.currentRound.turnOrder.length
        }
      }
    })),

    nextRound: assign(({ context }) => ({
      ...context,
      state: {
        ...context.state,
        history: [...context.state.history, context.state.currentRound],
        currentRound: {
          number: context.state.currentRound.number + 1,
          turnOrder: context.state.currentRound.turnOrder,
          currentTurnIndex: 0,
          actions: []
        }
      }
    })),

    endCombat: assign(({ context }) => {
      const winner = determineWinner(context.state);
      console.log(`Combat ended. Winner: ${winner}`);
      return {
        ...context,
        state: {
          ...context.state,
          isActive: false,
          winner
        }
      };
    }),

    resetCombat: assign(() => ({
      state: {
        id: '',
        participants: [],
        currentRound: {
          number: 0,
          turnOrder: [],
          currentTurnIndex: 0,
          actions: []
        },
        history: [],
        isActive: false,
        seed: ''
      },
      rng: () => Math.random()
    }))
  },

  guards: {
    isCombatEnded: ({ context }) => {
      const { participants } = context.state;
      const alivePlayers = participants.filter(p => p.type === 'player' && p.health.current > 0);
      const aliveEnemies = participants.filter(p => p.type === 'enemy' && p.health.current > 0);
      return alivePlayers.length === 0 || aliveEnemies.length === 0;
    },

    isPlayerTurn: ({ context }) => {
      const currentCombatant = getCurrentCombatant(context.state);
      return currentCombatant?.type === 'player';
    },

    isEnemyTurn: ({ context }) => {
      const currentCombatant = getCurrentCombatant(context.state);
      return currentCombatant?.type === 'enemy' || currentCombatant?.type === 'npc';
    }
  }
}).createMachine({
  id: 'combat',
  initial: 'idle',
  context: {
    state: {
      id: '',
      participants: [],
      currentRound: {
        number: 0,
        turnOrder: [],
        currentTurnIndex: 0,
        actions: []
      },
      history: [],
      isActive: false,
      seed: ''
    },
    rng: () => Math.random(),
    combatRNG: undefined,
    selectedAction: undefined
  },
  states: {
    idle: {
      on: {
        START_COMBAT: {
          target: 'initiative',
          actions: 'initializeCombat'
        }
      }
    },
    initiative: {
      entry: 'rollInitiative',
      on: {
        ROLL_INITIATIVE: {
          target: 'combat'
        }
      },
      after: {
        1000: 'combat' // Auto-transition after 1 second
      }
    },
    combat: {
      initial: 'playerTurn',
      entry: 'startRound',
      states: {
        playerTurn: {
          entry: 'startPlayerTurn',
          on: {
            SELECT_ACTION: {
              target: 'resolvingAction',
              actions: 'storeSelectedAction'
            },
            END_TURN: 'checkingTurnEnd'
          }
        },
        enemyTurn: {
          entry: 'startEnemyTurn',
          on: {
            SELECT_ACTION: {
              target: 'resolvingAction',
              actions: 'storeSelectedAction'
            },
            END_TURN: 'checkingTurnEnd'
          },
          after: {
            2000: { // Auto-play enemy turn after 2 seconds
              target: 'resolvingAction',
              actions: 'selectEnemyAction'
            }
          }
        },
        resolvingAction: {
          entry: 'resolveAction',
          on: {
            RESOLVE_ACTION: 'checkingTurnEnd'
          },
          after: {
            1500: 'checkingTurnEnd' // Auto-transition after resolution
          }
        },
        checkingTurnEnd: {
          always: [
            {
              target: '#combat.ended',
              guard: 'isCombatEnded'
            },
            {
              target: 'playerTurn',
              guard: 'isPlayerTurn',
              actions: 'nextTurn'
            },
            {
              target: 'enemyTurn',
              guard: 'isEnemyTurn',
              actions: 'nextTurn'
            },
            {
              target: 'playerTurn',
              actions: ['nextRound', 'nextTurn']
            }
          ]
        }
      }
    },
    ended: {
      id: 'ended',
      entry: 'endCombat',
      on: {
        RESET_COMBAT: {
          target: 'idle',
          actions: 'resetCombat'
        }
      }
    }
  }
});

// Helper functions
function getCurrentCombatant(state: CombatState): Combatant | undefined {
  const currentId = state.currentRound.turnOrder[state.currentRound.currentTurnIndex];
  return state.participants.find(p => p.id === currentId);
}

function determineWinner(state: CombatState): CombatState['winner'] {
  const alivePlayers = state.participants.filter(p => p.type === 'player' && p.health.current > 0);
  const aliveEnemies = state.participants.filter(p => p.type === 'enemy' && p.health.current > 0);
  
  if (alivePlayers.length === 0 && aliveEnemies.length === 0) {
    return 'draw';
  } else if (alivePlayers.length === 0) {
    return 'enemies';
  } else if (aliveEnemies.length === 0) {
    return 'players';
  }
  
  return undefined;
} 