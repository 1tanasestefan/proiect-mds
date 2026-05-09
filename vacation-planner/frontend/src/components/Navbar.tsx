"use client";

import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';
import { Sparkles, User as UserIcon, Map, LayoutDashboard, LogIn, LogOut } from 'lucide-react';
import { usePathname } from 'next/navigation';
import { motion } from 'motion/react';
import { ThemeToggle } from '@/components/ThemeToggle';

const MARKETING_LINKS = [
  { label: 'Features',     href: '#features' },
  { label: 'Destinations', href: '#destinations' },
  { label: 'How It Works', href: '#how-it-works' },
  { label: 'Pricing',      href: '#pricing' },
];

const NAV_ICONS: Record<string, React.ElementType> = {
  '/plan': Map,
  '/dashboard': LayoutDashboard,
  '/discover': Sparkles,
  '/login': LogIn,
};

export default function Navbar() {
  const { user, isAuthenticated, logout } = useAuth();
  const pathname = usePathname();
  const isHomepage = pathname === '/';

  const links = isAuthenticated
    ? [
        { href: '/plan', label: 'Plan a Trip' },
        { href: '/discover', label: 'Discover' },
        { href: '/dashboard', label: 'My Trips' },
      ]
    : [
        { href: '/plan', label: 'Plan a Trip' },
        { href: '/discover', label: 'Discover' },
        { href: '/dashboard', label: 'My Trips' },
        { href: '/login', label: 'Login' },
      ];

  // ── Marketing nav (homepage, unauthenticated) ──────────────────────────────
  if (isHomepage && !isAuthenticated) {
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
        <div className="backdrop-blur-xl bg-[rgba(255,251,243,0.88)] border border-[rgba(255,107,90,0.18)] rounded-[24px] px-6 py-3 shadow-[0_8px_32px_rgba(255,107,90,0.10)]">
          <div className="flex items-center justify-between">

            {/* Logo */}
            <Link href="/" className="flex items-center gap-2 group">
              <motion.div whileHover={{ rotate: 20 }} transition={{ type: "spring", stiffness: 300 }}>
                <Sparkles className="h-5 w-5 text-[#FF6B5A] group-hover:text-[#FF9F43] transition-colors duration-500" />
              </motion.div>
              <span
                className="text-xl font-bold tracking-tight text-[#10223A]"
                style={{ fontFamily: "'Archivo Black', sans-serif" }}
              >
                VibeTrips
              </span>
            </Link>

            {/* Center: Anchor links (desktop) */}
            <div className="hidden md:flex items-center gap-1">
              {MARKETING_LINKS.map((link) => (
                <a
                  key={link.href}
                  href={link.href}
                  className="px-4 py-2 rounded-[14px] text-sm font-medium text-[#10223A]/60 hover:text-[#FF6B5A] hover:bg-[#FF6B5A]/8 transition-all duration-200"
                  style={{ fontFamily: "'Inter', sans-serif" }}
                >
                  {link.label}
                </a>
              ))}
            </div>

            {/* Right: Auth CTAs */}
            <div className="flex items-center gap-3">
              <ThemeToggle />
              <Link
                href="/login"
                className="hidden sm:flex items-center px-5 py-2 rounded-full text-sm font-medium text-[#10223A]/60 hover:text-[#FF6B5A] border border-[rgba(255,107,90,0.22)] hover:border-[#FF6B5A]/50 hover:bg-[#FF6B5A]/6 transition-all duration-200"
                style={{ fontFamily: "'Inter', sans-serif" }}
              >
                Sign In
              </Link>
              <motion.div whileHover={{ scale: 1.04 }} whileTap={{ scale: 0.96 }}>
                <Link
                  href="/plan"
                  className="flex items-center gap-2 px-5 py-2 rounded-full bg-gradient-to-r from-[#FF6B5A] to-[#FF9F43] text-white text-sm font-semibold shadow-[0_4px_18px_rgba(255,107,90,0.35)] hover:shadow-[0_6px_24px_rgba(255,107,90,0.50)] transition-shadow duration-300"
                  style={{ fontFamily: "'Inter', sans-serif" }}
                >
                  Start Planning
                  <Sparkles className="h-3.5 w-3.5" />
                </Link>
              </motion.div>
            </div>
          </div>
        </div>
      </nav>
    );
  }

  // ── App nav (all other pages / authenticated) ─────────────────────────────


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
      <div className="backdrop-blur-xl bg-[rgba(255,251,243,0.88)] border border-[rgba(255,107,90,0.18)] rounded-[24px] px-6 py-3 shadow-[0_8px_32px_rgba(255,107,90,0.08)]">
        <div className="flex items-center justify-between">

          {/* Logo */}
          <Link href="/" className="flex items-center gap-2 group">
            <motion.div whileHover={{ rotate: 20 }} transition={{ type: "spring", stiffness: 300 }}>
              <Sparkles className="h-6 w-6 text-[#FF6B5A] group-hover:text-[#FF9F43] transition-colors duration-500" />
            </motion.div>
            <span
              className="text-2xl font-bold tracking-tight text-[#10223A]"
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
                      className="flex items-center gap-2 px-5 py-2 rounded-full bg-gradient-to-r from-[#FF6B5A] to-[#FF9F43] text-white text-sm font-semibold shadow-[0_4px_18px_rgba(255,107,90,0.35)] hover:shadow-[0_6px_24px_rgba(255,107,90,0.50)] transition-shadow duration-300"
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
                        ? 'text-[#FF6B5A]'
                        : 'text-[#10223A]/60 hover:text-[#10223A]'
                    }`}
                  >
                    {/* Animated background */}
                    {isActive ? (
                      <motion.div
                        layoutId="nav-pill"
                        className="absolute inset-0 rounded-[14px] bg-[#FF6B5A]/10 border border-[#FF6B5A]/20"
                        transition={{ type: "spring", stiffness: 400, damping: 35 }}
                      />
                    ) : (
                      <span className="absolute inset-0 rounded-[14px] bg-[#FF6B5A]/0 group-hover:bg-[#FF6B5A]/8 transition-colors duration-200" />
                    )}

                    {/* Icon with gradient on active */}
                    <span className={`relative z-10 transition-colors duration-300 ${isActive ? 'text-[#FF6B5A]' : 'text-current'}`}>
                      {Icon && <Icon className="h-4 w-4" />}
                    </span>

                    <span className="relative z-10">{link.label}</span>

                    {/* Active dot indicator */}
                    {isActive && (
                      <motion.span
                        layoutId="nav-dot"
                        className="relative z-10 ml-0.5 h-1.5 w-1.5 rounded-full bg-[#FF6B5A] shadow-[0_0_6px_#FF6B5A]"
                        transition={{ type: "spring", stiffness: 400, damping: 35 }}
                      />
                    )}
                  </motion.div>
                </Link>
              );
            })}

            {/* Divider */}
            <div className="w-px h-5 bg-[#FF6B5A]/20 mx-1" />

            {/* Theme Toggle */}
            <ThemeToggle />

            {/* User profile + Logout */}
            {isAuthenticated && (
              <div className="flex items-center gap-2 pl-1">
                {/* Avatar chip */}
                <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-[#FFE6D6] border border-[rgba(255,107,90,0.22)]">
                  <div className="h-5 w-5 rounded-full bg-gradient-to-br from-[#FF6B5A] to-[#FF9F43] flex items-center justify-center shadow-[0_0_8px_rgba(255,107,90,0.4)]">
                    <UserIcon className="h-3 w-3 text-white" />
                  </div>
                  <span
                    className="hidden sm:block text-sm font-medium text-[#10223A] max-w-[100px] truncate"
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
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium text-[#64748B] hover:text-red-500 hover:bg-red-50 border border-transparent hover:border-red-200 transition-all duration-200"
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
