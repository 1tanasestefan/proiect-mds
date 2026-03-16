"use client";

import { FadeUp } from "./FadeUp";

export function EmotionalSection() {
  return (
    <section className="relative bg-[#020202] overflow-hidden py-40 px-6 md:px-12">
      {/* Subtle orb — very faint */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
        <div className="h-[600px] w-[600px] rounded-full bg-[#00F0FF]/3 blur-[260px]" />
      </div>

      <div className="relative z-10 max-w-5xl mx-auto text-center">

        <FadeUp duration={1.1}>
          <p
            className="text-white/15 text-[0.6rem] uppercase tracking-[0.4em] mb-12"
            style={{ fontFamily: "'Inter', sans-serif" }}
          >
            The VibeTrips Difference
          </p>
        </FadeUp>

        {/* Main statement */}
        <FadeUp delay={0.1} duration={1.2}>
          <h2
            className="text-[clamp(2.6rem,7vw,7rem)] font-black leading-[0.88] tracking-tight text-white mb-6"
            style={{ fontFamily: "'Archivo Black', sans-serif" }}
          >
            The best trips aren&apos;t
            <br />
            planned{" "}
            <span className="relative inline-block">
              <span className="shimmer-text">perfectly</span>
            </span>
          </h2>
        </FadeUp>

        {/* Divider line */}
        <FadeUp delay={0.3} duration={1.0}>
          <div className="w-24 h-px mx-auto my-10 bg-gradient-to-r from-transparent via-white/20 to-transparent" />
        </FadeUp>

        {/* Secondary headline */}
        <FadeUp delay={0.4} duration={1.1}>
          <h3
            className="text-[clamp(2rem,5vw,5rem)] font-black leading-[0.92] tracking-tight mb-14"
            style={{ fontFamily: "'Archivo Black', sans-serif" }}
          >
            They&apos;re planned{" "}
            <span className="shimmer-text-alt">smartly</span>
          </h3>
        </FadeUp>

        {/* Body copy */}
        <FadeUp delay={0.55} duration={1.0}>
          <p
            className="text-white/38 text-xl md:text-2xl leading-relaxed max-w-2xl mx-auto"
            style={{ fontFamily: "'Inter', sans-serif" }}
          >
            VibeTrips gives you the structure
            <br />
            so you can enjoy the adventure.
          </p>
        </FadeUp>

        {/* Stats row */}
        <FadeUp delay={0.7} duration={1.0}>
          <div className="mt-20 grid grid-cols-3 divide-x divide-white/8 max-w-xl mx-auto">
            {[
              { stat: "AI-crafted", label: "Itineraries" },
              { stat: "Vibe-first", label: "Approach" },
              { stat: "Zero", label: "Guesswork" },
            ].map(({ stat, label }) => (
              <div key={label} className="px-6 py-2 text-center">
                <p
                  className="text-white/85 text-lg font-semibold"
                  style={{ fontFamily: "'Space Grotesk', sans-serif" }}
                >
                  {stat}
                </p>
                <p
                  className="text-white/25 text-xs mt-0.5 uppercase tracking-wider"
                  style={{ fontFamily: "'Inter', sans-serif" }}
                >
                  {label}
                </p>
              </div>
            ))}
          </div>
        </FadeUp>

      </div>
    </section>
  );
}
