"""
APEX OS — APScheduler Job Wiring
All Layer 1 scheduled jobs + market hours refresh loop.
"""

import logging
from datetime import date, datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger("apex.scheduler")

scheduler = AsyncIOScheduler(timezone="Asia/Kolkata")

# In-memory state for the current session
_session_state = {
    "oi_baseline": {},
    "market_open": False,
    "today_recommendation": None,
    "support": 0,
    "resistance": 0,
}


async def job_global_pulse():
    """06:00 AM — Fetch global markets data."""
    logger.info("⏰ Running: global_pulse")
    from data.global_fetcher import fetch_global_morning_data
    from db.supabase_client import save_market_snapshot
    data = await fetch_global_morning_data()
    await save_market_snapshot("global", data)
    logger.info("✓ Global pulse saved")


async def job_options_chain():
    """08:00 AM — Full options chain snapshot."""
    logger.info("⏰ Running: options_chain_snapshot")
    from data.nse_fetcher import fetch_options_chain
    from db.supabase_client import save_options_chain
    for index in ["BANKNIFTY", "NIFTY"]:
        chain = await fetch_options_chain(index)
        await save_options_chain(chain.get("strikes", []))
    logger.info("✓ Options chain snapshot saved")


async def job_news_pipeline():
    """08:30 AM — Fetch and score news."""
    logger.info("⏰ Running: news_pipeline")
    from data.news_fetcher import fetch_all_news
    from analysis.news_scorer import score_all_news
    from db.supabase_client import save_news_items
    raw = await fetch_all_news(hours=12)
    scored = await score_all_news(raw)
    await save_news_items(scored)
    logger.info(f"✓ {len(scored)} news items scored and saved")


async def job_strike_selector():
    """08:47 AM — Generate today's trade recommendation."""
    logger.info("⏰ Running: strike_selector")
    from data.nse_fetcher import fetch_options_chain, fetch_india_vix
    from data.price_fetcher import fetch_ohlcv
    from data.global_fetcher import fetch_global_morning_data
    from analysis import technical, sentiment, fundamental, news_scorer
    from analysis.strike_selector import generate_recommendation
    from db.supabase_client import (
        save_recommendation, get_fii_dii_last_n_days, get_recent_news
    )

    chain = await fetch_options_chain("BANKNIFTY")
    spot = chain.get("spot_price", 0)
    vix = await fetch_india_vix()
    ohlcv = await fetch_ohlcv("BANKNIFTY", period="5d", interval="15m")
    fii_data = await get_fii_dii_last_n_days(3)
    global_data = await fetch_global_morning_data()
    news_items = await get_recent_news(hours=12)

    tech = await technical.analyze(ohlcv, "BANKNIFTY")
    sent = await sentiment.analyze(chain)
    macro = await fundamental.analyze(fii_data, vix, global_data.get("global_markets"))
    news_bias = await news_scorer.aggregate_today(news_items)

    rec = await generate_recommendation(tech, sent, news_bias, macro, spot, chain, vix)
    rec_dict = rec.to_dict()
    await save_recommendation(rec_dict)

    _session_state["today_recommendation"] = rec_dict
    _session_state["support"] = tech.key_level_support
    _session_state["resistance"] = tech.key_level_resistance
    logger.info(f"✓ Recommendation: {rec.action} {rec.recommended_strike} @ {rec.confidence}%")


async def job_morning_telegram():
    """08:55 AM — Send morning pick via Telegram."""
    logger.info("⏰ Running: morning_telegram")
    from alerts.telegram_bot import send_morning_pick
    from db.supabase_client import get_today_recommendation
    rec = _session_state.get("today_recommendation") or await get_today_recommendation()
    if rec:
        await send_morning_pick(rec)
        logger.info("✓ Morning pick sent to Telegram")


async def job_market_open():
    """09:15 AM — Market open init."""
    logger.info("⏰ Market OPEN")
    from data.nse_fetcher import fetch_options_chain
    chain = await fetch_options_chain("BANKNIFTY")
    # Set OI baseline for the day
    baseline = {}
    for s in chain.get("strikes", []):
        key = f"{s['strike']}_{s['option_type']}"
        baseline[key] = s.get("oi", 0)
    _session_state["oi_baseline"] = baseline
    _session_state["market_open"] = True


