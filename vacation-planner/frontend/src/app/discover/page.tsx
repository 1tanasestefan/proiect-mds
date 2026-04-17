"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Sparkles, TrendingUp, Clock, Filter, Loader2, Compass } from "lucide-react";
import { CommunityTripCard } from "@/components/CommunityTripCard";
import { useAuth } from "@/context/AuthContext";

export default function DiscoverPage() {
  const { session } = useAuth();
  const [itineraries, setItineraries] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [sortBy, setSortBy] = useState<"likes" | "newest">("likes");

  const fetchFeed = async () => {
    setLoading(true);
    try {
      const url = new URL("http://127.0.0.1:8000/api/community/feed");
      url.searchParams.append("sort_by", sortBy);
      
      const headers: Record<string, string> = {};
      if (session?.access_token) {
        headers["Authorization"] = `Bearer ${session.access_token}`;
      }

      const response = await fetch(url.toString(), { headers });
      if (!response.ok) throw new Error("Failed to fetch feed");
      const data = await response.json();
      setItineraries(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFeed();
  }, [sortBy, session]);

  return (
    <div className="min-h-screen bg-[#F8F9FA] dark:bg-[#050505] pt-32 pb-24 px-8 relative overflow-hidden">
      {/* Background Decor */}
      <div className="absolute top-0 right-0 h-[600px] w-[600px] rounded-full bg-[#00F0FF]/5 dark:bg-[#00F0FF]/10 blur-[150px] -z-10" />
      <div className="absolute bottom-0 left-0 h-[600px] w-[600px] rounded-full bg-[#8A2BE2]/5 dark:bg-[#8A2BE2]/10 blur-[150px] -z-10" />

      <div className="max-w-7xl mx-auto">
        {/* Header Section */}
        <header className="mb-12 text-center md:text-left flex flex-col md:flex-row md:items-end justify-between gap-6">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
          >
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#00F0FF]/10 border border-[#00F0FF]/20 text-[#00F0FF] text-xs font-bold uppercase tracking-widest mb-4">
              <Compass className="h-3 w-3" />
              Community Discover
            </div>
            <h1 className="text-5xl md:text-6xl font-black mb-4 bg-gradient-to-r from-gray-900 dark:from-white to-gray-500 dark:to-white/60 bg-clip-text text-transparent" style={{ fontFamily: "'Archivo Black', sans-serif" }}>
              EXPLORE THE WORLD
            </h1>
            <p className="text-lg text-gray-500 dark:text-white/60 max-w-xl" style={{ fontFamily: "'Inter', sans-serif" }}>
              Unlock hand-crafted itineraries from fellow explorers or showcase your own adventures to the community.
            </p>
          </motion.div>

          {/* Sort Controls */}
          <motion.div 
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex items-center gap-2 p-1.5 bg-white dark:bg-white/5 border border-gray-200 dark:border-white/10 rounded-2xl backdrop-blur-xl shadow-lg self-center md:self-auto"
          >
            <button
              onClick={() => setSortBy("likes")}
              className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-bold transition-all ${
                sortBy === "likes" 
                  ? "bg-gray-900 dark:bg-white text-white dark:text-gray-900 shadow-md" 
                  : "text-gray-500 dark:text-white/40 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-white/5"
              }`}
            >
              <TrendingUp className="h-4 w-4" />
              Trending
            </button>
            <button
              onClick={() => setSortBy("newest")}
              className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-bold transition-all ${
                sortBy === "newest" 
                  ? "bg-gray-900 dark:bg-white text-white dark:text-gray-900 shadow-md" 
                  : "text-gray-500 dark:text-white/40 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-white/5"
              }`}
            >
              <Clock className="h-4 w-4" />
              Newest
            </button>
          </motion.div>
        </header>

        {/* Content Grid */}
        <div className="relative min-h-[400px]">
          <AnimatePresence mode="wait">
            {loading ? (
              <motion.div
                key="loading"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="absolute inset-0 flex flex-col items-center justify-center pt-20"
              >
                <Loader2 className="h-10 w-10 text-[#00F0FF] animate-spin mb-4" />
                <p className="text-gray-400 font-medium animate-pulse">Scanning the globe...</p>
              </motion.div>
            ) : itineraries.length > 0 ? (
              <motion.div
                key="grid"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8"
              >
                {itineraries.map((trip) => (
                  <CommunityTripCard key={trip.id} itinerary={trip} />
                ))}
              </motion.div>
            ) : (
              <motion.div
                key="empty"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="text-center py-32"
              >
                <Sparkles className="h-16 w-16 text-gray-300 dark:text-white/10 mx-auto mb-6" />
                <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">No itineraries found</h3>
                <p className="text-gray-500 dark:text-white/40">The community is still packing. Be the first to share a trip!</p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
