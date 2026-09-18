import re
import pandas as pd
from typing import Any, List, Dict

def sanitize_identifier(name: str) -> str:
    """
    Sanitizes string for safe SQLite table and column names.
    Converts spaces and special characters to underscores, lowers case.
    """
    if not name:
        return "unnamed_column"
    # Replace invalid chars with underscore
    clean = re.sub(r'[^a-zA-Z0-9_]', '_', str(name).strip())
    # Ensure starts with a letter or underscore
    if clean and clean[0].isdigit():
        clean = f"col_{clean}"
    # Collapse multiple underscores
    clean = re.sub(r'_+', '_', clean)
    return clean.lower().strip('_')

def format_currency(value: float) -> str:
    """
    Formats a numeric float into currency presentation string.
    """
    if pd.isna(value):
        return "$0.00"
    if abs(value) >= 1_000_000:
        return f"${value/1_000_000:.2f}M"
    elif abs(value) >= 1_000:
        return f"${value/1_000:.2f}K"
    else:
        return f"${value:,.2f}"

def format_number(value: float) -> str:
    """
    Formats numeric float into human readable string.
    """
    if pd.isna(value):
        return "0"
    if abs(value) >= 1_000_000:
        return f"{value/1_000_000:.2f}M"
    elif abs(value) >= 1_000:
        return f"{value/1_000:.2f}K"
    elif isinstance(value, float) and value.is_integer():
        return f"{int(value):,}"
    elif isinstance(value, (int, float)):
        return f"{value:,.2f}"
    return str(value)
