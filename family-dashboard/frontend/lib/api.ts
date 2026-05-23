// API client. Uses NEXT_PUBLIC_API_BASE; default to /api (Caddy reverse-proxies).
const BASE = process.env.NEXT_PUBLIC_API_BASE || "/api";

async function request(method: string, path: string, body?: any) {
  const res = await fetch(`${BASE}${path}`, {
    method,
    headers: body ? { "Content-Type": "application/json" } : undefined,
    body: body ? JSON.stringify(body) : undefined,
    cache: "no-store",
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${method} ${path} -> ${res.status}: ${text}`);
  }
  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  get: (p: string) => request("GET", p),
  post: (p: string, b: any) => request("POST", p, b),
  patch: (p: string, b: any) => request("PATCH", p, b),
  delete: (p: string) => request("DELETE", p),
};
