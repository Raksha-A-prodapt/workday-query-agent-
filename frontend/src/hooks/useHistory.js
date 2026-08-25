import { useState, useEffect } from "react";

const HISTORY_STORAGE_KEY = "workday_query_history";
const MAX_HISTORY_ITEMS = 10;

export function useHistory() {
  const [history, setHistory] = useState([]);

  useEffect(() => {
    try {
      const saved = localStorage.getItem(HISTORY_STORAGE_KEY);
      if (saved) {
        setHistory(JSON.parse(saved));
      }
    } catch (e) {
      console.warn("Failed to load history from localStorage:", e);
    }
  }, []);

  const addHistory = (question) => {
    if (!question || !question.trim()) return;
    const trimmed = question.trim();

    setHistory((prev) => {
      // Remove duplicate if already present
      const filtered = prev.filter((item) => item.toLowerCase() !== trimmed.toLowerCase());
      const updated = [trimmed, ...filtered].slice(0, MAX_HISTORY_ITEMS);
      try {
        localStorage.setItem(HISTORY_STORAGE_KEY, JSON.stringify(updated));
      } catch (e) {
        console.warn("Failed to save history to localStorage:", e);
      }
      return updated;
    });
  };

  const clearHistory = () => {
    setHistory([]);
    try {
      localStorage.removeItem(HISTORY_STORAGE_KEY);
    } catch (e) {
      console.warn("Failed to clear history from localStorage:", e);
    }
  };

  return {
    history,
    addHistory,
    clearHistory,
  };
}
