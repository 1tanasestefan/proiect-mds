"use client";

import React from "react";
import { FadeUp } from "@/components/landing/FadeUp";
import { motion } from "motion/react";
import { CalendarDays, Wallet, MapPin, Package, Cloud } from "lucide-react";

// ── Data ────────────────────────────────────────────────────────────────────

const DAYS = [
  {
    label: "Day 1 — Paris",
    items: ["Eiffel Tower visit", "Le Marais walking tour", "Seine dinner cruise"],
  },
  {
    label: "Day 2 — Paris",
    items: ["Louvre Museum", "Tuileries Garden stroll", "Champs-Élysées evening"],
  },
  {
    label: "Day 3 — Nice",
    items: ["Train to Nice", "Promenade des Anglais", "Rooftop cocktail bar"],
  },
];

const BUDGET = [
  { label: "Flights",     pct: 40, color: "#00F0FF" },
  { label: "Hotels",      pct: 30, color: "#8A2BE2" },
  { label: "Food",        pct: 20, color: "#F59E0B" },
  { label: "Activities",  pct: 10, color: "#10B981" },
];

const PACKING = [
  { label: "Passport",               done: true },
  { label: "Travel adapter",         done: true },
  { label: "Comfortable shoes",      done: true },
  { label: "Rain jacket",            done: false },
  { label: "Travel insurance docs",  done: false },
];

const FORECAST = [
  { day: "Tue", icon: "🌤", temp: "19°" },
  { day: "Wed", icon: "🌧", temp: "15°" },
  { day: "Thu", icon: "☀️", temp: "23°" },
];

// ── Shared card shell ────────────────────────────────────────────────────────

function BentoCard({
  children,
  className = "",
  label,
  icon: Icon,
  iconColor,
}: {
  children: React.ReactNode;
  className?: string;
  label: string;
  icon: React.ElementType;
  iconColor: string;
}) {
  return (
    <div
      className={`rounded-[22px] bg-white/[0.03] border border-white/8 p-6 hover:border-white/[0.13] transition-colors duration-300 ${className}`}
    >
      <div className="flex items-center gap-2">
        <Icon className="h-3.5 w-3.5" style={{ color: iconColor }} />
        <span
          className="text-white/38 text-xs font-medium"
          style={{ fontFamily: "'Inter', sans-serif" }}
        >
          {label}
        </span>
      </div>
      {children}
    </div>
  );
}

// ── Section ──────────────────────────────────────────────────────────────────

