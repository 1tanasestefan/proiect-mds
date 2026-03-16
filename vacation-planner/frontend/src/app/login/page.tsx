"use client";

import AuthForm from '@/components/AuthForm';

export default function LoginPage() {
  return (
    <div className="flex items-center justify-center min-h-[calc(100vh-4rem)] px-4">
      <AuthForm mode="login" />
    </div>
  );
}
