"""
APEX OS — Technical Analysis Module
Computes all TA indicators on BankNifty + Nifty.
Timeframes: 5m, 15m, 1H, 1D
"""

import logging
import numpy as np
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger("apex.technical")


@dataclass
class TechnicalBias:
    direction: str       # "BULLISH" | "BEARISH" | "NEUTRAL"
    strength: int        # 1-5
    key_level_support: float
    key_level_resistance: float
    vwap_position: str   # "above" | "below"
    ema_stack: str       # "aligned_bullish" | "aligned_bearish" | "mixed"
    momentum_state: str
    rsi: float
    macd_signal: str
    supertrend_signal: str
    atr: float
    reasoning: str
    confidence: int


def ema(data: list[float], period: int) -> list[float]:
    """Exponential Moving Average."""
    if len(data) < period:
        return [0.0] * len(data)
    multiplier = 2 / (period + 1)
    result = [0.0] * (period - 1)
    result.append(sum(data[:period]) / period)
    for i in range(period, len(data)):
        result.append((data[i] - result[-1]) * multiplier + result[-1])
    return result


def sma(data: list[float], period: int) -> list[float]:
    if len(data) < period:
        return [0.0] * len(data)
    result = [0.0] * (period - 1)
    for i in range(period - 1, len(data)):
        result.append(sum(data[i - period + 1:i + 1]) / period)
    return result


def rsi(closes: list[float], period: int = 14) -> float:
    if len(closes) < period + 1:
        return 50.0
    deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
    gains = [d if d > 0 else 0 for d in deltas]
    losses = [-d if d < 0 else 0 for d in deltas]
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return round(100 - (100 / (1 + rs)), 2)


def macd(closes: list[float], fast: int = 12, slow: int = 26, signal: int = 9) -> dict:
    ema_fast = ema(closes, fast)
    ema_slow = ema(closes, slow)
    if len(ema_fast) < slow or len(ema_slow) < slow:
        return {"line": 0, "signal": 0, "histogram": 0, "state": "NEUTRAL"}
    macd_line = [f - s for f, s in zip(ema_fast, ema_slow)]
    signal_line = ema(macd_line[slow-1:], signal)
    if not signal_line or signal_line[-1] == 0:
        return {"line": 0, "signal": 0, "histogram": 0, "state": "NEUTRAL"}
    hist = macd_line[-1] - signal_line[-1]
    state = "BULLISH" if hist > 0 else "BEARISH"
    return {
        "line": round(macd_line[-1], 2),
        "signal": round(signal_line[-1], 2),
        "histogram": round(hist, 2),
        "state": state,
    }


def bollinger_bands(closes: list[float], period: int = 20, std_dev: float = 2.0) -> dict:
    if len(closes) < period:
        return {"upper": 0, "middle": 0, "lower": 0}
    middle = sum(closes[-period:]) / period
    variance = sum((c - middle) ** 2 for c in closes[-period:]) / period
    std = variance ** 0.5
    return {
        "upper": round(middle + std_dev * std, 2),
        "middle": round(middle, 2),
        "lower": round(middle - std_dev * std, 2),
    }


def atr(highs: list[float], lows: list[float], closes: list[float], period: int = 14) -> float:
    if len(highs) < period + 1:
        return 0.0
    trs = []
    for i in range(1, len(highs)):
        tr = max(
            highs[i] - lows[i],
            abs(highs[i] - closes[i-1]),
            abs(lows[i] - closes[i-1])
        )
        trs.append(tr)
    return round(sum(trs[-period:]) / period, 2)


def supertrend(highs: list[float], lows: list[float], closes: list[float],
               period: int = 10, multiplier: float = 3.0) -> str:
    atr_val = atr(highs, lows, closes, period)
    if atr_val == 0 or not closes:
        return "NEUTRAL"
    hl2 = (highs[-1] + lows[-1]) / 2
    upper_band = hl2 + multiplier * atr_val
    lower_band = hl2 - multiplier * atr_val
    return "BULLISH" if closes[-1] > upper_band else "BEARISH" if closes[-1] < lower_band else "NEUTRAL"


