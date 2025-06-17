'use client';

import { useState, useEffect } from 'react';
import { 
  X, 
  Book, 
  Calendar, 
  MapPin, 
  Users, 
  Lightbulb, 
  PenTool, 
  Search,
  Filter,
  Plus,
  Clock,
  Star,
  Eye,
  FileText,
  Scroll,
  Map
} from 'lucide-react';

// Types
interface JournalEntry {
  id: string;
  title: string;
  content: string;
  timestamp: string;
  location: string;
  type: 'adventure_log' | 'discovery' | 'personal_note' | 'story_event' | 'character_interaction';
  tags: string[];
  important: boolean;
  character_id: number;
}

interface Discovery {
  id: string;
  name: string;
  description: string;
  type: 'location' | 'person' | 'item' | 'lore' | 'secret';
  discovered_at: string;
  location: string;
  notes?: string;
}

interface StoryTimelineEvent {
  id: string;
  title: string;
  description: string;
  timestamp: string;
  location: string;
  participants: string[];
  consequences?: string[];
  type: 'major_event' | 'combat' | 'discovery' | 'story_progression' | 'character_development';
}

interface JournalSystemProps {
  isOpen: boolean;
  onClose: () => void;
  character: {
    id: number;
    name: string;
    level: number;
  };
}

