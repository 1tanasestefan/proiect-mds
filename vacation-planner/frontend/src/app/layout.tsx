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
  icons: {
    icon: '/icon.svg',
    shortcut: '/icon.svg',
    apple: '/icon.svg',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.className} min-h-screen text-[#10223A] selection:bg-[#FF6B5A]/30 selection:text-[#FF6B5A] relative bg-[#FFF6E8]`}>
        {/* Global Warm Background & Orbs */}
        <div className="fixed inset-0 pointer-events-none z-[-1] bg-[#FFF6E8]">
          <div className="absolute top-20 right-20 h-96 w-96 rounded-full bg-[#FF6B5A]/12 blur-[130px]" />
          <div className="absolute bottom-20 left-20 h-96 w-96 rounded-full bg-[#FF9F43]/10 blur-[130px]" />
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 h-[600px] w-[600px] rounded-full bg-[#FFC1A1]/8 blur-[180px]" />
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
