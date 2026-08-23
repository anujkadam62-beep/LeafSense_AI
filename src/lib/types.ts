export type Severity = "None" | "Low" | "Moderate" | "High";

export interface AffectedArea {
  pixels: number;
  leaf_pixels: number;
  percentage: number;
}

export interface ColorFeatures {
  mean_hue: number;
  mean_saturation: number;
  mean_value: number;
}

export interface ShapeFeatures {
  leaf_area: number;
  perimeter: number;
  aspect_ratio: number;
}

export interface TextureFeatures {
  contrast: number;
  correlation: number;
  homogeneity: number;
}

export interface EdgeFeatures {
  edge_density: number;
  total_edges: number;
  mean_gradient: number;
}

export interface ExtractedFeatures {
  color: ColorFeatures;
  shape: ShapeFeatures;
  texture: TextureFeatures;
  edge: EdgeFeatures;
}

export interface AnalysisImages {
  /** Base64-encoded PNG (no data: prefix) of the segmented leaf. */
  segmented: string;
  /** Base64-encoded PNG (no data: prefix) with the affected region highlighted. */
  affected: string;
}

export interface AnalysisResult {
  prediction: string;
  confidence: number; // 0-100
  severity: Severity;
  probabilities: Record<string, number>;
  processing_time_ms: number;
  affected_area: AffectedArea;
  features: ExtractedFeatures;
  images: AnalysisImages;
}

// ---------------------------------------------------------------------
// Model evaluation (/evaluate)
// ---------------------------------------------------------------------

export interface PerClassMetric {
  class_name: string;
  precision: number;
  recall: number;
  f1: number;
  support: number;
}

export interface EvaluationDatasetStats {
  total_images_evaluated: number;
  per_class_counts: Record<string, number>;
  skipped_unreadable: number;
}

export interface EvaluationResult {
  model: string;
  class_names: string[];
  accuracy: number;
  precision: number;
  recall: number;
  f1: number;
  per_class: PerClassMetric[];
  confusion_matrix: number[][];
  /** Base64-encoded PNG (no data: prefix) of the rendered confusion matrix. */
  confusion_matrix_image: string;
  dataset: EvaluationDatasetStats;
  processing_time_ms: number;
  evaluated_at: number;
}
