"use client";

import { useCallback, useEffect, useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import { Sparkles, TrendingUp, Clock, Loader2, Compass } from "lucide-react";
import { CommunityTripCard } from "@/components/CommunityTripCard";
import { useAuth } from "@/context/AuthContext";

interface CommunityItinerary {
  id: string;
  title: string;
  destination: string;
  start_date?: string;
  end_date?: string;
  likes_count: number;
  forks_count: number;
  author_name: string;
  author_avatar?: string;
  ai_data: {
    experience?: {
      vibe_summary?: string;
      itinerary?: unknown[];
    };
  };
  is_liked_by_me?: boolean;
  created_at: string;
}

export default function DiscoverPage() {
  const { session } = useAuth();
  const [itineraries, setItineraries] = useState<CommunityItinerary[]>([]);
  const [loading, setLoading] = useState(true);
  const [sortBy, setSortBy] = useState<"likes" | "newest">("likes");

  const fetchFeed = useCallback(async () => {
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
  }, [session?.access_token, sortBy]);

  useEffect(() => {
    fetchFeed();
  }, [fetchFeed]);

  return (
    <div className="min-h-screen bg-[#FFF6E8] pt-32 pb-24 px-8 relative overflow-hidden">
      {/* Background Decor */}
      <div className="absolute top-0 right-0 h-[600px] w-[600px] rounded-full bg-[#FF6B5A]/8 blur-[150px] -z-10" />
      <div className="absolute bottom-0 left-0 h-[600px] w-[600px] rounded-full bg-[#FF9F43]/6 blur-[150px] -z-10" />

      <div className="max-w-7xl mx-auto">
        {/* Header Section */}
        <header className="mb-12 text-center md:text-left flex flex-col md:flex-row md:items-end justify-between gap-6">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
          >
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#FF6B5A]/10 border border-[#FF6B5A]/20 text-[#FF6B5A] text-xs font-bold uppercase tracking-widest mb-4">
              <Compass className="h-3 w-3" />
              Community Discover
            </div>
            <h1 className="text-5xl md:text-6xl font-bold mb-4 text-[#10223A]" style={{ fontFamily: "var(--font-playfair), Georgia, serif" }}>
              EXPLORE THE WORLD
            </h1>
            <p className="text-lg text-[#64748B] max-w-xl" style={{ fontFamily: "'Inter', sans-serif" }}>
              Unlock hand-crafted itineraries from fellow explorers or showcase your own adventures to the community.
            </p>
          </motion.div>

          {/* Sort Controls */}
          <motion.div 
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex items-center gap-2 p-1.5 bg-[#FFFBF3] border border-[rgba(255,107,90,0.18)] rounded-2xl backdrop-blur-xl shadow-lg self-center md:self-auto"
          >
            <button
              onClick={() => setSortBy("likes")}
              className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-bold transition-all ${
                sortBy === "likes" 
                  ? "bg-gradient-to-r from-[#FF6B5A] to-[#FF9F43] text-white shadow-md" 
                  : "text-[#64748B]/60 hover:text-[#10223A] hover:bg-[#FF6B5A]/8"
              }`}
            >
              <TrendingUp className="h-4 w-4" />
              Trending
            </button>
            <button
              onClick={() => setSortBy("newest")}
              className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-bold transition-all ${
                sortBy === "newest" 
                  ? "bg-gradient-to-r from-[#FF6B5A] to-[#FF9F43] text-white shadow-md" 
                  : "text-[#64748B]/60 hover:text-[#10223A] hover:bg-[#FF6B5A]/8"
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
                <Loader2 className="h-10 w-10 text-[#FF6B5A] animate-spin mb-4" />
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
                <Sparkles className="h-16 w-16 text-[#64748B]/20 mx-auto mb-6" />
                <h3 className="text-2xl font-bold text-[#10223A] mb-2">No itineraries found</h3>
                <p className="text-[#64748B]">The community is still packing. Be the first to share a trip!</p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
