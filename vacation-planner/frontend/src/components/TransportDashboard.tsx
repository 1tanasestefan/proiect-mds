"use client";

import { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import { motion, AnimatePresence } from "motion/react";
import { Train, Bus, Car, Plane } from "lucide-react";

// Types matching our Python backend models
interface Coordinate {
  lat: number;
  lng: number;
}

interface TransportLeg {
  mode: string;
  name: string;
  origin_coords: Coordinate;
  destination_coords: Coordinate;
  price: number;
  duration_minutes: number;
  polyline: string | null; // GeoJSON string
}

export interface ConsolidatedLogistics {
  total_price: number;
  currency: string;
  legs: TransportLeg[];
  map_center: Coordinate;
}

interface Props {
  options: Record<string, ConsolidatedLogistics>;
}

// Dynamically import the map to avoid Next.js SSR window is not defined errors
const TransportMapSSR = dynamic<{ currentOption: ConsolidatedLogistics }>(
  () => import("./TransportMap"),
  { ssr: false, loading: () => <div className="w-full h-full bg-white/5 animate-pulse rounded-2xl" /> }
);

export function TransportDashboard({ options }: Props) {
  const [activeTier, setActiveTier] = useState<string>("budget");

  // Default to balanced → budget → first available tier
  // MUST be before any early returns (React rules of hooks)
  useEffect(() => {
    if (options["balanced"]) setActiveTier("balanced");
    else if (options["budget"]) setActiveTier("budget");
    else setActiveTier(Object.keys(options)[0] ?? "budget");
  }, [options]);

  // Fallback if no valid options provided
  if (!options || Object.keys(options).length === 0) return null;

  const currentOption = options[activeTier];
  if (!currentOption) return null;

  const modeIcons: Record<string, React.ReactNode> = {
    flight: <Plane className="h-4 w-4" />,
    train: <Train className="h-4 w-4" />,
    bus: <Bus className="h-4 w-4" />,
    uber: <Car className="h-4 w-4" />
  };

  return (
    <div className="flex flex-col md:flex-row gap-6 mt-8 p-6 rounded-[32px] bg-white border border-[#FF6B5A]/20 shadow-xl">
      
      {/* Configuration Panel */}
      <div className="flex flex-col gap-6 md:w-80 shrink-0">
        <div>
          <h3 className="text-xl font-bold text-[#10223A] mb-2" style={{ fontFamily: "'Space Grotesk', sans-serif" }}>
            Transfers & Commute
          </h3>
          <p className="text-[#10223A]/50 text-sm">
            Select your preferred arrival transfer mode. The map will update automatically.
          </p>
        </div>

        {/* Toggles */}
        <div className="flex flex-col gap-3">
          {Object.keys(options).map((tierKey) => {
            const isActive = activeTier === tierKey;
            const price = options[tierKey].total_price;
            
            return (
              <button
                key={tierKey}
                onClick={() => setActiveTier(tierKey)}
                className={`relative overflow-hidden flex items-center justify-between p-4 rounded-2xl border transition-all duration-300 ${
                  isActive 
                    ? "bg-[#FFF6E8] border-[#FF6B5A]" 
                    : "bg-[#FFF6E8]/50 border-[#FF6B5A]/20 hover:border-[#FF6B5A]/50 hover:bg-[#FFF6E8]"
                }`}
              >
                <div className="flex flex-col items-start z-10">
                  <span className="text-[#10223A] font-medium capitalize">{tierKey}</span>
                  <span className="text-[#10223A]/50 text-xs mt-0.5">
                    {options[tierKey].legs.length > 1 ? options[tierKey].legs[1].name : "Standard Flight"}
                  </span>
                </div>
                <div className="z-10 font-bold text-[#FF6B5A]">
                  ${price}
                </div>
                {isActive && (
                  <motion.div layoutId="activeTier" className="absolute inset-0 bg-gradient-to-r from-[#FF6B5A]/10 to-transparent pointer-events-none" />
                )}
              </button>
            )
          })}
        </div>

        {/* Dynamic Total Price Badge */}
        <AnimatePresence mode="popLayout">
          <motion.div
            key={activeTier}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="mt-auto p-5 rounded-2xl bg-gradient-to-br from-[#FF6B5A] to-[#FF9F43] border border-[#FF6B5A]/30 text-center shadow-lg"
          >
            <p className="text-white/80 text-xs uppercase tracking-widest mb-1.5">Total Travel Cost</p>
            <p className="text-3xl font-bold text-white">${currentOption.total_price}</p>
          </motion.div>
        </AnimatePresence>
      </div>

      {/* Map Canvas */}
      <div className="relative flex-1 min-h-[400px] md:min-h-[500px] rounded-3xl overflow-hidden border border-[#FF6B5A]/20 bg-[#f5f5f5]">
         <TransportMapSSR currentOption={currentOption} />
         
         {/* Route overlay details */}
         <div className="absolute bottom-4 left-4 right-4 flex gap-2 overflow-x-auto pb-2 z-[400]">
           {currentOption.legs.map((leg, i) => (
             <div key={i} className="flex items-center gap-3 px-4 py-3 rounded-2xl bg-white/90 backdrop-blur-md border border-[#FF6B5A]/20 text-[#10223A] whitespace-nowrap shadow-lg">
                <div className="flex items-center justify-center w-8 h-8 rounded-full bg-[#FFF6E8] text-[#FF6B5A]">
                  {modeIcons[leg.mode] || <Plane className="h-4 w-4" />}
                </div>
                <div>
                   <p className="text-sm font-semibold">{leg.name}</p>
                   <p className="text-xs text-[#10223A]/50">{leg.duration_minutes} mins</p>
                </div>
             </div>
           ))}
         </div>
      </div>
    </div>
  );
}
