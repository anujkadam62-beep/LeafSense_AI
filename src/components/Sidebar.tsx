"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  Leaf,
  Menu,
  LayoutDashboard,
  Search,
  BarChart3,
  Database,
  Info,
  LogIn,
} from "lucide-react";
import { cn } from "@/lib/utils";

const navItems = [
  {
    label: "Dashboard",
    href: "#dashboard",
    id: "dashboard",
    icon: LayoutDashboard,
  },
  {
    label: "Analyze Leaf",
    href: "#analyze",
    id: "analyze",
    icon: Search,
  },
  {
    label: "Model Evaluation",
    href: "#evaluation",
    id: "evaluation",
    icon: BarChart3,
  },
  {
    label: "Dataset (RoCoLe)",
    href: "#dataset",
    id: "dataset",
    icon: Database,
  },
  {
    label: "About Project",
    href: "#about",
    id: "about",
    icon: Info,
  },
];

const pipelineSteps = [
  "Image Acquisition",
  "Preprocessing",
  "HSV Conversion",
  "Segmentation",
  "Feature Extraction",
  "ML Classification",
  "Prediction & Output",
];

export function Sidebar() {
  const [active, setActive] = useState("dashboard");

  useEffect(() => {
    const sections = navItems
      .map((item) => document.getElementById(item.id))
      .filter((section): section is HTMLElement => section !== null);

    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries.find((entry) => entry.isIntersecting);
        if (visible) {
          setActive(visible.target.id);
        }
      },
      {
        rootMargin: "-25% 0px -60% 0px",
        threshold: 0.15,
      }
    );

    sections.forEach((section) => observer.observe(section));

    return () => observer.disconnect();
  }, []);

  const handleNavigation = (
    e: React.MouseEvent<HTMLAnchorElement>,
    id: string
  ) => {
    e.preventDefault();

    const section = document.getElementById(id);

    if (section) {
      setActive(id);
      section.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });

      window.history.replaceState(null, "", `#${id}`);
    }
  };

  return (
    <aside className="sticky top-0 hidden h-screen w-64 shrink-0 flex-col bg-[var(--color-sidebar)] px-4 py-5 lg:flex">
      {/* Logo */}
      <div className="flex items-center justify-between px-1">
        <Link href="/" className="flex items-center gap-2 text-white">
          <Leaf className="h-5 w-5 text-emerald-400" />
          <span className="text-base font-semibold">CoffeeLeaf AI</span>
        </Link>

        <Menu className="h-4 w-4 text-white/50" />
      </div>

      {/* Navigation */}
      <nav className="mt-6 flex flex-col gap-1">
        {navItems.map((item) => (
          <a
            key={item.id}
            href={item.href}
            onClick={(e) => handleNavigation(e, item.id)}
            className={cn(
              "flex items-center gap-2.5 rounded-lg px-3 py-2.5 text-sm transition-all duration-300",
              active === item.id
                ? "bg-[var(--color-sidebar-active)] text-white font-medium shadow-lg shadow-emerald-900/20"
                : "text-white/70 hover:bg-white/5 hover:text-white hover:translate-x-1"
            )}
          >
            <item.icon className="h-4 w-4" />
            {item.label}
          </a>
        ))}
      </nav>

      {/* Pipeline */}
      <div className="mt-6 rounded-xl border border-white/10 bg-white/[0.03] p-4">
        <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-emerald-400">
          <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
          Pipeline Overview
        </div>

        <ol className="mt-4 space-y-3">
          {pipelineSteps.map((step, i) => (
            <li
              key={step}
              className="flex items-center gap-3 text-sm text-white/80"
            >
              <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-emerald-600 text-xs font-semibold text-white">
                {i + 1}
              </span>
              {step}
            </li>
          ))}
        </ol>
      </div>

      {/* Login */}
      <Link
        href="/login"
        className="mt-auto flex items-center gap-2.5 rounded-lg px-3 py-2.5 text-sm text-white/60 transition hover:bg-white/5 hover:text-white"
      >
        <LogIn className="h-4 w-4" />
        Login
      </Link>
    </aside>
  );
}