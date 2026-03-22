"use client";

import { useState } from 'react';
import ProtectedRoute from '@/components/ProtectedRoute';
import { InputFormSection } from '@/components/figma/input-form-section';
import { AIProcessing } from '@/components/figma/ai-processing';
import { ItineraryOutput, FinalTripPlan } from '@/components/figma/itinerary-output';

type ViewState = 'INPUT' | 'PROCESSING' | 'RESULTS';
type TripFormData = {
  budget: string;
  lifestyle: string;
  vacationType: string;
  origin: string;
  destination: string;
  startDate: string;
  endDate: string;
  travelers: string;
};

export default function PlanTripPage() {
  const [viewState, setViewState] = useState<ViewState>('INPUT');
  const [formData, setFormData] = useState<TripFormData | null>(null);
  const [itineraryData, setItineraryData] = useState<FinalTripPlan | null>(null);
  const [error, setError] = useState<string | null>(null);

  const ITINERARY_API_URL =
    process.env.NEXT_PUBLIC_ITINERARY_API_URL ||
    "http://127.0.0.1:8000/api/generate-itinerary";

  const handleGenerateItinerary = async (data: TripFormData) => {
    setFormData(data);
    setItineraryData(null);
    setError(null);
    setViewState('PROCESSING');

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 100000); // 100s timeout

    try {
      const payload = {
        budget: data.budget,
        lifestyle: data.lifestyle,
        vacationType: data.vacationType,
        origin: data.origin,
        destination: data.destination,
        start_date: data.startDate,
        end_date: data.endDate,
        travelers: parseInt(data.travelers, 10) || 1,
      };
      console.log("[DEBUG] Sending payload:", JSON.stringify(payload, null, 2));

      const response = await fetch(ITINERARY_API_URL, {
        method: "POST",
        signal: controller.signal,
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        let errorMsg = `Backend error: ${response.status}`;
        
        if (errorData) {
          if (typeof errorData === 'string') {
            errorMsg = errorData;
          } else if (errorData.detail) {
            errorMsg = typeof errorData.detail === 'string' 
              ? errorData.detail 
              : JSON.stringify(errorData.detail);
          } else {
            errorMsg = JSON.stringify(errorData);
          }
        }
        throw new Error(errorMsg);
      }

      const result = (await response.json()) as FinalTripPlan;
      setItineraryData(result);
      setViewState('RESULTS');
    } catch (err: unknown) {
      console.error("Failed to generate itinerary:", err);
      setError(err instanceof Error ? err.message : "Something went wrong while crafting your journey. Please try again.");
      setViewState('INPUT');
    }
  };

  return (
    <ProtectedRoute>
      <div className="flex flex-col min-h-screen text-white">
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

        {viewState === 'RESULTS' && itineraryData && (
          <ItineraryOutput 
            data={itineraryData}
            formData={formData}
            onReset={() => {
              setViewState('INPUT');
              setItineraryData(null);
              setError(null);
            }}
          />
        )}
      </div>
    </ProtectedRoute>
  );
}
