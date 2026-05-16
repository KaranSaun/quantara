"""
APEX OS — AI News Scorer
Scores each headline for relevance, direction, urgency, banking impact.
"""

import logging
from dataclasses import dataclass
import ai_router

logger = logging.getLogger("apex.news_scorer")

SCORING_PROMPT = """You are an expert Indian equity market analyst. Score this news headline:

Headline: "{headline}"
Source: {source}

Return ONLY valid JSON:
{{
  "relevance_score": 0-10,
  "direction": "bullish" | "bearish" | "neutral",
  "direction_magnitude": 1-5,
  "urgency": "breaking" | "scheduled" | "routine",
  "banking_impact": 0-10,
  "reasoning": "one sentence"
}}

Rules:
- relevance_score: How relevant to Indian equity/options trading (0=irrelevant, 10=critical)
- banking_impact: Specific impact on banking/financial sector (for BankNifty)
- direction: Expected market impact direction
- Be precise. Political events, RBI policy, FII flows, global cues = high relevance
"""


@dataclass
class NewsBias:
    direction: str
    strength: int
    top_headlines: list[dict]
    avg_relevance: float
    breaking_count: int
    reasoning: str
    confidence: int


async def score_headline(headline: str, source: str) -> dict:
    prompt = SCORING_PROMPT.format(headline=headline, source=source)
    try:
        response = await ai_router.analyze(prompt, task_type="fast", json_mode=True)
        return response.as_json() or {
            "relevance_score": 3, "direction": "neutral",
            "direction_magnitude": 1, "urgency": "routine",
            "banking_impact": 2, "reasoning": "Could not parse AI response"}
    except Exception as e:
        logger.warning(f"AI scoring failed for headline: {e}")
        return {
            "relevance_score": 3, "direction": "neutral",
            "direction_magnitude": 1, "urgency": "routine",
            "banking_impact": 2, "reasoning": f"Scoring error: {e}"}


async def score_all_news(news_items: list[dict]) -> list[dict]:
    scored = []
    for item in news_items[:30]:  # Limit to 30 to save API calls
        score = await score_headline(item["headline"], item.get("source", ""))
        item.update({
            "relevance_score": score.get("relevance_score", 3),
            "direction": score.get("direction", "neutral"),
            "urgency": score.get("urgency", "routine"),
            "banking_impact": score.get("banking_impact", 2),
            "raw_sentiment": score,
        })
        scored.append(item)
    return scored


async def aggregate_today(scored_news: list[dict]) -> NewsBias:
    if not scored_news:
        return NewsBias(
            direction="NEUTRAL", strength=1, top_headlines=[],
            avg_relevance=0, breaking_count=0,
            reasoning="No news data available.", confidence=15)

    relevant = [n for n in scored_news if n.get("relevance_score", 0) >= 4]
    if not relevant:
        return NewsBias(
            direction="NEUTRAL", strength=1, top_headlines=[],
            avg_relevance=sum(n.get("relevance_score", 0) for n in scored_news) / len(scored_news),
            breaking_count=0,
            reasoning="No highly relevant news for Indian markets today.", confidence=20)

    bull = sum(1 for n in relevant if n.get("direction") == "bullish")
    bear = sum(1 for n in relevant if n.get("direction") == "bearish")
    breaking = sum(1 for n in relevant if n.get("urgency") == "breaking")
    avg_rel = sum(n.get("relevance_score", 0) for n in relevant) / len(relevant)

    top = sorted(relevant, key=lambda x: x.get("relevance_score", 0), reverse=True)[:5]
    top_headlines = [{"headline": n["headline"], "direction": n.get("direction"),
                      "relevance": n.get("relevance_score"), "source": n.get("source")} for n in top]

    if bull > bear * 1.5:
        direction, strength = "BULLISH", min(5, bull)
    elif bear > bull * 1.5:
        direction, strength = "BEARISH", min(5, bear)
    else:
        direction, strength = "NEUTRAL", 1

    confidence = min(70, 15 + len(relevant) * 5 + breaking * 10)

    headlines_text = "; ".join([h["headline"][:60] for h in top_headlines[:3]])
    reasoning = (
        f"{len(relevant)} relevant news items ({bull} bullish, {bear} bearish). "
        f"{'BREAKING news present. ' if breaking else ''}"
        f"Top headlines: {headlines_text}."
    )

    return NewsBias(
        direction=direction, strength=strength, top_headlines=top_headlines,
        avg_relevance=round(avg_rel, 1), breaking_count=breaking,
        reasoning=reasoning, confidence=confidence)
