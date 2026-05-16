'use client';

import Sidebar from '@/components/ui/Sidebar';
import TickerStrip from '@/components/ui/TickerStrip';
import ConfidenceRing from '@/components/morning/ConfidenceRing';
import { useState } from 'react';

// Demo data — replaced by API in production
const DEMO_REC = {
  action: 'TRADE', date: '2025-01-15', index: 'BANKNIFTY',
  expiry: '2025-01-16', direction: 'BEARISH',
  recommended_strike: '56000 PE',
  entry_low: 145, entry_high: 155,
  stop_loss: 95, target1: 210, target2: 290,
  risk_reward: 2.8, confidence: 73,
  position_size: '1 lot (2% capital risk)',
  strategy_type: 'Directional buy',
  technical_bias: 'BEARISH — Below VWAP, EMA9 < EMA21 on 15m, RSI 38, MACD histogram turning negative',
  sentiment_bias: 'BEARISH — PCR 0.68, heavy CE OI buildup at 56200, max pain at 55800',
  news_bias: 'NEUTRAL — No major triggers in last 12 hours',
  macro_bias: 'MILDLY BEARISH — FII sold ₹1200Cr net yesterday, DXY up 0.4%',
  caution_flags: ['Expiry tomorrow — wide spreads expected', 'VIX at 16, slightly elevated'],
  alternatives: [
    { strike: '55800 PE', reasoning: 'Closer to max pain, higher delta' },
    { strategy: 'Bear Call Spread 56000/56500', reasoning: 'Defined risk, collect premium' },
  ],
  reasoning: 'Three of four biases align bearish today. Price action shows consistent lower highs since 10 AM, VWAP rejection confirmed at 56180. Options data shows call writers are active at 56200 suggesting smart money sees resistance there. FII sold significantly yesterday and DXY strength creates headwind for FII inflows. Only news is neutral — no positive catalyst to reverse the technical picture. Trade with discipline, respect the stop.',
  generated_at: new Date().toISOString(),
};

const LEVELS = [
  { label: 'Resistance 2', value: 56400, type: 'resistance' },
  { label: 'Resistance 1', value: 56200, type: 'resistance' },
  { label: 'Max Pain', value: 55800, type: 'neutral' },
  { label: 'Support 1', value: 55600, type: 'support' },
  { label: 'Support 2', value: 55300, type: 'support' },
];

function BiasChip({ label, text, dir }: { label: string; text: string; dir: string }) {
  const d = dir?.toUpperCase();
  const cls = d?.includes('BULLISH') ? 'bullish' : d?.includes('BEARISH') ? 'bearish' : 'neutral';
  return (
    <div style={{ flex: 1, minWidth: 200 }}>
      <div style={{ fontFamily: 'var(--font-head)', fontSize: 10, color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 6 }}>
        {label}
      </div>
      <div className={`bias-chip ${cls}`} style={{ width: '100%', padding: '8px 12px', fontSize: 11, lineHeight: 1.5 }}>
        {text}
      </div>
    </div>
  );
}

