"""
APEX OS — Sentiment Analysis (Options Intelligence)
PCR, OI analysis, max pain, IV rank.
"""

import logging
from dataclasses import dataclass

logger = logging.getLogger("apex.sentiment")


@dataclass
class SentimentBias:
    direction: str
    strength: int
    pcr: float
    pcr_interpretation: str
    max_pain: float
    iv_rank: float
    iv_strategy: str
    top_ce_oi_strikes: list
    top_pe_oi_strikes: list
    unusual_activity: list
    reasoning: str
    confidence: int


def compute_pcr(pe_oi: int, ce_oi: int) -> tuple[float, str]:
    if ce_oi == 0:
        return 1.0, "NEUTRAL"
    pcr = pe_oi / ce_oi
    if pcr > 1.3:
        return round(pcr, 2), "BULLISH — heavy put writing"
    elif pcr < 0.7:
        return round(pcr, 2), "BEARISH — call writing dominance"
    return round(pcr, 2), "NEUTRAL"


def compute_max_pain(strikes: list[dict], spot: float) -> float:
    strike_prices = sorted(set(s["strike"] for s in strikes))
    if not strike_prices:
        return spot
    min_pain = float("inf")
    mp_strike = spot
    for target in strike_prices:
        pain = 0
        for s in strikes:
            if s["option_type"] == "CE":
                pain += max(0, target - s["strike"]) * s.get("oi", 0)
            else:
                pain += max(0, s["strike"] - target) * s.get("oi", 0)
        if pain < min_pain:
            min_pain = pain
            mp_strike = target
    return mp_strike


def compute_iv_rank(iv: float, high: float, low: float) -> tuple[float, str]:
    if high == low:
        return 50.0, "Normal IV"
    rank = round(max(0, min(100, (iv - low) / (high - low) * 100)), 1)
    if rank > 50:
        return rank, "SELL options (elevated premium)"
    elif rank < 30:
        return rank, "BUY options (cheap premium)"
    return rank, "Either direction (normal IV)"


def find_top_oi(strikes: list[dict], otype: str, n: int = 5) -> list[dict]:
    f = sorted([s for s in strikes if s["option_type"] == otype],
               key=lambda x: x.get("oi", 0), reverse=True)
    return [{"strike": s["strike"], "oi": s.get("oi", 0),
             "oi_change": s.get("oi_change", 0), "iv": s.get("iv", 0),
             "ltp": s.get("ltp", 0)} for s in f[:n]]


def detect_unusual_oi(strikes: list[dict], thresh: float = 20.0) -> list[dict]:
    unusual = []
    for s in strikes:
        oi = s.get("oi", 0)
        chg = s.get("oi_change", 0)
        if oi > 0 and abs(chg) / oi * 100 > thresh:
            unusual.append({
                "strike": s["strike"], "option_type": s["option_type"],
                "oi": oi, "oi_change": chg,
                "change_pct": round(abs(chg) / oi * 100, 1),
                "type": "BUILDUP" if chg > 0 else "UNWINDING",
            })
    return sorted(unusual, key=lambda x: x["change_pct"], reverse=True)[:10]


async def analyze(chain_data: dict, iv_range: dict | None = None) -> SentimentBias:
    strikes = chain_data.get("strikes", [])
    spot = chain_data.get("spot_price", 0)
    ce_oi = chain_data.get("total_ce_oi", 0)
    pe_oi = chain_data.get("total_pe_oi", 0)

    pcr_val, pcr_interp = compute_pcr(pe_oi, ce_oi)
    max_pain_val = compute_max_pain(strikes, spot)
    iv_range = iv_range or {"iv_52w_high": 30, "iv_52w_low": 10, "iv_current": 15}
    iv_rank_val, iv_strat = compute_iv_rank(
        iv_range.get("iv_current", 15), iv_range.get("iv_52w_high", 30), iv_range.get("iv_52w_low", 10))
    top_ce = find_top_oi(strikes, "CE")
    top_pe = find_top_oi(strikes, "PE")
    unusual = detect_unusual_oi(strikes)

    bull, bear = 0, 0
    if pcr_val > 1.3: bull += 2
    elif pcr_val < 0.7: bear += 2
    if spot < max_pain_val: bull += 1
    elif spot > max_pain_val: bear += 1
    if top_pe and top_ce and top_pe[0]["oi"] > top_ce[0]["oi"]: bull += 1
    else: bear += 1

    if bull > bear:
        direction, strength, confidence = "BULLISH", min(5, bull), min(85, 35 + bull * 12)
    elif bear > bull:
        direction, strength, confidence = "BEARISH", min(5, bear), min(85, 35 + bear * 12)
    else:
        direction, strength, confidence = "NEUTRAL", 1, 30

    ce_r = top_ce[0]["strike"] if top_ce else "N/A"
    pe_s = top_pe[0]["strike"] if top_pe else "N/A"
    reasoning = (
        f"PCR at {pcr_val:.2f} — {pcr_interp}. "
        f"Max pain at {max_pain_val:.0f} (spot {spot:.0f}). "
        f"Highest CE OI at {ce_r} (resistance), PE OI at {pe_s} (support). "
        f"IV rank: {iv_rank_val:.0f}% — {iv_strat}."
    )

    return SentimentBias(
        direction=direction, strength=strength, pcr=pcr_val,
        pcr_interpretation=pcr_interp, max_pain=max_pain_val,
        iv_rank=iv_rank_val, iv_strategy=iv_strat,
        top_ce_oi_strikes=top_ce, top_pe_oi_strikes=top_pe,
        unusual_activity=unusual, reasoning=reasoning, confidence=confidence)
