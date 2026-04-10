"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { motion } from "motion/react";
import { useAuth } from "@/context/AuthContext";
import {
  ArrowLeft, MapPin, Calendar, Loader2,
  Plane, Hotel, Star, Clock, DollarSign,
} from "lucide-react";

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
}

interface FinalTripPlan {
  experience: ExperienceData;
  logistics?: TripLogistics;
}

interface SavedTrip {
  id: string;
  title: string;
  destination: string;
  start_date: string | null;
  end_date: string | null;
  created_at: string;
  ai_data: FinalTripPlan;
}

// ── Activity Card ─────────────────────────────────────────────────
function ActivityCard({ act, i }: { act: Activity; i: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -16 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: i * 0.06, duration: 0.4 }}
      className="flex gap-4 p-4 rounded-2xl bg-white/[0.03] border border-white/8 hover:border-white/15 transition-all"
    >
      {act.image_url && (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={act.image_url}
          alt={act.title}
          className="w-20 h-20 object-cover rounded-xl shrink-0"
          onError={(e) => { (e.target as HTMLImageElement).style.display = "none"; }}
        />
      )}
      <div className="flex flex-col gap-1 min-w-0">
        <p className="text-white/90 font-semibold text-sm leading-snug line-clamp-2"
           style={{ fontFamily: "'Space Grotesk', sans-serif" }}>
          {act.title}
        </p>
        {act.description && (
          <p className="text-white/45 text-xs leading-relaxed line-clamp-3">
            {act.description}
          </p>
        )}
        <div className="flex flex-wrap gap-3 mt-1">
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

  useEffect(() => {
    if (!authLoading && !isAuthenticated) router.push("/login");
  }, [authLoading, isAuthenticated, router]);

  useEffect(() => {
    if (!session || !id) return;
    const load = async () => {
      setLoading(true);
      try {
        const res = await fetch(`${API_BASE}/api/itineraries/${id}`, {
          headers: { Authorization: `Bearer ${session.access_token}` },
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        setTrip(data);
      } catch (e: unknown) {
        setError(e instanceof Error ? e.message : "Failed to load trip.");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [session, id]);

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

  return (
    <main className="min-h-screen bg-[#0A0A0A] text-white pb-24">
      {/* Ambient */}
      <div className="fixed inset-0 pointer-events-none z-0">
        <div className="absolute top-0 left-1/4 w-[500px] h-[500px] rounded-full bg-[#00F0FF]/4 blur-[160px]" />
        <div className="absolute bottom-0 right-1/4 w-[500px] h-[500px] rounded-full bg-[#8A2BE2]/4 blur-[160px]" />
      </div>

      <div className="relative z-10 max-w-4xl mx-auto px-6">

        {/* ── Back button ─────────────────────────────────────────── */}
        <motion.button
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          onClick={() => router.push("/dashboard")}
          className="flex items-center gap-2 pt-28 pb-8 text-white/40 hover:text-white/80 text-sm transition-colors"
        >
          <ArrowLeft className="h-4 w-4" /> Back to My Trips
        </motion.button>

        {/* ── Hero card ────────────────────────────────────────────── */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.55, ease: [0.32, 0.72, 0, 1] }}
          className="rounded-3xl bg-gradient-to-br from-white/[0.06] to-white/[0.02] border border-white/10 p-8 mb-10"
        >
          <p className="text-xs text-[#00F0FF]/60 uppercase tracking-widest mb-3">
            {trip.destination}
          </p>
          <h1 className="text-3xl sm:text-4xl font-bold text-white mb-3 leading-tight"
              style={{ fontFamily: "'Space Grotesk', sans-serif" }}>
            {experience.trip_title || trip.title}
          </h1>
          {experience.vibe_summary && (
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
        {experience.itinerary?.map((day, di) => (
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
              {day.activities?.map((act, ai) => (
                <ActivityCard key={ai} act={act} i={ai} />
              ))}
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
                  {logistics.flights.map((f, i) => (
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
              <div>
                <p className="text-white/40 text-xs flex items-center gap-1.5 mb-3">
                  <Hotel className="h-3.5 w-3.5" /> Accommodations
                </p>
                <div className="flex flex-col gap-3">
                  {logistics.accommodations.map((a, i) => (
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
          </motion.section>
        )}
      </div>
    </main>
  );
}
