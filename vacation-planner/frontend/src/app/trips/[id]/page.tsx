"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { motion } from "motion/react";
import { useAuth } from "@/context/AuthContext";
import { TransportDashboard } from "@/components/TransportDashboard";
import {
  ArrowLeft, MapPin, Calendar, Loader2,
  Plane, Hotel, Star, Clock, DollarSign, Users,
  Edit2, Save, RefreshCcw, ThumbsDown, Globe, Lock
} from "lucide-react";
import { toast } from "sonner";
import { useMultiplayer } from "@/hooks/useMultiplayer";

const API_BASE =
  process.env.NEXT_PUBLIC_ITINERARY_API_URL?.replace("/api/generate-itinerary", "") ||
  "http://127.0.0.1:8000";

// ── Types ──────────────────────────────────────────────────────────
interface Activity {
  title: string;
  description?: string;
  time?: string;
  cost?: string;
  location?: string;
  image_url?: string;
  type?: string;
}

interface ItineraryDay {
  day_number: number;
  activities: Activity[];
}

interface ExperienceData {
  trip_title: string;
  vibe_summary: string;
  itinerary: ItineraryDay[];
  destination?: string;
}

interface FlightOption {
  airline_type: string;
  estimated_price_usd: number;
  description: string;
  booking_link: string;
}

interface AccommodationOption {
  type: string;
  neighborhood: string;
  estimated_price_per_night_usd: number;
  booking_link: string;
}

interface TripLogistics {
  flights: FlightOption[];
  accommodations: AccommodationOption[];
  total_estimated_budget_usd: number;
  transit_options?: Record<string, any>;
}

interface FinalTripPlan {
  experience: ExperienceData;
  logistics?: TripLogistics;
}

interface SavedTrip {
  id: string;
  user_id?: string;
  title: string;
  destination: string;
  start_date: string | null;
  end_date: string | null;
  created_at: string;
  ai_data: any; 
  is_public: boolean;
}

interface VoteUser {
  id: string;
  name: string;
  avatarId?: number;
}

