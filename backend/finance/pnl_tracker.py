"""
APEX OS — P&L Tracker
Trade P&L aggregation, metrics, and performance analytics.
"""

import logging
from datetime import date, timedelta
from db.supabase_client import get_trades

logger = logging.getLogger("apex.pnl_tracker")


async def compute_metrics(start: date, end: date) -> dict:
    trades = await get_trades(start, end)
    if not trades:
        return {
            "total_pnl": 0, "win_rate": 0, "total_trades": 0,
            "winners": 0, "losers": 0, "avg_rr": 0,
            "max_win": 0, "max_loss": 0, "win_streak": 0,
            "lose_streak": 0, "avg_win": 0, "avg_loss": 0,
            "profit_factor": 0, "followed_system_pct": 0,
        }

    pnls = [t.get("pnl", 0) for t in trades]
    winners = [p for p in pnls if p > 0]
    losers = [p for p in pnls if p < 0]

    # Streaks
    win_streak = lose_streak = cur_w = cur_l = 0
    for p in pnls:
        if p > 0:
            cur_w += 1
            cur_l = 0
            win_streak = max(win_streak, cur_w)
        elif p < 0:
            cur_l += 1
            cur_w = 0
            lose_streak = max(lose_streak, cur_l)

    followed = [t for t in trades if t.get("followed_system")]
    gross_profit = sum(winners) if winners else 0
    gross_loss = abs(sum(losers)) if losers else 1

    return {
        "total_pnl": round(sum(pnls), 2),
        "win_rate": round(len(winners) / max(len(trades), 1) * 100, 1),
        "total_trades": len(trades),
        "winners": len(winners),
        "losers": len(losers),
        "avg_rr": round(
            (sum(winners) / max(len(winners), 1)) / max(abs(sum(losers) / max(len(losers), 1)), 1), 2
        ) if losers else 0,
        "max_win": round(max(winners), 2) if winners else 0,
        "max_loss": round(min(losers), 2) if losers else 0,
        "win_streak": win_streak,
        "lose_streak": lose_streak,
        "avg_win": round(sum(winners) / max(len(winners), 1), 2),
        "avg_loss": round(sum(losers) / max(len(losers), 1), 2),
        "profit_factor": round(gross_profit / max(gross_loss, 1), 2),
        "followed_system_pct": round(len(followed) / max(len(trades), 1) * 100, 1),
    }


async def daily_pnl_series(days: int = 30) -> list[dict]:
    end = date.today()
    start = end - timedelta(days=days)
    trades = await get_trades(start, end)

    daily = {}
    for t in trades:
        d = t.get("date", "")
        if d not in daily:
            daily[d] = 0
        daily[d] += t.get("pnl", 0)

    return [
        {"date": d, "pnl": round(v, 2), "cumulative": 0}
        for d, v in sorted(daily.items())
    ]


async def weekly_summary() -> dict:
    end = date.today()
    start = end - timedelta(days=7)
    return await compute_metrics(start, end)
