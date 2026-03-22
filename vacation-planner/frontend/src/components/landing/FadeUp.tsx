"use client";

import { useEffect, useMemo, useRef, useState, ReactNode } from "react";

interface FadeUpProps {
  children: ReactNode;
  delay?: number;
  duration?: number;
  y?: number;
  className?: string;
}

export function FadeUp({
  children,
  delay = 0,
  duration = 0.9,
  y = 40,
  className = "",
}: FadeUpProps) {
  const ref = useRef<HTMLDivElement>(null);
  const [revealed, setRevealed] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    const obs = new IntersectionObserver(
      (entries) => {
        const entry = entries[0];
        if (entry?.isIntersecting) {
          setRevealed(true);
          obs.disconnect();
        }
      },
      { threshold: 0.15 }
    );

    obs.observe(el);
    return () => obs.disconnect();
  }, []);

  const style = useMemo(
    () =>
      ({
        "--reveal-delay": `${Math.max(0, delay) * 1000}ms`,
        "--reveal-duration": `${Math.max(0.1, duration) * 1000}ms`,
        "--reveal-y": `${y}px`,
      } as React.CSSProperties),
    [delay, duration, y]
  );

  return (
    <div
      ref={ref}
      className={`${className} ${revealed ? "reveal-up" : ""}`}
      style={style}
    >
      {children}
    </div>
  );
}
