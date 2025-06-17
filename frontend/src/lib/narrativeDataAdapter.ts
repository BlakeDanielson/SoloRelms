// Data adapter to transform backend story data to frontend narrative context format

interface BackendStoryArc {
  id: number;
  title?: string;
  current_stage: string;
  major_decisions?: Array<{
    decision: string;
    description: string;
    timestamp: string;
    stage: string;
    consequences: string[];
  }>;
  npc_status?: Record<string, {
    status: string;
    health: string;
    location: string;
    disposition: string;
  }>;
  combat_outcomes?: Array<any>;
  story_completed: boolean;
  created_at: string;
  started_at?: string;
  completed_at?: string;
}

interface BackendWorldState {
  current_location: string;
  explored_areas?: Array<{
    name: string;
    first_visited: string;
    description: string;
    notable_features?: string[];
    npcs_encountered?: string[];
  }>;
  world_events?: Array<{
    event: string;
    location: string;
    description: string;
    timestamp: string;
    player_involved: boolean;
    consequences?: string[];
  }>;
  active_objectives?: Array<{
    id: string;
    title: string;
    description: string;
    stage: string;
    priority: string;
    status: string;
  }>;
  completed_objectives?: Array<any>;
  established_lore?: Record<string, string>;
  story_time_elapsed: number;
}

// Frontend interfaces
export interface MajorDecision {
  id: string;
  decision: string;
  description: string;
  timestamp: string;
  stage: string;
  consequences: string[];
  impact_score?: number;
}

export interface NPCStatus extends Record<string, unknown> {
  id: string;
  name: string;
  status: 'ally' | 'neutral' | 'hostile' | 'dead' | 'unknown';
  health: 'healthy' | 'injured' | 'dying' | 'dead' | 'unknown';
  location: string;
  disposition: 'friendly' | 'neutral' | 'unfriendly' | 'hostile' | 'unknown';
  relationship_strength: number; // -100 to 100
  first_met: string;
  last_interaction: string;
  notes?: string;
}

export interface WorldState {
  current_location: string;
  explored_areas: string[];
  active_objectives: Array<{
    id: string;
    title: string;
    description: string;
    priority: 'low' | 'medium' | 'high' | 'critical';
    status: 'active' | 'completed' | 'failed';
  }>;
  world_events: Array<{
    id: string;
    title: string;
    description: string;
    timestamp: string;
    location: string;
    significance: 'minor' | 'major' | 'critical';
  }>;
  established_lore: Record<string, string>;
  story_time_elapsed: number;
}

/**
 * Transforms backend major decisions to frontend format
 */
export function adaptMajorDecisions(storyArc: BackendStoryArc): MajorDecision[] {
  if (!storyArc.major_decisions) return [];

  return storyArc.major_decisions.map((decision, index) => ({
    id: `decision-${storyArc.id}-${index}`,
    decision: decision.decision,
    description: decision.description,
    timestamp: decision.timestamp,
    stage: decision.stage,
    consequences: decision.consequences || [],
    impact_score: decision.consequences?.length || 0, // Simple impact scoring
  }));
}

/**
 * Transforms backend NPC status to frontend format
 */
export function adaptNPCStatuses(storyArc: BackendStoryArc): NPCStatus[] {
  if (!storyArc.npc_status) return [];

  return Object.entries(storyArc.npc_status).map(([npcId, npcData]) => ({
    id: npcId,
    name: npcId.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
    status: normalizeStatus(npcData.status),
    health: normalizeHealth(npcData.health),
    location: npcData.location || 'Unknown',
    disposition: normalizeDisposition(npcData.disposition),
    relationship_strength: calculateRelationshipStrength(npcData),
    first_met: storyArc.started_at || storyArc.created_at,
    last_interaction: storyArc.completed_at || new Date().toISOString(),
    notes: `Status: ${npcData.status}, Health: ${npcData.health}`,
  }));
}

/**
 * Transforms backend world state to frontend format
 */
