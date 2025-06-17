'use client';

import { CheckCircle2, PlayCircle, Circle, Sparkles } from 'lucide-react';

// Types
interface StoryStageInfo {
  key: string;
  name: string;
  description: string;
  icon?: any;
}

interface StoryProgressTrackerProps {
  currentStage: string;
  stagesCompleted: string[];
  storyCompleted: boolean;
  compact?: boolean;
  className?: string;
}

// Story stages configuration
const STORY_STAGES: StoryStageInfo[] = [
  { 
    key: 'intro', 
    name: 'Introduction', 
    description: 'Setting the scene and meeting key characters',
    icon: Circle
  },
  { 
    key: 'inciting_incident', 
    name: 'Inciting Incident', 
    description: 'The event that starts the main adventure',
    icon: Sparkles
  },
  { 
    key: 'first_combat', 
    name: 'First Combat', 
    description: 'Initial challenge and combat encounter',
    icon: PlayCircle
  },
  { 
    key: 'twist', 
    name: 'Plot Twist', 
    description: 'Unexpected revelation or complication',
    icon: Sparkles
  },
  { 
    key: 'final_conflict', 
    name: 'Final Conflict', 
    description: 'Climactic battle or challenge',
    icon: PlayCircle
  },
  { 
    key: 'resolution', 
    name: 'Resolution', 
    description: 'Story conclusion and rewards',
    icon: CheckCircle2
  }
];

