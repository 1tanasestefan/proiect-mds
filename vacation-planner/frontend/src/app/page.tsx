"use client";

import { useState } from 'react';
import { HeroSection } from '@/components/figma/hero-section';
import { InputFormSection } from '@/components/figma/input-form-section';
import { AIProcessing } from '@/components/figma/ai-processing';
import { ItineraryOutput, ItineraryData } from '@/components/figma/itinerary-output';

type ViewState = 'HERO' | 'INPUT' | 'PROCESSING' | 'RESULTS';

export default function Home() {
  const [viewState, setViewState] = useState<ViewState>('HERO');
  const [formData, setFormData] = useState<Record<string, any> | null>(null);
  
  // Dummy data for the Itinerary Output Reveal
  const dummyItinerary: ItineraryData = {
    destination: formData?.destination || "Tokyo, Japan",
    travelers: formData?.travelers || "2",
    budget: formData?.budget || "medium",
    totalCost: 2450,
    duration: 5,
    days: [
      {
        day: 1,
        title: "Arrival & Neon Dreams",
        activities: [
          { type: "flight", title: "Flight Arrival", time: "14:00", cost: "$850", description: "JL002 from JFK to HND", image: "https://images.unsplash.com/photo-1436491865332-7a61a109cc05?q=80&w=2674&auto=format&fit=crop", agent: "logistics" },
          { type: "hotel", title: "Check-in at Shinjuku Granbell", time: "16:00", cost: "$200/night", description: "Premium City View Room", image: "https://images.unsplash.com/photo-1542314831-c6a4d2706864?q=80&w=3122&auto=format&fit=crop", agent: "logistics" },
          { type: "experience", title: "Omoide Yokocho Dinner", time: "19:00", cost: "$45", description: "Yakitori and local vibes in the famous memory lane.", image: "https://images.unsplash.com/photo-1551641506-ee5bf4cb45f1?q=80&w=2684&auto=format&fit=crop", agent: "experience" },
        ]
      },
      {
        day: 2,
        title: "Culture & Cybernetics",
        activities: [
          { type: "experience", title: "Meiji Shrine Morning Walk", time: "09:00", cost: "Free", description: "Serene walk through the sacred forest.", image: "https://images.unsplash.com/photo-1526481280693-3bfa7568e0f3?q=80&w=2671&auto=format&fit=crop", agent: "experience" },
          { type: "experience", title: "Akihabara Tech Exploration", time: "14:00", cost: "$120", description: "Arcades, maid cafes, and electronics.", image: "https://images.unsplash.com/photo-1542051812871-7575116fc53e?q=80&w=2670&auto=format&fit=crop", agent: "experience" },
        ]
      }
    ]
  };

  return (
    <div className="flex flex-col min-h-screen bg-[#050505] text-white">
      {viewState === 'HERO' && (
        <HeroSection onStartPlanning={() => setViewState('INPUT')} />
      )}
      
      {viewState === 'INPUT' && (
        <InputFormSection onSubmit={(data: any) => {
          setFormData(data);
          setViewState('PROCESSING');
        }} />
      )}

      {viewState === 'PROCESSING' && (
        <AIProcessing onComplete={() => setViewState('RESULTS')} />
      )}

      {viewState === 'RESULTS' && (
        <ItineraryOutput 
          data={dummyItinerary} 
        />
      )}
    </div>
  );
}
