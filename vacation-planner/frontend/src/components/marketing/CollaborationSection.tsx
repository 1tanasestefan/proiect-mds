"use client";

import { FadeUp } from "@/components/landing/FadeUp";
import { motion } from "motion/react";
import { Link2, MessageCircle, ThumbsUp, Bell } from "lucide-react";

const ACTIVITIES = [
  {
    color: "#00F0FF",
    char: "A",
    name: "Alex",
    action: "added Eiffel Tower to Day 1 🗼",
    time: "2m ago",
  },
  {
    color: "#8A2BE2",
    char: "S",
    name: "Sarah",
    action: "voted for the boat tour 🚢",
    time: "5m ago",
  },
  {
    color: "#F59E0B",
    char: "M",
    name: "Mike",
    action: "commented on hotel options",
    time: "12m ago",
  },
];

const COLLAB_FEATURES = [
  {
    icon: Link2,
    label: "Invite with a link",
    desc: "Share a private trip link with anyone in seconds.",
  },
  {
    icon: ThumbsUp,
    label: "Vote on activities",
    desc: "Let everyone weigh in on what to do each day.",
  },
  {
    icon: MessageCircle,
    label: "Leave comments",
    desc: "Discuss ideas right inside the itinerary.",
  },
  {
    icon: Bell,
    label: "Real-time updates",
    desc: "Everyone sees changes the moment they happen.",
  },
];

export function CollaborationSection() {
  return (
    <section className="relative bg-[#020204] overflow-hidden py-32 px-6 md:px-12">
      {/* Ambient */}
      <div className="absolute top-0 left-0 h-[600px] w-[600px] rounded-full bg-[#00F0FF]/5 blur-[220px] pointer-events-none" />
      <div className="absolute bottom-0 right-0 h-[400px] w-[400px] rounded-full bg-[#8A2BE2]/5 blur-[200px] pointer-events-none" />

      <div className="relative z-10 max-w-7xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 xl:gap-24 items-center">

          {/* ── Left: Text ── */}
          <div>
            <FadeUp>
              <p
                className="text-[#00F0FF]/50 text-[0.65rem] uppercase tracking-[0.35em] mb-5 font-medium"
                style={{ fontFamily: "'Inter', sans-serif" }}
              >
                Better together
              </p>
            </FadeUp>

            <FadeUp delay={0.1}>
              <h2
                className="font-black text-white leading-[1.0] mb-6"
                style={{
                  fontFamily: "'Archivo Black', sans-serif",
                  fontSize: "clamp(2rem, 4vw, 4rem)",
                }}
              >
                Plan as a team,
                <br />
                <span className="bg-gradient-to-r from-[#00F0FF] to-[#8A2BE2] bg-clip-text text-transparent">
                  travel in sync.
                </span>
              </h2>
            </FadeUp>

            <FadeUp delay={0.2}>
              <p
                className="text-white/38 text-lg leading-relaxed mb-10 max-w-md"
                style={{ fontFamily: "'Inter', sans-serif" }}
              >
                Invite friends and family to co-plan in real time. Everyone
                gets a voice — no endless group chats, no lost details.
              </p>
            </FadeUp>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
              {COLLAB_FEATURES.map((feat, i) => (
                <FadeUp key={i} delay={0.25 + i * 0.07}>
                  <div className="flex items-start gap-3">
                    <div className="h-9 w-9 rounded-xl bg-[#00F0FF]/10 flex items-center justify-center flex-shrink-0 mt-0.5">
                      <feat.icon className="h-4 w-4 text-[#00F0FF]" />
                    </div>
                    <div>
                      <p
                        className="text-white/80 text-sm font-semibold mb-0.5"
                        style={{ fontFamily: "'Space Grotesk', sans-serif" }}
                      >
                        {feat.label}
                      </p>
                      <p
                        className="text-white/32 text-xs leading-relaxed"
                        style={{ fontFamily: "'Inter', sans-serif" }}
                      >
                        {feat.desc}
                      </p>
                    </div>
                  </div>
                </FadeUp>
              ))}
            </div>
          </div>

          {/* ── Right: Collaboration UI mockup ── */}
          <FadeUp delay={0.15}>
            <div className="rounded-[24px] bg-[#08080f] border border-white/8 overflow-hidden shadow-[0_32px_80px_rgba(0,0,0,0.65)]">
              {/* Header */}
              <div className="px-6 py-5 border-b border-white/[0.06] flex items-center justify-between">
                <div>
                  <p
                    className="text-white font-semibold text-sm"
                    style={{ fontFamily: "'Space Grotesk', sans-serif" }}
                  >
                    Paris Trip · Spring 2025
                  </p>
                  <p
                    className="text-white/28 text-xs mt-0.5"
                    style={{ fontFamily: "'Inter', sans-serif" }}
                  >
                    3 collaborators · shared edit access
                  </p>
                </div>
                <div className="flex -space-x-2">
                  {[
                    ["#00F0FF", "A"],
                    ["#8A2BE2", "S"],
                    ["#F59E0B", "M"],
                  ].map(([c, ch], i) => (
                    <div
                      key={i}
                      className="h-8 w-8 rounded-full border-2 flex items-center justify-center text-[10px] font-bold"
                      style={{
                        backgroundColor: c + "25",
                        borderColor: "#08080f",
                        color: c,
                      }}
                    >
                      {ch}
                    </div>
                  ))}
                </div>
              </div>

              {/* Activity feed */}
              <div className="p-6 space-y-4">
                {ACTIVITIES.map((act, i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, x: -14 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.5 + i * 0.22, duration: 0.55 }}
                    className="flex items-start gap-3"
                  >
                    <div
                      className="h-8 w-8 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0 mt-0.5"
                      style={{
                        backgroundColor: act.color + "22",
                        color: act.color,
                      }}
                    >
                      {act.char}
                    </div>
                    <div className="flex-1 bg-white/[0.03] rounded-xl px-4 py-3 border border-white/[0.06]">
                      <p
                        className="text-white/72 text-sm"
                        style={{ fontFamily: "'Inter', sans-serif" }}
                      >
                        <span className="font-semibold text-white/88">
                          {act.name}
                        </span>{" "}
                        {act.action}
                      </p>
                      <p
                        className="text-white/22 text-xs mt-1"
                        style={{ fontFamily: "'Inter', sans-serif" }}
                      >
                        {act.time}
                      </p>
                    </div>
                  </motion.div>
                ))}
              </div>

              {/* Comment input */}
              <div className="px-6 pb-6">
                <div className="flex items-center gap-3 bg-white/[0.03] rounded-xl px-4 py-3 border border-white/8">
                  <MessageCircle className="h-4 w-4 text-white/18 flex-shrink-0" />
                  <span
                    className="text-white/22 text-sm flex-1"
                    style={{ fontFamily: "'Inter', sans-serif" }}
                  >
                    Add a comment...
                  </span>
                  <span
                    className="text-[#00F0FF]/55 text-xs font-semibold cursor-pointer hover:text-[#00F0FF]/80 transition-colors"
                    style={{ fontFamily: "'Inter', sans-serif" }}
                  >
                    Send
                  </span>
                </div>
              </div>
            </div>
          </FadeUp>
        </div>
      </div>
    </section>
  );
}
