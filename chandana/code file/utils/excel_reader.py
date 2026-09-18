import pandas as pd
import io
from typing import Union, Tuple, Dict
from utils.logger import logger
from utils.helper import sanitize_identifier

def load_excel_data(file_source: Union[str, io.BytesIO], sheet_name: Union[str, int] = 0) -> Tuple[pd.DataFrame, str]:
    """
    Reads Excel (.xlsx / .xls) file using pandas and openpyxl.
    Returns cleaned DataFrame and sanitized dataset table name.
    """
    try:
        if isinstance(file_source, str):
            excel_file = pd.ExcelFile(file_source)
            df = excel_file.parse(sheet_name)
        else:
            file_source.seek(0)
            excel_file = pd.ExcelFile(file_source)
            df = excel_file.parse(sheet_name)
            
        logger.info(f"Successfully loaded Excel sheet '{sheet_name}'")
    except Exception as e:
        logger.error(f"Error reading Excel file: {e}")
        raise ValueError(f"Could not parse Excel file: {e}")

    # Clean column names
    df.columns = [sanitize_identifier(col) for col in df.columns]

    # Infer table name
    table_name = "uploaded_excel_data"
    if isinstance(file_source, str):
        base_name = file_source.split('/')[-1].split('\\')[-1].replace('.xlsx', '').replace('.xls', '')
        table_name = sanitize_identifier(base_name)
    elif hasattr(file_source, 'name') and file_source.name:
        base_name = file_source.name.replace('.xlsx', '').replace('.xls', '')
        table_name = sanitize_identifier(base_name)

    return df, table_name

def get_excel_sheets(file_source: Union[str, io.BytesIO]) -> list:
    """
    Returns all sheet names present in the Excel file.
    """
    try:
        if isinstance(file_source, str):
            excel_file = pd.ExcelFile(file_source)
        else:
            file_source.seek(0)
            excel_file = pd.ExcelFile(file_source)
        return excel_file.sheet_names
    except Exception as e:
        logger.error(f"Error getting Excel sheets: {e}")
        return []
