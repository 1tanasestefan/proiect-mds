"use client";

import { ReactLenis } from 'lenis/react';

export default function SmoothScroller({ children }: { children: React.ReactNode }) {
  return (
    <ReactLenis root options={{ lerp: 0.12, duration: 1.2, smoothWheel: true, wheelMultiplier: 1, touchMultiplier: 2 }}>
      {children}
    </ReactLenis>
  );
}