export default function MorningPage() {
  const rec = DEMO_REC;
  const isBullish = rec.direction === 'BULLISH';
  const dirColor = isBullish ? 'var(--green)' : rec.direction === 'BEARISH' ? 'var(--red)' : 'var(--amber)';
  const [expanded, setExpanded] = useState(false);

  return (
    <>
      <Sidebar />
      <main className="main-container">
        <TickerStrip />
        <div className="content-viewport">
          <div className="page-content">

        <div style={{ maxWidth: 1200 }}>
          {/* Header */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 24 }}>
            <div>
              <h1 style={{ fontFamily: 'var(--font-head)', fontSize: 28, fontWeight: 800, letterSpacing: '-0.03em' }}>
                Morning Briefing
              </h1>
              <p style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--muted)', marginTop: 4 }}>
                {new Date().toLocaleDateString('en-IN', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })}
                {' • '}Generated at {new Date(rec.generated_at).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })}
              </p>
            </div>
            {/* Market Mood Badge */}
            <div style={{
              padding: '12px 28px', borderRadius: 8,
              background: rec.direction === 'BEARISH' ? 'rgba(255,59,92,0.1)' : rec.direction === 'BULLISH' ? 'rgba(0,255,136,0.1)' : 'rgba(245,166,35,0.1)',
              border: `1px solid ${dirColor}33`,
            }}>
              <div style={{ fontFamily: 'var(--font-head)', fontSize: 10, color: 'var(--muted)', letterSpacing: '0.1em', marginBottom: 4 }}>MARKET MOOD</div>
              <div style={{ fontFamily: 'var(--font-head)', fontSize: 22, fontWeight: 800, color: dirColor }}>
                {rec.direction === 'BEARISH' ? '🔴' : rec.direction === 'BULLISH' ? '🟢' : '🟡'} {rec.direction}
              </div>
            </div>
          </div>

          {/* Main Trade Card */}
          <div className="apex-card" style={{ padding: 0, marginBottom: 24 }}>
            {/* Top bar with strike */}
            <div style={{
              padding: '20px 28px',
              background: `linear-gradient(135deg, ${dirColor}08, transparent)`,
              borderBottom: '1px solid var(--border)',
              display: 'flex', alignItems: 'center', justifyContent: 'space-between',
            }}>
              <div>
                <div style={{ fontFamily: 'var(--font-head)', fontSize: 10, color: 'var(--muted)', letterSpacing: '0.1em', marginBottom: 6 }}>
                  TODAY&apos;S PICK — {rec.index}
                </div>
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: 32, fontWeight: 700, color: dirColor, letterSpacing: '-0.02em' }}>
                  {rec.recommended_strike}
                </div>
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--muted)', marginTop: 4 }}>
                  Expiry: {rec.expiry} • {rec.strategy_type} • {rec.position_size}
                </div>
              </div>
              <ConfidenceRing confidence={rec.confidence} size={110} />
            </div>

            {/* Entry / SL / Target boxes */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', borderBottom: '1px solid var(--border)' }}>
              {[
                { label: 'ENTRY RANGE', value: `₹${rec.entry_low} – ₹${rec.entry_high}`, color: 'var(--blue)' },
                { label: 'STOP LOSS', value: `₹${rec.stop_loss}`, sub: '35% of premium', color: 'var(--red)' },
                { label: 'TARGET 1', value: `₹${rec.target1}`, color: 'var(--green)' },
                { label: 'TARGET 2', value: `₹${rec.target2}`, sub: `R:R 1:${rec.risk_reward}`, color: 'var(--green)' },
              ].map((box, i) => (
                <div key={i} style={{
                  padding: '18px 24px',
                  borderRight: i < 3 ? '1px solid var(--border)' : 'none',
                }}>
                  <div style={{ fontFamily: 'var(--font-head)', fontSize: 9, color: 'var(--muted)', letterSpacing: '0.1em', marginBottom: 8 }}>
                    {box.label}
                  </div>
                  <div style={{ fontFamily: 'var(--font-mono)', fontSize: 20, fontWeight: 700, color: box.color }}>
                    {box.value}
                  </div>
                  {box.sub && (
                    <div style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: 'var(--muted)', marginTop: 4 }}>
                      {box.sub}
                    </div>
                  )}
                </div>
              ))}
            </div>

            {/* 4 Bias Chips */}
            <div style={{ display: 'flex', gap: 16, padding: '20px 28px', borderBottom: '1px solid var(--border)', flexWrap: 'wrap' }}>
              <BiasChip label="Technical" text={rec.technical_bias} dir={rec.technical_bias} />
              <BiasChip label="Sentiment" text={rec.sentiment_bias} dir={rec.sentiment_bias} />
              <BiasChip label="News" text={rec.news_bias} dir={rec.news_bias} />
              <BiasChip label="Macro" text={rec.macro_bias} dir={rec.macro_bias} />
            </div>

            {/* Reasoning */}
            <div style={{ padding: '20px 28px', borderBottom: '1px solid var(--border)' }}>
              <div style={{ fontFamily: 'var(--font-head)', fontSize: 10, color: 'var(--purple)', letterSpacing: '0.1em', marginBottom: 10 }}>
                ◎ AI REASONING
              </div>
              <p style={{ fontFamily: 'var(--font-head)', fontSize: 14, color: 'var(--text)', lineHeight: 1.7, maxWidth: 800 }}>
                {rec.reasoning}
              </p>
            </div>

            {/* Caution Flags */}
            <div style={{ padding: '16px 28px', borderBottom: '1px solid var(--border)' }}>
              <div style={{ fontFamily: 'var(--font-head)', fontSize: 10, color: 'var(--amber)', letterSpacing: '0.1em', marginBottom: 10 }}>
                ⚠ CAUTION FLAGS
              </div>
              <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
                {rec.caution_flags.map((flag, i) => (
                  <span key={i} className="bias-chip neutral" style={{ fontSize: 11 }}>
                    {flag}
                  </span>
                ))}
              </div>
            </div>

            {/* Alternatives */}
            <div style={{ padding: '16px 28px' }}>
              <div style={{ fontFamily: 'var(--font-head)', fontSize: 10, color: 'var(--muted)', letterSpacing: '0.1em', marginBottom: 10, cursor: 'pointer' }}
                   onClick={() => setExpanded(!expanded)}>
                {expanded ? '▼' : '▶'} ALTERNATIVES
              </div>
              {expanded && rec.alternatives.map((alt, i) => (
                <div key={i} style={{
                  padding: '10px 14px', marginBottom: 8,
                  background: 'var(--surface2)', borderRadius: 6, border: '1px solid var(--border)',
                }}>
                  <span style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--blue)', fontWeight: 700 }}>
                    {'strike' in alt ? alt.strike : alt.strategy}
                  </span>
                  <span style={{ fontFamily: 'var(--font-head)', fontSize: 12, color: 'var(--muted)', marginLeft: 12 }}>
                    — {alt.reasoning}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Key Levels Table */}
          <div className="apex-card" style={{ padding: '20px 24px', marginBottom: 24 }}>
            <div style={{ fontFamily: 'var(--font-head)', fontSize: 14, fontWeight: 700, marginBottom: 16 }}>
              Key Levels — {rec.index}
            </div>
            <div className="apex-table-wrapper"><table className="apex-table">
              <thead>
                <tr>
                  <th>Level</th>
                  <th>Price</th>
                  <th>Type</th>
                </tr>
              </thead>
              <tbody>
                {LEVELS.map((lv, i) => (
                  <tr key={i}>
                    <td style={{ color: 'var(--text)' }}>{lv.label}</td>
                    <td style={{
                      color: lv.type === 'resistance' ? 'var(--red)' : lv.type === 'support' ? 'var(--green)' : 'var(--amber)',
                      fontWeight: 700,
                    }}>
                      {lv.value.toLocaleString()}
                    </td>
                    <td>
                      <span className={`bias-chip ${lv.type === 'resistance' ? 'bearish' : lv.type === 'support' ? 'bullish' : 'neutral'}`}>
                        {lv.type.toUpperCase()}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table></div>
          </div>

          {/* One-liner Summary */}
          <div className="apex-card" style={{ padding: '16px 24px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <span style={{ color: 'var(--purple)', fontSize: 16 }}>◎</span>
              <p style={{ fontFamily: 'var(--font-head)', fontSize: 14, color: 'var(--text)', fontStyle: 'italic' }}>
                &quot;BankNifty bearish bias with 3/4 alignment. Sell rallies toward 56200, defend 55600 support. Discipline over conviction.&quot;
              </p>
            </div>
          </div>
        </div>
                </div>
        </div>
      </main>
    </>
  );
}
