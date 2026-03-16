import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { AuthProvider } from '@/context/AuthContext';
import Navbar from '@/components/Navbar';
import { ThemeProvider } from '@/components/ThemeProvider';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'VibeTrips - AI Vacation Planner',
  description: 'AI-Powered Multi-Agent Vacation Planner',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.className} min-h-screen text-gray-900 dark:text-white selection:bg-cyan-500/30 selection:text-cyan-200 relative bg-[#f8f9fa] dark:bg-[#050505] transition-colors duration-300`}>
        {/* Global Cinematic Background & Orbs */}
        <div className="fixed inset-0 pointer-events-none z-[-1] bg-[#f8f9fa] dark:bg-[#050505] transition-colors duration-300">
          <div className="absolute top-20 right-20 h-96 w-96 rounded-full bg-[#00F0FF]/10 dark:bg-[#00F0FF]/20 blur-[120px]" />
          <div className="absolute bottom-20 left-20 h-96 w-96 rounded-full bg-[#8A2BE2]/10 dark:bg-[#8A2BE2]/20 blur-[120px]" />
        </div>
        
        <ThemeProvider>
          <AuthProvider>
            <div className="min-h-screen flex flex-col relative z-0">
              <Navbar />
              <main className="flex-1">
                {children}
              </main>
            </div>
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
