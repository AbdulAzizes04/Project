import os
import sqlite3
from sqlalchemy import create_engine, Engine, inspect
from typing import List, Dict, Any, Tuple
import pandas as pd
from utils.logger import logger

DEFAULT_DB_PATH = os.path.join(os.path.dirname(__file__), "dataset.db")

class DatabaseManager:
    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        self.engine: Engine = create_engine(f"sqlite:///{self.db_path}", echo=False)
        logger.info(f"DatabaseManager initialized with DB at: {self.db_path}")

    def get_engine(self) -> Engine:
        return self.engine

    def execute_raw_sql(self, query: str) -> pd.DataFrame:
        """Executes a SQL SELECT query safely using pandas + sqlalchemy engine."""
        with self.engine.connect() as conn:
            df = pd.read_sql_query(query, conn)
            return df

    def get_table_names(self) -> List[str]:
        """Returns list of active tables in the SQLite database."""
        inspector = inspect(self.engine)
        return inspector.get_table_names()

    def get_table_schema(self, table_name: str) -> List[Dict[str, Any]]:
        """Returns column names and data types for a given table."""
        inspector = inspect(self.engine)
        columns = inspector.get_columns(table_name)
        return [{"name": col["name"], "type": str(col["type"])} for col in columns]

    def close(self):
        """Dispose database engine resources."""
        self.engine.dispose()

db_manager = DatabaseManager()
