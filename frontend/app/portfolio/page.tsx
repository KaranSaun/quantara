'use client';

import Sidebar from '@/components/ui/Sidebar';
import TickerStrip from '@/components/ui/TickerStrip';
import { useEffect, useState } from 'react';
import { api } from '@/lib/api';

const FALLBACK_PNL = [
  { day: 'Mon', pnl: 3200 }, { day: 'Tue', pnl: -1200 }, { day: 'Wed', pnl: 4500 },
  { day: 'Thu', pnl: 1800 }, { day: 'Fri', pnl: -800 }
];

const FALLBACK_TRADES = [
  { date: '15 Jan', instrument: 'BN 56000 PE', dir: 'SELL', entry: 155, exit: 95, qty: 15, pnl: -900, system: true },
  { date: '14 Jan', instrument: 'BN 55800 CE', dir: 'BUY', entry: 120, exit: 210, qty: 15, pnl: 1350, system: true },
];

export default function PortfolioPage() {
  const [positions, setPositions] = useState<any[]>([]);
  const [metrics, setMetrics] = useState<any>(null);
  const [pnlData, setPnlData] = useState(FALLBACK_PNL);
  const [trades, setTrades] = useState(FALLBACK_TRADES);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [posData, metricsData] = await Promise.all([
          api.getPositions(),
          api.getMetrics()
        ]);
        setPositions(posData || []);
        setMetrics(metricsData);
      } catch (err) {
        console.error('Failed to fetch portfolio:', err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  const maxPnl = Math.max(...pnlData.map(d => Math.abs(d.pnl)), 1000);

  return (
    <>
      <Sidebar />
      <main className="main-container">
        <TickerStrip />
        <div className="content-viewport">
          <div className="page-content">
            <h1 style={{ fontSize: 36, marginBottom: 8 }}>Portfolio & <span className="text-blue">Performance</span></h1>
            <p className="muted" style={{ fontSize: 12, marginBottom: 32, letterSpacing: '0.1em' }}>LIVE BROKER SYNCED • MULTI-ACCOUNT AGGREGATION</p>

            {/* Metrics Grid */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, marginBottom: 32 }}>
              {[
                { label: 'Total P&L', value: `₹${metrics?.total_pnl?.toLocaleString() || '0'}`, color: (metrics?.total_pnl || 0) >= 0 ? 'var(--green)' : 'var(--red)', sub: 'This month' },
                { label: 'Win Rate', value: `${metrics?.win_rate || '0'}%`, color: 'var(--green)', sub: `${metrics?.winners || '0'}/${metrics?.total_trades || '0'} trades` },
                { label: 'Profit Factor', value: metrics?.profit_factor || '0', color: 'var(--green)', sub: 'Gross P / Gross L' },
                { label: 'System Follow', value: `${metrics?.followed_system_pct || '0'}%`, color: 'var(--amber)', sub: 'Discipline rate' },
              ].map((m, i) => (
                <div key={i} className="apex-card">
                  <div style={{ fontSize: 10, color: 'var(--muted)', letterSpacing: '0.1em', marginBottom: 12 }}>{m.label.toUpperCase()}</div>
                  <div className="mono" style={{ fontSize: 28, fontWeight: 700, color: m.color }}>{m.value}</div>
                  <div className="mono" style={{ fontSize: 10, color: 'var(--muted)', marginTop: 8 }}>{m.sub}</div>
                </div>
              ))}
            </div>

            {/* P&L Bar Chart */}
            <div className="apex-card" style={{ marginBottom: 32 }}>
              <div style={{ fontSize: 14, fontWeight: 700, marginBottom: 32 }}>Equity Curve — Daily Snapshots</div>
              <div style={{ display: 'flex', alignItems: 'flex-end', gap: 12, height: 200, paddingBottom: 32, position: 'relative' }}>
                <div style={{ position: 'absolute', bottom: 32, left: 0, right: 0, height: 1, background: 'var(--border)', opacity: 0.5 }} />
                {pnlData.map((d, i) => {
                  const height = (Math.abs(d.pnl) / maxPnl) * 140;
                  const isPos = d.pnl >= 0;
                  return (
                    <div key={i} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'flex-end', height: '100%', position: 'relative' }}>
                      <div className="mono" style={{
                        fontSize: 10, color: isPos ? 'var(--green)' : 'var(--red)',
                        marginBottom: 6, position: 'absolute', bottom: isPos ? height + 36 : 24 - height - 16
                      }}>
                        {isPos ? '+' : ''}{(d.pnl / 1000).toFixed(1)}K
                      </div>
                      <div style={{
                        width: '60%', height, borderRadius: 2,
                        background: isPos ? 'var(--green)' : 'var(--red)',
                        opacity: 0.8,
                        position: 'absolute', bottom: isPos ? 32 : 32 - height,
                        transition: 'all 0.4s ease',
                      }} />
                      <div className="mono" style={{ fontSize: 10, color: 'var(--muted)', position: 'absolute', bottom: 8 }}>{d.day}</div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Trade Table */}
            <div className="apex-card">
              <div style={{ fontSize: 14, fontWeight: 700, marginBottom: 20 }}>Trade Execution Log</div>
              <div className="apex-table-wrapper"><table className="apex-table">
                <thead>
                  <tr>
                    <th>Date</th><th>Instrument</th><th>Direction</th><th>Entry</th><th>Exit</th><th>P&L</th><th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {trades.map((t, i) => (
                    <tr key={i}>
                      <td>{t.date}</td>
                      <td style={{ color: 'var(--text)', fontWeight: 700 }}>{t.instrument}</td>
                      <td><span className={`bias-chip ${t.dir === 'BUY' ? 'bullish' : 'bearish'}`}>{t.dir}</span></td>
                      <td>₹{t.entry}</td>
                      <td>₹{t.exit}</td>
                      <td className="mono" style={{ color: t.pnl >= 0 ? 'var(--green)' : 'var(--red)', fontWeight: 700 }}>
                        {t.pnl >= 0 ? '+' : ''}₹{t.pnl.toLocaleString()}
                      </td>
                      <td>{t.system ? '◎ SYSTEM' : '× MANUAL'}</td>
                    </tr>
                  ))}
                </tbody>
              </table></div>
            </div>
          </div>
        </div>
      </main>
    </>
  );
}
