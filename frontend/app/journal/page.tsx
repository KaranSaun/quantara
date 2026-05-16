'use client';

import Sidebar from '@/components/ui/Sidebar';
import TickerStrip from '@/components/ui/TickerStrip';
import { useState } from 'react';

export default function JournalPage() {
  const [notes, setNotes] = useState('');
  const [emotional, setEmotional] = useState(3);
  const [discipline, setDiscipline] = useState(3);

  const weekReview = {
    total_pnl: 12400,
    win_rate: 72,
    biggest_leak: 'Cutting winners 40% early on average',
    strongest_edge: 'Strong entry timing on bearish setups',
    next_week_focus: 'Let targets breathe — hold T1 for at least 15 min before trailing',
    encouragement: 'Your discipline on Thursday (staying flat when VIX spiked) saved you ₹4000+ in potential losses. That is professional-level restraint.',
  };

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      <Sidebar />
      <main style={{ marginLeft: 240, flex: 1, display: 'flex', flexDirection: 'column' }}>
        <TickerStrip />
        <div style={{ padding: '24px 32px', maxWidth: 1000 }}>
          <h1 style={{ fontFamily: 'var(--font-head)', fontSize: 28, fontWeight: 800, marginBottom: 24 }}>Trade Journal</h1>

          {/* Today's Entry */}
          <div className="apex-card" style={{ padding: '24px 28px', marginBottom: 24 }}>
            <div style={{ fontFamily: 'var(--font-head)', fontSize: 14, fontWeight: 700, marginBottom: 16 }}>
              Today&apos;s Journal — {new Date().toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })}
            </div>

            <div style={{ marginBottom: 16 }}>
              <label style={{ fontFamily: 'var(--font-head)', fontSize: 11, color: 'var(--muted)', display: 'block', marginBottom: 6 }}>POST-MARKET NOTES</label>
              <textarea className="apex-input" rows={4} value={notes} onChange={e => setNotes(e.target.value)}
                placeholder="What happened today? Did you follow the system? Any deviations?"
                style={{ resize: 'vertical', fontFamily: 'var(--font-head)', lineHeight: 1.6 }}
              />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 16 }}>
              <div>
                <label style={{ fontFamily: 'var(--font-head)', fontSize: 11, color: 'var(--muted)', display: 'block', marginBottom: 8 }}>EMOTIONAL STATE</label>
                <div style={{ display: 'flex', gap: 8 }}>
                  {[1, 2, 3, 4, 5].map(v => (
                    <button key={v} onClick={() => setEmotional(v)}
                      style={{
                        width: 40, height: 40, borderRadius: 6, border: `1px solid ${emotional === v ? 'var(--blue)' : 'var(--border)'}`,
                        background: emotional === v ? 'rgba(79,156,249,0.1)' : 'var(--surface2)',
                        color: emotional === v ? 'var(--blue)' : 'var(--muted)',
                        fontFamily: 'var(--font-mono)', fontSize: 16, fontWeight: 700, cursor: 'pointer',
                      }}>
                      {v}
                    </button>
                  ))}
                  <span style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: 'var(--muted)', alignSelf: 'center', marginLeft: 8 }}>
                    {emotional <= 2 ? 'Stressed' : emotional === 3 ? 'Neutral' : 'Confident'}
                  </span>
                </div>
              </div>
              <div>
                <label style={{ fontFamily: 'var(--font-head)', fontSize: 11, color: 'var(--muted)', display: 'block', marginBottom: 8 }}>DISCIPLINE SCORE</label>
                <div style={{ display: 'flex', gap: 8 }}>
                  {[1, 2, 3, 4, 5].map(v => (
                    <button key={v} onClick={() => setDiscipline(v)}
                      style={{
                        width: 40, height: 40, borderRadius: 6, border: `1px solid ${discipline === v ? 'var(--green)' : 'var(--border)'}`,
                        background: discipline === v ? 'rgba(0,255,136,0.1)' : 'var(--surface2)',
                        color: discipline === v ? 'var(--green)' : 'var(--muted)',
                        fontFamily: 'var(--font-mono)', fontSize: 16, fontWeight: 700, cursor: 'pointer',
                      }}>
                      {v}
                    </button>
                  ))}
                  <span style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: 'var(--muted)', alignSelf: 'center', marginLeft: 8 }}>
                    {discipline <= 2 ? 'Poor' : discipline === 3 ? 'OK' : 'Strong'}
                  </span>
                </div>
              </div>
            </div>

            <button className="apex-btn primary" style={{ marginTop: 8 }}>Save Journal Entry</button>
          </div>

          {/* Weekly AI Review */}
          <div className="apex-card" style={{ padding: '24px 28px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 20 }}>
              <span style={{ color: 'var(--purple)', fontSize: 16 }}>◎</span>
              <span style={{ fontFamily: 'var(--font-head)', fontSize: 14, fontWeight: 700 }}>AI Weekly Review</span>
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: 'var(--muted)', marginLeft: 'auto' }}>Sunday 8:00 PM</span>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 20 }}>
              <div style={{ padding: 16, background: 'var(--surface2)', borderRadius: 6 }}>
                <div style={{ fontFamily: 'var(--font-head)', fontSize: 10, color: 'var(--muted)', letterSpacing: '0.1em' }}>WEEKLY P&L</div>
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: 24, fontWeight: 700, color: 'var(--green)', marginTop: 6 }}>+₹{weekReview.total_pnl.toLocaleString()}</div>
              </div>
              <div style={{ padding: 16, background: 'var(--surface2)', borderRadius: 6 }}>
                <div style={{ fontFamily: 'var(--font-head)', fontSize: 10, color: 'var(--muted)', letterSpacing: '0.1em' }}>WIN RATE</div>
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: 24, fontWeight: 700, color: 'var(--green)', marginTop: 6 }}>{weekReview.win_rate}%</div>
              </div>
            </div>

            {[
              { label: '🔥 STRONGEST EDGE', text: weekReview.strongest_edge, color: 'var(--green)' },
              { label: '🩸 BIGGEST LEAK', text: weekReview.biggest_leak, color: 'var(--red)' },
              { label: '🎯 NEXT WEEK FOCUS', text: weekReview.next_week_focus, color: 'var(--blue)' },
            ].map((item, i) => (
              <div key={i} style={{ padding: '12px 16px', background: 'var(--surface2)', borderRadius: 6, marginBottom: 10, borderLeft: `3px solid ${item.color}` }}>
                <div style={{ fontFamily: 'var(--font-head)', fontSize: 10, color: 'var(--muted)', letterSpacing: '0.08em', marginBottom: 4 }}>{item.label}</div>
                <div style={{ fontFamily: 'var(--font-head)', fontSize: 13, color: 'var(--text)', lineHeight: 1.5 }}>{item.text}</div>
              </div>
            ))}

            <div style={{ padding: '16px', background: 'rgba(0,255,136,0.04)', border: '1px solid rgba(0,255,136,0.15)', borderRadius: 6, marginTop: 16 }}>
              <div style={{ fontFamily: 'var(--font-head)', fontSize: 10, color: 'var(--green)', letterSpacing: '0.08em', marginBottom: 4 }}>💪 ENCOURAGEMENT</div>
              <div style={{ fontFamily: 'var(--font-head)', fontSize: 13, color: 'var(--text)', lineHeight: 1.6, fontStyle: 'italic' }}>
                {weekReview.encouragement}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
