import { useState } from "react";
import { motion } from "motion/react";
import { 
  MapPin, 
  Calendar, 
  Users,
  Plane,
  Hotel,
  Clock,
  Sparkles,
  ArrowRight,
  ExternalLink,
  DollarSign,
  Bed,
  Bookmark,
  CheckCircle2,
} from "lucide-react";
import { ImageWithFallback } from "@/components/figma/ImageWithFallback";
import { useAuth } from "@/context/AuthContext";
import { supabase } from "@/lib/supabase";

export interface Activity {
  type: "flight" | "hotel" | "experience";
  title: string;
  description?: string;
  time?: string;
  cost?: string;
  location?: string;
  agent?: "logistics" | "experience";
  image?: string;
  image_url?: string;
  airline?: string;
  flightNumber?: string;
  nights?: number;
}

export interface ItineraryDay {
  day_number: number;
  activities: Activity[];
}

export interface FlightOption {
  airline_type: string;
  estimated_price_usd: number;
  description: string;
  booking_link: string;
}

export interface AccommodationOption {
  type: string;
  neighborhood: string;
  estimated_price_per_night_usd: number;
  booking_link: string;
}

export interface TripLogistics {
  flights: FlightOption[];
  accommodations: AccommodationOption[];
  total_estimated_budget_usd: number;
}

export interface ItineraryData {
  trip_title: string;
  vibe_summary: string;
  itinerary: ItineraryDay[];
  destination?: string;
  travelers?: number | string;
  budget?: string;
}

export interface FinalTripPlan {
  experience: ItineraryData;
  logistics: TripLogistics;
}

type TripFormData = {
  budget?: string;
  lifestyle?: string;
  vacationType?: string;
  origin?: string;
  destination?: string;
  startDate?: string;
  endDate?: string;
  travelers?: number | string;
};

