from typing import Dict, Any, List
import pandas as pd
from database.sqlite_db import db_manager
from utils.logger import logger

def get_database_schema_prompt_text(table_name: str) -> str:
    """
    Constructs a detailed schema text string containing columns, data types,
    and 3 sample data rows to guide LLMs in accurate SQL generation.
    """
    try:
        schema = db_manager.get_table_schema(table_name)
        if not schema:
            return f"Table '{table_name}' does not exist or has no columns."

        # Fetch sample rows
        sample_df = db_manager.execute_raw_sql(f"SELECT * FROM {table_name} LIMIT 3")
        
        schema_lines = [f"TABLE NAME: {table_name}", "COLUMNS AND TYPES:"]
        for col in schema:
            schema_lines.append(f"  - {col['name']} ({col['type']})")
            
        schema_lines.append("\nSAMPLE DATA (First 3 rows):")
        schema_lines.append(sample_df.to_string(index=False))
        
        return "\n".join(schema_lines)
    except Exception as e:
        logger.error(f"Error building schema text for table '{table_name}': {e}")
        return f"Table: {table_name}\nError inspecting schema: {e}"

def get_table_metadata(table_name: str) -> Dict[str, Any]:
    """
    Returns structured metadata including column count, row count, column names, data types.
    """
    try:
        schema = db_manager.get_table_schema(table_name)
        count_df = db_manager.execute_raw_sql(f"SELECT COUNT(*) AS row_count FROM {table_name}")
        row_count = int(count_df['row_count'].iloc[0]) if not count_df.empty else 0
        
        return {
            "table_name": table_name,
            "row_count": row_count,
            "column_count": len(schema),
            "columns": [col['name'] for col in schema],
            "dtypes": {col['name']: col['type'] for col in schema}
        }
    except Exception as e:
        logger.error(f"Error getting table metadata: {e}")
        return {"table_name": table_name, "row_count": 0, "column_count": 0, "columns": [], "dtypes": {}}

def generate_suggested_questions(table_name: str) -> List[str]:
    """
    Dynamically generates 3 tailored suggested questions based on the uploaded table's actual columns and data types.
    """
    meta = get_table_metadata(table_name)
    columns = meta.get("columns", [])
    dtypes = meta.get("dtypes", {})

    if not columns:
        return [
            "Show first 10 rows of data",
            "What is the total row count?",
            "Summarize the dataset"
        ]

    # Categorize columns
    numeric_cols = [c for c, dt in dtypes.items() if any(x in dt.lower() for x in ['int', 'float', 'double', 'real', 'num', 'bigint'])]
    text_cols = [c for c in columns if c not in numeric_cols]
    date_cols = [c for c in columns if any(kw in c.lower() for kw in ['date', 'time', 'year', 'month'])]

    questions = []

    # Priority 1: Top N query (if 1 text + 1 numeric)
    if text_cols and numeric_cols:
        cat = text_cols[0]
        val = numeric_cols[0]
        # Prefer sales/revenue/profit if present
        for col in numeric_cols:
            if any(kw in col.lower() for kw in ['sales', 'revenue', 'profit', 'total', 'amount', 'score']):
                val = col
                break
        for col in text_cols:
            if any(kw in col.lower() for kw in ['product', 'city', 'region', 'category', 'name', 'store', 'customer', 'salesperson']):
                cat = col
                break
        questions.append(f"What are the top 5 {cat}s by {val}?")

    # Priority 2: Date trend or Category distribution
    if date_cols and numeric_cols:
        d_col = date_cols[0]
        val = numeric_cols[0]
        questions.append(f"Show {val} trend by {d_col}")
    elif len(text_cols) >= 2 and numeric_cols:
        cat2 = text_cols[1]
        val = numeric_cols[0]
        questions.append(f"Show total {val} grouped by {cat2}")
    elif text_cols and len(numeric_cols) >= 2:
        cat = text_cols[0]
        val2 = numeric_cols[1]
        questions.append(f"What is the total {val2} by {cat}?")

    # Priority 3: Average / Distribution
    if text_cols and numeric_cols:
        cat = text_cols[0]
        val = numeric_cols[-1]
        questions.append(f"What is the average {val} by {cat}?")

    # Fallbacks if we don't have enough questions
    if len(questions) < 3:
        if numeric_cols:
            questions.append(f"Show top 5 records with highest {numeric_cols[0]}")
        if text_cols:
            questions.append(f"Show record count grouped by {text_cols[0]}")
        questions.append(f"Show all columns for first 10 rows")

    return questions[:3]

