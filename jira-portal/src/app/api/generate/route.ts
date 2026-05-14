import { NextResponse } from 'next/server';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const res = await fetch(`${API_URL}/api/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    
    if (!res.ok) return NextResponse.json({ error: 'Generation failed' }, { status: res.status });
    
    const data = await res.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Bridge Generation Error:', error);
    return NextResponse.json({ error: 'Backend Unreachable' }, { status: 503 });
  }
}
