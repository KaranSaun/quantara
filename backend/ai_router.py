"""
APEX OS — Universal AI Router
Every feature calls this. Never hardcode providers in business logic.
Supports: gemini, groq, openrouter, ollama, claude, openai
Auto-fallback on quota/timeout errors.
"""

import json
import base64
import logging
import httpx
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from config import (
    AI_PROVIDER, AI_PROVIDERS, AI_PRIORITY_CHAINS, get_api_key
)

logger = logging.getLogger("apex.ai_router")


class QuotaError(Exception):
    pass

class TimeoutError(Exception):
    pass

class AllProvidersFailedError(Exception):
    pass


@dataclass
class AIResponse:
    text: str
    provider: str
    model: str
    tokens_used: int = 0
    latency_ms: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    raw_json: Optional[dict] = None

    def as_json(self) -> dict | None:
        """Try to parse text as JSON."""
        if self.raw_json:
            return self.raw_json
        try:
            # Handle markdown code blocks
            text = self.text.strip()
            if text.startswith("```"):
                lines = text.split("\n")
                text = "\n".join(lines[1:-1])
            return json.loads(text)
        except (json.JSONDecodeError, IndexError):
            return None


def get_priority_chain(task_type: str = "text") -> list[str]:
    """Get provider chain, starting with configured primary."""
    chain = AI_PRIORITY_CHAINS.get(task_type, AI_PRIORITY_CHAINS["text"])
    # Put the configured provider first
    if AI_PROVIDER in chain:
        chain = [AI_PROVIDER] + [p for p in chain if p != AI_PROVIDER]
    else:
        chain = [AI_PROVIDER] + chain
    return chain


async def _call_gemini(prompt: str, image_b64: str | None, config: dict) -> str:
    """Call Google Gemini API."""
    api_key = get_api_key("gemini")
    if not api_key:
        raise QuotaError("No Gemini API key")

    model = config["vision_model"] if image_b64 else config["model"]
    url = f"{config['base_url']}/models/{model}:generateContent?key={api_key}"

    parts = [{"text": prompt}]
    if image_b64:
        parts.append({
            "inline_data": {
                "mime_type": "image/png",
                "data": image_b64
            }
        })

    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "maxOutputTokens": config["max_tokens"],
            "temperature": 0.3,
        }
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(url, json=payload)
        if resp.status_code == 429:
            raise QuotaError("Gemini quota exceeded")
        resp.raise_for_status()
        data = resp.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]


async def _call_openai_compatible(
    prompt: str, image_b64: str | None, config: dict, provider: str
) -> str:
    """Call OpenAI-compatible API (Groq, OpenRouter, OpenAI)."""
    api_key = get_api_key(provider)
    if not api_key:
        raise QuotaError(f"No {provider} API key")

    model = config["vision_model"] if image_b64 and config.get("supports_vision") else config["model"]
    url = f"{config['base_url']}/chat/completions"

    messages = []
    if image_b64 and config.get("supports_vision"):
        messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_b64}"}}
            ]
        })
    else:
        messages.append({"role": "user", "content": prompt})

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    if provider == "openrouter":
        headers["HTTP-Referer"] = "https://apex-os.local"
        headers["X-Title"] = "APEX OS"

    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": config["max_tokens"],
        "temperature": 0.3,
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(url, json=payload, headers=headers)
        if resp.status_code == 429:
            raise QuotaError(f"{provider} quota exceeded")
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]


