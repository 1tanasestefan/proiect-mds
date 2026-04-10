"use client";

import { useState, useCallback } from "react";
import { motion, AnimatePresence } from "motion/react";
import Image from "next/image";
import { FadeUp } from "./FadeUp";
import { ChevronLeft, ChevronRight } from "lucide-react";

const destinations = [
  {
    label: "Neon Tokyo",
    sublabel: "Japan — Electric nights & samurai soul",
    image: "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=1200&q=85&auto=format&fit=crop",
    accent: "#00F0FF",
    vibe: "Urban",
  },
  {
    label: "Tuscany Villas",
    sublabel: "Italy — Rolling hills & harvest gold",
    image: "https://images.unsplash.com/photo-1499678329028-101435549a4e?w=1200&q=85&auto=format&fit=crop",
    accent: "#FFB347",
    vibe: "Luxury",
  },
  {
    label: "Maldives Overwater",
    sublabel: "Maldives — Private infinity & turquoise silence",
    image: "https://images.unsplash.com/photo-1514282401047-d79a71a590e8?w=1200&q=85&auto=format&fit=crop",
    accent: "#00D4AA",
    vibe: "Island",
  },
  {
    label: "Paris, City of Light",
    sublabel: "France — Art, cuisine & Eiffel magic",
    image: "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=1200&q=85&auto=format&fit=crop",
    accent: "#8A2BE2",
    vibe: "Culture",
  },
];

const bullets = [
  "Hidden beaches that never make the lists.",
  "Local food spots only locals know.",
  "Epic viewpoints off the tourist trail.",
  "Cultural experiences that stay with you.",
];

const SLIDE_VARIANTS = {
  enter: (dir: number) => ({ x: dir > 0 ? 80 : -80, opacity: 0, scale: 0.97 }),
  center: { x: 0, opacity: 1, scale: 1 },
  exit: (dir: number) => ({ x: dir > 0 ? -80 : 80, opacity: 0, scale: 0.97 }),
};

