"""
Database models for quest system including quests, objectives, rewards, and character quest tracking.
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from database import Base


class QuestType(str, Enum):
    """Valid quest types."""
    main = "main"
    side = "side"
    daily = "daily"
    hidden = "hidden"


class DifficultyLevel(str, Enum):
    """Valid difficulty levels."""
    easy = "easy"
    medium = "medium"
    hard = "hard"
    legendary = "legendary"


class ObjectiveType(str, Enum):
    """Valid objective types."""
    kill = "kill"
    collect = "collect"
    visit = "visit"
    talk = "talk"
    deliver = "deliver"
    explore = "explore"
    survive = "survive"


class RewardType(str, Enum):
    """Valid reward types."""
    xp = "xp"
    gold = "gold"
    item = "item"
    ability = "ability"


class QuestStatus(str, Enum):
    """Valid quest status values."""
    active = "active"
    completed = "completed"
    failed = "failed"
    abandoned = "abandoned"


class Quest(Base):
    """Quest model for managing quests and their basic information."""
    __tablename__ = "quests"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    quest_type = Column(SQLEnum(QuestType), nullable=False)
    difficulty_level = Column(SQLEnum(DifficultyLevel), nullable=False)
    required_level = Column(Integer, default=1, nullable=False)
    time_limit_hours = Column(Integer, nullable=True)  # NULL means no time limit
    prerequisite_quest_ids = Column(JSON, default=list)  # List of quest IDs
    location = Column(String(255), nullable=True)
    giver_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_repeatable = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    objectives = relationship("QuestObjective", back_populates="quest", cascade="all, delete-orphan")
    rewards = relationship("QuestReward", back_populates="quest", cascade="all, delete-orphan")
    character_quests = relationship("CharacterQuest", back_populates="quest", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Quest(id={self.id}, title='{self.title}', type='{self.quest_type}')>"


class QuestObjective(Base):
    """Quest objective model for tracking individual quest goals."""
    __tablename__ = "quest_objectives"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(Text, nullable=False)
    objective_type = Column(SQLEnum(ObjectiveType), nullable=False)
    target_type = Column(String(100), nullable=True)  # e.g., "monster", "item", "location"
    target_id = Column(String(100), nullable=True)  # ID or name of target
    required_amount = Column(Integer, default=1, nullable=False)
    order_index = Column(Integer, default=0, nullable=False)  # Order in quest
    
    # Relationships
    quest_id = Column(Integer, ForeignKey("quests.id"), nullable=False)
    quest = relationship("Quest", back_populates="objectives")
    progress = relationship("QuestObjectiveProgress", back_populates="objective", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<QuestObjective(id={self.id}, type='{self.objective_type}', target='{self.target_type}')>"


class QuestReward(Base):
    """Quest reward model for tracking quest rewards."""
    __tablename__ = "quest_rewards"

    id = Column(Integer, primary_key=True, index=True)
    reward_type = Column(SQLEnum(RewardType), nullable=False)
    reward_id = Column(String(100), nullable=True)  # Item ID, ability ID, etc.
    amount = Column(Integer, default=1, nullable=False)
    rarity = Column(String(50), default="common", nullable=False)
    
    # Relationships
    quest_id = Column(Integer, ForeignKey("quests.id"), nullable=False)
    quest = relationship("Quest", back_populates="rewards")

    def __repr__(self):
        return f"<QuestReward(id={self.id}, type='{self.reward_type}', amount={self.amount})>"


class CharacterQuest(Base):
    """Character quest model for tracking quest assignments and progress."""
    __tablename__ = "character_quests"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(SQLEnum(QuestStatus), default=QuestStatus.active, nullable=False)
    accepted_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    
    # Relationships
    character_id = Column(Integer, ForeignKey("characters.id"), nullable=False)
    quest_id = Column(Integer, ForeignKey("quests.id"), nullable=False)
    
    character = relationship("Character", back_populates="character_quests")
    quest = relationship("Quest", back_populates="character_quests")
    objective_progress = relationship("QuestObjectiveProgress", back_populates="character_quest", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<CharacterQuest(id={self.id}, character_id={self.character_id}, quest_id={self.quest_id}, status='{self.status}')>"


class QuestObjectiveProgress(Base):
    """Quest objective progress model for tracking individual objective completion."""
    __tablename__ = "quest_objective_progress"

    id = Column(Integer, primary_key=True, index=True)
    current_amount = Column(Integer, default=0, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    character_quest_id = Column(Integer, ForeignKey("character_quests.id"), nullable=False)
    objective_id = Column(Integer, ForeignKey("quest_objectives.id"), nullable=False)
    
    character_quest = relationship("CharacterQuest", back_populates="objective_progress")
    objective = relationship("QuestObjective", back_populates="progress")

    def __repr__(self):
        return f"<QuestObjectiveProgress(id={self.id}, current={self.current_amount}, objective_id={self.objective_id})>" 