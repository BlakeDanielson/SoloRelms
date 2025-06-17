from fastapi import APIRouter, Query, Response
from fastapi.responses import HTMLResponse
from typing import Optional
import io
import base64

router = APIRouter(prefix="/placeholder", tags=["placeholder"])

@router.get("/{width}/{height}")
async def generate_placeholder(
    width: int,
    height: int,
    text: Optional[str] = Query(None, description="Text to display on the image"),
    bg: Optional[str] = Query("CCCCCC", description="Background color in hex (without #)"),
    text_color: Optional[str] = Query("333333", description="Text color in hex (without #)")
):
    """
    Generate a simple SVG placeholder image with specified dimensions and text.
    """
    # Ensure reasonable limits
    width = min(max(width, 50), 2000)
    height = min(max(height, 50), 2000)
    
    # Clean up colors (remove # if present)
    bg = bg.replace('#', '')
    text_color = text_color.replace('#', '')
    
    # Default text if none provided
    if not text:
        text = f"{width}×{height}"
    
    # Calculate font size based on image dimensions
    font_size = min(width, height) // 10
    font_size = max(12, min(font_size, 48))  # Keep font size reasonable
    
    # Calculate text position (centered)
    text_x = width // 2
    text_y = height // 2 + font_size // 3
    
    # Generate SVG
    svg_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
    <rect width="100%" height="100%" fill="#{bg}"/>
    <text x="{text_x}" y="{text_y}" 
          font-family="Arial, sans-serif" 
          font-size="{font_size}px" 
          fill="#{text_color}" 
          text-anchor="middle" 
          dominant-baseline="middle">
        {text}
    </text>
</svg>"""
    
    return Response(
        content=svg_content,
        media_type="image/svg+xml",
        headers={
            "Cache-Control": "public, max-age=31536000",  # Cache for 1 year
            "Content-Disposition": f"inline; filename=\"placeholder_{width}x{height}.svg\""
        }
    )

@router.get("/")
async def placeholder_info():
    """
    Information about the placeholder image service
    """
    return {
        "service": "Placeholder Image Generator",
        "usage": "/api/placeholder/{width}/{height}",
        "parameters": {
            "text": "Optional text to display (default: dimensions)",
            "bg": "Background color in hex without # (default: CCCCCC)",
            "text_color": "Text color in hex without # (default: 333333)"
        },
        "examples": [
            "/api/placeholder/600/300",
            "/api/placeholder/400/200?text=Hello+World",
            "/api/placeholder/600/300?text=Combat+Scene&bg=8B0000&text_color=FFFFFF"
        ]
    } 