export function DiscoverSection() {
  const [index, setIndex] = useState(0);
  const [direction, setDirection] = useState(1);

  const go = useCallback((delta: number) => {
    setDirection(delta);
    setIndex((prev) => (prev + delta + destinations.length) % destinations.length);
  }, []);

  const current = destinations[index];

  return (
    <section className="relative bg-[#060606] overflow-hidden py-36 px-6 md:px-12">
      {/* Background orbs */}
      <div className="absolute top-1/2 right-0 -translate-y-1/2 h-[700px] w-[400px] rounded-full bg-[#00F0FF]/4 blur-[220px] pointer-events-none" />
      <div className="absolute bottom-0 left-1/4 h-[400px] w-[400px] rounded-full bg-[#8A2BE2]/4 blur-[200px] pointer-events-none" />

      <div className="relative z-10 max-w-7xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 xl:gap-24 items-center">

          {/* ── Left: Text ──────────────────────────────────────── */}
          <div>
            <FadeUp>
              <p className="text-[#8A2BE2]/60 text-[0.65rem] uppercase tracking-[0.3em] mb-6 font-medium"
                 style={{ fontFamily: "'Inter', sans-serif" }}>
                Curated by AI
              </p>
            </FadeUp>

            <FadeUp delay={0.1}>
              <h2 className="text-[clamp(2.8rem,6vw,5.5rem)] font-black leading-[0.9] mb-10 text-white"
                  style={{ fontFamily: "'Archivo Black', sans-serif" }}>
                Discover places<br />
                you didn&apos;t know{" "}
                <span className="bg-gradient-to-r from-[#8A2BE2] to-[#00F0FF] bg-clip-text text-transparent">
                  existed
                </span>
              </h2>
            </FadeUp>

            <div className="space-y-5 mb-12">
              {bullets.map((line, i) => (
                <FadeUp key={i} delay={0.2 + i * 0.1}>
                  <div className="flex items-start gap-3">
                    <span className="mt-[9px] h-[2px] w-5 flex-shrink-0 rounded-full bg-gradient-to-r from-[#00F0FF] to-[#8A2BE2]" />
                    <p className="text-white/55 text-lg leading-snug" style={{ fontFamily: "'Inter', sans-serif" }}>
                      {line}
                    </p>
                  </div>
                </FadeUp>
              ))}
            </div>

            <FadeUp delay={0.65}>
              <p className="text-white/25 text-base leading-relaxed max-w-sm" style={{ fontFamily: "'Inter', sans-serif" }}>
                Your next favorite place might be somewhere<br />
                you&apos;ve never even searched for.
              </p>
            </FadeUp>
          </div>

          {/* ── Right: Slideshow ────────────────────────────────── */}
          <div className="flex flex-col gap-5">

            {/* Main slide */}
            <div className="relative aspect-[4/3] rounded-3xl overflow-hidden">
              <AnimatePresence custom={direction} mode="popLayout">
                <motion.div
                  key={index}
                  custom={direction}
                  variants={SLIDE_VARIANTS}
                  initial="enter"
                  animate="center"
                  exit="exit"
                  transition={{ duration: 0.5, ease: [0.32, 0.72, 0, 1] }}
                  className="absolute inset-0"
                >
                  <Image
                    src={current.image}
                    alt={current.label}
                    fill
                    sizes="(max-width: 768px) 100vw, 50vw"
                    className="object-cover"
                    priority
                  />
                  {/* Gradient overlay */}
                  <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent" />

                  {/* Vibe badge */}
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    className="absolute top-5 left-5"
                  >
                    <span
                      className="text-[0.6rem] font-bold uppercase tracking-widest px-3 py-1.5 rounded-full backdrop-blur-md"
                      style={{ background: `${current.accent}22`, color: current.accent, border: `1px solid ${current.accent}44` }}
                    >
                      {current.vibe}
                    </span>
                  </motion.div>

                  {/* Label */}
                  <motion.div
                    initial={{ opacity: 0, y: 12 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.18 }}
                    className="absolute bottom-0 left-0 right-0 p-6"
                  >
                    <h3 className="text-white text-2xl font-bold leading-tight"
                        style={{ fontFamily: "'Space Grotesk', sans-serif" }}>
                      {current.label}
                    </h3>
                    <p className="text-white/55 text-sm mt-1" style={{ fontFamily: "'Inter', sans-serif" }}>
                      {current.sublabel}
                    </p>
                  </motion.div>

                  {/* Accent border on active */}
                  <div
                    className="absolute inset-0 rounded-3xl pointer-events-none transition-all duration-500"
                    style={{ boxShadow: `inset 0 0 0 1px ${current.accent}30` }}
                  />
                </motion.div>
              </AnimatePresence>
            </div>

            {/* Controls row */}
            <div className="flex items-center justify-between">

              {/* Dot indicators */}
              <div className="flex gap-2">
                {destinations.map((d, i) => (
                  <button
                    key={i}
                    onClick={() => { setDirection(i > index ? 1 : -1); setIndex(i); }}
                    className="rounded-full transition-all duration-300 focus:outline-none"
                    style={{
                      width: i === index ? 24 : 8,
                      height: 8,
                      background: i === index ? current.accent : "rgba(255,255,255,0.2)",
                    }}
                    aria-label={`Go to ${destinations[i].label}`}
                  />
                ))}
              </div>

              {/* Arrow buttons */}
              <div className="flex gap-2">
                <button
                  onClick={() => go(-1)}
                  className="flex items-center justify-center h-10 w-10 rounded-2xl bg-white/5 border border-white/10 text-white/60 hover:text-white hover:bg-white/10 hover:border-white/20 transition-all"
                  aria-label="Previous"
                >
                  <ChevronLeft className="h-5 w-5" />
                </button>
                <button
                  onClick={() => go(1)}
                  className="flex items-center justify-center h-10 w-10 rounded-2xl bg-white/5 border border-white/10 text-white/60 hover:text-white hover:bg-white/10 hover:border-white/20 transition-all"
                  aria-label="Next"
                >
                  <ChevronRight className="h-5 w-5" />
                </button>
              </div>
            </div>

            {/* Thumbnail strip */}
            <div className="grid grid-cols-4 gap-2">
              {destinations.map((d, i) => (
                <button
                  key={i}
                  onClick={() => { setDirection(i > index ? 1 : -1); setIndex(i); }}
                  className="relative aspect-square rounded-xl overflow-hidden focus:outline-none"
                  style={{ opacity: i === index ? 1 : 0.45 }}
                >
                  <Image src={d.image} alt={d.label} fill sizes="10vw" className="object-cover transition-transform duration-300 hover:scale-110" />
                  {i === index && (
                    <div
                      className="absolute inset-0 rounded-xl"
                      style={{ boxShadow: `inset 0 0 0 2px ${d.accent}` }}
                    />
                  )}
                </button>
              ))}
            </div>

          </div>
        </div>
      </div>
    </section>
  );
}
