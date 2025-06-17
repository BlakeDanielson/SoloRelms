'use client';

import React, { useState, useEffect } from 'react';
import { useCombat } from '../../../hooks/useCombat';
import { Combatant, CombatAction, CombatActionResult } from '../../../lib/combat/types';
import ActionSelection from '../../../components/game/ActionSelection';
import TargetSelection from '../../../components/game/TargetSelection';
import CombatLog from '../../../components/game/CombatLog';
import VirtualizedCombatLog from '../../../components/game/VirtualizedCombatLog';
import AnimatedHealthBar from '../../../components/game/AnimatedHealthBar';
import CombatActionAnimations from '../../../components/game/CombatActionAnimations';
import ProjectileEffects from '../../../components/game/ProjectileEffects';
import ParticleSystem, { createParticleEffect } from '../../../components/game/ParticleSystem';
import { Sword, Shield, Heart, Zap, RotateCcw, Play } from 'lucide-react';

// Mock combatants for testing
const createMockPlayer = (id: string, name: string): Combatant => ({
  id,
  name,
  type: 'player',
  health: { current: 25, max: 25, temporary: 0 },
  armorClass: 15,
  speed: 30,
  stats: {
    strength: 14,
    dexterity: 16,
    constitution: 13,
    intelligence: 12,
    wisdom: 14,
    charisma: 10
  },
  modifiers: {
    strength: 2,
    dexterity: 3,
    constitution: 1,
    intelligence: 1,
    wisdom: 2,
    charisma: 0
  },
  initiative: 0,
  conditions: []
});

const createMockEnemy = (id: string, name: string): Combatant => ({
  id,
  name,
  type: 'enemy',
  health: { current: 15, max: 15, temporary: 0 },
  armorClass: 13,
  speed: 25,
  stats: {
    strength: 12,
    dexterity: 14,
    constitution: 12,
    intelligence: 8,
    wisdom: 10,
    charisma: 6
  },
  modifiers: {
    strength: 1,
    dexterity: 2,
    constitution: 1,
    intelligence: -1,
    wisdom: 0,
    charisma: -2
  },
  initiative: 0,
  conditions: []
});

