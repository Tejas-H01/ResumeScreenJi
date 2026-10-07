const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";

export async function recommendUploadedResume({ file, jobText, experienceYears, education, certifications, projectsCount }) {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("job_text", jobText);
  if (experienceYears !== "") formData.append("experience_years", String(experienceYears));
  formData.append("education", education || "");
  formData.append("certifications", certifications || "");
  formData.append("projects_count", String(projectsCount || 0));

  let response;
  try {
    response = await fetch(`${API_BASE}/api/recommend-upload`, {
      method: "POST",
      body: formData,
    });
  } catch (error) {
    throw new Error(`Could not reach FastAPI backend at ${API_BASE}. Make sure the backend server is running.`);
  }

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    throw new Error(errorBody.detail || `Request failed with status ${response.status}`);
  }

  return response.json();
}

export async function checkHealth() {
  const response = await fetch(`${API_BASE}/health`);
  if (!response.ok) return false;
  const body = await response.json();
  return body.status === "ok";
}

export async function exportRankings(rankings) {
  let response;
  try {
    response = await fetch(`${API_BASE}/api/export-rankings`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ rankings }),
    });
  } catch (error) {
    throw new Error(`Could not reach FastAPI backend at ${API_BASE}. Make sure the backend server is running.`);
  }

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    throw new Error(errorBody.detail || `Export failed with status ${response.status}`);
  }

  return response.json();
}

export async function submitFeedback(feedback) {
  let response;
  try {
    response = await fetch(`${API_BASE}/api/feedback`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(feedback),
    });
  } catch (error) {
    throw new Error(`Could not reach FastAPI backend at ${API_BASE}. Make sure the backend server is running.`);
  }

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    throw new Error(errorBody.detail || `Feedback failed with status ${response.status}`);
  }

  return response.json();
}

export async function getModelStatus() {
  const response = await fetch(`${API_BASE}/api/model-status`);
  if (!response.ok) {
    throw new Error(`Model status failed with status ${response.status}`);
  }
  return response.json();
}

export async function createModelVersion(reason = "manual_snapshot") {
  const response = await fetch(`${API_BASE}/api/create-model-version`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ reason }),
  });
  if (!response.ok) {
    throw new Error(`Model versioning failed with status ${response.status}`);
  }
  return response.json();
}

export async function retrainModels() {
  const response = await fetch(`${API_BASE}/api/retrain`, { method: "POST" });
  if (!response.ok) {
    throw new Error(`Retraining failed with status ${response.status}`);
  }
  return response.json();
}
