const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "API error");
  }
  return res.json();
}

export const api = {
  createSession: (body) => request("/sessions", { method: "POST", body: JSON.stringify(body) }),
  getSessions: (userId, days = 7) => request(`/sessions/${userId}?days=${days}`),
  generateDigest: (userId) => request("/digest/generate", { method: "POST", body: JSON.stringify({ user_id: userId }) }),
  getDigest: (userId) => request(`/digest/${userId}`),
  searchDrills: (query, sport, limit = 5) =>
    request(`/drills/search?query=${encodeURIComponent(query)}&sport=${sport || ""}&limit=${limit}`),
};
