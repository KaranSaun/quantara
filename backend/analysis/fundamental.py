"""
APEX OS — Fundamental / Macro Analysis
FII/DII scoring, India VIX rules, global risk score.
"""

import logging
from dataclasses import dataclass

logger = logging.getLogger("apex.fundamental")

VIX_RULES = {
    "LOW": (0, 14, "Safe to sell options"),
    "NORMAL": (14, 20, "Standard strategies OK"),
    "ELEVATED": (20, 25, "CAUTION — prefer defined risk"),
    "HIGH": (25, 100, "HIGH VOLATILITY — consider staying flat"),
}


@dataclass
class MacroBias:
    direction: str
    strength: int
    fii_signal: str
    fii_net_3d: float
    vix_level: str
    vix_value: float
    vix_warning: str
    global_risk_score: float
    reasoning: str
    confidence: int


def fii_signal(fii_data: list[dict]) -> tuple[str, str]:
    if not fii_data:
        return "NEUTRAL", "No FII data available"
    cumulative = sum(d.get("fii_cash_net", 0) for d in fii_data)
    if cumulative > 0:
        return "BULLISH", f"FII net bought ₹{cumulative:.0f}Cr over {len(fii_data)} days"
    elif cumulative < 0:
        return "BEARISH", f"FII net sold ₹{abs(cumulative):.0f}Cr over {len(fii_data)} days"
    return "NEUTRAL", "FII flow is flat"


def vix_assessment(vix: float) -> tuple[str, str]:
    for level, (low, high, msg) in VIX_RULES.items():
        if low <= vix < high:
            return level, msg
    return "NORMAL", "VIX data unavailable"


def global_risk_score(
    sgx_change: float = 0, dow_change: float = 0,
    crude_change: float = 0, dxy_change: float = 0,
) -> tuple[float, str]:
    score = 5.0  # Neutral baseline
    notes = []

    if sgx_change < -0.5:
        score += abs(sgx_change) * 1.5
        notes.append(f"SGX Nifty down {sgx_change:.1f}%")
    elif sgx_change > 0.5:
        score -= sgx_change * 1.0

    if dow_change < -0.5:
        score += abs(dow_change) * 1.0
        notes.append(f"Dow futures down {dow_change:.1f}%")
    elif dow_change > 0.5:
        score -= dow_change * 0.5

    if crude_change > 2:
        score += crude_change * 0.8
        notes.append(f"Crude spiked {crude_change:.1f}%")

    if dxy_change > 0.5:
        score += dxy_change * 1.2
        notes.append(f"DXY up {dxy_change:.1f}%")

    score = max(0, min(10, score))
    summary = "; ".join(notes) if notes else "No major global risk signals"
    return round(score, 1), summary


async def analyze(
    fii_data: list[dict], vix: float, global_data: dict | None = None,
) -> MacroBias:
    fii_dir, fii_msg = fii_signal(fii_data)
    vix_lvl, vix_warn = vix_assessment(vix)

    sgx = global_data.get("sgx_nifty", {}).get("change_pct", 0) if global_data else 0
    dow = global_data.get("dow_futures", {}).get("change_pct", 0) if global_data else 0
    crude = global_data.get("crude_wti", {}).get("change_pct", 0) if global_data else 0
    dxy = global_data.get("dxy", {}).get("change_pct", 0) if global_data else 0
    risk, risk_note = global_risk_score(sgx, dow, crude, dxy)

    bull, bear = 0, 0
    if fii_dir == "BULLISH": bull += 2
    elif fii_dir == "BEARISH": bear += 2
    if vix < 16: bull += 1
    elif vix > 22: bear += 1
    if risk < 4: bull += 1
    elif risk > 6: bear += 1

    if bull > bear:
        direction, strength = "BULLISH", min(5, bull)
        confidence = min(80, 30 + bull * 12)
    elif bear > bull:
        direction, strength = "BEARISH", min(5, bear)
        confidence = min(80, 30 + bear * 12)
    else:
        direction, strength, confidence = "NEUTRAL", 1, 25

    fii_net = sum(d.get("fii_cash_net", 0) for d in fii_data)
    reasoning = (
        f"{fii_msg}. India VIX at {vix:.1f} ({vix_lvl} — {vix_warn}). "
        f"Global risk score: {risk}/10 — {risk_note}."
    )

    return MacroBias(
        direction=direction, strength=strength, fii_signal=fii_dir,
        fii_net_3d=fii_net, vix_level=vix_lvl, vix_value=vix,
        vix_warning=vix_warn, global_risk_score=risk,
        reasoning=reasoning, confidence=confidence)