export default function StoryProgressTracker({
  currentStage,
  stagesCompleted = [],
  storyCompleted = false,
  compact = false,
  className = ''
}: StoryProgressTrackerProps) {
  
  // Helper functions
  const getCurrentStageIndex = () => {
    return STORY_STAGES.findIndex(stage => stage.key === currentStage);
  };

  const getProgressPercentage = () => {
    if (storyCompleted) return 100;
    const currentIndex = getCurrentStageIndex();
    return Math.round((currentIndex / STORY_STAGES.length) * 100);
  };

  const getStageStatus = (stage: StoryStageInfo, index: number) => {
    const isCompleted = stagesCompleted.includes(stage.key);
    const isCurrent = currentStage === stage.key;
    const isUpcoming = index > getCurrentStageIndex();

    return {
      isCompleted,
      isCurrent,
      isUpcoming,
      status: isCompleted ? 'completed' : isCurrent ? 'current' : 'upcoming'
    };
  };

  const getStageColors = (status: string) => {
    switch (status) {
      case 'completed':
        return {
          bg: 'bg-green-500',
          border: 'border-green-500/30',
          cardBg: 'bg-green-900/30',
          text: 'text-green-300',
          icon: 'text-white'
        };
      case 'current':
        return {
          bg: 'bg-blue-500',
          border: 'border-blue-500/30',
          cardBg: 'bg-blue-900/30',
          text: 'text-blue-300',
          icon: 'text-white'
        };
      default:
        return {
          bg: 'bg-gray-600',
          border: 'border-gray-600/30',
          cardBg: 'bg-gray-900/30',
          text: 'text-gray-300',
          icon: 'text-gray-400'
        };
    }
  };

  if (compact) {
    return (
      <div className={`bg-black/40 backdrop-blur-sm rounded-lg p-4 border border-white/10 ${className}`}>
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-lg font-bold text-white">Story Progress</h3>
          <span className="text-sm text-gray-300">{getProgressPercentage()}%</span>
        </div>
        
        {/* Compact Progress Bar */}
        <div className="w-full bg-gray-700 rounded-full h-2 mb-3">
          <div
            className="bg-gradient-to-r from-purple-500 to-blue-500 h-2 rounded-full transition-all duration-300"
            style={{ width: `${getProgressPercentage()}%` }}
          />
        </div>

        {/* Stage Pills */}
        <div className="flex flex-wrap gap-1">
          {STORY_STAGES.map((stage, index) => {
            const { status } = getStageStatus(stage, index);
            const colors = getStageColors(status);
            
            return (
              <div
                key={stage.key}
                className={`px-2 py-1 rounded text-xs font-medium ${colors.cardBg} ${colors.text} border ${colors.border}`}
                title={stage.description}
              >
                {stage.name}
              </div>
            );
          })}
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-black/40 backdrop-blur-sm rounded-lg p-6 border border-white/10 ${className}`}>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-white">Story Progress</h2>
        <div className="flex items-center space-x-2">
          {storyCompleted ? (
            <span className="flex items-center text-green-400">
              <CheckCircle2 className="w-5 h-5 mr-1" />
              Completed
            </span>
          ) : (
            <span className="flex items-center text-yellow-400">
              <PlayCircle className="w-5 h-5 mr-1" />
              In Progress
            </span>
          )}
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mb-6">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm text-gray-300">Overall Progress</span>
          <span className="text-sm text-gray-300">{getProgressPercentage()}%</span>
        </div>
        <div className="w-full bg-gray-700 rounded-full h-3">
          <div
            className="bg-gradient-to-r from-purple-500 to-blue-500 h-3 rounded-full transition-all duration-300"
            style={{ width: `${getProgressPercentage()}%` }}
          />
        </div>
      </div>

      {/* Story Stages */}
      <div className="space-y-3">
        {STORY_STAGES.map((stage, index) => {
          const { isCompleted, isCurrent, status } = getStageStatus(stage, index);
          const colors = getStageColors(status);
          const IconComponent = stage.icon;

          return (
            <div
              key={stage.key}
              className={`flex items-center p-4 rounded-lg border transition-all duration-200 ${colors.cardBg} ${colors.border}`}
            >
              {/* Stage Icon/Number */}
              <div className={`w-10 h-10 rounded-full flex items-center justify-center mr-4 ${colors.bg} transition-all duration-200`}>
                {isCompleted ? (
                  <CheckCircle2 className={`w-6 h-6 ${colors.icon}`} />
                ) : isCurrent ? (
                  <PlayCircle className={`w-6 h-6 ${colors.icon}`} />
                ) : (
                  <span className={`text-sm font-bold ${colors.icon}`}>{index + 1}</span>
                )}
              </div>

              {/* Stage Content */}
              <div className="flex-1">
                <h3 className={`text-lg font-bold mb-1 ${colors.text}`}>
                  {stage.name}
                </h3>
                <p className="text-gray-400 text-sm">{stage.description}</p>
                
                {/* Stage-specific indicators */}
                {isCurrent && (
                  <div className="mt-2">
                    <span className="inline-flex items-center px-2 py-1 bg-blue-500/20 text-blue-300 text-xs rounded-full">
                      <div className="w-2 h-2 bg-blue-400 rounded-full mr-1 animate-pulse" />
                      Current Stage
                    </span>
                  </div>
                )}
                
                {isCompleted && (
                  <div className="mt-2">
                    <span className="inline-flex items-center px-2 py-1 bg-green-500/20 text-green-300 text-xs rounded-full">
                      <CheckCircle2 className="w-3 h-3 mr-1" />
                      Completed
                    </span>
                  </div>
                )}
              </div>

              {/* Connection Line */}
              {index < STORY_STAGES.length - 1 && (
                <div className="absolute left-9 top-16 w-0.5 h-6 bg-gray-600" />
              )}
            </div>
          );
        })}
      </div>

      {/* Story Completion Status */}
      {storyCompleted && (
        <div className="mt-6 p-4 bg-green-900/30 border border-green-500/30 rounded-lg">
          <div className="flex items-center">
            <CheckCircle2 className="w-6 h-6 text-green-400 mr-3" />
            <div>
              <h3 className="text-lg font-bold text-green-300">Adventure Complete!</h3>
              <p className="text-green-400 text-sm">You have successfully completed this story arc.</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Export stage configuration for use in other components
export { STORY_STAGES };
export type { StoryStageInfo }; 