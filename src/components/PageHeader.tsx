import { Leaf } from "lucide-react";

export function PageHeader() {
  return (
    <div id="top" className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
      <div>
        <h1 className="flex items-center gap-2.5 text-2xl font-semibold text-white sm:text-3xl">
          <Leaf className="h-6 w-6 shrink-0 text-emerald-400" />
          Coffee Leaf Disease Detection &amp; Severity Estimation
        </h1>
        <p className="mt-1.5 text-sm text-white/50">
          Computer Vision &amp; Machine Learning Application
        </p>
      </div>

      <span className="flex shrink-0 items-center gap-2 rounded-lg bg-emerald-800/40 px-4 py-2 text-sm font-medium text-emerald-300">
        <Leaf className="h-4 w-4" />
        Healthy Plants, Better Future
      </span>
    </div>
  );
}
