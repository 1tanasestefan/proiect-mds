"use client";

import { motion } from "motion/react";
import { FadeUp } from "./FadeUp";

interface LandingCTAProps {
  onStartPlanning: () => void;
}

export function LandingCTA({ onStartPlanning }: LandingCTAProps) {
  return (
    <section className="relative bg-[#040404] overflow-hidden py-44 px-6 md:px-12">
      {/* Top separator gradient */}
      <div className="absolute inset-x-0 top-0 h-40 bg-gradient-to-b from-[#020202] to-transparent pointer-events-none" />

      {/* Ambient orbs */}
      <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 h-[800px] w-[800px] rounded-full bg-[#00F0FF]/4 blur-[280px] pointer-events-none" />
      <div className="absolute right-0 bottom-0 h-[400px] w-[400px] rounded-full bg-[#8A2BE2]/7 blur-[200px] pointer-events-none" />

      <div className="relative z-10 max-w-4xl mx-auto text-center">

        {/* Small eyebrow */}
        <FadeUp>
          <p
            className="text-[#00F0FF]/40 text-[0.6rem] uppercase tracking-[0.4em] mb-10"
            style={{ fontFamily: "'Inter', sans-serif" }}
          >
            Your journey starts here
          </p>
        </FadeUp>

        {/* Main headline */}
        <FadeUp delay={0.1} duration={1.2}>
          <h2
            className="text-[clamp(2.8rem,7vw,7.5rem)] font-black leading-[0.88] text-white tracking-tight mb-8"
            style={{ fontFamily: "'Archivo Black', sans-serif" }}
          >
            Where will your
            <br />
            next{" "}
            <span className="bg-gradient-to-r from-[#00F0FF] via-[#8A2BE2] to-[#00F0FF] bg-[length:200%] bg-clip-text text-transparent animate-gradient-x">
              adventure
            </span>
            <br />
            take you?
          </h2>
        </FadeUp>

        {/* Subtext */}
        <FadeUp delay={0.25} duration={1.0}>
          <p
            className="text-white/35 text-xl md:text-2xl leading-relaxed mb-16 max-w-xl mx-auto"
            style={{ fontFamily: "'Inter', sans-serif" }}
          >
            Start planning your dream trip today.
            <br />
            Free, fast, and built around your vibe.
          </p>
        </FadeUp>

        {/* CTA Button */}
        <FadeUp delay={0.4} duration={1.0}>
          <div className="flex justify-center">
            <motion.button
              onClick={onStartPlanning}
              whileHover={{ scale: 1.04 }}
              whileTap={{ scale: 0.97 }}
              transition={{ type: "spring", stiffness: 400, damping: 28 }}
              className="relative group overflow-hidden rounded-full px-12 py-5 text-black font-bold text-lg"
              style={{ fontFamily: "'Space Grotesk', sans-serif" }}
            >
              {/* Default gradient */}
              <span
                className="absolute inset-0 bg-gradient-to-r from-[#00F0FF] to-[#8A2BE2] transition-opacity duration-300 group-hover:opacity-0"
                aria-hidden
              />
              {/* Hover gradient (reversed) */}
              <span
                className="absolute inset-0 bg-gradient-to-r from-[#8A2BE2] to-[#00F0FF] opacity-0 transition-opacity duration-300 group-hover:opacity-100"
                aria-hidden
              />
              {/* Glow */}
              <span
                className="absolute inset-0 rounded-full transition-all duration-300"
                style={{
                  boxShadow:
                    "0 0 0 0 rgba(0,240,255,0.4)",
                }}
              />
              <motion.span
                className="absolute inset-0 rounded-full pointer-events-none"
                initial={{ boxShadow: "0 0 30px rgba(0,240,255,0.35)" }}
                whileHover={{ boxShadow: "0 0 60px rgba(138,43,226,0.5)" }}
                transition={{ duration: 0.3 }}
              />
              <span className="relative z-10 text-white tracking-wide">
                Start Planning
              </span>
            </motion.button>
          </div>
        </FadeUp>

        {/* Micro caption */}
        <FadeUp delay={0.55}>
          <p
            className="mt-6 text-white/15 text-sm"
            style={{ fontFamily: "'Inter', sans-serif" }}
          >
            No account needed to explore
          </p>
        </FadeUp>

      </div>

      {/* Bottom gradient fade-out */}
      <div className="absolute inset-x-0 bottom-0 h-32 bg-gradient-to-t from-black/60 to-transparent pointer-events-none" />
    </section>
  );
}
