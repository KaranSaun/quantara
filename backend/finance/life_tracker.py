"""
APEX OS — Life Finance Tracker
Income, expenses, net worth, budgeting.
"""

import logging
from datetime import date, timedelta
from db.supabase_client import get_finance_entries, save_finance_entry

logger = logging.getLogger("apex.life_tracker")


async def get_monthly_summary(year: int, month: int) -> dict:
    entries = await get_finance_entries()
    monthly = [
        e for e in entries
        if e.get("date", "").startswith(f"{year}-{month:02d}")
    ]

    income = sum(e.get("amount", 0) for e in monthly if e.get("category") == "income")
    expense = sum(e.get("amount", 0) for e in monthly if e.get("category") == "expense")

    # Group expenses by subcategory
    expense_breakdown = {}
    for e in monthly:
        if e.get("category") == "expense":
            sub = e.get("subcategory", "other")
            expense_breakdown[sub] = expense_breakdown.get(sub, 0) + e.get("amount", 0)

    return {
        "year": year, "month": month,
        "total_income": round(income, 2),
        "total_expense": round(expense, 2),
        "savings": round(income - expense, 2),
        "savings_rate": round((income - expense) / max(income, 1) * 100, 1),
        "expense_breakdown": expense_breakdown,
    }


async def get_net_worth() -> dict:
    entries = await get_finance_entries()
    assets = sum(e.get("amount", 0) for e in entries if e.get("category") == "asset")
    liabilities = sum(e.get("amount", 0) for e in entries if e.get("category") == "liability")
    return {
        "total_assets": round(assets, 2),
        "total_liabilities": round(liabilities, 2),
        "net_worth": round(assets - liabilities, 2),
    }


async def add_entry(
    category: str, subcategory: str, amount: float,
    description: str = "", recurring: bool = False,
) -> dict:
    return await save_finance_entry({
        "date": date.today().isoformat(),
        "category": category,
        "subcategory": subcategory,
        "amount": amount,
        "description": description,
        "recurring": recurring,
    })
