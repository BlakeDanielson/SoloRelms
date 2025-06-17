from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
try:
    from ..database import Base
except ImportError:
    # Fallback for when running from alembic or direct execution
    from database import Base

class User(Base):
    __tablename__ = "users"
    
    # Use Clerk user ID as primary key for easy lookups
    id = Column(String, primary_key=True, index=True)  # Clerk user ID (e.g., "user_2ABC...")
    
    # Profile information from Clerk
    email = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    username = Column(String, unique=True, index=True, nullable=True)
    image_url = Column(String, nullable=True)
    
    # Account status
    is_active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Game-specific data
    total_characters = Column(Integer, default=0)
    total_adventures = Column(Integer, default=0)
    total_playtime_minutes = Column(Integer, default=0)
    total_xp_earned = Column(Integer, default=0)
    
    # User preferences (stored as JSON-like text for flexibility)
    preferences = Column(Text, nullable=True)  # JSON string for user settings
    
    # Relationships to game entities
    characters = relationship("Character", back_populates="user", cascade="all, delete-orphan")
    story_arcs = relationship("StoryArc", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id='{self.id}', email='{self.email}', username='{self.username}')>"
    
    @property
    def display_name(self):
        """Get the best available display name for the user"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.username:
            return self.username
        else:
            return self.email.split("@")[0]
    
    @property
    def full_name(self):
        """Get the full name if available"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return None
    
    def to_dict(self):
        """Convert user to dictionary for API responses"""
        return {
            "id": self.id,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "username": self.username,
            "image_url": self.image_url,
            "display_name": self.display_name,
            "full_name": self.full_name,
            "is_active": self.is_active,
            "email_verified": self.email_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "stats": {
                "total_characters": self.total_characters,
                "total_adventures": self.total_adventures,
                "total_playtime_minutes": self.total_playtime_minutes,
                "total_xp_earned": self.total_xp_earned
            }
        } 