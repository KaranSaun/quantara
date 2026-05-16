"""
APEX OS — Strike Selector Engine
THE CORE: Synthesizes all 4 biases into one trade recommendation.
"""

import logging
import random
from math import floor
from datetime import date, datetime, timedelta
from dataclasses import dataclass, field, asdict
from typing import Optional

import ai_router
from config import (
    TRADING_CAPITAL, RISK_PER_TRADE_PCT,
    LOT_SIZE_BANKNIFTY, GUARDRAILS
)
from analysis.technical import TechnicalBias
from analysis.sentiment import SentimentBias
from analysis.fundamental import MacroBias
from analysis.news_scorer import NewsBias

logger = logging.getLogger("apex.strike_selector")

REASONING_PROMPT = """You are an expert Indian options trader. Given today's analysis:

Technical: {technical}
Sentiment: {sentiment}
News: {news}
Macro: {macro}

Direction: {direction} | Confidence: {confidence}%
Strike: {strike} | Entry: ₹{entry} | SL: ₹{sl} | T1: ₹{t1} | T2: ₹{t2}

Write a 4-6 sentence trading thesis. Be specific with numbers. Include risk factors.
End with a discipline reminder. Do NOT use vague language."""


@dataclass
class TradeRecommendation:
    date: str
    action: str  # "TRADE" | "NO_TRADE"
    index: str
    expiry: str
    direction: str
    recommended_strike: str
    entry_low: float
    entry_high: float
    stop_loss: float
    target1: float
    target2: float
    risk_reward: float
    confidence: int
    position_size: str
    strategy_type: str
    technical_bias: str
    sentiment_bias: str
    news_bias: str
    macro_bias: str
    caution_flags: list[str]
    alternatives: list[dict]
    reasoning: str
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return asdict(self)


def next_expiry() -> date:
    """Find next Thursday (weekly expiry for BankNifty)."""
    today = date.today()
    days_ahead = 3 - today.weekday()  # Thursday = 3
    if days_ahead <= 0:
        days_ahead += 7
    return today + timedelta(days=days_ahead)


def count_aligned(
    tech: TechnicalBias, sent: SentimentBias,
    news: NewsBias, macro: MacroBias
) -> tuple[int, str]:
    dirs = [tech.direction, sent.direction, news.direction, macro.direction]
    bull = sum(1 for d in dirs if d == "BULLISH")
    bear = sum(1 for d in dirs if d == "BEARISH")
    if bull >= bear:
        return bull, "BULLISH"
    return bear, "BEARISH"


def generate_caution_flags(
    vix: float, expiry: date, global_risk: float
) -> list[str]:
    flags = []
    if vix > GUARDRAILS["vix_danger_level"]:
        flags.append(f"⚠️ VIX at {vix:.1f} — HIGH VOLATILITY. Consider staying flat.")
    elif vix > GUARDRAILS["vix_caution_level"]:
        flags.append(f"India VIX at {vix:.1f} — elevated. Use defined risk strategies.")
    days_to_exp = (expiry - date.today()).days
    if days_to_exp <= 1:
        flags.append("🔴 EXPIRY DAY — gamma risk elevated, wide spreads expected.")
    elif days_to_exp <= 2:
        flags.append("Expiry tomorrow — theta decay accelerating.")
    if global_risk > 7:
        flags.append(f"Global risk score {global_risk}/10 — external headwinds present.")
    return flags if flags else ["No flags"]


