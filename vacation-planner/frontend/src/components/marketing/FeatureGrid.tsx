"use client";

import { FadeUp } from "@/components/landing/FadeUp";
import { motion } from "motion/react";
import { Zap, Plane, Map, Users, Wallet, Compass } from "lucide-react";

const FEATURES = [
  {
    icon: Zap,
    color: "#00F0FF",
    title: "Smart Itineraries",
    desc: "Our AI builds a day-by-day plan tailored to your vibe, budget, and travel style — in seconds.",
  },
  {
    icon: Plane,
    color: "#8A2BE2",
    title: "Flights & Hotels",
    desc: "Find the best deals on flights and accommodation, then sync everything into your trip timeline.",
  },
  {
    icon: Map,
    color: "#00F0FF",
    title: "Interactive Maps",
    desc: "Visualize your route, navigate between stops, and explore neighborhoods before you arrive.",
  },
  {
    icon: Users,
    color: "#8A2BE2",
    title: "Plan With Friends",
    desc: "Invite your travel crew, share ideas, vote on activities, and co-edit your itinerary in real time.",
  },
  {
    icon: Wallet,
    color: "#00F0FF",
    title: "Budget Tracking",
    desc: "Set a budget per person, track spending across categories, and always know where you stand.",
  },
  {
    icon: Compass,
    color: "#8A2BE2",
    title: "Hidden Gems",
    desc: "Discover off-the-beaten-path spots curated by AI — not the usual tourist traps.",
  },
];

type Feature = (typeof FEATURES)[0];

function FeatureCard({ icon: Icon, color, title, desc }: Feature) {
  return (
    <motion.div
      whileHover={{ y: -6, scale: 1.015 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
      className="group relative rounded-[22px] bg-white/[0.03] border border-white/8 p-7 overflow-hidden hover:border-white/[0.13] transition-colors duration-300 cursor-default"
    >
      {/* Hover radial glow */}
      <div
        className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none"
        style={{
          background: `radial-gradient(circle at 50% 0%, ${color}0a 0%, transparent 68%)`,
        }}
      />

      {/* Icon */}
      <div
        className="h-12 w-12 rounded-xl flex items-center justify-center mb-5"
        style={{
          backgroundColor: color + "16",
          boxShadow: `0 0 28px ${color}20`,
        }}
      >
        <Icon className="h-6 w-6" style={{ color }} />
      </div>

      <h3
        className="text-white font-semibold text-lg mb-2.5 leading-snug"
        style={{ fontFamily: "'Space Grotesk', sans-serif" }}
      >
        {title}
      </h3>
      <p
        className="text-white/38 text-sm leading-relaxed"
        style={{ fontFamily: "'Inter', sans-serif" }}
      >
        {desc}
      </p>
    </motion.div>
  );
}

export function FeatureGrid() {
  return (
    <section
      id="features"
      className="relative bg-[#020204] overflow-hidden py-32 px-6 md:px-12"
    >
      {/* Ambient center orb */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 h-[800px] w-[800px] rounded-full bg-[#00F0FF]/4 blur-[260px] pointer-events-none" />

      <div className="relative z-10 max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-20">
          <FadeUp>
            <p
              className="text-[#00F0FF]/50 text-[0.65rem] uppercase tracking-[0.35em] mb-5 font-medium"
              style={{ fontFamily: "'Inter', sans-serif" }}
            >
              Everything you need
            </p>
          </FadeUp>
          <FadeUp delay={0.1}>
            <h2
              className="font-black text-white leading-[1.0] tracking-tight"
              style={{
                fontFamily: "'Archivo Black', sans-serif",
                fontSize: "clamp(2.2rem, 5vw, 4.5rem)",
              }}
            >
              One platform.
              <br />
              <span className="bg-gradient-to-r from-[#00F0FF] to-[#8A2BE2] bg-clip-text text-transparent">
                Total trip control.
              </span>
            </h2>
          </FadeUp>
          <FadeUp delay={0.2}>
            <p
              className="text-white/38 text-lg mt-6 max-w-xl mx-auto leading-relaxed"
              style={{ fontFamily: "'Inter', sans-serif" }}
            >
              VibeTrips brings together every tool you need to plan, organize,
              and experience your best trips yet.
            </p>
          </FadeUp>
        </div>

        {/* Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {FEATURES.map((feat, i) => (
            <FadeUp key={i} delay={0.05 * i}>
              <FeatureCard {...feat} />
            </FadeUp>
          ))}
        </div>
      </div>
    </section>
  );
}
