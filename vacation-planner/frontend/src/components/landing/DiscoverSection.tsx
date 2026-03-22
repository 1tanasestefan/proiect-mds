"use client";

import { motion } from "motion/react";
import Image from "next/image";
import { FadeUp } from "./FadeUp";

const destinations = [
  {
    label: "Hidden Beaches",
    sublabel: "Secret shores & turquoise water",
    image:
      "https://images.unsplash.com/photo-1679766826593-738e9b6338c6?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&q=80&w=800",
    accent: "#00F0FF",
  },
  {
    label: "Epic Viewpoints",
    sublabel: "Breathtaking panoramas",
    image:
      "https://images.unsplash.com/photo-1530122037265-a5f1f91d3b99?q=80&w=800&auto=format&fit=crop",
    accent: "#8A2BE2",
  },
  {
    label: "Local Cuisine",
    sublabel: "Flavors you can't find at home",
    image:
      "https://images.unsplash.com/photo-1643757343278-5d50309dfa44?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&q=80&w=800",
    accent: "#00F0FF",
  },
  {
    label: "Cultural Gems",
    sublabel: "Living history & sacred places",
    image:
      "https://images.unsplash.com/photo-1600209892743-c50f8091b231?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&q=80&w=800",
    accent: "#8A2BE2",
  },
];

const bullets = [
  "Hidden beaches that never make the lists.",
  "Local food spots only locals know.",
  "Epic viewpoints off the tourist trail.",
  "Cultural experiences that stay with you.",
];

interface CardProps {
  label: string;
  sublabel: string;
  image: string;
  accent: string;
  delay: number;
}

function DestCard({ label, sublabel, image, accent, delay }: CardProps) {
  return (
    <FadeUp delay={delay}>
      <motion.div
        whileHover={{ scale: 1.03, y: -6 }}
        transition={{ duration: 0.35, ease: "easeOut" }}
        className="relative overflow-hidden rounded-2xl aspect-square group cursor-pointer"
      >
        <Image
          src={image}
          alt={label}
          fill
          sizes="(max-width: 768px) 50vw, 20vw"
          className="object-cover transition-transform duration-700 group-hover:scale-110"
        />
        {/* Base overlay */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/85 via-black/30 to-transparent" />
        {/* Hover glow border */}
        <motion.div
          initial={{ opacity: 0 }}
          whileHover={{ opacity: 1 }}
          transition={{ duration: 0.3 }}
          className="absolute inset-0 rounded-2xl pointer-events-none"
          style={{
            boxShadow: `inset 0 0 0 1px ${accent}50, 0 0 40px ${accent}18`,
          }}
        />
        {/* Label */}
        <div className="absolute bottom-0 left-0 right-0 p-4">
          <p
            className="text-white font-bold text-sm"
            style={{ fontFamily: "'Space Grotesk', sans-serif" }}
          >
            {label}
          </p>
          <p
            className="text-white/50 text-xs mt-0.5"
            style={{ fontFamily: "'Inter', sans-serif" }}
          >
            {sublabel}
          </p>
        </div>
      </motion.div>
    </FadeUp>
  );
}

export function DiscoverSection() {
  return (
    <section className="relative bg-[#060606] overflow-hidden py-36 px-6 md:px-12">
      {/* Background orb */}
      <div className="absolute top-1/2 right-0 -translate-y-1/2 h-[700px] w-[400px] rounded-full bg-[#00F0FF]/4 blur-[220px] pointer-events-none" />
      <div className="absolute bottom-0 left-1/4 h-[400px] w-[400px] rounded-full bg-[#8A2BE2]/4 blur-[200px] pointer-events-none" />

      <div className="relative z-10 max-w-7xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 xl:gap-24 items-center">

          {/* Left: Text */}
          <div>
            <FadeUp>
              <p
                className="text-[#8A2BE2]/60 text-[0.65rem] uppercase tracking-[0.3em] mb-6 font-medium"
                style={{ fontFamily: "'Inter', sans-serif" }}
              >
                Curated by AI
              </p>
            </FadeUp>

            <FadeUp delay={0.1}>
              <h2
                className="text-[clamp(2.8rem,6vw,5.5rem)] font-black leading-[0.9] mb-10 text-white"
                style={{ fontFamily: "'Archivo Black', sans-serif" }}
              >
                Discover places
                <br />
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
                    <p
                      className="text-white/55 text-lg leading-snug"
                      style={{ fontFamily: "'Inter', sans-serif" }}
                    >
                      {line}
                    </p>
                  </div>
                </FadeUp>
              ))}
            </div>

            <FadeUp delay={0.65}>
              <p
                className="text-white/25 text-base leading-relaxed max-w-sm"
                style={{ fontFamily: "'Inter', sans-serif" }}
              >
                Your next favorite place might be somewhere
                <br />
                you&apos;ve never even searched for.
              </p>
            </FadeUp>
          </div>

          {/* Right: 2×2 card grid */}
          <div className="grid grid-cols-2 gap-4">
            {destinations.map((dest, i) => (
              <DestCard key={dest.label} {...dest} delay={0.15 + i * 0.1} />
            ))}
          </div>

        </div>
      </div>
    </section>
  );
}
