'use client'

import React, { useState, useEffect, useCallback } from 'react'
import { Search, Filter, X, ChevronDown, SortAsc, SortDesc } from 'lucide-react'

interface SearchAndFilterProps {
  onSearchChange: (search: string) => void
  onFilterChange: (filters: FilterOptions) => void
  onSortChange: (sort: SortOptions) => void
  totalCount: number
  filteredCount: number
  className?: string
}

interface FilterOptions {
  classes: string[]
  races: string[]
  levelRange: [number, number]
  showActive: boolean
}

interface SortOptions {
  field: 'name' | 'level' | 'created_at' | 'last_played'
  direction: 'asc' | 'desc'
}

const CLASSES = [
  'Barbarian', 'Bard', 'Cleric', 'Druid', 'Fighter', 'Monk',
  'Paladin', 'Ranger', 'Rogue', 'Sorcerer', 'Warlock', 'Wizard'
]

const RACES = [
  'Human', 'Elf', 'Dwarf', 'Halfling', 'Dragonborn', 'Gnome',
  'Half-Elf', 'Half-Orc', 'Tiefling'
]

const SORT_OPTIONS = [
  { field: 'name', label: 'Name' },
  { field: 'level', label: 'Level' },
  { field: 'created_at', label: 'Created' },
  { field: 'last_played', label: 'Last Played' }
] as const

