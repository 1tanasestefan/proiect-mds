"use client";

import ProtectedRoute from '@/components/ProtectedRoute';

export default function PlanTripPage() {
  return (
    <ProtectedRoute>
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <h1 className="text-3xl font-bold text-gray-900 mb-8 text-center">
          Plan Your Next Trip
        </h1>
        
        <div className="bg-white shadow-xl rounded-2xl p-8 border border-gray-100">
          {/* Form placeholder for now */}
          <p className="text-center text-gray-500">
            Trip Planner form will be implemented here.
          </p>
        </div>
      </div>
    </ProtectedRoute>
  );
}
