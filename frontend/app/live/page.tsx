'use client';

import Sidebar from '@/components/ui/Sidebar';
import TickerStrip from '@/components/ui/TickerStrip';
import { useState, useCallback } from 'react';

const DEMO_CHAIN = Array.from({ length: 15 }, (_, i) => {
  const strike = 55000 + i * 100;
  const atm = 55700;
  const dist = Math.abs(strike - atm);
  return {
    strike,
    ce_oi: Math.round(Math.random() * 80000 + 10000),
    ce_chg: Math.round((Math.random() - 0.4) * 15000),
    ce_iv: +(18 + Math.random() * 8).toFixed(1),
    ce_ltp: +(Math.max(5, (atm - strike) + Math.random() * 80)).toFixed(1),
    pe_oi: Math.round(Math.random() * 80000 + 10000),
    pe_chg: Math.round((Math.random() - 0.4) * 15000),
    pe_iv: +(18 + Math.random() * 8).toFixed(1),
    pe_ltp: +(Math.max(5, (strike - atm) + Math.random() * 80)).toFixed(1),
    isATM: Math.abs(strike - atm) < 100,
  };
});

function PCRGauge({ pcr }: { pcr: number }) {
  const angle = Math.min(Math.max((pcr / 2.0) * 180, 0), 180);
  const color = pcr > 1.3 ? 'var(--green)' : pcr < 0.7 ? 'var(--red)' : 'var(--amber)';
  const label = pcr > 1.3 ? 'BULLISH' : pcr < 0.7 ? 'BEARISH' : 'NEUTRAL';

  return (
    <div className="apex-card" style={{ padding: 20, textAlign: 'center' }}>
      <div style={{ fontFamily: 'var(--font-head)', fontSize: 10, color: 'var(--muted)', letterSpacing: '0.1em', marginBottom: 12 }}>PCR GAUGE</div>
      <svg width="160" height="90" viewBox="0 0 160 90">
        <path d="M 10 80 A 70 70 0 0 1 150 80" fill="none" stroke="var(--border)" strokeWidth="8" strokeLinecap="round" />
        <path d="M 10 80 A 70 70 0 0 1 57 18" fill="none" stroke="var(--red)" strokeWidth="3" opacity="0.3" strokeLinecap="round" />
        <path d="M 57 18 A 70 70 0 0 1 103 18" fill="none" stroke="var(--amber)" strokeWidth="3" opacity="0.3" strokeLinecap="round" />
        <path d="M 103 18 A 70 70 0 0 1 150 80" fill="none" stroke="var(--green)" strokeWidth="3" opacity="0.3" strokeLinecap="round" />
        <line
          x1="80" y1="80"
          x2={80 + 55 * Math.cos(Math.PI - (angle * Math.PI / 180))}
          y2={80 - 55 * Math.sin(Math.PI - (angle * Math.PI / 180))}
          stroke={color} strokeWidth="2.5" strokeLinecap="round"
          style={{ transition: 'all 0.8s ease' }}
        />
        <circle cx="80" cy="80" r="4" fill={color} />
      </svg>
      <div style={{ fontFamily: 'var(--font-mono)', fontSize: 28, fontWeight: 700, color, marginTop: 4 }}>{pcr.toFixed(2)}</div>
      <div style={{ fontFamily: 'var(--font-head)', fontSize: 11, color, fontWeight: 600, letterSpacing: '0.05em' }}>{label}</div>
    </div>
  );
}

function VIXMeter({ vix }: { vix: number }) {
  const pct = Math.min(vix / 40 * 100, 100);
  const color = vix > 25 ? 'var(--red)' : vix > 20 ? 'var(--amber)' : 'var(--green)';
  const zone = vix > 25 ? 'HIGH' : vix > 20 ? 'ELEVATED' : vix > 14 ? 'NORMAL' : 'LOW';

  return (
    <div className="apex-card" style={{ padding: 20, textAlign: 'center' }}>
      <div style={{ fontFamily: 'var(--font-head)', fontSize: 10, color: 'var(--muted)', letterSpacing: '0.1em', marginBottom: 12 }}>INDIA VIX</div>
      <div style={{ fontFamily: 'var(--font-mono)', fontSize: 36, fontWeight: 700, color }}>{vix.toFixed(1)}</div>
      <div style={{ width: '100%', height: 6, background: 'var(--surface2)', borderRadius: 3, marginTop: 12, overflow: 'hidden' }}>
        <div style={{ width: `${pct}%`, height: '100%', background: color, borderRadius: 3, transition: 'width 0.8s ease' }} />
      </div>
      <div style={{ fontFamily: 'var(--font-head)', fontSize: 11, color, fontWeight: 600, marginTop: 8 }}>{zone}</div>
    </div>
  );
}

