import sqlglot
from typing import Dict, Any, List

def parse_sql_ast(query: str) -> Dict[str, Any]:
    """Parses SQL query into AST breakdown using SQLGlot."""
    try:
        expression = sqlglot.parse_one(query, read="sqlite")
        tables = [table.name for table in expression.find_all(sqlglot.exp.Table)]
        columns = [column.name for column in expression.find_all(sqlglot.exp.Column)]
        
        return {
            "tables": list(set(tables)),
            "columns": list(set(columns)),
            "type": type(expression).__name__
        }
    except Exception as e:
        return {"tables": [], "columns": [], "type": "Unknown", "error": str(e)}
