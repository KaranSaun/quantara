'use client';

import Sidebar from '@/components/ui/Sidebar';
import TickerStrip from '@/components/ui/TickerStrip';
import { useState, useRef, useEffect } from 'react';

interface Message {
  role: 'user' | 'ai';
  text: string;
  time: string;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    { role: 'ai', text: 'QUANTARA OS AI ready. I have full context of today\'s market data, your portfolio, and trade history. Ask me anything.', time: new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' }) },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;
    const userMsg: Message = { role: 'user', text: input, time: new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' }) };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const { api } = await import('@/lib/api');
      const res = await api.chat(userMsg.text);
      setMessages(prev => [...prev, {
        role: 'ai', text: res.response || 'No response',
        time: new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' }),
      }]);
    } catch {
      setMessages(prev => [...prev, {
        role: 'ai', text: 'Connection to backend failed. Ensure the API server is running on localhost:8000.',
        time: new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' }),
      }]);
    }
    setLoading(false);
  };

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      <Sidebar />
      <main style={{ marginLeft: 240, flex: 1, display: 'flex', flexDirection: 'column', height: '100vh', width: 'calc(100% - 240px)' }}>
        <TickerStrip />

        <div style={{ padding: '32px 40px 16px' }}>
          <h1 style={{ fontFamily: 'var(--font-head)', fontSize: 32, fontWeight: 800, letterSpacing: '-0.02em', marginBottom: 4 }}>
            Command <span style={{ color: 'var(--purple)' }}>Center</span>
          </h1>
          <p style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: 'var(--muted)', letterSpacing: '0.1em' }}>FULL MARKET CONTEXT • PORTFOLIO AWARE • OPTIONS INTELLIGENCE</p>
        </div>

        {/* Quick prompts */}
        <div style={{ padding: '0 32px 12px', display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          {[
            'Should I take today\'s pick?',
            'What\'s the risk if VIX spikes?',
            'Analyze BankNifty OI buildup',
            'Review my week',
            'Is there a hedge strategy?',
          ].map((q, i) => (
            <button key={i} className="apex-btn" style={{ fontSize: 10, padding: '5px 12px' }}
              onClick={() => { setInput(q); }}>
              {q}
            </button>
          ))}
        </div>

        {/* Messages */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '0 32px 16px' }}>
          {messages.map((msg, i) => (
            <div key={i} style={{
              display: 'flex',
              justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
              marginBottom: 12,
            }}>
              <div style={{
                maxWidth: 650,
                padding: '12px 16px',
                borderRadius: msg.role === 'user' ? '12px 12px 2px 12px' : '12px 12px 12px 2px',
                background: msg.role === 'user' ? 'rgba(79,156,249,0.12)' : 'var(--surface)',
                border: `1px solid ${msg.role === 'user' ? 'rgba(79,156,249,0.25)' : 'var(--border)'}`,
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
                  <span style={{ fontFamily: 'var(--font-head)', fontSize: 10, color: msg.role === 'user' ? 'var(--blue)' : 'var(--purple)', fontWeight: 600, letterSpacing: '0.05em' }}>
                    {msg.role === 'user' ? 'YOU' : '◎ APEX AI'}
                  </span>
                  <span style={{ fontFamily: 'var(--font-mono)', fontSize: 9, color: 'var(--muted)' }}>{msg.time}</span>
                </div>
                <div style={{ fontFamily: 'var(--font-head)', fontSize: 13, color: 'var(--text)', lineHeight: 1.7, whiteSpace: 'pre-wrap' }}>
                  {msg.text}
                </div>
              </div>
            </div>
          ))}
          {loading && (
            <div style={{ display: 'flex', gap: 8, padding: '12px 0' }}>
              <span style={{ color: 'var(--purple)', fontFamily: 'var(--font-mono)', fontSize: 12 }}>◎ Thinking...</span>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {/* Input */}
        <div style={{ padding: '12px 32px 20px', borderTop: '1px solid var(--border)', background: 'var(--bg)' }}>
          <div style={{ display: 'flex', gap: 10 }}>
            <input className="apex-input" value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleSend()}
              placeholder="Ask anything about market, trades, portfolio..."
              style={{ flex: 1, fontFamily: 'var(--font-head)' }}
            />
            <button className="apex-btn primary" onClick={handleSend} disabled={loading}>
              Send
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}
