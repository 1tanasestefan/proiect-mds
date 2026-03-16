"use client";

import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';
import { Sparkles, User as UserIcon } from 'lucide-react';
import { usePathname } from 'next/navigation';
import { motion } from 'framer-motion';

export default function Navbar() {
  const { user, isAuthenticated, logout } = useAuth();
  const pathname = usePathname();

  const links = isAuthenticated
    ? [
        { href: '/plan', label: 'Plan a Trip' },
        { href: '/dashboard', label: 'My Trips' },
      ]
    : [
        { href: '/plan', label: 'Plan a Trip' },
        { href: '/dashboard', label: 'My Trips' },
        { href: '/login', label: 'Login' },
      ];

  return (
    <motion.nav
      initial={{ y: -100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.8, ease: "easeOut" }}
      className="fixed top-8 inset-x-0 mx-auto z-50 w-[90%] max-w-7xl"
    >
      <div className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-[24px] px-8 py-4 shadow-[0_8px_32px_rgba(0,0,0,0.4)]">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2 group">
            <Sparkles className="h-6 w-6 text-[#00F0FF] group-hover:text-[#8A2BE2] transition-colors duration-500" />
            <span className="text-2xl font-bold text-white tracking-tight" style={{ fontFamily: "'Archivo Black', sans-serif" }}>
              VibeTrips
            </span>
          </Link>

          {/* Links */}
          <div className="flex items-center gap-8">
            {links.map((link) => {
              const isActive = pathname === link.href;
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  className="relative group px-3 py-1"
                  style={{ fontFamily: "'Inter', sans-serif" }}
                >
                  {isActive && (
                    <motion.div
                      layoutId="navbar-active-bg"
                      className="absolute inset-0 bg-white/10 rounded-full"
                      transition={{ type: "spring", stiffness: 300, damping: 30 }}
                    />
                  )}
                  <motion.span
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className={`relative z-10 transition-colors duration-300 font-medium ${
                      isActive ? "text-white" : "text-white/70 group-hover:text-white"
                    }`}
                  >
                    {link.label}
                  </motion.span>
                </Link>
              );
            })}

            {/* Auth Button / User Profile */}
            {isAuthenticated && (
              <div className="flex items-center gap-4 pl-4 border-l border-white/10">
                <div className="flex items-center gap-2 text-sm text-white/90">
                  <div className="bg-gradient-to-r from-[#00F0FF] to-[#8A2BE2] p-1 rounded-full">
                    <UserIcon className="h-4 w-4 text-white" />
                  </div>
                  <span className="hidden sm:inline-block font-medium" style={{ fontFamily: "'Inter', sans-serif" }}>
                    {user?.displayName}
                  </span>
                </div>
                <button
                  onClick={logout}
                  className="text-white/50 hover:text-[#ff4444] text-sm font-medium transition-colors"
                  style={{ fontFamily: "'Inter', sans-serif" }}
                >
                  Logout
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </motion.nav>
  );
}
