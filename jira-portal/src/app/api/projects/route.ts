import { NextResponse } from 'next/server';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';

export async function GET() {
  try {
    const res = await fetch(`${API_URL}/api/projects`, {
      cache: 'no-store'
    });
    
    if (!res.ok) return NextResponse.json({}, { status: res.status });
    
    const data = await res.json();
    return NextResponse.json(data);
  } catch (error) {
    return NextResponse.json({ error: 'Backend Unreachable' }, { status: 503 });
  }
}
