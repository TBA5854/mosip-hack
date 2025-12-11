import { describe, expect, it, beforeAll } from 'bun:test';
import { app } from '../src/app';

const BASE_URL = 'http://localhost:3000';

describe('Backend API', () => {
  let token: string;
  const testUser = {
    username: `testuser_${Date.now()}`,
    password: 'password123',
  };
  const testOCR = {
    imageHash: `hash_${Date.now()}`,
    ocrText: 'Detected Text',
    userEdits: 'Edited Text',
  };

  beforeAll(async () => {
    // Cleanup if needed, but using unique data is safer
  });

  it('should register a new user', async () => {
    const req = new Request(`${BASE_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(testUser),
    });
    const res = await app.handle(req);
    if (res.status !== 200) {
        console.log('Register Error:', await res.text());
    }
    expect(res.status).toBe(200);
    const body = await res.json();
    expect(body).toHaveProperty('id');
    expect(body).toHaveProperty('username', testUser.username);
  });

  it('should login the user', async () => {
    const req = new Request(`${BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(testUser),
    });
    const res = await app.handle(req);
    if (res.status !== 200) {
        console.log('Login Error:', await res.text());
    }
    expect(res.status).toBe(200);
    const body = await res.json();
    expect(body).toHaveProperty('token');
    token = body.token;
  });

  it('should save OCR data', async () => {
    const req = new Request(`${BASE_URL}/ocr/cache`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(testOCR),
    });
    const res = await app.handle(req);
    expect(res.status).toBe(200);
    const body = await res.json();
    expect(body).toHaveProperty('id');
    expect(body).toHaveProperty('ocrText', testOCR.ocrText);
  });

  it('should retrieve OCR data', async () => {
    const req = new Request(`${BASE_URL}/ocr/${testOCR.imageHash}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    const res = await app.handle(req);
    expect(res.status).toBe(200);
    const body = await res.json();
    expect(body).toHaveProperty('ocrText', testOCR.ocrText);
  });
});
