'use client';

import Sidebar from '@/components/ui/Sidebar';
import TickerStrip from '@/components/ui/TickerStrip';
import { useState } from 'react';

export default function SettingsPage() {
  const [provider, setProvider] = useState('gemini');
  const [broker, setBroker] = useState('angel_one');
  const [capital, setCapital] = useState('100000');
  const [risk, setRisk] = useState('2');
  const [telegramEnabled, setTelegramEnabled] = useState(true);

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      <Sidebar />
      <main style={{ marginLeft: 240, flex: 1, display: 'flex', flexDirection: 'column' }}>
        <TickerStrip />
        <div style={{ padding: '24px 32px', maxWidth: 800 }}>
          <h1 style={{ fontFamily: 'var(--font-head)', fontSize: 28, fontWeight: 800, marginBottom: 24 }}>Settings</h1>

          {/* AI Provider */}
          <div className="apex-card" style={{ padding: '24px 28px', marginBottom: 16 }}>
            <div style={{ fontFamily: 'var(--font-head)', fontSize: 14, fontWeight: 700, marginBottom: 16 }}>AI Provider</div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 8 }}>
              {[
                { id: 'gemini', name: 'Gemini 2.0 Flash', sub: 'Free • 1500/day • Vision', badge: '🟢' },
                { id: 'groq', name: 'Groq Llama 3.3', sub: 'Free • 14400/day • Fastest', badge: '⚡' },
                { id: 'openrouter', name: 'OpenRouter', sub: 'Free tier • Fallback', badge: '🔄' },
                { id: 'ollama', name: 'Ollama Local', sub: 'Offline • Unlimited', badge: '💻' },
                { id: 'claude', name: 'Claude Sonnet', sub: 'Paid • Best analysis', badge: '🧠' },
                { id: 'openai', name: 'GPT-4o', sub: 'Paid • Alternative', badge: '🤖' },
              ].map(p => (
                <button key={p.id} onClick={() => setProvider(p.id)} style={{
                  padding: '12px 16px', borderRadius: 6, textAlign: 'left', cursor: 'pointer',
                  background: provider === p.id ? 'rgba(0,255,136,0.08)' : 'var(--surface2)',
                  border: `1px solid ${provider === p.id ? 'rgba(0,255,136,0.3)' : 'var(--border)'}`,
                }}>
                  <div style={{ fontSize: 14, marginBottom: 4 }}>{p.badge}</div>
                  <div style={{ fontFamily: 'var(--font-head)', fontSize: 12, color: provider === p.id ? 'var(--green)' : 'var(--text)', fontWeight: 600 }}>{p.name}</div>
                  <div style={{ fontFamily: 'var(--font-mono)', fontSize: 9, color: 'var(--muted)', marginTop: 4 }}>{p.sub}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Broker */}
          <div className="apex-card" style={{ padding: '24px 28px', marginBottom: 16 }}>
            <div style={{ fontFamily: 'var(--font-head)', fontSize: 14, fontWeight: 700, marginBottom: 16 }}>Active Broker</div>
            <div style={{ display: 'flex', gap: 8 }}>
              {['angel_one', 'upstox', 'dhan', 'zerodha'].map(b => (
                <button key={b} onClick={() => setBroker(b)} className="apex-btn" style={{
                  fontSize: 11,
                  ...(broker === b ? { background: 'rgba(0,255,136,0.1)', borderColor: 'rgba(0,255,136,0.3)', color: 'var(--green)' } : {}),
                }}>
                  {b.replace('_', ' ').toUpperCase()}
                </button>
              ))}
            </div>
          </div>

          {/* Trading Params */}
          <div className="apex-card" style={{ padding: '24px 28px', marginBottom: 16 }}>
            <div style={{ fontFamily: 'var(--font-head)', fontSize: 14, fontWeight: 700, marginBottom: 16 }}>Trading Parameters</div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
              <div>
                <label style={{ fontFamily: 'var(--font-head)', fontSize: 11, color: 'var(--muted)', display: 'block', marginBottom: 6 }}>TRADING CAPITAL (₹)</label>
                <input className="apex-input" value={capital} onChange={e => setCapital(e.target.value)} />
              </div>
              <div>
                <label style={{ fontFamily: 'var(--font-head)', fontSize: 11, color: 'var(--muted)', display: 'block', marginBottom: 6 }}>RISK PER TRADE (%)</label>
                <input className="apex-input" value={risk} onChange={e => setRisk(e.target.value)} />
              </div>
            </div>
          </div>

          {/* Alerts */}
          <div className="apex-card" style={{ padding: '24px 28px', marginBottom: 16 }}>
            <div style={{ fontFamily: 'var(--font-head)', fontSize: 14, fontWeight: 700, marginBottom: 16 }}>Alerts</div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div>
                <div style={{ fontFamily: 'var(--font-head)', fontSize: 13, color: 'var(--text)' }}>Telegram Alerts</div>
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: 'var(--muted)', marginTop: 2 }}>Morning picks, live alerts, weekly reviews</div>
              </div>
              <button onClick={() => setTelegramEnabled(!telegramEnabled)} style={{
                width: 48, height: 26, borderRadius: 13, border: 'none', cursor: 'pointer',
                background: telegramEnabled ? 'var(--green)' : 'var(--border)',
                position: 'relative', transition: 'background 0.2s',
              }}>
                <div style={{
                  width: 20, height: 20, borderRadius: '50%', background: 'white',
                  position: 'absolute', top: 3,
                  left: telegramEnabled ? 25 : 3,
                  transition: 'left 0.2s',
                }} />
              </button>
            </div>
          </div>

          {/* Save */}
          <button className="apex-btn primary" style={{ width: '100%', justifyContent: 'center', padding: 14, fontSize: 14 }}>
            Save Configuration
          </button>
        </div>
      </main>
    </div>
  );
}
