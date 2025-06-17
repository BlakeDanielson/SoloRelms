// Core game types for the D&D RPG system

export interface Character {
  id: number
  name: string
  class: string
  race: string
  level: number
  current_hp: number
  max_hp: number
  armor_class: number
  location: string
  avatar_url?: string
  status_effects: string[]
  inventory: InventoryItem[]
  stats?: CharacterStats
  spells?: Spell[]
  equipment?: Equipment
}

export interface CharacterStats {
  strength: number
  dexterity: number
  constitution: number
  intelligence: number
  wisdom: number
  charisma: number
  proficiency_bonus: number
  skills: Record<string, number>
  saving_throws: Record<string, number>
}

export interface InventoryItem {
  id: number
  name: string
  description: string
  quantity: number
  type: 'weapon' | 'armor' | 'helmet' | 'shield' | 'consumable' | 'treasure' | 'misc' | 'gloves' | 'gauntlets' | 'belt' | 'pants' | 'leggings' | 'boots' | 'shoes' | 'amulet' | 'necklace' | 'cloak' | 'pauldrons' | 'robe' | 'hat'
  rarity?: 'common' | 'uncommon' | 'rare' | 'epic' | 'legendary'
  value?: number
  weight?: number
  properties?: string[]
}

export interface Spell {
  id: number
  name: string
  level: number
  school: string
  casting_time: string
  range: string
  components: string[]
  duration: string
  description: string
  prepared?: boolean
  spell_slots_used?: number
}

export interface Equipment {
  weapon?: InventoryItem
  armor?: InventoryItem
  shield?: InventoryItem
  accessories: InventoryItem[]
}

export interface GameState {
  current_scene: string
  scene_image_url?: string
  scene_type?: 'combat' | 'exploration' | 'dialogue' | 'story_narration'
  objectives: string[]
  recent_events: string[]
  current_location: string
  party_members: Character[]
  game_id?: string
  session_id?: string
  dm_notes?: string[]
  world_state?: WorldState
}

export interface WorldState {
  time_of_day: 'dawn' | 'morning' | 'noon' | 'afternoon' | 'evening' | 'night' | 'midnight'
  weather: string
  season: 'spring' | 'summer' | 'fall' | 'winter'
  important_npcs: NPC[]
  active_quests: Quest[]
  world_events: WorldEvent[]
}

export interface NPC {
  id: number
  name: string
  race: string
  class?: string
  role: string
  location: string
  description: string
  disposition: 'hostile' | 'unfriendly' | 'neutral' | 'friendly' | 'helpful'
  relationship_with_party?: string
}

export interface Quest {
  id: number
  title: string
  description: string
  status: 'available' | 'active' | 'completed' | 'failed'
  objectives: QuestObjective[]
  rewards?: string[]
  giver?: string
}

export interface QuestObjective {
  id: number
  description: string
  completed: boolean
  optional: boolean
}

export interface WorldEvent {
  id: number
  title: string
  description: string
  impact: string
  timestamp: Date
}

export interface ChatMessage {
  id: string
  type: 'dm_narration' | 'player_action' | 'player_speech' | 'player_thought' | 'dice_roll' | 'system'
  content: string
  timestamp: Date
  metadata?: ChatMessageMetadata
  character_id?: number
  character_name?: string
}

export interface ChatMessageMetadata {
  // For dice rolls
  diceType?: string
  rolls?: number[]
  modifier?: number
  total?: number
  label?: string
  critical?: boolean
  
  // For actions/scenes
  scene_change?: boolean
  character_update?: boolean
  game_state_update?: boolean
  
  // For system messages
  system_type?: 'connection' | 'error' | 'notification' | 'command'
  
  // General metadata
  [key: string]: any
}

export interface DiceRoll {
  diceType: string
  count: number
  modifier: number
  rolls: number[]
  total: number
  label?: string
  critical?: boolean
  timestamp: Date
}

export interface Scene {
  id: string
  name: string
  description: string
  image_url?: string
  type: 'combat' | 'exploration' | 'dialogue' | 'story_narration'
  location: string
  characters_present: number[]
  props?: SceneProp[]
  environmental_effects?: string[]
}

export interface SceneProp {
  id: number
  name: string
  description: string
  interactive: boolean
  position?: { x: number; y: number }
  state?: 'normal' | 'damaged' | 'destroyed' | 'hidden'
}

// Action types for user input
export type PlayerActionType = 'action' | 'speech' | 'thought'

export interface PlayerAction {
  type: PlayerActionType
  content: string
  character_id: number
  timestamp: Date
  metadata?: {
    dice_rolls?: DiceRoll[]
    target?: string
    item_used?: number
    spell_cast?: number
  }
}

// WebSocket message types
export type WebSocketEventType = 
  | 'chat_message' 
  | 'game_state_update' 
  | 'character_update' 
  | 'scene_change' 
  | 'system_notification'
  | 'dice_roll'
  | 'connection_status'

export interface WebSocketEvent {
  type: WebSocketEventType
  data: any
  timestamp: string
  session_id?: string
}

// Connection status
export type ConnectionStatus = 'connecting' | 'connected' | 'disconnected' | 'error' | 'reconnecting'

export interface ConnectionState {
  status: ConnectionStatus
  attempts?: number
  lastError?: string
  latency?: number
}

// API Response wrapper
export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  error?: string
  message?: string
  timestamp?: string
}

// Game session management
export interface GameSession {
  id: string
  name: string
  dm_id: string
  player_ids: number[]
  characters: Character[]
  current_scene_id: string
  game_state: GameState
  created_at: Date
  last_activity: Date
  settings: GameSettings
}

export interface GameSettings {
  max_players: number
  dice_rolling_mode: 'manual' | 'automatic' | 'mixed'
  ai_dm_personality: string
  difficulty_level: 'easy' | 'normal' | 'hard' | 'deadly'
  house_rules: string[]
  content_rating: 'family' | 'teen' | 'mature'
}

// Input validation types
export interface InputValidation {
  isValid: boolean
  errors: string[]
  warnings: string[]
  suggestions?: string[]
}

// Utility types
export type SceneType = GameState['scene_type']
export type CharacterClass = string
export type CharacterRace = string
export type ItemType = InventoryItem['type']
export type ItemRarity = InventoryItem['rarity']
export type MessageType = ChatMessage['type']

export interface StatusEffect {
  id: string
  name: string
  icon: string
  duration: number
  type: 'buff' | 'debuff' | 'neutral'
  description: string
}

export interface CombatEntity {
  id: string
  name: string
  type: 'player' | 'ally' | 'enemy'
  initiative: number
  currentHp: number
  maxHp: number
  currentMp?: number
  maxMp?: number
  armorClass: number
  statusEffects: StatusEffect[]
  avatar?: string
  isActive: boolean
}

export interface CombatAction {
  id: string
  name: string
  icon: React.ComponentType<any>
  description: string
  actionType: 'attack' | 'defend' | 'spell' | 'item' | 'move'
  disabled?: boolean
  cooldown?: number
} 