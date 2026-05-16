"""
APEX OS — Supabase Client & Database Interface
Typed query helpers for all tables.
"""

import logging
from datetime import date, datetime
from typing import Any, Optional
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_SERVICE_KEY

logger = logging.getLogger("apex.db")

_client: Client | None = None


def get_client() -> Client:
    global _client
    if _client is None:
        if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
            raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")
        _client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    return _client


# ── Market Snapshots ──
async def save_market_snapshot(snapshot_type: str, data: dict) -> dict:
    client = get_client()
    row = {
        "snapshot_type": snapshot_type,
        "data": data,
        "timestamp": datetime.now().isoformat(),
    }
    result = client.table("market_snapshots").insert(row).execute()
    return result.data[0] if result.data else {}


async def get_latest_snapshot(snapshot_type: str) -> dict | None:
    client = get_client()
    result = (
        client.table("market_snapshots")
        .select("*")
        .eq("snapshot_type", snapshot_type)
        .order("timestamp", desc=True)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None


# ── Options Strikes ──
async def save_options_chain(strikes: list[dict]) -> int:
    client = get_client()
    if not strikes:
        return 0
    result = client.table("options_strikes").insert(strikes).execute()
    return len(result.data) if result.data else 0


async def get_options_chain(
    index: str, expiry: date, timestamp_after: datetime | None = None
) -> list[dict]:
    client = get_client()
    query = (
        client.table("options_strikes")
        .select("*")
        .eq("index", index)
        .eq("expiry", expiry.isoformat())
        .order("strike")
    )
    if timestamp_after:
        query = query.gte("timestamp", timestamp_after.isoformat())
    result = query.execute()
    return result.data or []


# ── News Items ──
async def save_news_items(items: list[dict]) -> int:
    client = get_client()
    if not items:
        return 0
    result = client.table("news_items").insert(items).execute()
    return len(result.data) if result.data else 0


async def get_recent_news(hours: int = 12, min_relevance: float = 3.0) -> list[dict]:
    client = get_client()
    cutoff = datetime.now().isoformat()
    result = (
        client.table("news_items")
        .select("*")
        .gte("relevance_score", min_relevance)
        .order("fetched_at", desc=True)
        .limit(50)
        .execute()
    )
    return result.data or []


# ── FII/DII ──
async def save_fii_dii(data: dict) -> dict:
    client = get_client()
    result = client.table("fii_dii").upsert(data, on_conflict="date").execute()
    return result.data[0] if result.data else {}


async def get_fii_dii_last_n_days(n: int = 3) -> list[dict]:
    client = get_client()
    result = (
        client.table("fii_dii")
        .select("*")
        .order("date", desc=True)
        .limit(n)
        .execute()
    )
    return result.data or []


# ── Trade Recommendations ──
async def save_recommendation(rec: dict) -> dict:
    client = get_client()
    rec["generated_at"] = datetime.now().isoformat()
    result = client.table("trade_recommendations").insert(rec).execute()
    return result.data[0] if result.data else {}


async def get_today_recommendation() -> dict | None:
    client = get_client()
    today = date.today().isoformat()
    result = (
        client.table("trade_recommendations")
        .select("*")
        .gte("generated_at", f"{today}T00:00:00")
        .order("generated_at", desc=True)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None


# ── Trades Log ──
async def save_trade(trade: dict) -> dict:
    client = get_client()
    result = client.table("trades_log").insert(trade).execute()
    return result.data[0] if result.data else {}


async def get_trades(start_date: date, end_date: date) -> list[dict]:
    client = get_client()
    result = (
        client.table("trades_log")
        .select("*")
        .gte("date", start_date.isoformat())
        .lte("date", end_date.isoformat())
        .order("date", desc=True)
        .execute()
    )
    return result.data or []


# ── Journal ──
async def save_journal(entry: dict) -> dict:
    client = get_client()
    result = client.table("journal_entries").upsert(entry, on_conflict="date").execute()
    return result.data[0] if result.data else {}


async def get_journal_week(end_date: date) -> list[dict]:
    from datetime import timedelta
    start = end_date - timedelta(days=7)
    client = get_client()
    result = (
        client.table("journal_entries")
        .select("*")
        .gte("date", start.isoformat())
        .lte("date", end_date.isoformat())
        .order("date")
        .execute()
    )
    return result.data or []


# ── Life Finance ──
async def save_finance_entry(entry: dict) -> dict:
    client = get_client()
    result = client.table("life_finance").insert(entry).execute()
    return result.data[0] if result.data else {}


async def get_finance_entries(category: str | None = None) -> list[dict]:
    client = get_client()
    query = client.table("life_finance").select("*").order("date", desc=True)
    if category:
        query = query.eq("category", category)
    result = query.limit(200).execute()
    return result.data or []


# ── Goals ──
async def save_goal(goal: dict) -> dict:
    client = get_client()
    result = client.table("goals").upsert(goal).execute()
    return result.data[0] if result.data else {}


async def get_goals() -> list[dict]:
    client = get_client()
    result = client.table("goals").select("*").order("created_at", desc=True).execute()
    return result.data or []


# ── Alerts ──
async def log_alert(alert: dict) -> dict:
    client = get_client()
    alert["fired_at"] = datetime.now().isoformat()
    result = client.table("alerts_log").insert(alert).execute()
    return result.data[0] if result.data else {}


# ── SQL Migrations ──
MIGRATIONS = """
-- Run these in Supabase SQL Editor

CREATE TABLE IF NOT EXISTS market_snapshots (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  timestamp timestamptz NOT NULL DEFAULT now(),
  snapshot_type text,
  data jsonb NOT NULL
);

CREATE TABLE IF NOT EXISTS options_strikes (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  timestamp timestamptz NOT NULL DEFAULT now(),
  index text NOT NULL,
  expiry date NOT NULL,
  strike int NOT NULL,
  option_type text NOT NULL,
  oi bigint, oi_change bigint, iv float,
  ltp float, bid float, ask float, volume bigint
);

CREATE TABLE IF NOT EXISTS news_items (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  fetched_at timestamptz NOT NULL DEFAULT now(),
  source text, headline text, url text,
  relevance_score float, direction text, urgency text,
  banking_impact float, raw_sentiment jsonb
);

CREATE TABLE IF NOT EXISTS fii_dii (
  date date PRIMARY KEY,
  fii_cash_net float, fii_fo_net float,
  dii_cash_net float, dii_fo_net float,
  is_provisional boolean DEFAULT false
);

CREATE TABLE IF NOT EXISTS trade_recommendations (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  generated_at timestamptz NOT NULL DEFAULT now(),
  index text, expiry date, direction text,
  strike text, entry_low float, entry_high float,
  stop_loss float, target1 float, target2 float,
  risk_reward float, confidence int,
  technical_bias text, sentiment_bias text,
  news_bias text, macro_bias text,
  reasoning text, caution_flags jsonb,
  strategy_type text, position_size text
);

CREATE TABLE IF NOT EXISTS trades_log (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  date date NOT NULL,
  recommendation_id uuid REFERENCES trade_recommendations(id),
  instrument text, strike text, direction text,
  entry_price float, exit_price float,
  quantity int, pnl float, brokerage float,
  followed_system boolean, deviation_reason text,
  emotional_state int CHECK (emotional_state BETWEEN 1 AND 5),
  discipline_score int CHECK (discipline_score BETWEEN 1 AND 5),
  notes text
);

CREATE TABLE IF NOT EXISTS journal_entries (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  date date NOT NULL UNIQUE,
  pre_market_notes text, post_market_notes text,
  market_conditions text, lessons text,
  emotional_state int, discipline_score int,
  ai_weekly_review text, ai_reviewed_at timestamptz
);

CREATE TABLE IF NOT EXISTS life_finance (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  date timestamptz NOT NULL DEFAULT now(),
  category text,
  amount float NOT NULL,
  type text CHECK (type IN ('income', 'expense')),
  description text
);

CREATE TABLE IF NOT EXISTS goals (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at timestamptz DEFAULT now(),
  goal_name text NOT NULL,
  target_amount float NOT NULL,
  target_date date,
  current float DEFAULT 0,
  monthly_target float DEFAULT 0,
  risk_appetite text,
  ai_plan jsonb,
  last_reviewed date
);

CREATE TABLE IF NOT EXISTS chat_history (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at timestamptz DEFAULT now(),
  role text CHECK (role IN ('user', 'assistant')),
  content text NOT NULL,
  context_metadata jsonb
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_snapshots_type_time ON market_snapshots(snapshot_type, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_options_index_expiry ON options_strikes(index, expiry, strike);
CREATE INDEX IF NOT EXISTS idx_news_time ON news_items(fetched_at DESC);
CREATE INDEX IF NOT EXISTS idx_trades_date ON trades_log(date DESC);
CREATE INDEX IF NOT EXISTS idx_alerts_time ON alerts_log(fired_at DESC);
CREATE INDEX IF NOT EXISTS idx_chat_time ON chat_history(created_at DESC);

-- Enable RLS on all tables
ALTER TABLE market_snapshots ENABLE ROW LEVEL SECURITY;
ALTER TABLE options_strikes ENABLE ROW LEVEL SECURITY;
ALTER TABLE news_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE fii_dii ENABLE ROW LEVEL SECURITY;
ALTER TABLE trade_recommendations ENABLE ROW LEVEL SECURITY;
ALTER TABLE trades_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE journal_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE life_finance ENABLE ROW LEVEL SECURITY;
ALTER TABLE goals ENABLE ROW LEVEL SECURITY;
ALTER TABLE alerts_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_history ENABLE ROW LEVEL SECURITY;
"""
