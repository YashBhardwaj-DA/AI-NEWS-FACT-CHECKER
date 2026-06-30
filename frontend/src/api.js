const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export async function fetchFeed() {
  const res = await fetch(`${API_BASE}/feed`);
  if (!res.ok) throw new Error("Failed to load feed");
  return res.json();
}

export async function checkClaim(claim) {
  const res = await fetch(`${API_BASE}/check`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ claim }),
  });
  if (!res.ok) throw new Error("Failed to check claim");
  return res.json();
}
