"""
Text-to-Speech API endpoints using OpenAI TTS
"""
from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
from openai import OpenAI
import os
import logging
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/tts", tags=["text-to-speech"])

class TTSRequest(BaseModel):
    text: str
    voice: Optional[str] = "nova"  # alloy, echo, fable, nova, onyx, shimmer
    model: Optional[str] = "tts-1-hd"  # tts-1, tts-1-hd, or gpt-4o-mini-tts

@router.post("/generate")
async def generate_speech(request: TTSRequest):
    """
    Generate speech from text using OpenAI TTS
    """
    try:
        # Initialize OpenAI client
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        logger.info(f"🎤 Generating TTS for {len(request.text)} characters with voice: {request.voice}")
        
        # Generate speech
        response = client.audio.speech.create(
            model=request.model,
            voice=request.voice,
            input=request.text,
            response_format="mp3"
        )
        
        # Return audio as binary response
        audio_content = response.content
        
        logger.info(f"✅ TTS generated successfully, audio size: {len(audio_content)} bytes")
        
        return Response(
            content=audio_content,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "inline; filename=speech.mp3",
                "Access-Control-Allow-Origin": "*"
            }
        )
        
    except Exception as e:
        logger.error(f"❌ TTS generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"TTS generation failed: {str(e)}")

@router.get("/voices")
async def get_available_voices():
    """
    Get list of available TTS voices
    """
    return {
        "voices": [
            {"id": "alloy", "name": "Alloy", "description": "Neutral, clear voice"},
            {"id": "echo", "name": "Echo", "description": "Male voice"},
            {"id": "fable", "name": "Fable", "description": "British accent"},
            {"id": "nova", "name": "Nova", "description": "Female voice (recommended for DM)"},
            {"id": "onyx", "name": "Onyx", "description": "Deep male voice"},
            {"id": "shimmer", "name": "Shimmer", "description": "Soft female voice"}
        ],
        "models": [
            {"id": "tts-1", "name": "Standard", "description": "Faster, lower quality"},
            {"id": "tts-1-hd", "name": "HD", "description": "Higher quality, more realistic"},
            {"id": "gpt-4o-mini-tts", "name": "GPT-4o Mini TTS", "description": "Latest 2025 model, enhanced naturalness"}
        ]
    } 