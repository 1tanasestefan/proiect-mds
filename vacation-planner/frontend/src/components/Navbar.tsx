"use client";

import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';
import { Sparkles, User as UserIcon, Map, LayoutDashboard, LogIn, LogOut } from 'lucide-react';
import { usePathname } from 'next/navigation';
import { motion } from 'framer-motion';
import { ThemeToggle } from '@/components/ThemeToggle';

const NAV_ICONS: Record<string, React.ElementType> = {
  '/plan': Map,
  '/dashboard': LayoutDashboard,
  '/login': LogIn,
};

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
    <nav
      className="fixed top-6 inset-x-0 mx-auto z-50 w-[90%] max-w-7xl reveal-down"
      style={
        {
          "--reveal-delay": "60ms",
          "--reveal-duration": "900ms",
          "--reveal-y": "-22px",
        } as React.CSSProperties
      }
    >
      <div className="backdrop-blur-xl bg-white/80 dark:bg-white/5 border border-gray-200/60 dark:border-white/10 rounded-[24px] px-6 py-3 shadow-[0_8px_32px_rgba(0,0,0,0.10)] dark:shadow-[0_8px_32px_rgba(0,0,0,0.4)]">
        <div className="flex items-center justify-between">

          {/* Logo */}
          <Link href="/" className="flex items-center gap-2 group">
            <motion.div whileHover={{ rotate: 20 }} transition={{ type: "spring", stiffness: 300 }}>
              <Sparkles className="h-6 w-6 text-[#00F0FF] group-hover:text-[#8A2BE2] transition-colors duration-500" />
            </motion.div>
            <span
              className="text-2xl font-bold tracking-tight bg-gradient-to-r from-gray-900 to-gray-600 dark:from-white dark:to-white/60 bg-clip-text text-transparent"
              style={{ fontFamily: "'Archivo Black', sans-serif" }}
            >
              VibeTrips
            </span>
          </Link>


          {/* Links */}
          <div className="flex items-center gap-2">
            {links.map((link) => {
              const isActive = pathname === link.href;
              const Icon = NAV_ICONS[link.href];
              const isLogin = link.href === '/login';

              if (isLogin) {
                // Login gets a distinct CTA pill style
                return (
                  <motion.div key={link.href} whileHover={{ scale: 1.04 }} whileTap={{ scale: 0.96 }}>
                    <Link
                      href={link.href}
                      className="flex items-center gap-2 px-5 py-2 rounded-full bg-gradient-to-r from-[#00F0FF] to-[#8A2BE2] text-white text-sm font-semibold shadow-[0_0_20px_rgba(0,240,255,0.25)] hover:shadow-[0_0_30px_rgba(0,240,255,0.45)] transition-shadow duration-300"
                      style={{ fontFamily: "'Inter', sans-serif" }}
                    >
                      <LogIn className="h-3.5 w-3.5" />
                      {link.label}
                    </Link>
                  </motion.div>
                );
              }

              return (
                <Link
                  key={link.href}
                  href={link.href}
                  className="relative group"
                  style={{ fontFamily: "'Inter', sans-serif" }}
                >
                  <motion.div
                    whileHover={{ scale: 1.03 }}
                    whileTap={{ scale: 0.97 }}
                    className={`relative flex items-center gap-2 px-4 py-2 rounded-[14px] text-sm font-medium transition-all duration-300 overflow-hidden ${
                      isActive
                        ? 'text-gray-900 dark:text-white'
                        : 'text-gray-500 dark:text-white/60 hover:text-gray-900 dark:hover:text-white'
                    }`}
                  >
                    {/* Animated background */}
                    {isActive ? (
                      <motion.div
                        layoutId="nav-pill"
                        className="absolute inset-0 rounded-[14px] bg-gray-100 dark:bg-white/10 border border-gray-200 dark:border-white/15"
                        transition={{ type: "spring", stiffness: 400, damping: 35 }}
                      />
                    ) : (
                      <span className="absolute inset-0 rounded-[14px] bg-gray-100/0 dark:bg-white/0 group-hover:bg-gray-100 dark:group-hover:bg-white/5 transition-colors duration-200" />
                    )}

                    {/* Icon with gradient on active */}
                    <span className={`relative z-10 transition-colors duration-300 ${isActive ? 'text-[#00F0FF]' : 'text-current'}`}>
                      {Icon && <Icon className="h-4 w-4" />}
                    </span>

                    <span className="relative z-10">{link.label}</span>

                    {/* Active dot indicator */}
                    {isActive && (
                      <motion.span
                        layoutId="nav-dot"
                        className="relative z-10 ml-0.5 h-1.5 w-1.5 rounded-full bg-[#00F0FF] shadow-[0_0_6px_#00F0FF]"
                        transition={{ type: "spring", stiffness: 400, damping: 35 }}
                      />
                    )}
                  </motion.div>
                </Link>
              );
            })}

            {/* Divider */}
            <div className="w-px h-5 bg-gray-200 dark:bg-white/10 mx-1" />

            {/* Theme Toggle */}
            <ThemeToggle />

            {/* User profile + Logout */}
            {isAuthenticated && (
              <div className="flex items-center gap-2 pl-1">
                {/* Avatar chip */}
                <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-gray-100 dark:bg-white/10 border border-gray-200 dark:border-white/15">
                  <div className="h-5 w-5 rounded-full bg-gradient-to-br from-[#00F0FF] to-[#8A2BE2] flex items-center justify-center shadow-[0_0_8px_rgba(0,240,255,0.5)]">
                    <UserIcon className="h-3 w-3 text-white" />
                  </div>
                  <span
                    className="hidden sm:block text-sm font-medium text-gray-800 dark:text-white/90 max-w-[100px] truncate"
                    style={{ fontFamily: "'Inter', sans-serif" }}
                  >
                    {user?.user_metadata?.display_name || user?.email?.split('@')[0]}
                  </span>
                </div>

                {/* Logout */}
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={logout}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium text-gray-400 dark:text-white/40 hover:text-red-500 dark:hover:text-red-400 hover:bg-red-50 dark:hover:bg-red-500/10 border border-transparent hover:border-red-200 dark:hover:border-red-500/20 transition-all duration-200"
                  style={{ fontFamily: "'Inter', sans-serif" }}
                >
                  <LogOut className="h-3.5 w-3.5" />
                  <span className="hidden sm:block">Logout</span>
                </motion.button>
              </div>
            )}
          </div>

        </div>
      </div>
    </nav>
  );
}
