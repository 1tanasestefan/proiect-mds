"use client";

import { motion } from "motion/react";
import { FadeUp } from "@/components/landing/FadeUp";
import { Sparkles, CheckCircle2 } from "lucide-react";

interface MarketingCTAProps {
  onStartPlanning: () => void;
}

const TRUST_ITEMS = [
  "Free forever plan",
  "No credit card required",
  "Cancel anytime",
];

export function MarketingCTA({ onStartPlanning }: MarketingCTAProps) {
  return (
    <section
      id="pricing"
      className="relative bg-[#020204] overflow-hidden py-44 px-6 md:px-12"
    >
      {/* Ambient */}
      <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 h-[900px] w-[900px] rounded-full bg-[#00F0FF]/5 blur-[310px] pointer-events-none" />
      <div className="absolute right-1/4 bottom-0 h-[420px] w-[420px] rounded-full bg-[#8A2BE2]/7 blur-[210px] pointer-events-none" />

      {/* Top separator */}
      <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/10 to-transparent" />

      <div className="relative z-10 max-w-4xl mx-auto text-center">
        <FadeUp>
          <p
            className="text-[#00F0FF]/38 text-[0.6rem] uppercase tracking-[0.45em] mb-10 font-medium"
            style={{ fontFamily: "'Inter', sans-serif" }}
          >
            Ready when you are
          </p>
        </FadeUp>

        <FadeUp delay={0.1} duration={1.1}>
          <h2
            className="font-black text-white leading-[0.92] tracking-tight mb-8"
            style={{
              fontFamily: "'Archivo Black', sans-serif",
              fontSize: "clamp(2.8rem, 7vw, 7rem)",
            }}
          >
            Your dream trip is
            <br />
            one{" "}
            <span className="bg-gradient-to-r from-[#00F0FF] via-[#8A2BE2] to-[#00F0FF] bg-[length:200%] bg-clip-text text-transparent animate-gradient-x">
              plan away.
            </span>
          </h2>
        </FadeUp>

        <FadeUp delay={0.22} duration={1.0}>
          <p
            className="text-white/32 text-xl leading-relaxed mb-14 max-w-lg mx-auto"
            style={{ fontFamily: "'Inter', sans-serif" }}
          >
            Join 50,000+ travelers who plan smarter, travel lighter, and
            experience more — with VibeTrips.
          </p>
        </FadeUp>

        <FadeUp delay={0.34}>
          <motion.button
            onClick={onStartPlanning}
            whileHover={{ scale: 1.04 }}
            whileTap={{ scale: 0.97 }}
            transition={{ type: "spring", stiffness: 400, damping: 25 }}
            className="relative group overflow-hidden rounded-full px-14 py-5 text-white font-bold text-lg inline-flex items-center gap-3 shadow-[0_0_60px_rgba(0,240,255,0.35),0_0_90px_rgba(138,43,226,0.18)]"
            style={{ fontFamily: "'Space Grotesk', sans-serif" }}
          >
            <span className="absolute inset-0 bg-gradient-to-r from-[#00F0FF] to-[#8A2BE2]" />
            <span className="absolute inset-0 bg-gradient-to-r from-[#8A2BE2] to-[#00F0FF] opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
            <span className="relative z-10 flex items-center gap-3">
              <Sparkles className="h-5 w-5" />
              Start Planning — It&apos;s Free
            </span>
          </motion.button>
        </FadeUp>

        <FadeUp delay={0.46}>
          <div className="mt-8 flex items-center justify-center gap-8 flex-wrap">
            {TRUST_ITEMS.map((item, i) => (
              <div key={i} className="flex items-center gap-2 text-white/28">
                <CheckCircle2 className="h-3.5 w-3.5 text-[#10B981]/55" />
                <span
                  className="text-sm"
                  style={{ fontFamily: "'Inter', sans-serif" }}
                >
                  {item}
                </span>
              </div>
            ))}
          </div>
        </FadeUp>
      </div>
    </section>
  );
}
