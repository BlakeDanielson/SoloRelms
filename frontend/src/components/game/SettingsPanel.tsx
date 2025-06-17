'use client'

import React, { useState, useEffect } from 'react'
import { 
  Settings, 
  Volume2, 
  VolumeX, 
  Eye, 
  EyeOff, 
  Gamepad2, 
  Bell, 
  BellOff, 
  Accessibility, 
  Monitor, 
  X,
  RotateCcw,
  Save,
  ChevronRight,
  ChevronDown
} from 'lucide-react'

interface SettingsData {
  audio: {
    masterVolume: number
    musicVolume: number
    sfxVolume: number
    voiceVolume: number
    muteAll: boolean
  }
  visual: {
    brightness: number
    contrast: number
    textSize: number
    animationSpeed: number
    particleEffects: boolean
    screenShake: boolean
  }
  gameplay: {
    autoSave: boolean
    autoSaveInterval: number
    confirmActions: boolean
    showDamageNumbers: boolean
    combatAnimations: boolean
    fastForwardText: boolean
  }
  notifications: {
    questComplete: boolean
    levelUp: boolean
    itemFound: boolean
    combatStart: boolean
    pushNotifications: boolean
  }
  accessibility: {
    colorBlindMode: boolean
    highContrast: boolean
    reducedMotion: boolean
    screenReader: boolean
    subtitles: boolean
    largeText: boolean
  }
  advanced: {
    debugMode: boolean
    showFPS: boolean
    logLevel: 'error' | 'warn' | 'info' | 'debug'
    cacheSize: number
    networkTimeout: number
  }
}

interface SettingsPanelProps {
  isOpen: boolean
  onClose: () => void
  onSettingsChange?: (settings: SettingsData) => void
}

const DEFAULT_SETTINGS: SettingsData = {
  audio: {
    masterVolume: 80,
    musicVolume: 70,
    sfxVolume: 85,
    voiceVolume: 90,
    muteAll: false
  },
  visual: {
    brightness: 50,
    contrast: 50,
    textSize: 16,
    animationSpeed: 100,
    particleEffects: true,
    screenShake: true
  },
  gameplay: {
    autoSave: true,
    autoSaveInterval: 5,
    confirmActions: true,
    showDamageNumbers: true,
    combatAnimations: true,
    fastForwardText: false
  },
  notifications: {
    questComplete: true,
    levelUp: true,
    itemFound: true,
    combatStart: true,
    pushNotifications: false
  },
  accessibility: {
    colorBlindMode: false,
    highContrast: false,
    reducedMotion: false,
    screenReader: false,
    subtitles: true,
    largeText: false
  },
  advanced: {
    debugMode: false,
    showFPS: false,
    logLevel: 'warn',
    cacheSize: 100,
    networkTimeout: 30
  }
}

