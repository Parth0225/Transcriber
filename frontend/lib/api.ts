const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function api<T = unknown>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`${res.status}: ${detail}`);
  }
  return res.status === 204 ? (undefined as T) : ((await res.json()) as T);
}
