'use client';

import Sidebar from '@/components/ui/Sidebar';
import TickerStrip from '@/components/ui/TickerStrip';
import { useState } from 'react';

const CHAIN = Array.from({ length: 25 }, (_, i) => {
  const strike = 54800 + i * 100;
  const atm = 55700;
  return {
    strike, isATM: Math.abs(strike - atm) < 50,
    ce_oi: Math.round(Math.random() * 120000 + 5000),
    ce_chg: Math.round((Math.random() - 0.45) * 20000),
    ce_iv: +(15 + Math.random() * 12).toFixed(1),
    ce_ltp: +(Math.max(2, (atm - strike) * 0.4 + Math.random() * 60)).toFixed(1),
    ce_vol: Math.round(Math.random() * 50000),
    pe_oi: Math.round(Math.random() * 120000 + 5000),
    pe_chg: Math.round((Math.random() - 0.45) * 20000),
    pe_iv: +(15 + Math.random() * 12).toFixed(1),
    pe_ltp: +(Math.max(2, (strike - atm) * 0.4 + Math.random() * 60)).toFixed(1),
    pe_vol: Math.round(Math.random() * 50000),
  };
});

export default function OptionsPage() {
  const [index, setIndex] = useState<'BANKNIFTY' | 'NIFTY'>('BANKNIFTY');
  const [search, setSearch] = useState('');
  const maxOI = Math.max(...CHAIN.map(r => Math.max(r.ce_oi, r.pe_oi)));

  const filteredChain = CHAIN.filter(r => 
    r.strike.toString().includes(search) || 
    (search.toUpperCase() === 'ATM' && r.isATM)
  );

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      <Sidebar />
      <main style={{ marginLeft: 240, flex: 1, display: 'flex', flexDirection: 'column', width: 'calc(100% - 240px)' }}>
        <TickerStrip />
        <div style={{ padding: '32px 40px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 32 }}>
            <h1 style={{ fontFamily: 'var(--font-head)', fontSize: 32, fontWeight: 800, letterSpacing: '-0.02em' }}>
              Options <span style={{ color: 'var(--amber)' }}>Chain</span>
            </h1>
            
            <div style={{ display: 'flex', gap: 16, alignItems: 'center' }}>
              <div style={{ width: 300, position: 'relative' }}>
                <input 
                  className="apex-input" 
                  placeholder="SEARCH STRIKE (e.g. 55800)..." 
                  value={search}
                  onChange={e => setSearch(e.target.value)}
                  style={{ fontSize: 11, paddingLeft: 40 }}
                />
                <span style={{ position: 'absolute', left: 16, top: 12, opacity: 0.5 }}>🔍</span>
              </div>

              <div style={{ display: 'flex', gap: 4 }}>
                {(['BANKNIFTY', 'NIFTY'] as const).map(idx => (
                  <button key={idx} onClick={() => setIndex(idx)} className="apex-btn" style={{
                    fontSize: 11, padding: '8px 20px',
                    ...(index === idx ? { background: 'rgba(245,166,35,0.1)', borderColor: 'rgba(245,166,35,0.3)', color: 'var(--amber)' } : {}),
                  }}>
                    {idx}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Summary row */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12, marginBottom: 20 }}>
            {[
              { label: 'SPOT', value: '55,742.30', color: 'var(--text)' },
              { label: 'PCR', value: '0.85', color: 'var(--amber)' },
              { label: 'MAX PAIN', value: '55,800', color: 'var(--purple)' },
              { label: 'IV RANK', value: '42%', color: 'var(--blue)' },
            ].map((s, i) => (
              <div key={i} className="apex-card" style={{ padding: '12px 16px', textAlign: 'center' }}>
                <div style={{ fontFamily: 'var(--font-head)', fontSize: 9, color: 'var(--muted)', letterSpacing: '0.1em' }}>{s.label}</div>
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: 20, fontWeight: 700, color: s.color, marginTop: 4 }}>{s.value}</div>
              </div>
            ))}
          </div>

          {/* Full Chain */}
          <div className="apex-card" style={{ padding: '16px 20px', overflow: 'auto' }}>
            <table className="apex-table" style={{ fontSize: 11 }}>
              <thead>
                <tr>
                  <th>OI CHG</th><th>OI</th><th style={{ width: 70 }}>OI BAR</th><th>VOL</th><th>IV</th><th>LTP</th>
                  <th style={{ textAlign: 'center', color: 'var(--amber)', fontSize: 12 }}>STRIKE</th>
                  <th>LTP</th><th>IV</th><th>VOL</th><th style={{ width: 70 }}>OI BAR</th><th>OI</th><th>OI CHG</th>
                </tr>
              </thead>
              <tbody>
                {filteredChain.map((r) => (
                  <tr key={r.strike} style={{ background: r.isATM ? 'rgba(245,166,35,0.08)' : 'transparent' }}>
                    <td style={{ color: r.ce_chg > 0 ? 'var(--red)' : 'var(--green)' }}>{r.ce_chg > 0 ? '+' : ''}{(r.ce_chg / 1000).toFixed(1)}K</td>
                    <td>{(r.ce_oi / 1000).toFixed(0)}K</td>
                    <td><div style={{ width: '100%', height: 6, background: 'var(--surface2)', borderRadius: 3 }}><div style={{ width: `${(r.ce_oi / maxOI) * 100}%`, height: '100%', background: 'var(--red)', opacity: 0.5, borderRadius: 3 }} /></div></td>
                    <td style={{ color: 'var(--muted)' }}>{(r.ce_vol / 1000).toFixed(0)}K</td>
                    <td style={{ color: 'var(--muted)' }}>{r.ce_iv}</td>
                    <td style={{ fontWeight: 600 }}>{r.ce_ltp}</td>
                    <td style={{ textAlign: 'center', fontWeight: 700, fontSize: r.isATM ? 13 : 11, color: r.isATM ? 'var(--amber)' : 'var(--text)', borderLeft: '1px solid var(--border)', borderRight: '1px solid var(--border)' }}>
                      {r.strike.toLocaleString()}
                    </td>
                    <td style={{ fontWeight: 600 }}>{r.pe_ltp}</td>
                    <td style={{ color: 'var(--muted)' }}>{r.pe_iv}</td>
                    <td style={{ color: 'var(--muted)' }}>{(r.pe_vol / 1000).toFixed(0)}K</td>
                    <td><div style={{ width: '100%', height: 6, background: 'var(--surface2)', borderRadius: 3 }}><div style={{ width: `${(r.pe_oi / maxOI) * 100}%`, height: '100%', background: 'var(--green)', opacity: 0.5, borderRadius: 3 }} /></div></td>
                    <td>{(r.pe_oi / 1000).toFixed(0)}K</td>
                    <td style={{ color: r.pe_chg > 0 ? 'var(--green)' : 'var(--red)' }}>{r.pe_chg > 0 ? '+' : ''}{(r.pe_chg / 1000).toFixed(1)}K</td>
                  </tr>
                ))}
              </tbody>
            </table></div>
          </div>
        </div>
      </div></div></main>
    </div>
  );
}
