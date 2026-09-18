import sqlglot

def format_sql_query(query: str) -> str:
    """Pretty prints and formats raw SQL queries with proper line breaks and indents."""
    try:
        clean = query.strip().rstrip(';')
        formatted = sqlglot.transpile(clean, read="sqlite", write="sqlite", pretty=True)[0]
        return formatted
    except Exception:
        return query
