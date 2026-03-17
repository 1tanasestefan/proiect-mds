"use client";

import { useState } from 'react';
import { HeroSection } from '@/components/figma/hero-section';
import { InputFormSection } from '@/components/figma/input-form-section';
import { AIProcessing } from '@/components/figma/ai-processing';
import { ItineraryOutput, ItineraryData } from '@/components/figma/itinerary-output';
import { InspirationSection } from '@/components/landing/InspirationSection';
import { DiscoverSection } from '@/components/landing/DiscoverSection';
import { EmotionalSection } from '@/components/landing/EmotionalSection';
import { LandingCTA } from '@/components/landing/LandingCTA';

type ViewState = 'HERO' | 'INPUT' | 'PROCESSING' | 'RESULTS';

export default function Home() {
  const [viewState, setViewState] = useState<ViewState>('HERO');
  const [formData, setFormData] = useState<Record<string, any> | null>(null);
  const [itineraryData, setItineraryData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  
  const handleGenerateItinerary = async (data: any) => {
    setFormData(data);
    setViewState('PROCESSING');
    setError(null);

    try {
      const response = await fetch("http://localhost:8000/api/generate-itinerary", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          ...data,
          travelers: parseInt(data.travelers, 10) || 1
        }),
      });

      if (!response.ok) {
        throw new Error(`Backend error: ${response.statusText}`);
      }

      const result = await response.json();
      setItineraryData(result);
      setViewState('RESULTS');
    } catch (err: any) {
      console.error("Failed to generate itinerary:", err);
      setError(err.message || "Something went wrong while crafting your journey. Please try again.");
      setViewState('INPUT');
    }
  };

  return (
    <div className="flex flex-col min-h-screen text-gray-900 dark:text-white">
      {viewState === 'HERO' && (
        <>
          <HeroSection onStartPlanning={() => setViewState('INPUT')} />
          <InspirationSection />
          <DiscoverSection />
          <EmotionalSection />
          <LandingCTA onStartPlanning={() => setViewState('INPUT')} />
        </>
      )}
      
      {viewState === 'INPUT' && (
        <div className="relative">
          {error && (
            <div className="absolute top-24 left-1/2 -translate-x-1/2 z-50 w-full max-w-xl px-4">
              <div className="backdrop-blur-xl bg-red-500/10 border border-red-500/20 text-red-200 px-6 py-4 rounded-2xl shadow-2xl flex items-center justify-between">
                <span>{error}</span>
                <button onClick={() => setError(null)} className="opacity-50 hover:opacity-100 italic transition-opacity">dismiss</button>
              </div>
            </div>
          )}
          <InputFormSection onSubmit={handleGenerateItinerary} />
        </div>
      )}

      {viewState === 'PROCESSING' && (
        <AIProcessing />
      )}

      {viewState === 'RESULTS' && (
        <ItineraryOutput 
          data={itineraryData} 
          formData={formData}
        />
      )}
    </div>
  );
}