export function ItineraryOutput({ data, formData, onReset }: { data: FinalTripPlan, formData?: TripFormData | null, onReset: () => void }) {
  const { isAuthenticated } = useAuth();
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  
  const experience = data.experience;
  const logistics = data.logistics;
  const itineraryItems = experience.itinerary || [];
  const destination = experience.destination || formData?.destination || "";

  const handleSaveToMyTrips = async () => {
    if (!isAuthenticated) return;
    setIsSaving(true);
    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session) throw new Error("No active session");

      const response = await fetch("http://127.0.0.1:8000/api/itineraries/save", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${session.access_token}`
        },
        body: JSON.stringify({
          title: experience.trip_title || `Trip to ${destination}`,
          destination: destination,
          start_date: formData?.startDate || null,
          end_date: formData?.endDate || null,
          is_public: false,
          ai_data: data
        })
      });

      if (!response.ok) {
        throw new Error("Failed to save itinerary");
      }

      setSaveSuccess(true);
      setTimeout(() => {
        window.location.href = '/dashboard';
      }, 1500);
    } catch (error) {
      console.error("Save error:", error);
      alert("Failed to save itinerary. Please try again.");
    } finally {
      setIsSaving(false);
    }
  };

  const fallbackImage = (query: string) =>
    `https://placehold.co/600x400/1a1a2e/8A2BE2?text=${encodeURIComponent(query.slice(0, 60))}&font=raleway`;

  return (
    <section className="min-h-screen bg-gray-100 dark:bg-[#0A0A0A] py-24 px-8 relative overflow-hidden">
      {/* Background effects */}
      <div className="absolute top-20 right-20 h-96 w-96 rounded-full bg-[#00F0FF]/5 dark:bg-[#00F0FF]/10 blur-[150px]" />
      <div className="absolute bottom-20 left-20 h-96 w-96 rounded-full bg-[#8A2BE2]/5 dark:bg-[#8A2BE2]/10 blur-[150px]" />

      <div className="max-w-[1800px] mx-auto">
        {/* Header */}
        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          className="text-center mb-16"
        >
          <h2 
            className="text-6xl md:text-7xl font-black mb-6 bg-gradient-to-r from-gray-900 dark:from-white to-gray-500 dark:to-white/60 bg-clip-text text-transparent"
            style={{ fontFamily: "'Archivo Black', sans-serif" }}
          >
            {experience.trip_title.toUpperCase()}
          </h2>
          <p className="text-xl text-gray-500 dark:text-white/60 mb-8 max-w-2xl mx-auto" style={{ fontFamily: "'Inter', sans-serif" }}>
            {experience.vibe_summary}
          </p>

          <div className="flex flex-col md:flex-row items-center justify-center gap-4">
            <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-[#8A2BE2]/10 border border-[#8A2BE2]/30">
              <Sparkles className="h-4 w-4 text-[#8A2BE2]" />
              <span className="text-[#8A2BE2] text-sm font-semibold" style={{ fontFamily: "'Inter', sans-serif" }}>
                Experience Agent
              </span>
            </div>
            <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-[#00F0FF]/10 border border-[#00F0FF]/30">
              <Plane className="h-4 w-4 text-[#00F0FF]" />
              <span className="text-[#00F0FF] text-sm font-semibold" style={{ fontFamily: "'Inter', sans-serif" }}>
                Logistics Agent
              </span>
            </div>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={onReset}
              className="px-4 py-2 rounded-full bg-white/5 border border-white/10 text-white/60 hover:text-white transition-colors text-sm font-semibold"
              style={{ fontFamily: "'Inter', sans-serif" }}
            >
              Plan Another Trip
            </motion.button>
          </div>
        </motion.div>

        {/* Split Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-[420px_1fr] gap-8">
          {/* Left Sticky Sidebar - Summary */}
          <motion.div
            initial={{ x: -50, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="lg:sticky lg:top-8 h-fit space-y-6"
          >
            {/* Trip Summary Card */}
            <div className="backdrop-blur-xl bg-white/80 dark:bg-white/5 border border-gray-200 dark:border-white/10 rounded-[24px] p-8 shadow-[0_8px_32px_rgba(0,0,0,0.08)] dark:shadow-[0_8px_32px_rgba(0,0,0,0.4)]">
              <h3 
                className="text-2xl font-bold text-gray-900 dark:text-white mb-6"
                style={{ fontFamily: "'Space Grotesk', sans-serif" }}
              >
                Trip Summary
              </h3>
              
              <div className="space-y-4">
                <div className="flex items-center gap-3">
                  <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-[#00F0FF] to-[#0080FF] flex items-center justify-center">
                    <MapPin className="h-5 w-5 text-white" />
                  </div>
                  <div>
                    <p className="text-gray-400 dark:text-white/60 text-sm" style={{ fontFamily: "'Inter', sans-serif" }}>Destination</p>
                    <p className="text-gray-900 dark:text-white font-semibold" style={{ fontFamily: "'Inter', sans-serif" }}>{experience.destination || formData?.destination}</p>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-[#8A2BE2] to-[#FF1493] flex items-center justify-center">
                    <Calendar className="h-5 w-5 text-white" />
                  </div>
                  <div>
                    <p className="text-gray-400 dark:text-white/60 text-sm" style={{ fontFamily: "'Inter', sans-serif" }}>Duration</p>
                    <p className="text-gray-900 dark:text-white font-semibold" style={{ fontFamily: "'Inter', sans-serif" }}>{itineraryItems.length} Days</p>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center">
                    <Users className="h-5 w-5 text-white" />
                  </div>
                  <div>
                    <p className="text-gray-400 dark:text-white/60 text-sm" style={{ fontFamily: "'Inter', sans-serif" }}>Travelers</p>
                    <p className="text-gray-900 dark:text-white font-semibold" style={{ fontFamily: "'Inter', sans-serif" }}>{experience.travelers || formData?.travelers} People</p>
                  </div>
                </div>
              </div>

              <div className="mt-6 pt-6 border-t border-gray-200 dark:border-white/10">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-gray-500 dark:text-white/60" style={{ fontFamily: "'Inter', sans-serif" }}>Estimated Budget</span>
                  <span className="text-3xl font-bold text-gray-900 dark:text-white" style={{ fontFamily: "'Space Grotesk', sans-serif" }}>
                    ${logistics.total_estimated_budget_usd.toLocaleString()}
                  </span>
                </div>
                <p className="text-[10px] text-gray-400 italic text-center uppercase tracking-widest mb-6 border-b border-gray-100 dark:border-white/5 pb-6">
                  Per person · calculated by Logistics Agent
                </p>

                {/* Save to My Trips Action */}
                {isAuthenticated ? (
                  <motion.button
                    whileHover={{ scale: saveSuccess ? 1 : 1.02 }}
                    whileTap={{ scale: saveSuccess ? 1 : 0.98 }}
                    onClick={handleSaveToMyTrips}
                    disabled={isSaving || saveSuccess}
                    className={`w-full py-4 rounded-xl flex items-center justify-center gap-2 font-bold transition-all shadow-lg ${
                      saveSuccess 
                        ? "bg-emerald-500 text-white shadow-emerald-500/20" 
                        : "bg-gray-900 dark:bg-white text-white dark:text-gray-900 hover:bg-gray-800 dark:hover:bg-gray-100 shadow-gray-900/10 dark:shadow-white/10"
                    }`}
                    style={{ fontFamily: "'Inter', sans-serif" }}
                  >
                    {isSaving ? (
                      <div className="h-5 w-5 rounded-full border-2 border-current border-t-transparent animate-spin" />
                    ) : saveSuccess ? (
                      <>
                        <CheckCircle2 className="h-5 w-5" />
                        Saved to My Trips
                      </>
                    ) : (
                      <>
                        <Bookmark className="h-5 w-5" />
                        Save to My Trips
                      </>
                    )}
                  </motion.button>
                ) : (
                  <div className="text-center p-4 rounded-xl bg-[#00F0FF]/5 border border-[#00F0FF]/20">
                    <p className="text-sm text-[#00F0FF]" style={{ fontFamily: "'Inter', sans-serif" }}>
                      <a href="/login" className="font-bold underline hover:text-[#00F0FF]/80">Log in</a> to save this itinerary to your collections.
                    </p>
                  </div>
                )}
              </div>
            </div>
          </motion.div>

          {/* Right Scrollable Content - Bento Grid */}
          <div className="space-y-12">
            {itineraryItems.map((dayItem, dayIndex) => (
              <motion.div
                key={dayItem.day_number}
                initial={{ y: 50, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ delay: 0.1 * dayIndex }}
              >
                {/* Day Header */}
                <div className="flex items-center gap-4 mb-6">
                  <div className="h-12 w-12 rounded-2xl bg-gradient-to-br from-[#00F0FF] to-[#8A2BE2] flex items-center justify-center">
                    <span className="text-white font-bold text-lg" style={{ fontFamily: "'Space Grotesk', sans-serif" }}>
                      {dayItem.day_number}
                    </span>
                  </div>
                  <h3 className="text-2xl font-bold text-gray-900 dark:text-white" style={{ fontFamily: "'Space Grotesk', sans-serif" }}>
                    Day {dayItem.day_number}
                  </h3>
                </div>

                {/* Bento Grid for Activities */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Real Experiences */}
                  {dayItem.activities.map((activity, actIndex) => (
                    <motion.div
                      key={actIndex}
                      whileHover={{ y: -4 }}
                      className={`group backdrop-blur-xl bg-white/80 dark:bg-white/5 border rounded-[24px] overflow-hidden shadow-[0_8px_32px_rgba(0,0,0,0.08)] dark:shadow-[0_8px_32px_rgba(0,0,0,0.4)] transition-all duration-300 ${
                        activity.agent === "logistics" 
                          ? "border-[#00F0FF]/20" 
                          : "border-[#8A2BE2]/20"
                      } ${
                        activity.type === "experience" && (activity.image_url || activity.image)
                          ? "md:col-span-2 min-h-[320px]"
                          : "h-64"
                      }`}
                    >
                      {activity.type === "experience" ? (
                        // Experience Card Redesign
                        <div className="flex flex-col md:flex-row h-full">
                          {/* Image Section */}
                          <div className={`relative overflow-hidden ${
                            (activity.image_url || activity.image) ? "md:w-2/5 min-h-[200px] md:min-h-full" : "w-0"
                          }`}>
                            {(activity.image_url || activity.image) ? (
                              <>
                                <ImageWithFallback
                                  src={(activity.image_url || activity.image) as string}
                                  alt={activity.title}
                                  fallbackSrc={fallbackImage(`${destination} ${activity.title}`.trim())}
                                  loading="lazy"
                                  referrerPolicy="no-referrer"
                                  className="absolute inset-0 h-full w-full object-cover transition-transform duration-700 group-hover:scale-110"
                                />
                                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-transparent to-black/10 dark:to-[#0A0A0A]/20" />
                              </>
                            ) : (
                              <div className="absolute inset-0 bg-gradient-to-br from-[#00F0FF]/20 to-[#8A2BE2]/20 flex items-center justify-center">
                                <Sparkles className="h-12 w-12 text-white/20 animate-pulse" />
                              </div>
                            )}
                          </div>

                          {/* Content Section */}
                          <div className={`flex flex-col p-8 ${(activity.image_url || activity.image) ? "md:w-3/5" : "w-full"}`}>
                            <div className="flex items-center gap-2 mb-3">
                              <div className="px-3 py-1 rounded-full bg-[#8A2BE2]/10 dark:bg-[#8A2BE2]/20 backdrop-blur-sm border border-[#8A2BE2]/30">
                                <Sparkles className="h-3 w-3 text-[#8A2BE2] inline mr-1" />
                                <span className="text-[#8A2BE2] text-xs font-semibold" style={{ fontFamily: "'Inter', sans-serif" }}>
                                  Experience
                                </span>
                              </div>
                            </div>
                            
                            <h4 className="text-2xl font-bold text-gray-900 dark:text-white mb-3 group-hover:text-[#8A2BE2] transition-colors" style={{ fontFamily: "'Space Grotesk', sans-serif" }}>
                              {activity.title}
                            </h4>
                            
                            <p className="text-gray-500 dark:text-white/70 mb-6 line-clamp-3 leading-relaxed" style={{ fontFamily: "'Inter', sans-serif" }}>
                              {activity.description}
                            </p>
                            
                            <div className="mt-auto flex items-center justify-between">
                              <div className="flex flex-col gap-1">
                                <div className="flex items-center gap-2 text-gray-400 dark:text-white/40">
                                  <Clock className="h-3.5 w-3.5" />
                                  <span className="text-xs uppercase tracking-wider font-medium" style={{ fontFamily: "'Inter', sans-serif" }}>{activity.time}</span>
                                </div>
                                <div className="flex items-center gap-2 text-gray-400 dark:text-white/40">
                                  <MapPin className="h-3.5 w-3.5" />
                                  <span className="text-xs truncate max-w-[150px]" style={{ fontFamily: "'Inter', sans-serif" }}>{activity.location}</span>
                                </div>
                              </div>
                              
                              {activity.cost && (
                                <div className="text-right text-gray-900 dark:text-white">
                                  <p className="text-[10px] uppercase tracking-tighter text-gray-400">Est. Cost</p>
                                  <span className="text-xl font-bold" style={{ fontFamily: "'Space Grotesk', sans-serif" }}>
                                    {activity.cost}
                                  </span>
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      ) : (
                        // Logistics Card Placeholder
                        <div className="p-6 h-full flex flex-col items-center justify-center opacity-40 grayscale group">
                          <Plane className="h-12 w-12 text-[#00F0FF] mb-4 group-hover:animate-pulse" />
                          <p className="text-[#00F0FF] font-bold uppercase tracking-[0.2em] text-xs">Waiting for Logistics Agent</p>
                          <p className="text-white/20 text-[10px] mt-2 italic">Phase 3 Integration Pending</p>
                        </div>
                      )}
                    </motion.div>
                  ))}

                  {/* Logistics Cards (Flights & Hotels) */}
                  {dayIndex === 0 && logistics.flights.length > 0 && (
                    <motion.div
                      initial={{ y: 20, opacity: 0 }}
                      animate={{ y: 0, opacity: 1 }}
                      className="backdrop-blur-xl bg-white/80 dark:bg-white/5 border border-[#00F0FF]/20 rounded-[24px] p-6 h-fit"
                    >
                      <div className="flex items-center gap-2 mb-4">
                        <div className="px-3 py-1 rounded-full bg-[#00F0FF]/10 dark:bg-[#00F0FF]/20 border border-[#00F0FF]/30">
                          <Plane className="h-3 w-3 text-[#00F0FF] inline mr-1" />
                          <span className="text-[#00F0FF] text-xs font-semibold" style={{ fontFamily: "'Inter', sans-serif" }}>Flights</span>
                        </div>
                      </div>
                      <div className="space-y-3">
                        {logistics.flights.map((flight, fi) => (
                          <div key={fi} className="flex items-center justify-between p-3 rounded-xl bg-black/5 dark:bg-white/5">
                            <div>
                              <p className="text-sm font-semibold text-gray-900 dark:text-white" style={{ fontFamily: "'Inter', sans-serif" }}>{flight.airline_type}</p>
                              <p className="text-xs text-gray-400 dark:text-white/40">{flight.description}</p>
                            </div>
                            <div className="text-right flex items-center gap-3">
                              <span className="text-lg font-bold text-gray-900 dark:text-white" style={{ fontFamily: "'Space Grotesk', sans-serif" }}>${flight.estimated_price_usd}</span>
                              <a href={flight.booking_link} target="_blank" rel="noopener noreferrer" className="text-[#00F0FF] hover:text-[#00F0FF]/80 transition-colors">
                                <ExternalLink className="h-4 w-4" />
                              </a>
                            </div>
                          </div>
                        ))}
                      </div>
                    </motion.div>
                  )}

                  {dayIndex === 0 && logistics.accommodations.length > 0 && (
                    <motion.div
                      initial={{ y: 20, opacity: 0 }}
                      animate={{ y: 0, opacity: 1 }}
                      className="backdrop-blur-xl bg-white/80 dark:bg-white/5 border border-[#00F0FF]/20 rounded-[24px] p-6 h-fit"
                    >
                      <div className="flex items-center gap-2 mb-4">
                        <div className="px-3 py-1 rounded-full bg-[#00F0FF]/10 dark:bg-[#00F0FF]/20 border border-[#00F0FF]/30">
                          <Bed className="h-3 w-3 text-[#00F0FF] inline mr-1" />
                          <span className="text-[#00F0FF] text-xs font-semibold" style={{ fontFamily: "'Inter', sans-serif" }}>Accommodations</span>
                        </div>
                      </div>
                      <div className="space-y-3">
                        {logistics.accommodations.map((accom, ai) => (
                          <div key={ai} className="flex items-center justify-between p-3 rounded-xl bg-black/5 dark:bg-white/5">
                            <div>
                              <p className="text-sm font-semibold text-gray-900 dark:text-white" style={{ fontFamily: "'Inter', sans-serif" }}>{accom.type}</p>
                              <p className="text-xs text-gray-400 dark:text-white/40">{accom.neighborhood}</p>
                            </div>
                            <div className="text-right flex items-center gap-3">
                              <div>
                                <span className="text-lg font-bold text-gray-900 dark:text-white" style={{ fontFamily: "'Space Grotesk', sans-serif" }}>${accom.estimated_price_per_night_usd}</span>
                                <span className="text-[10px] text-gray-400 dark:text-white/40 block">/night</span>
                              </div>
                              <a href={accom.booking_link} target="_blank" rel="noopener noreferrer" className="text-[#00F0FF] hover:text-[#00F0FF]/80 transition-colors">
                                <ExternalLink className="h-4 w-4" />
                              </a>
                            </div>
                          </div>
                        ))}
                      </div>
                    </motion.div>
                  )}
                </div>
              </motion.div>
            ))}

            {/* Final CTA */}
            <motion.div
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.8 }}
              className="backdrop-blur-xl bg-gradient-to-r from-[#00F0FF]/5 dark:from-[#00F0FF]/10 to-[#8A2BE2]/5 dark:to-[#8A2BE2]/10 border border-gray-200 dark:border-white/10 rounded-[24px] p-12 text-center"
            >
              <h3 className="text-3xl font-bold text-gray-900 dark:text-white mb-4" style={{ fontFamily: "'Space Grotesk', sans-serif" }}>
                Ready to book this adventure?
              </h3>
              <p className="text-gray-500 dark:text-white/60 mb-8" style={{ fontFamily: "'Inter', sans-serif" }}>
                Save this itinerary or customize it further
              </p>
              <div className="flex gap-4 justify-center">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.98 }}
                  className="px-8 py-4 rounded-[16px] bg-gradient-to-r from-[#00F0FF] to-[#8A2BE2] text-white font-bold shadow-[0_0_30px_rgba(0,240,255,0.3)] flex items-center gap-2"
                  style={{ fontFamily: "'Space Grotesk', sans-serif" }}
                >
                  Book Now
                  <ArrowRight className="h-5 w-5" />
                </motion.button>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.98 }}
                  className="px-8 py-4 rounded-[16px] bg-black/5 dark:bg-white/5 border border-gray-300 dark:border-white/20 text-gray-900 dark:text-white font-bold"
                  style={{ fontFamily: "'Space Grotesk', sans-serif" }}
                >
                  Customize
                </motion.button>
              </div>
            </motion.div>
          </div>
        </div>
      </div>
    </section>
  );
}
