from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db, engine
from models.character import Character
import sqlalchemy

app = FastAPI(
    title="SoloRealms Backend",
    description="AI-powered solo D&D game backend",
    version="1.0.0"
)

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
        
        # Test model query
        character_count = db.query(Character).count()
        
        return {
            "status": "healthy",
            "database": "connected",
            "character_count": character_count
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database connection failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 