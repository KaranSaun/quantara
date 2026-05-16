"""
APEX OS — NSE Options Chain Fetcher
Fetches live options chain, OI, PCR, indices from NSE India.
Respectful scraping with 2-second delay between calls.
"""

import asyncio
import logging
import httpx
from datetime import date, datetime
from typing import Optional

from config import GUARDRAILS

logger = logging.getLogger("apex.nse_fetcher")

NSE_BASE = "https://www.nseindia.com"
NSE_API = "https://www.nseindia.com/api"

# NSE requires valid session cookies — we manage them here
_session_cookies: dict = {}
_last_request_time: float = 0


async def _get_nse_session(client: httpx.AsyncClient) -> None:
    """Establish NSE session by hitting the homepage first."""
    global _session_cookies
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    resp = await client.get(NSE_BASE, headers=headers, follow_redirects=True)
    _session_cookies = dict(resp.cookies)


async def _rate_limited_request(client: httpx.AsyncClient, url: str) -> dict:
    """Make rate-limited request to NSE API."""
    global _last_request_time
    
    # Enforce delay
    delay = GUARDRAILS.get("nse_request_delay", 2.0)
    now = asyncio.get_event_loop().time()
    elapsed = now - _last_request_time
    if elapsed < delay:
        await asyncio.sleep(delay - elapsed)
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
        "Referer": NSE_BASE,
    }
    
    resp = await client.get(url, headers=headers, cookies=_session_cookies)
    _last_request_time = asyncio.get_event_loop().time()
    
    if resp.status_code == 401:
        # Session expired, refresh
        await _get_nse_session(client)
        resp = await client.get(url, headers=headers, cookies=_session_cookies)
    
    resp.raise_for_status()
    return resp.json()


async def fetch_options_chain(index: str = "BANKNIFTY") -> dict:
    """
    Fetch full options chain from NSE.
    Returns: {spot_price, expiry_dates, strikes: [...]}
    """
    symbol = "BANKNIFTY" if index.upper() == "BANKNIFTY" else "NIFTY"
    url = f"{NSE_API}/option-chain-indices?symbol={symbol}"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        if not _session_cookies:
            await _get_nse_session(client)
        
        data = await _rate_limited_request(client, url)
    
    records = data.get("records", {})
    filtered = data.get("filtered", {})
    
    spot_price = records.get("underlyingValue", 0)
    expiry_dates = records.get("expiryDates", [])
    
    # Parse strike data
    strikes = []
    for row in filtered.get("data", []):
        strike_price = row.get("strikePrice", 0)
        expiry = row.get("expiryDate", "")
        
        ce = row.get("CE", {})
        pe = row.get("PE", {})
        
        if ce:
            strikes.append({
                "index": index.upper(),
                "expiry": expiry,
                "strike": strike_price,
                "option_type": "CE",
                "oi": ce.get("openInterest", 0),
                "oi_change": ce.get("changeinOpenInterest", 0),
                "iv": ce.get("impliedVolatility", 0),
                "ltp": ce.get("lastPrice", 0),
                "bid": ce.get("bidprice", 0),
                "ask": ce.get("askPrice", 0),
                "volume": ce.get("totalTradedVolume", 0),
                "timestamp": datetime.now().isoformat(),
            })
        
        if pe:
            strikes.append({
                "index": index.upper(),
                "expiry": expiry,
                "strike": strike_price,
                "option_type": "PE",
                "oi": pe.get("openInterest", 0),
                "oi_change": pe.get("changeinOpenInterest", 0),
                "iv": pe.get("impliedVolatility", 0),
                "ltp": pe.get("lastPrice", 0),
                "bid": pe.get("bidprice", 0),
                "ask": pe.get("askPrice", 0),
                "volume": pe.get("totalTradedVolume", 0),
                "timestamp": datetime.now().isoformat(),
            })
    
    return {
        "spot_price": spot_price,
        "expiry_dates": expiry_dates,
        "strikes": strikes,
        "total_ce_oi": filtered.get("CE", {}).get("totOI", 0),
        "total_pe_oi": filtered.get("PE", {}).get("totOI", 0),
        "pcr": (
            filtered.get("PE", {}).get("totOI", 0) / 
            max(filtered.get("CE", {}).get("totOI", 1), 1)
        ),
        "fetched_at": datetime.now().isoformat(),
    }


async def fetch_india_vix() -> float:
    """Fetch India VIX from NSE."""
    url = f"{NSE_API}/allIndices"
    async with httpx.AsyncClient(timeout=30.0) as client:
        if not _session_cookies:
            await _get_nse_session(client)
        data = await _rate_limited_request(client, url)
    
    for idx in data.get("data", []):
        if idx.get("index") == "INDIA VIX":
            return idx.get("last", 0)
    return 0.0


async def fetch_index_data(index: str = "BANKNIFTY") -> dict:
    """Fetch live index data — spot, change, high, low."""
    url = f"{NSE_API}/allIndices"
    async with httpx.AsyncClient(timeout=30.0) as client:
        if not _session_cookies:
            await _get_nse_session(client)
        data = await _rate_limited_request(client, url)
    
    target = "NIFTY BANK" if index.upper() == "BANKNIFTY" else "NIFTY 50"
    for idx in data.get("data", []):
        if idx.get("index") == target:
            return {
                "index": index.upper(),
                "last": idx.get("last", 0),
                "change": idx.get("variation", 0),
                "percent_change": idx.get("percentChange", 0),
                "open": idx.get("open", 0),
                "high": idx.get("high", 0),
                "low": idx.get("low", 0),
                "prev_close": idx.get("previousClose", 0),
                "timestamp": datetime.now().isoformat(),
            }
    return {}


async def fetch_fii_dii_data() -> dict:
    """Fetch FII/DII activity data from NSE."""
    url = f"{NSE_API}/fiidiiActivity/WEB"
    async with httpx.AsyncClient(timeout=30.0) as client:
        if not _session_cookies:
            await _get_nse_session(client)
        data = await _rate_limited_request(client, url)
    
    result = {
        "date": date.today().isoformat(),
        "fii_cash_net": 0,
        "dii_cash_net": 0,
        "is_provisional": True,
    }
    
    for entry in data:
        category = entry.get("category", "")
        if "FII" in category or "FPI" in category:
            result["fii_cash_net"] = entry.get("buyValue", 0) - entry.get("sellValue", 0)
        elif "DII" in category:
            result["dii_cash_net"] = entry.get("buyValue", 0) - entry.get("sellValue", 0)
    
    return result
