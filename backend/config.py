"""
APEX OS — Central Configuration
"""
import os
from pathlib import Path
from dotenv import load_dotenv

ENV_PATH = Path(__file__).parent.parent / ".env"
load_dotenv(ENV_PATH)

# ── AI Provider ──
AI_PROVIDER: str = os.getenv("ACTIVE_AI_PROVIDER", "gemini")

AI_PROVIDERS = {
    "gemini": {
        "api_key_env": "GEMINI_API_KEY",
        "model": "gemini-2.0-flash",
        "vision_model": "gemini-2.0-flash",
        "max_tokens": 8192,
        "rate_limit": 1500,
        "supports_vision": True,
        "base_url": "https://generativelanguage.googleapis.com/v1beta",
    },
    "groq": {
        "api_key_env": "GROQ_API_KEY",
        "model": "llama-3.3-70b-versatile",
        "vision_model": None,
        "max_tokens": 8192,
        "rate_limit": 14400,
        "supports_vision": False,
        "base_url": "https://api.groq.com/openai/v1",
    },
    "openrouter": {
        "api_key_env": "OPENROUTER_API_KEY",
        "model": "meta-llama/llama-3.3-70b-instruct:free",
        "vision_model": "google/gemini-2.0-flash-exp:free",
        "max_tokens": 4096,
        "rate_limit": 200,
        "supports_vision": True,
        "base_url": "https://openrouter.ai/api/v1",
    },
    "ollama": {
        "api_key_env": None,
        "model": "llama3.1:8b",
        "vision_model": "llava:13b",
        "max_tokens": 4096,
        "rate_limit": None,
        "supports_vision": True,
        "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
    },
    "claude": {
        "api_key_env": "ANTHROPIC_API_KEY",
        "model": "claude-sonnet-4-20250514",
        "vision_model": "claude-sonnet-4-20250514",
        "max_tokens": 8192,
        "rate_limit": None,
        "supports_vision": True,
        "base_url": "https://api.anthropic.com/v1",
    },
    "openai": {
        "api_key_env": "OPENAI_API_KEY",
        "model": "gpt-4o",
        "vision_model": "gpt-4o",
        "max_tokens": 8192,
        "rate_limit": None,
        "supports_vision": True,
        "base_url": "https://api.openai.com/v1",
    },
}

AI_PRIORITY_CHAINS = {
    "text": ["gemini", "groq", "openrouter", "ollama"],
    "vision": ["gemini", "openrouter", "claude", "openai", "ollama"],
    "fast": ["groq", "gemini", "openrouter"],
    "reasoning": ["claude", "openai", "gemini", "groq"],
}

# ── Database ──
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")

# ── Telegram ──
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
TELEGRAM_ALERT_ENABLED = os.getenv("TELEGRAM_ALERT_ENABLED", "true").lower() == "true"

# ── Brokers ──
ACTIVE_BROKERS = os.getenv("ACTIVE_BROKERS", "angel_one").split(",")

BROKER_CONFIGS = {
    "angel_one": {
        "client_id": os.getenv("ANGEL_ONE_CLIENT_ID", ""),
        "password": os.getenv("ANGEL_ONE_PASSWORD", ""),
        "totp_secret": os.getenv("ANGEL_ONE_TOTP_SECRET", ""),
    },
    "upstox": {
        "api_key": os.getenv("UPSTOX_API_KEY", ""),
        "secret": os.getenv("UPSTOX_SECRET", ""),
    },
    "dhan": {
        "client_id": os.getenv("DHAN_CLIENT_ID", ""),
        "access_token": os.getenv("DHAN_ACCESS_TOKEN", ""),
    },
}

# ── Trading ──
TRADING_CAPITAL = float(os.getenv("TRADING_CAPITAL", "100000"))
RISK_PER_TRADE_PCT = float(os.getenv("RISK_PER_TRADE_PCT", "2"))
LOT_SIZE_BANKNIFTY = 15
LOT_SIZE_NIFTY = 25
SCAN_TIME = os.getenv("SCAN_TIME", "08:45")
MARKET_OPEN_HOUR, MARKET_OPEN_MINUTE = 9, 15
MARKET_CLOSE_HOUR, MARKET_CLOSE_MINUTE = 15, 30

# ── News ──
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
RSS_FEEDS = {
    "economic_times": "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
    "moneycontrol": "https://www.moneycontrol.com/rss/marketreports.xml",
    "livemint": "https://www.livemint.com/rss/markets",
    "rbi": "https://rbi.org.in/scripts/rss.aspx",
    "ndtv_profit": "https://feeds.feedburner.com/ndtvprofit-latest",
    "reuters_india": "https://feeds.reuters.com/reuters/INtopNews",
}

# ── Guardrails ──
GUARDRAILS = {
    "auto_order": False,
    "confidence_threshold": 50,
    "vix_caution_level": 20,
    "vix_danger_level": 25,
    "expiry_day_warning": True,
    "max_entry_range": 50,
    "min_reasoning_sentences": 3,
    "log_all_api_keys": False,
    "rls_enabled": True,
    "rate_limit_nse": True,
    "nse_request_delay": 2.0,
}

# ── Schedule (IST) ──
SCHEDULE = {
    "global_pulse": "06:00",
    "options_chain_snapshot": "08:00",
    "news_pipeline": "08:30",
    "fii_dii_provisional": "09:00",
    "market_open_init": "09:15",
    "live_refresh_interval_min": 5,
    "eod_snapshot": "15:30",
    "fii_dii_final": "18:00",
    "crypto_forex_update": "20:00",
    "strike_selector_run": "08:47",
    "morning_telegram": "08:55",
    "weekly_review": "SUN-20:00",
}


def get_api_key(provider: str) -> str | None:
    env_var = AI_PROVIDERS.get(provider, {}).get("api_key_env")
    if env_var is None:
        return None
    return os.getenv(env_var, "")


def is_market_hours() -> bool:
    from datetime import datetime
    import pytz
    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist)
    if now.weekday() >= 5:
        return False
    market_open = now.replace(hour=MARKET_OPEN_HOUR, minute=MARKET_OPEN_MINUTE, second=0, microsecond=0)
    market_close = now.replace(hour=MARKET_CLOSE_HOUR, minute=MARKET_CLOSE_MINUTE, second=0, microsecond=0)
    return market_open <= now <= market_close
