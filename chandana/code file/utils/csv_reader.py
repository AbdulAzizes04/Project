import pandas as pd
import io
from typing import Union, Tuple
from utils.logger import logger
from utils.helper import sanitize_identifier

def load_csv_data(file_source: Union[str, io.BytesIO]) -> Tuple[pd.DataFrame, str]:
    """
    Reads CSV file with automatic encoding fallback (utf-8, latin1, cp1252).
    Returns cleaned DataFrame and sanitized dataset table name.
    """
    encodings = ['utf-8', 'latin1', 'cp1252', 'utf-16']
    df = None
    
    for encoding in encodings:
        try:
            if isinstance(file_source, str):
                df = pd.read_csv(file_source, encoding=encoding)
            else:
                file_source.seek(0)
                df = pd.read_csv(file_source, encoding=encoding)
            logger.info(f"Successfully loaded CSV with encoding: {encoding}")
            break
        except Exception as e:
            continue
            
    if df is None:
        raise ValueError("Failed to read CSV file with standard encodings.")
        
    # Clean column names
    df.columns = [sanitize_identifier(col) for col in df.columns]
    
    # Infer table name
    table_name = "uploaded_csv_data"
    if isinstance(file_source, str):
        table_name = sanitize_identifier(file_source.split('/')[-1].split('\\')[-1].replace('.csv', ''))
    elif hasattr(file_source, 'name') and file_source.name:
        table_name = sanitize_identifier(file_source.name.replace('.csv', ''))
        
    return df, table_name
