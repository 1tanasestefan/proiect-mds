"use client";

import ProtectedRoute from '@/components/ProtectedRoute';
import { useAuth } from '@/context/AuthContext';
import Link from 'next/link';

export default function DashboardPage() {
  const { user } = useAuth();

  return (
    <ProtectedRoute>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">
          Welcome back, {user?.displayName}!
        </h1>
        
        <div className="bg-white shadow rounded-lg p-6 flex flex-col items-center justify-center min-h-[400px] border border-gray-100">
          <div className="text-center space-y-4">
            <h2 className="text-xl font-medium text-gray-900">Your next adventure awaits</h2>
            <p className="text-gray-500 max-w-sm mx-auto">
              Our AI agents are ready to plan the perfect itinerary based on your vibe, budget, and lifestyle.
            </p>
            <Link 
              href="/plan" 
              className="inline-block px-6 py-3 mt-4 text-white bg-indigo-600 rounded-full hover:bg-indigo-700 transition"
            >
              Start Planning
            </Link>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}
