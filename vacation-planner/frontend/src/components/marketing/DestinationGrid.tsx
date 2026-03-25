"use client";

import { FadeUp } from "@/components/landing/FadeUp";
import { motion } from "motion/react";
import Image from "next/image";
import { ArrowRight } from "lucide-react";

const DESTINATIONS = [
  {
    label: "Beach Escapes",
    sub: "Sun, sand & turquoise water",
    image:
      "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&auto=format&fit=crop&q=80",
    color: "#00F0FF",
  },
  {
    label: "City Breaks",
    sub: "Urban culture & vibrant nightlife",
    image:
      "https://images.unsplash.com/photo-1514565131-fce0801e6b2e?w=800&auto=format&fit=crop&q=80",
    color: "#8A2BE2",
  },
  {
    label: "Mountain Retreats",
    sub: "Fresh air & breathtaking vistas",
    image:
      "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=800&auto=format&fit=crop&q=80",
    color: "#00F0FF",
  },
  {
    label: "Romantic Getaways",
    sub: "Unforgettable moments for two",
    image:
      "https://images.unsplash.com/photo-1499856871958-5b9627545d1a?w=800&auto=format&fit=crop&q=80",
    color: "#EF4444",
  },
  {
    label: "Family Adventures",
    sub: "Memories that last a lifetime",
    image:
      "https://images.unsplash.com/photo-1528360983277-13d401cdc186?w=800&auto=format&fit=crop&q=80",
    color: "#F59E0B",
  },
  {
    label: "Food & Culture",
    sub: "Eat, explore, and discover",
    image:
      "https://images.unsplash.com/photo-1504754524776-8f4f37790ca0?w=800&auto=format&fit=crop&q=80",
    color: "#10B981",
  },
];

type Destination = (typeof DESTINATIONS)[0];

function DestCard({ label, sub, image, color }: Destination) {
  return (
    <motion.div
      whileHover={{ scale: 1.025, y: -5 }}
      transition={{ duration: 0.35, ease: "easeOut" }}
      className="relative aspect-[4/3] rounded-[20px] overflow-hidden group cursor-pointer"
    >
      <Image
        src={image}
        alt={label}
        fill
        sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
        className="object-cover transition-transform duration-700 group-hover:scale-110"
      />

      {/* Base gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-t from-black/88 via-black/25 to-transparent" />

      {/* Color wash on hover */}
      <div
        className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500"
        style={{
          background: `linear-gradient(to top, ${color}28, transparent 55%)`,
        }}
      />

      {/* Border glow on hover */}
      <div
        className="absolute inset-0 rounded-[20px] opacity-0 group-hover:opacity-100 transition-opacity duration-500"
        style={{ boxShadow: `inset 0 0 0 1px ${color}30` }}
      />

      {/* Content */}
      <div className="absolute bottom-0 left-0 right-0 p-5 flex items-end justify-between">
        <div>
          <p
            className="text-white font-bold text-[1.05rem] leading-tight"
            style={{ fontFamily: "'Space Grotesk', sans-serif" }}
          >
            {label}
          </p>
          <p
            className="text-white/45 text-xs mt-1"
            style={{ fontFamily: "'Inter', sans-serif" }}
          >
            {sub}
          </p>
        </div>
        <div className="h-9 w-9 rounded-full bg-white/10 border border-white/15 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all duration-300 translate-x-2 group-hover:translate-x-0">
          <ArrowRight className="h-4 w-4 text-white" />
        </div>
      </div>
    </motion.div>
  );
}

export function DestinationGrid() {
  return (
    <section
      id="destinations"
      className="relative bg-[#020204] overflow-hidden py-32 px-6 md:px-12"
    >
      {/* Ambient */}
      <div className="absolute bottom-0 right-0 h-[600px] w-[600px] rounded-full bg-[#8A2BE2]/5 blur-[230px] pointer-events-none" />
      <div className="absolute top-0 left-0 h-[400px] w-[400px] rounded-full bg-[#00F0FF]/4 blur-[200px] pointer-events-none" />

      <div className="relative z-10 max-w-7xl mx-auto">
        {/* Header row */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-8 mb-14">
          <div>
            <FadeUp>
              <p
                className="text-[#8A2BE2]/50 text-[0.65rem] uppercase tracking-[0.35em] mb-5 font-medium"
                style={{ fontFamily: "'Inter', sans-serif" }}
              >
                Inspiration awaits
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
                Discover where
                <br />
                you want to{" "}
                <span className="bg-gradient-to-r from-[#00F0FF] to-[#8A2BE2] bg-clip-text text-transparent">
                  go next.
                </span>
              </h2>
            </FadeUp>
          </div>
          <FadeUp delay={0.2}>
            <p
              className="text-white/32 text-base max-w-xs leading-relaxed"
              style={{ fontFamily: "'Inter', sans-serif" }}
            >
              Browse by travel style. Our AI knows the best spots in every
              category.
            </p>
          </FadeUp>
        </div>

        {/* Destination grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {DESTINATIONS.map((dest, i) => (
            <FadeUp key={i} delay={0.06 * i}>
              <DestCard {...dest} />
            </FadeUp>
          ))}
        </div>
      </div>
    </section>
  );
}
