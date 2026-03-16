"use client";

import AuthForm from '@/components/AuthForm';

export default function RegisterPage() {
  return (
    <div className="flex items-center justify-center min-h-[calc(100vh-4rem)] bg-slate-50 px-4">
      <AuthForm mode="register" />
    </div>
  );
}
