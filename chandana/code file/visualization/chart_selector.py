import pandas as pd
from typing import Tuple, Optional
import plotly.graph_objects as go
from visualization.charts import (
    create_bar_chart,
    create_line_chart,
    create_pie_chart,
    create_scatter_chart,
    create_box_plot
)
from utils.logger import logger

def recommend_and_create_chart(df: pd.DataFrame) -> Tuple[Optional[go.Figure], str]:
    """
    Analyzes DataFrame structure and automatically generates the optimal Plotly chart.

    Returns:
        (plotly_figure_object, chart_type_name)
    """
    if df.empty or len(df.columns) < 2:
        return None, "None"

    cols = list(df.columns)
    
    # Identify numeric and categorical columns
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    cat_cols = df.select_dtypes(include=['object', 'category', 'string']).columns.tolist()
    date_cols = [c for c in cols if 'date' in c.lower() or 'time' in c.lower() or 'year' in c.lower() or 'month' in c.lower()]

    # Case 1: Time Series / Trend
    if date_cols and numeric_cols:
        x_col = date_cols[0]
        y_col = numeric_cols[0]
        fig = create_line_chart(df, x_col, y_col)
        return fig, "Line Chart (Time Series)"

    # Case 2: 1 Categorical + 1 Numeric (Bar / Donut Chart)
    if cat_cols and numeric_cols:
        x_col = cat_cols[0]
        y_col = numeric_cols[0]
        
        # Donut chart if few categories (3 to 6)
        if 3 <= len(df) <= 6:
            fig = create_pie_chart(df, names_col=x_col, values_col=y_col)
            return fig, "Donut Chart (Composition)"
        else:
            fig = create_bar_chart(df, x_col, y_col)
            return fig, "Bar Chart (Comparison)"

    # Case 3: 2 Numeric Columns (Scatter Plot)
    if len(numeric_cols) >= 2:
        x_col = numeric_cols[0]
        y_col = numeric_cols[1]
        fig = create_scatter_chart(df, x_col, y_col)
        return fig, "Scatter Plot (Correlation)"

    # Case 4: Default Bar Chart for first 2 columns
    fig = create_bar_chart(df, cols[0], cols[1])
    return fig, "Bar Chart (Default)"
