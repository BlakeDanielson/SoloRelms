'use client';

import { useState, useEffect } from 'react';
import { 
  X, 
  Search, 
  Filter, 
  Package, 
  Sword, 
  Shield, 
  Crown,
  Shirt,
  Zap,
  Star,
  Trash2,
  Eye,
  ArrowUpRight,
  ArrowDownLeft,
  Info,
  Plus,
  Minus,
  MoreVertical,
  Settings,
  User,
  Target,
  Heart,
  Footprints,
  Hand
} from 'lucide-react';

// Types
interface InventoryItem {
  id: number;
  name: string;
  description: string;
  quantity: number;
  type: string;
  rarity: 'common' | 'uncommon' | 'rare' | 'epic' | 'legendary';
  weight?: number;
  value?: number;
  equipped?: boolean;
  slot?: string;
  stats?: {
    armor_class?: number;
    damage?: string;
    healing?: string;
    bonus?: number;
  };
}

interface EquipmentSlot {
  id: string;
  name: string;
  icon: any;
  item?: InventoryItem;
  allowedTypes: string[];
}

interface Character {
  id: number;
  name: string;
  race: string;
  character_class: string;
  level: number;
  current_hp: number;
  max_hp: number;
  armor_class: number;
  inventory: InventoryItem[];
}

interface EnhancedInventoryPanelProps {
  character: Character;
  inventory: InventoryItem[];
  isOpen: boolean;
  onClose: () => void;
  onUseItem: (item: InventoryItem) => void;
  onEquipItem: (item: InventoryItem, slot: string) => void;
  onUnequipItem: (slot: string) => void;
  onDiscardItem: (item: InventoryItem) => void;
  onMoveItem: (fromIndex: number, toIndex: number) => void;
}

// Equipment slot configuration
const EQUIPMENT_SLOTS: EquipmentSlot[] = [
  { id: 'helmet', name: 'Helmet', icon: Crown, allowedTypes: ['helmet', 'hat'], item: undefined },
  { id: 'armor', name: 'Armor', icon: Shirt, allowedTypes: ['armor', 'robe'], item: undefined },
  { id: 'gloves', name: 'Gloves', icon: Hand, allowedTypes: ['gloves', 'gauntlets'], item: undefined },
  { id: 'boots', name: 'Boots', icon: Footprints, allowedTypes: ['boots', 'shoes'], item: undefined },
  { id: 'main_hand', name: 'Main Hand', icon: Sword, allowedTypes: ['weapon', 'sword', 'dagger', 'staff'], item: undefined },
  { id: 'off_hand', name: 'Off Hand', icon: Shield, allowedTypes: ['shield', 'weapon', 'dagger'], item: undefined },
  { id: 'ring1', name: 'Ring 1', icon: Target, allowedTypes: ['ring'], item: undefined },
  { id: 'ring2', name: 'Ring 2', icon: Target, allowedTypes: ['ring'], item: undefined },
  { id: 'necklace', name: 'Necklace', icon: Star, allowedTypes: ['necklace', 'amulet'], item: undefined },
  { id: 'cloak', name: 'Cloak', icon: User, allowedTypes: ['cloak', 'cape'], item: undefined }
];

// Item categories for filtering
const ITEM_CATEGORIES = [
  { id: 'all', name: 'All Items', icon: Package },
  { id: 'weapon', name: 'Weapons', icon: Sword },
  { id: 'armor', name: 'Armor', icon: Shield },
  { id: 'consumable', name: 'Consumables', icon: Heart },
  { id: 'misc', name: 'Miscellaneous', icon: Star },
  { id: 'treasure', name: 'Treasure', icon: Zap }
];

