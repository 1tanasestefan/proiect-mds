"use client";

import { useState } from "react";
import { motion } from "motion/react";
import { Heart, Bookmark, MapPin, Calendar, Clock, User, Share2 } from "lucide-react";
import { toast } from "sonner";
import { useAuth } from "@/context/AuthContext";
import Image from "next/image";

interface CommunityTripCardProps {
  itinerary: {
    id: string;
    title: string;
    destination: string;
    start_date?: string;
    end_date?: string;
    likes_count: number;
    forks_count: number;
    author_name: string;
    author_avatar?: string;
    ai_data: any;
    is_liked_by_me?: boolean;
    created_at: string;
  };
}

export function CommunityTripCard({ itinerary }: CommunityTripCardProps) {
  const { session, isAuthenticated } = useAuth();
  const [isLiked, setIsLiked] = useState(itinerary.is_liked_by_me);
  const [likesCount, setLikesCount] = useState(itinerary.likes_count);
  const [isForking, setIsForking] = useState(false);

  const handleLike = async (e: React.MouseEvent) => {
    e.stopPropagation();
    if (!isAuthenticated) {
      toast.error("Please log in to like trips!");
      return;
    }

    // Optimistic UI
    const prevLiked = isLiked;
    const prevCount = likesCount;
    setIsLiked(!prevLiked);
    setLikesCount(prevLiked ? prevCount - 1 : prevCount + 1);

    try {
      const res = await fetch(`http://127.0.0.1:8000/api/community/like/${itinerary.id}`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${session?.access_token}`,
        },
      });

      if (!res.ok) throw new Error();
      const data = await res.json();
      setLikesCount(data.likes_count);
    } catch (err) {
      // Rollback
      setIsLiked(prevLiked);
      setLikesCount(prevCount);
      toast.error("Failed to update like");
    }
  };

  const handleFork = async (e: React.MouseEvent) => {
    e.stopPropagation();
    if (!isAuthenticated) {
      toast.error("Please log in to save trips!");
      return;
    }

    setIsForking(true);
    const toastId = toast.loading("Cloning itinerary to your account...");

    try {
      const res = await fetch(`http://127.0.0.1:8000/api/community/fork/${itinerary.id}`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${session?.access_token}`,
        },
      });

      if (!res.ok) throw new Error();
      
      toast.success("Trip saved! You can find it in your dashboard.", { id: toastId });
    } catch (err) {
      toast.error("Failed to clone trip", { id: toastId });
    } finally {
      setIsForking(false);
    }
  };

  const durationDays = itinerary.ai_data?.experience?.itinerary?.length || 0;

  return (
    <motion.div
      whileHover={{ y: -8 }}
      className="group relative backdrop-blur-xl bg-white/80 dark:bg-white/5 border border-gray-200 dark:border-white/10 rounded-[32px] overflow-hidden shadow-[0_8px_32px_rgba(0,0,0,0.08)] dark:shadow-[0_8px_32px_rgba(0,0,0,0.4)] transition-all duration-500 hover:border-[#00F0FF]/40"
    >
      {/* Cover Image Section */}
      <div className="relative h-56 w-full overflow-hidden">
        <Image
          src={`https://images.unsplash.com/photo-1544013501-5717a0ce4b9a?q=80&w=800&auto=format&fit=crop`} // Placeholder logic
          alt={itinerary.destination}
          fill
          className="object-cover transition-transform duration-700 group-hover:scale-110"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent" />
        
        {/* Quick Stats Over Image */}
        <div className="absolute bottom-4 left-4 right-4 flex justify-between items-center text-white">
          <div className="flex items-center gap-2">
            <div className="flex -space-x-2">
              <div className="h-8 w-8 rounded-full border-2 border-white/20 bg-[#8A2BE2] flex items-center justify-center text-[10px] font-bold">
                {itinerary.author_name.charAt(0).toUpperCase()}
              </div>
            </div>
            <span className="text-xs font-medium backdrop-blur-md bg-white/10 px-2 py-1 rounded-lg border border-white/10">
              @{itinerary.author_name.toLowerCase()}
            </span>
          </div>
          <div className="flex items-center gap-3">
             <div className="flex items-center gap-1.5 backdrop-blur-md bg-black/30 px-2 py-1 rounded-lg border border-white/10 text-[10px] font-semibold uppercase tracking-widest">
                <Clock className="h-3 w-3 text-[#00F0FF]" />
                {durationDays} Days
             </div>
          </div>
        </div>
      </div>

      {/* Content Section */}
      <div className="p-6">
        <div className="flex items-start justify-between mb-3">
          <div>
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-1 group-hover:text-[#00F0FF] transition-colors" style={{ fontFamily: "'Space Grotesk', sans-serif" }}>
              {itinerary.title}
            </h3>
            <div className="flex items-center gap-1.5 text-gray-500 dark:text-white/40 text-sm">
              <MapPin className="h-3.5 w-3.5 text-[#00F0FF]" />
              {itinerary.destination}
            </div>
          </div>
        </div>

        <p className="text-sm text-gray-500 dark:text-white/60 line-clamp-2 mb-6" style={{ fontFamily: "'Inter', sans-serif" }}>
          {itinerary.ai_data?.experience?.vibe_summary || "Explore a personalized journey crafted by AI."}
        </p>

        {/* Action Bar */}
        <div className="flex items-center justify-between pt-4 border-t border-gray-100 dark:border-white/5">
          <div className="flex items-center gap-4">
            <button 
              onClick={handleLike}
              className={`flex items-center gap-1.5 transition-all ${isLiked ? "text-rose-500" : "text-gray-400 hover:text-rose-400"}`}
            >
              <Heart className={`h-5 w-5 ${isLiked ? "fill-current" : ""}`} />
              <span className="text-sm font-bold">{likesCount}</span>
            </button>
            <div className="flex items-center gap-1.5 text-gray-400">
              <Share2 className="h-5 w-5" />
              <span className="text-sm font-bold">{itinerary.forks_count}</span>
            </div>
          </div>

          <button
            onClick={handleFork}
            disabled={isForking}
            className="group/btn relative px-4 py-2 rounded-xl bg-gray-900 dark:bg-white/10 text-white dark:text-white font-bold text-xs overflow-hidden transition-all hover:bg-[#8A2BE2] hover:text-white active:scale-95"
          >
            <span className="relative z-10 flex items-center gap-2">
              <Bookmark className="h-3.5 w-3.5" />
              Save Trip
            </span>
          </button>
        </div>
      </div>
    </motion.div>
  );
}
