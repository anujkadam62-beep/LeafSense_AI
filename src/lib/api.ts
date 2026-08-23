import type { AnalysisResult, EvaluationResult } from "./types";

const API_BASE_URL = "/api";

export class AnalysisError extends Error {}
export class EvaluationError extends Error {}

async function parseErrorMessage(res: Response, fallback: string): Promise<string> {
  const body = await res.json().catch(() => null);
  return body?.detail ?? body?.error ?? fallback;
}

/**
 * Uploads an image to the backend's /analyze endpoint and returns the
 * parsed prediction. Throws AnalysisError with the server's message on
 * a non-2xx response (invalid image, missing model weights, etc).
 */
export async function analyzeLeaf(file: File): Promise<AnalysisResult> {
  const form = new FormData();
  form.append("file", file);

  const res = await fetch(`${API_BASE_URL}/analyze`, {
    method: "POST",
    body: form,
  });

  if (!res.ok) {
    throw new AnalysisError(await parseErrorMessage(res, `Request failed (${res.status})`));
  }

  return res.json();
}

/**
 * Uploads a labeled validation set (.zip, one subfolder per class) and
 * returns real accuracy/precision/recall/F1 + a confusion matrix
 * computed by running the loaded model over it.
 */
export async function evaluateModel(file: File): Promise<EvaluationResult> {
  const form = new FormData();
  form.append("file", file);

  const res = await fetch(`${API_BASE_URL}/evaluate`, {
    method: "POST",
    body: form,
  });

  if (!res.ok) {
    throw new EvaluationError(await parseErrorMessage(res, `Request failed (${res.status})`));
  }

  return res.json();
}

/**
 * Fetches the most recently cached evaluation result, if any evaluation
 * has ever been run against this backend.
 */
export async function fetchLatestEvaluation(): Promise<EvaluationResult | null> {
  const res = await fetch(`${API_BASE_URL}/evaluate/latest`);

  if (!res.ok) {
    return null;
  }

  const body = await res.json().catch(() => null);
  return body?.result ?? null;
}
