"use client";

import { useLeafAnalysis } from "@/hooks/useLeafAnalysis";
import { PageHeader } from "@/components/PageHeader";
import { UploadPanel } from "@/components/UploadPanel";
import { ImageProcessingGrid } from "@/components/ImageProcessingGrid";
import { FeatureExtractionRow } from "@/components/FeatureExtractionRow";
import { ModelEvaluationSection } from "@/components/ModelEvaluationSection";
import { PageFooter } from "@/components/PageFooter";

export default function DashboardPage() {
  const { previewUrl, analyzing, result, error, analyze } = useLeafAnalysis();

  return (
    <main className="flex-1 space-y-8 p-6">
      {/* Dashboard */}
      <section id="dashboard" className="scroll-mt-24">
        <PageHeader />
      </section>

      {/* Analyze Leaf */}
      <section id="analyze" className="scroll-mt-24 space-y-4">
        <UploadPanel onAnalyze={analyze} analyzing={analyzing} />

        {error && (
          <p className="rounded-md border border-red-800 bg-red-950/40 px-4 py-2 text-sm text-red-300">
            {error}
          </p>
        )}

        <ImageProcessingGrid
          previewUrl={previewUrl}
          analyzing={analyzing}
          result={result}
        />

        <FeatureExtractionRow result={result} />
      </section>

      {/* Model Evaluation */}
      <section id="evaluation" className="scroll-mt-24">
        <ModelEvaluationSection />
      </section>

      {/* Dataset */}
      <section id="dataset" className="scroll-mt-24">
        <div className="rounded-xl bg-[var(--color-surface)] p-6">
          <h2 className="mb-2 text-xl font-semibold text-zinc-900">
            RoCoLe Dataset
          </h2>
          <p className="text-zinc-600">
            This project uses the RoCoLe coffee leaf dataset containing Healthy
            and Unhealthy coffee leaf images for training and evaluation.
          </p>
        </div>
      </section>

      {/* About */}
      <section id="about" className="scroll-mt-24">
        <PageFooter />
      </section>
    </main>
  );
}