import { NextRequest, NextResponse } from 'next/server';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ params: string[] }> }
) {
  try {
    const resolvedParams = await params;
    const [width, height] = resolvedParams.params;
    const { searchParams } = new URL(request.url);
    const text = searchParams.get('text') || 'Placeholder';
    const bg = searchParams.get('bg') || '888888';
    
    // Create a simple SVG placeholder
    const svg = `
      <svg width="${width}" height="${height}" xmlns="http://www.w3.org/2000/svg">
        <rect width="100%" height="100%" fill="#${bg}" />
        <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" 
              fill="white" font-family="Arial, sans-serif" font-size="16">
          ${text}
        </text>
      </svg>
    `.trim();

    return new Response(svg, {
      headers: {
        'Content-Type': 'image/svg+xml',
        'Cache-Control': 'public, max-age=31536000',
      },
    });

  } catch (error) {
    console.error('Error generating placeholder:', error);
    return NextResponse.json(
      { error: 'Failed to generate placeholder image' },
      { status: 500 }
    );
  }
} 