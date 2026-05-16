"""
APEX OS — Goal Planner
AI-powered financial goal calculation with milestones.
"""

import logging
from datetime import date
import ai_router

logger = logging.getLogger("apex.goal_planner")

GOAL_PROMPT = """You are a financial planner for Indian retail traders.

Goal: {goal_name}
Target: ₹{target_amount:,.0f}
Current capital: ₹{current_capital:,.0f}
Monthly savings: ₹{monthly_savings:,.0f}
Risk appetite: {risk_appetite}
Today: {today}
Target date: {target_date}

Return ONLY valid JSON:
{{
  "is_realistic": true/false,
  "realistic_assessment": "2-3 sentences",
  "monthly_trading_target": float,
  "required_monthly_return_pct": float,
  "monthly_savings_needed": float,
  "milestones": [
    {{"months_from_now": 3, "target_net_worth": float, "checkpoint": "string"}}
  ],
  "income_streams_needed": [
    {{
      "stream": "string",
      "monthly_target": float,
      "capital_required": float,
      "difficulty": "LOW|MEDIUM|HIGH",
      "how_to_start": "string"
    }}
  ],
  "revised_timeline_if_unrealistic": "date or null",
  "risk_warning": "string or null"
}}"""


async def generate_plan(
    goal_name: str, target_amount: float, current_capital: float,
    monthly_savings: float, risk_appetite: str, target_date: str,
) -> dict:
    prompt = GOAL_PROMPT.format(
        goal_name=goal_name, target_amount=target_amount,
        current_capital=current_capital, monthly_savings=monthly_savings,
        risk_appetite=risk_appetite, today=date.today().isoformat(),
        target_date=target_date,
    )

    try:
        response = await ai_router.analyze(prompt, task_type="reasoning", json_mode=True)
        plan = response.as_json()
        if plan:
            return plan
    except Exception as e:
        logger.error(f"Goal planning AI failed: {e}")

    # Fallback basic calculation
    months = max(1, ((date.fromisoformat(target_date) - date.today()).days) // 30)
    gap = target_amount - current_capital
    monthly_needed = gap / months
    return {
        "is_realistic": monthly_needed < monthly_savings * 3,
        "realistic_assessment": f"Need ₹{monthly_needed:,.0f}/month to reach goal.",
        "monthly_trading_target": round(monthly_needed - monthly_savings, 2),
        "required_monthly_return_pct": round((monthly_needed - monthly_savings) / max(current_capital, 1) * 100, 2),
        "monthly_savings_needed": round(monthly_savings, 2),
        "milestones": [],
        "income_streams_needed": [],
        "revised_timeline_if_unrealistic": None,
        "risk_warning": None,
    }
