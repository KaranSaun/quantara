"""
APEX OS — Alert Engine
Monitors 8 alert conditions every 5 minutes during market hours.
"""

import logging
from datetime import datetime
from typing import Optional
from alerts.telegram_bot import send_alert
from db.supabase_client import log_alert

logger = logging.getLogger("apex.alert_engine")

# Track previous state for cross-detection
_prev_state = {
    "pcr": None,
    "vix": None,
    "spot_banknifty": None,
    "spot_nifty": None,
}


async def check_pcr_cross(pcr: float) -> Optional[dict]:
    prev = _prev_state.get("pcr")
    _prev_state["pcr"] = pcr
    if prev is None:
        return None
    if prev < 1.3 and pcr >= 1.3:
        return {"type": "PCR_CROSS_BULLISH",
                "message": f"🟢 PCR crossed 1.3 → {pcr:.2f} | Bullish signal activated"}
    if prev > 0.7 and pcr <= 0.7:
        return {"type": "PCR_CROSS_BEARISH",
                "message": f"🔴 PCR dropped to {pcr:.2f} → Bearish signal activated"}
    return None


async def check_vix_spike(vix: float) -> Optional[dict]:
    prev = _prev_state.get("vix")
    _prev_state["vix"] = vix
    if prev is None or prev == 0:
        return None
    change_pct = abs(vix - prev) / prev * 100
    if change_pct > 5:
        direction = "surged" if vix > prev else "dropped"
        return {"type": "VIX_SPIKE",
                "message": f"⚠️ VIX ALERT: India VIX {direction} {change_pct:.1f}% to {vix:.1f} | Adjust risk"}
    return None


async def check_oi_spike(strikes: list[dict], baseline: dict) -> list[dict]:
    alerts = []
    for s in strikes:
        key = f"{s['strike']}_{s['option_type']}"
        base_oi = baseline.get(key, 0)
        if base_oi > 0:
            change_pct = (s.get("oi", 0) - base_oi) / base_oi * 100
            if abs(change_pct) > 15:
                alerts.append({
                    "type": "OI_SPIKE",
                    "message": f"⚡ OI SPIKE: {s.get('index', '')} {s['strike']} "
                               f"{s['option_type']} | OI {'+' if change_pct > 0 else ''}"
                               f"{change_pct:.0f}% in 5 min"
                })
        # Unusual OI > 1 lakh
        if s.get("oi", 0) > 100000:
            alerts.append({
                "type": "UNUSUAL_OI",
                "message": f"👁️ UNUSUAL OI: {s.get('index', '')} {s['strike']} "
                           f"{s['option_type']} | OI {s['oi']:,} contracts"
            })
    return alerts[:5]  # Cap at 5 to avoid spam


async def check_key_levels(
    spot: float, support: float, resistance: float, index: str = "BANKNIFTY"
) -> Optional[dict]:
    prev = _prev_state.get(f"spot_{index.lower()}")
    _prev_state[f"spot_{index.lower()}"] = spot
    if prev is None:
        return None
    if prev < resistance and spot >= resistance:
        return {"type": "KEY_LEVEL_BREACH",
                "message": f"📍 KEY LEVEL: {index} broke RESISTANCE at {resistance:.0f} | Now: {spot:.0f}"}
    if prev > support and spot <= support:
        return {"type": "KEY_LEVEL_BREACH",
                "message": f"📍 KEY LEVEL: {index} broke SUPPORT at {support:.0f} | Now: {spot:.0f}"}
    return None


async def check_sl_approaching(
    strike: str, ltp: float, sl: float
) -> Optional[dict]:
    if sl <= 0:
        return None
    distance_pct = (ltp - sl) / ltp * 100 if ltp > 0 else 100
    if 0 < distance_pct <= 5:
        return {"type": "SL_APPROACHING",
                "message": f"🚨 SL WARNING: {strike} LTP ₹{ltp:.0f} approaching SL ₹{sl:.0f} | Monitor closely"}
    return None


async def check_target_hit(
    strike: str, ltp: float, target1: float
) -> Optional[dict]:
    if target1 <= 0:
        return None
    if ltp >= target1:
        return {"type": "TARGET_HIT",
                "message": f"✅ TARGET 1 HIT: {strike} ₹{ltp:.0f} | Consider booking 50%, trail SL to entry"}
    return None


async def run_all_checks(
    chain_data: dict, vix: float,
    support: float, resistance: float,
    active_trade: dict | None = None,
    oi_baseline: dict | None = None,
) -> list[dict]:
    """Run all 8 alert conditions. Called every 5 min during market hours."""
    fired = []

    # PCR cross
    pcr = chain_data.get("pcr", 1.0)
    alert = await check_pcr_cross(pcr)
    if alert:
        fired.append(alert)

    # VIX spike
    alert = await check_vix_spike(vix)
    if alert:
        fired.append(alert)

    # OI spikes
    if oi_baseline:
        oi_alerts = await check_oi_spike(chain_data.get("strikes", []), oi_baseline)
        fired.extend(oi_alerts)

    # Key level breach
    spot = chain_data.get("spot_price", 0)
    if support and resistance:
        alert = await check_key_levels(spot, support, resistance)
        if alert:
            fired.append(alert)

    # Active trade alerts
    if active_trade:
        strike_name = active_trade.get("recommended_strike", "")
        # Find LTP for active strike
        for s in chain_data.get("strikes", []):
            strike_str = f"{s['strike']} {s['option_type']}"
            if strike_str == strike_name:
                ltp = s.get("ltp", 0)
                sl_alert = await check_sl_approaching(strike_name, ltp, active_trade.get("stop_loss", 0))
                if sl_alert:
                    fired.append(sl_alert)
                t1_alert = await check_target_hit(strike_name, ltp, active_trade.get("target1", 0))
                if t1_alert:
                    fired.append(t1_alert)
                break

    # Send all alerts
    for a in fired:
        await send_alert(a["type"], a["message"])
        await log_alert({
            "alert_type": a["type"],
            "message": a["message"],
            "data": {"pcr": pcr, "vix": vix, "spot": spot},
            "telegram_sent": True,
        })
        logger.info(f"ALERT FIRED: {a['type']} — {a['message']}")

    return fired
