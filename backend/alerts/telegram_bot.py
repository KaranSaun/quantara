"""
APEX OS — Telegram Bot
Send alerts, morning picks, and weekly reviews.
"""

import logging
import httpx
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, TELEGRAM_ALERT_ENABLED

logger = logging.getLogger("apex.telegram")


async def send_message(text: str, parse_mode: str = "HTML") -> bool:
    if not TELEGRAM_ALERT_ENABLED or not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.warning("Telegram not configured or disabled")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": True,
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            logger.info("Telegram message sent successfully")
            return True
    except Exception as e:
        logger.error(f"Telegram send failed: {e}")
        return False


async def send_morning_pick(rec: dict) -> bool:
    if rec.get("action") == "NO_TRADE":
        msg = (
            "🔲 <b>APEX OS — No Trade Today</b>\n\n"
            f"📅 {rec.get('date', 'N/A')}\n"
            f"⚠️ {rec.get('reasoning', 'Conditions unclear')}\n\n"
            "<i>Discipline is doing nothing when there's nothing to do.</i>"
        )
    else:
        flags = rec.get("caution_flags", [])
        flags_text = "\n".join(f"  ⚠️ {f}" for f in flags) if flags else "  ✅ No flags"
        msg = (
            f"🎯 <b>APEX OS — Today's Pick</b>\n\n"
            f"📅 {rec.get('date', '')}\n"
            f"{'🟢' if rec.get('direction') == 'BULLISH' else '🔴'} "
            f"<b>{rec.get('recommended_strike', '')}</b>\n\n"
            f"📊 Direction: <b>{rec.get('direction', '')}</b>\n"
            f"💰 Entry: ₹{rec.get('entry_low', 0):.0f} – ₹{rec.get('entry_high', 0):.0f}\n"
            f"🛑 Stop Loss: ₹{rec.get('stop_loss', 0):.0f}\n"
            f"🎯 Target 1: ₹{rec.get('target1', 0):.0f}\n"
            f"🎯 Target 2: ₹{rec.get('target2', 0):.0f}\n"
            f"📐 R:R — 1:{rec.get('risk_reward', 0)}\n"
            f"🔒 Confidence: <b>{rec.get('confidence', 0)}%</b>\n"
            f"📦 Size: {rec.get('position_size', '')}\n\n"
            f"<b>Caution:</b>\n{flags_text}\n\n"
            f"<i>{rec.get('reasoning', '')[:400]}</i>"
        )
    return await send_message(msg)


async def send_alert(alert_type: str, message: str) -> bool:
    return await send_message(f"📡 <b>APEX ALERT</b>\n\n{message}")


async def send_weekly_review(review: dict) -> bool:
    perf = review.get("performance_summary", {})
    recs = review.get("specific_recommendations", [])
    recs_text = "\n".join(f"  • {r}" for r in recs[:3])
    msg = (
        "📊 <b>APEX OS — Weekly Review</b>\n\n"
        f"💰 P&L: ₹{perf.get('total_pnl', 0):,.0f}\n"
        f"✅ Win Rate: {perf.get('win_rate', 0):.0f}%\n"
        f"📐 Avg R:R: {perf.get('avg_rr_achieved', 0):.1f}\n"
        f"🎯 System Follow: {perf.get('followed_system_pct', 0):.0f}%\n\n"
        f"🔥 <b>Edge:</b> {review.get('strongest_edge', 'N/A')}\n"
        f"🩸 <b>Leak:</b> {review.get('biggest_leak', 'N/A')}\n\n"
        f"<b>Recommendations:</b>\n{recs_text}\n\n"
        f"🎯 <b>Next Week Focus:</b> {review.get('next_week_focus', 'N/A')}\n\n"
        f"💪 {review.get('encouragement', '')}"
    )
    return await send_message(msg)