export default function EnhancedInventoryPanel({
  character,
  inventory,
  isOpen,
  onClose,
  onUseItem,
  onEquipItem,
  onUnequipItem,
  onDiscardItem,
  onMoveItem
}: EnhancedInventoryPanelProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedItem, setSelectedItem] = useState<InventoryItem | null>(null);
  const [showItemDetails, setShowItemDetails] = useState(false);
  const [equipmentSlots, setEquipmentSlots] = useState<EquipmentSlot[]>(EQUIPMENT_SLOTS);
  const [showEquipment, setShowEquipment] = useState(true);
  const [sortBy, setSortBy] = useState<'name' | 'type' | 'rarity' | 'value'>('name');

  // Initialize equipment slots with equipped items
  useEffect(() => {
    const updatedSlots = [...EQUIPMENT_SLOTS];
    inventory.forEach(item => {
      if (item.equipped && item.slot) {
        const slotIndex = updatedSlots.findIndex(slot => slot.id === item.slot);
        if (slotIndex !== -1) {
          updatedSlots[slotIndex] = { ...updatedSlots[slotIndex], item };
        }
      }
    });
    setEquipmentSlots(updatedSlots);
  }, [inventory]);

  // Filter and sort inventory
  const filteredInventory = inventory
    .filter(item => {
      // Don't show equipped items in inventory grid
      if (item.equipped) return false;
      
      // Category filter
      if (selectedCategory !== 'all' && item.type !== selectedCategory) return false;
      
      // Search filter
      if (searchTerm && !item.name.toLowerCase().includes(searchTerm.toLowerCase())) return false;
      
      return true;
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.name.localeCompare(b.name);
        case 'type':
          return a.type.localeCompare(b.type);
        case 'rarity':
          const rarityOrder = { common: 1, uncommon: 2, rare: 3, epic: 4, legendary: 5 };
          return rarityOrder[b.rarity] - rarityOrder[a.rarity];
        case 'value':
          return (b.value || 0) - (a.value || 0);
        default:
          return 0;
      }
    });

  // Get rarity color
  const getRarityColor = (rarity: string) => {
    switch (rarity) {
      case 'common': return 'text-gray-300 border-gray-600';
      case 'uncommon': return 'text-green-300 border-green-600';
      case 'rare': return 'text-blue-300 border-blue-600';
      case 'epic': return 'text-purple-300 border-purple-600';
      case 'legendary': return 'text-orange-300 border-orange-600';
      default: return 'text-gray-300 border-gray-600';
    }
  };

  // Handle equipping an item
  const handleEquipItem = (item: InventoryItem) => {
    const availableSlots = equipmentSlots.filter(slot => 
      slot.allowedTypes.includes(item.type) && !slot.item
    );
    
    if (availableSlots.length > 0) {
      onEquipItem(item, availableSlots[0].id);
    }
  };

  // Handle unequipping an item
  const handleUnequipItem = (slot: string) => {
    onUnequipItem(slot);
  };

  // Calculate total inventory value
  const totalValue = inventory.reduce((sum, item) => sum + (item.value || 0) * item.quantity, 0);
  const totalWeight = inventory.reduce((sum, item) => sum + (item.weight || 0) * item.quantity, 0);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-gray-900/95 backdrop-blur-sm border border-purple-500/30 rounded-lg w-full max-w-7xl h-[90vh] flex flex-col">
        
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-700/50">
          <div className="flex items-center">
            <Package className="w-6 h-6 text-purple-400 mr-3" />
            <div>
              <h2 className="text-2xl font-bold text-white">{character.name}'s Inventory</h2>
              <p className="text-sm text-gray-400">
                {inventory.length} items • {totalValue}gp • {totalWeight.toFixed(1)}lbs
              </p>
            </div>
          </div>
          
          <div className="flex items-center gap-4">
            <button
              onClick={() => setShowEquipment(!showEquipment)}
              className={`px-4 py-2 rounded-md transition-colors ${
                showEquipment ? 'bg-purple-600 text-white' : 'bg-gray-700 text-gray-300'
              }`}
            >
              Equipment
            </button>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-white transition-colors"
            >
              <X className="w-6 h-6" />
            </button>
          </div>
        </div>

        <div className="flex-1 flex overflow-hidden">
          
          {/* Equipment Panel */}
          {showEquipment && (
            <div className="w-80 border-r border-gray-700/50 p-6 overflow-y-auto">
              <h3 className="text-lg font-bold text-white mb-4">Equipment Slots</h3>
              
              {/* Character Stats Summary */}
              <div className="bg-gray-800/50 rounded-lg p-4 mb-6">
                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div className="flex items-center">
                    <Shield className="w-4 h-4 text-blue-400 mr-2" />
                    <span className="text-gray-300">AC: {character.armor_class}</span>
                  </div>
                  <div className="flex items-center">
                    <Heart className="w-4 h-4 text-red-400 mr-2" />
                    <span className="text-gray-300">HP: {character.current_hp}/{character.max_hp}</span>
                  </div>
                </div>
              </div>

              {/* Equipment Slots Grid */}
              <div className="grid grid-cols-2 gap-3">
                {equipmentSlots.map((slot) => {
                  const IconComponent = slot.icon;
                  return (
                    <div
                      key={slot.id}
                      className={`relative border-2 border-dashed rounded-lg p-4 transition-all ${
                        slot.item 
                          ? `${getRarityColor(slot.item.rarity)} bg-gray-800/30` 
                          : 'border-gray-600 hover:border-gray-500'
                      }`}
                    >
                      <div className="text-center">
                        <IconComponent className="w-6 h-6 mx-auto mb-2 text-gray-400" />
                        <div className="text-xs text-gray-400 mb-2">{slot.name}</div>
                        
                        {slot.item ? (
                          <div>
                            <div className={`text-sm font-medium ${getRarityColor(slot.item.rarity).split(' ')[0]}`}>
                              {slot.item.name}
                            </div>
                            <button
                              onClick={() => handleUnequipItem(slot.id)}
                              className="mt-2 text-xs bg-red-600/20 hover:bg-red-600/30 text-red-300 px-2 py-1 rounded transition-colors"
                            >
                              Unequip
                            </button>
                          </div>
                        ) : (
                          <div className="text-xs text-gray-500">Empty</div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Main Inventory Panel */}
          <div className="flex-1 flex flex-col">
            
            {/* Inventory Controls */}
            <div className="p-6 border-b border-gray-700/50">
              <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
                {/* Search */}
                <div className="relative flex-1 max-w-md">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                  <input
                    type="text"
                    placeholder="Search items..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 bg-gray-800/50 border border-gray-600/50 rounded-md text-white placeholder-gray-400 focus:outline-none focus:border-purple-400"
                  />
                </div>

                {/* Sort */}
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value as any)}
                  className="bg-gray-800/50 border border-gray-600/50 rounded-md text-white px-3 py-2 focus:outline-none focus:border-purple-400"
                >
                  <option value="name">Sort by Name</option>
                  <option value="type">Sort by Type</option>
                  <option value="rarity">Sort by Rarity</option>
                  <option value="value">Sort by Value</option>
                </select>
              </div>

              {/* Category Filters */}
              <div className="mt-4 flex flex-wrap gap-2">
                {ITEM_CATEGORIES.map((category) => {
                  const IconComponent = category.icon;
                  return (
                    <button
                      key={category.id}
                      onClick={() => setSelectedCategory(category.id)}
                      className={`flex items-center px-3 py-2 rounded-md text-sm transition-colors ${
                        selectedCategory === category.id
                          ? 'bg-purple-600 text-white'
                          : 'bg-gray-700/50 text-gray-300 hover:bg-gray-600/50'
                      }`}
                    >
                      <IconComponent className="w-4 h-4 mr-2" />
                      {category.name}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Inventory Grid */}
            <div className="flex-1 p-6 overflow-y-auto">
              {filteredInventory.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-64">
                  <Package className="w-16 h-16 text-gray-500 mb-4" />
                  <h3 className="text-lg font-bold text-gray-400 mb-2">No items found</h3>
                  <p className="text-gray-500 text-center">
                    {searchTerm || selectedCategory !== 'all' 
                      ? 'Try adjusting your search or filter criteria.'
                      : 'Your inventory is empty.'
                    }
                  </p>
                </div>
              ) : (
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-4">
                  {filteredInventory.map((item) => (
                    <div
                      key={item.id}
                      className={`relative bg-gray-800/50 border-2 rounded-lg p-4 hover:bg-gray-700/50 transition-all cursor-pointer ${getRarityColor(item.rarity)}`}
                      onClick={() => {
                        setSelectedItem(item);
                        setShowItemDetails(true);
                      }}
                    >
                      {/* Item Icon/Image */}
                      <div className="w-12 h-12 bg-gray-700 rounded-lg flex items-center justify-center mb-3 mx-auto">
                        <Package className="w-6 h-6 text-gray-400" />
                      </div>

                      {/* Item Name */}
                      <h4 className={`text-sm font-bold text-center mb-2 ${getRarityColor(item.rarity).split(' ')[0]}`}>
                        {item.name}
                      </h4>

                      {/* Item Type */}
                      <p className="text-xs text-gray-400 text-center capitalize mb-2">
                        {item.type}
                      </p>

                      {/* Quantity Badge */}
                      {item.quantity > 1 && (
                        <div className="absolute top-2 right-2 bg-blue-600 text-white text-xs rounded-full w-6 h-6 flex items-center justify-center">
                          {item.quantity}
                        </div>
                      )}

                      {/* Quick Action Buttons */}
                      <div className="flex gap-1 mt-2">
                        {item.type === 'consumable' ? (
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              onUseItem(item);
                            }}
                            className="flex-1 bg-green-600 hover:bg-green-700 text-white text-xs py-1 rounded transition-colors"
                          >
                            Use
                          </button>
                        ) : (
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handleEquipItem(item);
                            }}
                            className="flex-1 bg-blue-600 hover:bg-blue-700 text-white text-xs py-1 rounded transition-colors"
                          >
                            Equip
                          </button>
                        )}
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            onDiscardItem(item);
                          }}
                          className="bg-red-600 hover:bg-red-700 text-white text-xs px-2 py-1 rounded transition-colors"
                        >
                          <Trash2 className="w-3 h-3" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Item Details Modal */}
      {showItemDetails && selectedItem && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-60 p-4">
          <div className="bg-gray-900 border border-purple-500/30 rounded-lg p-6 max-w-md w-full">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className={`text-xl font-bold ${getRarityColor(selectedItem.rarity).split(' ')[0]}`}>
                  {selectedItem.name}
                </h3>
                <p className="text-sm text-gray-400 capitalize">
                  {selectedItem.type} • {selectedItem.rarity}
                </p>
              </div>
              <button
                onClick={() => setShowItemDetails(false)}
                className="text-gray-400 hover:text-white transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4">
              <p className="text-gray-300">{selectedItem.description}</p>
              
              {/* Item Stats */}
              {selectedItem.stats && (
                <div className="bg-gray-800/50 rounded p-3">
                  <h4 className="text-sm font-bold text-white mb-2">Stats</h4>
                  {selectedItem.stats.armor_class && (
                    <div className="text-sm text-gray-300">AC: +{selectedItem.stats.armor_class}</div>
                  )}
                  {selectedItem.stats.damage && (
                    <div className="text-sm text-gray-300">Damage: {selectedItem.stats.damage}</div>
                  )}
                  {selectedItem.stats.healing && (
                    <div className="text-sm text-gray-300">Healing: {selectedItem.stats.healing}</div>
                  )}
                  {selectedItem.stats.bonus && (
                    <div className="text-sm text-gray-300">Bonus: +{selectedItem.stats.bonus}</div>
                  )}
                </div>
              )}

              {/* Item Properties */}
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-400">Quantity:</span>
                  <span className="text-white ml-2">{selectedItem.quantity}</span>
                </div>
                {selectedItem.weight && (
                  <div>
                    <span className="text-gray-400">Weight:</span>
                    <span className="text-white ml-2">{selectedItem.weight} lbs</span>
                  </div>
                )}
                {selectedItem.value && (
                  <div>
                    <span className="text-gray-400">Value:</span>
                    <span className="text-white ml-2">{selectedItem.value} gp</span>
                  </div>
                )}
              </div>

              {/* Action Buttons */}
              <div className="flex gap-2 pt-4">
                {selectedItem.type === 'consumable' ? (
                  <button
                    onClick={() => {
                      onUseItem(selectedItem);
                      setShowItemDetails(false);
                    }}
                    className="flex-1 bg-green-600 hover:bg-green-700 text-white py-2 rounded transition-colors"
                  >
                    Use Item
                  </button>
                ) : (
                  <button
                    onClick={() => {
                      handleEquipItem(selectedItem);
                      setShowItemDetails(false);
                    }}
                    className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 rounded transition-colors"
                  >
                    Equip Item
                  </button>
                )}
                <button
                  onClick={() => {
                    onDiscardItem(selectedItem);
                    setShowItemDetails(false);
                  }}
                  className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded transition-colors"
                >
                  Discard
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
} 