const SettingsPanel: React.FC<SettingsPanelProps> = ({ 
  isOpen, 
  onClose, 
  onSettingsChange 
}) => {
  const [settings, setSettings] = useState<SettingsData>(DEFAULT_SETTINGS)
  const [activeTab, setActiveTab] = useState<keyof SettingsData>('audio')
  const [hasChanges, setHasChanges] = useState(false)
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({})

  // Load settings from localStorage on mount
  useEffect(() => {
    const savedSettings = localStorage.getItem('solorelms-settings')
    if (savedSettings) {
      try {
        const parsed = JSON.parse(savedSettings)
        setSettings({ ...DEFAULT_SETTINGS, ...parsed })
      } catch (error) {
        console.error('Failed to parse saved settings:', error)
      }
    }
  }, [])

  // Save settings to localStorage
  const saveSettings = () => {
    localStorage.setItem('solorelms-settings', JSON.stringify(settings))
    setHasChanges(false)
    onSettingsChange?.(settings)
  }

  // Reset settings to defaults
  const resetSettings = () => {
    setSettings(DEFAULT_SETTINGS)
    setHasChanges(true)
  }

  // Update setting value
  const updateSetting = (category: keyof SettingsData, key: string, value: any) => {
    setSettings(prev => ({
      ...prev,
      [category]: {
        ...prev[category],
        [key]: value
      }
    }))
    setHasChanges(true)
  }

  // Toggle section expansion
  const toggleSection = (section: string) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }))
  }

  if (!isOpen) return null

  const tabs = [
    { id: 'audio', label: 'Audio', icon: Volume2 },
    { id: 'visual', label: 'Visual', icon: Eye },
    { id: 'gameplay', label: 'Gameplay', icon: Gamepad2 },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'accessibility', label: 'Accessibility', icon: Accessibility },
    { id: 'advanced', label: 'Advanced', icon: Monitor }
  ] as const

  const renderSlider = (
    label: string,
    value: number,
    onChange: (value: number) => void,
    min = 0,
    max = 100,
    step = 1,
    unit = '%'
  ) => (
    <div className="mb-4">
      <div className="flex justify-between items-center mb-2">
        <label className="text-sm font-medium text-gray-300">{label}</label>
        <span className="text-sm text-gray-400">{value}{unit}</span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
      />
    </div>
  )

  const renderToggle = (
    label: string,
    value: boolean,
    onChange: (value: boolean) => void,
    description?: string
  ) => (
    <div className="flex items-center justify-between py-2">
      <div>
        <label className="text-sm font-medium text-gray-300">{label}</label>
        {description && <p className="text-xs text-gray-500">{description}</p>}
      </div>
      <button
        onClick={() => onChange(!value)}
        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
          value ? 'bg-purple-600' : 'bg-gray-600'
        }`}
      >
        <span
          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
            value ? 'translate-x-6' : 'translate-x-1'
          }`}
        />
      </button>
    </div>
  )

  const renderSelect = (
    label: string,
    value: string,
    options: { value: string; label: string }[],
    onChange: (value: string) => void
  ) => (
    <div className="mb-4">
      <label className="block text-sm font-medium text-gray-300 mb-2">{label}</label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white text-sm focus:border-purple-500 focus:outline-none"
      >
        {options.map(option => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </div>
  )

  const renderTabContent = () => {
    switch (activeTab) {
      case 'audio':
        return (
          <div className="space-y-4">
            {renderToggle(
              'Mute All Audio',
              settings.audio.muteAll,
              (value) => updateSetting('audio', 'muteAll', value),
              'Disable all game audio'
            )}
            {!settings.audio.muteAll && (
              <>
                {renderSlider(
                  'Master Volume',
                  settings.audio.masterVolume,
                  (value) => updateSetting('audio', 'masterVolume', value)
                )}
                {renderSlider(
                  'Music Volume',
                  settings.audio.musicVolume,
                  (value) => updateSetting('audio', 'musicVolume', value)
                )}
                {renderSlider(
                  'Sound Effects',
                  settings.audio.sfxVolume,
                  (value) => updateSetting('audio', 'sfxVolume', value)
                )}
                {renderSlider(
                  'Voice Volume',
                  settings.audio.voiceVolume,
                  (value) => updateSetting('audio', 'voiceVolume', value)
                )}
              </>
            )}
          </div>
        )

      case 'visual':
        return (
          <div className="space-y-4">
            {renderSlider(
              'Brightness',
              settings.visual.brightness,
              (value) => updateSetting('visual', 'brightness', value)
            )}
            {renderSlider(
              'Contrast',
              settings.visual.contrast,
              (value) => updateSetting('visual', 'contrast', value)
            )}
            {renderSlider(
              'Text Size',
              settings.visual.textSize,
              (value) => updateSetting('visual', 'textSize', value),
              12,
              24,
              1,
              'px'
            )}
            {renderSlider(
              'Animation Speed',
              settings.visual.animationSpeed,
              (value) => updateSetting('visual', 'animationSpeed', value),
              50,
              200,
              10,
              '%'
            )}
            {renderToggle(
              'Particle Effects',
              settings.visual.particleEffects,
              (value) => updateSetting('visual', 'particleEffects', value),
              'Show visual particle effects'
            )}
            {renderToggle(
              'Screen Shake',
              settings.visual.screenShake,
              (value) => updateSetting('visual', 'screenShake', value),
              'Enable screen shake effects'
            )}
          </div>
        )

      case 'gameplay':
        return (
          <div className="space-y-4">
            {renderToggle(
              'Auto Save',
              settings.gameplay.autoSave,
              (value) => updateSetting('gameplay', 'autoSave', value),
              'Automatically save game progress'
            )}
            {settings.gameplay.autoSave && renderSlider(
              'Auto Save Interval',
              settings.gameplay.autoSaveInterval,
              (value) => updateSetting('gameplay', 'autoSaveInterval', value),
              1,
              30,
              1,
              ' min'
            )}
            {renderToggle(
              'Confirm Actions',
              settings.gameplay.confirmActions,
              (value) => updateSetting('gameplay', 'confirmActions', value),
              'Show confirmation for important actions'
            )}
            {renderToggle(
              'Show Damage Numbers',
              settings.gameplay.showDamageNumbers,
              (value) => updateSetting('gameplay', 'showDamageNumbers', value),
              'Display floating damage numbers'
            )}
            {renderToggle(
              'Combat Animations',
              settings.gameplay.combatAnimations,
              (value) => updateSetting('gameplay', 'combatAnimations', value),
              'Play combat animation sequences'
            )}
            {renderToggle(
              'Fast Forward Text',
              settings.gameplay.fastForwardText,
              (value) => updateSetting('gameplay', 'fastForwardText', value),
              'Skip text animation delays'
            )}
          </div>
        )

      case 'notifications':
        return (
          <div className="space-y-4">
            {renderToggle(
              'Quest Complete',
              settings.notifications.questComplete,
              (value) => updateSetting('notifications', 'questComplete', value),
              'Notify when quests are completed'
            )}
            {renderToggle(
              'Level Up',
              settings.notifications.levelUp,
              (value) => updateSetting('notifications', 'levelUp', value),
              'Notify when character levels up'
            )}
            {renderToggle(
              'Item Found',
              settings.notifications.itemFound,
              (value) => updateSetting('notifications', 'itemFound', value),
              'Notify when items are discovered'
            )}
            {renderToggle(
              'Combat Start',
              settings.notifications.combatStart,
              (value) => updateSetting('notifications', 'combatStart', value),
              'Notify when combat begins'
            )}
            {renderToggle(
              'Push Notifications',
              settings.notifications.pushNotifications,
              (value) => updateSetting('notifications', 'pushNotifications', value),
              'Send browser notifications when game is closed'
            )}
          </div>
        )

      case 'accessibility':
        return (
          <div className="space-y-4">
            {renderToggle(
              'Color Blind Mode',
              settings.accessibility.colorBlindMode,
              (value) => updateSetting('accessibility', 'colorBlindMode', value),
              'Use color blind-friendly palette'
            )}
            {renderToggle(
              'High Contrast',
              settings.accessibility.highContrast,
              (value) => updateSetting('accessibility', 'highContrast', value),
              'Increase UI contrast for better visibility'
            )}
            {renderToggle(
              'Reduced Motion',
              settings.accessibility.reducedMotion,
              (value) => updateSetting('accessibility', 'reducedMotion', value),
              'Reduce or disable animations'
            )}
            {renderToggle(
              'Screen Reader Support',
              settings.accessibility.screenReader,
              (value) => updateSetting('accessibility', 'screenReader', value),
              'Enable screen reader optimizations'
            )}
            {renderToggle(
              'Subtitles',
              settings.accessibility.subtitles,
              (value) => updateSetting('accessibility', 'subtitles', value),
              'Show text for all audio content'
            )}
            {renderToggle(
              'Large Text',
              settings.accessibility.largeText,
              (value) => updateSetting('accessibility', 'largeText', value),
              'Use larger text throughout the interface'
            )}
          </div>
        )

      case 'advanced':
        return (
          <div className="space-y-4">
            {renderToggle(
              'Debug Mode',
              settings.advanced.debugMode,
              (value) => updateSetting('advanced', 'debugMode', value),
              'Show debug information and tools'
            )}
            {renderToggle(
              'Show FPS',
              settings.advanced.showFPS,
              (value) => updateSetting('advanced', 'showFPS', value),
              'Display frame rate counter'
            )}
            {renderSelect(
              'Log Level',
              settings.advanced.logLevel,
              [
                { value: 'error', label: 'Error' },
                { value: 'warn', label: 'Warning' },
                { value: 'info', label: 'Info' },
                { value: 'debug', label: 'Debug' }
              ],
              (value) => updateSetting('advanced', 'logLevel', value as any)
            )}
            {renderSlider(
              'Cache Size',
              settings.advanced.cacheSize,
              (value) => updateSetting('advanced', 'cacheSize', value),
              50,
              500,
              10,
              ' MB'
            )}
            {renderSlider(
              'Network Timeout',
              settings.advanced.networkTimeout,
              (value) => updateSetting('advanced', 'networkTimeout', value),
              10,
              120,
              5,
              's'
            )}
          </div>
        )

      default:
        return null
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-gray-800 rounded-lg border border-purple-500/30 w-full max-w-4xl max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-700">
          <div className="flex items-center gap-3">
            <Settings className="w-6 h-6 text-purple-400" />
            <h2 className="text-xl font-bold text-white">Settings</h2>
          </div>
          <div className="flex items-center gap-2">
            {hasChanges && (
              <>
                <button
                  onClick={resetSettings}
                  className="px-3 py-1 bg-gray-600 hover:bg-gray-500 text-white rounded text-sm flex items-center gap-1 transition-colors"
                >
                  <RotateCcw className="w-4 h-4" />
                  Reset
                </button>
                <button
                  onClick={saveSettings}
                  className="px-3 py-1 bg-purple-600 hover:bg-purple-500 text-white rounded text-sm flex items-center gap-1 transition-colors"
                >
                  <Save className="w-4 h-4" />
                  Save
                </button>
              </>
            )}
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-700 rounded transition-colors"
            >
              <X className="w-5 h-5 text-gray-400" />
            </button>
          </div>
        </div>

        <div className="flex flex-1 overflow-hidden">
          {/* Sidebar */}
          <div className="w-48 bg-gray-900/50 border-r border-gray-700 p-4">
            <nav className="space-y-1">
              {tabs.map((tab) => {
                const Icon = tab.icon
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`w-full flex items-center gap-3 px-3 py-2 rounded text-sm font-medium transition-colors ${
                      activeTab === tab.id
                        ? 'bg-purple-600 text-white'
                        : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    {tab.label}
                  </button>
                )
              })}
            </nav>
          </div>

          {/* Content */}
          <div className="flex-1 p-6 overflow-y-auto">
            <div className="max-w-md">
              <h3 className="text-lg font-semibold text-white mb-4 capitalize">
                {activeTab} Settings
              </h3>
              {renderTabContent()}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-gray-700 bg-gray-900/30">
          <div className="flex justify-between items-center text-sm text-gray-400">
            <span>Changes are saved automatically to your browser</span>
            {hasChanges && (
              <span className="text-yellow-400">⚠️ Unsaved changes</span>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default SettingsPanel 