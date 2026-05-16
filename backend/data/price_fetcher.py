"""
APEX OS — Price Fetcher
Historical OHLCV + live spot prices via yfinance.
Global indices, commodities, crypto.
"""

import logging
from datetime import date, datetime, timedelta
from typing import Optional
import yfinance as yf

logger = logging.getLogger("apex.price_fetcher")

# Ticker mappings
TICKERS = {
    "BANKNIFTY": "^NSEBANK",
    "NIFTY": "^NSEI",
    "SGX_NIFTY": "SGX=F",
    "DOW_FUTURES": "YM=F",
    "SP500_FUTURES": "ES=F",
    "NASDAQ_FUTURES": "NQ=F",
    "CRUDE_WTI": "CL=F",
    "CRUDE_BRENT": "BZ=F",
    "GOLD": "GC=F",
    "SILVER": "SI=F",
    "DXY": "DX-Y.NYB",
    "USDINR": "INR=X",
    "NIKKEI": "^N225",
    "HANG_SENG": "^HSI",
    "SHANGHAI": "000001.SS",
    "BITCOIN": "BTC-USD",
    "ETHEREUM": "ETH-USD",
    "SOLANA": "SOL-USD",
}


async def fetch_ohlcv(
    symbol: str = "BANKNIFTY",
    period: str = "1mo",
    interval: str = "15m",
) -> list[dict]:
    """Fetch OHLCV data for technical analysis."""
    ticker_symbol = TICKERS.get(symbol.upper(), symbol)
    
    try:
        ticker = yf.Ticker(ticker_symbol)
        df = ticker.history(period=period, interval=interval)
        
        if df.empty:
            logger.warning(f"No data for {symbol} ({ticker_symbol})")
            return []
        
        records = []
        for idx, row in df.iterrows():
            records.append({
                "timestamp": idx.isoformat(),
                "open": round(row["Open"], 2),
                "high": round(row["High"], 2),
                "low": round(row["Low"], 2),
                "close": round(row["Close"], 2),
                "volume": int(row.get("Volume", 0)),
            })
        
        return records
    except Exception as e:
        logger.error(f"Error fetching {symbol}: {e}")
        return []


async def fetch_live_price(symbol: str = "BANKNIFTY") -> dict:
    """Fetch current live price snapshot."""
    ticker_symbol = TICKERS.get(symbol.upper(), symbol)
    
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.fast_info
        
        return {
            "symbol": symbol.upper(),
            "price": round(info.last_price, 2) if info.last_price else 0,
            "prev_close": round(info.previous_close, 2) if info.previous_close else 0,
            "change": round(
                (info.last_price or 0) - (info.previous_close or 0), 2
            ),
            "change_pct": round(
                ((info.last_price or 0) - (info.previous_close or 0))
                / max(info.previous_close or 1, 1) * 100, 2
            ),
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error fetching live price for {symbol}: {e}")
        return {"symbol": symbol.upper(), "price": 0, "error": str(e)}


async def fetch_global_pulse() -> dict:
    """
    Fetch all global cues for morning briefing.
    SGX Nifty, Dow/S&P/NASDAQ futures, crude, gold, DXY, Asian markets.
    """
    global_symbols = [
        "SGX_NIFTY", "DOW_FUTURES", "SP500_FUTURES", "NASDAQ_FUTURES",
        "CRUDE_WTI", "CRUDE_BRENT", "GOLD", "SILVER", "DXY", "USDINR",
        "NIKKEI", "HANG_SENG", "SHANGHAI",
    ]
    
    results = {}
    for sym in global_symbols:
        price_data = await fetch_live_price(sym)
        results[sym.lower()] = price_data
    
    return {
        "type": "global_pulse",
        "data": results,
        "fetched_at": datetime.now().isoformat(),
    }


async def fetch_crypto_prices() -> dict:
    """Fetch crypto prices (Bitcoin, Ethereum, Solana)."""
    crypto_symbols = ["BITCOIN", "ETHEREUM", "SOLANA"]
    results = {}
    for sym in crypto_symbols:
        price_data = await fetch_live_price(sym)
        results[sym.lower()] = price_data
    
    return {
        "type": "crypto",
        "data": results,
        "fetched_at": datetime.now().isoformat(),
    }


async def fetch_historical_iv_range(
    symbol: str = "BANKNIFTY", days: int = 252
) -> dict:
    """Compute 52-week IV high/low using historical volatility as proxy."""
    data = await fetch_ohlcv(symbol, period="1y", interval="1d")
    if len(data) < 20:
        return {"iv_52w_high": 30.0, "iv_52w_low": 10.0}
    
    import numpy as np
    closes = [d["close"] for d in data]
    returns = np.diff(np.log(closes))
    
    # Rolling 20-day HV annualized
    window = 20
    hvs = []
    for i in range(window, len(returns)):
        hv = np.std(returns[i-window:i]) * np.sqrt(252) * 100
        hvs.append(hv)
    
    if not hvs:
        return {"iv_52w_high": 30.0, "iv_52w_low": 10.0}
    
    return {
        "iv_52w_high": round(max(hvs), 2),
        "iv_52w_low": round(min(hvs), 2),
        "iv_current": round(hvs[-1], 2),
    }