// ── Activity Card ─────────────────────────────────────────────────
function ActivityCard({ 
  act, i, isHighlighted, onClick, 
  voteKey, votes, isRegenerating, onVote, totalOnline 
}: { 
  act: Activity; i: number; isHighlighted?: boolean; onClick?: () => void;
  voteKey: string; votes: VoteUser[]; isRegenerating: boolean; onVote: () => void; totalOnline: number;
}) {
  const threshold = Math.floor(totalOnline / 2);
  const isDraw = votes.length > 0 && votes.length <= threshold;

  return (
    <motion.div
      initial={{ opacity: 0, x: -16 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: i * 0.06, duration: 0.4 }}
      onClick={isRegenerating ? undefined : onClick}
      className={`flex gap-4 p-4 rounded-2xl bg-white/[0.03] transition-all relative overflow-hidden ${
        isRegenerating ? "border-[#22C55E]/40 shadow-[0_0_20px_rgba(34,197,94,0.2)] bg-black/40 cursor-wait" :
        isHighlighted 
          ? "border-[#00F0FF] shadow-[0_0_15px_rgba(0,240,255,0.4)] bg-[#00F0FF]/10 scale-[1.02] cursor-pointer" 
          : "border-white/8 hover:border-white/20 cursor-pointer"
      }`}
    >
      {isRegenerating && (
        <div className="absolute inset-0 z-20 backdrop-blur-[2px] flex items-center justify-center bg-black/40">
           <div className="flex flex-col items-center gap-2">
             <Loader2 className="h-6 w-6 text-[#22C55E] animate-spin" />
             <span className="text-xs text-[#22C55E] font-medium tracking-widest uppercase">Regenerating...</span>
           </div>
        </div>
      )}

      {isHighlighted && !isRegenerating && (
        <div className="absolute top-2 right-3 flex items-center gap-1.5 opacity-80 z-10">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#00F0FF] opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-[#00F0FF]"></span>
          </span>
          <span className="text-[10px] text-[#00F0FF] font-medium tracking-wide">Someone is viewing</span>
        </div>
      )}

      {act.image_url && (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={act.image_url}
          alt={act.title}
          className="w-20 h-20 object-cover rounded-xl shrink-0"
          onError={(e) => { (e.target as HTMLImageElement).style.display = "none"; }}
        />
      )}
      <div className="flex flex-col gap-1 min-w-0 flex-1">
        <div className="flex justify-between items-start gap-2">
          <p className="text-white/90 font-semibold text-sm leading-snug line-clamp-2"
             style={{ fontFamily: "'Space Grotesk', sans-serif" }}>
            {act.title}
          </p>
          <button 
             onClick={(e) => { e.stopPropagation(); onVote(); }}
             className="text-white/20 hover:text-white/60 transition-colors shrink-0 z-10"
             title="Vote to change this activity"
          >
             <RefreshCcw className="h-4 w-4" />
          </button>
        </div>
        {act.description && (
          <p className="text-white/45 text-xs leading-relaxed line-clamp-3">
            {act.description}
          </p>
        )}
        <div className="flex flex-wrap items-center gap-3 mt-1">
          {act.time && (
            <span className="flex items-center gap-1 text-[10px] text-[#00F0FF]/60">
              <Clock className="h-3 w-3" />{act.time}
            </span>
          )}
          {act.cost && (
            <span className="flex items-center gap-1 text-[10px] text-[#8A2BE2]/70">
              <DollarSign className="h-3 w-3" />{act.cost}
            </span>
          )}
          {act.location && (
            <span className="flex items-center gap-1 text-[10px] text-white/35">
              <MapPin className="h-3 w-3" />{act.location}
            </span>
          )}
        </div>
        
        {/* Voting UI */}
        {votes.length > 0 && !isRegenerating && (
           <div className="flex items-center gap-3 mt-2 pt-2 border-t border-white/5">
              <div className="flex -space-x-1">
                 {votes.map((v, idx) => (
                    <div key={v.id} className="h-5 w-5 rounded-full flex items-center justify-center text-[8px] font-bold text-white border border-black z-10"
                         style={{ background: `hsl(${(v.avatarId || idx) * 36}, 80%, 60%)` }} title={v.name}>
                       {v.name.charAt(0).toUpperCase()}
                    </div>
                 ))}
              </div>
              <span className="text-[10px] text-white/50">
                 {isDraw 
                    ? <span className="text-orange-400/80">Activity will not be changed ({votes.length}/{totalOnline} votes)</span> 
                    : <span className="text-yellow-400/80">{votes.length}/{totalOnline} want to change</span>}
              </span>
           </div>
        )}
      </div>
    </motion.div>
  );
}

