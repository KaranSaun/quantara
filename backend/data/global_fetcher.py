"""
APEX OS — Global Data Fetcher
SGX Nifty, Dow futures, commodities, crypto, Fear & Greed.
"""

import logging
from datetime import datetime
import httpx
from data.price_fetcher import fetch_live_price, fetch_global_pulse, fetch_crypto_prices

logger = logging.getLogger("apex.global_fetcher")


async def fetch_fear_greed_index() -> dict:
    """Fetch Crypto Fear & Greed Index (alternative.me — free, no key)."""
    url = "https://api.alternative.me/fng/?limit=1"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()

        fng = data.get("data", [{}])[0]
        return {
            "value": int(fng.get("value", 50)),
            "classification": fng.get("value_classification", "Neutral"),
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Fear & Greed fetch failed: {e}")
        return {"value": 50, "classification": "Neutral", "error": str(e)}


async def fetch_global_morning_data() -> dict:
    """
    Complete morning global data package.
    Called at 06:00 AM IST.
    """
    pulse = await fetch_global_pulse()
    fng = await fetch_fear_greed_index()

    return {
        "type": "global_morning",
        "global_markets": pulse.get("data", {}),
        "fear_greed": fng,
        "fetched_at": datetime.now().isoformat(),
    }


async def fetch_eod_global_data() -> dict:
    """
    Evening crypto + forex update.
    Called at 20:00 PM IST.
    """
    crypto = await fetch_crypto_prices()

    forex_pairs = ["USDINR"]
    forex = {}
    for pair in forex_pairs:
        forex[pair.lower()] = await fetch_live_price(pair)

    fng = await fetch_fear_greed_index()

    return {
        "type": "eod_global",
        "crypto": crypto.get("data", {}),
        "forex": forex,
        "fear_greed": fng,
        "fetched_at": datetime.now().isoformat(),
    }
