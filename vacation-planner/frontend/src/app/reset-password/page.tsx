"use client";

import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";
import { motion } from "motion/react";
import { AlertCircle, CheckCircle2, Loader2, Lock, Save } from "lucide-react";
import { supabase } from "@/lib/supabase";

export default function ResetPasswordPage() {
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);
  const [checkingSession, setCheckingSession] = useState(true);
  const [hasRecoverySession, setHasRecoverySession] = useState(false);

  useEffect(() => {
    let isMounted = true;

    const readUrlError = () => {
      const url = new URL(window.location.href);
      const hashParams = new URLSearchParams(window.location.hash.replace(/^#/, ""));
      const message =
        url.searchParams.get("error_description") ||
        hashParams.get("error_description") ||
        url.searchParams.get("error") ||
        hashParams.get("error");

      if (message) {
        setError(message.replace(/\+/g, " "));
      }

      return {
        code: url.searchParams.get("code"),
        hasRecoveryToken: hashParams.get("type") === "recovery" && !!hashParams.get("access_token"),
      };
    };

    const prepareRecoverySession = async () => {
      if (!supabase) {
        setError(
          "Supabase is not configured. Add NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY to frontend/.env.local."
        );
        setCheckingSession(false);
        return;
      }

      const { code, hasRecoveryToken } = readUrlError();

      if (code) {
        const { error: exchangeError } = await supabase.auth.exchangeCodeForSession(code);
        if (exchangeError) {
          setError(exchangeError.message);
        }
      }

      const {
        data: { session },
      } = await supabase.auth.getSession();

      if (!isMounted) return;
      setHasRecoverySession(!!session || hasRecoveryToken);
      setCheckingSession(false);
    };

    const subscription = supabase?.auth.onAuthStateChange((event, session) => {
      if (event === "PASSWORD_RECOVERY" || session) {
        setHasRecoverySession(true);
      }
    }).data.subscription;

    prepareRecoverySession();

    return () => {
      isMounted = false;
      subscription?.unsubscribe();
    };
  }, []);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError("");
    setSuccess(false);

    if (password.length < 6) {
      setError("Password must be at least 6 characters.");
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);

    try {
      if (!supabase) {
        throw new Error(
          "Supabase is not configured. Add NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY to frontend/.env.local."
        );
      }

      const { error: updateError } = await supabase.auth.updateUser({ password });
      if (updateError) throw updateError;

      await supabase.auth.signOut();
      setPassword("");
      setConfirmPassword("");
      setSuccess(true);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Could not update your password.");
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
        <div className="text-center mb-8">
          <h1
            className="text-4xl font-bold bg-gradient-to-r from-[#FF6B5A] to-[#FF9F43] bg-clip-text text-transparent mb-3"
            style={{ fontFamily: "var(--font-playfair), Georgia, serif" }}
          >
            New Password
          </h1>
          <p className="text-[#64748B]" style={{ fontFamily: "'Inter', sans-serif" }}>
            Choose a new password for your VibeTrips account.
          </p>
        </div>

        {checkingSession && (
          <div className="flex items-center justify-center gap-3 p-4 mb-6 text-sm text-[#64748B]">
            <Loader2 className="h-5 w-5 animate-spin text-[#FF6B5A]" />
            Checking reset link...
          </div>
        )}

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

        {success && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex items-center gap-3 p-4 mb-6 text-sm text-emerald-600 bg-emerald-500/10 border border-emerald-500/20 rounded-2xl"
          >
            <CheckCircle2 className="h-5 w-5 shrink-0" />
            <p>Your password was updated. You can log in with it now.</p>
          </motion.div>
        )}

        {!checkingSession && !hasRecoverySession && !success && (
          <div className="mb-6 text-sm text-[#64748B] bg-[#FFF6E8] border border-[rgba(255,107,90,0.18)] rounded-2xl p-4">
            This reset link is missing or expired. Request a new one from the forgot password page.
          </div>
        )}

        {!success && (
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <label className="block text-sm font-medium text-[#10223A]/70">New Password</label>
              <div className="relative">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  type="password"
                  required
                  minLength={6}
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  className="w-full pl-12 pr-4 py-4 border border-[rgba(255,107,90,0.20)] rounded-2xl bg-[#FFFBF3] text-[#10223A] placeholder:text-[#64748B]/50 focus:outline-none focus:border-[#FF6B5A]/60 focus:shadow-[0_0_16px_rgba(255,107,90,0.14)] transition-all"
                  placeholder="Enter a new password"
                />
              </div>
            </div>

            <div className="space-y-2">
              <label className="block text-sm font-medium text-[#10223A]/70">Confirm Password</label>
              <div className="relative">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  type="password"
                  required
                  minLength={6}
                  value={confirmPassword}
                  onChange={(event) => setConfirmPassword(event.target.value)}
                  className="w-full pl-12 pr-4 py-4 border border-[rgba(255,107,90,0.20)] rounded-2xl bg-[#FFFBF3] text-[#10223A] placeholder:text-[#64748B]/50 focus:outline-none focus:border-[#FF6B5A]/60 focus:shadow-[0_0_16px_rgba(255,107,90,0.14)] transition-all"
                  placeholder="Confirm your new password"
                />
              </div>
            </div>

            <motion.button
              whileHover={{ scale: 1.01 }}
              whileTap={{ scale: 0.98 }}
              type="submit"
              disabled={loading || checkingSession || !hasRecoverySession || !supabase}
              className="w-full py-4 bg-gradient-to-r from-[#FF6B5A] to-[#FF9F43] text-white rounded-2xl font-bold flex items-center justify-center gap-2 shadow-[0_4px_24px_rgba(255,107,90,0.35)] disabled:opacity-50 transition-all cursor-pointer"
            >
              {loading ? "Updating..." : "Update Password"}
              {!loading && <Save className="h-5 w-5" />}
            </motion.button>
          </form>
        )}

        <div className="mt-8 text-center text-[#64748B]">
          <Link href="/login" className="font-medium text-[#FF6B5A] hover:text-[#FF6B5A]/80 transition-colors">
            Return to login
          </Link>
        </div>
      </motion.div>
    </div>
  );
}
