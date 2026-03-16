"use client";

import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';
import { Compass, LogOut, User as UserIcon } from 'lucide-react';
import { usePathname } from 'next/navigation';

export default function Navbar() {
  const { user, isAuthenticated, logout } = useAuth();
  const pathname = usePathname();

  if (pathname === '/') return null;

  return (
    <nav className="bg-white border-b border-gray-100 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link href="/" className="flex items-center gap-2 group">
              <Compass className="h-8 w-8 text-indigo-600 group-hover:rotate-12 transition-transform duration-300" />
              <span className="font-bold text-xl text-gray-900 tracking-tight">VibeTrips</span>
            </Link>
          </div>

          <div className="flex items-center gap-4">
            {isAuthenticated ? (
              <>
                <Link href="/plan" className="text-gray-600 hover:text-indigo-600 font-medium text-sm transition-colors">
                  Plan a Trip
                </Link>
                <Link href="/dashboard" className="text-gray-600 hover:text-indigo-600 font-medium text-sm transition-colors">
                  My Trips
                </Link>
                <div className="h-6 w-px bg-gray-200 mx-2"></div>
                <div className="flex items-center gap-2 text-sm text-gray-700">
                  <UserIcon className="h-4 w-4" />
                  <span className="hidden sm:inline-block font-medium">{user?.displayName}</span>
                </div>
                <button
                  onClick={logout}
                  className="p-2 text-gray-400 hover:text-red-600 transition-colors ml-2"
                  title="Logout"
                >
                  <LogOut className="h-5 w-5" />
                </button>
              </>
            ) : (
              <>
                <Link href="/login" className="text-gray-600 hover:text-indigo-600 font-medium text-sm transition-colors">
                  Log in
                </Link>
                <Link
                  href="/register"
                  className="bg-indigo-600 text-white px-4 py-2 rounded-full font-medium text-sm hover:bg-indigo-700 transition-colors shadow-sm"
                >
                  Sign up
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
