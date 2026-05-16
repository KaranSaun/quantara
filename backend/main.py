"""
APEX OS — FastAPI Main Application
Routes, WebSocket, and API endpoints.
"""

import base64
import logging
from datetime import date, timedelta
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config import is_market_hours, TRADING_CAPITAL
from scheduler import setup_scheduler

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")
logger = logging.getLogger("apex.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 APEX OS starting...")
    setup_scheduler()
    yield
    logger.info("APEX OS shutting down")


app = FastAPI(title="APEX OS", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Pydantic Models ──
class TradeLogEntry(BaseModel):
    instrument: str
    strike: str
    direction: str
    entry_price: float
    exit_price: float = 0
    quantity: int = 1
    pnl: float = 0
    followed_system: bool = True
    deviation_reason: str = ""
    emotional_state: int = 3
    discipline_score: int = 3
    notes: str = ""

class JournalEntry(BaseModel):
    pre_market_notes: str = ""
    post_market_notes: str = ""
    market_conditions: str = ""
    lessons: str = ""
    emotional_state: int = 3
    discipline_score: int = 3

class FinanceEntry(BaseModel):
    category: str
    subcategory: str
    amount: float
    description: str = ""
    recurring: bool = False

class GoalInput(BaseModel):
    goal_name: str
    target_amount: float
    target_date: str
    current_capital: float = 0
    monthly_savings: float = 0
    risk_appetite: str = "moderate"

class ChatMessage(BaseModel):
    message: str


# ── Health ──
@app.get("/api/health")
async def health():
    return {"status": "operational", "market_open": is_market_hours()}


# ── Morning Briefing ──
@app.get("/api/morning/briefing")
async def morning_briefing():
    from db.supabase_client import get_today_recommendation, get_latest_snapshot
    rec = await get_today_recommendation()
    global_data = await get_latest_snapshot("global")
    return {
        "recommendation": rec,
        "global_data": global_data.get("data") if global_data else None,
        "market_open": is_market_hours(),
    }


# ── Live Market Data ──
@app.get("/api/live/spot")
async def live_spot():
    from data.nse_fetcher import fetch_index_data
    bn = await fetch_index_data("BANKNIFTY")
    nf = await fetch_index_data("NIFTY")
    return {"banknifty": bn, "nifty": nf}


@app.get("/api/live/options-chain/{index}")
async def live_options_chain(index: str = "BANKNIFTY"):
    from data.nse_fetcher import fetch_options_chain
    return await fetch_options_chain(index.upper())


@app.get("/api/live/vix")
async def live_vix():
    from data.nse_fetcher import fetch_india_vix
    vix = await fetch_india_vix()
    return {"vix": vix}


@app.get("/api/live/global")
async def live_global():
    from data.price_fetcher import fetch_global_pulse
    return await fetch_global_pulse()


# --- PORTFOLIO ---
@app.get("/api/portfolio/metrics")
async def get_portfolio_metrics():
    from finance.pnl_tracker import compute_metrics
    end = date.today()
    start = end - timedelta(days=30)
    try:
        return await compute_metrics(start, end)
    except Exception:
        # Fallback for fresh DB
        return {
            "total_pnl": 0, "win_rate": 0, "winners": 0,
            "total_trades": 0, "profit_factor": 0, "followed_system_pct": 0
        }

# --- FINANCE ---
@app.get("/api/finance/items")
async def get_finance_items():
    from db.supabase_client import get_finance_entries
    return await get_finance_entries()

@app.post("/api/finance/items")
async def add_finance_item(item: dict):
    from db.supabase_client import save_finance_entry
    # Map 'type' if coming from frontend with 'type' field
    return await save_finance_entry(item)

@app.delete("/api/finance/items/{item_id}")
async def delete_finance_item(item_id: str):
    from db.supabase_client import get_client
    supabase = get_client()
    supabase.table("life_finance").delete().eq("id", item_id).execute()
    return {"status": "ok"}

@app.get("/api/finance/goals")
async def get_goals():
    from db.supabase_client import get_goals
    return await get_goals()


# ── Chart Analysis ──
@app.post("/api/analyze-chart")
async def analyze_chart(file: UploadFile = File(...)):
    import ai_router
    from prompts.chart_analysis import CHART_ANALYSIS_PROMPT

    contents = await file.read()
    b64 = base64.b64encode(contents).decode("utf-8")

    try:
        resp = await ai_router.analyze(
            CHART_ANALYSIS_PROMPT, image_base64=b64,
            task_type="vision", json_mode=True)
        result = resp.as_json()
        if result:
            return {"analysis": result, "provider": resp.provider, "latency_ms": resp.latency_ms}
        return {"analysis": resp.text, "provider": resp.provider, "latency_ms": resp.latency_ms}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Portfolio & P&L ──
@app.get("/api/portfolio/metrics")
async def portfolio_metrics():
    from finance.pnl_tracker import compute_metrics
    end = date.today()
    start = end - timedelta(days=30)
    return await compute_metrics(start, end)


@app.get("/api/portfolio/pnl-series")
async def pnl_series(days: int = 30):
    from finance.pnl_tracker import daily_pnl_series
    return await daily_pnl_series(days)


@app.get("/api/portfolio/positions")
async def positions():
    try:
        from execution.broker_router import BrokerRouter
        router = BrokerRouter()
        pos = await router.get_positions()
        return [{"symbol": p.symbol, "qty": p.quantity, "avg": p.avg_price,
                 "ltp": p.ltp, "pnl": p.pnl} for p in pos]
    except Exception:
        return []


# ── Trade Journal ──
@app.post("/api/journal/trade")
async def log_trade(entry: TradeLogEntry):
    from db.supabase_client import save_trade
    return await save_trade({
        "date": date.today().isoformat(), **entry.model_dump()
    })


@app.post("/api/journal/entry")
async def save_journal(entry: JournalEntry):
    from db.supabase_client import save_journal as db_save
    return await db_save({
        "date": date.today().isoformat(), **entry.model_dump()
    })


@app.get("/api/journal/week")
async def journal_week():
    from db.supabase_client import get_journal_week
    return await get_journal_week(date.today())


@app.get("/api/journal/trades")
async def get_trades(days: int = 30):
    from db.supabase_client import get_trades as db_trades
    end = date.today()
    start = end - timedelta(days=days)
    return await db_trades(start, end)


# ── Finance ──
@app.post("/api/finance/entry")
async def add_finance(entry: FinanceEntry):
    from finance.life_tracker import add_entry
    return await add_entry(**entry.model_dump())


@app.get("/api/finance/monthly")
async def monthly_finance(year: int = 0, month: int = 0):
    from finance.life_tracker import get_monthly_summary
    y = year or date.today().year
    m = month or date.today().month
    return await get_monthly_summary(y, m)


@app.get("/api/finance/net-worth")
async def net_worth():
    from finance.life_tracker import get_net_worth
    return await get_net_worth()


# ── Goals ──
@app.post("/api/goals/plan")
async def create_goal_plan(goal: GoalInput):
    from finance.goal_planner import generate_plan
    plan = await generate_plan(**goal.model_dump())
    return plan


@app.get("/api/goals")
async def list_goals():
    from db.supabase_client import get_goals
    return await get_goals()


# ── AI Chat ──
@app.post("/api/chat")
async def ai_chat(msg: ChatMessage):
    import ai_router
    from db.supabase_client import get_today_recommendation, get_latest_snapshot, get_client

    rec = await get_today_recommendation()
    global_snap = await get_latest_snapshot("global")

    context = f"""You are QUANTARA OS AI assistant for an Indian options trader.
Today's recommendation: {rec}
Global data: {global_snap}
Capital: ₹{TRADING_CAPITAL:,.0f}
Market open: {is_market_hours()}

User question: {msg.message}
"""
    resp = await ai_router.analyze(context, task_type="reasoning")
    
    # Log to DB
    try:
        supabase = get_client()
        supabase.table("chat_history").insert([
            {"role": "user", "content": msg.message},
            {"role": "assistant", "content": resp.text}
        ]).execute()
    except Exception as e:
        logger.error(f"Failed to log chat: {e}")

    return {"response": resp.text, "provider": resp.provider}


# ── Alerts ──
@app.get("/api/alerts/recent")
async def recent_alerts():
    from db.supabase_client import get_client
    client = get_client()
    result = (client.table("alerts_log").select("*")
              .order("fired_at", desc=True).limit(20).execute())
    return result.data or []


# ── WebSocket for real-time push ──
@app.websocket("/ws/live")
async def websocket_live(ws: WebSocket):
    await ws.accept()
    import asyncio
    try:
        while True:
            if is_market_hours():
                from data.nse_fetcher import fetch_index_data
                bn = await fetch_index_data("BANKNIFTY")
                nf = await fetch_index_data("NIFTY")
                await ws.send_json({"type": "spot", "banknifty": bn, "nifty": nf})
            await asyncio.sleep(30)
    except Exception:
        pass


# ── Manual trigger endpoints (for testing) ──
@app.post("/api/admin/run-job/{job_name}")
async def run_job(job_name: str):
    from scheduler import (
        job_global_pulse, job_options_chain, job_news_pipeline,
        job_strike_selector, job_morning_telegram, job_eod,
        job_fii_dii, job_crypto_forex
    )
    jobs = {
        "global_pulse": job_global_pulse,
        "options_chain": job_options_chain,
        "news_pipeline": job_news_pipeline,
        "strike_selector": job_strike_selector,
        "morning_telegram": job_morning_telegram,
        "eod": job_eod,
        "fii_dii": job_fii_dii,
        "crypto_forex": job_crypto_forex,
    }
    fn = jobs.get(job_name)
    if not fn:
        raise HTTPException(404, f"Unknown job: {job_name}")
    await fn()
    return {"status": "completed", "job": job_name}
