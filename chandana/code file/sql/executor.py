import time
import pandas as pd
from typing import Tuple, Dict, Any
from database.sqlite_db import db_manager
from ai.sql_validator import validate_sql_query
from utils.logger import logger

def execute_sql_query(query: str, max_rows: int = 1000) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Validates and executes a SQL SELECT query against the SQLite database.

    Returns:
        (result_dataframe, execution_metadata_dict)
    """
    start_time = time.time()
    
    # 1. Validate query safety
    is_valid, msg = validate_sql_query(query)
    if not is_valid:
        raise ValueError(f"Query Validation Error: {msg}")

    clean_query = query.strip().rstrip(';')

    try:
        # Execute query
        df = db_manager.execute_raw_sql(clean_query)
        execution_time = time.time() - start_time
        
        # Enforce max row cap for frontend responsiveness
        total_rows = len(df)
        if total_rows > max_rows:
            df = df.head(max_rows)
            truncated = True
        else:
            truncated = False

        metadata = {
            "execution_time_seconds": round(execution_time, 4),
            "total_rows": total_rows,
            "returned_rows": len(df),
            "columns_count": len(df.columns),
            "is_truncated": truncated,
            "status": "SUCCESS"
        }
        
        logger.info(f"Query executed successfully in {metadata['execution_time_seconds']}s returning {len(df)} rows.")
        return df, metadata

    except Exception as e:
        logger.error(f"SQL execution error for query '{clean_query}': {e}")
        raise RuntimeError(f"Database Execution Failure: {e}")
