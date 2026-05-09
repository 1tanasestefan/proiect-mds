"use client";

import { FadeUp } from "@/components/landing/FadeUp";
import { Search, CalendarDays, Backpack } from "lucide-react";

const STEPS = [
  {
    number: "01",
    icon: Search,
    color: "#FF6B5A",
    title: "Pick your destination",
    desc: "Tell our AI where you want to go — or get inspired by personalised destination suggestions based on your travel style.",
    preview: (
      <div className="mt-6 rounded-xl bg-[#FFE6D6]/40 border border-[rgba(255,107,90,0.20)] p-4 space-y-3">
        <div className="flex items-center gap-2.5 bg-[#FFFBF3] rounded-xl px-4 py-3 border border-[rgba(255,107,90,0.18)]">
          <Search className="h-4 w-4 text-[#64748B]/30 flex-shrink-0" />
          <span className="text-[#64748B]/40 text-sm flex-1" style={{ fontFamily: "'Inter', sans-serif" }}>Bali, Indonesia...</span>
          <span className="h-1.5 w-1.5 rounded-full bg-[#FF6B5A] animate-pulse" />
        </div>
        <div className="flex flex-wrap gap-2">
          {["🏖 Bali", "🗼 Paris", "🏯 Tokyo", "🗽 NYC"].map((s, i) => (
            <span
              key={i}
              className="px-3 py-1 rounded-full bg-[#FFFBF3] border border-[rgba(255,107,90,0.18)] text-[#64748B]/60 text-xs"
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
    color: "#FF9F43",
    title: "Build your itinerary",
    desc: "Our AI generates a complete day-by-day plan. Adjust, reorder, and add your own ideas — no travel agent required.",
    preview: (
      <div className="mt-6 rounded-xl bg-[#FFE6D6]/40 border border-[rgba(255,107,90,0.20)] p-4 space-y-2.5">
        {[
          { label: "Morning", color: "#FF6B5A" },
          { label: "Afternoon", color: "#FF9F43" },
          { label: "Evening", color: "#FFD166" },
        ].map((period, i) => (
          <div key={i} className="flex items-center gap-3">
            <div
              className="h-1.5 w-1.5 rounded-full flex-shrink-0"
              style={{ backgroundColor: period.color }}
            />
              <div className="flex-1 h-7 rounded-lg bg-[#FFFBF3] border border-[rgba(255,107,90,0.15)] flex items-center px-3">
              <span className="text-[#64748B]/40 text-xs" style={{ fontFamily: "'Inter', sans-serif" }}>{period.label} activity</span>
            </div>
          </div>
        ))}
      </div>
    ),
  },
  {
    number: "03",
    icon: Backpack,
    color: "#2EC4B6",
    title: "Travel with everything in one place",
    desc: "Your tickets, confirmations, maps, packing list, and budget — all accessible on the go, even offline.",
    preview: (
      <div className="mt-6 rounded-xl bg-[#FFE6D6]/40 border border-[rgba(255,107,90,0.20)] p-4">
        <div className="grid grid-cols-2 gap-2">
          {[
            { icon: "✈️", label: "Boarding Pass" },
            { icon: "🏨", label: "Hotel Pin" },
            { icon: "💰", label: "Budget" },
            { icon: "🗺", label: "Offline Map" },
          ].map((item, i) => (
            <div
              key={i}
              className="rounded-xl bg-[#FFFBF3] border border-[rgba(255,107,90,0.15)] p-3 flex items-center gap-2.5"
            >
              <span className="text-xl">{item.icon}</span>
              <span
                className="text-[#64748B]/60 text-xs"
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
      className="relative bg-[#FFF6E8] overflow-hidden py-32 px-6 md:px-12"
    >
      {/* Ambient */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 h-[900px] w-[900px] rounded-full bg-[#FF9F43]/6 blur-[290px] pointer-events-none" />

      <div className="relative z-10 max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-20">
          <FadeUp>
            <p
              className="text-[#FF6B5A]/60 text-[0.65rem] uppercase tracking-[0.35em] mb-5 font-medium"
              style={{ fontFamily: "'Inter', sans-serif" }}
            >
              Simple by design
            </p>
          </FadeUp>
          <FadeUp delay={0.1}>
            <h2
              className="font-bold text-[#10223A] leading-[1.08]"
              style={{
                fontFamily: "var(--font-playfair), Georgia, serif",
                fontSize: "clamp(2rem, 4.5vw, 3.8rem)",
              }}
            >
              From idea to itinerary
              <br />
              <span className="bg-gradient-to-r from-[#FF6B5A] to-[#FF9F43] bg-clip-text text-transparent">
                in three steps.
              </span>
            </h2>
          </FadeUp>
        </div>

        {/* Steps grid */}
        <div className="relative grid grid-cols-1 md:grid-cols-3 gap-10 lg:gap-14">
          {/* Desktop connector line */}
          <div className="hidden md:block absolute top-10 left-[calc(16.67%+32px)] right-[calc(16.67%+32px)] h-px bg-gradient-to-r from-transparent via-[rgba(255,107,90,0.2)] to-transparent pointer-events-none" />

          {STEPS.map((step, i) => (
            <FadeUp key={i} delay={0.1 * i}>
              <div
                className="relative rounded-[22px] bg-[#FFFBF3] border-2 p-7 shadow-[0_8px_40px_rgba(0,0,0,0.10)] hover:shadow-[0_16px_56px_rgba(0,0,0,0.15)] hover:-translate-y-1 transition-all duration-300 overflow-hidden"
                style={{ borderColor: step.color + "55" }}
              >
                {/* Colored top accent bar */}
                <div
                  className="absolute top-0 left-0 right-0 h-1 rounded-t-[22px]"
                  style={{ background: `linear-gradient(90deg, ${step.color}, ${step.color}88)` }}
                />

                {/* Step number + icon row */}
                <div className="flex items-center justify-between mb-6">
                  <span
                    className="font-black leading-none select-none"
                    style={{
                      fontFamily: "'Archivo Black', sans-serif",
                      fontSize: "4rem",
                      color: step.color,
                      opacity: 0.18,
                    }}
                  >
                    {step.number}
                  </span>
                  <div
                    className="h-14 w-14 rounded-2xl flex items-center justify-center flex-shrink-0 shadow-md"
                    style={{ backgroundColor: step.color, boxShadow: `0 6px 20px ${step.color}55` }}
                  >
                    <step.icon className="h-7 w-7 text-white" />
                  </div>
                </div>

                <h3
                  className="text-[#10223A] font-bold text-xl mb-3 leading-snug"
                  style={{ fontFamily: "'Space Grotesk', sans-serif" }}
                >
                  {step.title}
                </h3>

                <p
                  className="text-[#64748B] text-sm leading-relaxed"
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
