import React from 'react'
import { Wifi, WifiOff, Loader2, AlertTriangle, CheckCircle } from 'lucide-react'
import type { ConnectionStatus } from '@/types/game'

interface ConnectionStatusProps {
  status: ConnectionStatus
  isLoading?: boolean
  error?: string | null
  lastPing?: Date | null
  onReconnect?: () => void
  className?: string
}

const ConnectionStatusIndicator: React.FC<ConnectionStatusProps> = ({
  status,
  isLoading = false,
  error,
  lastPing,
  onReconnect,
  className = ''
}) => {
  const getStatusConfig = () => {
    switch (status) {
      case 'connected':
        return {
          icon: CheckCircle,
          color: 'text-green-400',
          bgColor: 'bg-green-500/20',
          borderColor: 'border-green-400/50',
          label: 'Connected',
          description: 'Real-time connection active'
        }
      case 'connecting':
        return {
          icon: Loader2,
          color: 'text-yellow-400',
          bgColor: 'bg-yellow-500/20',
          borderColor: 'border-yellow-400/50',
          label: 'Connecting...',
          description: 'Establishing connection'
        }
      case 'disconnected':
        return {
          icon: WifiOff,
          color: 'text-gray-400',
          bgColor: 'bg-gray-500/20',
          borderColor: 'border-gray-400/50',
          label: 'Disconnected',
          description: 'No connection'
        }
      case 'error':
        return {
          icon: AlertTriangle,
          color: 'text-red-400',
          bgColor: 'bg-red-500/20',
          borderColor: 'border-red-400/50',
          label: 'Connection Error',
          description: error || 'Connection failed'
        }
      case 'reconnecting':
        return {
          icon: Wifi,
          color: 'text-orange-400',
          bgColor: 'bg-orange-500/20',
          borderColor: 'border-orange-400/50',
          label: 'Reconnecting...',
          description: 'Attempting to reconnect'
        }
      default:
        return {
          icon: WifiOff,
          color: 'text-gray-400',
          bgColor: 'bg-gray-500/20',
          borderColor: 'border-gray-400/50',
          label: 'Unknown',
          description: 'Connection status unknown'
        }
    }
  }

  const config = getStatusConfig()
  const IconComponent = config.icon

  const formatLastPing = (date: Date | null) => {
    if (!date) return 'Never'
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    
    if (diff < 1000) return 'Just now'
    if (diff < 60000) return `${Math.floor(diff / 1000)}s ago`
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`
    return date.toLocaleTimeString()
  }

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      {/* Status Icon */}
      <div className={`flex items-center justify-center w-8 h-8 rounded-full ${config.bgColor} border ${config.borderColor}`}>
        <IconComponent 
          className={`w-4 h-4 ${config.color} ${
            (status === 'connecting' || status === 'reconnecting') ? 'animate-spin' : ''
          }`} 
        />
      </div>

      {/* Status Details */}
      <div className="flex flex-col">
        <div className="flex items-center gap-2">
          <span className={`text-sm font-medium ${config.color}`}>
            {config.label}
          </span>
          {isLoading && (
            <Loader2 className="w-3 h-3 text-blue-400 animate-spin" />
          )}
        </div>
        
        <div className="flex items-center gap-2 text-xs text-gray-400">
          <span>{config.description}</span>
          
          {status === 'connected' && lastPing && (
            <>
              <span>•</span>
              <span>Last ping: {formatLastPing(lastPing)}</span>
            </>
          )}
          
          {status === 'error' && onReconnect && (
            <>
              <span>•</span>
              <button
                onClick={onReconnect}
                className="text-blue-400 hover:text-blue-300 underline"
              >
                Retry
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

// Compact version for smaller spaces
export const CompactConnectionStatus: React.FC<ConnectionStatusProps> = ({
  status,
  isLoading = false,
  onReconnect,
  className = ''
}) => {
  const getStatusConfig = () => {
    switch (status) {
      case 'connected':
        return { icon: CheckCircle, color: 'text-green-400', pulse: false }
      case 'connecting':
      case 'reconnecting':
        return { icon: Loader2, color: 'text-yellow-400', pulse: true }
      case 'disconnected':
        return { icon: WifiOff, color: 'text-gray-400', pulse: false }
      case 'error':
        return { icon: AlertTriangle, color: 'text-red-400', pulse: false }
      default:
        return { icon: WifiOff, color: 'text-gray-400', pulse: false }
    }
  }

  const config = getStatusConfig()
  const IconComponent = config.icon

  return (
    <div className={`flex items-center ${className}`}>
      <div className="relative">
        <IconComponent 
          className={`w-5 h-5 ${config.color} ${config.pulse ? 'animate-spin' : ''}`} 
        />
        {status === 'connected' && (
          <div className="absolute -top-1 -right-1 w-2 h-2 bg-green-400 rounded-full animate-pulse" />
        )}
      </div>
      
      {status === 'error' && onReconnect && (
        <button
          onClick={onReconnect}
          className="ml-2 text-xs text-blue-400 hover:text-blue-300 underline"
        >
          Retry
        </button>
      )}
    </div>
  )
}

export default ConnectionStatusIndicator 