def vwap(highs: list[float], lows: list[float], closes: list[float],
         volumes: list[int]) -> dict:
    if not volumes or sum(volumes) == 0:
        return {"vwap": 0, "upper_1s": 0, "lower_1s": 0}
    typical = [(h + l + c) / 3 for h, l, c in zip(highs, lows, closes)]
    cum_tp_vol = sum(t * v for t, v in zip(typical, volumes))
    cum_vol = sum(volumes)
    vwap_val = cum_tp_vol / cum_vol
    # Standard deviation bands
    variance = sum(v * (t - vwap_val) ** 2 for t, v in zip(typical, volumes)) / cum_vol
    std = variance ** 0.5
    return {
        "vwap": round(vwap_val, 2),
        "upper_1s": round(vwap_val + std, 2),
        "lower_1s": round(vwap_val - std, 2),
        "upper_2s": round(vwap_val + 2 * std, 2),
        "lower_2s": round(vwap_val - 2 * std, 2),
    }


def find_swing_points(highs: list[float], lows: list[float], lookback: int = 5) -> dict:
    swing_highs = []
    swing_lows = []
    for i in range(lookback, len(highs) - lookback):
        if highs[i] == max(highs[i-lookback:i+lookback+1]):
            swing_highs.append(highs[i])
        if lows[i] == min(lows[i-lookback:i+lookback+1]):
            swing_lows.append(lows[i])
    return {
        "swing_highs": sorted(swing_highs, reverse=True)[:3],
        "swing_lows": sorted(swing_lows)[:3],
    }


def detect_day_structure(highs: list[float], lows: list[float]) -> str:
    if len(highs) < 4:
        return "INSUFFICIENT_DATA"
    recent_highs = highs[-4:]
    recent_lows = lows[-4:]
    hh = all(recent_highs[i] > recent_highs[i-1] for i in range(1, len(recent_highs)))
    hl = all(recent_lows[i] > recent_lows[i-1] for i in range(1, len(recent_lows)))
    lh = all(recent_highs[i] < recent_highs[i-1] for i in range(1, len(recent_highs)))
    ll = all(recent_lows[i] < recent_lows[i-1] for i in range(1, len(recent_lows)))
    if hh and hl:
        return "HH_HL_BULLISH"
    elif lh and ll:
        return "LH_LL_BEARISH"
    return "MIXED"