export function adaptWorldState(worldState: BackendWorldState): WorldState {
  return {
    current_location: worldState.current_location,
    explored_areas: worldState.explored_areas?.map(area => area.name) || [],
    active_objectives: worldState.active_objectives?.map(obj => ({
      id: obj.id,
      title: obj.title,
      description: obj.description,
      priority: normalizePriority(obj.priority),
      status: normalizeObjectiveStatus(obj.status),
    })) || [],
    world_events: worldState.world_events?.map((event, index) => ({
      id: `event-${index}`,
      title: event.event.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
      description: event.description,
      timestamp: event.timestamp,
      location: event.location,
      significance: event.player_involved ? 'major' : 'minor' as 'minor' | 'major' | 'critical',
    })) || [],
    established_lore: worldState.established_lore || {},
    story_time_elapsed: worldState.story_time_elapsed || 0,
  };
}

// Helper functions to normalize backend data
function normalizeStatus(status: string): 'ally' | 'neutral' | 'hostile' | 'dead' | 'unknown' {
  const normalized = status.toLowerCase();
  if (['ally', 'friend', 'friendly'].includes(normalized)) return 'ally';
  if (['enemy', 'hostile', 'antagonist'].includes(normalized)) return 'hostile';
  if (['dead', 'deceased', 'killed'].includes(normalized)) return 'dead';
  if (['neutral', 'indifferent'].includes(normalized)) return 'neutral';
  return 'unknown';
}

function normalizeHealth(health: string): 'healthy' | 'injured' | 'dying' | 'dead' | 'unknown' {
  const normalized = health.toLowerCase();
  if (['healthy', 'fine', 'good', 'well'].includes(normalized)) return 'healthy';
  if (['injured', 'hurt', 'wounded', 'damaged'].includes(normalized)) return 'injured';
  if (['dying', 'critical', 'near death'].includes(normalized)) return 'dying';
  if (['dead', 'deceased', 'killed'].includes(normalized)) return 'dead';
  return 'unknown';
}

function normalizeDisposition(disposition: string): 'friendly' | 'neutral' | 'unfriendly' | 'hostile' | 'unknown' {
  const normalized = disposition.toLowerCase();
  if (['friendly', 'kind', 'grateful', 'pleased'].includes(normalized)) return 'friendly';
  if (['hostile', 'angry', 'vengeful', 'aggressive'].includes(normalized)) return 'hostile';
  if (['unfriendly', 'annoyed', 'displeased', 'cold'].includes(normalized)) return 'unfriendly';
  if (['neutral', 'indifferent', 'calm'].includes(normalized)) return 'neutral';
  return 'unknown';
}

function normalizePriority(priority: string): 'low' | 'medium' | 'high' | 'critical' {
  const normalized = priority.toLowerCase();
  if (['critical', 'urgent', 'main'].includes(normalized)) return 'critical';
  if (['high', 'important'].includes(normalized)) return 'high';
  if (['low', 'minor', 'optional'].includes(normalized)) return 'low';
  return 'medium';
}

function normalizeObjectiveStatus(status: string): 'active' | 'completed' | 'failed' {
  const normalized = status.toLowerCase();
  if (['completed', 'done', 'finished', 'success'].includes(normalized)) return 'completed';
  if (['failed', 'failure', 'abandoned'].includes(normalized)) return 'failed';
  return 'active';
}

function calculateRelationshipStrength(npcData: any): number {
  // Simple relationship calculation based on status and disposition
  let strength = 0;
  
  switch (npcData.disposition?.toLowerCase()) {
    case 'grateful':
    case 'friendly':
    case 'pleased':
      strength += 30;
      break;
    case 'hostile':
    case 'vengeful':
    case 'angry':
      strength -= 50;
      break;
    case 'neutral':
    case 'indifferent':
      strength += 0;
      break;
    default:
      strength += 10;
  }

  switch (npcData.status?.toLowerCase()) {
    case 'ally':
    case 'friend':
      strength += 50;
      break;
    case 'hostile':
    case 'enemy':
      strength -= 70;
      break;
    default:
      strength += 0;
  }

  // Clamp between -100 and 100
  return Math.max(-100, Math.min(100, strength));
}

/**
 * Main adapter function to transform all story data
 */
export function adaptStoryData(storyArc: BackendStoryArc, worldState: BackendWorldState) {
  return {
    majorDecisions: adaptMajorDecisions(storyArc),
    npcStatuses: adaptNPCStatuses(storyArc),
    worldState: adaptWorldState(worldState),
  };
} 