async def _call_claude(prompt: str, image_b64: str | None, config: dict) -> str:
    """Call Anthropic Claude API."""
    api_key = get_api_key("claude")
    if not api_key:
        raise QuotaError("No Claude API key")

    url = f"{config['base_url']}/messages"
    content = []
    if image_b64:
        content.append({
            "type": "image",
            "source": {"type": "base64", "media_type": "image/png", "data": image_b64}
        })
    content.append({"type": "text", "text": prompt})

    headers = {
        "x-api-key": api_key,
        "content-type": "application/json",
        "anthropic-version": "2023-06-01",
    }
    payload = {
        "model": config["model"],
        "max_tokens": config["max_tokens"],
        "messages": [{"role": "user", "content": content}],
        "temperature": 0.3,
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(url, json=payload, headers=headers)
        if resp.status_code == 429:
            raise QuotaError("Claude quota exceeded")
        resp.raise_for_status()
        data = resp.json()
        return data["content"][0]["text"]


async def _call_ollama(prompt: str, image_b64: str | None, config: dict) -> str:
    """Call local Ollama instance."""
    model = config["vision_model"] if image_b64 else config["model"]
    url = f"{config['base_url']}/api/generate"

    payload = {"model": model, "prompt": prompt, "stream": False}
    if image_b64:
        payload["images"] = [image_b64]

    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data["response"]


PROVIDER_CALLERS = {
    "gemini": _call_gemini,
    "groq": lambda p, i, c: _call_openai_compatible(p, i, c, "groq"),
    "openrouter": lambda p, i, c: _call_openai_compatible(p, i, c, "openrouter"),
    "openai": lambda p, i, c: _call_openai_compatible(p, i, c, "openai"),
    "claude": _call_claude,
    "ollama": _call_ollama,
}


async def call_provider(provider: str, prompt: str, image_b64: str | None = None) -> str:
    """Call a specific AI provider."""
    config = AI_PROVIDERS.get(provider)
    if not config:
        raise ValueError(f"Unknown provider: {provider}")

    # Skip if vision requested but not supported
    if image_b64 and not config.get("supports_vision"):
        raise QuotaError(f"{provider} doesn't support vision")

    caller = PROVIDER_CALLERS.get(provider)
    if not caller:
        raise ValueError(f"No caller for provider: {provider}")

    return await caller(prompt, image_b64, config)


async def analyze(
    prompt: str,
    image_base64: str | None = None,
    task_type: str = "text",
    fallback: bool = True,
    json_mode: bool = False,
) -> AIResponse:
    """
    Universal AI analysis entry point.
    Every feature in APEX OS calls this — never hardcode providers.
    
    Args:
        prompt: The prompt to send
        image_base64: Optional base64-encoded image for vision tasks
        task_type: "text" | "vision" | "fast" | "reasoning"
        fallback: Whether to try next provider on failure
        json_mode: If True, append JSON instruction to prompt
    """
    if image_base64:
        task_type = "vision"

    if json_mode:
        prompt += "\n\nRespond ONLY with valid JSON. No markdown, no preamble."

    providers = get_priority_chain(task_type)
    errors = []

    for provider in providers:
        config = AI_PROVIDERS.get(provider, {})
        start = datetime.now()
        try:
            logger.info(f"Calling {provider} ({config.get('model', '?')}) for {task_type}")
            text = await call_provider(provider, prompt, image_base64)
            latency = (datetime.now() - start).total_seconds() * 1000

            response = AIResponse(
                text=text,
                provider=provider,
                model=config.get("model", "unknown"),
                latency_ms=latency,
            )

            if json_mode:
                parsed = response.as_json()
                if parsed:
                    response.raw_json = parsed
                else:
                    logger.warning(f"{provider} returned non-JSON, trying next")
                    if fallback:
                        continue
            
            logger.info(f"✓ {provider} responded in {latency:.0f}ms")
            return response

        except (QuotaError, httpx.HTTPStatusError) as e:
            errors.append(f"{provider}: {e}")
            logger.warning(f"✗ {provider} failed: {e}")
            if fallback:
                continue
            raise
        except Exception as e:
            errors.append(f"{provider}: {e}")
            logger.error(f"✗ {provider} unexpected error: {e}")
            if fallback:
                continue
            raise

    raise AllProvidersFailedError(
        f"All providers failed for {task_type}:\n" + "\n".join(errors)
    )