async def job_live_refresh():
    """Every 5 min during 09:15-15:30 — Live data refresh + alerts."""
    if not _session_state.get("market_open"):
        return
    from config import is_market_hours
    if not is_market_hours():
        return

    logger.debug("⏰ Live refresh")
    from data.nse_fetcher import fetch_options_chain, fetch_india_vix
    from alerts.alert_engine import run_all_checks

    chain = await fetch_options_chain("BANKNIFTY")
    vix = await fetch_india_vix()

    await run_all_checks(
        chain_data=chain, vix=vix,
        support=_session_state.get("support", 0),
        resistance=_session_state.get("resistance", 0),
        active_trade=_session_state.get("today_recommendation"),
        oi_baseline=_session_state.get("oi_baseline"),
    )


async def job_eod():
    """15:30 PM — End of day snapshot."""
    logger.info("⏰ Running: eod_snapshot")
    _session_state["market_open"] = False
    from data.nse_fetcher import fetch_options_chain
    from db.supabase_client import save_market_snapshot
    for index in ["BANKNIFTY", "NIFTY"]:
        chain = await fetch_options_chain(index)
        await save_market_snapshot("eod", {"index": index, **chain})
    logger.info("✓ EOD snapshot saved")


async def job_fii_dii():
    """18:00 PM — Final FII/DII data."""
    logger.info("⏰ Running: fii_dii_final")
    from data.nse_fetcher import fetch_fii_dii_data
    from db.supabase_client import save_fii_dii
    data = await fetch_fii_dii_data()
    data["is_provisional"] = False
    await save_fii_dii(data)
    logger.info("✓ FII/DII final data saved")


async def job_crypto_forex():
    """20:00 PM — Evening crypto + forex update."""
    logger.info("⏰ Running: crypto_forex_update")
    from data.global_fetcher import fetch_eod_global_data
    from db.supabase_client import save_market_snapshot
    data = await fetch_eod_global_data()
    await save_market_snapshot("eod_global", data)
    logger.info("✓ Crypto/forex update saved")


async def job_weekly_review():
    """Sunday 8 PM — Weekly journal AI review."""
    logger.info("⏰ Running: weekly_review")
    import ai_router
    from prompts.chart_analysis import JOURNAL_REVIEW_PROMPT
    from db.supabase_client import get_journal_week, get_trades
    from alerts.telegram_bot import send_weekly_review
    from datetime import timedelta

    end = date.today()
    start = end - timedelta(days=7)
    journal = await get_journal_week(end)
    trades = await get_trades(start, end)

    journal_data = f"Journal: {journal}\nTrades: {trades}"
    prompt = JOURNAL_REVIEW_PROMPT.format(journal_data=journal_data)
    resp = await ai_router.analyze(prompt, task_type="reasoning", json_mode=True)
    review = resp.as_json() or {}
    await send_weekly_review(review)
    logger.info("✓ Weekly review sent")


def setup_scheduler():
    """Wire all scheduled jobs."""
    # Daily jobs
    scheduler.add_job(job_global_pulse, CronTrigger(hour=6, minute=0))
    scheduler.add_job(job_options_chain, CronTrigger(hour=8, minute=0))
    scheduler.add_job(job_news_pipeline, CronTrigger(hour=8, minute=30))
    scheduler.add_job(job_strike_selector, CronTrigger(hour=8, minute=47))
    scheduler.add_job(job_morning_telegram, CronTrigger(hour=8, minute=55))
    scheduler.add_job(job_market_open, CronTrigger(hour=9, minute=15, day_of_week="mon-fri"))
    scheduler.add_job(job_eod, CronTrigger(hour=15, minute=30, day_of_week="mon-fri"))
    scheduler.add_job(job_fii_dii, CronTrigger(hour=18, minute=0, day_of_week="mon-fri"))
    scheduler.add_job(job_crypto_forex, CronTrigger(hour=20, minute=0))

    # Live refresh every 5 min during market hours
    scheduler.add_job(job_live_refresh, "interval", minutes=5)

    # Weekly review
    scheduler.add_job(job_weekly_review, CronTrigger(day_of_week="sun", hour=20, minute=0))

    scheduler.start()
    logger.info("✓ Scheduler started with all jobs wired")
