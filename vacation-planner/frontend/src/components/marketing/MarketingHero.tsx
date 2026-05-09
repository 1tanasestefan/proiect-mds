"use client";

import { useRouter } from "next/navigation";
import { motion } from "motion/react";
import {
  Sparkles,
  Play,
  MapPin,
  Wallet,
  Cloud,
  CheckCircle2,
} from "lucide-react";

interface MarketingHeroProps {
  onStartPlanning?: () => void;
}

const ITINERARY = [
  { time: "9:00 am",  place: "Eiffel Tower",        dot: "#FF6B5A" },
  { time: "12:30 pm", place: "Le Jules Verne",       dot: "#FF9F43" },
  { time: "3:00 pm",  place: "Musée d'Orsay",        dot: "#FF8FA3" },
  { time: "7:30 pm",  place: "Montmartre Wine Bar",  dot: "#FF9F43" },
];

const AVATARS = [
  { char: "A", color: "#FF6B5A" },
  { char: "S", color: "#FF9F43" },
  { char: "M", color: "#FF8FA3" },
  { char: "R", color: "#FFC1A1" },
  { char: "T", color: "#2EC4B6" },
];

export function MarketingHero({ onStartPlanning }: MarketingHeroProps) {
  const router = useRouter();
  const handleStartPlanning = onStartPlanning ?? (() => router.push("/plan"));
  return (
    <section
      id="hero"
      className="relative min-h-screen flex items-center overflow-hidden bg-[#FFF6E8]"
    >
      {/* ── Ambient background ── */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-[20%] left-[28%] h-[700px] w-[700px] rounded-full bg-[#FF6B5A]/8 blur-[200px]" />
        <div className="absolute bottom-[20%] right-[18%] h-[550px] w-[550px] rounded-full bg-[#FF9F43]/8 blur-[180px]" />
        <div className="absolute top-0 right-0 h-[320px] w-[320px] rounded-full bg-[#FFC1A1]/6 blur-[130px]" />
        {/* Grid texture */}
        <div
          className="absolute inset-0 opacity-[0.022]"
          style={{
            backgroundImage:
              "linear-gradient(rgba(16,34,58,0.06) 1px, transparent 1px), linear-gradient(90deg, rgba(16,34,58,0.06) 1px, transparent 1px)",
            backgroundSize: "72px 72px",
          }}
        />
      </div>

      <div className="relative z-10 max-w-7xl mx-auto w-full px-6 md:px-12 pt-36 pb-24">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 xl:gap-24 items-center">

          {/* ── Left: Copy ── */}
          <div>
            {/* Badge */}
            <div
              className="reveal-up mb-8 inline-block"
              style={{
                "--reveal-delay": "0ms",
                "--reveal-duration": "800ms",
                "--reveal-y": "16px",
              } as React.CSSProperties}
            >
              <span
                className="inline-flex items-center gap-2.5 px-4 py-2 rounded-full border border-[#FF6B5A]/25 bg-[#FF6B5A]/8 text-[#FF6B5A] text-xs font-semibold tracking-widest uppercase"
                style={{ fontFamily: "'Inter', sans-serif" }}
              >
                <span className="h-1.5 w-1.5 rounded-full bg-[#FF6B5A] animate-pulse" />
                AI-Powered Travel Planning
              </span>
            </div>

            {/* Headline */}
            <h1
              className="reveal-up font-black text-[#10223A] mb-7 leading-[1.02]"
              style={{
                fontFamily: "var(--font-playfair), Georgia, serif",
                fontSize: "clamp(2.6rem, 5vw, 5.2rem)",
                fontWeight: 700,
                "--reveal-delay": "80ms",
                "--reveal-duration": "1000ms",
                "--reveal-y": "28px",
              } as React.CSSProperties}
            >
              Plan unforgettable
              <br />
              trips,{" "}
              <span className="bg-gradient-to-r from-[#FF6B5A] to-[#FF9F43] bg-clip-text text-transparent">
                without
              </span>
              <br />
              the chaos.
            </h1>

            {/* Subtext */}
            <p
              className="reveal-up text-lg md:text-xl text-[#64748B] leading-relaxed mb-10 max-w-[490px]"
              style={{
                fontFamily: "'Inter', sans-serif",
                "--reveal-delay": "200ms",
                "--reveal-duration": "900ms",
                "--reveal-y": "22px",
              } as React.CSSProperties}
            >
              AI-powered planning that turns your travel dreams into organized
              reality. Itineraries, bookings, maps, and your whole crew — all
              in one place.
            </p>

            {/* CTAs */}
            <div
              className="reveal-up flex flex-col sm:flex-row items-start gap-4 mb-12"
              style={{
                "--reveal-delay": "320ms",
                "--reveal-duration": "900ms",
                "--reveal-y": "18px",
              } as React.CSSProperties}
            >
              <motion.button
                onClick={handleStartPlanning}
                whileHover={{ scale: 1.03 }}
                whileTap={{ scale: 0.98 }}
                transition={{ duration: 0.22, ease: "easeOut" }}
                className="relative group overflow-hidden rounded-full px-8 py-4 font-bold text-white text-base flex items-center gap-2.5 shadow-[0_4px_24px_rgba(255,107,90,0.35)]"
                style={{ fontFamily: "'Space Grotesk', sans-serif" }}
              >
                <span className="absolute inset-0 bg-gradient-to-r from-[#FF6B5A] to-[#FF9F43]" />
                <span className="absolute inset-0 bg-gradient-to-r from-[#FF9F43] to-[#FF6B5A] opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                <span className="relative z-10 flex items-center gap-2.5">
                  <Sparkles className="h-4 w-4" />
                  Start Planning — Free
                </span>
              </motion.button>

              <motion.button
                whileHover={{ scale: 1.03 }}
                whileTap={{ scale: 0.97 }}
                className="flex items-center gap-3 px-6 py-4 rounded-full border border-[rgba(255,107,90,0.22)] bg-[#FF6B5A]/4 text-[#10223A]/60 hover:text-[#10223A]/80 hover:border-[#FF6B5A]/30 hover:bg-[#FF6B5A]/8 font-medium text-base transition-all duration-300"
                style={{ fontFamily: "'Space Grotesk', sans-serif" }}
              >
                <span className="flex items-center justify-center h-7 w-7 rounded-full bg-[#FF6B5A]/12">
                  <Play className="h-3 w-3 ml-0.5 fill-current" />
                </span>
                See how it works
              </motion.button>
            </div>

            {/* Social proof micro-strip */}
            <div
              className="reveal-up flex items-center gap-4"
              style={{
                "--reveal-delay": "440ms",
                "--reveal-duration": "900ms",
                "--reveal-y": "14px",
              } as React.CSSProperties}
            >
              <div className="flex -space-x-2.5">
                {AVATARS.map((av, i) => (
                  <div
                    key={i}
                    className="h-8 w-8 rounded-full border-2 flex items-center justify-center text-[10px] font-bold"
                    style={{
                      backgroundColor: av.color + "25",
                      borderColor: "#FFF6E8",
                      color: av.color,
                    }}
                  >
                    {av.char}
                  </div>
                ))}
              </div>
              <p
                className="text-[#64748B]/60 text-sm"
                style={{ fontFamily: "'Inter', sans-serif" }}
              >
                <span className="text-[#10223A]/70 font-semibold">50,000+</span>{" "}
                trips planned this year
              </p>
            </div>
          </div>

          {/* ── Right: Dashboard Mockup ── */}
          <div
            className="reveal-up hidden lg:flex items-center justify-center"
            style={{
              "--reveal-delay": "180ms",
              "--reveal-duration": "1100ms",
              "--reveal-y": "36px",
            } as React.CSSProperties}
          >
            <DashboardMockup />
          </div>
        </div>
      </div>

      {/* Bottom fade */}
      <div className="absolute bottom-0 inset-x-0 h-24 bg-gradient-to-t from-[#FFF6E8] to-transparent pointer-events-none" />
    </section>
  );
}

function DashboardMockup() {
  return (
    <div className="relative w-full max-w-[460px]">
      {/* ── Main card ── */}
      <motion.div
        animate={{ y: [0, -8, 0] }}
        transition={{ duration: 6, repeat: Infinity, ease: "easeInOut" }}
        className="relative z-10 rounded-[24px] bg-[#FFFBF3] border border-[rgba(255,107,90,0.18)] shadow-[0_32px_80px_rgba(16,34,58,0.12),0_0_0_1px_rgba(255,107,90,0.06)] overflow-hidden"
      >
        {/* Card header */}
        <div className="px-6 pt-5 pb-4 border-b border-[rgba(255,107,90,0.10)]">
          <div className="flex items-center justify-between mb-1">
            <div className="flex items-center gap-2">
              <MapPin className="h-4 w-4 text-[#FF6B5A]" />
              <span
                className="text-[#10223A] font-semibold text-base"
                style={{ fontFamily: "'Space Grotesk', sans-serif" }}
              >
                Paris in Spring
              </span>
            </div>
            <span
              className="text-[10px] text-[#64748B] px-2 py-0.5 rounded-full bg-[rgba(255,107,90,0.08)] border border-[rgba(255,107,90,0.14)]"
              style={{ fontFamily: "'Inter', sans-serif" }}
            >
              Apr 15–18
            </span>
          </div>
          <p
            className="text-[#64748B] text-xs"
            style={{ fontFamily: "'Inter', sans-serif" }}
          >
            2 travelers · 4 days
          </p>
        </div>

        {/* Day 1 timeline */}
        <div className="px-6 py-4">
          <p
            className="text-[10px] text-[#FF6B5A]/70 uppercase tracking-widest mb-3.5 font-medium"
            style={{ fontFamily: "'Inter', sans-serif" }}
          >
            Day 1 — Monday
          </p>
          <div className="space-y-3">
            {ITINERARY.map((item, i) => (
              <div key={i} className="flex items-start gap-3">
                <div className="flex flex-col items-center flex-shrink-0 pt-[5px]">
                  <div
                    className="h-2 w-2 rounded-full"
                    style={{ backgroundColor: item.dot }}
                  />
                  {i < ITINERARY.length - 1 && (
                    <div className="w-px h-5 bg-[rgba(255,107,90,0.15)] mt-1" />
                  )}
                </div>
                <div className="flex-1 flex items-center justify-between">
                  <span
                    className="text-[#10223A] text-sm font-medium"
                    style={{ fontFamily: "'Inter', sans-serif" }}
                  >
                    {item.place}
                  </span>
                  <span
                    className="text-[#64748B]/60 text-xs"
                    style={{ fontFamily: "'Inter', sans-serif" }}
                  >
                    {item.time}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Budget bar */}
        <div className="px-6 py-3 bg-[rgba(255,107,90,0.04)] border-t border-b border-[rgba(255,107,90,0.10)]">
          <div className="flex items-center justify-between mb-2">
            <span
              className="text-[#64748B] text-xs flex items-center gap-1.5"
              style={{ fontFamily: "'Inter', sans-serif" }}
            >
              <Wallet className="h-3 w-3" />
              Budget
            </span>
            <span
              className="text-[#10223A] text-xs font-medium"
              style={{ fontFamily: "'Inter', sans-serif" }}
            >
              $420{" "}
              <span className="text-[#64748B]/50">/ $600</span>
            </span>
          </div>
          <div className="h-1.5 rounded-full bg-[rgba(255,107,90,0.12)] overflow-hidden">
            <motion.div
              className="h-full rounded-full bg-gradient-to-r from-[#FF6B5A] to-[#FF9F43]"
              initial={{ width: "0%" }}
              animate={{ width: "70%" }}
              transition={{ duration: 1.5, delay: 0.9, ease: "easeOut" }}
            />
          </div>
        </div>

        {/* Bottom strip */}
        <div className="px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2 text-[#64748B]">
            <Cloud className="h-3.5 w-3.5" />
            <span
              className="text-xs"
              style={{ fontFamily: "'Inter', sans-serif" }}
            >
              21°C · Sunny
            </span>
          </div>
          <div className="flex items-center gap-1.5 text-[#FF9F43]">
            <span className="text-xs font-medium" style={{ fontFamily: "'Inter', sans-serif" }}>
              ★ 14 saved places
            </span>
          </div>
        </div>
      </motion.div>

      {/* ── Floating card: Collaboration ── */}
      <motion.div
        animate={{ y: [0, 6, 0] }}
        transition={{ duration: 5, repeat: Infinity, ease: "easeInOut", delay: 1 }}
        className="absolute -bottom-10 -left-10 z-20 rounded-2xl bg-[#FFFBF3] border border-[rgba(255,107,90,0.18)] p-4 shadow-[0_16px_40px_rgba(16,34,58,0.12)] flex items-center gap-3"
      >
        <div className="flex -space-x-2">
          {[["#FF6B5A", "A"], ["#FF9F43", "M"], ["#2EC4B6", "S"]].map(
            ([c, ch], i) => (
              <div
                key={i}
                className="h-7 w-7 rounded-full border-2 flex items-center justify-center text-[9px] font-bold"
                style={{
                  backgroundColor: c + "20",
                  borderColor: "#FFFBF3",
                  color: c,
                }}
              >
                {ch}
              </div>
            )
          )}
        </div>
        <div>
          <p
            className="text-[#10223A] text-xs font-semibold"
            style={{ fontFamily: "'Space Grotesk', sans-serif" }}
          >
            3 planning together
          </p>
          <p
            className="text-[#64748B] text-[10px]"
            style={{ fontFamily: "'Inter', sans-serif" }}
          >
            Sarah just joined
          </p>
        </div>
      </motion.div>

      {/* ── Floating card: Confirmation ── */}
      <motion.div
        animate={{ y: [0, -6, 0] }}
        transition={{ duration: 4, repeat: Infinity, ease: "easeInOut", delay: 0.5 }}
        className="absolute -top-8 -right-8 z-20 rounded-2xl bg-[#FFFBF3] border border-[rgba(46,196,182,0.25)] p-3.5 shadow-[0_16px_40px_rgba(16,34,58,0.10)] flex items-center gap-2.5"
      >
        <div className="h-8 w-8 rounded-xl bg-[#10B981]/15 flex items-center justify-center flex-shrink-0">
          <CheckCircle2 className="h-4 w-4 text-[#10B981]" />
        </div>
        <div>
          <p
            className="text-[#10223A] text-xs font-semibold whitespace-nowrap"
            style={{ fontFamily: "'Space Grotesk', sans-serif" }}
          >
            Flights booked ✓
          </p>
          <p
            className="text-[#10B981]/55 text-[10px]"
            style={{ fontFamily: "'Inter', sans-serif" }}
          >
            CDG · Apr 15, 6:45 am
          </p>
        </div>
      </motion.div>
    </div>
  );
}
