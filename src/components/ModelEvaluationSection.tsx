"use client";

import { useCallback, useRef } from "react";
import { BarChart3, Upload, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { useModelEvaluation } from "@/hooks/useModelEvaluation";

export function ModelEvaluationSection() {
  const { result, loading, checkingCache, error, evaluate } =
    useModelEvaluation();

  const inputRef = useRef<HTMLInputElement>(null);

  const onFileChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];

      if (file) evaluate(file);

      e.target.value = "";
    },
    [evaluate]
  );

  return (
    <div
      id="evaluation"
      className="grid grid-cols-1 gap-4 lg:grid-cols-[1.4fr_1fr]"
    >
      {/* Left Panel */}
      <div className="rounded-xl bg-[var(--color-surface)] p-4">
        <div className="mb-3 flex items-center justify-between gap-2">
          <div className="flex items-center gap-1.5 text-sm font-medium text-zinc-900">
            <BarChart3 className="h-4 w-4 text-emerald-600" />
            Model Evaluation
          </div>

          <div className="flex items-center gap-2">
            <input
              ref={inputRef}
              type="file"
              accept=".zip"
              className="hidden"
              onChange={onFileChange}
            />

            <button
              onClick={() => inputRef.current?.click()}
              disabled={loading}
              className="flex items-center gap-1.5 rounded-md border border-[var(--color-border)] px-3 py-1.5 text-xs font-medium text-zinc-700 transition hover:bg-zinc-50 disabled:opacity-60"
            >
              {loading ? (
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
              ) : (
                <Upload className="h-3.5 w-3.5" />
              )}

              {loading ? "Evaluating..." : "Upload validation set (.zip)"}
            </button>
          </div>
        </div>

        {/* Loading cached evaluation */}
        {checkingCache && (
          <div className="flex min-h-[160px] items-center justify-center gap-2 text-sm text-zinc-500">
            <Loader2 className="h-5 w-5 animate-spin text-emerald-600" />
            Loading latest evaluation...
          </div>
        )}

        {/* Error */}
        {!checkingCache && error && (
          <p className="mb-3 rounded-md bg-red-50 px-3 py-2 text-xs text-red-700">
            {error}
          </p>
        )}

        {/* Empty state */}
        {!checkingCache && !result && !error && (
          <div className="flex min-h-[160px] flex-col items-center justify-center gap-1 rounded-lg border border-dashed border-[var(--color-border)] text-center text-xs text-zinc-400">
            <p>No evaluation has been run yet.</p>
            <p>
              Upload a <code>.zip</code> with one labeled subfolder per class
              (for example <code>Healthy/</code> and{" "}
              <code>Unhealthy/</code>) to compute real metrics from the loaded
              model.
            </p>
          </div>
        )}

        {/* Results */}
        {!checkingCache && result && (
          <>
            <p className="mb-3 text-xs text-zinc-500">
              {result.model} —{" "}
              {result.dataset.total_images_evaluated.toLocaleString()} images
              evaluated
              {result.dataset.skipped_unreadable > 0 &&
                ` • ${result.dataset.skipped_unreadable} skipped`}
            </p>

            {/* Overall Metrics */}
            <div className="mb-4 grid grid-cols-2 gap-3 lg:grid-cols-4">
              <MetricCard
                label="Accuracy"
                value={`${(result.accuracy * 100).toFixed(2)}%`}
              />
              <MetricCard
                label="Precision"
                value={result.precision.toFixed(3)}
              />
              <MetricCard label="Recall" value={result.recall.toFixed(3)} />
              <MetricCard label="F1 Score" value={result.f1.toFixed(3)} />
            </div>

            {/* Per-class table */}
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-[var(--color-border)] text-left text-xs text-zinc-400">
                    <th className="py-2 font-medium">Class</th>
                    <th className="py-2 font-medium">Precision</th>
                    <th className="py-2 font-medium">Recall</th>
                    <th className="py-2 font-medium">F1</th>
                    <th className="py-2 font-medium">Support</th>
                  </tr>
                </thead>

                <tbody>
                  {result.per_class.map((c) => (
                    <tr
                      key={c.class_name}
                      className="border-b border-[var(--color-border)] last:border-0"
                    >
                      <td className="py-2.5 font-medium text-zinc-800">
                        {c.class_name}
                      </td>
                      <td className="py-2.5 text-zinc-600">
                        {c.precision.toFixed(3)}
                      </td>
                      <td className="py-2.5 text-zinc-600">
                        {c.recall.toFixed(3)}
                      </td>
                      <td className="py-2.5 text-zinc-600">
                        {c.f1.toFixed(3)}
                      </td>
                      <td className="py-2.5 text-zinc-600">{c.support}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Dataset summary */}
            <div className="mt-4 rounded-lg border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-900">
              <p>
                <strong>Total images:</strong>{" "}
                {result.dataset.total_images_evaluated}
              </p>

              <p>
                <strong>Processing time:</strong>{" "}
                {result.processing_time_ms.toLocaleString()} ms
              </p>

              <p>
                <strong>Unreadable skipped:</strong>{" "}
                {result.dataset.skipped_unreadable}
              </p>
            </div>
          </>
        )}
      </div>

      {/* Right Panel */}
      <div className="rounded-xl bg-[var(--color-surface)] p-4">
        <p className="mb-3 text-sm font-medium text-zinc-900">
          Confusion Matrix
        </p>

        {checkingCache ? (
          <div className="flex min-h-[220px] items-center justify-center text-zinc-400">
            <Loader2 className="h-6 w-6 animate-spin text-emerald-600" />
          </div>
        ) : result ? (
          <img
            src={`data:image/png;base64,${result.confusion_matrix_image}`}
            alt="Confusion Matrix"
            className="w-full rounded-lg border border-zinc-200"
          />
        ) : (
          <div
            className={cn(
              "flex min-h-[220px] items-center justify-center rounded-lg border border-dashed border-[var(--color-border)] text-center text-xs text-zinc-400"
            )}
          >
            Run an evaluation to see a real confusion matrix.
          </div>
        )}
      </div>
    </div>
  );
}

function MetricCard({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-lg border border-zinc-200 bg-zinc-50 p-3">
      <p className="text-xs text-zinc-500">{label}</p>
      <p className="mt-1 text-lg font-semibold text-zinc-900">{value}</p>
    </div>
  );
}