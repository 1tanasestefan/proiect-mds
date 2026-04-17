"use client";

import ProtectedRoute from '@/components/ProtectedRoute';
import { useAuth } from '@/context/AuthContext';
import { motion, AnimatePresence } from 'framer-motion';
import { useRouter } from 'next/navigation';
import { Calendar, MapPin, Compass, ArrowRight, Heart, Wallet, Loader2, Plane, ChevronLeft, ChevronRight } from 'lucide-react';
import Image from 'next/image';
import { supabase } from '@/lib/supabase';
import { useEffect, useState, useCallback } from 'react';
import { FinalTripPlan } from '@/components/figma/itinerary-output';
import { toast } from 'sonner';
import { Eye, EyeOff, Globe, Lock } from 'lucide-react';

// ── Spotlight slideshow data ────────────────────────────────────────
const SPOTLIGHT = [
  {
    label: 'Neon Tokyo',
    location: 'Tokyo, Japan',
    vibe: 'Energetic Nightlife',
    image: 'https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=1400&q=85&auto=format&fit=crop',
    accent: '#00F0FF',
    query: 'Tokyo Japan',
  },
  {
    label: 'Tuscany Villas',
    location: 'Tuscany, Italy',
    vibe: 'Luxury Countryside',
    image: 'https://images.unsplash.com/photo-1499678329028-101435549a4e?w=1400&q=85&auto=format&fit=crop',
    accent: '#FFB347',
    query: 'Tuscany Italy',
  },
  {
    label: 'Maldives Overwater',
    location: 'Maldives',
    vibe: 'Private Island Escape',
    image: 'https://images.unsplash.com/photo-1514282401047-d79a71a590e8?w=1400&q=85&auto=format&fit=crop',
    accent: '#00D4AA',
    query: 'Maldives',
  },
  {
    label: 'Paris, City of Light',
    location: 'Paris, France',
    vibe: 'Art & Gastronomy',
    image: 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=1400&q=85&auto=format&fit=crop',
    accent: '#8A2BE2',
    query: 'Paris France',
  },
];

const SLIDE_VARIANTS = {
  enter: (dir: number) => ({ x: dir > 0 ? 60 : -60, opacity: 0 }),
  center: { x: 0, opacity: 1 },
  exit: (dir: number) => ({ x: dir > 0 ? -60 : 60, opacity: 0 }),
};

