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
    } catch (err: any) {
      setError(err.message || 'An error occurred during authentication');
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="w-full max-w-md p-10 backdrop-blur-xl bg-white/80 dark:bg-[#1a1a2e]/80 rounded-[32px] shadow-[0_8px_32px_rgba(0,0,0,0.1)] dark:shadow-[0_8px_32px_rgba(0,0,0,0.4)] border border-gray-200 dark:border-white/10"
    >
      <div className="text-center mb-10">
        <h2 
          className="text-4xl font-bold bg-gradient-to-r from-[#00F0FF] to-[#8A2BE2] bg-clip-text text-transparent mb-3"
          style={{ fontFamily: "'Space Grotesk', sans-serif" }}
        >
          {mode === 'login' ? 'Welcome Back' : 'Create Account'}
        </h2>
        <p className="text-gray-500 dark:text-white/60" style={{ fontFamily: "'Inter', sans-serif" }}>
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
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Display Name</label>
            <div className="relative">
              <UserIcon className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                required
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
                className="w-full pl-12 pr-4 py-4 border border-gray-200 dark:border-white/10 rounded-2xl bg-black/5 dark:bg-white/5 text-gray-900 dark:text-white placeholder:text-gray-400 focus:outline-none focus:border-[#00F0FF]/50 focus:shadow-[0_0_20px_rgba(0,240,255,0.1)] transition-all"
                placeholder="How should we call you?"
              />
            </div>
          </div>
        )}

        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Email Address</label>
          <div className="relative">
            <Mail className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full pl-12 pr-4 py-4 border border-gray-200 dark:border-white/10 rounded-2xl bg-black/5 dark:bg-white/5 text-gray-900 dark:text-white placeholder:text-gray-400 focus:outline-none focus:border-[#00F0FF]/50 focus:shadow-[0_0_20px_rgba(0,240,255,0.1)] transition-all"
              placeholder="you@example.com"
            />
          </div>
        </div>

        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Password</label>
          <div className="relative">
            <Lock className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full pl-12 pr-4 py-4 border border-gray-200 dark:border-white/10 rounded-2xl bg-black/5 dark:bg-white/5 text-gray-900 dark:text-white placeholder:text-gray-400 focus:outline-none focus:border-[#8A2BE2]/50 focus:shadow-[0_0_20px_rgba(138,43,226,0.1)] transition-all"
              placeholder="••••••••"
            />
          </div>
        </div>

        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          type="submit"
          disabled={loading}
          className="w-full py-4 mt-4 bg-gradient-to-r from-[#00F0FF] to-[#8A2BE2] text-white rounded-2xl font-bold flex items-center justify-center gap-2 shadow-[0_0_30px_rgba(0,240,255,0.3)] disabled:opacity-50 transition-all cursor-pointer"
        >
          {loading ? 'Processing...' : (mode === 'login' ? 'Sign In' : 'Create Account')}
          {!loading && <ArrowRight className="h-5 w-5" />}
        </motion.button>
      </form>

      <div className="mt-8 text-center text-gray-600 dark:text-gray-400">
        {mode === 'login' ? (
          <p>
            Don't have an account?{' '}
            <Link href="/register" className="font-medium text-[#00F0FF] hover:text-[#00F0FF]/80 transition-colors">
              Sign up
            </Link>
          </p>
        ) : (
          <p>
            Already have an account?{' '}
            <Link href="/login" className="font-medium text-[#8A2BE2] hover:text-[#8A2BE2]/80 transition-colors">
              Log in
            </Link>
          </p>
        )}
      </div>
    </motion.div>
  );
}
