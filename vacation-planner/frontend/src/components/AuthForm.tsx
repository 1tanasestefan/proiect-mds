"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { supabase } from '@/lib/supabase';
import { motion } from 'motion/react';
import Link from 'next/link';
import { Mail, Lock, User as UserIcon, AlertCircle, ArrowRight } from 'lucide-react';

interface AuthFormProps {
  mode: 'login' | 'register';
}

export default function AuthForm({ mode }: AuthFormProps) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [displayName, setDisplayName] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (!supabase) {
        throw new Error('Supabase is not configured. Add NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY to frontend/.env.local.');
      }

      if (mode === 'register') {
        const { error: signUpError } = await supabase.auth.signUp({
          email,
          password,
          options: {
            data: {
              display_name: displayName,
            },
          },
        });
        if (signUpError) throw signUpError;
        router.push('/dashboard');
      } else {
        const { error: signInError } = await supabase.auth.signInWithPassword({
          email,
          password,
        });
        if (signInError) throw signInError;
        router.push('/dashboard');
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'An error occurred during authentication');
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="w-full max-w-md p-10 backdrop-blur-xl bg-[#FFFBF3] rounded-[32px] shadow-[0_8px_40px_rgba(255,107,90,0.12)] border border-[rgba(255,107,90,0.18)]"
    >
      <div className="text-center mb-10">
        <h2 
          className="text-4xl font-bold bg-gradient-to-r from-[#FF6B5A] to-[#FF9F43] bg-clip-text text-transparent mb-3"
          style={{ fontFamily: "'Space Grotesk', sans-serif" }}
        >
          {mode === 'login' ? 'Welcome Back' : 'Create Account'}
        </h2>
        <p className="text-[#64748B]" style={{ fontFamily: "'Inter', sans-serif" }}>
          {mode === 'login' ? 'Enter your details to access your trips' : 'Join VibeTrips to save and share itineraries'}
        </p>
      </div>
      
      {error && (
        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="flex items-center gap-3 p-4 mb-6 text-sm text-red-500 bg-red-500/10 border border-red-500/20 rounded-2xl"
        >
          <AlertCircle className="h-5 w-5 shrink-0" />
          <p>{error}</p>
        </motion.div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {mode === 'register' && (
          <div className="space-y-2">
            <label className="block text-sm font-medium text-[#10223A]/70">Display Name</label>
            <div className="relative">
              <UserIcon className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                required
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
                className="w-full pl-12 pr-4 py-4 border border-[rgba(255,107,90,0.20)] rounded-2xl bg-[#FFFBF3] text-[#10223A] placeholder:text-[#64748B]/50 focus:outline-none focus:border-[#FF6B5A]/60 focus:shadow-[0_0_16px_rgba(255,107,90,0.14)] transition-all"
                placeholder="How should we call you?"
              />
            </div>
          </div>
        )}

        <div className="space-y-2">
          <label className="block text-sm font-medium text-[#10223A]/70">Email Address</label>
          <div className="relative">
            <Mail className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full pl-12 pr-4 py-4 border border-[rgba(255,107,90,0.20)] rounded-2xl bg-[#FFFBF3] text-[#10223A] placeholder:text-[#64748B]/50 focus:outline-none focus:border-[#FF6B5A]/60 focus:shadow-[0_0_16px_rgba(255,107,90,0.14)] transition-all"
              placeholder="you@example.com"
            />
          </div>
        </div>

        <div className="space-y-2">
          <label className="block text-sm font-medium text-[#10223A]/70">Password</label>
          <div className="relative">
            <Lock className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full pl-12 pr-4 py-4 border border-[rgba(255,107,90,0.20)] rounded-2xl bg-[#FFFBF3] text-[#10223A] placeholder:text-[#64748B]/50 focus:outline-none focus:border-[#FF6B5A]/60 focus:shadow-[0_0_16px_rgba(255,107,90,0.14)] transition-all"
              placeholder="••••••••"
            />
          </div>
        </div>

        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          type="submit"
          disabled={loading || !supabase}
          className="w-full py-4 mt-4 bg-gradient-to-r from-[#FF6B5A] to-[#FF9F43] text-white rounded-2xl font-bold flex items-center justify-center gap-2 shadow-[0_4px_24px_rgba(255,107,90,0.35)] disabled:opacity-50 transition-all cursor-pointer"
        >
          {loading ? 'Processing...' : (mode === 'login' ? 'Sign In' : 'Create Account')}
          {!loading && <ArrowRight className="h-5 w-5" />}
        </motion.button>
      </form>

      <div className="mt-8 text-center text-[#64748B]">
        {mode === 'login' ? (
          <p>
            Don&apos;t have an account?{' '}
            <Link href="/register" className="font-medium text-[#FF6B5A] hover:text-[#FF6B5A]/80 transition-colors">
              Sign up
            </Link>
          </p>
        ) : (
          <p>
            Already have an account?{' '}
            <Link href="/login" className="font-medium text-[#FF9F43] hover:text-[#FF9F43]/80 transition-colors">
              Log in
            </Link>
          </p>
        )}
      </div>
    </motion.div>
  );
}
