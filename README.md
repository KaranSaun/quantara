# APEX OS — AI Trading & Financial Operating System
### Indian Retail Trader Edition (BankNifty / Nifty Options)

APEX OS is a production-grade, personal AI-powered command center designed for the high-precision needs of an Indian retail options trader. It synthesizes technical analysis, options sentiment (OI/PCR), global macro cues, and real-time news into actionable trade recommendations delivered directly to your dashboard and Telegram.

## 🚀 Key Features
- **AI-Driven Trade Recommendations**: Daily "Morning Pick" at 8:55 AM based on 4-bias alignment.
- **Universal AI Router**: Seamless fallback between Gemini, Groq, Claude, and local Ollama.
- **Live Market Intelligence**: Real-time OI heatmaps, PCR gauges, and India VIX monitoring.
- **Chart Analysis Vision**: Drop any chart screenshot for an instant AI-powered technical read.
- **Behavioral Journaling**: Weekly AI reviews of your trading psychology and discipline.
- **Life Finance Hub**: Track net worth, expenses, and AI-planned financial goals.

## 🛠️ Tech Stack
- **Backend**: FastAPI (Python 3.11+), APScheduler, Supabase (PostgreSQL).
- **Frontend**: Next.js 14 (App Router), Tailwind CSS, Framer Motion, Lightweight Charts.
- **Data**: NSE Python, yfinance, RSS feeds, NewsAPI.
- **Deployment**: Vercel (Frontend), Railway/DigitalOcean (Backend).

## 📦 Setup Instructions

### 1. Database Setup
1. Create a free project on [Supabase](https://supabase.com/).
2. Run the SQL migration script found in `backend/db/supabase_client.py` (MIGRATIONS constant) in the Supabase SQL Editor.

### 2. Backend Setup
1. `cd apex-os/backend`
2. `pip install -r requirements.txt`
3. Rename `.env.example` to `.env` and fill in your API keys (Gemini, Telegram, Supabase, etc.).
4. Start the server: `uvicorn main:app --reload`

### 3. Frontend Setup
1. `cd apex-os/frontend`
2. `npm install`
3. Start the dev server: `npm run dev`

## 📅 Daily Routine
- **08:47 AM**: System generates the daily analysis.
- **08:55 AM**: Telegram message arrives with the "Morning Pick".
- **09:15 AM**: Dashboard goes live; alerts fire based on price and OI triggers.
- **15:30 PM**: Market close; EOD snapshots captured.
- **Evening**: Log your journal entry and update personal finance data.

## 🛡️ Guardrails
- **No Auto-Orders**: System never places orders without explicit user confirmation.
- **Confidence Filter**: Recommendations below 50% confidence are flagged as speculative.
- **VIX Warning**: Automatic risk reduction warnings when India VIX > 20.

---
*Built for precision. Driven by intelligence.*
