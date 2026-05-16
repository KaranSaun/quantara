'use client';

import Sidebar from '@/components/ui/Sidebar';
import TickerStrip from '@/components/ui/TickerStrip';
import { useState, useEffect } from 'react';
import { api } from '@/lib/api';

interface FinanceItem {
  id: string;
  category: string;
  amount: number;
  type: 'income' | 'expense';
  date: string;
}

export default function FinancePage() {
  const [tab, setTab] = useState<'overview' | 'goals'>('overview');
  const [items, setItems] = useState<FinanceItem[]>([]);
  const [goals, setGoals] = useState<any[]>([]);
  const [newItem, setNewItem] = useState({ category: '', amount: '', type: 'expense' });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [financeData, goalsData] = await Promise.all([
          api.getFinanceData(),
          api.getGoals()
        ]);
        setItems(financeData || []);
        setGoals(goalsData || []);
      } catch (err) {
        console.error('Failed to load finance data:', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const totalIncome = items.filter(i => i.type === 'income').reduce((s, i) => s + i.amount, 0);
  const totalExpense = items.filter(i => i.type === 'expense').reduce((s, i) => s + i.amount, 0);
  const savings = totalIncome - totalExpense;

  const handleAddItem = async () => {
    if (!newItem.category || !newItem.amount) return;
    const item = { ...newItem, amount: Number(newItem.amount), date: new Date().toISOString() };
    try {
      const res = await api.addFinanceItem(item);
      setItems([...items, res]);
      setNewItem({ category: '', amount: '', type: 'expense' });
    } catch (err) { console.error(err); }
  };

  const handleDeleteItem = async (id: string) => {
    try {
      await api.deleteFinanceItem(id);
      setItems(items.filter(i => i.id !== id));
    } catch (err) { console.error(err); }
  };

  return (
    <>
      <Sidebar />
      <main className="main-container">
        <TickerStrip />
        <div className="content-viewport">
          <div className="page-content">
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 32 }}>
              <div>
                <h1 style={{ fontSize: 36, marginBottom: 8 }}>Finance & <span className="text-green">Goals</span></h1>
                <p className="muted" style={{ fontSize: 12, letterSpacing: '0.1em' }}>CAPITAL MANAGEMENT • EXPENSE TRACKING • MILESTONES</p>
              </div>
              <div style={{ display: 'flex', gap: 4 }}>
                {(['overview', 'goals'] as const).map(t => (
                  <button key={t} onClick={() => setTab(t)} className="apex-btn" style={{
                    fontSize: 10, padding: '10px 24px',
                    ...(tab === t ? { background: 'rgba(0,255,136,0.1)', borderColor: 'var(--green)', color: 'var(--green)' } : {}),
                  }}>
                    {t.toUpperCase()}
                  </button>
                ))}
              </div>
            </div>

            {tab === 'overview' && (
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 380px', gap: 32, alignItems: 'start' }}>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 32 }}>
                  {/* Summary Cards */}
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16 }}>
                    {[
                      { label: 'MONTHLY INCOME', value: `₹${totalIncome.toLocaleString()}`, color: 'var(--green)' },
                      { label: 'TOTAL EXPENSES', value: `₹${totalExpense.toLocaleString()}`, color: 'var(--red)' },
                      { label: 'SAVINGS', value: `₹${savings.toLocaleString()}`, color: savings >= 0 ? 'var(--green)' : 'var(--red)' },
                    ].map((c, i) => (
                      <div key={i} className="apex-card">
                        <div style={{ fontSize: 9, color: 'var(--muted)', letterSpacing: '0.1em', marginBottom: 12 }}>{c.label}</div>
                        <div className="mono" style={{ fontSize: 24, fontWeight: 700, color: c.color }}>{c.value}</div>
                      </div>
                    ))}
                  </div>

                  {/* List of Items */}
                  <div className="apex-card">
                    <div style={{ fontSize: 14, fontWeight: 700, marginBottom: 24 }}>Transaction Ledger</div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                      {items.length === 0 && <div className="muted mono" style={{ fontSize: 12, textAlign: 'center', padding: 40 }}>NO TRANSACTIONS RECORDED</div>}
                      {items.map((item) => (
                        <div key={item.id} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '16px 20px', background: 'var(--surface2)', borderRadius: 4, border: '1px solid var(--border)' }}>
                          <div>
                            <div style={{ fontSize: 14, fontWeight: 700, color: 'var(--text)' }}>{item.category}</div>
                            <div className="mono" style={{ fontSize: 9, color: 'var(--muted)', marginTop: 4 }}>{new Date(item.date).toLocaleDateString()} • {item.type.toUpperCase()}</div>
                          </div>
                          <div style={{ display: 'flex', alignItems: 'center', gap: 20 }}>
                            <span className="mono" style={{ fontSize: 16, fontWeight: 700, color: item.type === 'income' ? 'var(--green)' : 'var(--red)' }}>
                              {item.type === 'income' ? '+' : '-'}₹{item.amount.toLocaleString()}
                            </span>
                            <button onClick={() => handleDeleteItem(item.id)} className="apex-btn" style={{ padding: '6px 12px', borderColor: 'transparent', color: 'var(--red)', fontSize: 16 }}>×</button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Add New Section */}
                <div className="apex-card" style={{ position: 'sticky', top: 32 }}>
                  <div style={{ fontSize: 14, fontWeight: 700, marginBottom: 24 }}>Log Entry</div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
                    <div>
                      <label style={{ fontSize: 9, color: 'var(--muted)', display: 'block', marginBottom: 8, letterSpacing: '0.1em' }}>CATEGORY</label>
                      <input className="apex-input" placeholder="e.g. Rent, Freelance" value={newItem.category} onChange={e => setNewItem({...newItem, category: e.target.value})} />
                    </div>
                    <div>
                      <label style={{ fontSize: 9, color: 'var(--muted)', display: 'block', marginBottom: 8, letterSpacing: '0.1em' }}>AMOUNT (₹)</label>
                      <input className="apex-input" type="number" placeholder="0.00" value={newItem.amount} onChange={e => setNewItem({...newItem, amount: e.target.value})} />
                    </div>
                    <div>
                      <label style={{ fontSize: 9, color: 'var(--muted)', display: 'block', marginBottom: 8, letterSpacing: '0.1em' }}>TYPE</label>
                      <div style={{ display: 'flex', gap: 8 }}>
                        {(['expense', 'income'] as const).map(t => (
                          <button key={t} onClick={() => setNewItem({...newItem, type: t})} className="apex-btn" style={{
                            flex: 1, fontSize: 10,
                            ...(newItem.type === t ? { background: t === 'income' ? 'rgba(0,255,136,0.1)' : 'rgba(255,59,92,0.1)', color: t === 'income' ? 'var(--green)' : 'var(--red)', borderColor: t === 'income' ? 'var(--green)' : 'var(--red)' } : {})
                          }}>
                            {t.toUpperCase()}
                          </button>
                        ))}
                      </div>
                    </div>
                    <button className="apex-btn primary" onClick={handleAddItem} style={{ marginTop: 12, justifyContent: 'center', padding: 14 }}>COMMIT TRANSACTION</button>
                  </div>
                </div>
              </div>
            )}

          {tab === 'goals' && (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(400px, 1fr))', gap: 24 }}>
              {goals.map((goal, i) => (
                <div key={i} className="apex-card" style={{ padding: '24px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 20 }}>
                    <div>
                      <div style={{ fontFamily: 'var(--font-head)', fontSize: 18, fontWeight: 700 }}>{goal.goal_name}</div>
                      <div style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: 'var(--muted)', marginTop: 4 }}>TARGET: ₹{goal.target_amount.toLocaleString()} BY {new Date(goal.target_date).toLocaleDateString()}</div>
                    </div>
                    <div style={{ fontFamily: 'var(--font-mono)', fontSize: 20, fontWeight: 800, color: 'var(--blue)' }}>{((goal.current / goal.target_amount) * 100).toFixed(0)}%</div>
                  </div>

                  <div style={{ height: 6, background: 'var(--surface2)', borderRadius: 3, overflow: 'hidden', marginBottom: 24 }}>
                    <div style={{ width: `${(goal.current / goal.target_amount) * 100}%`, height: '100%', background: 'linear-gradient(90deg, var(--blue), var(--green))' }} />
                  </div>

                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                    <div style={{ padding: 12, background: 'var(--surface2)', borderRadius: 4 }}>
                      <div style={{ fontSize: 9, color: 'var(--muted)' }}>CURRENT CAPITAL</div>
                      <div style={{ fontFamily: 'var(--font-mono)', fontSize: 16, fontWeight: 700, color: 'var(--text)', marginTop: 4 }}>₹{goal.current.toLocaleString()}</div>
                    </div>
                    <div style={{ padding: 12, background: 'var(--surface2)', borderRadius: 4 }}>
                      <div style={{ fontSize: 9, color: 'var(--muted)' }}>MONTHLY TARGET</div>
                      <div style={{ fontFamily: 'var(--font-mono)', fontSize: 16, fontWeight: 700, color: 'var(--green)', marginTop: 4 }}>₹{goal.monthly_target.toLocaleString()}</div>
                    </div>
                  </div>
                </div>
              ))}
              
              <button className="apex-card" style={{
                display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
                padding: '40px', borderStyle: 'dashed', background: 'transparent', cursor: 'pointer',
                color: 'var(--muted)', gap: 12,
              }}>
                <span style={{ fontSize: 32 }}>+</span>
                <span style={{ fontFamily: 'var(--font-head)', fontSize: 12, letterSpacing: '0.1em' }}>CREATE NEW FINANCIAL GOAL</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </main>
    </>
  );
}
