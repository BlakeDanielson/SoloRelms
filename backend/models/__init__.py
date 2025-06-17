# Models package - Import all models for SQLAlchemy registration
from .user import User
from .character import Character
from .story import StoryArc, WorldState
from .combat import EnemyTemplate, CombatEncounter, CombatParticipant
from .quest import Quest, QuestObjective, QuestReward, CharacterQuest, QuestObjectiveProgress
from .journal import JournalEntry, Discovery, TimelineEvent

# Export all models for easy access
__all__ = [
    "User",
    "Character",
    "StoryArc", 
    "WorldState",
    "EnemyTemplate",
    "CombatEncounter", 
    "CombatParticipant",
    "Quest",
    "QuestObjective",
    "QuestReward", 
    "CharacterQuest",
    "QuestObjectiveProgress",
    "JournalEntry",
    "Discovery",
    "TimelineEvent"
] 