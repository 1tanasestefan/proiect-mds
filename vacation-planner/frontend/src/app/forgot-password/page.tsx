"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { motion } from "motion/react";
import { AlertCircle, ArrowLeft, CheckCircle2, Mail, Send } from "lucide-react";
import { supabase } from "@/lib/supabase";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const [sent, setSent] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError("");
    setSent(false);
    setLoading(true);

    try {
      if (!supabase) {
        throw new Error(
          "Supabase is not configured. Add NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY to frontend/.env.local."
        );
      }

      const redirectTo =
        typeof window !== "undefined"
          ? `${window.location.origin}/reset-password`
          : undefined;

      const { error: resetError } = await supabase.auth.resetPasswordForEmail(email, {
        redirectTo,
      });

      if (resetError) throw resetError;
      setSent(true);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Could not send the reset email.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-[calc(100vh-4rem)] px-4 py-12">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md p-10 backdrop-blur-xl bg-[#FFFBF3] rounded-[32px] shadow-[0_8px_40px_rgba(255,107,90,0.12)] border border-[rgba(255,107,90,0.18)]"
      >
        <div className="mb-8">
          <Link
            href="/login"
            className="inline-flex items-center gap-2 text-sm font-medium text-[#64748B] hover:text-[#FF6B5A] transition-colors mb-8"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to login
          </Link>
          <h1
            className="text-4xl font-bold bg-gradient-to-r from-[#FF6B5A] to-[#FF9F43] bg-clip-text text-transparent mb-3"
            style={{ fontFamily: "var(--font-playfair), Georgia, serif" }}
          >
            Reset Password
          </h1>
          <p className="text-[#64748B]" style={{ fontFamily: "'Inter', sans-serif" }}>
            Enter your account email and we&apos;ll send you a secure reset link.
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

        {sent && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex items-center gap-3 p-4 mb-6 text-sm text-emerald-600 bg-emerald-500/10 border border-emerald-500/20 rounded-2xl"
          >
            <CheckCircle2 className="h-5 w-5 shrink-0" />
            <p>Check your inbox for the reset link.</p>
          </motion.div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <label className="block text-sm font-medium text-[#10223A]/70">Email Address</label>
            <div className="relative">
              <Mail className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="email"
                required
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                className="w-full pl-12 pr-4 py-4 border border-[rgba(255,107,90,0.20)] rounded-2xl bg-[#FFFBF3] text-[#10223A] placeholder:text-[#64748B]/50 focus:outline-none focus:border-[#FF6B5A]/60 focus:shadow-[0_0_16px_rgba(255,107,90,0.14)] transition-all"
                placeholder="you@example.com"
              />
            </div>
          </div>

          <motion.button
            whileHover={{ scale: 1.01 }}
            whileTap={{ scale: 0.98 }}
            type="submit"
            disabled={loading || !supabase}
            className="w-full py-4 bg-gradient-to-r from-[#FF6B5A] to-[#FF9F43] text-white rounded-2xl font-bold flex items-center justify-center gap-2 shadow-[0_4px_24px_rgba(255,107,90,0.35)] disabled:opacity-50 transition-all cursor-pointer"
          >
            {loading ? "Sending..." : "Send Reset Link"}
            {!loading && <Send className="h-5 w-5" />}
          </motion.button>
        </form>
      </motion.div>
    </div>
  );
}
