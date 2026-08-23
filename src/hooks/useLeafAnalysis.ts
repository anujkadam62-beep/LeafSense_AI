"use client";

import { useCallback, useState } from "react";
import { analyzeLeaf, AnalysisError } from "@/lib/api";
import type { AnalysisResult } from "@/lib/types";

export interface HistoryEntry extends AnalysisResult {
  id: string;
  fileName: string;
  timestamp: number;
}

export function useLeafAnalysis() {
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [history, setHistory] = useState<HistoryEntry[]>([]);

  const analyze = useCallback(async (file: File) => {
    setPreviewUrl((prev) => {
      if (prev) URL.revokeObjectURL(prev);
      return URL.createObjectURL(file);
    });
    setAnalyzing(true);
    setError(null);
    setResult(null);

    try {
      const data = await analyzeLeaf(file);
      setResult(data);
      setHistory((prev) => [
        { ...data, id: crypto.randomUUID(), fileName: file.name, timestamp: Date.now() },
        ...prev,
      ].slice(0, 8));
    } catch (err) {
      setError(err instanceof AnalysisError ? err.message : "Something went wrong. Is the backend running?");
    } finally {
      setAnalyzing(false);
    }
  }, []);

  const reset = useCallback(() => {
    setPreviewUrl((prev) => {
      if (prev) URL.revokeObjectURL(prev);
      return null;
    });
    setResult(null);
    setError(null);
  }, []);

  return { previewUrl, analyzing, result, error, history, analyze, reset };
}
