'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function Home() {
  const router = useRouter();
  useEffect(() => { router.replace('/morning'); }, [router]);
  return (
    <div style={{
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      height: '100vh', background: 'var(--bg)',
    }}>
      <div style={{ textAlign: 'center' }}>
        <h1 style={{
          fontFamily: 'var(--font-head)', fontSize: 48, fontWeight: 800,
          background: 'linear-gradient(135deg, var(--green), var(--blue))',
          WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
        }}>QUANTARA OS</h1>
        <p style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--muted)', marginTop: 12 }}>
          INITIALIZING TRADING SYSTEM...
        </p>
      </div>
    </div>
  );
}
