from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic_settings import BaseSettings
import os

class DatabaseSettings(BaseSettings):
    """Database configuration settings"""
    database_url: str = os.getenv("DATABASE_URL", "postgresql://username:password@localhost/solorelms")
    echo: bool = False  # Set to True for SQL debugging
    
    class Config:
        env_file = ".env"

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