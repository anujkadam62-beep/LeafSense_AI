import { Leaf, ScanLine, BarChart3, ShieldCheck } from "lucide-react";

const features = [
  {
    icon: ScanLine,
    title: "AI-Powered Detection",
    description: "Advanced ML models for accurate disease identification.",
  },
  {
    icon: BarChart3,
    title: "Severity Estimation",
    description: "Know how serious the disease is with percentage analysis.",
  },
  {
    icon: ShieldCheck,
    title: "Better Decisions",
    description: "Take timely action and protect your crop.",
  },
];

export function LoginShowcase() {
  return (
    <div className="relative hidden overflow-hidden bg-[#06170d] lg:flex lg:w-1/2 lg:flex-col lg:justify-between">
      <LeafArtwork />

      <div className="relative z-10 flex flex-1 flex-col justify-between p-10 xl:p-12">
        <div className="flex items-center gap-2 text-white">
          <Leaf className="h-5 w-5 text-emerald-400" />
          <span className="text-base font-semibold">CoffeeLeaf AI</span>
        </div>

        <div className="max-w-sm">
          <h1 className="text-4xl leading-tight font-bold text-white">
            Smart Detection.
            <br />
            <span className="text-emerald-400">Healthier Plants.</span>
          </h1>
          <p className="mt-4 text-sm leading-relaxed text-white/60">
            Detect coffee leaf diseases, estimate severity, and take better
            actions for better yield.
          </p>

          <div className="mt-8 space-y-4">
            {features.map((feature) => (
              <div key={feature.title} className="flex items-start gap-3">
                <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-emerald-600/90">
                  <feature.icon className="h-4 w-4 text-white" />
                </span>
                <div>
                  <p className="text-sm font-medium text-white">{feature.title}</p>
                  <p className="text-xs text-white/50">{feature.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <p className="text-xs text-white/35">
          © {new Date().getFullYear()} CoffeeLeaf AI. All rights reserved.
        </p>
      </div>
    </div>
  );
}

/**
 * Original SVG botanical illustration (no stock photo) — organic leaf
 * shapes with a berry cluster, faded behind a dark gradient so the
 * text on the left stays legible while the leaves are visible on the
 * right, similar to the reference layout.
 */
function LeafArtwork() {
  return (
    <div className="absolute inset-0">
      <svg
        viewBox="0 0 600 800"
        preserveAspectRatio="xMaxYMid slice"
        className="h-full w-full opacity-90"
      >
        <defs>
          <linearGradient id="leafFill" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#2f6f45" />
            <stop offset="100%" stopColor="#123a20" />
          </linearGradient>
          <radialGradient id="berryFill" cx="35%" cy="30%" r="70%">
            <stop offset="0%" stopColor="#ef4444" />
            <stop offset="100%" stopColor="#7f1d1d" />
          </radialGradient>
          <linearGradient id="fadeOverlay" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor="#06170d" stopOpacity="1" />
            <stop offset="55%" stopColor="#06170d" stopOpacity="0.75" />
            <stop offset="100%" stopColor="#06170d" stopOpacity="0.15" />
          </linearGradient>
        </defs>

        <path
          d="M420 40 C 560 90, 610 260, 540 420 C 480 560, 470 700, 520 800 L 700 800 L 700 -20 L 420 -20 Z"
          fill="url(#leafFill)"
        />
        <path
          d="M470 60 C 560 180, 540 380, 460 520"
          stroke="#0d2a17"
          strokeWidth="3"
          fill="none"
          opacity="0.5"
        />
        <path
          d="M300 120 C 420 160, 470 300, 400 420 C 340 520, 360 640, 430 760 L 640 760 L 640 60 L 300 60 Z"
          fill="url(#leafFill)"
          opacity="0.75"
        />

        {[
          [430, 140],
          [465, 165],
          [450, 195],
          [485, 200],
          [410, 175],
        ].map(([cx, cy], i) => (
          <circle key={i} cx={cx} cy={cy} r={14} fill="url(#berryFill)" />
        ))}

        <rect x="0" y="0" width="600" height="800" fill="url(#fadeOverlay)" />
      </svg>
    </div>
  );
}
