import React, { useState, useRef, useEffect } from 'react'
import { 
  Package, Search, Filter, Grid, List, Sword, Shield, 
  Shirt, Crown, Footprints, Hand, Gem, Zap, 
  Trash2, Star, Eye, ArrowUpDown, MoreVertical 
} from 'lucide-react'
import type { InventoryItem, Character } from '@/types/game'

interface EquipmentSlot {
  id: string
  name: string
  icon: React.ComponentType<any>
  equippedItem?: InventoryItem
  allowedTypes: string[]
  position: { x: number; y: number }
}

interface InventoryCategory {
  id: string
  name: string
  icon: React.ComponentType<any>
  color: string
  types: string[]
}

interface InventoryPanelProps {
  character: Character
  inventory: InventoryItem[]
  isOpen: boolean
  onClose: () => void
  onUseItem: (item: InventoryItem) => void
  onEquipItem: (item: InventoryItem, slot: string) => void
  onUnequipItem: (slot: string) => void
  onDiscardItem: (item: InventoryItem) => void
  onMoveItem: (fromIndex: number, toIndex: number) => void
  className?: string
}

const InventoryPanel: React.FC<InventoryPanelProps> = ({
  character,
  inventory,
  isOpen,
  onClose,
  onUseItem,
  onEquipItem,
  onUnequipItem,
  onDiscardItem,
  onMoveItem,
  className = ''
}) => {
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [searchTerm, setSearchTerm] = useState('')
  const [draggedItem, setDraggedItem] = useState<InventoryItem | null>(null)
  const [hoveredSlot, setHoveredSlot] = useState<string | null>(null)
  const [selectedItem, setSelectedItem] = useState<InventoryItem | null>(null)

  // Inventory categories
  const categories: InventoryCategory[] = [
    { id: 'all', name: 'All Items', icon: Package, color: 'text-gray-400', types: [] },
    { id: 'weapons', name: 'Weapons', icon: Sword, color: 'text-red-400', types: ['weapon'] },
    { id: 'armor', name: 'Armor', icon: Shield, color: 'text-blue-400', types: ['armor'] },
    { id: 'consumables', name: 'Consumables', icon: Zap, color: 'text-green-400', types: ['consumable'] },
    { id: 'treasure', name: 'Treasure', icon: Gem, color: 'text-yellow-400', types: ['treasure'] },
    { id: 'misc', name: 'Miscellaneous', icon: Package, color: 'text-purple-400', types: ['misc'] }
  ]

  // Equipment slots layout (paper doll style)
  const equipmentSlots: EquipmentSlot[] = [
    { id: 'head', name: 'Head', icon: Crown, allowedTypes: ['helmet', 'hat'], position: { x: 50, y: 10 } },
    { id: 'neck', name: 'Neck', icon: Gem, allowedTypes: ['amulet', 'necklace'], position: { x: 50, y: 25 } },
    { id: 'shoulders', name: 'Shoulders', icon: Shirt, allowedTypes: ['cloak', 'pauldrons'], position: { x: 25, y: 35 } },
    { id: 'chest', name: 'Chest', icon: Shirt, allowedTypes: ['armor', 'robe'], position: { x: 50, y: 40 } },
    { id: 'mainhand', name: 'Main Hand', icon: Sword, allowedTypes: ['weapon'], position: { x: 15, y: 55 } },
    { id: 'offhand', name: 'Off Hand', icon: Shield, allowedTypes: ['shield', 'weapon'], position: { x: 85, y: 55 } },
    { id: 'hands', name: 'Hands', icon: Hand, allowedTypes: ['gloves', 'gauntlets'], position: { x: 50, y: 60 } },
    { id: 'waist', name: 'Waist', icon: Gem, allowedTypes: ['belt'], position: { x: 50, y: 70 } },
    { id: 'legs', name: 'Legs', icon: Shirt, allowedTypes: ['pants', 'leggings'], position: { x: 50, y: 80 } },
    { id: 'feet', name: 'Feet', icon: Footprints, allowedTypes: ['boots', 'shoes'], position: { x: 50, y: 95 } }
  ]

  // Get item rarity color
  const getRarityColor = (rarity?: string) => {
    switch (rarity) {
      case 'legendary': return 'text-orange-400 border-orange-400'
      case 'epic': return 'text-purple-400 border-purple-400'
      case 'rare': return 'text-blue-400 border-blue-400'
      case 'uncommon': return 'text-green-400 border-green-400'
      default: return 'text-gray-400 border-gray-400'
    }
  }

  // Get item type icon
  const getItemIcon = (type: string) => {
    const iconMap: Record<string, React.ComponentType<any>> = {
      weapon: Sword,
      armor: Shield,
      helmet: Crown,
      shield: Shield,
      consumable: Zap,
      treasure: Gem,
      misc: Package
    }
    return iconMap[type] || Package
  }

  // Filter inventory based on category and search
  const filteredInventory = inventory.filter(item => {
    const matchesCategory = selectedCategory === 'all' || 
      categories.find(cat => cat.id === selectedCategory)?.types.includes(item.type)
    const matchesSearch = item.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.description.toLowerCase().includes(searchTerm.toLowerCase())
    return matchesCategory && matchesSearch
  })

  // Handle drag start
  const handleDragStart = (e: React.DragEvent, item: InventoryItem) => {
    setDraggedItem(item)
    e.dataTransfer.effectAllowed = 'move'
  }

  // Handle drag over equipment slot
  const handleDragOver = (e: React.DragEvent, slotId: string) => {
    e.preventDefault()
    const slot = equipmentSlots.find(s => s.id === slotId)
    if (slot && draggedItem && slot.allowedTypes.includes(draggedItem.type)) {
      e.dataTransfer.dropEffect = 'move'
      setHoveredSlot(slotId)
    }
  }

  // Handle drop on equipment slot
  const handleDrop = (e: React.DragEvent, slotId: string) => {
    e.preventDefault()
    if (draggedItem) {
      onEquipItem(draggedItem, slotId)
    }
    setDraggedItem(null)
    setHoveredSlot(null)
  }

  if (!isOpen) return null

  return (
    <div className={`fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4 ${className}`}>
      <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-lg border border-purple-500/30 shadow-2xl max-w-6xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="bg-purple-900/50 p-4 border-b border-purple-500/30">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Package className="w-6 h-6 text-purple-400" />
              <h2 className="text-xl font-bold text-purple-200">Inventory</h2>
              <div className="text-sm text-purple-300">
                {inventory.length} items • {character.name}
              </div>
            </div>
            <div className="flex items-center gap-2">
              {/* View Toggle */}
              <div className="flex bg-gray-700 rounded p-1">
                <button
                  onClick={() => setViewMode('grid')}
                  className={`p-1 rounded ${viewMode === 'grid' ? 'bg-purple-600' : 'hover:bg-gray-600'}`}
                >
                  <Grid className="w-4 h-4" />
                </button>
                <button
                  onClick={() => setViewMode('list')}
                  className={`p-1 rounded ${viewMode === 'list' ? 'bg-purple-600' : 'hover:bg-gray-600'}`}
                >
                  <List className="w-4 h-4" />
                </button>
              </div>
              <button
                onClick={onClose}
                className="p-2 hover:bg-gray-700 rounded transition-colors"
              >
                ✕
              </button>
            </div>
          </div>
        </div>

        <div className="flex h-[calc(90vh-100px)]">
          {/* Equipment Slots (Paper Doll) */}
          <div className="w-64 p-4 border-r border-gray-600/50">
            <h3 className="text-lg font-semibold text-gray-200 mb-4">Equipment</h3>
            <div className="relative h-80 bg-gray-800/50 rounded-lg border-2 border-dashed border-gray-600">
              {/* Character Silhouette */}
              <div className="absolute inset-4 bg-gray-700/30 rounded-lg opacity-30" />
              
              {/* Equipment Slots */}
              {equipmentSlots.map((slot) => {
                const IconComponent = slot.icon
                const isHovered = hoveredSlot === slot.id
                return (
                  <div
                    key={slot.id}
                    className={`absolute w-12 h-12 border-2 rounded-lg bg-gray-800 flex items-center justify-center transition-all ${
                      isHovered ? 'border-purple-400 bg-purple-600/20' : 'border-gray-600'
                    }`}
                    style={{
                      left: `${slot.position.x}%`,
                      top: `${slot.position.y}%`,
                      transform: 'translate(-50%, -50%)'
                    }}
                    onDragOver={(e) => handleDragOver(e, slot.id)}
                    onDrop={(e) => handleDrop(e, slot.id)}
                    onDragLeave={() => setHoveredSlot(null)}
                    title={slot.name}
                  >
                    {slot.equippedItem ? (
                      <div className="w-full h-full rounded bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                        <IconComponent className="w-6 h-6 text-white" />
                      </div>
                    ) : (
                      <IconComponent className="w-6 h-6 text-gray-500" />
                    )}
                  </div>
                )
              })}
            </div>
          </div>

          {/* Inventory Content */}
          <div className="flex-1 flex flex-col">
            {/* Controls */}
            <div className="p-4 border-b border-gray-600/50">
              <div className="flex items-center gap-4 mb-3">
                {/* Search */}
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search items..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-purple-500"
                  />
                </div>
              </div>

              {/* Category Filters */}
              <div className="flex gap-2 overflow-x-auto">
                {categories.map((category) => {
                  const IconComponent = category.icon
                  return (
                    <button
                      key={category.id}
                      onClick={() => setSelectedCategory(category.id)}
                      className={`flex items-center gap-2 px-3 py-2 rounded-lg whitespace-nowrap transition-all ${
                        selectedCategory === category.id
                          ? 'bg-purple-600 text-white'
                          : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                      }`}
                    >
                      <IconComponent className={`w-4 h-4 ${category.color}`} />
                      <span className="text-sm">{category.name}</span>
                    </button>
                  )
                })}
              </div>
            </div>

            {/* Items Display */}
            <div className="flex-1 p-4 overflow-y-auto">
              {filteredInventory.length === 0 ? (
                <div className="text-center text-gray-400 py-12">
                  <Package className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>No items found</p>
                </div>
              ) : viewMode === 'grid' ? (
                <div className="grid grid-cols-6 gap-3">
                  {filteredInventory.map((item, index) => {
                    const IconComponent = getItemIcon(item.type)
                    return (
                      <div
                        key={item.id}
                        draggable
                        onDragStart={(e) => handleDragStart(e, item)}
                        onClick={() => setSelectedItem(item)}
                        className={`relative aspect-square border-2 rounded-lg bg-gray-800 p-2 cursor-pointer transition-all hover:scale-105 hover:border-purple-400 ${
                          selectedItem?.id === item.id ? 'border-purple-400 bg-purple-600/20' : getRarityColor(item.rarity)
                        }`}
                        title={item.name}
                      >
                        <IconComponent className="w-6 h-6 mx-auto text-gray-300" />
                        {item.quantity > 1 && (
                          <div className="absolute bottom-1 right-1 bg-blue-600 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                            {item.quantity}
                          </div>
                        )}
                      </div>
                    )
                  })}
                </div>
              ) : (
                <div className="space-y-2">
                  {filteredInventory.map((item) => {
                    const IconComponent = getItemIcon(item.type)
                    return (
                      <div
                        key={item.id}
                        draggable
                        onDragStart={(e) => handleDragStart(e, item)}
                        onClick={() => setSelectedItem(item)}
                        className={`flex items-center gap-3 p-3 border rounded-lg bg-gray-800/50 cursor-pointer transition-all hover:bg-gray-700/50 ${
                          selectedItem?.id === item.id ? 'border-purple-400 bg-purple-600/20' : 'border-gray-600'
                        }`}
                      >
                        <IconComponent className={`w-6 h-6 ${getRarityColor(item.rarity)}`} />
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <span className="font-medium text-white">{item.name}</span>
                            {item.quantity > 1 && (
                              <span className="text-sm text-gray-400">x{item.quantity}</span>
                            )}
                          </div>
                          <p className="text-sm text-gray-400 truncate">{item.description}</p>
                        </div>
                        <div className="flex gap-1">
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              onUseItem(item)
                            }}
                            className="p-1 hover:bg-green-600/20 rounded text-green-400"
                            title="Use Item"
                          >
                            <Eye className="w-4 h-4" />
                          </button>
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              onDiscardItem(item)
                            }}
                            className="p-1 hover:bg-red-600/20 rounded text-red-400"
                            title="Discard Item"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                    )
                  })}
                </div>
              )}
            </div>
          </div>

          {/* Item Details Panel */}
          {selectedItem && (
            <div className="w-80 p-4 border-l border-gray-600/50">
              <div className="space-y-4">
                <div className="text-center">
                  <div className={`w-16 h-16 mx-auto border-2 rounded-lg flex items-center justify-center mb-3 ${getRarityColor(selectedItem.rarity)}`}>
                    {React.createElement(getItemIcon(selectedItem.type), { className: "w-8 h-8" })}
                  </div>
                  <h3 className="text-lg font-bold text-white">{selectedItem.name}</h3>
                  <p className="text-sm text-gray-400 capitalize">{selectedItem.type}</p>
                  {selectedItem.quantity > 1 && (
                    <p className="text-sm text-blue-400">Quantity: {selectedItem.quantity}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <h4 className="font-medium text-gray-200">Description</h4>
                  <p className="text-sm text-gray-400">{selectedItem.description}</p>
                </div>

                <div className="flex gap-2">
                  <button
                    onClick={() => onUseItem(selectedItem)}
                    className="flex-1 py-2 bg-green-600 hover:bg-green-700 rounded font-medium transition-colors"
                  >
                    Use
                  </button>
                  <button
                    onClick={() => onDiscardItem(selectedItem)}
                    className="px-4 py-2 bg-red-600 hover:bg-red-700 rounded transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default InventoryPanel 