async def generate_recommendation(
    tech: TechnicalBias, sent: SentimentBias,
    news: NewsBias, macro: MacroBias,
    spot_price: float, chain_data: dict,
    vix: float = 15.0,
) -> TradeRecommendation:

    aligned, direction = count_aligned(tech, sent, news, macro)

    # Confidence scoring
    if aligned >= 4:
        confidence = random.randint(85, 95)
    elif aligned == 3:
        confidence = random.randint(65, 80)
    elif aligned == 2:
        confidence = random.randint(40, 60)
    else:
        return TradeRecommendation(
            date=date.today().isoformat(), action="NO_TRADE",
            index="BANKNIFTY", expiry=next_expiry().isoformat(),
            direction="NEUTRAL", recommended_strike="N/A",
            entry_low=0, entry_high=0, stop_loss=0,
            target1=0, target2=0, risk_reward=0,
            confidence=random.randint(15, 35),
            position_size="0 lots", strategy_type="FLAT",
            technical_bias=tech.reasoning, sentiment_bias=sent.reasoning,
            news_bias=news.reasoning, macro_bias=macro.reasoning,
            caution_flags=["Less than 2 biases aligned. Stay flat."],
            alternatives=[], reasoning="Conditions unclear. No trade today.")

    # Strike selection
    atm = round(spot_price / 100) * 100
    atr_offset = max(100, round(tech.atr / 100) * 100) if tech.atr > 0 else 200
    expiry = next_expiry()
    dte = (expiry - date.today()).days

    if dte <= 1:
        otm_offset = 100
    elif dte <= 3:
        otm_offset = min(200, atr_offset)
    else:
        otm_offset = min(400, atr_offset * 2)

    if direction == "BEARISH":
        strike = atm - otm_offset
        opt_type = "PE"
    else:
        strike = atm + otm_offset
        opt_type = "CE"

    # Find premium from chain
    premium = 0
    for s in chain_data.get("strikes", []):
        if s["strike"] == strike and s["option_type"] == opt_type:
            premium = s.get("ltp", 0)
            break
    if premium == 0:
        premium = 150  # Fallback estimate

    # Position sizing
    sl_price = round(premium * 0.65, 2)
    t1 = round(premium * 1.5, 2)
    t2 = round(premium * 2.0, 2)
    risk_per_trade = TRADING_CAPITAL * (RISK_PER_TRADE_PCT / 100)
    risk_per_lot = (premium - sl_price) * LOT_SIZE_BANKNIFTY
    lots = max(1, floor(risk_per_trade / risk_per_lot)) if risk_per_lot > 0 else 1
    rr = round((t2 - premium) / max(premium - sl_price, 1), 1)

    # Caution flags
    flags = generate_caution_flags(vix, expiry, macro.global_risk_score)
    if confidence < GUARDRAILS["confidence_threshold"]:
        flags.insert(0, "SPECULATIVE — consider half position size")

    # Alternatives
    alt_strike = atm if direction == "BEARISH" else atm
    alternatives = [
        {"strike": f"{alt_strike} {opt_type}",
         "reasoning": "ATM strike — higher delta, higher premium"},
        {"strategy": f"{'Bear Call' if direction == 'BEARISH' else 'Bull Put'} Spread {strike}/{strike + 500 if direction == 'BULLISH' else strike - 500}",
         "reasoning": "Defined risk spread, collect premium on elevated IV"},
    ]

    # AI reasoning
    try:
        prompt = REASONING_PROMPT.format(
            technical=tech.reasoning, sentiment=sent.reasoning,
            news=news.reasoning, macro=macro.reasoning,
            direction=direction, confidence=confidence,
            strike=f"{strike} {opt_type}", entry=premium,
            sl=sl_price, t1=t1, t2=t2)
        ai_resp = await ai_router.analyze(prompt, task_type="reasoning")
        reasoning_text = ai_resp.text
    except Exception as e:
        logger.warning(f"AI reasoning failed: {e}")
        reasoning_text = (
            f"{aligned} of 4 biases align {direction.lower()}. "
            f"Technical shows {tech.direction.lower()} bias with {tech.ema_stack} EMA stack. "
            f"Options data shows PCR at {sent.pcr:.2f} with max pain at {sent.max_pain:.0f}. "
            f"Trade with discipline, respect the stop at ₹{sl_price}.")

    entry_low = round(premium * 0.97, 2)
    entry_high = round(premium * 1.03, 2)
    if entry_high - entry_low > GUARDRAILS["max_entry_range"]:
        mid = (entry_low + entry_high) / 2
        entry_low = round(mid - 25, 2)
        entry_high = round(mid + 25, 2)

    return TradeRecommendation(
        date=date.today().isoformat(), action="TRADE",
        index="BANKNIFTY", expiry=expiry.isoformat(),
        direction=direction, recommended_strike=f"{strike} {opt_type}",
        entry_low=entry_low, entry_high=entry_high,
        stop_loss=sl_price, target1=t1, target2=t2,
        risk_reward=rr, confidence=confidence,
        position_size=f"{lots} lot(s) ({RISK_PER_TRADE_PCT}% capital risk)",
        strategy_type="Directional buy",
        technical_bias=tech.reasoning, sentiment_bias=sent.reasoning,
        news_bias=news.reasoning, macro_bias=macro.reasoning,
        caution_flags=flags, alternatives=alternatives,
        reasoning=reasoning_text)
