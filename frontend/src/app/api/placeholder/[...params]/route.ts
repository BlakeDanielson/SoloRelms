import { NextRequest, NextResponse } from 'next/server';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ params: string[] }> }
) {
  try {
    const { params: pathParams } = await params;
    const [width, height] = pathParams;
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

    return new NextResponse(svg, {
      headers: {
        'Content-Type': 'image/svg+xml',
        'Cache-Control': 'public, max-age=31536000',
      },
    });

  } catch (error) {
    console.error('Placeholder image error:', error);
    
    // Return a basic fallback SVG
    const fallbackSvg = `
      <svg width="400" height="200" xmlns="http://www.w3.org/2000/svg">
        <rect width="100%" height="100%" fill="#cccccc"/>
        <text x="50%" y="50%" font-family="Arial, sans-serif" font-size="14" 
              fill="#666666" text-anchor="middle" dominant-baseline="central">
          Image Placeholder
        </text>
      </svg>
    `;

    return new NextResponse(fallbackSvg, {
      headers: {
        'Content-Type': 'image/svg+xml'
      }
    });
  }
} 