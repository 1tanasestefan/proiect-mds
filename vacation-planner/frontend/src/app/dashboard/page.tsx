"use client";

import ProtectedRoute from '@/components/ProtectedRoute';
import { useAuth } from '@/context/AuthContext';
import { motion } from 'framer-motion';
import { Calendar, MapPin, Settings2, Compass, ArrowRight, Heart, Wallet, Loader2, Plane } from 'lucide-react';
import Image from 'next/image';
import { supabase } from '@/lib/supabase';
import { useEffect, useState } from 'react';
import { FinalTripPlan } from '@/components/figma/itinerary-output';

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

interface SavedItinerary {
  id: string;
  title: string;
  destination: string;
  start_date: string | null;
  end_date: string | null;
  created_at: string;
  ai_data: FinalTripPlan;
}

export default function DashboardPage() {
  const { user, session } = useAuth();
  const [itineraries, setItineraries] = useState<SavedItinerary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchItineraries = async () => {
      if (!session) return;
      try {
        const response = await fetch("http://127.0.0.1:8000/api/itineraries/me", {
          headers: {
            "Authorization": `Bearer ${session.access_token}`
          }
        });
        if (!response.ok) throw new Error("Failed to fetch itineraries");
        const data = await response.json();
        setItineraries(data.itineraries || []);
      } catch (err: any) {
        console.error(err);
        setError("Could not load your trips.");
      } finally {
        setLoading(false);
      }
    };

    fetchItineraries();
  }, [session]);

  const displayName = user?.user_metadata?.display_name || user?.email?.split('@')[0] || "Explorer";

  return (
    <ProtectedRoute>
      <div className="min-h-screen pt-32 pb-24 px-8 relative z-10 text-gray-900 dark:text-white">
        <div className="max-w-[1400px] mx-auto">
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-12"
          >
            <h1 className="text-4xl md:text-5xl font-black mb-4 bg-gradient-to-r from-gray-900 dark:from-white to-gray-500 dark:to-white/60 bg-clip-text text-transparent" style={{ fontFamily: "'Archivo Black', sans-serif" }}>
              Welcome back, {displayName}
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
            <motion.div variants={item} className="md:col-span-2 relative overflow-hidden rounded-[32px] group min-h-[400px] border border-gray-200 dark:border-white/10 shadow-lg">
              <Image
                src="https://images.unsplash.com/photo-1542051812871-7575116fc53e?q=80&w=2670&auto=format&fit=crop"
                alt="Tokyo"
                fill
                className="object-cover transition-transform duration-700 group-hover:scale-105"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/40 to-black/10" />
              
              <div className="absolute inset-0 p-8 flex flex-col justify-between">
                <div className="flex justify-between items-start">
                  <div className="backdrop-blur-xl bg-white/10 border border-white/20 px-4 py-2 rounded-full inline-flex items-center gap-2 text-sm font-medium text-white shadow-lg">
                    <span className="w-2 h-2 rounded-full bg-[#00F0FF] animate-pulse" />
                    Spotlight Destination
                  </div>
                  <button className="h-12 w-12 rounded-full bg-white/10 backdrop-blur-xl border border-white/20 flex items-center justify-center hover:bg-white/20 transition-colors shadow-lg">
                    <ArrowRight className="h-5 w-5 text-white" />
                  </button>
                </div>

                <div>
                  <h2 className="text-5xl font-bold text-white mb-3" style={{ fontFamily: "'Space Grotesk', sans-serif" }}>
                    Neon Tokyo
                  </h2>
                  <div className="flex flex-wrap gap-4 text-white/90 font-medium" style={{ fontFamily: "'Inter', sans-serif" }}>
                    <span className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/10 backdrop-blur-md border border-white/10"><MapPin className="h-4 w-4 text-[#00F0FF]" /> Tokyo, Japan</span>
                    <span className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/10 backdrop-blur-md border border-white/10"><Heart className="h-4 w-4 text-[#8A2BE2]" /> Energetic Nightlife</span>
                  </div>
                </div>
              </div>
            </motion.div>

            {/* Empty space filler for col 3 */}
            <motion.div variants={item} className="backdrop-blur-xl bg-gradient-to-br from-[#00F0FF]/10 to-[#8A2BE2]/10 border border-gray-200 dark:border-white/10 rounded-[32px] p-8 flex flex-col items-center justify-center text-center shadow-lg">
              <div className="h-20 w-20 rounded-full bg-white dark:bg-black/50 border border-gray-200 dark:border-white/10 flex items-center justify-center mb-6 shadow-xl">
                 <Plane className="h-8 w-8 text-[#8A2BE2]" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2" style={{ fontFamily: "'Space Grotesk', sans-serif" }}>Plan a New Trip</h3>
              <p className="text-gray-500 dark:text-white/60 mb-6" style={{ fontFamily: "'Inter', sans-serif" }}>Discover amazing destinations curated by our AI agents.</p>
              <a href="/plan" className="w-full py-4 rounded-xl bg-gray-900 dark:bg-white text-white dark:text-gray-900 font-bold hover:opacity-90 transition-opacity">
                Start Planning
              </a>
            </motion.div>

            {/* Saved Itineraries */}
            <motion.div variants={item} className="md:col-span-3 backdrop-blur-xl bg-white/80 dark:bg-[#1a1a2e]/60 border border-gray-200 dark:border-white/10 rounded-[32px] p-10 mt-4 shadow-xl">
              <div className="flex items-center justify-between mb-8 pb-6 border-b border-gray-200 dark:border-white/10">
                <div className="flex items-center gap-4">
                  <div className="p-3 bg-gradient-to-br from-[#00F0FF]/20 to-[#8A2BE2]/20 rounded-xl border border-[#00F0FF]/20">
                    <Compass className="h-8 w-8 text-[#00F0FF]" />
                  </div>
                  <div>
                    <h3 className="text-3xl font-bold text-gray-900 dark:text-white" style={{ fontFamily: "'Space Grotesk', sans-serif" }}>My Saved Trips</h3>
                    <p className="text-gray-500 dark:text-white/50 text-sm mt-1">Your curated AI itineraries</p>
                  </div>
                </div>
              </div>

              {loading ? (
                <div className="flex flex-col items-center justify-center py-20">
                  <Loader2 className="h-10 w-10 text-[#8A2BE2] animate-spin mb-4" />
                  <p className="text-gray-500 dark:text-white/60">Loading your itineraries...</p>
                </div>
              ) : error ? (
                <div className="text-center py-10 text-red-500 bg-red-500/10 rounded-2xl border border-red-500/20">{error}</div>
              ) : itineraries.length === 0 ? (
                <div className="text-center py-20 px-4">
                  <div className="inline-flex h-24 w-24 rounded-full bg-gray-100 dark:bg-white/5 items-center justify-center mb-6">
                    <MapPin className="h-10 w-10 text-gray-400 dark:text-white/20" />
                  </div>
                  <h4 className="text-2xl font-bold text-gray-900 dark:text-white mb-2" style={{ fontFamily: "'Space Grotesk', sans-serif" }}>No Trips Yet</h4>
                  <p className="text-gray-500 dark:text-white/50 max-w-md mx-auto">You haven't saved any itineraries yet. Head over to the planning tool to create your first adventure!</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {itineraries.map((trip) => (
                    <motion.div 
                      key={trip.id}
                      whileHover={{ y: -5 }}
                      className="group flex flex-col bg-white dark:bg-black/20 border border-gray-200 dark:border-white/10 rounded-2xl overflow-hidden hover:border-[#00F0FF]/50 transition-all duration-300 shadow-sm hover:shadow-[0_10px_30px_rgba(0,240,255,0.1)]"
                    >
                      <div className="p-6 flex-1 flex flex-col">
                        <div className="flex justify-between items-start mb-4">
                          <h4 className="text-xl font-bold text-gray-900 dark:text-white line-clamp-1" style={{ fontFamily: "'Space Grotesk', sans-serif" }}>
                            {trip.title}
                          </h4>
                        </div>
                        
                        <div className="space-y-3 mb-6 flex-1">
                          <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-white/70">
                            <MapPin className="h-4 w-4 text-[#00F0FF]" />
                            {trip.destination}
                          </div>
                          {(trip.start_date || trip.end_date) && (
                            <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-white/70">
                              <Calendar className="h-4 w-4 text-[#8A2BE2]" />
                              {trip.start_date} {trip.end_date ? `— ${trip.end_date}` : ''}
                            </div>
                          )}
                          <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-white/70">
                            <Wallet className="h-4 w-4 text-emerald-500" />
                            ${trip.ai_data?.logistics?.total_estimated_budget_usd?.toLocaleString() || 'TBD'} est.
                          </div>
                        </div>

                        <button className="w-full py-3 rounded-xl bg-gray-100 dark:bg-white/10 text-gray-900 dark:text-white font-medium hover:bg-[#00F0FF]/10 hover:text-[#00F0FF] transition-colors border border-transparent hover:border-[#00F0FF]/30 flex items-center justify-center gap-2">
                          View details
                          <ArrowRight className="h-4 w-4" />
                        </button>
                      </div>
                    </motion.div>
                  ))}
                </div>
              )}
            </motion.div>
          </motion.div>
        </div>
      </div>
    </ProtectedRoute>
  );
}
