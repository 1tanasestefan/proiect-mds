import type { Metadata } from 'next';
import { Inter, Playfair_Display } from 'next/font/google';
import './globals.css';
import { AuthProvider } from '@/context/AuthContext';
import Navbar from '@/components/Navbar';
import { ThemeProvider } from '@/components/ThemeProvider';
import { Toaster } from '@/components/figma/ui/sonner';

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' });
const playfair = Playfair_Display({ subsets: ['latin'], variable: '--font-playfair', weight: ['400', '500', '600', '700'] });

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
      <body className={`${inter.variable} ${playfair.variable} ${inter.className} min-h-screen text-[#10223A] selection:bg-[#FF6B5A]/30 selection:text-[#FF6B5A] relative bg-[#FFF6E8]`}>
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
              <Toaster richColors position="bottom-right" />
            </div>
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