// ── Main Page ─────────────────────────────────────────────────────
export default function TripDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const { session, isAuthenticated, isLoading: authLoading } = useAuth();

  const [trip, setTrip] = useState<SavedTrip | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [userIsConfirmedHost, setUserIsConfirmedHost] = useState(false);

  // Edit Mode States
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState("");
  const [editDestination, setEditDestination] = useState("");
  const [editVibe, setEditVibe] = useState("");
  const [isSaving, setIsSaving] = useState(false);

  // Multiplayer Hook
  const { onlineUsers, highlightedActivityId, broadcastActivityHighlight, broadcastRefreshSignal } = useMultiplayer(
    id,
    session?.user ? { id: session.user.id, email: session.user.email || "user" } : null,
    (newData) => {
      if (newData._SIGNAL_REFETCH) {
        loadItinerary();
        return;
      }
      // Postgres sync: gracefully merge incoming AI updates
      setTrip((prev) => {
        if (!prev) return prev;
        return { ...prev, ...newData };
      });
    }
  );

  const loadItinerary = async () => {
    if (!session || !id) return;
    try {
      const res = await fetch(`${API_BASE}/api/itineraries/${id}`, {
        headers: { Authorization: `Bearer ${session.access_token}` },
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setTrip(data);

      // Robust Host Check
      if (data.user_id && data.user_id === session.user.id) {
        setUserIsConfirmedHost(true);
      }
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to load trip.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadItinerary();
  }, [session, id]);

  // Intelligent Polling for Regeneration
  useEffect(() => {
    const isAnyRegenerating = trip?.ai_data?.regenerating_keys && 
                             Object.values(trip.ai_data.regenerating_keys).some(v => v === true);
    
    if (!isAnyRegenerating) return;

    const interval = setInterval(() => {
      loadItinerary();
    }, 2000); // Poll every 2 seconds while something is cooking

    return () => clearInterval(interval);
  }, [trip?.ai_data?.regenerating_keys]);

  if (authLoading || loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-[#0A0A0A]">
        <Loader2 className="h-8 w-8 text-[#00F0FF] animate-spin" />
      </div>
    );
  }

  if (error || !trip) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-[#0A0A0A] gap-4">
        <p className="text-red-400">{error || "Trip not found."}</p>
        <button onClick={() => router.push("/dashboard")}
                className="text-[#00F0FF]/70 hover:text-[#00F0FF] text-sm transition-colors">
          ← Back to My Trips
        </button>
      </div>
    );
  }

  const { experience, logistics } = trip.ai_data;
  const isHost = trip?.user_id ? session?.user?.id === trip?.user_id : userIsConfirmedHost;

  const handleEditToggle = () => {
    if (!isEditing && trip) {
      setEditTitle(trip.ai_data.experience?.trip_title || trip.title);
      setEditDestination(trip.destination);
      setEditVibe(trip.ai_data.experience?.vibe_summary || "");
    }
    setIsEditing(!isEditing);
  };

  const handleSave = async () => {
    if (!session || !trip) return;
    setIsSaving(true);
    try {
      const updatedAiData = {
        ...trip.ai_data,
        experience: {
          ...trip.ai_data.experience,
          trip_title: editTitle,
          vibe_summary: editVibe,
        }
      };

      const res = await fetch(`${API_BASE}/api/itineraries/${id}`, {
        method: 'PATCH',
        headers: { 
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          title: editTitle,
          destination: editDestination,
          ai_data: updatedAiData
        })
      });

      if (!res.ok) throw new Error("Failed to save updates.");
      setIsEditing(false);
    } catch (err: unknown) {
      alert("Error saving: " + (err instanceof Error ? err.message : "Unknown error"));
    } finally {
      setIsSaving(false);
    }
  };

  const handleVoteRegenerate = async (dayIndex: number, actIndex: number) => {
    if (!session?.user || isSaving) return;
    const voter = {
      id: session.user.id,
      name: session.user.email?.split('@')[0] || "User",
      avatarId: session.user.email?.length ? session.user.email.length % 10 : 0
    };
    const voteKey = `day_${dayIndex}_act_${actIndex}`;

    // 1. OPTIMISTIC UI: Immediately lock in the vote visually!
    let thresholdExceeded = false;
    setTrip((prev) => {
      if (!prev) return prev;
      const newTrip = JSON.parse(JSON.stringify(prev)); // Deep clone to break reference safely
      if (!newTrip.ai_data) newTrip.ai_data = {};
      if (!newTrip.ai_data.votes) newTrip.ai_data.votes = {};
      
      const actVotes = newTrip.ai_data.votes[voteKey] || [];
      if (!actVotes.some((v: any) => v.id === voter.id)) {
          actVotes.push(voter);
      }
      newTrip.ai_data.votes[voteKey] = actVotes;
      
      // Calculate theoretically if this click triggers threshold
      const totalOnline = Math.max(1, onlineUsers.length);
      const threshold = Math.floor(totalOnline / 2);
      if (actVotes.length > threshold) {
          thresholdExceeded = true;
          if (!newTrip.ai_data.regenerating_keys) newTrip.ai_data.regenerating_keys = {};
          newTrip.ai_data.regenerating_keys[voteKey] = true;
      }
      return newTrip;
    });

    try {
      // 2. Transmit gracefully in the background
      const resp = await fetch(`${API_BASE}/api/itineraries/${id}/vote-regenerate`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          day_index: dayIndex,
          activity_index: actIndex,
          total_online: Math.max(1, onlineUsers.length),
          voter
        })
      });
      
      const data = await resp.json();
      
      // BROADCAST to everyone to refetch their state so they see the vote or the loader
      broadcastRefreshSignal();
      
      // 3. Fallback Optimistic UI (if threshold was hit via network desync but not locally)
      if (data.status === "regeneration_started" || data.status === "already_regenerating") {
         if (!thresholdExceeded) {
             setTrip((prev) => {
                 if (!prev) return prev;
                 const newTrip = JSON.parse(JSON.stringify(prev));
                 if (!newTrip.ai_data.regenerating_keys) newTrip.ai_data.regenerating_keys = {};
                 newTrip.ai_data.regenerating_keys[voteKey] = true;
                 return newTrip;
             });
         }
      }
    } catch(e) {
      console.error("Voting failed", e);
    }
  };

  return (
    <main className="min-h-screen bg-[#0A0A0A] text-white pb-24">
      {/* Ambient */}
      <div className="fixed inset-0 pointer-events-none z-0">
        <div className="absolute top-0 left-1/4 w-[500px] h-[500px] rounded-full bg-[#00F0FF]/4 blur-[160px]" />
        <div className="absolute bottom-0 right-1/4 w-[500px] h-[500px] rounded-full bg-[#8A2BE2]/4 blur-[160px]" />
      </div>

      <div className="relative z-10 max-w-4xl mx-auto px-6">

        {/* ── Back button & Multiplayer Header ────────────────────── */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pt-28 pb-8 gap-4">
          <motion.button
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            onClick={() => router.push("/dashboard")}
            className="flex items-center gap-2 text-white/40 hover:text-white/80 text-sm transition-colors"
          >
            <ArrowLeft className="h-4 w-4" /> Back to My Trips
          </motion.button>

          {/* Multiplayer Online Users */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex items-center gap-3 bg-white/5 border border-white/10 rounded-full px-4 py-2"
            >
              <div className="flex items-center gap-2 text-xs text-white/70">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#22C55E] opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-[#22C55E]"></span>
                </span>
                {isHost ? `You are hosting. ${onlineUsers.length} viewing.` : "Live viewing Host's trip."}
              </div>
              <div className="flex items-center -space-x-2">
                {onlineUsers.slice(0, 4).map((ou, idx) => (
                  <div
                    key={ou.id}
                    className="h-7 w-7 rounded-full flex items-center justify-center text-xs font-bold text-white border border-black z-10"
                    style={{
                      background: `hsl(${(ou.avatarId || idx) * 36}, 80%, 60%)`,
                      boxShadow: "0 0 10px rgba(255,255,255,0.1)"
                    }}
                    title={ou.name}
                  >
                    {ou.name.charAt(0).toUpperCase()}
                  </div>
                ))}
                {onlineUsers.length > 4 && (
                  <div className="h-7 w-7 rounded-full bg-white/10 flex items-center justify-center text-[10px] text-white border border-black z-0">
                    +{onlineUsers.length - 4}
                  </div>
                )}
              </div>
            </motion.div>
        </div>

        {/* ── Hero card ────────────────────────────────────────────── */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.55, ease: [0.32, 0.72, 0, 1] }}
          className="rounded-3xl bg-gradient-to-br from-white/[0.06] to-white/[0.02] border border-white/10 p-8 mb-10 relative group"
        >
          {isHost && (
            <div className="absolute top-6 right-6 flex items-center gap-3">
              <button
                onClick={async () => {
                  if (!session) return;
                  const newStatus = !trip.is_public;
                  // Optimistic update
                  setTrip({ ...trip, is_public: newStatus });
                  try {
                    const res = await fetch(`${API_BASE}/api/itineraries/${id}`, {
                      method: "PATCH",
                      headers: {
                        "Authorization": `Bearer ${session.access_token}`,
                        "Content-Type": "application/json",
                      },
                      body: JSON.stringify({ is_public: newStatus }),
                    });
                    if (!res.ok) throw new Error();
                    toast.success(newStatus ? "Published to Discover!" : "Trip is now private.");
                  } catch (e) {
                    setTrip({ ...trip, is_public: !newStatus });
                    toast.error("Failed to update status.");
                  }
                }}
                className={`flex items-center justify-center gap-2 transition-colors py-2 px-4 rounded-full text-xs font-medium backdrop-blur-md border ${
                  trip.is_public 
                    ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20 hover:bg-emerald-500/20" 
                    : "bg-white/5 text-white/40 border-white/10 hover:bg-white/10 hover:text-white/60"
                }`}
              >
                {trip.is_public ? <Globe className="h-4 w-4" /> : <Lock className="h-4 w-4" />}
                {trip.is_public ? "Public" : "Private"}
              </button>

              <button 
                onClick={isEditing ? handleSave : handleEditToggle}
                disabled={isSaving}
                className="flex items-center justify-center gap-2 bg-white/10 hover:bg-white/20 transition-colors text-white py-2 px-4 rounded-full text-xs font-medium backdrop-blur-md border border-white/10"
              >
                {isSaving ? <Loader2 className="h-4 w-4 animate-spin" /> : isEditing ? <Save className="h-4 w-4" /> : <Edit2 className="h-4 w-4" />}
                {isEditing ? "Save Changes" : "Edit Trip"}
              </button>
            </div>
          )}

          {isEditing ? (
            <input 
              className="bg-transparent border-b border-white/20 text-[#00F0FF]/60 uppercase tracking-widest text-xs mb-3 outline-none focus:border-[#00F0FF]/60 w-full md:w-1/2"
              value={editDestination}
              onChange={(e) => setEditDestination(e.target.value)}
              placeholder="Destination"
            />
          ) : (
            <p className="text-xs text-[#00F0FF]/60 uppercase tracking-widest mb-3">
              {trip.destination}
            </p>
          )}

          {isEditing ? (
            <input 
              className="bg-transparent border-b border-white/20 text-3xl sm:text-4xl font-bold text-white mb-3 leading-tight outline-none focus:border-white/50 w-full block"
              style={{ fontFamily: "'Space Grotesk', sans-serif" }}
              value={editTitle}
              onChange={(e) => setEditTitle(e.target.value)}
              placeholder="Trip Title"
            />
          ) : (
            <h1 className="text-3xl sm:text-4xl font-bold text-white mb-3 leading-tight"
                style={{ fontFamily: "'Space Grotesk', sans-serif" }}>
              {experience.trip_title || trip.title}
            </h1>
          )}

          {isEditing ? (
            <textarea 
              className="bg-black/20 border border-white/10 text-white/70 text-sm leading-relaxed w-full min-h-[80px] p-3 rounded-xl outline-none focus:border-white/30 resize-none mt-2"
              value={editVibe}
              onChange={(e) => setEditVibe(e.target.value)}
              placeholder="Vibe Summary"
            />
          ) : experience.vibe_summary && (
            <p className="text-white/50 text-sm leading-relaxed max-w-2xl">
              {experience.vibe_summary}
            </p>
          )}

          <div className="flex flex-wrap gap-4 mt-5 text-sm text-white/40">
            {trip.start_date && (
              <span className="flex items-center gap-1.5">
                <Calendar className="h-4 w-4 text-[#8A2BE2]/60" />
                {trip.start_date}{trip.end_date ? ` → ${trip.end_date}` : ""}
              </span>
            )}
            {logistics?.total_estimated_budget_usd && (
              <span className="flex items-center gap-1.5">
                <DollarSign className="h-4 w-4 text-[#00F0FF]/60" />
                Est. ${logistics.total_estimated_budget_usd.toLocaleString()} total
              </span>
            )}
          </div>
        </motion.div>

        {/* ── Day-by-day itinerary ─────────────────────────────────── */}
        {experience.itinerary?.map((day: any, di: number) => (
          <motion.section
            key={day.day_number}
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 + di * 0.08, duration: 0.5 }}
            className="mb-10"
          >
            <div className="flex items-center gap-3 mb-4">
              <span className="flex items-center justify-center h-8 w-8 rounded-xl text-xs font-bold"
                    style={{ background: "linear-gradient(135deg, #00F0FF22, #8A2BE222)", border: "1px solid rgba(0,240,255,0.2)", color: "#00F0FF" }}>
                {day.day_number}
              </span>
              <h2 className="text-white/70 font-semibold text-sm uppercase tracking-widest"
                  style={{ fontFamily: "'Space Grotesk', sans-serif" }}>
                Day {day.day_number}
              </h2>
            </div>
            <div className="flex flex-col gap-3 pl-11">
              {day.activities?.map((act: any, ai: number) => {
                const globalActivityId = `${day.day_number}-${ai}`;
                const voteKey = `day_${di}_act_${ai}`; // Use di, since it matches the zero-based array index backend needs, not day.day_number!
                
                const votes = trip.ai_data?.votes?.[voteKey] || [];
                const isRegenerating = trip.ai_data?.regenerating_keys?.[voteKey] === true;

                return (
                  <ActivityCard 
                    key={ai} 
                    act={act} 
                    i={ai} 
                    voteKey={voteKey}
                    votes={votes}
                    isRegenerating={isRegenerating}
                    onVote={() => handleVoteRegenerate(di, ai)}
                    totalOnline={Math.max(1, onlineUsers.length)}
                    isHighlighted={highlightedActivityId === globalActivityId}
                    onClick={() => broadcastActivityHighlight(globalActivityId)}
                  />
                );
              })}
            </div>
          </motion.section>
        ))}

        {/* ── Logistics ────────────────────────────────────────────── */}
        {logistics && (
          <motion.section
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
            className="mt-12"
          >
            <h2 className="text-white/60 text-sm uppercase tracking-widest font-semibold mb-5"
                style={{ fontFamily: "'Space Grotesk', sans-serif" }}>
              Logistics
            </h2>

            {/* Flights */}
            {logistics.flights?.length > 0 && (
              <div className="mb-6">
                <p className="text-white/40 text-xs flex items-center gap-1.5 mb-3">
                  <Plane className="h-3.5 w-3.5" /> Flights
                </p>
                <div className="flex flex-col gap-3">
                  {logistics.flights.map((f: any, i: number) => (
                    <div key={i} className="flex items-center justify-between p-4 rounded-2xl bg-white/[0.03] border border-white/8">
                      <div>
                        <p className="text-white/80 text-sm font-medium">{f.airline_type}</p>
                        <p className="text-white/40 text-xs mt-0.5">{f.description}</p>
                      </div>
                      <div className="text-right">
                        <p className="text-[#00F0FF] font-bold text-sm">${f.estimated_price_usd}</p>
                        {f.booking_link && (
                          <a href={f.booking_link} target="_blank" rel="noopener noreferrer"
                             className="text-[10px] text-white/30 hover:text-[#00F0FF]/60 transition-colors">
                            Book →
                          </a>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Accommodations */}
            {logistics.accommodations?.length > 0 && (
              <div className="mb-6">
                <p className="text-white/40 text-xs flex items-center gap-1.5 mb-3">
                  <Hotel className="h-3.5 w-3.5" /> Accommodations
                </p>
                <div className="flex flex-col gap-3">
                  {logistics.accommodations.map((a: any, i: number) => (
                    <div key={i} className="flex items-center justify-between p-4 rounded-2xl bg-white/[0.03] border border-white/8">
                      <div>
                        <p className="text-white/80 text-sm font-medium">{a.type}</p>
                        <p className="text-white/40 text-xs mt-0.5">{a.neighborhood}</p>
                      </div>
                      <div className="text-right">
                        <p className="text-[#8A2BE2] font-bold text-sm">${a.estimated_price_per_night_usd}/night</p>
                        {a.booking_link && (
                          <a href={a.booking_link} target="_blank" rel="noopener noreferrer"
                             className="text-[10px] text-white/30 hover:text-[#8A2BE2]/60 transition-colors">
                            Book →
                          </a>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Multimodal Transport Dashboard */}
            {logistics.transit_options && Object.keys(logistics.transit_options).length > 0 && (
              <div>
                <TransportDashboard options={logistics.transit_options} />
              </div>
            )}

          </motion.section>
        )}
      </div>
    </main>
  );
}
