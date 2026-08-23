"use client";

import { useCallback, useEffect, useState } from "react";
import { evaluateModel, fetchLatestEvaluation, EvaluationError } from "@/lib/api";
import type { EvaluationResult } from "@/lib/types";

export function useModelEvaluation() {
  const [result, setResult] = useState<EvaluationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [checkingCache, setCheckingCache] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // On mount, show the last real run (if the backend has one cached)
  // instead of starting from nothing every page load.
  useEffect(() => {
    let cancelled = false;

    fetchLatestEvaluation()
      .then((cached) => {
        if (!cancelled && cached) setResult(cached);
      })
      .finally(() => {
        if (!cancelled) setCheckingCache(false);
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const evaluate = useCallback(async (file: File) => {
    setLoading(true);
    setError(null);

    try {
      const data = await evaluateModel(file);
      setResult(data);
    } catch (err) {
      setError(
        err instanceof EvaluationError
          ? err.message
          : "Evaluation failed. Is the backend running?"
      );
    } finally {
      setLoading(false);
    }
  }, []);

  return { result, loading, checkingCache, error, evaluate };
}
