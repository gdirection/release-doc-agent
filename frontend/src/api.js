const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export async function getHealth() {
  const response = await fetch(`${API_BASE_URL}/api/health`);
  return parseJsonResponse(response);
}

export async function generateReleasePackage() {
  const response = await fetch(`${API_BASE_URL}/api/generate`, {
    method: "POST",
  });
  return parseJsonResponse(response);
}

export async function approveReleasePackage(releasePackage) {
  const response = await fetch(`${API_BASE_URL}/api/approve`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ release_package: releasePackage }),
  });
  return parseJsonResponse(response);
}

async function parseJsonResponse(response) {
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.detail ?? "Request failed");
  }
  return payload;
}