async def analyze(ohlcv: list[dict], index: str = "BANKNIFTY") -> TechnicalBias:
    """
    Run full technical analysis on OHLCV data.
    Returns structured TechnicalBias with direction, levels, reasoning.
    """
    if len(ohlcv) < 30:
        return TechnicalBias(
            direction="NEUTRAL", strength=1,
            key_level_support=0, key_level_resistance=0,
            vwap_position="unknown", ema_stack="unknown",
            momentum_state="insufficient_data", rsi=50, macd_signal="NEUTRAL",
            supertrend_signal="NEUTRAL", atr=0,
            reasoning="Insufficient data for analysis. Need at least 30 candles.",
            confidence=10,
        )

    closes = [c["close"] for c in ohlcv]
    highs = [c["high"] for c in ohlcv]
    lows = [c["low"] for c in ohlcv]
    volumes = [c.get("volume", 0) for c in ohlcv]
    spot = closes[-1]

    # EMAs
    ema9 = ema(closes, 9)
    ema21 = ema(closes, 21)
    ema50 = ema(closes, 50)

    ema9_val = ema9[-1] if ema9 else 0
    ema21_val = ema21[-1] if ema21 else 0
    ema50_val = ema50[-1] if ema50 else 0

    if ema9_val > ema21_val > ema50_val:
        ema_stack_val = "aligned_bullish"
    elif ema9_val < ema21_val < ema50_val:
        ema_stack_val = "aligned_bearish"
    else:
        ema_stack_val = "mixed"

    # VWAP
    vwap_data = vwap(highs, lows, closes, volumes)
    vwap_pos = "above" if spot > vwap_data["vwap"] else "below"

    # RSI
    rsi_val = rsi(closes, 14)

    # MACD
    macd_data = macd(closes)

    # Supertrend
    st_signal = supertrend(highs, lows, closes)

    # ATR
    atr_val = atr(highs, lows, closes)

    # Swing points
    swings = find_swing_points(highs, lows)
    support = swings["swing_lows"][0] if swings["swing_lows"] else spot - atr_val * 2
    resistance = swings["swing_highs"][0] if swings["swing_highs"] else spot + atr_val * 2

    # Day structure
    structure = detect_day_structure(highs, lows)

    # Bollinger
    bb = bollinger_bands(closes)

    # ── Score direction ──
    bullish_score = 0
    bearish_score = 0

    if ema_stack_val == "aligned_bullish": bullish_score += 2
    elif ema_stack_val == "aligned_bearish": bearish_score += 2

    if vwap_pos == "above": bullish_score += 1
    else: bearish_score += 1

    if rsi_val > 60: bullish_score += 1
    elif rsi_val < 40: bearish_score += 1

    if macd_data["state"] == "BULLISH": bullish_score += 1
    else: bearish_score += 1

    if st_signal == "BULLISH": bullish_score += 1
    elif st_signal == "BEARISH": bearish_score += 1

    if "BULLISH" in structure: bullish_score += 1
    elif "BEARISH" in structure: bearish_score += 1

    total = bullish_score + bearish_score
    if bullish_score > bearish_score:
        direction = "BULLISH"
        strength = min(5, bullish_score)
        confidence = min(90, 40 + bullish_score * 10)
    elif bearish_score > bullish_score:
        direction = "BEARISH"
        strength = min(5, bearish_score)
        confidence = min(90, 40 + bearish_score * 10)
    else:
        direction = "NEUTRAL"
        strength = 1
        confidence = 30

    # Momentum state
    if rsi_val > 70:
        momentum = "OVERBOUGHT"
    elif rsi_val < 30:
        momentum = "OVERSOLD"
    elif macd_data["histogram"] > 0 and rsi_val > 50:
        momentum = "BULLISH_MOMENTUM"
    elif macd_data["histogram"] < 0 and rsi_val < 50:
        momentum = "BEARISH_MOMENTUM"
    else:
        momentum = "NEUTRAL"

    # Build reasoning
    reasoning = (
        f"{index} is trading at {spot:.0f}, {vwap_pos} VWAP ({vwap_data['vwap']:.0f}). "
        f"EMA stack is {ema_stack_val.replace('_', ' ')} "
        f"(EMA9={ema9_val:.0f}, EMA21={ema21_val:.0f}, EMA50={ema50_val:.0f}). "
        f"RSI at {rsi_val:.1f} indicates {momentum.lower().replace('_', ' ')}. "
        f"MACD histogram {macd_data['histogram']:.2f} is {macd_data['state'].lower()}. "
        f"Supertrend signal: {st_signal}. ATR(14): {atr_val:.0f}. "
        f"Key support at {support:.0f}, resistance at {resistance:.0f}."
    )

    return TechnicalBias(
        direction=direction,
        strength=strength,
        key_level_support=round(support, 2),
        key_level_resistance=round(resistance, 2),
        vwap_position=vwap_pos,
        ema_stack=ema_stack_val,
        momentum_state=momentum,
        rsi=rsi_val,
        macd_signal=macd_data["state"],
        supertrend_signal=st_signal,
        atr=atr_val,
        reasoning=reasoning,
        confidence=confidence,
    )
