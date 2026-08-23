import { Palette, Shapes, Grid3x3, Waves, Leaf } from "lucide-react";
import type { AnalysisResult } from "@/lib/types";

interface FeatureExtractionRowProps {
  result: AnalysisResult | null;
}

const SAMPLE_ROWS = {
  color: [
    ["Mean Hue", "72.45"],
    ["Mean Saturation", "0.42"],
    ["Mean Value", "0.58"],
  ],
  shape: [
    ["Leaf Area (px)", "128,450"],
    ["Perimeter (px)", "1,892.33"],
    ["Aspect Ratio", "1.87"],
  ],
  texture: [
    ["Contrast", "0.312"],
    ["Correlation", "0.862"],
    ["Homogeneity", "0.754"],
  ],
  edge: [
    ["Edge Density", "0.163"],
    ["Total Edges", "8,745"],
    ["Mean Gradient", "0.287"],
  ],
  affected: [
    ["Affected (px)", "24,052"],
    ["Total Leaf (px)", "128,450"],
    ["Percentage", "18.72%"],
  ],
};

function fmt(n: number, decimals = 2): string {
  return n.toLocaleString(undefined, { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
}

export function FeatureExtractionRow({ result }: FeatureExtractionRowProps) {
  const rows = result
    ? {
        color: [
          ["Mean Hue", fmt(result.features.color.mean_hue)],
          ["Mean Saturation", fmt(result.features.color.mean_saturation)],
          ["Mean Value", fmt(result.features.color.mean_value)],
        ],
        shape: [
          ["Leaf Area (px)", result.features.shape.leaf_area.toLocaleString()],
          ["Perimeter (px)", fmt(result.features.shape.perimeter)],
          ["Aspect Ratio", fmt(result.features.shape.aspect_ratio)],
        ],
        texture: [
          ["Contrast", fmt(result.features.texture.contrast, 3)],
          ["Correlation", fmt(result.features.texture.correlation, 3)],
          ["Homogeneity", fmt(result.features.texture.homogeneity, 3)],
        ],
        edge: [
          ["Edge Density", fmt(result.features.edge.edge_density, 3)],
          ["Total Edges", result.features.edge.total_edges.toLocaleString()],
          ["Mean Gradient", fmt(result.features.edge.mean_gradient, 3)],
        ],
        affected: [
          ["Affected (px)", result.affected_area.pixels.toLocaleString()],
          ["Total Leaf (px)", result.affected_area.leaf_pixels.toLocaleString()],
          ["Percentage", `${result.affected_area.percentage}%`],
        ],
      }
    : SAMPLE_ROWS;

  const groups = [
    { icon: Palette, title: "Color Features", rows: rows.color },
    { icon: Shapes, title: "Shape Features", rows: rows.shape },
    { icon: Grid3x3, title: "Texture Features", rows: rows.texture },
    { icon: Waves, title: "Edge Features", rows: rows.edge },
    { icon: Leaf, title: "Affected Area", rows: rows.affected },
  ];

  return (
    <div id="features" className="rounded-xl bg-[var(--color-surface)] p-4">
      <p className="mb-4 text-sm font-medium text-zinc-900">
        Extracted Features {result ? "" : "(Sample — upload an image to compute real values)"}
      </p>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
        {groups.map((group) => (
          <div key={group.title} className="rounded-lg border border-[var(--color-border)] p-3.5">
            <div className="flex items-center gap-1.5 text-xs font-semibold text-zinc-700">
              <group.icon className="h-3.5 w-3.5 text-emerald-600" />
              {group.title}
            </div>
            <dl className="mt-2.5 space-y-1.5">
              {group.rows.map(([label, value]) => (
                <div key={label} className="flex items-center justify-between text-xs">
                  <dt className="text-zinc-400">{label}</dt>
                  <dd className="font-medium text-zinc-800">{value}</dd>
                </div>
              ))}
            </dl>
          </div>
        ))}
      </div>
    </div>
  );
}
