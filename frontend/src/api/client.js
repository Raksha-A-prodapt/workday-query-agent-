/**
 * API Client for Workday HR Analytics Backend.
 * Connects to http://localhost:8000/query.
 */

const API_BASE_URL = "http://localhost:8000";

export async function fetchQuery(question) {
  if (!question || !question.trim()) {
    throw new Error("Question cannot be empty.");
  }

  try {
    const response = await fetch(`${API_BASE_URL}/query`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ question: question.trim() }),
    });

    const data = await response.json();

    if (!response.ok) {
      const errorMsg = data.detail || `Server returned error status ${response.status}`;
      throw new Error(errorMsg);
    }

    return data;
  } catch (err) {
    if (err.message && err.message.includes("Failed to fetch")) {
      throw new Error("Unable to connect to the backend server. Please verify FastAPI is running at http://localhost:8000.");
    }
    throw err;
  }
}
