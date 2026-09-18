"""
Helper utilities for formatting numbers, currency, dates, and text badges.
"""

from datetime import datetime, timedelta

def format_currency(amount: float, currency_symbol: str = "$") -> str:
    """Formats a float as standard currency string."""
    if amount >= 1_000_000:
        return f"{currency_symbol}{amount / 1_000_000:.2f}M"
    elif amount >= 1_000:
        return f"{currency_symbol}{amount / 1_000:.1f}k"
    return f"{currency_symbol}{amount:,.2f}"

def format_pct(value: float) -> str:
    """Formats decimal or float to percentage string."""
    return f"{value:.1f}%"

def calculate_date_offset(base_date_str: str, days: int) -> str:
    """Adds N days to a ISO date string YYYY-MM-DD."""
    try:
        dt = datetime.strptime(base_date_str, "%Y-%m-%d")
        new_dt = dt + timedelta(days=days)
        return new_dt.strftime("%Y-%m-%d")
    except Exception:
        return base_date_str

def get_days_between(start_str: str, end_str: str) -> int:
    """Calculates days between two YYYY-MM-DD date strings."""
    try:
        d1 = datetime.strptime(start_str, "%Y-%m-%d")
        d2 = datetime.strptime(end_str, "%Y-%m-%d")
        return max(1, (d2 - d1).days)
    except Exception:
        return 30
