"use client";

import Link from "next/link";
import { motion } from "motion/react";
import { Sparkles, Twitter, Instagram, Github, Linkedin } from "lucide-react";

const NAV_COLS = [
  {
    title: "Product",
    links: [
      { label: "Features",     href: "#features" },
      { label: "Destinations", href: "#destinations" },
      { label: "How It Works", href: "#how-it-works" },
      { label: "Pricing",      href: "#pricing" },
      { label: "Changelog",    href: "#" },
    ],
  },
  {
    title: "Company",
    links: [
      { label: "About",    href: "#" },
      { label: "Blog",     href: "#" },
      { label: "Careers",  href: "#" },
      { label: "Press",    href: "#" },
    ],
  },
  {
    title: "Legal",
    links: [
      { label: "Privacy Policy",   href: "#" },
      { label: "Terms of Service", href: "#" },
      { label: "Cookie Policy",    href: "#" },
    ],
  },
];

const SOCIALS = [
  { icon: Twitter,   href: "#", label: "Twitter" },
  { icon: Instagram, href: "#", label: "Instagram" },
  { icon: Linkedin,  href: "#", label: "LinkedIn" },
  { icon: Github,    href: "#", label: "GitHub" },
];

export function MarketingFooter() {
  return (
    <footer className="relative bg-[#010103] border-t border-white/[0.05] px-6 md:px-12 pt-16 pb-10 overflow-hidden">
      {/* Ambient */}
      <div className="absolute bottom-0 left-1/2 -translate-x-1/2 h-[300px] w-[800px] rounded-full bg-[#8A2BE2]/4 blur-[210px] pointer-events-none" />

      <div className="relative z-10 max-w-7xl mx-auto">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-12 mb-14">

          {/* Logo + tagline column */}
          <div className="col-span-2 md:col-span-1">
            <div className="flex items-center gap-2 mb-5">
              <Sparkles className="h-5 w-5 text-[#00F0FF]" />
              <span
                className="text-[1.25rem] font-bold text-white"
                style={{ fontFamily: "'Archivo Black', sans-serif" }}
              >
                VibeTrips
              </span>
            </div>
            <p
              className="text-white/28 text-sm leading-relaxed mb-7 max-w-[210px]"
              style={{ fontFamily: "'Inter', sans-serif" }}
            >
              AI-powered travel planning for modern explorers.
            </p>
            <div className="flex items-center gap-3">
              {SOCIALS.map((s, i) => (
                <motion.a
                  key={i}
                  href={s.href}
                  aria-label={s.label}
                  whileHover={{ scale: 1.15 }}
                  whileTap={{ scale: 0.9 }}
                  className="h-9 w-9 rounded-xl bg-white/[0.04] border border-white/8 flex items-center justify-center text-white/38 hover:text-white/65 hover:border-white/15 transition-colors duration-200"
                >
                  <s.icon className="h-4 w-4" />
                </motion.a>
              ))}
            </div>
          </div>

          {/* Link columns */}
          {NAV_COLS.map((col, ci) => (
            <div key={ci}>
              <p
                className="text-white/55 text-[0.65rem] font-semibold uppercase tracking-widest mb-5"
                style={{ fontFamily: "'Inter', sans-serif" }}
              >
                {col.title}
              </p>
              <ul className="space-y-3">
                {col.links.map((link, li) => (
                  <li key={li}>
                    <Link
                      href={link.href}
                      className="text-white/32 text-sm hover:text-white/62 transition-colors duration-200"
                      style={{ fontFamily: "'Inter', sans-serif" }}
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom row */}
        <div className="pt-8 border-t border-white/[0.05] flex flex-col md:flex-row items-center justify-between gap-4">
          <p
            className="text-white/18 text-sm"
            style={{ fontFamily: "'Inter', sans-serif" }}
          >
            © {new Date().getFullYear()} VibeTrips. All rights reserved.
          </p>
          <p
            className="text-white/14 text-sm"
            style={{ fontFamily: "'Inter', sans-serif" }}
          >
            Made with ♥ for travelers everywhere
          </p>
        </div>
      </div>
    </footer>
  );
}
