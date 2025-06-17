import { useState, useEffect, useCallback } from 'react';
import { adaptStoryData, MajorDecision, NPCStatus, WorldState } from '../lib/narrativeDataAdapter';

interface UseNarrativeContextProps {
  adventureId?: string;
  characterId?: string;
}

interface NarrativeContextData {
  majorDecisions: MajorDecision[];
  npcStatuses: NPCStatus[];
  worldState: WorldState;
  isLoading: boolean;
  error: string | null;
}

/**
 * Hook to manage narrative context data for the current adventure
 */
export function useNarrativeContext({ 
  adventureId, 
  characterId 
}: UseNarrativeContextProps): NarrativeContextData {
  const [data, setData] = useState<NarrativeContextData>({
    majorDecisions: [],
    npcStatuses: [],
    worldState: {
      current_location: 'Unknown',
      explored_areas: [],
      active_objectives: [],
      world_events: [],
      established_lore: {},
      story_time_elapsed: 0,
    },
    isLoading: false,
    error: null,
  });

  const fetchNarrativeData = useCallback(async () => {
    if (!adventureId || !characterId) {
      return;
    }

    setData(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      // Fetch story arc and world state from the backend
      const [storyResponse, worldResponse] = await Promise.all([
        fetch(`/api/adventures/${adventureId}/story-arc`),
        fetch(`/api/adventures/${adventureId}/world-state`),
      ]);

      if (!storyResponse.ok || !worldResponse.ok) {
        throw new Error('Failed to fetch narrative data');
      }

      const storyArc = await storyResponse.json();
      const worldState = await worldResponse.json();

      // Transform the backend data using our adapter
      const adaptedData = adaptStoryData(storyArc, worldState);

      setData(prev => ({
        ...prev,
        ...adaptedData,
        isLoading: false,
      }));
    } catch (error) {
      console.error('Error fetching narrative context:', error);
      setData(prev => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to load narrative data',
      }));
    }
  }, [adventureId, characterId]);

  useEffect(() => {
    fetchNarrativeData();
  }, [fetchNarrativeData]);

  return data;
}

/**
 * Mock hook for development/testing with sample data
 */