export default function CombatTestPage() {
  const combat = useCombat();
  const [showActionSelection, setShowActionSelection] = useState(false);
  const [showTargetSelection, setShowTargetSelection] = useState(false);
  const [selectedAction, setSelectedAction] = useState<CombatAction | null>(null);
  const [selectedTarget, setSelectedTarget] = useState<Combatant | null>(null);
  const [actionAnimation, setActionAnimation] = useState<{
    action: CombatAction;
    result?: CombatActionResult;
    isVisible: boolean;
  } | null>(null);
    const [projectileEffect, setProjectileEffect] = useState<{
    id: string;
    action: CombatAction;
    result?: CombatActionResult;
    startPosition: { x: number; y: number };
    endPosition: { x: number; y: number };
    isVisible: boolean;
  } | null>(null);
  const [particleEffect, setParticleEffect] = useState<any>(null);
  const [testParticipants] = useState<Combatant[]>([ 
    createMockPlayer('player1', 'Aria the Rogue'),
    createMockPlayer('player2', 'Thorin the Fighter'),
    createMockEnemy('enemy1', 'Goblin Warrior'),
    createMockEnemy('enemy2', 'Orc Brute')
  ]);

  // Watch for new action results to trigger animations
  useEffect(() => {
    const currentRound = combat.combatState.currentRound;
    if (currentRound.actions.length > 0) {
      const latestAction = currentRound.actions[currentRound.actions.length - 1];
      
      // Only animate if this is a new action (simple check)
      if (actionAnimation?.result?.timestamp !== latestAction.timestamp) {
        // Check if this action should show a projectile effect
        const isProjectileAction = (
          latestAction.action.category === 'attack' && 
          latestAction.action.name.toLowerCase().includes('bow')
        ) || (
          latestAction.action.category === 'spell' && 
          ['fire bolt', 'ray of frost', 'eldritch blast', 'magic missile'].some(spell => 
            latestAction.action.name.toLowerCase().includes(spell.toLowerCase())
          )
        );

        if (isProjectileAction) {
          // Show projectile effect for ranged attacks and spells
          setProjectileEffect({
            id: `projectile-${latestAction.timestamp}`,
            action: latestAction.action,
            result: latestAction,
            startPosition: { x: 200, y: 300 }, // Mock attacker position
            endPosition: { x: 600, y: 300 },   // Mock target position
            isVisible: true
          });
          
          // Hide projectile after animation completes
          setTimeout(() => {
            setProjectileEffect(prev => prev ? { ...prev, isVisible: false } : null);
          }, 2000);
        } else {
          // Show regular action animation for melee attacks and non-projectile spells
          setActionAnimation({
            action: latestAction.action,
            result: latestAction,
            isVisible: true
          });
          
          // Auto-hide animation after 3 seconds
          setTimeout(() => {
            setActionAnimation(prev => prev ? { ...prev, isVisible: false } : null);
          }, 3000);
        }

        // Trigger particle effects based on action result
        const getParticleType = () => {
          if (latestAction.result.criticalHit) return 'critical';
          if (!latestAction.result.hit) return 'miss';
          if (latestAction.action.category === 'spell') {
            if (latestAction.action.name.toLowerCase().includes('heal')) return 'healing';
            if (latestAction.action.damage?.type) return 'elemental';
            return 'explosion';
          }
          if (latestAction.action.category === 'attack') return 'explosion';
          return 'buff';
        };

        // Create particle effect at target position
        const newParticleEffect = createParticleEffect(
          getParticleType(),
          { x: 600, y: 300 }, // Mock target position
          latestAction.action,
          latestAction,
          latestAction.result.criticalHit ? 'high' : 'medium'
        );

        setParticleEffect(newParticleEffect);

        // Hide particle effect after duration
        setTimeout(() => {
          setParticleEffect(null);
        }, 3000);
      }
    }
  }, [combat.combatState.currentRound.actions, actionAnimation]);

  const handleStartCombat = () => {
    combat.startCombat(testParticipants);
  };

  const handleSelectAction = () => {
    setShowActionSelection(true);
  };

  const handleActionSelected = (action: CombatAction) => {
    setSelectedAction(action);
    setShowActionSelection(false);
    
    // Check if action needs a target
    if (action.category === 'attack' || (action.category === 'spell' && action.savingThrow)) {
      setShowTargetSelection(true);
    } else {
      // Actions that don't need targets can be executed immediately
      console.log('Action selected:', action);
      combat.selectAction(action);
    }
  };

  const handleTargetSelect = (target: Combatant) => {
    if (!selectedAction) return;
    
    // Add target to action
    const actionWithTarget = {
      ...selectedAction,
      target: target.id
    };
    
    setSelectedTarget(target);
    setShowTargetSelection(false);
    console.log('Action with target selected:', actionWithTarget);
    combat.selectAction(actionWithTarget);
  };

  const handleCancelTargetSelection = () => {
    setShowTargetSelection(false);
    setSelectedAction(null);
    setSelectedTarget(null);
  };

  const handleEndTurn = () => {
    combat.endTurn();
  };

  const handleResetCombat = () => {
    combat.resetCombat();
    setShowActionSelection(false);
  };

  const getStateColor = () => {
    if (combat.isIdle) return 'bg-gray-600';
    if (combat.isRollingInitiative) return 'bg-yellow-600';
    if (combat.isPlayerTurn) return 'bg-green-600';
    if (combat.isEnemyTurn) return 'bg-red-600';
    if (combat.isResolvingAction) return 'bg-purple-600';
    if (combat.isEnded) return 'bg-blue-600';
    return 'bg-gray-600';
  };

  const getStateText = () => {
    if (combat.isIdle) return 'Idle';
    if (combat.isRollingInitiative) return 'Rolling Initiative';
    if (combat.isPlayerTurn) return 'Player Turn';
    if (combat.isEnemyTurn) return 'Enemy Turn';
    if (combat.isResolvingAction) return 'Resolving Action';
    if (combat.isEnded) return 'Combat Ended';
    return 'Unknown';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="bg-black/40 backdrop-blur-sm rounded-lg border border-white/10 p-6 mb-6">
          <h1 className="text-3xl font-bold text-white mb-2">Combat System Test</h1>
          <p className="text-gray-300">Testing XState combat state machine and initiative system</p>
        </div>

        {/* Combat State */}
        <div className="bg-black/40 backdrop-blur-sm rounded-lg border border-white/10 p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-white">Combat State</h2>
            <div className={`px-4 py-2 rounded-full text-white font-medium ${getStateColor()}`}>
              {getStateText()}
            </div>
          </div>

          {/* Combat Controls */}
          <div className="flex gap-4 mb-6">
            <button
              onClick={handleStartCombat}
              disabled={!combat.isIdle}
              className="flex items-center bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white px-4 py-2 rounded-md transition-colors"
            >
              <Play className="w-4 h-4 mr-2" />
              Start Combat
            </button>
            
            <button
              onClick={handleSelectAction}
              disabled={!combat.isPlayerTurn}
              className="flex items-center bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 text-white px-4 py-2 rounded-md transition-colors"
            >
              <Zap className="w-4 h-4 mr-2" />
              Select Action
            </button>
            
            <button
              onClick={handleEndTurn}
              disabled={!combat.isPlayerTurn}
              className="flex items-center bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white px-4 py-2 rounded-md transition-colors"
            >
              <Zap className="w-4 h-4 mr-2" />
              End Turn
            </button>
            
            <button
              onClick={handleResetCombat}
              className="flex items-center bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md transition-colors"
            >
              <RotateCcw className="w-4 h-4 mr-2" />
              Reset Combat
            </button>
          </div>

          {/* Combat Info */}
          {combat.combatState.isActive && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div className="bg-gray-800/50 rounded-lg p-3">
                <div className="text-gray-300 font-medium">Round</div>
                <div className="text-white text-lg">{combat.combatState.currentRound.number}</div>
              </div>
              
              <div className="bg-gray-800/50 rounded-lg p-3">
                <div className="text-gray-300 font-medium">Current Turn</div>
                <div className="text-white text-lg">
                  {combat.currentCombatant?.name || 'None'}
                </div>
              </div>
              
              <div className="bg-gray-800/50 rounded-lg p-3">
                <div className="text-gray-300 font-medium">Turn Index</div>
                <div className="text-white text-lg">
                  {combat.combatState.currentRound.currentTurnIndex + 1} / {combat.combatState.currentRound.turnOrder.length}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Participants */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Players */}
          <div className="bg-black/40 backdrop-blur-sm rounded-lg border border-white/10 p-6">
            <h3 className="text-xl font-bold text-white mb-4 flex items-center">
              <Shield className="w-5 h-5 mr-2 text-green-400" />
              Players
            </h3>
            <div className="space-y-3">
              {combat.combatState.participants
                .filter(p => p.type === 'player')
                .map((participant) => (
                  <div
                    key={participant.id}
                    className={`bg-gray-800/50 rounded-lg border-2 transition-colors ${
                      combat.currentCombatant?.id === participant.id
                        ? 'border-green-400 bg-green-900/20'
                        : 'border-transparent'
                    }`}
                  >
                    <AnimatedHealthBar
                      current={participant.health.current}
                      max={participant.health.max}
                      temporary={participant.health.temporary}
                      name={participant.name}
                      isDead={participant.health.current <= 0}
                      armorClass={participant.armorClass}
                      size="md"
                      className="mb-2"
                    />
                    <div className="px-3 pb-2">
                      <div className="text-sm text-gray-400">
                        Initiative: {participant.initiative}
                      </div>
                    </div>
                  </div>
                ))}
            </div>
          </div>

          {/* Enemies */}
          <div className="bg-black/40 backdrop-blur-sm rounded-lg border border-white/10 p-6">
            <h3 className="text-xl font-bold text-white mb-4 flex items-center">
              <Sword className="w-5 h-5 mr-2 text-red-400" />
              Enemies
            </h3>
            <div className="space-y-3">
              {combat.combatState.participants
                .filter(p => p.type === 'enemy')
                .map((participant) => (
                  <div
                    key={participant.id}
                    className={`bg-gray-800/50 rounded-lg border-2 transition-colors ${
                      combat.currentCombatant?.id === participant.id
                        ? 'border-red-400 bg-red-900/20'
                        : 'border-transparent'
                    }`}
                  >
                    <AnimatedHealthBar
                      current={participant.health.current}
                      max={participant.health.max}
                      temporary={participant.health.temporary}
                      name={participant.name}
                      isDead={participant.health.current <= 0}
                      armorClass={participant.armorClass}
                      size="md"
                      className="mb-2"
                    />
                    <div className="px-3 pb-2">
                      <div className="text-sm text-gray-400">
                        Initiative: {participant.initiative}
                      </div>
                    </div>
                  </div>
                ))}
            </div>
          </div>
        </div>

        {/* Initiative Order and Combat Log */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
          {/* Initiative Order */}
          {combat.combatState.isActive && (
            <div className="bg-black/40 backdrop-blur-sm rounded-lg border border-white/10 p-6">
              <h3 className="text-xl font-bold text-white mb-4">Initiative Order</h3>
              <div className="flex flex-wrap gap-2">
                {combat.combatState.currentRound.turnOrder.map((participantId, index) => {
                  const participant = combat.combatState.participants.find(p => p.id === participantId);
                  const isCurrent = index === combat.combatState.currentRound.currentTurnIndex;
                  
                  return (
                    <div
                      key={participantId}
                      className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                        isCurrent
                          ? participant?.type === 'player'
                            ? 'bg-green-600 text-white'
                            : 'bg-red-600 text-white'
                          : 'bg-gray-700 text-gray-300'
                      }`}
                    >
                      {index + 1}. {participant?.name} ({participant?.initiative})
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Virtualized Combat Log */}
          <div>
            <VirtualizedCombatLog
              actionResults={combat.combatState.currentRound.actions}
              participants={combat.combatState.participants}
              maxHeight={400}
              showTimestamps={true}
              showDamageNumbers={true}
              autoScroll={true}
            />
          </div>
        </div>

        {/* Debug Info */}
        <div className="bg-black/40 backdrop-blur-sm rounded-lg border border-white/10 p-6 mt-6">
          <h3 className="text-xl font-bold text-white mb-4">Debug Info</h3>
          
          {/* RNG Debug Info */}
          {combat.combatRNG && (
            <div className="mb-4 p-3 bg-yellow-900/20 rounded border border-yellow-600/30">
              <div className="font-semibold text-yellow-400 mb-2">🎲 Deterministic RNG Status:</div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-300">
                <div>
                  <span className="text-yellow-300">Seed:</span> {combat.combatRNG.getSeed()}
                </div>
                <div>
                  <span className="text-yellow-300">Calls Made:</span> {combat.combatRNG.getCallCount()}
                </div>
                <div>
                  <span className="text-yellow-300">Next Values:</span> [{combat.combatRNG.getDebugInfo().nextPreview.join(', ')}]
                </div>
              </div>
            </div>
          )}
          
          <pre className="text-xs text-gray-300 bg-gray-900/50 rounded p-4 overflow-auto">
            {JSON.stringify(combat.machineState.value, null, 2)}
          </pre>
        </div>
      </div>

      {/* Action Selection Modal */}
      {showActionSelection && combat.currentCombatant && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <ActionSelection
              combatant={combat.currentCombatant}
              onActionSelect={handleActionSelected}
              onCancel={() => setShowActionSelection(false)}
            />
          </div>
        </div>
      )}

      {/* Target Selection Modal */}
      {showTargetSelection && selectedAction && combat.currentCombatant && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <TargetSelection
              actor={combat.currentCombatant}
              action={selectedAction}
              allCombatants={combat.combatState.participants}
              onTargetSelect={handleTargetSelect}
              onCancel={handleCancelTargetSelection}
              selectedTarget={selectedTarget}
            />
          </div>
        </div>
      )}

      {/* Combat Action Animations */}
      {actionAnimation && (
        <CombatActionAnimations
          action={actionAnimation.action}
          result={actionAnimation.result}
          isVisible={actionAnimation.isVisible}
          onAnimationComplete={() => setActionAnimation(null)}
        />
      )}

      {/* Projectile Effects */}
      {projectileEffect && (
        <ProjectileEffects
          projectile={projectileEffect}
          onProjectileComplete={() => setProjectileEffect(null)}
        />
      )}

      {/* Particle Effects */}
      {particleEffect && (
        <ParticleSystem
          effect={particleEffect}
          onEffectComplete={() => setParticleEffect(null)}
        />
      )}
    </div>
  );
} 