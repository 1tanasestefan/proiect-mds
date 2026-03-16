import { motion } from "motion/react";
import { Sparkles } from "lucide-react";
import Image from "next/image";
import Link from "next/link";

export function HeroSection({ onStartPlanning }: { onStartPlanning: () => void }) {
  return (
    <section className="relative h-screen w-full overflow-hidden">
      {/* Background Image with Overlay */}
      <div className="absolute inset-0">
        <Image
          src="https://images.unsplash.com/photo-1679766826593-738e9b6338c6?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxleG90aWMlMjB0cm9waWNhbCUyMGJlYWNoJTIwcGFyYWRpc2UlMjBjaW5lbWF0aWN8ZW58MXx8fHwxNzczNjcyODQ5fDA&ixlib=rb-4.1.0&q=80&w=1080"
          alt="Exotic destination"
          fill
          priority
          className="object-cover"
        />
        {/* Dark gradient overlay */}
        <div className="absolute inset-0 bg-gradient-to-b from-black/60 via-black/40 to-black/80" />
      </div>



      {/* Hero Content */}
      <div className="relative z-10 h-full flex items-center justify-center">
        <div className="max-w-6xl mx-auto px-8 text-center">
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 1, delay: 0.3 }}
          >
            {/* Oversized Masked Typography */}
            <h1
              className="text-[clamp(4rem,12vw,10rem)] leading-[0.9] mb-6 font-black bg-clip-text text-transparent bg-gradient-to-br from-white via-white to-white/60"
              style={{ 
                fontFamily: "'Archivo Black', sans-serif",
                WebkitTextStroke: "1px rgba(255,255,255,0.1)"
              }}
            >
              YOUR NEXT
              <br />
              ADVENTURE
              <br />
              <span className="bg-gradient-to-r from-[#00F0FF] via-[#8A2BE2] to-[#00F0FF] bg-clip-text text-transparent">
                AWAITS
              </span>
            </h1>

            <motion.p
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.8, delay: 0.6 }}
              className="text-xl md:text-2xl text-white/70 mb-12 max-w-3xl mx-auto"
              style={{ fontFamily: "'Inter', sans-serif" }}
            >
              Powered by dual AI agents that craft the perfect balance between{" "}
              <span className="text-[#8A2BE2]">unforgettable experiences</span> and{" "}
              <span className="text-[#00F0FF]">seamless logistics</span>
            </motion.p>

            {/* Magnetic CTA Button */}
            <motion.button
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.8, delay: 0.9 }}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.98 }}
              onClick={onStartPlanning}
              className="group relative px-12 py-6 text-xl rounded-[20px] overflow-hidden bg-gradient-to-r from-[#00F0FF] to-[#8A2BE2] shadow-[0_0_40px_rgba(0,240,255,0.4),0_0_60px_rgba(138,43,226,0.3)]"
              style={{ fontFamily: "'Space Grotesk', sans-serif" }}
            >
              <div className="absolute inset-0 bg-gradient-to-r from-[#8A2BE2] to-[#00F0FF] opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
              <span className="relative z-10 text-white font-bold flex items-center gap-3">
                Start Planning
                <Sparkles className="h-5 w-5" />
              </span>
            </motion.button>
          </motion.div>
        </div>
      </div>

      {/* Scroll Indicator */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 1, delay: 1.5 }}
        className="absolute bottom-12 left-1/2 -translate-x-1/2 z-20"
      >
        <motion.div
          animate={{ y: [0, 12, 0] }}
          transition={{ duration: 2, repeat: Infinity }}
          className="flex flex-col items-center gap-2"
        >
          <span className="text-white/50 text-sm uppercase tracking-widest" style={{ fontFamily: "'Inter', sans-serif" }}>
            Scroll to explore
          </span>
          <div className="w-[1px] h-16 bg-gradient-to-b from-white/50 to-transparent" />
        </motion.div>
      </motion.div>
    </section>
  );
}
