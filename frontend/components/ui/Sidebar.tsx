'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useEffect, useState } from 'react';

const NAV_ITEMS = [
  { path: '/morning', label: 'BRIEFING', icon: '◉' },
  { path: '/live', label: 'LIVE', icon: '◈' },
  { path: '/options', label: 'OPTIONS', icon: '◆' },
  { path: '/portfolio', label: 'PORTFOLIO', icon: '▣' },
  { path: '/journal', label: 'JOURNAL', icon: '▤' },
  { path: '/finance', label: 'FINANCE', icon: '▥' },
  { path: '/chat', label: 'AI CHAT', icon: '◎' },
  { path: '/settings', label: 'SETTINGS', icon: '⚙' },
];

export default function Sidebar() {
  const pathname = usePathname();
  const [time, setTime] = useState('');
  const [marketOpen, setMarketOpen] = useState(false);

  useEffect(() => {
    const tick = () => {
      const now = new Date();
      setTime(now.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false }));
      const h = now.getHours(), m = now.getMinutes();
      const day = now.getDay();
      setMarketOpen(day >= 1 && day <= 5 && ((h === 9 && m >= 15) || (h > 9 && h < 15) || (h === 15 && m <= 30)));
    };
    tick();
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, []);

  return (
    <aside className="sidebar-container" style={{
      padding: '24px 0',
    }}>
      {/* Logo */}
      <div style={{ padding: '0 24px 32px', borderBottom: '1px solid var(--border)' }}>
        <h1 style={{
          fontFamily: 'var(--font-head)',
          fontSize: 28,
          fontWeight: 900,
          letterSpacing: '-0.04em',
          color: 'var(--text)',
          lineHeight: 1,
        }}>
          QUANTARA <span style={{ color: 'var(--green)' }}>OS</span>
        </h1>
        <div style={{ fontFamily: 'var(--font-mono)', fontSize: 9, color: 'var(--muted)', marginTop: 8, letterSpacing: '0.15em', fontWeight: 700 }}>
          INTELLIGENCE COMMAND
        </div>
      </div>

      {/* Market Status */}
      <div style={{
        margin: '16px 8px',
        padding: '10px 12px',
        background: marketOpen ? 'rgba(0,255,136,0.06)' : 'rgba(255,59,92,0.06)',
        border: `1px solid ${marketOpen ? 'rgba(0,255,136,0.2)' : 'rgba(255,59,92,0.2)'}`,
        borderRadius: 6,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <div style={{
            width: 8, height: 8, borderRadius: '50%',
            background: marketOpen ? 'var(--green)' : 'var(--red)',
            animation: marketOpen ? 'pulse-green 2s infinite' : 'none',
          }} />
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: marketOpen ? 'var(--green)' : 'var(--red)' }}>
            {marketOpen ? 'MARKET LIVE' : 'MARKET CLOSED'}
          </span>
        </div>
        <div style={{ fontFamily: 'var(--font-mono)', fontSize: 18, fontWeight: 700, color: 'var(--text)', marginTop: 6 }}>
          {time}
        </div>
        <div style={{ fontFamily: 'var(--font-mono)', fontSize: 9, color: 'var(--muted)', marginTop: 2 }}>
          IST • NSE
        </div>
      </div>

      {/* Nav */}
      <nav style={{ display: 'flex', flexDirection: 'column', gap: 2, flex: 1, marginTop: 8 }}>
        {NAV_ITEMS.map(item => {
          const active = pathname === item.path;
          return (
            <Link key={item.path} href={item.path} className={`nav-link ${active ? 'active' : ''}`}>
              <span style={{ fontSize: 14, opacity: active ? 1 : 0.5 }}>{item.icon}</span>
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div style={{
        padding: '12px 8px',
        borderTop: '1px solid var(--border)',
        fontFamily: 'var(--font-mono)',
        fontSize: 9,
        color: 'var(--muted)',
        lineHeight: 1.6,
      }}>
        DESIGNED AND DEVELOPED BY<br />
        KARAN SAUN
      </div>
    </aside>
  );
}
