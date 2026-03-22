import { motion } from "motion/react";
import { Brain, Plane, Sparkles } from "lucide-react";
import { useEffect, useRef, useState } from "react";

const PHASES = [
  { label: "Experience Guide: Initializing destination analysis...", agent: "experience" },
  { label: "Logistics Agent: Checking flight availability and weather data...", agent: "logistics" },
  { label: "Experience Guide: Searching for hidden gems and local favorites...", agent: "experience" },
  { label: "Logistics Agent: Optimizing travel routes and transit times...", agent: "logistics" },
  { label: "Experience Guide: Curating exclusive dining and cultural events...", agent: "experience" },
  { label: "Multi-Agent: Synchronizing itinerary components...", agent: "both" },
  { label: "Experience Guide: Finalizing your luxury vibe summary...", agent: "experience" },
  { label: "Logistics Agent: Calculating estimated budget windows...", agent: "logistics" },
  { label: "System: Generating your cinematic travel preview...", agent: "both" },
] as const;

export function AIProcessing({ onComplete }: { onComplete?: () => void }) {
  const [progress, setProgress] = useState(0);
  const [currentPhase, setCurrentPhase] = useState(0);
  const completedRef = useRef(false);
  const onCompleteRef = useRef(onComplete);
  const shouldAutoCompleteRef = useRef(Boolean(onComplete));
  const currentPhaseRef = useRef(currentPhase);
  const intervalIdsRef = useRef<{ phase?: ReturnType<typeof setInterval>; progress?: ReturnType<typeof setInterval> }>({});

  useEffect(() => {
    onCompleteRef.current = onComplete;
    shouldAutoCompleteRef.current = Boolean(onComplete);
  }, [onComplete]);

  useEffect(() => {
    currentPhaseRef.current = currentPhase;
  }, [currentPhase]);

  useEffect(() => {
    const phaseInterval = setInterval(() => {
      setCurrentPhase((prev) => {
        if (prev < PHASES.length - 1) {
          return prev + 1;
        }
        return prev;
      });
    }, 4000); // 4 seconds per phase for better readability
    intervalIdsRef.current.phase = phaseInterval;

    const progressInterval = setInterval(() => {
      setProgress((prev) => {
        const shouldAutoComplete = shouldAutoCompleteRef.current;
        const isLastPhase = currentPhaseRef.current >= PHASES.length - 1;

        if (shouldAutoComplete && isLastPhase) {
          return prev >= 100 ? 100 : Math.min(100, prev + 1);
        }

        if (prev >= 98) {
          // If we reach 99, stay there but allow it to finish if the parent switches view
          return prev >= 99.5 ? 99.5 : prev + 0.05; 
        }
        return prev + 1;
      });
    }, 150);
    intervalIdsRef.current.progress = progressInterval;

    return () => {
      clearInterval(phaseInterval);
      clearInterval(progressInterval);
    };
  }, []); // Removed onComplete dependency to avoid unnecessary resets

  useEffect(() => {
    if (!shouldAutoCompleteRef.current) return;
    if (completedRef.current) return;

    const atEnd = currentPhase >= PHASES.length - 1 && progress >= 100;
    if (!atEnd) return;

    completedRef.current = true;
    if (intervalIdsRef.current.phase) clearInterval(intervalIdsRef.current.phase);
    if (intervalIdsRef.current.progress) clearInterval(intervalIdsRef.current.progress);

    const id = setTimeout(() => onCompleteRef.current?.(), 400);
    return () => clearTimeout(id);
  }, [currentPhase, progress]);

  return (
    <section className="min-h-screen bg-gray-50 dark:bg-[#050505] flex items-center justify-center px-8 relative overflow-hidden">
      {/* Animated background grid */}
      <div className="absolute inset-0 opacity-10 dark:opacity-20">
        <div className="absolute inset-0" style={{
          backgroundImage: `
            linear-gradient(rgba(0,240,255,0.1) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0,240,255,0.1) 1px, transparent 1px)
          `,
          backgroundSize: "50px 50px",
        }} />
      </div>

      {/* Glowing orbs */}
      <motion.div
        animate={{
          scale: [1, 1.2, 1],
          opacity: [0.3, 0.5, 0.3],
        }}
        transition={{ duration: 3, repeat: Infinity }}
        className="absolute top-1/3 left-1/4 h-96 w-96 rounded-full bg-[#00F0FF]/20 blur-[150px]"
      />
      <motion.div
        animate={{
          scale: [1, 1.3, 1],
          opacity: [0.3, 0.5, 0.3],
        }}
        transition={{ duration: 3, repeat: Infinity, delay: 1.5 }}
        className="absolute bottom-1/3 right-1/4 h-96 w-96 rounded-full bg-[#8A2BE2]/20 blur-[150px]"
      />

      <div className="relative z-10 max-w-4xl w-full">
        {/* Main AI Visualization */}
        <div className="flex items-center justify-center mb-16 relative h-64">
          {/* Experience Agent Orb - Left */}
          <motion.div
            animate={{
              y: [0, -20, 0],
              rotate: [0, 360],
            }}
            transition={{ 
              y: { duration: 3, repeat: Infinity, ease: "easeInOut" },
              rotate: { duration: 20, repeat: Infinity, ease: "linear" }
            }}
            className="absolute left-1/4 -translate-x-1/2"
          >
            <div className="relative">
              <div className="h-32 w-32 rounded-full bg-gradient-to-br from-[#8A2BE2] to-[#FF1493] shadow-[0_0_60px_rgba(138,43,226,0.6)] flex items-center justify-center">
                <Sparkles className="h-12 w-12 text-white" />
              </div>
              {/* Pulsing rings */}
              <motion.div
                animate={{ scale: [1, 1.5], opacity: [0.5, 0] }}
                transition={{ duration: 2, repeat: Infinity }}
                className="absolute inset-0 rounded-full border-2 border-[#8A2BE2]"
              />
              <motion.div
                animate={{ scale: [1, 1.5], opacity: [0.5, 0] }}
                transition={{ duration: 2, repeat: Infinity, delay: 1 }}
                className="absolute inset-0 rounded-full border-2 border-[#8A2BE2]"
              />
            </div>
            <motion.p 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-[#8A2BE2] text-sm text-center mt-4 font-semibold"
              style={{ fontFamily: "'Inter', sans-serif" }}
            >
              Experience Agent
            </motion.p>
          </motion.div>

          {/* Logistics Agent Orb - Right */}
          <motion.div
            animate={{
              y: [0, 20, 0],
              rotate: [360, 0],
            }}
            transition={{ 
              y: { duration: 3, repeat: Infinity, ease: "easeInOut" },
              rotate: { duration: 20, repeat: Infinity, ease: "linear" }
            }}
            className="absolute right-1/4 translate-x-1/2"
          >
            <div className="relative">
              <div className="h-32 w-32 rounded-full bg-gradient-to-br from-[#00F0FF] to-[#0080FF] shadow-[0_0_60px_rgba(0,240,255,0.6)] flex items-center justify-center">
                <Plane className="h-12 w-12 text-white" />
              </div>
              {/* Pulsing rings */}
              <motion.div
                animate={{ scale: [1, 1.5], opacity: [0.5, 0] }}
                transition={{ duration: 2, repeat: Infinity }}
                className="absolute inset-0 rounded-full border-2 border-[#00F0FF]"
              />
              <motion.div
                animate={{ scale: [1, 1.5], opacity: [0.5, 0] }}
                transition={{ duration: 2, repeat: Infinity, delay: 1 }}
                className="absolute inset-0 rounded-full border-2 border-[#00F0FF]"
              />
            </div>
            <motion.p 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-[#00F0FF] text-sm text-center mt-4 font-semibold"
              style={{ fontFamily: "'Inter', sans-serif" }}
            >
              Logistics Agent
            </motion.p>
          </motion.div>

          {/* Connecting energy streams */}
          <svg className="absolute inset-0 w-full h-full pointer-events-none">
            <motion.path
              d="M 0 128 Q 200 100, 400 128"
              stroke="url(#gradient1)"
              strokeWidth="2"
              fill="none"
              initial={{ pathLength: 0, opacity: 0 }}
              animate={{ pathLength: 1, opacity: 0.6 }}
              transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
            />
            <motion.path
              d="M 0 128 Q 200 156, 400 128"
              stroke="url(#gradient2)"
              strokeWidth="2"
              fill="none"
              initial={{ pathLength: 0, opacity: 0 }}
              animate={{ pathLength: 1, opacity: 0.6 }}
              transition={{ duration: 2, repeat: Infinity, ease: "linear", delay: 1 }}
            />
            <defs>
              <linearGradient id="gradient1" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#8A2BE2" />
                <stop offset="100%" stopColor="#00F0FF" />
              </linearGradient>
              <linearGradient id="gradient2" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#00F0FF" />
                <stop offset="100%" stopColor="#8A2BE2" />
              </linearGradient>
            </defs>
          </svg>

          {/* Center brain icon */}
          <motion.div
            animate={{ 
              scale: [1, 1.1, 1],
              rotate: [0, 5, -5, 0]
            }}
            transition={{ duration: 4, repeat: Infinity }}
            className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2"
          >
            <div className="h-16 w-16 rounded-2xl bg-gradient-to-br from-[#8A2BE2] via-white to-[#00F0FF] p-[2px]">
              <div className="h-full w-full bg-gray-50 dark:bg-[#050505] rounded-2xl flex items-center justify-center">
                <Brain className="h-8 w-8 text-gray-800 dark:text-white" />
              </div>
            </div>
          </motion.div>
        </div>

        {/* Status Container */}
        <motion.div
          layout
          className="backdrop-blur-xl bg-white/80 dark:bg-white/5 border border-gray-200 dark:border-white/10 rounded-[32px] p-12 shadow-[0_8px_32px_rgba(0,0,0,0.08)] dark:shadow-[0_8px_32px_rgba(0,0,0,0.4)]"
        >
          {/* Current Phase */}
          <motion.div
            key={currentPhase}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-12"
          >
            <h3 
              className="text-4xl font-bold text-gray-900 dark:text-white mb-4"
              style={{ fontFamily: "'Space Grotesk', sans-serif" }}
            >
              {PHASES[currentPhase].label}
            </h3>
            <div className="flex items-center justify-center gap-2">
              {PHASES[currentPhase].agent === "experience" && (
                <span className="text-[#8A2BE2] font-semibold" style={{ fontFamily: "'Inter', sans-serif" }}>
                  <Sparkles className="inline h-4 w-4 mr-1" />
                  Experience Agent
                </span>
              )}
              {PHASES[currentPhase].agent === "logistics" && (
                <span className="text-[#00F0FF] font-semibold" style={{ fontFamily: "'Inter', sans-serif" }}>
                  <Plane className="inline h-4 w-4 mr-1" />
                  Logistics Agent
                </span>
              )}
              {PHASES[currentPhase].agent === "both" && (
                <span className="text-gray-500 dark:text-white/60 font-semibold" style={{ fontFamily: "'Inter', sans-serif" }}>
                  <Brain className="inline h-4 w-4 mr-1" />
                  Dual AI Processing
                </span>
              )}
            </div>
          </motion.div>

          {/* Progress Bar */}
          <div className="relative h-3 bg-black/10 dark:bg-white/5 rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.3 }}
              className="h-full bg-gradient-to-r from-[#8A2BE2] via-white to-[#00F0FF] rounded-full shadow-[0_0_20px_rgba(138,43,226,0.5)]"
            />
          </div>

          {/* Progress Percentage */}
          <motion.p 
            className="text-center text-gray-600 dark:text-white/80 mt-6 text-xl"
            style={{ fontFamily: "'Inter', sans-serif" }}
          >
            {Math.floor(progress)}%
          </motion.p>

          {/* Long running hint */}
          {progress >= 99 && (
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-center text-[#8A2BE2] mt-4 text-sm font-medium animate-pulse"
              style={{ fontFamily: "'Inter', sans-serif" }}
            >
              Our agents are finding the best hidden gems... almost there!
            </motion.p>
          )}

          {/* Loading dots animation */}
          <div className="flex justify-center gap-2 mt-8">
            {[0, 1, 2].map((i) => (
              <motion.div
                key={i}
                animate={{
                  y: [0, -10, 0],
                  opacity: [0.3, 1, 0.3],
                }}
                transition={{
                  duration: 1,
                  repeat: Infinity,
                  delay: i * 0.2,
                }}
                className="h-2 w-2 rounded-full bg-gray-400 dark:bg-white"
              />
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  );
}

