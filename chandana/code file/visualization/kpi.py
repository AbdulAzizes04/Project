import pandas as pd
from typing import List, Dict, Any
from utils.helper import format_currency, format_number

def compute_kpis_from_df(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Computes key performance indicators (KPIs) dynamically from query results.
    """
    kpis = []
    if df.empty:
        return kpis

    # KPI 1: Total Records
    kpis.append({
        "label": "Total Records",
        "value": f"{len(df):,}",
        "subtitle": "Rows Returned"
    })

    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()

    if numeric_cols:
        primary_num_col = numeric_cols[0]
        col_name_clean = primary_num_col.replace('_', ' ').title()
        
        total_val = df[primary_num_col].sum()
        avg_val = df[primary_num_col].mean()
        max_val = df[primary_num_col].max()

        is_currency = any(kw in primary_num_col.lower() for kw in ['sales', 'profit', 'revenue', 'price', 'cost', 'amount'])

        if is_currency:
            kpis.append({"label": f"Total {col_name_clean}", "value": format_currency(total_val), "subtitle": "Aggregated Sum"})
            kpis.append({"label": f"Average {col_name_clean}", "value": format_currency(avg_val), "subtitle": "Mean Value"})
            kpis.append({"label": f"Peak {col_name_clean}", "value": format_currency(max_val), "subtitle": "Maximum Record"})
        else:
            kpis.append({"label": f"Total {col_name_clean}", "value": format_number(total_val), "subtitle": "Aggregated Sum"})
            kpis.append({"label": f"Average {col_name_clean}", "value": format_number(avg_val), "subtitle": "Mean Value"})
            kpis.append({"label": f"Peak {col_name_clean}", "value": format_number(max_val), "subtitle": "Maximum Record"})

    return kpis[:4]  # Return top 4 KPIs
