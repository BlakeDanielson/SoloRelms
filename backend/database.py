from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
import os

class DatabaseSettings(BaseSettings):
    """Database configuration settings"""
    model_config = ConfigDict(
        env_file="../.env",  # Load from project root
        extra="ignore",  # Ignore extra fields from .env file
        env_file_encoding="utf-8"
    )
    
    database_url: str = "sqlite:///./solorelms.db"
    echo: bool = False  # Set to True for SQL debugging
    
    def __init__(self, **kwargs):
        # Override with environment variable if available
        database_url = os.getenv("DATABASE_URL")
        if database_url:
            kwargs["database_url"] = database_url
        super().__init__(**kwargs)

# Create settings instance
settings = DatabaseSettings()

# Create SQLAlchemy engine
engine = create_engine(
    settings.database_url,
    echo=settings.echo,
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=3600    # Recycle connections every hour
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for declarative models
Base = declarative_base()

# Dependency to get DB session
def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 