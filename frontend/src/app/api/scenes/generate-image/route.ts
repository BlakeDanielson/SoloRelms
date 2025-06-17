import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { description } = body;

    // For now, return a placeholder response until backend image generation is properly set up
    const placeholderResponse = {
      success: true,
      imageUrl: `/api/placeholder/800/400?text=${encodeURIComponent(description || 'Scene Image')}&bg=4a5568`,
      description: description || 'Scene description',
      generatedAt: new Date().toISOString()
    };

    return NextResponse.json(placeholderResponse);
  } catch (error) {
    console.error('Image generation placeholder error:', error);
    return NextResponse.json(
      { 
        success: false, 
        error: 'Image generation temporarily unavailable',
        imageUrl: '/api/placeholder/800/400?text=Scene%20Image&bg=4a5568'
      },
      { status: 200 } // Return 200 with fallback instead of 501
    );
  }
} 