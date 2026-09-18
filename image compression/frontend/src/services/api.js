/**
 * API client for QuantumMedCompress FastAPI backend.
 */

const API_BASE = "";

export async function getDashboard() {
  const res = await fetch(`${API_BASE}/api/dashboard`);
  if (!res.ok) throw new Error("Failed to fetch dashboard data");
  return res.json();
}

export async function getModelInfo() {
  const res = await fetch(`${API_BASE}/api/model-info`);
  if (!res.ok) throw new Error("Failed to fetch model info");
  return res.json();
}

export async function uploadImage(file) {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_BASE}/api/upload`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || "Failed to upload image");
  }
  return res.json();
}

export async function compressImage(imageId, modelType = "HYBRID_QUANTUM") {
  const res = await fetch(`${API_BASE}/api/compress`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ image_id: imageId, model_type: modelType }),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || "Compression request failed");
  }
  return res.json();
}

export async function compareAll(imageId) {
  const res = await fetch(`${API_BASE}/api/compare-all`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ image_id: imageId, model_type: "ALL" }),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || "Comparison request failed");
  }
  return res.json();
}

export async function getResults(limit = 25) {
  const res = await fetch(`${API_BASE}/api/results?limit=${limit}`);
  if (!res.ok) throw new Error("Failed to fetch compression results");
  return res.json();
}

export async function getExperiments() {
  const res = await fetch(`${API_BASE}/api/experiments`);
  if (!res.ok) throw new Error("Failed to fetch experiments history");
  return res.json();
}

export async function getBenchmarkData() {
  const res = await fetch(`${API_BASE}/api/benchmark-data`);
  if (!res.ok) throw new Error("Failed to fetch benchmark data");
  return res.json();
}
