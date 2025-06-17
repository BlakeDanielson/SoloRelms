'use client';

import React, { useState, useMemo, useCallback } from 'react';
import '@xyflow/react/dist/style.css';
import {
  Sidebar,
  ProSidebarProvider,
} from 'react-pro-sidebar';
import {
  ReactFlow,
  Node,
  Edge,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  NodeTypes,
} from '@xyflow/react';
import {
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getSortedRowModel,
  useReactTable,
  createColumnHelper,
  ColumnFiltersState,
  SortingState,
} from '@tanstack/react-table';
import { Tooltip } from 'react-tooltip';
import {
  ChevronLeft,
  ChevronRight,
  History,
  Users,
  MapPin,
  Clock,
  Search,
  Filter,
  Eye,
  Heart,
  Shield,
  Sword,
  Target,
  Book,
  Zap,
  Minus,
} from 'lucide-react';

import { MajorDecision, NPCStatus, WorldState } from '../../lib/narrativeDataAdapter';

interface NarrativeContextDisplayProps {
  isOpen: boolean;
  onToggle: () => void;
  majorDecisions: MajorDecision[];
  npcStatuses: NPCStatus[];
  worldState: WorldState;
  className?: string;
}

// Custom Node Components for NPC Relationship Graph
const NPCNode: React.FC<{ data: NPCStatus }> = ({ data }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ally': return 'bg-green-500';
      case 'hostile': return 'bg-red-500';
      case 'neutral': return 'bg-gray-500';
      case 'dead': return 'bg-black';
      default: return 'bg-gray-400';
    }
  };

  const getDispositionIcon = (disposition: string) => {
    switch (disposition) {
      case 'friendly': return <Heart className="w-4 h-4 text-green-400" />;
      case 'hostile': return <Sword className="w-4 h-4 text-red-400" />;
      case 'neutral': return <Shield className="w-4 h-4 text-gray-400" />;
      default: return <Minus className="w-4 h-4 text-gray-400" />;
    }
  };

  return (
    <div
      className={`px-3 py-2 rounded-lg border-2 border-white/20 text-white text-sm min-w-[120px] ${getStatusColor(data.status)}`}
      data-tooltip-id={`npc-${data.id}`}
      data-tooltip-content={`${data.name}\nStatus: ${data.status}\nLocation: ${data.location}\nRelationship: ${data.relationship_strength}/100`}
    >
      <div className="flex items-center justify-between">
        <span className="font-medium truncate">{data.name}</span>
        {getDispositionIcon(data.disposition)}
      </div>
      <div className="text-xs opacity-80">{data.location}</div>
    </div>
  );
};

const nodeTypes: NodeTypes = {
  npcNode: NPCNode,
};

