"use client";

import { FadeUp } from "./FadeUp";

const lines: { text: string; accent: string | null; after: string | null }[] = [
  { text: "Every journey begins with a spark of ", accent: "curiosity", after: "." },
  { text: "A place you've never seen.", accent: null, after: null },
  { text: "A culture you've never experienced.", accent: null, after: null },
  { text: "A ", accent: "memory", after: " waiting to happen." },
];

export function InspirationSection() {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-[#FFF6E8] py-40 px-6">
      {/* Background orbs */}
      <div className="absolute top-1/4 left-1/4 h-[560px] w-[560px] rounded-full bg-[#FF6B5A]/8 blur-[200px] pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 h-[400px] w-[400px] rounded-full bg-[#FF9F43]/8 blur-[180px] pointer-events-none" />

      {/* Top fade from hero */}
      <div className="absolute top-0 inset-x-0 h-32 bg-gradient-to-b from-[#FFF6E8] to-transparent pointer-events-none" />

      <div className="relative z-10 max-w-4xl mx-auto text-center">
        {/* Eyebrow */}
        <FadeUp>
          <p
            className="text-[#FF6B5A]/60 text-[0.65rem] uppercase tracking-[0.3em] mb-10 font-medium"
            style={{ fontFamily: "'Inter', sans-serif" }}
          >
            The VibeTrips Philosophy
          </p>
        </FadeUp>

        {/* Heading */}
        <FadeUp delay={0.1}>
          <h2
            className="text-[clamp(3rem,8vw,6.5rem)] font-black leading-[0.9] mb-20 text-[#10223A]"
            style={{ fontFamily: "'Archivo Black', sans-serif" }}
          >
            Travel isn&apos;t just
            <br />
            about{" "}
              <span className="bg-gradient-to-r from-[#FF6B5A] to-[#FF9F43] bg-clip-text text-transparent">
              destinations
            </span>
          </h2>
        </FadeUp>

        {/* Staggered lines */}
        <div className="space-y-6 mb-14">
          {lines.map((line, i) => (
            <FadeUp key={i} delay={0.22 + i * 0.12}>
              <p
                className="text-xl md:text-2xl text-[#64748B] leading-relaxed"
                style={{ fontFamily: "'Inter', sans-serif" }}
              >
                {line.accent ? (
                  <>
                    {line.text}
                    <span className="bg-gradient-to-r from-[#FF6B5A] to-[#FF9F43] bg-clip-text text-transparent font-semibold">
                      {line.accent}
                    </span>
                    {line.after}
                  </>
                ) : (
                  line.text
                )}
              </p>
            </FadeUp>
          ))}
        </div>

        {/* Closing */}
        <FadeUp delay={0.78}>
          <p
            className="text-lg text-[#64748B]/50 max-w-md mx-auto leading-relaxed"
            style={{ fontFamily: "'Inter', sans-serif" }}
          >
            VibeTrips helps you turn those sparks into real{" "}
            <span className="text-[#10223A]/70 font-medium">adventures</span>.
          </p>
        </FadeUp>
      </div>
    </section>
  );
}
