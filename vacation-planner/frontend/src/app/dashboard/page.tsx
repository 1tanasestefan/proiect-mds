"use client";

import ProtectedRoute from '@/components/ProtectedRoute';
import { useAuth } from '@/context/AuthContext';
import { motion } from 'framer-motion';
import { Calendar, MapPin, Settings2, Compass, ArrowRight, Heart, Wallet } from 'lucide-react';
import Image from 'next/image';

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.1 }
  }
};

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0, transition: { type: "spring" as const, stiffness: 300, damping: 24 } }
};

export default function DashboardPage() {
  const { user } = useAuth();

  return (
    <ProtectedRoute>
      <div className="min-h-screen pt-32 pb-24 px-8 relative z-10 text-gray-900 dark:text-white">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-12"
          >
            <h1 className="text-4xl md:text-5xl font-black mb-4 bg-gradient-to-r from-gray-900 dark:from-white to-gray-500 dark:to-white/60 bg-clip-text text-transparent" style={{ fontFamily: "'Archivo Black', sans-serif" }}>
              Welcome back, {user?.displayName || "Explorer"}
            </h1>
            <p className="text-lg text-gray-500 dark:text-white/60" style={{ fontFamily: "'Inter', sans-serif" }}>
              Ready for your next adventure?
            </p>
          </motion.div>

          <motion.div 
            variants={container}
            initial="hidden"
            animate="show"
            className="grid grid-cols-1 md:grid-cols-3 gap-6"
          >
            {/* Upcoming Trip - Span 2 columns */}
            <motion.div variants={item} className="md:col-span-2 relative overflow-hidden rounded-[32px] group min-h-[400px]">
              <Image
                src="https://images.unsplash.com/photo-1537996194471-e657df975ab4?q=80&w=2038&auto=format&fit=crop"
                alt="Bali Sunset"
                fill
                className="object-cover transition-transform duration-700 group-hover:scale-105"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/40 to-transparent" />
              
              <div className="absolute inset-0 p-8 flex flex-col justify-between">
                <div className="flex justify-between items-start">
                  <div className="backdrop-blur-xl bg-white/10 border border-white/20 px-4 py-2 rounded-full inline-flex items-center gap-2 text-sm font-medium">
                    <span className="w-2 h-2 rounded-full bg-[#00F0FF] animate-pulse" />
                    Upcoming in 14 days
                  </div>
                  <button className="h-12 w-12 rounded-full bg-white/10 backdrop-blur-xl border border-white/20 flex items-center justify-center hover:bg-white/20 transition-colors">
                    <ArrowRight className="h-5 w-5 text-white" />
                  </button>
                </div>

                <div>
                  <h2 className="text-4xl font-bold text-white mb-2" style={{ fontFamily: "'Space Grotesk', sans-serif" }}>
                    Bali Retreat
                  </h2>
                  <div className="flex flex-wrap gap-4 text-white/80" style={{ fontFamily: "'Inter', sans-serif" }}>
                    <span className="flex items-center gap-2"><MapPin className="h-4 w-4 text-[#00F0FF]" /> Seminyak, Indonesia</span>
                    <span className="flex items-center gap-2"><Calendar className="h-4 w-4 text-[#8A2BE2]" /> Oct 12 - Oct 20</span>
                  </div>
                </div>
              </div>
            </motion.div>

            {/* AI Preferences */}
            <motion.div variants={item} className="backdrop-blur-xl bg-white/80 dark:bg-white/5 border border-gray-200 dark:border-white/10 rounded-[32px] p-8 flex flex-col">
              <div className="flex items-center gap-3 mb-8">
                <div className="h-12 w-12 rounded-2xl bg-gradient-to-br from-[#8A2BE2] to-[#00F0FF] flex items-center justify-center shadow-lg">
                  <Settings2 className="h-6 w-6 text-white" />
                </div>
                <h3 className="text-2xl font-bold text-gray-900 dark:text-white" style={{ fontFamily: "'Space Grotesk', sans-serif" }}>AI Preferences</h3>
              </div>

              <div className="flex-1 space-y-6">
                <div className="bg-black/5 dark:bg-white/5 border border-gray-200 dark:border-white/10 rounded-2xl p-4">
                  <div className="text-gray-400 dark:text-white/50 text-sm mb-2" style={{ fontFamily: "'Inter', sans-serif" }}>Default Vibe</div>
                  <div className="flex items-center gap-2 text-gray-900 dark:text-white font-medium">
                    <Heart className="h-4 w-4 text-[#8A2BE2]" /> Relaxed & Cultural
                  </div>
                </div>
                <div className="bg-black/5 dark:bg-white/5 border border-gray-200 dark:border-white/10 rounded-2xl p-4">
                  <div className="text-gray-400 dark:text-white/50 text-sm mb-2" style={{ fontFamily: "'Inter', sans-serif" }}>Target Budget</div>
                  <div className="flex items-center gap-2 text-gray-900 dark:text-white font-medium">
                    <Wallet className="h-4 w-4 text-[#00F0FF]" /> Comfort Seeker
                  </div>
                </div>
              </div>
            </motion.div>

            {/* Saved Itineraries */}
            <motion.div variants={item} className="md:col-span-3 backdrop-blur-xl bg-white/80 dark:bg-white/5 border border-gray-200 dark:border-white/10 rounded-[32px] p-8 mt-4">
              <div className="flex items-center justify-between mb-8">
                <div className="flex items-center gap-3">
                  <Compass className="h-8 w-8 text-[#00F0FF]" />
                  <h3 className="text-2xl font-bold text-gray-900 dark:text-white" style={{ fontFamily: "'Space Grotesk', sans-serif" }}>Saved Itineraries</h3>
                </div>
                <button className="text-[#00F0FF] hover:text-white transition-colors text-sm font-medium" style={{ fontFamily: "'Inter', sans-serif" }}>
                  View All
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {[
                  { title: "Neon Tokyo Exploration", image: "https://images.unsplash.com/photo-1542051812871-7575116fc53e?q=80&w=2670&auto=format&fit=crop", cost: "High", duration: "7 days" },
                  { title: "Amalfi Coast Drive", image: "https://images.unsplash.com/photo-1533676802871-eca1ae998ce5?q=80&w=2670&auto=format&fit=crop", cost: "Premium", duration: "5 days" },
                  { title: "Swiss Alps Adventure", image: "https://images.unsplash.com/photo-1530122037265-a5f1f91d3b99?q=80&w=2670&auto=format&fit=crop", cost: "Medium", duration: "4 days" }
                ].map((trip, idx) => (
                  <motion.div 
                    key={idx}
                    whileHover={{ y: -5 }}
                    className="group cursor-pointer bg-black/5 dark:bg-white/5 border border-gray-200 dark:border-white/10 rounded-2xl overflow-hidden hover:border-gray-400 dark:hover:border-white/30 transition-all duration-300"
                  >
                    <div className="relative h-48 w-full">
                      <Image src={trip.image} alt={trip.title} fill className="object-cover group-hover:scale-105 transition-transform duration-500" />
                      <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent" />
                      <div className="absolute bottom-4 left-4 right-4">
                        <h4 className="text-lg font-bold text-white mb-1" style={{ fontFamily: "'Space Grotesk', sans-serif" }}>{trip.title}</h4>
                        <div className="flex justify-between items-center text-xs text-white/70" style={{ fontFamily: "'Inter', sans-serif" }}>
                          <span>{trip.duration}</span>
                          <span className="bg-white/20 px-2 py-1 rounded backdrop-blur-md">{trip.cost}</span>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          </motion.div>
        </div>
      </div>
    </ProtectedRoute>
  );
}