export default function NarrativeContextDisplay({
  isOpen,
  onToggle,
  majorDecisions,
  npcStatuses,
  worldState,
  className = '',
}: NarrativeContextDisplayProps) {
  const [activeTab, setActiveTab] = useState<'decisions' | 'npcs' | 'world'>('decisions');
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStage, setFilterStage] = useState('all');
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [sorting, setSorting] = useState<SortingState>([]);

  // Decision table setup
  const columnHelper = createColumnHelper<MajorDecision>();

  const decisionColumns = useMemo(
    () => [
      columnHelper.accessor('timestamp', {
        header: 'Time',
        cell: (info) => (
          <div className="flex items-center space-x-2">
            <Clock className="w-4 h-4 text-gray-400" />
            <span className="text-sm text-gray-300">
              {new Date(info.getValue()).toLocaleDateString()}
            </span>
          </div>
        ),
        size: 120,
      }),
      columnHelper.accessor('decision', {
        header: 'Decision',
        cell: (info) => (
          <div className="font-medium text-white">
            {info.getValue()}
          </div>
        ),
        size: 150,
      }),
      columnHelper.accessor('description', {
        header: 'Description',
        cell: (info) => (
          <div className="text-sm text-gray-300 max-w-xs">
            {info.getValue()}
          </div>
        ),
        size: 250,
      }),
      columnHelper.accessor('stage', {
        header: 'Stage',
        cell: (info) => (
          <span className="px-2 py-1 bg-purple-900/50 text-purple-300 text-xs rounded">
            {info.getValue()}
          </span>
        ),
        size: 100,
      }),
      columnHelper.accessor('consequences', {
        header: 'Impact',
        cell: (info) => (
          <div className="flex flex-wrap gap-1 max-w-xs">
            {info.getValue().slice(0, 3).map((consequence, idx) => (
              <span key={idx} className="px-1 py-0.5 bg-orange-900/50 text-orange-300 text-xs rounded">
                {consequence}
              </span>
            ))}
            {info.getValue().length > 3 && (
              <span className="text-xs text-gray-400">+{info.getValue().length - 3} more</span>
            )}
          </div>
        ),
        size: 200,
      }),
    ],
    [columnHelper]
  );

  const table = useReactTable({
    data: majorDecisions,
    columns: decisionColumns,
    getCoreRowModel: getCoreRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getSortedRowModel: getSortedRowModel(),
    onColumnFiltersChange: setColumnFilters,
    onSortingChange: setSorting,
    state: {
      columnFilters,
      sorting,
    },
  });

  // NPC Relationship Graph setup
  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);

  const generateNPCGraph = useCallback(() => {
    const npcNodes: Node[] = npcStatuses.map((npc, index) => ({
      id: npc.id,
      type: 'npcNode',
      position: {
        x: (index % 3) * 200,
        y: Math.floor(index / 3) * 100,
      },
      data: npc,
    }));

    const relationshipEdges: Edge[] = [];
    npcStatuses.forEach((npc, index) => {
      if (index > 0) {
        const prevNpc = npcStatuses[index - 1];
        relationshipEdges.push({
          id: `${prevNpc.id}-${npc.id}`,
          source: prevNpc.id,
          target: npc.id,
          type: 'smoothstep',
          style: {
            stroke: npc.relationship_strength > 0 ? '#10b981' : '#ef4444',
            strokeWidth: Math.abs(npc.relationship_strength) / 25,
          },
        });
      }
    });

    setNodes(npcNodes);
    setEdges(relationshipEdges);
  }, [npcStatuses, setNodes, setEdges]);

  React.useEffect(() => {
    generateNPCGraph();
  }, [generateNPCGraph]);

  // Filtered data
  const filteredDecisions = useMemo(() => {
    return majorDecisions.filter((decision) => {
      const matchesSearch = decision.decision.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           decision.description.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesStage = filterStage === 'all' || decision.stage === filterStage;
      return matchesSearch && matchesStage;
    });
  }, [majorDecisions, searchTerm, filterStage]);

  const uniqueStages = useMemo(() => {
    return [...new Set(majorDecisions.map(d => d.stage))];
  }, [majorDecisions]);

  const renderDecisionsTab = () => (
    <div className="space-y-4">
      {/* Search and Filter Controls */}
      <div className="flex flex-col sm:flex-row gap-4 p-4 bg-black/40 rounded-lg border border-white/10">
        <div className="flex-1">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search decisions..."
              className="w-full pl-10 pr-4 py-2 bg-black/60 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-purple-500"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <Filter className="w-4 h-4 text-gray-400" />
          <select
            className="px-3 py-2 bg-black/60 border border-white/20 rounded-lg text-white focus:outline-none focus:border-purple-500"
            value={filterStage}
            onChange={(e) => setFilterStage(e.target.value)}
          >
            <option value="all">All Stages</option>
            {uniqueStages.map(stage => (
              <option key={stage} value={stage}>{stage}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Decisions Table */}
      <div className="bg-black/40 rounded-lg border border-white/10 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-black/60">
              {table.getHeaderGroups().map(headerGroup => (
                <tr key={headerGroup.id}>
                  {headerGroup.headers.map(header => (
                    <th
                      key={header.id}
                      className="px-4 py-3 text-left text-sm font-medium text-gray-300 cursor-pointer hover:text-white"
                      onClick={header.column.getToggleSortingHandler()}
                    >
                      {header.isPlaceholder ? null : (
                        <div className="flex items-center space-x-2">
                          {flexRender(header.column.columnDef.header, header.getContext())}
                          {{
                            asc: <ChevronLeft className="w-4 h-4" />,
                            desc: <ChevronRight className="w-4 h-4" />,
                          }[header.column.getIsSorted() as string] ?? null}
                        </div>
                      )}
                    </th>
                  ))}
                </tr>
              ))}
            </thead>
            <tbody>
              {table.getRowModel().rows.map((row) => (
                <tr key={row.id} className="hover:bg-white/5 transition-colors">
                  {row.getVisibleCells().map(cell => (
                    <td key={cell.id} className="px-4 py-3 border-t border-white/10">
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {filteredDecisions.length === 0 && (
        <div className="text-center py-8 text-gray-400">
          <History className="w-12 h-12 mx-auto mb-4 opacity-50" />
          <p>No decisions found matching your criteria</p>
        </div>
      )}
    </div>
  );

  const renderNPCsTab = () => (
    <div className="space-y-4">
      {/* NPC Relationship Graph */}
      <div className="bg-black/40 rounded-lg border border-white/10 p-4">
        <h3 className="text-lg font-bold text-white mb-4 flex items-center">
          <Users className="w-5 h-5 mr-2" />
          NPC Relationship Network
        </h3>
        <div className="h-64 bg-black/60 rounded-lg overflow-hidden">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            nodeTypes={nodeTypes}
            fitView
            className="bg-gray-900"
          >
            <Background />
            <Controls />
            <MiniMap nodeColor="#6366f1" />
          </ReactFlow>
        </div>
      </div>

      {/* NPC Status List */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {npcStatuses.map((npc) => (
          <div key={npc.id} className="bg-black/40 rounded-lg border border-white/10 p-4">
            <div className="flex items-start justify-between mb-3">
              <div>
                <h4 className="text-lg font-bold text-white">{npc.name}</h4>
                <p className="text-sm text-gray-400">{npc.location}</p>
              </div>
              <div className="flex flex-col items-end space-y-1">
                <span className={`px-2 py-1 text-xs rounded ${
                  npc.status === 'ally' ? 'bg-green-900/50 text-green-300' :
                  npc.status === 'hostile' ? 'bg-red-900/50 text-red-300' :
                  npc.status === 'dead' ? 'bg-gray-900/50 text-gray-300' :
                  'bg-gray-700/50 text-gray-300'
                }`}>
                  {npc.status}
                </span>
                <span className={`px-2 py-1 text-xs rounded ${
                  npc.health === 'healthy' ? 'bg-green-900/50 text-green-300' :
                  npc.health === 'injured' ? 'bg-yellow-900/50 text-yellow-300' :
                  npc.health === 'dying' ? 'bg-red-900/50 text-red-300' :
                  npc.health === 'dead' ? 'bg-gray-900/50 text-gray-300' :
                  'bg-gray-700/50 text-gray-300'
                }`}>
                  {npc.health}
                </span>
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-300">Relationship</span>
                <div className="flex items-center space-x-2">
                  <div className="w-20 bg-gray-700 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${
                        npc.relationship_strength > 0 ? 'bg-green-500' : 'bg-red-500'
                      }`}
                      style={{ width: `${Math.abs(npc.relationship_strength)}%` }}
                    />
                  </div>
                  <span className="text-xs text-gray-400">{npc.relationship_strength}</span>
                </div>
              </div>

              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-300">First Met</span>
                <span className="text-gray-400">{new Date(npc.first_met).toLocaleDateString()}</span>
              </div>

              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-300">Last Seen</span>
                <span className="text-gray-400">{new Date(npc.last_interaction).toLocaleDateString()}</span>
              </div>

              {npc.notes && (
                <div className="mt-3 p-2 bg-black/60 rounded border border-white/10">
                  <p className="text-sm text-gray-300">{npc.notes}</p>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {npcStatuses.length === 0 && (
        <div className="text-center py-8 text-gray-400">
          <Users className="w-12 h-12 mx-auto mb-4 opacity-50" />
          <p>No NPCs encountered yet</p>
        </div>
      )}
    </div>
  );

  const renderWorldTab = () => (
    <div className="space-y-4">
      {/* Current Status */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-black/40 rounded-lg border border-white/10 p-4">
          <h3 className="text-lg font-bold text-white mb-3 flex items-center">
            <MapPin className="w-5 h-5 mr-2" />
            Current Location
          </h3>
          <p className="text-2xl font-bold text-purple-300">{worldState.current_location}</p>
          <p className="text-sm text-gray-400 mt-2">
            Time Elapsed: {Math.floor(worldState.story_time_elapsed / 60)}h {worldState.story_time_elapsed % 60}m
          </p>
        </div>

        <div className="bg-black/40 rounded-lg border border-white/10 p-4">
          <h3 className="text-lg font-bold text-white mb-3 flex items-center">
            <Target className="w-5 h-5 mr-2" />
            Active Objectives
          </h3>
          <div className="space-y-2">
            {worldState.active_objectives.slice(0, 3).map((objective) => (
              <div key={objective.id} className="flex items-center space-x-2">
                <div className={`w-2 h-2 rounded-full ${
                  objective.priority === 'critical' ? 'bg-red-500' :
                  objective.priority === 'high' ? 'bg-orange-500' :
                  objective.priority === 'medium' ? 'bg-yellow-500' :
                  'bg-green-500'
                }`} />
                <span className="text-sm text-gray-300 flex-1">{objective.title}</span>
              </div>
            ))}
            {worldState.active_objectives.length > 3 && (
              <p className="text-xs text-gray-400">+{worldState.active_objectives.length - 3} more objectives</p>
            )}
          </div>
        </div>
      </div>

      {/* Explored Areas */}
      <div className="bg-black/40 rounded-lg border border-white/10 p-4">
        <h3 className="text-lg font-bold text-white mb-3 flex items-center">
          <Eye className="w-5 h-5 mr-2" />
          Explored Areas
        </h3>
        <div className="flex flex-wrap gap-2">
          {worldState.explored_areas.map((area, index) => (
            <span key={index} className="px-3 py-1 bg-blue-900/50 text-blue-300 text-sm rounded">
              {area}
            </span>
          ))}
        </div>
      </div>

      {/* Recent World Events */}
      <div className="bg-black/40 rounded-lg border border-white/10 p-4">
        <h3 className="text-lg font-bold text-white mb-3 flex items-center">
          <Zap className="w-5 h-5 mr-2" />
          Recent World Events
        </h3>
        <div className="space-y-3">
          {worldState.world_events.slice(0, 5).map((event) => (
            <div key={event.id} className="border-l-2 border-purple-500 pl-4">
              <div className="flex items-center justify-between mb-1">
                <h4 className="font-medium text-white">{event.title}</h4>
                <div className="flex items-center space-x-2">
                  <span className={`w-2 h-2 rounded-full ${
                    event.significance === 'critical' ? 'bg-red-500' :
                    event.significance === 'major' ? 'bg-orange-500' :
                    'bg-green-500'
                  }`} />
                  <span className="text-xs text-gray-400">
                    {new Date(event.timestamp).toLocaleDateString()}
                  </span>
                </div>
              </div>
              <p className="text-sm text-gray-300">{event.description}</p>
              <p className="text-xs text-gray-400 mt-1">{event.location}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Established Lore */}
      <div className="bg-black/40 rounded-lg border border-white/10 p-4">
        <h3 className="text-lg font-bold text-white mb-3 flex items-center">
          <Book className="w-5 h-5 mr-2" />
          Established Lore
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {Object.entries(worldState.established_lore).map(([key, value]) => (
            <div key={key} className="p-3 bg-black/60 rounded border border-white/10">
              <h4 className="font-medium text-purple-300 text-sm">
                {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </h4>
              <p className="text-sm text-gray-300 mt-1">{value}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  if (!isOpen) {
    return (
      <button
        onClick={onToggle}
        className={`fixed right-4 top-1/2 transform -translate-y-1/2 z-50 bg-purple-600 hover:bg-purple-700 text-white p-3 rounded-l-lg border border-white/20 transition-colors ${className}`}
        data-tooltip-id="narrative-toggle"
        data-tooltip-content="Open Narrative Context"
      >
        <ChevronLeft className="w-5 h-5" />
        <Tooltip id="narrative-toggle" />
      </button>
    );
  }

  return (
    <ProSidebarProvider>
      <div className={`fixed right-0 top-0 h-full z-40 ${className}`}>
        <Sidebar
          width="480px"
          backgroundColor="rgba(0, 0, 0, 0.95)"
          rootStyles={{
            border: '1px solid rgba(255, 255, 255, 0.1)',
            borderRight: 'none',
          }}
        >
          <div className="flex flex-col h-full">
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-white/10">
              <h2 className="text-xl font-bold text-white">Narrative Context</h2>
              <button
                onClick={onToggle}
                className="text-gray-400 hover:text-white transition-colors"
              >
                <ChevronRight className="w-5 h-5" />
              </button>
            </div>

            {/* Tab Navigation */}
            <div className="flex border-b border-white/10">
              {[
                { id: 'decisions', label: 'Decisions', icon: History },
                { id: 'npcs', label: 'NPCs', icon: Users },
                { id: 'world', label: 'World', icon: MapPin },
              ].map(({ id, label, icon: Icon }) => (
                <button
                  key={id}
                  onClick={() => setActiveTab(id as 'decisions' | 'npcs' | 'world')}
                  className={`flex-1 flex items-center justify-center space-x-2 py-3 px-4 transition-colors ${
                    activeTab === id
                      ? 'bg-purple-600/30 text-purple-300 border-b-2 border-purple-500'
                      : 'text-gray-400 hover:text-white hover:bg-white/5'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span className="text-sm font-medium">{label}</span>
                </button>
              ))}
            </div>

            {/* Content Area */}
            <div className="flex-1 overflow-y-auto p-4">
              {activeTab === 'decisions' && renderDecisionsTab()}
              {activeTab === 'npcs' && renderNPCsTab()}
              {activeTab === 'world' && renderWorldTab()}
            </div>
          </div>
        </Sidebar>

        {/* Tooltips */}
        {npcStatuses.map((npc) => (
          <Tooltip
            key={`npc-${npc.id}`}
            id={`npc-${npc.id}`}
            className="bg-black/90 text-white p-2 rounded border border-white/20"
          />
        ))}
      </div>
    </ProSidebarProvider>
  );
} 