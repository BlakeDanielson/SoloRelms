import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import get_db, engine
from models.character import Character
from api.users import router as users_router
from api.webhooks import router as webhooks_router
from api.stories import router as stories_router
from api.characters import router as characters_router
from api.dice import router as dice_router
from api.combat import router as combat_router
from api.ai import router as ai_router
from api.redis_state import router as redis_router
from api.response_parsing import router as parsing_router
from api.game_orchestration import router as orchestration_router
from api.scenes import router as scenes_router
from api.placeholder import router as placeholder_router
from api.websocket import router as websocket_router
from api.games import router as games_router
from api.feedback import router as feedback_router
from api.adventures import router as adventures_router
from api.character_progression import router as character_progression_router
from api.quests import router as quests_router
from api.journal import router as journal_router
from api.tts import router as tts_router
import sqlalchemy

app = FastAPI(
    title="SoloRealms Backend",
    description="AI-powered solo D&D game backend with authentication",
    version="1.0.0"
)

# Add CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://localhost:3001",
        "http://localhost:3002",  # Add the actual frontend port
        "http://localhost:3003",  # Add the new frontend port
        "ws://localhost:3003"     # Add WebSocket support
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(users_router, prefix="/api")
app.include_router(webhooks_router, prefix="/api")
app.include_router(stories_router, prefix="/api")
app.include_router(characters_router, prefix="/api")
app.include_router(dice_router)
app.include_router(combat_router)
app.include_router(ai_router, prefix="/api")
app.include_router(redis_router, prefix="/api")
app.include_router(parsing_router, prefix="/api")
app.include_router(orchestration_router, prefix="/api")
app.include_router(scenes_router, prefix="/api")
app.include_router(placeholder_router, prefix="/api")
app.include_router(websocket_router)  # WebSocket doesn't need /api prefix
app.include_router(games_router, prefix="/api")
app.include_router(feedback_router, prefix="/api")  # Add feedback collection system
app.include_router(adventures_router, prefix="/api/adventures", tags=["adventures"])
app.include_router(character_progression_router, prefix="/api/character-progression", tags=["character-progression"])
app.include_router(quests_router, prefix="/api", tags=["quests"])
app.include_router(journal_router, prefix="/api", tags=["journal"])
app.include_router(tts_router)

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Hello from SoloRealms Backend"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "SoloRealms Backend"}

@app.get("/health/database")
async def database_health_check(db: Session = Depends(get_db)):
    """Database health check endpoint"""
    try:
        # Test database connection
        result = db.execute(sqlalchemy.text("SELECT 1"))
        result.fetchone()
        
        # Test model queries
        character_count = db.query(Character).count()
        
        return {
            "status": "healthy",
            "database": "connected",
            "character_count": character_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database health check failed: {str(e)}")

@app.get("/api/test-auth")
async def test_auth_endpoint():
    """Test endpoint to verify API structure"""
    return {"message": "Authentication API is ready"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 