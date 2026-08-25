import { useState, useEffect, useRef } from "react";
import { fetchQuery } from "../api/client";

export const LOADING_STEPS = [
  "Understanding your question",
  "Retrieving schema context",
  "Generating SQL",
  "Validating safe query",
  "Fetching HR data",
  "Generating answer",
];

export function useQuery() {
  const [question, setQuestion] = useState("");
  const [inputQuestion, setInputQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [stepIndex, setStepIndex] = useState(0);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const stepTimerRef = useRef(null);

  useEffect(() => {
    if (loading) {
      setStepIndex(0);
      stepTimerRef.current = setInterval(() => {
        setStepIndex((prev) => (prev < LOADING_STEPS.length - 1 ? prev + 1 : prev));
      }, 450);
    } else {
      if (stepTimerRef.current) clearInterval(stepTimerRef.current);
    }

    return () => {
      if (stepTimerRef.current) clearInterval(stepTimerRef.current);
    };
  }, [loading]);

  const submitQuery = async (queryText) => {
    const targetQ = queryText || inputQuestion;
    if (!targetQ || !targetQ.trim()) return;

    const trimmed = targetQ.trim();
    setQuestion(trimmed);
    setInputQuestion(trimmed);
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const responseData = await fetchQuery(trimmed);
      setResult(responseData);
    } catch (err) {
      setError(err.message || "An error occurred while processing your request.");
    } finally {
      setLoading(false);
    }
  };

  return {
    question,
    inputQuestion,
    setInputQuestion,
    loading,
    stepIndex,
    result,
    error,
    submitQuery,
  };
}