export default function JournalSystem({ isOpen, onClose, character }: JournalSystemProps) {
  const [activeTab, setActiveTab] = useState<'journal' | 'discoveries' | 'timeline' | 'notes'>('journal');
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState<string>('all');
  const [selectedEntry, setSelectedEntry] = useState<JournalEntry | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [newEntry, setNewEntry] = useState({
    title: '',
    content: '',
    type: 'adventure_log' as const,
    tags: '',
    important: false
  });

  // Mock data - would come from API
  const [journalEntries, setJournalEntries] = useState<JournalEntry[]>([
    {
      id: '1',
      title: 'The Mysterious Ruins',
      content: 'Today we discovered ancient ruins deep in the Whispering Woods. The architecture is unlike anything I\'ve seen before - tall spires reaching toward the canopy, covered in glowing runes that pulse with magical energy. Thorin believes these might be Elvish in origin, but the style is far older than any Elvish settlement we know of.\n\nThe runes seem to respond to touch, glowing brighter when approached. We\'ve decided to set up camp nearby and study them further tomorrow. There\'s definitely something important here.',
      timestamp: '2024-01-15T14:30:00Z',
      location: 'Whispering Woods - Ancient Clearing',
      type: 'discovery',
      tags: ['magic', 'ruins', 'elvish', 'mystery'],
      important: true,
      character_id: 1
    },
    {
      id: '2',
      title: 'Meeting with Captain Thorne',
      content: 'Captain Thorne approached us with urgent news about missing merchants on the road to Millbrook. Three caravans have vanished in the past two weeks, all carrying valuable goods. The last known position was near the old bridge crossing.\n\nStrange tracks were found at the scene - larger than human, but not quite matching any known creature. The Captain suspects bandits, but I have my doubts. This feels like something more sinister.',
      timestamp: '2024-01-14T09:15:00Z',
      location: 'Riverdale Tavern',
      type: 'story_event',
      tags: ['quest', 'merchants', 'mystery', 'captain thorne'],
      important: false,
      character_id: 1
    },
    {
      id: '3',
      title: 'Combat Strategy Notes',
      content: 'After the skirmish with the shadow cultists, I\'ve learned some important lessons about fighting in low-light conditions:\n\n1. Always cast Light on my shield before engaging\n2. Shadow creatures are vulnerable to radiant damage\n3. Keep healing potions easily accessible\n4. Trust Thorin to watch my flanks\n\nThe cultists seemed to be performing some kind of ritual. We interrupted them before completion, but I wonder what they were trying to accomplish.',
      timestamp: '2024-01-13T18:45:00Z',
      location: 'Shadow Grove',
      type: 'personal_note',
      tags: ['combat', 'strategy', 'shadow cultists', 'tactics'],
      important: false,
      character_id: 1
    },
    {
      id: '4',
      title: 'The Talking Fox',
      content: 'Most peculiar encounter today! While gathering herbs near the moonlit pond, a silver fox approached and began speaking in the common tongue. It introduced itself as Silvermoon, a guardian spirit of the forest.\n\nSilvermoon warned us about the "darkness stirring in the deep places" and mentioned that the balance of nature is being threatened. It gave us a small crystal pendant, saying it would "light the way when all seems lost." The fox vanished when dawn broke, leaving only silver pawprints that faded with the morning dew.',
      timestamp: '2024-01-12T23:20:00Z',
      location: 'Moonlit Pond',
      type: 'character_interaction',
      tags: ['fox', 'spirit', 'guardian', 'crystal', 'warning'],
      important: true,
      character_id: 1
    }
  ]);

  const [discoveries, setDiscoveries] = useState<Discovery[]>([
    {
      id: '1',
      name: 'Ancient Elvish Ruins',
      description: 'Mysterious ruins covered in glowing magical runes that respond to touch. Architecture suggests pre-kingdom elvish origin.',
      type: 'location',
      discovered_at: '2024-01-15T14:30:00Z',
      location: 'Whispering Woods',
      notes: 'Runes pulse with blue light. Possible magical properties or hidden mechanisms.'
    },
    {
      id: '2',
      name: 'Silvermoon the Guardian Fox',
      description: 'A silver fox spirit guardian who can speak and seems to protect the forest balance.',
      type: 'person',
      discovered_at: '2024-01-12T23:20:00Z',
      location: 'Moonlit Pond',
      notes: 'Gave us a crystal pendant as protection. Warned about darkness in deep places.'
    },
    {
      id: '3',
      name: 'Crystal of Guidance',
      description: 'A small pendant given by Silvermoon that "lights the way when all seems lost."',
      type: 'item',
      discovered_at: '2024-01-12T23:20:00Z',
      location: 'Moonlit Pond',
      notes: 'Glows faintly when held. Magical properties unknown.'
    },
    {
      id: '4',
      name: 'Shadow Cult Ritual Site',
      description: 'A grove where shadow cultists were performing an unknown ritual before we interrupted them.',
      type: 'location',
      discovered_at: '2024-01-13T18:00:00Z',
      location: 'Shadow Grove',
      notes: 'Ritual circle with strange symbols. Purpose unknown but likely malevolent.'
    }
  ]);

  const [timelineEvents, setTimelineEvents] = useState<StoryTimelineEvent[]>([
    {
      id: '1',
      title: 'The Journey Begins',
      description: 'Our party was formed and set out from Riverdale to investigate the missing merchants.',
      timestamp: '2024-01-10T08:00:00Z',
      location: 'Riverdale',
      participants: ['Elara Brightblade', 'Thorin Ironbeard'],
      type: 'major_event'
    },
    {
      id: '2',
      title: 'Encounter with Silvermoon',
      description: 'Met the guardian fox spirit who warned us about darkness stirring and gave us a crystal pendant.',
      timestamp: '2024-01-12T23:20:00Z',
      location: 'Moonlit Pond',
      participants: ['Elara Brightblade', 'Thorin Ironbeard', 'Silvermoon'],
      consequences: ['Received Crystal of Guidance', 'Learned about forest threat'],
      type: 'story_progression'
    },
    {
      id: '3',
      title: 'Battle with Shadow Cultists',
      description: 'Interrupted a dark ritual and fought shadow cultists in combat.',
      timestamp: '2024-01-13T18:00:00Z',
      location: 'Shadow Grove',
      participants: ['Elara Brightblade', 'Thorin Ironbeard', 'Shadow Cultists'],
      consequences: ['Prevented unknown ritual', 'Discovered cult activity'],
      type: 'combat'
    },
    {
      id: '4',
      title: 'Discovery of Ancient Ruins',
      description: 'Found mysterious elvish ruins with magical properties in the Whispering Woods.',
      timestamp: '2024-01-15T14:30:00Z',
      location: 'Whispering Woods',
      participants: ['Elara Brightblade', 'Thorin Ironbeard'],
      consequences: ['Found magical runes', 'Possible key to larger mystery'],
      type: 'discovery'
    }
  ]);

  const filteredEntries = journalEntries.filter(entry => {
    const matchesSearch = entry.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         entry.content.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         entry.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesFilter = filterType === 'all' || entry.type === filterType;
    return matchesSearch && matchesFilter;
  });

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'adventure_log': return <Book className="w-4 h-4 text-blue-400" />;
      case 'discovery': return <Lightbulb className="w-4 h-4 text-yellow-400" />;
      case 'personal_note': return <PenTool className="w-4 h-4 text-green-400" />;
      case 'story_event': return <FileText className="w-4 h-4 text-purple-400" />;
      case 'character_interaction': return <Users className="w-4 h-4 text-pink-400" />;
      default: return <Scroll className="w-4 h-4 text-gray-400" />;
    }
  };

  const getDiscoveryIcon = (type: string) => {
    switch (type) {
      case 'location': return <MapPin className="w-4 h-4 text-red-400" />;
      case 'person': return <Users className="w-4 h-4 text-blue-400" />;
      case 'item': return <Star className="w-4 h-4 text-yellow-400" />;
      case 'lore': return <Book className="w-4 h-4 text-purple-400" />;
      case 'secret': return <Eye className="w-4 h-4 text-green-400" />;
      default: return <Lightbulb className="w-4 h-4 text-gray-400" />;
    }
  };

  const handleCreateEntry = () => {
    const entry: JournalEntry = {
      id: Date.now().toString(),
      title: newEntry.title,
      content: newEntry.content,
      timestamp: new Date().toISOString(),
      location: 'Current Location', // Would get from game state
      type: newEntry.type,
      tags: newEntry.tags.split(',').map(tag => tag.trim()).filter(tag => tag.length > 0),
      important: newEntry.important,
      character_id: character.id
    };

    setJournalEntries([entry, ...journalEntries]);
    setNewEntry({ title: '', content: '', type: 'adventure_log', tags: '', important: false });
    setIsCreating(false);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-900 rounded-lg border border-gray-700 w-full max-w-7xl h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-700">
          <div className="flex items-center space-x-3">
            <Book className="w-6 h-6 text-blue-400" />
            <h2 className="text-2xl font-bold text-white">Adventure Journal</h2>
            <span className="text-sm text-gray-400">- {character.name}</span>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-gray-700">
          {[
            { key: 'journal', label: 'Journal Entries', icon: Book },
            { key: 'discoveries', label: 'Discoveries', icon: Lightbulb },
            { key: 'timeline', label: 'Story Timeline', icon: Calendar },
            { key: 'notes', label: 'Quick Notes', icon: PenTool }
          ].map(tab => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key as any)}
                className={`flex items-center space-x-2 px-6 py-3 text-sm font-medium transition-colors border-b-2 ${
                  activeTab === tab.key
                    ? 'text-blue-400 border-blue-400'
                    : 'text-gray-400 border-transparent hover:text-gray-300'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        <div className="flex flex-1 overflow-hidden">
          {/* Content Area */}
          {activeTab === 'journal' && (
            <>
              {/* Sidebar */}
              <div className="w-1/2 border-r border-gray-700 flex flex-col">
                {/* Search and Filter */}
                <div className="p-4 border-b border-gray-700">
                  <div className="flex space-x-2 mb-3">
                    <div className="flex-1 relative">
                      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                      <input
                        type="text"
                        placeholder="Search entries..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="w-full pl-10 pr-4 py-2 bg-gray-800 border border-gray-600 rounded text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                      />
                    </div>
                    <button
                      onClick={() => setIsCreating(true)}
                      className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded transition-colors flex items-center space-x-2"
                    >
                      <Plus className="w-4 h-4" />
                      <span>New</span>
                    </button>
                  </div>
                  
                  <select
                    value={filterType}
                    onChange={(e) => setFilterType(e.target.value)}
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded text-white focus:outline-none focus:border-blue-500"
                  >
                    <option value="all">All Types</option>
                    <option value="adventure_log">Adventure Log</option>
                    <option value="discovery">Discoveries</option>
                    <option value="personal_note">Personal Notes</option>
                    <option value="story_event">Story Events</option>
                    <option value="character_interaction">Character Interactions</option>
                  </select>
                </div>

                {/* Entry List */}
                <div className="flex-1 overflow-y-auto">
                  {isCreating && (
                    <div className="p-4 bg-gray-800 border-b border-gray-600">
                      <div className="space-y-3">
                        <input
                          type="text"
                          placeholder="Entry title..."
                          value={newEntry.title}
                          onChange={(e) => setNewEntry({ ...newEntry, title: e.target.value })}
                          className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                        />
                        <select
                          value={newEntry.type}
                          onChange={(e) => setNewEntry({ ...newEntry, type: e.target.value as any })}
                          className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:outline-none focus:border-blue-500"
                        >
                          <option value="adventure_log">Adventure Log</option>
                          <option value="discovery">Discovery</option>
                          <option value="personal_note">Personal Note</option>
                          <option value="story_event">Story Event</option>
                          <option value="character_interaction">Character Interaction</option>
                        </select>
                        <div className="flex space-x-2">
                          <button
                            onClick={handleCreateEntry}
                            disabled={!newEntry.title}
                            className="flex-1 px-3 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white rounded transition-colors"
                          >
                            Create
                          </button>
                          <button
                            onClick={() => setIsCreating(false)}
                            className="flex-1 px-3 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded transition-colors"
                          >
                            Cancel
                          </button>
                        </div>
                      </div>
                    </div>
                  )}

                  {filteredEntries.map(entry => (
                    <div
                      key={entry.id}
                      onClick={() => setSelectedEntry(entry)}
                      className={`p-4 border-b border-gray-700 cursor-pointer transition-colors hover:bg-gray-800 ${
                        selectedEntry?.id === entry.id ? 'bg-gray-800' : ''
                      }`}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center space-x-2">
                          {getTypeIcon(entry.type)}
                          <h3 className="font-semibold text-white">{entry.title}</h3>
                          {entry.important && <Star className="w-4 h-4 text-yellow-400 fill-current" />}
                        </div>
                        <span className="text-xs text-gray-400">
                          {new Date(entry.timestamp).toLocaleDateString()}
                        </span>
                      </div>
                      
                      <p className="text-sm text-gray-400 mb-2 line-clamp-2">{entry.content}</p>
                      
                      <div className="flex items-center justify-between text-xs text-gray-500">
                        <div className="flex items-center space-x-1">
                          <MapPin className="w-3 h-3" />
                          <span>{entry.location}</span>
                        </div>
                        {entry.tags.length > 0 && (
                          <div className="flex space-x-1">
                            {entry.tags.slice(0, 2).map(tag => (
                              <span key={tag} className="px-2 py-1 bg-gray-700 rounded text-xs">
                                {tag}
                              </span>
                            ))}
                            {entry.tags.length > 2 && (
                              <span className="text-gray-400">+{entry.tags.length - 2}</span>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Entry Details */}
              <div className="w-1/2 flex flex-col">
                {selectedEntry ? (
                  <>
                    <div className="p-6 border-b border-gray-700">
                      <div className="flex items-start justify-between mb-4">
                        <div>
                          <div className="flex items-center space-x-2 mb-2">
                            {getTypeIcon(selectedEntry.type)}
                            <h3 className="text-xl font-bold text-white">{selectedEntry.title}</h3>
                            {selectedEntry.important && <Star className="w-5 h-5 text-yellow-400 fill-current" />}
                          </div>
                          <div className="flex items-center space-x-4 text-sm text-gray-400">
                            <div className="flex items-center space-x-1">
                              <Clock className="w-4 h-4" />
                              <span>{new Date(selectedEntry.timestamp).toLocaleString()}</span>
                            </div>
                            <div className="flex items-center space-x-1">
                              <MapPin className="w-4 h-4" />
                              <span>{selectedEntry.location}</span>
                            </div>
                          </div>
                        </div>
                      </div>
                      
                      <div className="prose prose-invert max-w-none">
                        <div className="text-gray-300 whitespace-pre-wrap">{selectedEntry.content}</div>
                      </div>

                      {selectedEntry.tags.length > 0 && (
                        <div className="mt-4">
                          <h4 className="text-sm font-semibold text-gray-400 mb-2">Tags</h4>
                          <div className="flex flex-wrap gap-2">
                            {selectedEntry.tags.map(tag => (
                              <span key={tag} className="px-3 py-1 bg-gray-700 rounded-full text-sm text-gray-300">
                                {tag}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </>
                ) : (
                  <div className="flex-1 flex items-center justify-center text-gray-400">
                    <div className="text-center">
                      <Book className="w-12 h-12 mx-auto mb-4 opacity-50" />
                      <p>Select an entry to view details</p>
                    </div>
                  </div>
                )}
              </div>
            </>
          )}

          {/* Other tabs content would go here */}
          {activeTab === 'discoveries' && (
            <div className="flex-1 p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {discoveries.map(discovery => (
                  <div key={discovery.id} className="bg-gray-800 rounded-lg border border-gray-600 p-4">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center space-x-2">
                        {getDiscoveryIcon(discovery.type)}
                        <h3 className="font-semibold text-white">{discovery.name}</h3>
                      </div>
                      <span className="text-xs text-gray-400 capitalize">{discovery.type}</span>
                    </div>
                    
                    <p className="text-sm text-gray-300 mb-3">{discovery.description}</p>
                    
                    <div className="space-y-2 text-xs text-gray-400">
                      <div className="flex items-center space-x-1">
                        <MapPin className="w-3 h-3" />
                        <span>{discovery.location}</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <Clock className="w-3 h-3" />
                        <span>{new Date(discovery.discovered_at).toLocaleDateString()}</span>
                      </div>
                    </div>
                    
                    {discovery.notes && (
                      <div className="mt-3 pt-3 border-t border-gray-700">
                        <p className="text-xs text-gray-400">{discovery.notes}</p>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'timeline' && (
            <div className="flex-1 p-6">
              <div className="space-y-4">
                {timelineEvents.map((event, index) => (
                  <div key={event.id} className="flex items-start space-x-4">
                    <div className="flex flex-col items-center">
                      <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold text-sm">
                        {index + 1}
                      </div>
                      {index < timelineEvents.length - 1 && (
                        <div className="w-px h-20 bg-gray-600 mt-2"></div>
                      )}
                    </div>
                    
                    <div className="flex-1 bg-gray-800 rounded-lg border border-gray-600 p-4">
                      <div className="flex items-start justify-between mb-2">
                        <h3 className="font-semibold text-white">{event.title}</h3>
                        <span className="text-xs text-gray-400">
                          {new Date(event.timestamp).toLocaleDateString()}
                        </span>
                      </div>
                      
                      <p className="text-sm text-gray-300 mb-3">{event.description}</p>
                      
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                        <div>
                          <span className="text-gray-400">Location:</span>
                          <span className="text-white ml-2">{event.location}</span>
                        </div>
                        <div>
                          <span className="text-gray-400">Type:</span>
                          <span className="text-white ml-2 capitalize">{event.type.replace('_', ' ')}</span>
                        </div>
                      </div>
                      
                      {event.participants.length > 0 && (
                        <div className="mt-3">
                          <span className="text-xs text-gray-400">Participants:</span>
                          <div className="flex flex-wrap gap-1 mt-1">
                            {event.participants.map(participant => (
                              <span key={participant} className="px-2 py-1 bg-gray-700 rounded text-xs text-gray-300">
                                {participant}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                      
                      {event.consequences && event.consequences.length > 0 && (
                        <div className="mt-3">
                          <span className="text-xs text-gray-400">Consequences:</span>
                          <ul className="mt-1 space-y-1">
                            {event.consequences.map((consequence, idx) => (
                              <li key={idx} className="text-xs text-gray-300 flex items-start">
                                <span className="w-1 h-1 bg-gray-500 rounded-full mt-2 mr-2 flex-shrink-0"></span>
                                {consequence}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'notes' && (
            <div className="flex-1 p-6">
              <div className="text-center text-gray-400">
                <PenTool className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>Quick notes feature coming soon...</p>
                <p className="text-sm mt-2">This will allow for quick jotting down of ideas, reminders, and temporary notes.</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
} 