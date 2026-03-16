import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { AuthProvider } from '@/context/AuthContext';
import Navbar from '@/components/Navbar';
import SmoothScroller from '@/components/animations/SmoothScroller';

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
    <html lang="en" className="h-full bg-[#0a0a0a]">
      <body className={`${inter.className} h-full text-white selection:bg-cyan-500/30 selection:text-cyan-200`}>
        <AuthProvider>
          <SmoothScroller>
            <div className="min-h-full flex flex-col">
              <Navbar />
              <main className="flex-1">
                {children}
              </main>
            </div>
          </SmoothScroller>
        </AuthProvider>
      </body>
    </html>
  );
}