export function useMockNarrativeContext(): NarrativeContextData {
  return {
    majorDecisions: [
      {
        id: 'decision-1',
        decision: 'Spare the bandit leader',
        description: 'Instead of executing the captured bandit leader, you chose to show mercy and negotiate.',
        timestamp: new Date(Date.now() - 86400000).toISOString(),
        stage: 'Forest Clearing',
        consequences: ['Gained reputation for mercy', 'Bandits may return later', 'Local villagers are worried'],
        impact_score: 3,
      },
      {
        id: 'decision-2',
        decision: 'Accept the mysterious contract',
        description: 'You decided to take on the strange job offered by the hooded figure in the tavern.',
        timestamp: new Date(Date.now() - 172800000).toISOString(),
        stage: 'The Prancing Pony',
        consequences: ['Gained mysterious ally', '500 gold received', 'Unknown dangers ahead'],
        impact_score: 4,
      },
      {
        id: 'decision-3',
        decision: 'Help the wounded traveler',
        description: 'You stopped to assist an injured merchant on the road, using your healing supplies.',
        timestamp: new Date(Date.now() - 259200000).toISOString(),
        stage: 'Mountain Pass',
        consequences: ['Merchant owes you a favor', 'Used healing potions', 'Delayed travel by 2 hours'],
        impact_score: 2,
      },
    ],
    npcStatuses: [
      {
        id: 'gareth_the_wise',
        name: 'Gareth the Wise',
        status: 'ally',
        health: 'healthy',
        location: 'Millbrook Village',
        disposition: 'friendly',
        relationship_strength: 75,
        first_met: new Date(Date.now() - 604800000).toISOString(),
        last_interaction: new Date(Date.now() - 86400000).toISOString(),
        notes: 'Village elder who provided crucial information about the ancient ruins.',
      },
      {
        id: 'captain_mordak',
        name: 'Captain Mordak',
        status: 'hostile',
        health: 'injured',
        location: 'Bandit Camp',
        disposition: 'hostile',
        relationship_strength: -60,
        first_met: new Date(Date.now() - 172800000).toISOString(),
        last_interaction: new Date(Date.now() - 86400000).toISOString(),
        notes: 'Bandit leader who escaped after you spared his life. Swore vengeance.',
      },
      {
        id: 'elena_nightwhisper',
        name: 'Elena Nightwhisper',
        status: 'neutral',
        health: 'healthy',
        location: 'The Prancing Pony',
        disposition: 'neutral',
        relationship_strength: 20,
        first_met: new Date(Date.now() - 172800000).toISOString(),
        last_interaction: new Date(Date.now() - 172800000).toISOString(),
        notes: 'Mysterious figure who offered the contract. Motives unknown.',
      },
      {
        id: 'merchant_tobias',
        name: 'Merchant Tobias',
        status: 'ally',
        health: 'injured',
        location: 'Millbrook Village',
        disposition: 'friendly',
        relationship_strength: 45,
        first_met: new Date(Date.now() - 259200000).toISOString(),
        last_interaction: new Date(Date.now() - 259200000).toISOString(),
        notes: 'Grateful merchant who owes you a favor for helping him on the road.',
      },
    ],
    worldState: {
      current_location: 'Millbrook Village',
      explored_areas: ['Forest Clearing', 'Mountain Pass', 'Millbrook Village', 'The Prancing Pony', 'Bandit Camp'],
      active_objectives: [
        {
          id: 'obj-1',
          title: 'Investigate the Ancient Ruins',
          description: 'Explore the mysterious ruins that Gareth mentioned, located north of the village.',
          priority: 'high',
          status: 'active',
        },
        {
          id: 'obj-2',
          title: 'Complete the Mysterious Contract',
          description: 'Fulfill the terms of the contract given by Elena Nightwhisper.',
          priority: 'critical',
          status: 'active',
        },
        {
          id: 'obj-3',
          title: 'Deal with Bandit Threat',
          description: 'Address the potential return of Captain Mordak and his bandits.',
          priority: 'medium',
          status: 'active',
        },
      ],
      world_events: [
        {
          id: 'event-1',
          title: 'Bandit Leader Escaped',
          description: 'Captain Mordak and his remaining followers fled the camp after your confrontation.',
          timestamp: new Date(Date.now() - 86400000).toISOString(),
          location: 'Bandit Camp',
          significance: 'major',
        },
        {
          id: 'event-2',
          title: 'Mysterious Contract Accepted',
          description: 'A hooded figure offered you a lucrative but mysterious job in the tavern.',
          timestamp: new Date(Date.now() - 172800000).toISOString(),
          location: 'The Prancing Pony',
          significance: 'critical',
        },
        {
          id: 'event-3',
          title: 'Village Elder\'s Revelation',
          description: 'Gareth shared ancient knowledge about ruins hidden in the northern hills.',
          timestamp: new Date(Date.now() - 259200000).toISOString(),
          location: 'Millbrook Village',
          significance: 'major',
        },
        {
          id: 'event-4',
          title: 'Merchant Rescue',
          description: 'You helped an injured merchant being attacked by wolves on the mountain pass.',
          timestamp: new Date(Date.now() - 345600000).toISOString(),
          location: 'Mountain Pass',
          significance: 'minor',
        },
      ],
      established_lore: {
        ancient_ruins: 'Mysterious structures built by an unknown civilization, said to contain powerful artifacts.',
        bandit_threat: 'Local bandit groups have been increasingly active, threatening trade routes.',
        village_history: 'Millbrook Village has stood for over 200 years, originally founded by retired adventurers.',
        the_contract: 'A mysterious job involving the retrieval of an ancient artifact from dangerous ruins.',
        mountain_pass: 'The main trade route through the mountains, known for both beauty and danger.',
      },
      story_time_elapsed: 240, // 4 hours
    },
    isLoading: false,
    error: null,
  };
} 