import pandas as pd
from typing import Optional
from ai.llm import get_llm_instance
from ai.prompt import sql_explain_prompt
from utils.logger import logger

def generate_plain_english_explanation(
    question: str,
    sql_query: str,
    df: pd.DataFrame,
    provider: str = "gemini",
    api_key: Optional[str] = None,
    model_name: Optional[str] = None
) -> str:
    """
    Generates a clear Plain English business explanation for the SQL query and query results.
    """
    if df.empty:
        return f"The query executed successfully but returned 0 rows matching your criteria."

    # Sample summary text
    result_summary = f"Returned {len(df)} rows and {len(df.columns)} columns.\nFirst 3 rows:\n{df.head(3).to_string(index=False)}"

    # Try LLM
    llm = get_llm_instance(provider=provider, api_key=api_key, model_name=model_name)
    if llm is not None:
        try:
            formatted_prompt = sql_explain_prompt.format(
                question=question,
                sql_query=sql_query,
                result_summary=result_summary
            )
            response = llm.invoke(formatted_prompt)
            explanation = response.content if hasattr(response, 'content') else str(response)
            return explanation.strip()
        except Exception as e:
            logger.error(f"LLM explanation error: {e}")

    # Rule-Based Analytical Fallback Explanation
    return _rule_based_explanation(question, sql_query, df)

def _rule_based_explanation(question: str, sql_query: str, df: pd.DataFrame) -> str:
    """Analytical template generator for offline plain English business explanation."""
    num_rows = len(df)
    cols = list(df.columns)
    
    explanation_parts = [
        f"This query analyzes data based on your request: '{question}'."
    ]

    if num_rows > 0 and len(cols) >= 2:
        group_col = cols[0]
        val_col = cols[1]
        top_item = df.iloc[0][group_col]
        top_val = df.iloc[0][val_col]

        if isinstance(top_val, (int, float)):
            top_val_str = f"{top_val:,.2f}" if isinstance(top_val, float) else f"{top_val:,}"
        else:
            top_val_str = str(top_val)

        explanation_parts.append(
            f"The top result is **{top_item}** with **{val_col}** of **{top_val_str}**."
        )
        if num_rows > 1:
            explanation_parts.append(
                f"The dataset displays a total of {num_rows} distinct grouped records."
            )
    elif num_rows > 0:
        explanation_parts.append(f"Retrieved {num_rows} records from the database.")

    return " ".join(explanation_parts)

