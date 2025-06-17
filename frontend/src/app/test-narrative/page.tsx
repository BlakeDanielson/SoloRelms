'use client';

import React, { useState } from 'react';
import NarrativeContextDisplay from '../../components/game/NarrativeContextDisplay';
import { useMockNarrativeContext } from '../../hooks/useNarrativeContext';

export default function TestNarrativePage() {
  const [isNarrativeOpen, setIsNarrativeOpen] = useState(true);
  const narrativeData = useMockNarrativeContext();

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900 text-white">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-center mb-4">
            Narrative Context Display Test
          </h1>
          <p className="text-gray-300 text-center max-w-2xl mx-auto">
            Testing the Narrative Context Display component with mock data to verify all features work correctly.
          </p>
        </div>

        <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg border border-gray-700/50 p-6 mb-6">
          <h2 className="text-2xl font-semibold mb-4">Component Controls</h2>
          <div className="flex gap-4 items-center">
            <button
              onClick={() => setIsNarrativeOpen(!isNarrativeOpen)}
              className={`px-4 py-2 rounded transition-colors ${
                isNarrativeOpen 
                  ? 'bg-blue-600 hover:bg-blue-700' 
                  : 'bg-gray-600 hover:bg-gray-700'
              }`}
            >
              {isNarrativeOpen ? 'Hide' : 'Show'} Narrative Context
            </button>
            <span className="text-gray-300">
              Status: {narrativeData.isLoading ? 'Loading...' : 'Ready'}
            </span>
          </div>
        </div>

        <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg border border-gray-700/50 p-6 mb-6">
          <h2 className="text-2xl font-semibold mb-4">Test Data Summary</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-gray-700/50 rounded-lg p-4">
              <h3 className="font-semibold text-blue-300 mb-2">Major Decisions</h3>
              <p className="text-2xl font-bold">{narrativeData.majorDecisions.length}</p>
              <p className="text-sm text-gray-400">Tracked decisions</p>
            </div>
            <div className="bg-gray-700/50 rounded-lg p-4">
              <h3 className="font-semibold text-green-300 mb-2">NPCs</h3>
              <p className="text-2xl font-bold">{narrativeData.npcStatuses.length}</p>
              <p className="text-sm text-gray-400">Known characters</p>
            </div>
            <div className="bg-gray-700/50 rounded-lg p-4">
              <h3 className="font-semibold text-purple-300 mb-2">Objectives</h3>
              <p className="text-2xl font-bold">{narrativeData.worldState.active_objectives.length}</p>
              <p className="text-sm text-gray-400">Active goals</p>
            </div>
          </div>
        </div>

        {narrativeData.error && (
          <div className="bg-red-900/50 border border-red-500/50 rounded-lg p-4 mb-6">
            <h3 className="font-semibold text-red-300 mb-2">Error</h3>
            <p className="text-red-200">{narrativeData.error}</p>
          </div>
        )}

        {/* Main Test Area - Full Height Container */}
        <div className="relative h-[600px] bg-gray-800/30 backdrop-blur-sm rounded-lg border border-gray-700/50 overflow-hidden">
          <div className="absolute inset-0 flex items-center justify-center text-gray-500">
            <div className="text-center">
              <p className="text-lg mb-2">Game Interface Would Go Here</p>
              <p className="text-sm">The Narrative Context Display overlays on the right →</p>
            </div>
          </div>
          
          {/* Narrative Context Display Component */}
          <NarrativeContextDisplay
            isOpen={isNarrativeOpen}
            onToggle={() => setIsNarrativeOpen(!isNarrativeOpen)}
            majorDecisions={narrativeData.majorDecisions}
            npcStatuses={narrativeData.npcStatuses}
            worldState={narrativeData.worldState}
            className="absolute top-0 right-0 h-full"
          />
        </div>

        <div className="mt-6 bg-gray-800/50 backdrop-blur-sm rounded-lg border border-gray-700/50 p-6">
          <h2 className="text-2xl font-semibold mb-4">Test Instructions</h2>
          <div className="space-y-3 text-gray-300">
            <p>✅ <strong>Sidebar Toggle:</strong> Click the toggle button or arrow to open/close the sidebar</p>
            <p>✅ <strong>Tab Navigation:</strong> Switch between Decisions, NPCs, and World State tabs</p>
            <p>✅ <strong>Decision Table:</strong> Sort and filter major decisions by various criteria</p>
            <p>✅ <strong>NPC Graph:</strong> Interactive relationship visualization with ReactFlow</p>
            <p>✅ <strong>World State:</strong> View active objectives, explored areas, and events</p>
            <p>✅ <strong>Responsive Design:</strong> Test on different screen sizes</p>
          </div>
        </div>
      </div>
    </div>
  );
} 