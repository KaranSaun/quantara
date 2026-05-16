const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: { 'Content-Type': 'application/json', ...options?.headers },
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export const api = {
  // Morning
  getMorningBriefing: () => apiFetch<any>('/api/morning/briefing'),

  // Live
  getSpot: () => apiFetch<any>('/api/live/spot'),
  getOptionsChain: (index: string) => apiFetch<any>(`/api/live/options-chain/${index}`),
  getVix: () => apiFetch<any>('/api/live/vix'),
  getGlobal: () => apiFetch<any>('/api/live/global'),

  // Chart
  analyzeChart: async (file: File) => {
    const form = new FormData();
    form.append('file', file);
    const res = await fetch(`${API_BASE}/api/analyze-chart`, { method: 'POST', body: form });
    return res.json();
  },

  // Portfolio
  getMetrics: () => apiFetch<any>('/api/portfolio/metrics'),
  getPnlSeries: (days?: number) => apiFetch<any>(`/api/portfolio/pnl-series?days=${days || 30}`),
  getPositions: () => apiFetch<any>('/api/portfolio/positions'),

  // Journal
  logTrade: (data: any) => apiFetch<any>('/api/journal/trade', { method: 'POST', body: JSON.stringify(data) }),
  saveJournal: (data: any) => apiFetch<any>('/api/journal/entry', { method: 'POST', body: JSON.stringify(data) }),
  getJournalWeek: () => apiFetch<any>('/api/journal/week'),
  getTrades: (days?: number) => apiFetch<any>(`/api/journal/trades?days=${days || 30}`),

  // Finance
  getFinanceData: () => apiFetch<any>('/api/finance/monthly'),
  addFinanceItem: (data: any) => apiFetch<any>('/api/finance/entry', { method: 'POST', body: JSON.stringify(data) }),
  deleteFinanceItem: (id: string) => apiFetch<any>(`/api/finance/entry/${id}`, { method: 'DELETE' }),
  addFinance: (data: any) => apiFetch<any>('/api/finance/entry', { method: 'POST', body: JSON.stringify(data) }),
  getMonthly: (year?: number, month?: number) => apiFetch<any>(`/api/finance/monthly?year=${year || 0}&month=${month || 0}`),
  getNetWorth: () => apiFetch<any>('/api/finance/net-worth'),

  // Goals
  createGoal: (data: any) => apiFetch<any>('/api/goals/plan', { method: 'POST', body: JSON.stringify(data) }),
  getGoals: () => apiFetch<any>('/api/goals'),

  // Chat
  chat: (message: string) => apiFetch<any>('/api/chat', { method: 'POST', body: JSON.stringify({ message }) }),

  // Alerts
  getAlerts: () => apiFetch<any>('/api/alerts/recent'),

  // Health
  getHealth: () => apiFetch<any>('/api/health'),
};

// WebSocket
export function createLiveSocket(onMessage: (data: any) => void): WebSocket | null {
  const wsBase = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace('http', 'ws');
  try {
    const ws = new WebSocket(`${wsBase}/ws/live`);
    ws.onmessage = (event) => onMessage(JSON.parse(event.data));
    ws.onerror = () => {};
    return ws;
  } catch {
    return null;
  }
}
