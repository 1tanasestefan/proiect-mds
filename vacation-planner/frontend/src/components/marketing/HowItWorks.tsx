"use client";

import { FadeUp } from "@/components/landing/FadeUp";
import { Search, CalendarDays, Backpack } from "lucide-react";

const STEPS = [
  {
    number: "01",
    icon: Search,
    color: "#00F0FF",
    title: "Pick your destination",
    desc: "Tell our AI where you want to go — or get inspired by personalised destination suggestions based on your travel style.",
    preview: (
      <div className="mt-6 rounded-xl bg-[#020204] border border-white/8 p-4 space-y-3">
        <div className="flex items-center gap-2.5 bg-white/[0.04] rounded-xl px-4 py-3 border border-white/8">
          <Search className="h-4 w-4 text-white/20 flex-shrink-0" />
          <span
            className="text-white/28 text-sm flex-1"
            style={{ fontFamily: "'Inter', sans-serif" }}
          >
            Bali, Indonesia...
          </span>
          <span className="h-1.5 w-1.5 rounded-full bg-[#00F0FF] animate-pulse" />
        </div>
        <div className="flex flex-wrap gap-2">
          {["🏖 Bali", "🗼 Paris", "🏯 Tokyo", "🗽 NYC"].map((s, i) => (
            <span
              key={i}
              className="px-3 py-1 rounded-full bg-white/[0.04] border border-white/8 text-white/42 text-xs"
              style={{ fontFamily: "'Inter', sans-serif" }}
            >
              {s}
            </span>
          ))}
        </div>
      </div>
    ),
  },
  {
    number: "02",
    icon: CalendarDays,
    color: "#8A2BE2",
    title: "Build your itinerary",
    desc: "Our AI generates a complete day-by-day plan. Adjust, reorder, and add your own ideas — no travel agent required.",
    preview: (
      <div className="mt-6 rounded-xl bg-[#020204] border border-white/8 p-4 space-y-2.5">
        {[
          { label: "Morning", color: "#00F0FF" },
          { label: "Afternoon", color: "#8A2BE2" },
          { label: "Evening", color: "#F59E0B" },
        ].map((period, i) => (
          <div key={i} className="flex items-center gap-3">
            <div
              className="h-1.5 w-1.5 rounded-full flex-shrink-0"
              style={{ backgroundColor: period.color }}
            />
            <div className="flex-1 h-7 rounded-lg bg-white/[0.04] border border-white/[0.07] flex items-center px-3">
              <span
                className="text-white/35 text-xs"
                style={{ fontFamily: "'Inter', sans-serif" }}
              >
                {period.label} activity
              </span>
            </div>
          </div>
        ))}
      </div>
    ),
  },
  {
    number: "03",
    icon: Backpack,
    color: "#10B981",
    title: "Travel with everything in one place",
    desc: "Your tickets, confirmations, maps, packing list, and budget — all accessible on the go, even offline.",
    preview: (
      <div className="mt-6 rounded-xl bg-[#020204] border border-white/8 p-4">
        <div className="grid grid-cols-2 gap-2">
          {[
            { icon: "✈️", label: "Boarding Pass" },
            { icon: "🏨", label: "Hotel Pin" },
            { icon: "💰", label: "Budget" },
            { icon: "🗺", label: "Offline Map" },
          ].map((item, i) => (
            <div
              key={i}
              className="rounded-xl bg-white/[0.04] border border-white/8 p-3 flex items-center gap-2.5"
            >
              <span className="text-xl">{item.icon}</span>
              <span
                className="text-white/45 text-xs"
                style={{ fontFamily: "'Inter', sans-serif" }}
              >
                {item.label}
              </span>
            </div>
          ))}
        </div>
      </div>
    ),
  },
];

export function HowItWorks() {
  return (
    <section
      id="how-it-works"
      className="relative bg-[#030305] overflow-hidden py-32 px-6 md:px-12"
    >
      {/* Ambient */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 h-[900px] w-[900px] rounded-full bg-[#8A2BE2]/4 blur-[290px] pointer-events-none" />

      <div className="relative z-10 max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-20">
          <FadeUp>
            <p
              className="text-[#00F0FF]/50 text-[0.65rem] uppercase tracking-[0.35em] mb-5 font-medium"
              style={{ fontFamily: "'Inter', sans-serif" }}
            >
              Simple by design
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
              From idea to itinerary
              <br />
              <span className="bg-gradient-to-r from-[#00F0FF] to-[#8A2BE2] bg-clip-text text-transparent">
                in three steps.
              </span>
            </h2>
          </FadeUp>
        </div>

        {/* Steps grid */}
        <div className="relative grid grid-cols-1 md:grid-cols-3 gap-10 lg:gap-14">
          {/* Desktop connector line */}
          <div className="hidden md:block absolute top-10 left-[calc(16.67%+32px)] right-[calc(16.67%+32px)] h-px bg-gradient-to-r from-transparent via-white/[0.08] to-transparent pointer-events-none" />

          {STEPS.map((step, i) => (
            <FadeUp key={i} delay={0.1 * i}>
              <div className="relative">
                {/* Step number + icon row */}
                <div className="flex items-center gap-4 mb-6">
                  <span
                    className="font-black leading-none select-none"
                    style={{
                      fontFamily: "'Archivo Black', sans-serif",
                      fontSize: "3.2rem",
                      WebkitTextStroke: `1.5px ${step.color}45`,
                      color: "transparent",
                    }}
                  >
                    {step.number}
                  </span>
                  <div
                    className="h-10 w-10 rounded-xl flex items-center justify-center flex-shrink-0"
                    style={{ backgroundColor: step.color + "18" }}
                  >
                    <step.icon
                      className="h-5 w-5"
                      style={{ color: step.color }}
                    />
                  </div>
                </div>

                <h3
                  className="text-white font-bold text-xl mb-3 leading-snug"
                  style={{ fontFamily: "'Space Grotesk', sans-serif" }}
                >
                  {step.title}
                </h3>

                <p
                  className="text-white/38 text-sm leading-relaxed"
                  style={{ fontFamily: "'Inter', sans-serif" }}
                >
                  {step.desc}
                </p>

                {step.preview}
              </div>
            </FadeUp>
          ))}
        </div>
      </div>
    </section>
  );
}
