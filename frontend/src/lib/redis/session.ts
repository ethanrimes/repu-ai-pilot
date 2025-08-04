// src/lib/redis/session.ts
// Path: src/lib/redis/session.ts

import { Redis } from '@upstash/redis';

const redis = new Redis({
  url: process.env.UPSTASH_REDIS_REST_URL!,
  token: process.env.UPSTASH_REDIS_REST_TOKEN!,
});

export async function createSession(userId: string, data: any) {
  const sessionId = `session:${userId}:${Date.now()}`;
  await redis.setex(sessionId, 3600, JSON.stringify(data)); // 1 hour TTL
  return sessionId;
}

export async function getSession(sessionId: string) {
  const data = await redis.get(sessionId);
  return data ? JSON.parse(data as string) : null;
}

export async function updateSession(sessionId: string, data: any) {
  const ttl = await redis.ttl(sessionId);
  if (ttl > 0) {
    await redis.setex(sessionId, ttl, JSON.stringify(data));
  }
}