function SpotlightSlideshow({ onPlan }: { onPlan: (query: string) => void }) {
  const [index, setIndex] = useState(0);
  const [dir, setDir] = useState(1);

  const go = useCallback((delta: number) => {
    setDir(delta);
    setIndex(prev => (prev + delta + SPOTLIGHT.length) % SPOTLIGHT.length);
  }, []);

  // Auto-advance every 5 s
  useEffect(() => {
    const t = setInterval(() => go(1), 5000);
    return () => clearInterval(t);
  }, [go]);

  const slide = SPOTLIGHT[index];

  return (
    <div className="relative overflow-hidden rounded-[32px] min-h-[400px] border border-gray-200 dark:border-white/10 shadow-lg">
      {/* Slide images */}
      <AnimatePresence custom={dir} mode="popLayout">
        <motion.div
          key={index}
          custom={dir}
          variants={SLIDE_VARIANTS}
          initial="enter"
          animate="center"
          exit="exit"
          transition={{ duration: 0.5, ease: [0.32, 0.72, 0, 1] }}
          className="absolute inset-0"
        >
          <Image
            src={slide.image}
            alt={slide.label}
            fill
            sizes="(max-width: 768px) 100vw, 66vw"
            className="object-cover"
            priority
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/35 to-black/10" />
        </motion.div>
      </AnimatePresence>

      {/* Overlay content */}
      <div className="absolute inset-0 p-8 flex flex-col justify-between z-10">
        {/* Top row */}
        <div className="flex justify-between items-start">
          <div className="backdrop-blur-xl bg-white/10 border border-white/20 px-4 py-2 rounded-full inline-flex items-center gap-2 text-sm font-medium text-white shadow-lg">
            <span className="w-2 h-2 rounded-full animate-pulse" style={{ background: slide.accent }} />
            Spotlight Destination
          </div>

          {/* Arrow controls */}
          <div className="flex gap-2">
            <button
              onClick={() => go(-1)}
              className="h-10 w-10 rounded-full bg-white/10 backdrop-blur-xl border border-white/20 flex items-center justify-center hover:bg-white/20 transition-colors"
            >
              <ChevronLeft className="h-5 w-5 text-white" />
            </button>
            <button
              onClick={() => go(1)}
              className="h-10 w-10 rounded-full bg-white/10 backdrop-blur-xl border border-white/20 flex items-center justify-center hover:bg-white/20 transition-colors"
            >
              <ChevronRight className="h-5 w-5 text-white" />
            </button>
          </div>
        </div>

        {/* Bottom: label + tags + dots */}
        <div>
          <AnimatePresence mode="wait">
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.3 }}
            >
              <h2 className="text-5xl font-bold text-white mb-3" style={{ fontFamily: "'Space Grotesk', sans-serif" }}>
                {slide.label}
              </h2>
              <div className="flex flex-wrap gap-3 text-white/90 font-medium mb-5" style={{ fontFamily: "'Inter', sans-serif" }}>
                <span className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/10 backdrop-blur-md border border-white/10">
                  <MapPin className="h-4 w-4" style={{ color: slide.accent }} />
                  {slide.location}
                </span>
                <span className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/10 backdrop-blur-md border border-white/10">
                  <Heart className="h-4 w-4 text-[#8A2BE2]" />
                  {slide.vibe}
                </span>
              </div>
            </motion.div>
          </AnimatePresence>

          {/* Dot indicators */}
          <div className="flex gap-2">
            {SPOTLIGHT.map((_, i) => (
              <button
                key={i}
                onClick={() => { setDir(i > index ? 1 : -1); setIndex(i); }}
                className="rounded-full transition-all duration-300"
                style={{
                  width: i === index ? 24 : 8,
                  height: 8,
                  background: i === index ? slide.accent : 'rgba(255,255,255,0.3)',
                }}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}


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
  is_public: boolean;
}

export default function DashboardPage() {
  const { user, session } = useAuth();
  const router = useRouter();
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

  const handleTogglePublic = async (tripId: string, currentStatus: boolean) => {
    if (!session) return;
    
    // Optimistic Update
    setItineraries(prev => prev.map(t => t.id === tripId ? { ...t, is_public: !currentStatus } : t));
    
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_ITINERARY_API_URL || 'http://127.0.0.1:8000'}/api/itineraries/${tripId}`, {
        method: "PATCH",
        headers: {
          "Authorization": `Bearer ${session.access_token}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ is_public: !currentStatus })
      });
      
      if (!response.ok) throw new Error();
      toast.success(!currentStatus ? "Trip published to Discover feed!" : "Trip is now private.");
    } catch (err) {
      // Rollback
      setItineraries(prev => prev.map(t => t.id === tripId ? { ...t, is_public: currentStatus } : t));
      toast.error("Failed to update status.");
    }
  };

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
            {/* Spotlight Slideshow - Span 2 columns */}
            <motion.div variants={item} className="md:col-span-2">
              <SpotlightSlideshow onPlan={(q) => router.push(`/plan?destination=${encodeURIComponent(q)}`)} />
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
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handleTogglePublic(trip.id, trip.is_public);
                            }}
                            className={`p-2 rounded-full transition-colors ${
                              trip.is_public 
                                ? "bg-emerald-500/10 text-emerald-500 hover:bg-emerald-500/20" 
                                : "bg-gray-100 dark:bg-white/5 text-gray-400 hover:bg-gray-200 dark:hover:bg-white/10"
                            }`}
                            title={trip.is_public ? "Public on Discover" : "Private"}
                          >
                            {trip.is_public ? <Globe className="h-4 w-4" /> : <Lock className="h-4 w-4" />}
                          </button>
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

                        <button
                          onClick={() => router.push(`/trips/${trip.id}`)}
                          className="w-full py-3 rounded-xl bg-gray-100 dark:bg-white/10 text-gray-900 dark:text-white font-medium hover:bg-[#00F0FF]/10 hover:text-[#00F0FF] transition-colors border border-transparent hover:border-[#00F0FF]/30 flex items-center justify-center gap-2"
                        >
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