const SearchAndFilter: React.FC<SearchAndFilterProps> = ({
  onSearchChange,
  onFilterChange,
  onSortChange,
  totalCount,
  filteredCount,
  className = ''
}) => {
  const [searchTerm, setSearchTerm] = useState('')
  const [isFilterOpen, setIsFilterOpen] = useState(false)
  const [isSortOpen, setIsSortOpen] = useState(false)
  
  const [filters, setFilters] = useState<FilterOptions>({
    classes: [],
    races: [],
    levelRange: [1, 20],
    showActive: true
  })
  
  const [sort, setSort] = useState<SortOptions>({
    field: 'name',
    direction: 'asc'
  })

  // Debounced search
  const debouncedSearch = useCallback(
    debounce((value: string) => {
      onSearchChange(value)
    }, 300),
    [onSearchChange]
  )

  useEffect(() => {
    debouncedSearch(searchTerm)
  }, [searchTerm, debouncedSearch])

  useEffect(() => {
    onFilterChange(filters)
  }, [filters, onFilterChange])

  useEffect(() => {
    onSortChange(sort)
  }, [sort, onSortChange])

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value)
  }

  const handleClassToggle = (className: string) => {
    setFilters(prev => ({
      ...prev,
      classes: prev.classes.includes(className)
        ? prev.classes.filter(c => c !== className)
        : [...prev.classes, className]
    }))
  }

  const handleRaceToggle = (race: string) => {
    setFilters(prev => ({
      ...prev,
      races: prev.races.includes(race)
        ? prev.races.filter(r => r !== race)
        : [...prev.races, race]
    }))
  }

  const handleLevelRangeChange = (index: number, value: number) => {
    setFilters(prev => ({
      ...prev,
      levelRange: index === 0
        ? [value, prev.levelRange[1]]
        : [prev.levelRange[0], value] as [number, number]
    }))
  }

  const handleSortChange = (field: SortOptions['field']) => {
    setSort(prev => ({
      field,
      direction: prev.field === field && prev.direction === 'asc' ? 'desc' : 'asc'
    }))
    setIsSortOpen(false)
  }

  const clearFilters = () => {
    setFilters({
      classes: [],
      races: [],
      levelRange: [1, 20],
      showActive: true
    })
    setSearchTerm('')
  }

  const hasActiveFilters = searchTerm || filters.classes.length > 0 || 
    filters.races.length > 0 || filters.levelRange[0] > 1 || filters.levelRange[1] < 20

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Search Bar */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
        <input
          type="text"
          placeholder="Search characters by name, race, or class..."
          value={searchTerm}
          onChange={handleSearchChange}
          className="w-full bg-white/10 border border-white/20 rounded-lg pl-10 pr-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
        />
        {searchTerm && (
          <button
            onClick={() => setSearchTerm('')}
            className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-white"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Filter and Sort Controls */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div className="flex items-center space-x-4">
          {/* Filter Button */}
          <div className="relative">
            <button
              onClick={() => setIsFilterOpen(!isFilterOpen)}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg border transition-colors ${
                hasActiveFilters
                  ? 'bg-purple-600/20 border-purple-500/50 text-purple-300'
                  : 'bg-white/10 border-white/20 text-white hover:bg-white/15'
              }`}
            >
              <Filter className="w-4 h-4" />
              <span>Filters</span>
              {hasActiveFilters && (
                <span className="bg-purple-500 text-white text-xs rounded-full px-2 py-0.5">
                  {filters.classes.length + filters.races.length + 
                   (filters.levelRange[0] > 1 || filters.levelRange[1] < 20 ? 1 : 0)}
                </span>
              )}
              <ChevronDown className={`w-4 h-4 transition-transform ${isFilterOpen ? 'rotate-180' : ''}`} />
            </button>

            {/* Filter Dropdown */}
            {isFilterOpen && (
              <div className="absolute top-full left-0 mt-2 w-80 bg-gray-900/95 backdrop-blur-sm border border-white/20 rounded-lg p-4 z-10">
                <div className="space-y-4">
                  {/* Classes */}
                  <div>
                    <h4 className="text-sm font-medium text-white mb-2">Classes</h4>
                    <div className="grid grid-cols-3 gap-2">
                      {CLASSES.map(className => (
                        <label key={className} className="flex items-center space-x-2 cursor-pointer">
                          <input
                            type="checkbox"
                            checked={filters.classes.includes(className)}
                            onChange={() => handleClassToggle(className)}
                            className="rounded border-white/20 bg-white/10 text-purple-600 focus:ring-purple-500"
                          />
                          <span className="text-xs text-gray-300">{className}</span>
                        </label>
                      ))}
                    </div>
                  </div>

                  {/* Races */}
                  <div>
                    <h4 className="text-sm font-medium text-white mb-2">Races</h4>
                    <div className="grid grid-cols-3 gap-2">
                      {RACES.map(race => (
                        <label key={race} className="flex items-center space-x-2 cursor-pointer">
                          <input
                            type="checkbox"
                            checked={filters.races.includes(race)}
                            onChange={() => handleRaceToggle(race)}
                            className="rounded border-white/20 bg-white/10 text-purple-600 focus:ring-purple-500"
                          />
                          <span className="text-xs text-gray-300">{race}</span>
                        </label>
                      ))}
                    </div>
                  </div>

                  {/* Level Range */}
                  <div>
                    <h4 className="text-sm font-medium text-white mb-2">Level Range</h4>
                    <div className="flex items-center space-x-4">
                      <div className="flex items-center space-x-2">
                        <span className="text-xs text-gray-400">Min:</span>
                        <input
                          type="number"
                          min="1"
                          max="20"
                          value={filters.levelRange[0]}
                          onChange={(e) => handleLevelRangeChange(0, parseInt(e.target.value) || 1)}
                          className="w-16 bg-white/10 border border-white/20 rounded px-2 py-1 text-white text-xs"
                        />
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className="text-xs text-gray-400">Max:</span>
                        <input
                          type="number"
                          min="1"
                          max="20"
                          value={filters.levelRange[1]}
                          onChange={(e) => handleLevelRangeChange(1, parseInt(e.target.value) || 20)}
                          className="w-16 bg-white/10 border border-white/20 rounded px-2 py-1 text-white text-xs"
                        />
                      </div>
                    </div>
                  </div>

                  {/* Clear Filters */}
                  {hasActiveFilters && (
                    <button
                      onClick={clearFilters}
                      className="w-full bg-red-600/20 hover:bg-red-600/30 text-red-300 px-3 py-2 rounded-lg text-sm transition-colors"
                    >
                      Clear All Filters
                    </button>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Sort Button */}
          <div className="relative">
            <button
              onClick={() => setIsSortOpen(!isSortOpen)}
              className="flex items-center space-x-2 px-4 py-2 rounded-lg border bg-white/10 border-white/20 text-white hover:bg-white/15 transition-colors"
            >
              {sort.direction === 'asc' ? <SortAsc className="w-4 h-4" /> : <SortDesc className="w-4 h-4" />}
              <span>Sort by {SORT_OPTIONS.find(opt => opt.field === sort.field)?.label}</span>
              <ChevronDown className={`w-4 h-4 transition-transform ${isSortOpen ? 'rotate-180' : ''}`} />
            </button>

            {/* Sort Dropdown */}
            {isSortOpen && (
              <div className="absolute top-full left-0 mt-2 w-48 bg-gray-900/95 backdrop-blur-sm border border-white/20 rounded-lg p-2 z-10">
                {SORT_OPTIONS.map(option => (
                  <button
                    key={option.field}
                    onClick={() => handleSortChange(option.field)}
                    className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors ${
                      sort.field === option.field
                        ? 'bg-purple-600/20 text-purple-300'
                        : 'text-gray-300 hover:bg-white/10'
                    }`}
                  >
                    {option.label}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Results Count */}
        <div className="text-sm text-gray-400">
          {filteredCount === totalCount ? (
            `${totalCount} character${totalCount !== 1 ? 's' : ''}`
          ) : (
            `${filteredCount} of ${totalCount} character${totalCount !== 1 ? 's' : ''}`
          )}
        </div>
      </div>
    </div>
  )
}

// Debounce utility function
function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout
  return (...args: Parameters<T>) => {
    clearTimeout(timeout)
    timeout = setTimeout(() => func(...args), wait)
  }
}

export default SearchAndFilter
export type { FilterOptions, SortOptions } 