export function ProductPreview() {
  return (
    <section className="relative bg-[#030305] overflow-hidden py-32 px-6 md:px-12">
      {/* Ambient */}
      <div className="absolute top-0 right-1/4 h-[600px] w-[600px] rounded-full bg-[#8A2BE2]/5 blur-[220px] pointer-events-none" />
      <div className="absolute bottom-0 left-1/4 h-[400px] w-[400px] rounded-full bg-[#00F0FF]/5 blur-[200px] pointer-events-none" />

      <div className="relative z-10 max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-16">
          <FadeUp>
            <p
              className="text-[#8A2BE2]/50 text-[0.65rem] uppercase tracking-[0.35em] mb-5 font-medium"
              style={{ fontFamily: "'Inter', sans-serif" }}
            >
              Product preview
            </p>
          </FadeUp>
          <FadeUp delay={0.1}>
            <h2
              className="font-black text-white leading-[1.0]"
              style={{
                fontFamily: "'Archivo Black', sans-serif",
                fontSize: "clamp(2rem, 4.5vw, 4.2rem)",
              }}
            >
              Your entire trip,
              <br />
              <span className="bg-gradient-to-r from-[#00F0FF] to-[#8A2BE2] bg-clip-text text-transparent">
                beautifully organized.
              </span>
            </h2>
          </FadeUp>
        </div>

        {/* ── Bento grid ── */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">

          {/* Card 1: Day-by-day plan (2/3 width) */}
          <FadeUp delay={0.05} className="md:col-span-2">
            <BentoCard
              label="Day-by-Day Plan"
              icon={CalendarDays}
              iconColor="#00F0FF"
              className="h-full min-h-[340px]"
            >
              <div className="mt-4 space-y-4">
                {DAYS.map((d, di) => (
                  <div key={di}>
                    <p
                      className="text-[10px] text-[#00F0FF]/50 uppercase tracking-widest mb-2 font-medium"
                      style={{ fontFamily: "'Inter', sans-serif" }}
                    >
                      {d.label}
                    </p>
                    <div className="space-y-2">
                      {d.items.map((item, ii) => (
                        <div key={ii} className="flex items-center gap-2.5">
                          <div className="h-1.5 w-1.5 rounded-full bg-[#00F0FF]/35 flex-shrink-0" />
                          <span
                            className="text-white/60 text-sm"
                            style={{ fontFamily: "'Inter', sans-serif" }}
                          >
                            {item}
                          </span>
                        </div>
                      ))}
                    </div>
                    {di < DAYS.length - 1 && (
                      <div className="mt-3.5 h-px bg-white/[0.05]" />
                    )}
                  </div>
                ))}
              </div>
            </BentoCard>
          </FadeUp>

          {/* Card 2: Budget overview (1/3) */}
          <FadeUp delay={0.1}>
            <BentoCard
              label="Budget Overview"
              icon={Wallet}
              iconColor="#8A2BE2"
              className="min-h-[340px]"
            >
              <div className="mt-4">
                <p
                  className="font-black text-white leading-none mb-0.5"
                  style={{
                    fontFamily: "'Archivo Black', sans-serif",
                    fontSize: "2rem",
                  }}
                >
                  $1,840
                </p>
                <p
                  className="text-white/28 text-xs mb-5"
                  style={{ fontFamily: "'Inter', sans-serif" }}
                >
                  total · 2 travelers · 5 days
                </p>
                <div className="space-y-3">
                  {BUDGET.map((item, i) => (
                    <div key={i}>
                      <div className="flex justify-between mb-1.5">
                        <span
                          className="text-white/45 text-xs"
                          style={{ fontFamily: "'Inter', sans-serif" }}
                        >
                          {item.label}
                        </span>
                        <span
                          className="text-white/35 text-xs font-medium"
                          style={{ fontFamily: "'Inter', sans-serif" }}
                        >
                          {item.pct}%
                        </span>
                      </div>
                      <div className="h-1.5 rounded-full bg-white/8 overflow-hidden">
                        <motion.div
                          className="h-full rounded-full"
                          style={{ backgroundColor: item.color }}
                          initial={{ width: "0%" }}
                          animate={{ width: `${item.pct}%` }}
                          transition={{
                            duration: 1.2,
                            delay: 0.5 + i * 0.12,
                            ease: "easeOut",
                          }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </BentoCard>
          </FadeUp>

          {/* Card 3: Map preview (1/3) */}
          <FadeUp delay={0.15}>
            <BentoCard
              label="Route Map"
              icon={MapPin}
              iconColor="#00F0FF"
              className="min-h-[240px]"
            >
              <div className="mt-4 relative h-36 rounded-xl overflow-hidden bg-[#0a1520] border border-white/5">
                {/* Grid texture */}
                <div
                  className="absolute inset-0 opacity-[0.18]"
                  style={{
                    backgroundImage:
                      "linear-gradient(rgba(0,240,255,0.4) 1px, transparent 1px), linear-gradient(90deg, rgba(0,240,255,0.4) 1px, transparent 1px)",
                    backgroundSize: "20px 20px",
                  }}
                />
                {/* Route line */}
                <svg
                  className="absolute inset-0 w-full h-full"
                  viewBox="0 0 100 100"
                  preserveAspectRatio="none"
                >
                  <path
                    d="M20,25 Q35,35 50,45 Q62,55 75,65"
                    stroke="#00F0FF"
                    strokeWidth="1"
                    fill="none"
                    strokeDasharray="3,3"
                    opacity="0.45"
                  />
                </svg>
                {/* City dots */}
                {[
                  { top: "25%", left: "20%", name: "Paris" },
                  { top: "45%", left: "50%", name: "Lyon" },
                  { top: "65%", left: "75%", name: "Nice" },
                ].map((dot, i) => (
                  <div
                    key={i}
                    className="absolute flex flex-col items-center"
                    style={{ top: dot.top, left: dot.left }}
                  >
                    <div className="h-3 w-3 rounded-full bg-[#00F0FF] border-2 border-[#0a1520] shadow-[0_0_10px_rgba(0,240,255,0.9)]" />
                    <span
                      className="text-[8px] text-[#00F0FF]/75 mt-0.5 whitespace-nowrap"
                      style={{ fontFamily: "'Inter', sans-serif" }}
                    >
                      {dot.name}
                    </span>
                  </div>
                ))}
              </div>
            </BentoCard>
          </FadeUp>

          {/* Card 4: Packing list (1/3) */}
          <FadeUp delay={0.2}>
            <BentoCard
              label="Packing List"
              icon={Package}
              iconColor="#8A2BE2"
              className="min-h-[240px]"
            >
              <div className="mt-4 space-y-2.5">
                {PACKING.map((item, i) => (
                  <div key={i} className="flex items-center gap-2.5">
                    <div
                      className={`h-4 w-4 rounded-md border flex-shrink-0 flex items-center justify-center ${
                        item.done
                          ? "bg-[#10B981]/20 border-[#10B981]/40"
                          : "bg-white/[0.03] border-white/10"
                      }`}
                    >
                      {item.done && (
                        <div className="h-2 w-2 rounded-sm bg-[#10B981]" />
                      )}
                    </div>
                    <span
                      className={`text-sm ${
                        item.done
                          ? "text-white/40 line-through"
                          : "text-white/72"
                      }`}
                      style={{ fontFamily: "'Inter', sans-serif" }}
                    >
                      {item.label}
                    </span>
                  </div>
                ))}
              </div>
            </BentoCard>
          </FadeUp>

          {/* Card 5: Weather (1/3) */}
          <FadeUp delay={0.25}>
            <BentoCard
              label="Weather Ahead"
              icon={Cloud}
              iconColor="#00F0FF"
              className="min-h-[240px]"
            >
              <div className="mt-4">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <p
                      className="font-black text-white leading-none"
                      style={{
                        fontFamily: "'Archivo Black', sans-serif",
                        fontSize: "2.4rem",
                      }}
                    >
                      21°
                    </p>
                    <p
                      className="text-white/35 text-xs mt-1"
                      style={{ fontFamily: "'Inter', sans-serif" }}
                    >
                      Paris · Apr 15
                    </p>
                  </div>
                  <span className="text-4xl">☀️</span>
                </div>
                <div className="grid grid-cols-3 gap-2">
                  {FORECAST.map((w, i) => (
                    <div
                      key={i}
                      className="rounded-xl bg-white/[0.04] border border-white/5 p-2.5 text-center"
                    >
                      <p
                        className="text-white/35 text-[10px] mb-1"
                        style={{ fontFamily: "'Inter', sans-serif" }}
                      >
                        {w.day}
                      </p>
                      <p className="text-xl">{w.icon}</p>
                      <p
                        className="text-white/65 text-xs font-medium mt-0.5"
                        style={{ fontFamily: "'Inter', sans-serif" }}
                      >
                        {w.temp}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            </BentoCard>
          </FadeUp>
        </div>
      </div>
    </section>
  );
}
