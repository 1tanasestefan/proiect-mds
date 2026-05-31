"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "motion/react";
import { Heart, Bookmark, MapPin, Clock, Share2 } from "lucide-react";
import { toast } from "sonner";
import { useAuth } from "@/context/AuthContext";
import Image from "next/image";
import { apiUrl } from "@/lib/backend";

interface CommunityActivity {
  image_url?: string;
  title?: string;
  type?: string;
}

interface CommunityDay {
  activities?: CommunityActivity[];
}

interface CommunityAiData {
  experience?: {
    vibe_summary?: string;
    itinerary?: CommunityDay[];
  };
}

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
    ai_data: CommunityAiData;
    is_liked_by_me?: boolean;
    created_at: string;
  };
}

export function CommunityTripCard({ itinerary }: CommunityTripCardProps) {
  const router = useRouter();
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
      const res = await fetch(apiUrl(`/api/community/like/${itinerary.id}`), {
        method: "POST",
        headers: {
          Authorization: `Bearer ${session?.access_token}`,
        },
      });

      if (!res.ok) throw new Error();
      const data = await res.json();
      setLikesCount(data.likes_count);
    } catch {
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
      const res = await fetch(apiUrl(`/api/community/fork/${itinerary.id}`), {
        method: "POST",
        headers: {
          Authorization: `Bearer ${session?.access_token}`,
        },
      });

      if (!res.ok) throw new Error();
      
      toast.success("Trip saved! You can find it in your dashboard.", { id: toastId });
    } catch {
      toast.error("Failed to clone trip", { id: toastId });
    } finally {
      setIsForking(false);
    }
  };

  const durationDays = itinerary.ai_data?.experience?.itinerary?.length || 0;

  // Skip transport activities by type or by title keywords
  const SKIP_TYPES = new Set(["flight", "hotel", "departure", "arrival", "transfer"]);
  const SKIP_TITLE_KEYWORDS = /\b(flight|transfer|airport|check-in|check in|departure|arrival)\b/i;
  const allActivities = itinerary.ai_data?.experience?.itinerary?.flatMap((day) => day.activities ?? []) ?? [];
  const coverImage =
    allActivities.find((act) => act.image_url && (!act.type || !SKIP_TYPES.has(act.type)) && !SKIP_TITLE_KEYWORDS.test(act.title ?? ""))
      ?.image_url ??
    allActivities.find((act) => act.image_url)?.image_url ??
    `https://images.unsplash.com/photo-1488085061387-422e29b40080?q=80&w=800&auto=format&fit=crop`;

  return (
    <motion.div
      whileHover={{ y: -4 }}
      onClick={() => router.push(`/trips/${itinerary.id}`)}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          router.push(`/trips/${itinerary.id}`);
        }
      }}
      role="button"
      tabIndex={0}
      className="group relative backdrop-blur-xl bg-[#FFFBF3] border border-[rgba(255,107,90,0.14)] rounded-[32px] overflow-hidden shadow-[0_8px_32px_rgba(255,107,90,0.10)] transition-all duration-500 hover:border-[#FF6B5A]/40 cursor-pointer focus:outline-none focus:ring-2 focus:ring-[#FF6B5A]/40"
    >
      {/* Cover Image Section */}
      <div className="relative h-56 w-full overflow-hidden">
        <Image
          src={coverImage}
          alt={itinerary.destination}
          fill
          className="object-cover transition-transform duration-700 group-hover:scale-110"
          unoptimized={coverImage.includes('pexels.com')}
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent" />
        
        {/* Quick Stats Over Image */}
        <div className="absolute bottom-4 left-4 right-4 flex justify-between items-center text-white">
          <div className="flex items-center gap-2">
            <div className="flex -space-x-2">
              <div className="h-8 w-8 rounded-full border-2 border-white/20 bg-gradient-to-br from-[#FF6B5A] to-[#FF9F43] flex items-center justify-center text-[10px] font-bold text-white">
                {itinerary.author_name.charAt(0).toUpperCase()}
              </div>
            </div>
            <span className="text-xs font-medium backdrop-blur-md bg-white/10 px-2 py-1 rounded-lg border border-white/10">
              @{itinerary.author_name.toLowerCase()}
            </span>
          </div>
          <div className="flex items-center gap-3">
             <div className="flex items-center gap-1.5 backdrop-blur-md bg-black/30 px-2 py-1 rounded-lg border border-white/10 text-[10px] font-semibold uppercase tracking-widest">
                <Clock className="h-3 w-3 text-[#FF6B5A]" />
                {durationDays} Days
             </div>
          </div>
        </div>
      </div>

      {/* Content Section */}
      <div className="p-6">
        <div className="flex items-start justify-between mb-3">
          <div>
            <h3 className="text-xl font-bold text-[#10223A] mb-1 group-hover:text-[#FF6B5A] transition-colors" style={{ fontFamily: "'Space Grotesk', sans-serif" }}>
              {itinerary.title}
            </h3>
            <div className="flex items-center gap-1.5 text-[#64748B]/60 text-sm">
              <MapPin className="h-3.5 w-3.5 text-[#FF6B5A]" />
              {itinerary.destination}
            </div>
          </div>
        </div>

        <p className="text-sm text-[#64748B] line-clamp-2 mb-6" style={{ fontFamily: "'Inter', sans-serif" }}>
          {itinerary.ai_data?.experience?.vibe_summary || "Explore a personalized journey crafted by AI."}
        </p>

        {/* Action Bar */}
          <div className="flex items-center justify-between pt-4 border-t border-[rgba(255,107,90,0.10)]">
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
            className="group/btn relative px-4 py-2 rounded-xl bg-gradient-to-r from-[#FF6B5A] to-[#FF9F43] text-white font-bold text-xs overflow-hidden transition-all hover:shadow-[0_4px_14px_rgba(255,107,90,0.4)] active:scale-95"
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
