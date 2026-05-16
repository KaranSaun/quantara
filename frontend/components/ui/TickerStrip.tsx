'use client';

import { formatPrice, formatPct } from '@/lib/formatters';

interface TickerItem {
  label: string;
  price: number;
  change_pct: number;
}

const DEMO_DATA: TickerItem[] = [
  { label: 'SGX NIFTY', price: 24850.50, change_pct: 0.35 },
  { label: 'DOW FUT', price: 42380.00, change_pct: -0.12 },
  { label: 'S&P FUT', price: 5890.25, change_pct: 0.08 },
  { label: 'CRUDE WTI', price: 78.45, change_pct: 1.2 },
  { label: 'GOLD', price: 2650.30, change_pct: -0.05 },
  { label: 'DXY', price: 104.85, change_pct: 0.22 },
  { label: 'USD/INR', price: 83.42, change_pct: 0.04 },
  { label: 'BTC', price: 98540.0, change_pct: 2.1 },
];

export default function TickerStrip({ data }: { data?: TickerItem[] }) {
  const items = data || DEMO_DATA;
  const doubled = [...items, ...items]; // Duplicate for seamless scroll

  return (
    <div style={{
      width: '100%',
      overflow: 'hidden',
      background: 'var(--surface)',
      borderBottom: '1px solid var(--border)',
      padding: '6px 0',
    }}>
      <div className="ticker-track">
        {doubled.map((item, i) => (
          <div key={i} style={{
            display: 'flex',
            alignItems: 'center',
            gap: 10,
            padding: '0 32px',
            whiteSpace: 'nowrap',
            borderRight: '1px solid rgba(255,255,255,0.05)',
          }}>
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: 9, color: 'var(--muted)', fontWeight: 700, letterSpacing: '0.1em' }}>
              {item.label}
            </span>
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: 13, color: 'var(--text)', fontWeight: 800 }}>
              {formatPrice(item.price)}
            </span>
            <span style={{
              fontFamily: 'var(--font-mono)',
              fontSize: 11,
              color: item.change_pct >= 0 ? 'var(--green)' : 'var(--red)',
              fontWeight: 800,
            }}>
              {item.change_pct >= 0 ? '▲' : '▼'}{Math.abs(item.change_pct).toFixed(2)}%
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