export default function LivePage() {
  const [dragOver, setDragOver] = useState(false);
  const [chartResult, setChartResult] = useState<any>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [search, setSearch] = useState('');

  const handleDrop = useCallback(async (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (!file) return;
    setAnalyzing(true);
    try {
      const { api } = await import('@/lib/api');
      const result = await api.analyzeChart(file);
      setChartResult(result);
    } catch { setChartResult({ error: 'Analysis failed' }); }
    setAnalyzing(false);
  }, []);

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      <Sidebar />
      <main style={{ marginLeft: 240, flex: 1, display: 'flex', flexDirection: 'column', width: 'calc(100% - 240px)' }}>
        <TickerStrip />

        <div style={{ padding: '32px 40px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 32 }}>
            <h1 style={{ fontFamily: 'var(--font-head)', fontSize: 32, fontWeight: 800, letterSpacing: '-0.02em' }}>
              Live <span style={{ color: 'var(--blue)' }}>Market</span>
            </h1>
            <div style={{ width: 400, position: 'relative' }}>
              <input 
                className="apex-input" 
                placeholder="SEARCH SYMBOL (e.g. RELIANCE, HDFCBANK)..." 
                value={search}
                onChange={e => setSearch(e.target.value)}
                style={{ fontSize: 11, paddingLeft: 40 }}
              />
              <span style={{ position: 'absolute', left: 16, top: 12, opacity: 0.5 }}>🔍</span>
            </div>
          </div>

          {/* Spot Tickers */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, marginBottom: 32 }}>
            {[
              { symbol: 'BANKNIFTY', name: 'Nifty Bank Index', price: 55742.30, change: -187.45, pct: -0.34 },
              { symbol: 'NIFTY', name: 'Nifty 50 Index', price: 24685.15, change: 42.30, pct: 0.17 },
            ].map((idx) => (
              <div key={idx.symbol} className="apex-card" style={{ padding: '24px 32px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div>
                    <div style={{ fontFamily: 'var(--font-mono)', fontSize: 18, fontWeight: 800, color: 'var(--text)' }}>{idx.symbol}</div>
                    <div style={{ fontFamily: 'var(--font-head)', fontSize: 11, color: 'var(--muted)', marginTop: 2 }}>{idx.name}</div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontFamily: 'var(--font-mono)', fontSize: 32, fontWeight: 700, color: 'var(--text)' }}>
                      {idx.price.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                    </div>
                    <div style={{
                      fontFamily: 'var(--font-mono)', fontSize: 14, fontWeight: 700,
                      color: idx.change >= 0 ? 'var(--green)' : 'var(--red)',
                      marginTop: 4
                    }}>
                      {idx.change >= 0 ? '▲' : '▼'} {Math.abs(idx.change).toFixed(2)} ({idx.pct >= 0 ? '+' : ''}{idx.pct.toFixed(2)}%)
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 200px 200px', gap: 16, marginBottom: 24 }}>
            {/* Chart Upload */}
            <div
              className="apex-card"
              onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
              onDragLeave={() => setDragOver(false)}
              onDrop={handleDrop}
              style={{
                padding: 24,
                border: dragOver ? '2px dashed var(--purple)' : '1px solid var(--border)',
                background: dragOver ? 'rgba(167,139,250,0.05)' : 'var(--surface)',
                cursor: 'pointer', minHeight: 180,
                display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
              }}
            >
              {analyzing ? (
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontFamily: 'var(--font-mono)', fontSize: 14, color: 'var(--purple)' }}>◎ ANALYZING...</div>
                  <div style={{ fontFamily: 'var(--font-head)', fontSize: 11, color: 'var(--muted)', marginTop: 8 }}>AI vision processing</div>
                </div>
              ) : chartResult ? (
                <div style={{ width: '100%', fontSize: 12, fontFamily: 'var(--font-mono)' }}>
                  <div style={{ color: 'var(--purple)', fontFamily: 'var(--font-head)', fontSize: 10, letterSpacing: '0.1em', marginBottom: 10 }}>◎ CHART ANALYSIS RESULT</div>
                  <div style={{ color: chartResult.analysis?.current_trend === 'BULLISH' ? 'var(--green)' : chartResult.analysis?.current_trend === 'BEARISH' ? 'var(--red)' : 'var(--amber)', fontSize: 18, fontWeight: 700, marginBottom: 8 }}>
                    {chartResult.analysis?.current_trend || 'N/A'} — Confidence {chartResult.analysis?.confidence || 0}%
                  </div>
                  <p style={{ fontSize: 11, color: 'var(--text)', lineHeight: 1.6 }}>{chartResult.analysis?.reasoning || chartResult.error}</p>
                  <button className="apex-btn" style={{ marginTop: 12, fontSize: 11 }} onClick={() => setChartResult(null)}>Clear</button>
                </div>
              ) : (
                <>
                  <div style={{ fontSize: 36, marginBottom: 8, opacity: 0.3 }}>📊</div>
                  <div style={{ fontFamily: 'var(--font-head)', fontSize: 13, color: 'var(--muted)' }}>Drop chart screenshot here</div>
                  <div style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: 'var(--muted)', marginTop: 4 }}>AI analysis in &lt;15 seconds</div>
                </>
              )}
            </div>

            <PCRGauge pcr={0.85} />
            <VIXMeter vix={16.4} />
          </div>

          {/* OI Heatmap Table */}
          <div className="apex-card" style={{ padding: '20px 24px', marginBottom: 24 }}>
            <div style={{ fontFamily: 'var(--font-head)', fontSize: 14, fontWeight: 700, marginBottom: 16 }}>
              OI Heatmap — BANKNIFTY
            </div>
            <div className="apex-table-wrapper"><table className="apex-table">
              <thead>
                <tr>
                  <th>CE OI CHG</th><th>CE OI</th><th>CE IV</th><th>CE LTP</th>
                  <th style={{ textAlign: 'center', color: 'var(--amber)' }}>STRIKE</th>
                  <th>PE LTP</th><th>PE IV</th><th>PE OI</th><th>PE OI CHG</th>
                </tr>
              </thead>
              <tbody>
                {DEMO_CHAIN.map((row) => {
                  const maxCeOI = Math.max(...DEMO_CHAIN.map(r => r.ce_oi));
                  const maxPeOI = Math.max(...DEMO_CHAIN.map(r => r.pe_oi));
                  return (
                    <tr key={row.strike} style={{ background: row.isATM ? 'rgba(245,166,35,0.06)' : 'transparent' }}>
                      <td style={{ color: row.ce_chg > 0 ? 'var(--red)' : 'var(--green)' }}>{row.ce_chg > 0 ? '+' : ''}{row.ce_chg.toLocaleString()}</td>
                      <td>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                          <div style={{ width: 60, height: 6, background: 'var(--surface2)', borderRadius: 3, overflow: 'hidden' }}>
                            <div style={{ width: `${(row.ce_oi / maxCeOI) * 100}%`, height: '100%', background: 'var(--red)', borderRadius: 3, opacity: 0.6 }} />
                          </div>
                          <span>{(row.ce_oi / 1000).toFixed(0)}K</span>
                        </div>
                      </td>
                      <td style={{ color: 'var(--muted)' }}>{row.ce_iv}</td>
                      <td>{row.ce_ltp.toFixed(1)}</td>
                      <td style={{ textAlign: 'center', fontWeight: 700, color: row.isATM ? 'var(--amber)' : 'var(--text)', fontSize: row.isATM ? 14 : 12 }}>
                        {row.strike.toLocaleString()}
                      </td>
                      <td>{row.pe_ltp.toFixed(1)}</td>
                      <td style={{ color: 'var(--muted)' }}>{row.pe_iv}</td>
                      <td>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                          <span>{(row.pe_oi / 1000).toFixed(0)}K</span>
                          <div style={{ width: 60, height: 6, background: 'var(--surface2)', borderRadius: 3, overflow: 'hidden' }}>
                            <div style={{ width: `${(row.pe_oi / maxPeOI) * 100}%`, height: '100%', background: 'var(--green)', borderRadius: 3, opacity: 0.6 }} />
                          </div>
                        </div>
                      </td>
                      <td style={{ color: row.pe_chg > 0 ? 'var(--green)' : 'var(--red)' }}>{row.pe_chg > 0 ? '+' : ''}{row.pe_chg.toLocaleString()}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table></div>
          </div>

          {/* Alert Feed */}
          <div className="apex-card" style={{ padding: '20px 24px' }}>
            <div style={{ fontFamily: 'var(--font-head)', fontSize: 14, fontWeight: 700, marginBottom: 16 }}>Alert Feed</div>
            {[
              { time: '10:35', msg: '🟢 PCR crossed 1.3 → 1.34 | Bullish signal activated', type: 'bullish' },
              { time: '11:10', msg: '⚡ OI SPIKE: BANKNIFTY 56000 CE | OI +18% in 5 min', type: 'neutral' },
              { time: '12:45', msg: '📍 KEY LEVEL: BANKNIFTY broke SUPPORT at 55600 | Now: 55542', type: 'bearish' },
            ].map((a, i) => (
              <div key={i} style={{
                display: 'flex', gap: 12, padding: '10px 0',
                borderBottom: '1px solid rgba(30,45,71,0.4)',
              }}>
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--muted)', minWidth: 45 }}>{a.time}</span>
                <span style={{ fontFamily: 'var(--font-head)', fontSize: 12, color: 'var(--text)' }}>{a.msg}</span>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}
