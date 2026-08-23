"use client";

import { useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { UploadCloud, ImageIcon } from "lucide-react";
import { cn } from "@/lib/utils";

interface UploadPanelProps {
  onAnalyze: (file: File) => void;
  analyzing: boolean;
}

export function UploadPanel({ onAnalyze, analyzing }: UploadPanelProps) {
  const onDrop = useCallback(
    (accepted: File[]) => {
      const file = accepted[0];
      if (file) onAnalyze(file);
    },
    [onAnalyze]
  );

  const { getRootProps, getInputProps, isDragActive, open } = useDropzone({
    onDrop,
    accept: { "image/png": [".png"], "image/jpeg": [".jpg", ".jpeg"] },
    maxFiles: 1,
    noClick: true,
  });

  return (
    <div
      id="upload"
      {...getRootProps()}
      className={cn(
        "flex flex-col items-center justify-between gap-4 rounded-xl border-2 border-dashed border-emerald-700/40 bg-[var(--color-surface)]/[0.04] px-6 py-6 sm:flex-row",
        isDragActive && "border-emerald-400 bg-emerald-950/30"
      )}
    >
      <input {...getInputProps()} />
      <div className="flex items-center gap-4">
        <UploadCloud className="h-7 w-7 shrink-0 text-white/40" />
        <div>
          <p className="text-sm font-medium text-white">
            Upload or Capture a Coffee Leaf Image
          </p>
          <p className="mt-0.5 text-sm text-white/50">
            {isDragActive ? "Drop the image here" : "Drag and drop an image file here, or click to browse"}
          </p>
          <p className="mt-0.5 flex items-center gap-1.5 text-xs text-white/35">
            <ImageIcon className="h-3.5 w-3.5" />
            Supports JPG, JPEG, PNG
          </p>
        </div>
      </div>

      <button
        onClick={open}
        disabled={analyzing}
        className="flex shrink-0 items-center gap-2 rounded-md bg-[var(--color-accent)] px-4 py-2.5 text-sm font-medium text-white transition hover:bg-[var(--color-accent-hover)] disabled:opacity-60"
      >
        <UploadCloud className="h-4 w-4" />
        {analyzing ? "Analyzing…" : "Browse Files"}
      </button>
    </div>
  );
}
