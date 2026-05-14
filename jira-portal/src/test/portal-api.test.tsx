import { describe, it, expect } from 'vitest';

describe('Portal API Routes', () => {
  const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8501';

  it('should return 200 for portal root', async () => {
    const res = await fetch(`${BASE_URL}/`);
    expect(res.status).toBe(200);
  });

  it('should return projects from API route', async () => {
    const res = await fetch(`${BASE_URL}/api/projects`);
    // Should return either data or 503 if API is unreachable
    expect([200, 503]).toContain(res.status);
    if (res.status === 200) {
      const data = await res.json();
      expect(typeof data).toBe('object');
    }
  });

  it('should check Ollama health', async () => {
    const res = await fetch(`${BASE_URL}/api/ollama/health`);
    expect([200, 503]).toContain(res.status);
  });

  it('should list reports', async () => {
    const res = await fetch(`${BASE_URL}/api/reports/list`);
    expect([200, 503]).toContain(res.status);
    if (res.status === 200) {
      const data = await res.json();
      expect(Array.isArray(data)).toBe(true);
    }
  });

  it('should generate report', async () => {
    const res = await fetch(`${BASE_URL}/api/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        project_key: 'IM',
        report_type: 'progress',
        use_ai: false
      })
    });
    expect([200, 503]).toContain(res.status);
    if (res.status === 200) {
      const data = await res.json();
      expect(data.status).toBe('success');
    }
  });
});
