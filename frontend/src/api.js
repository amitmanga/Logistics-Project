const API_BASE = import.meta.env.VITE_API_BASE ?? "";

export async function fetchPlan(scenario, options = {}) {
  const response = await fetch(`${API_BASE}/api/plan`, {
    method: "POST",
    signal: options.signal,
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(scenario),
  });

  if (!response.ok) {
    throw new Error(`Plan request failed with ${response.status}`);
  }

  return response.json();
}
