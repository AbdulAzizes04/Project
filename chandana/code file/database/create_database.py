import os
import pandas as pd
from typing import Tuple, List, Dict
from sqlalchemy import Engine
from database.sqlite_db import db_manager, DEFAULT_DB_PATH
from utils.helper import sanitize_identifier
from utils.logger import logger

def ingest_dataframe_to_sqlite(
    df: pd.DataFrame,
    table_name: str = "dataset",
    db_path: str = DEFAULT_DB_PATH,
    if_exists: str = "replace"
) -> Tuple[str, List[str], Dict[str, str]]:
    """
    Ingests a Pandas DataFrame into SQLite database table.
    
    Returns:
        (sanitized_table_name, column_names_list, column_data_types_dict)
    """
    # Sanitize table name
    clean_table_name = sanitize_identifier(table_name)
    if not clean_table_name:
        clean_table_name = "uploaded_dataset"

    # Copy and sanitize column headers
    cleaned_df = df.copy()
    cleaned_df.columns = [sanitize_identifier(col) for col in cleaned_df.columns]

    # Convert datetime objects to ISO formatted strings for SQLite compatibility
    for col in cleaned_df.columns:
        if pd.api.types.is_datetime64_any_dtype(cleaned_df[col]):
            cleaned_df[col] = cleaned_df[col].dt.strftime('%Y-%m-%d %H:%M:%S')

    # Write to SQLite
    engine = db_manager.engine
    cleaned_df.to_sql(name=clean_table_name, con=engine, if_exists=if_exists, index=False)
    logger.info(f"Successfully ingested {len(cleaned_df)} rows into table '{clean_table_name}' in SQLite DB.")

    columns = list(cleaned_df.columns)
    dtypes = {col: str(cleaned_df[col].dtype) for col in columns}

    return clean_table_name, columns, dtypes
