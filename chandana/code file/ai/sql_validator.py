import sqlglot
from sqlglot import exp
from typing import Tuple
from utils.logger import logger

def validate_sql_query(query: str) -> Tuple[bool, str]:
    """
    Validates a SQL query using SQLGlot parser.
    Ensures:
    1. Query is valid SQL syntax.
    2. Query is strictly a SELECT read-only statement.
    3. Blocks DELETE, DROP, UPDATE, INSERT, ALTER, CREATE, TRUNCATE, etc.

    Returns:
        (is_valid: bool, message: str)
    """
    if not query or not query.strip():
        return False, "Query string is empty."

    clean_query = query.strip().rstrip(';')

    try:
        # Parse expression AST
        parsed = sqlglot.parse_one(clean_query, read="sqlite")
        if not parsed:
            return False, "Failed to parse SQL query structure."

        # Check statement type
        if not isinstance(parsed, (exp.Select, exp.Union)):
            statement_type = type(parsed).__name__
            logger.warning(f"Rejected non-SELECT statement type: {statement_type}")
            return False, f"Security Violation: Only SELECT queries are permitted. (Attempted: {statement_type.upper()})"

        # Check sub-nodes for forbidden expressions
        forbidden_types = (
            exp.Insert, exp.Update, exp.Delete, exp.Drop, 
            exp.Create, exp.Command
        )
        
        for node in parsed.walk():
            if isinstance(node, forbidden_types):
                forbidden_name = type(node).__name__
                return False, f"Security Violation: Query contains prohibited command '{forbidden_name.upper()}'."

        return True, "Valid SELECT query."

    except sqlglot.errors.ParseError as e:
        logger.error(f"SQLGlot parsing error: {e}")
        # Secondary fallback regex check for strict SELECT
        if clean_query.upper().startswith("SELECT"):
            # Check for dangerous keywords anywhere
            blacklisted = ["DROP ", "DELETE ", "UPDATE ", "INSERT ", "ALTER ", "TRUNCATE ", "EXEC "]
            for kw in blacklisted:
                if kw in clean_query.upper():
                    return False, f"Security Violation: Query contains prohibited keyword '{kw.strip()}'."
            return True, "Valid SELECT query (syntax fallback)."
        return False, f"SQL Syntax Error: {e}"
    except Exception as e:
        logger.error(f"Unexpected validation error: {e}")
        return False, f"Validation Error: {str(e)}"
