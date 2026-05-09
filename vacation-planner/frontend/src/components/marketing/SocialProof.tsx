"use client";

import { FadeUp } from "@/components/landing/FadeUp";
import { Star } from "lucide-react";

const STATS = [
  { value: "50k+",  label: "Trips Planned" },
  { value: "120+",  label: "Countries" },
  { value: "4.9 ★", label: "Avg Rating" },
  { value: "2 min", label: "Setup Time" },
];

const AVATARS = [
  { char: "A", color: "#FF6B5A" },
  { char: "S", color: "#FF9F43" },
  { char: "M", color: "#FF8FA3" },
  { char: "R", color: "#FFC1A1" },
  { char: "T", color: "#2EC4B6" },
  { char: "J", color: "#FFD166" },
];

export function SocialProof() {
  return (
    <section className="relative bg-[#FFFBF3] border-y border-[rgba(255,107,90,0.12)] overflow-hidden py-10 px-6">
      {/* Subtle gradient wash */}
      <div className="absolute inset-0 bg-gradient-to-r from-[#FF6B5A]/4 via-transparent to-[#FF9F43]/4 pointer-events-none" />

      <div className="relative z-10 max-w-6xl mx-auto">
        <FadeUp>
          <div className="flex flex-col md:flex-row items-center justify-between gap-10">

            {/* Left: avatar cluster + star rating */}
            <div className="flex items-center gap-5">
              <div className="flex -space-x-3">
                {AVATARS.map((av, i) => (
                  <div
                    key={i}
                    className="h-9 w-9 rounded-full border-2 border-[#FFFBF3] flex items-center justify-center text-[11px] font-bold"
                    style={{ backgroundColor: av.color + "22", color: av.color }}
                  >
                    {av.char}
                  </div>
                ))}
              </div>
              <div>
                <p
                  className="text-[#10223A]/80 text-sm font-semibold"
                  style={{ fontFamily: "'Space Grotesk', sans-serif" }}
                >
                  Trusted by travelers worldwide
                </p>
                <div className="flex items-center gap-1 mt-1">
                  {Array.from({ length: 5 }).map((_, i) => (
                    <Star
                      key={i}
                      className="h-3 w-3 fill-[#F59E0B] text-[#F59E0B]"
                    />
                  ))}
                  <span
                    className="text-[#64748B]/60 text-xs ml-1.5"
                    style={{ fontFamily: "'Inter', sans-serif" }}
                  >
                    4.9 out of 5
                  </span>
                </div>
              </div>
            </div>

            {/* Right: stats */}
            <div className="flex items-center gap-8 md:gap-14 flex-wrap justify-center">
              {STATS.map((stat, i) => (
                <div key={i} className="text-center">
                  <p
                    className="font-black text-white leading-none"
                    style={{
                      fontFamily: "'Archivo Black', sans-serif",
                      fontSize: "clamp(1.4rem, 3vw, 2rem)",
                    }}
                  >
                    <span className="bg-gradient-to-r from-[#FF6B5A] to-[#FF9F43] bg-clip-text text-transparent">
                      {stat.value}
                    </span>
                  </p>
                  <p
                    className="text-[#64748B]/50 text-xs mt-1 whitespace-nowrap"
                    style={{ fontFamily: "'Inter', sans-serif" }}
                  >
                    {stat.label}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </FadeUp>
      </div>
    </section>
  );
}
