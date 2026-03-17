import { motion } from "motion/react";
import { 
  MapPin, 
  Calendar, 
  Users,
  Plane,
  Hotel,
  Clock,
  Sparkles,
  ArrowRight
} from "lucide-react";
import Image from "next/image";

export interface Activity {
  type: "flight" | "hotel" | "experience";
  title: string;
  description?: string;
  time?: string;
  cost?: string;
  location?: string;
  agent?: "logistics" | "experience";
  image?: string;
  airline?: string;
  flightNumber?: string;
  nights?: number;
}

export interface ItineraryDay {
  day_number: number;
  activities: Activity[];
}

export interface ItineraryData {
  trip_title: string;
  vibe_summary: string;
  itinerary: ItineraryDay[];
  destination?: string;
  travelers?: number | string;
  budget?: string;
}

export function ItineraryOutput({ data, formData }: { data: ItineraryData, formData?: any }) {
  const itineraryItems = data.itinerary || [];
  
  // Helper to enrich activities with agent tags and icons
  const processActivities = (activities: Activity[]) => {
    return activities.map(act => ({
      ...act,
      agent: act.type === 'experience' ? 'experience' : 'logistics' as const
    }));
  };

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
            {data.trip_title.toUpperCase()}
          </h2>
          <p className="text-xl text-gray-500 dark:text-white/60 mb-8 max-w-2xl mx-auto" style={{ fontFamily: "'Inter', sans-serif" }}>
            {data.vibe_summary}
          </p>

          {/* Agent indicators */}
          <div className="flex items-center justify-center gap-8">
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
          </div>
        </motion.div>

        {/* Split Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
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
                    <p className="text-gray-900 dark:text-white font-semibold" style={{ fontFamily: "'Inter', sans-serif" }}>{data.destination || formData?.destination}</p>
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
                    <p className="text-gray-900 dark:text-white font-semibold" style={{ fontFamily: "'Inter', sans-serif" }}>{data.travelers || formData?.travelers} People</p>
                  </div>
                </div>
              </div>

              <div className="mt-6 pt-6 border-t border-gray-200 dark:border-white/10">
                <div className="flex items-center justify-between">
                  <span className="text-gray-500 dark:text-white/60" style={{ fontFamily: "'Inter', sans-serif" }}>Estimated Cost</span>
                  <span className="text-3xl font-bold text-gray-900 dark:text-white" style={{ fontFamily: "'Space Grotesk', sans-serif" }}>
                    TBD
                  </span>
                </div>
                <p className="text-[10px] text-gray-400 mt-2 italic text-center uppercase tracking-widest">Pricing locked by Logistics Agent</p>
              </div>
            </div>

            {/* Map Placeholder */}
            <div className="backdrop-blur-xl bg-white/80 dark:bg-white/5 border border-gray-200 dark:border-white/10 rounded-[24px] p-6 shadow-[0_8px_32px_rgba(0,0,0,0.08)] dark:shadow-[0_8px_32px_rgba(0,0,0,0.4)] aspect-square relative overflow-hidden">
              <Image 
                src="https://images.unsplash.com/photo-1679766826593-738e9b6338c6?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxleG90aWMlMjB0cm9waWNhbCUyMGJlYWNoJTIwcGFyYWRpc2UlMjBjaW5lbWF0aWN8ZW58MXx8fHwxNzczNjcyODQ5fDA&ixlib=rb-4.1.0&q=80&w=1080"
                alt="Destination"
                fill
                sizes="(max-width: 768px) 100vw, 33vw"
                className="object-cover rounded-[16px]"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black via-transparent to-transparent rounded-[16px]" />
              <div className="absolute bottom-4 left-4 right-4">
                <p className="text-white text-lg font-bold" style={{ fontFamily: "'Space Grotesk', sans-serif" }}>
                  {data.destination}
                </p>
              </div>
            </div>
          </motion.div>

          {/* Right Scrollable Content - Bento Grid */}
          <div className="lg:col-span-2 space-y-12">
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
                      whileHover={{ scale: 1.02, y: -4 }}
                      className={`backdrop-blur-xl bg-white/80 dark:bg-white/5 border rounded-[24px] overflow-hidden shadow-[0_8px_32px_rgba(0,0,0,0.08)] dark:shadow-[0_8px_32px_rgba(0,0,0,0.4)] ${
                        activity.agent === "logistics" 
                          ? "border-[#00F0FF]/20" 
                          : "border-[#8A2BE2]/20"
                      } ${
                        activity.type === "experience" && activity.image
                          ? "md:col-span-2 h-80"
                          : "h-64"
                      }`}
                    >
                      {activity.type === "experience" ? (
                        // Experience Card with Image
                        <div className="relative h-full">
                          {activity.image ? (
                            <Image 
                              src={activity.image} 
                              alt={activity.title}
                              fill
                              sizes="(max-width: 768px) 100vw, 50vw"
                              className="object-cover"
                            />
                          ) : (
                             // Fallback colorful background if no image
                             <div className="absolute inset-0 bg-gradient-to-br from-[#8A2BE2]/20 to-[#FF1493]/20" />
                          )}
                          <div className="absolute inset-0 bg-gradient-to-t from-black via-black/40 to-transparent" />
                          <div className="relative h-full flex flex-col justify-end p-8">
                            <div className="flex items-center gap-2 mb-3">
                              <div className="px-3 py-1 rounded-full bg-[#8A2BE2]/20 backdrop-blur-sm border border-[#8A2BE2]/30">
                                <Sparkles className="h-3 w-3 text-[#8A2BE2] inline mr-1" />
                                <span className="text-[#8A2BE2] text-xs font-semibold" style={{ fontFamily: "'Inter', sans-serif" }}>
                                  Experience Agent
                                </span>
                              </div>
                            </div>
                            <h4 className="text-3xl font-bold text-white mb-2" style={{ fontFamily: "'Space Grotesk', sans-serif" }}>
                              {activity.title}
                            </h4>
                            <p className="text-white/80 mb-3 line-clamp-2" style={{ fontFamily: "'Inter', sans-serif" }}>
                              {activity.description}
                            </p>
                            <div className="flex items-center justify-between">
                              <div className="flex items-center gap-2 text-white/80">
                                <Clock className="h-4 w-4" />
                                <span className="text-sm" style={{ fontFamily: "'Inter', sans-serif" }}>{activity.time}</span>
                              </div>
                              {activity.cost && (
                                <span className="text-xl font-bold text-white" style={{ fontFamily: "'Space Grotesk', sans-serif" }}>
                                  {activity.cost}
                                </span>
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

                  {/* Automatic Logistics Skeletons (One per day to hold space) */}
                  <div className="backdrop-blur-xl bg-white/5 border border-[#00F0FF]/10 rounded-[24px] p-6 h-64 flex flex-col items-center justify-center opacity-30">
                     <Hotel className="h-10 w-10 text-[#00F0FF] mb-4" />
                     <p className="text-[#00F0FF] font-bold text-[10px] uppercase tracking-widest text-center">Logistics: Stay & Transit<br/>Calculating best routes...</p>
                  </div>
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
