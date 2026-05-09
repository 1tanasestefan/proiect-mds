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
  { label: "Flights",     pct: 40, color: "#FF6B5A" },
  { label: "Hotels",      pct: 30, color: "#FF9F43" },
  { label: "Food",        pct: 20, color: "#FFD166" },
  { label: "Activities",  pct: 10, color: "#2EC4B6" },
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
      className={`rounded-[22px] bg-[#FFFBF3] border-2 border-[rgba(255,107,90,0.18)] p-6 shadow-[0_8px_32px_rgba(0,0,0,0.08)] hover:shadow-[0_16px_48px_rgba(0,0,0,0.13)] hover:-translate-y-0.5 hover:border-[rgba(255,107,90,0.38)] transition-all duration-300 ${className}`}
    >
      <div className="flex items-center gap-2.5 mb-1">
        <div
          className="h-7 w-7 rounded-lg flex items-center justify-center flex-shrink-0"
          style={{ backgroundColor: iconColor + "22" }}
        >
          <Icon className="h-3.5 w-3.5" style={{ color: iconColor }} />
        </div>
        <span
          className="text-[#10223A]/70 text-xs font-semibold uppercase tracking-wide"
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
    <section className="relative bg-[#FFF6E8] overflow-hidden py-32 px-6 md:px-12">
      {/* Ambient */}
      <div className="absolute top-0 right-1/4 h-[600px] w-[600px] rounded-full bg-[#FF9F43]/6 blur-[220px] pointer-events-none" />
      <div className="absolute bottom-0 left-1/4 h-[400px] w-[400px] rounded-full bg-[#FF6B5A]/6 blur-[200px] pointer-events-none" />

      <div className="relative z-10 max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-16">
          <FadeUp>
            <p
              className="text-[#FF9F43]/80 text-[0.65rem] uppercase tracking-[0.35em] mb-5 font-medium"
              style={{ fontFamily: "'Inter', sans-serif" }}
            >
              Product preview
            </p>
          </FadeUp>
          <FadeUp delay={0.1}>
            <h2
              className="font-black text-[#10223A] leading-[1.0]"
              style={{
                fontFamily: "'Archivo Black', sans-serif",
                fontSize: "clamp(2rem, 4.5vw, 4.2rem)",
              }}
            >
              Your entire trip,
              <br />
              <span className="bg-gradient-to-r from-[#FF6B5A] to-[#FF9F43] bg-clip-text text-transparent">
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
              iconColor="#FF6B5A"
              className="h-full min-h-[340px]"
            >
              <div className="mt-4 space-y-4">
                {DAYS.map((d, di) => (
                  <div key={di}>
                    <p
                      className="text-[10px] text-[#FF6B5A]/60 uppercase tracking-widest mb-2 font-medium"
                      style={{ fontFamily: "'Inter', sans-serif" }}
                    >
                      {d.label}
                    </p>
                    <div className="space-y-2">
                      {d.items.map((item, ii) => (
                        <div key={ii} className="flex items-center gap-2.5">
                          <div className="h-1.5 w-1.5 rounded-full bg-[#FF6B5A]/35 flex-shrink-0" />
                          <span
                            className="text-[#64748B] text-sm"
                            style={{ fontFamily: "'Inter', sans-serif" }}
                          >
                            {item}
                          </span>
                        </div>
                      ))}
                    </div>
                    {di < DAYS.length - 1 && (
                      <div className="mt-3.5 h-px bg-[rgba(255,107,90,0.1)]" />
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
              iconColor="#FF9F43"
              className="min-h-[340px]"
            >
              <div className="mt-4">
                <p
                  className="font-black text-[#10223A] leading-none mb-0.5"
                  style={{
                    fontFamily: "'Archivo Black', sans-serif",
                    fontSize: "2rem",
                  }}
                >
                  $1,840
                </p>
                <p
                  className="text-[#64748B]/70 text-xs mb-5"
                  style={{ fontFamily: "'Inter', sans-serif" }}
                >
                  total · 2 travelers · 5 days
                </p>
                <div className="space-y-3">
                  {BUDGET.map((item, i) => (
                    <div key={i}>
                      <div className="flex justify-between mb-1.5">
                        <span
                          className="text-[#64748B] text-xs"
                          style={{ fontFamily: "'Inter', sans-serif" }}
                        >
                          {item.label}
                        </span>
                        <span
                          className="text-[#64748B]/70 text-xs font-medium"
                          style={{ fontFamily: "'Inter', sans-serif" }}
                        >
                          {item.pct}%
                        </span>
                      </div>
                      <div className="h-1.5 rounded-full bg-[rgba(255,107,90,0.12)] overflow-hidden">
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
              iconColor="#FF6B5A"
              className="min-h-[240px]"
            >
              <div className="mt-4 relative h-36 rounded-xl overflow-hidden bg-[#FFE6D6]/60 border border-[rgba(255,107,90,0.15)]">
                {/* Grid texture */}
                <div
                  className="absolute inset-0 opacity-[0.18]"
                  style={{
                    backgroundImage:
                      "linear-gradient(rgba(255,107,90,0.4) 1px, transparent 1px), linear-gradient(90deg, rgba(255,107,90,0.4) 1px, transparent 1px)",
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
                    stroke="#FF6B5A"
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
                    <div className="h-3 w-3 rounded-full bg-[#FF6B5A] border-2 border-[#FFE6D6] shadow-[0_0_10px_rgba(255,107,90,0.7)]" />
                    <span
                      className="text-[8px] text-[#FF6B5A]/80 mt-0.5 whitespace-nowrap"
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
              iconColor="#FF9F43"
              className="min-h-[240px]"
            >
              <div className="mt-4 space-y-2.5">
                {PACKING.map((item, i) => (
                  <div key={i} className="flex items-center gap-2.5">
                    <div
                      className={`h-4 w-4 rounded-md border flex-shrink-0 flex items-center justify-center ${
                        item.done
                          ? "bg-[#10B981]/20 border-[#10B981]/40"
                          : "bg-[rgba(255,107,90,0.06)] border-[rgba(255,107,90,0.20)]"
                      }`}
                    >
                      {item.done && (
                        <div className="h-2 w-2 rounded-sm bg-[#10B981]" />
                      )}
                    </div>
                    <span
                      className={`text-sm ${
                        item.done
                          ? "text-[#64748B]/50 line-through"
                          : "text-[#10223A]/80"
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
              iconColor="#FF6B5A"
              className="min-h-[240px]"
            >
              <div className="mt-4">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <p
                      className="font-black text-[#10223A] leading-none"
                      style={{
                        fontFamily: "'Archivo Black', sans-serif",
                        fontSize: "2.4rem",
                      }}
                    >
                      21°
                    </p>
                    <p
                      className="text-[#64748B]/60 text-xs mt-1"
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
                      className="rounded-xl bg-[#FFFBF3] border border-[rgba(255,107,90,0.12)] p-2.5 text-center"
                    >
                      <p
                        className="text-[#64748B]/60 text-[10px] mb-1"
                        style={{ fontFamily: "'Inter', sans-serif" }}
                      >
                        {w.day}
                      </p>
                      <p className="text-xl">{w.icon}</p>
                      <p
                        className="text-[#10223A]/70 text-xs font-medium mt-0.5"
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
