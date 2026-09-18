import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Optional

DARK_THEME_LAYOUT = dict(
    paper_bgcolor='rgba(15, 23, 42, 0.6)',
    plot_bgcolor='rgba(15, 23, 42, 0.6)',
    font=dict(family="Inter, Roboto, sans-serif", color="#F8FAFC", size=12),
    xaxis=dict(
        gridcolor='rgba(255, 255, 255, 0.1)',
        zerolinecolor='rgba(255, 255, 255, 0.2)',
        tickfont=dict(color="#94A3B8")
    ),
    yaxis=dict(
        gridcolor='rgba(255, 255, 255, 0.1)',
        zerolinecolor='rgba(255, 255, 255, 0.2)',
        tickfont=dict(color="#94A3B8")
    ),
    margin=dict(l=40, r=40, t=50, b=40)
)

COLOR_PALETTE = ['#3B82F6', '#10B981', '#F59E0B', '#EC4899', '#8B5CF6', '#06B6D4', '#6366F1']

def create_bar_chart(df: pd.DataFrame, x_col: str, y_col: str, title: Optional[str] = None) -> go.Figure:
    fig = px.bar(
        df,
        x=x_col,
        y=y_col,
        title=title or f"{y_col.replace('_', ' ').title()} by {x_col.replace('_', ' ').title()}",
        color_discrete_sequence=[COLOR_PALETTE[0]],
        text_auto='.2s'
    )
    fig.update_layout(**DARK_THEME_LAYOUT)
    fig.update_traces(hovertemplate="<b>%{x}</b><br>%{y:,}")
    return fig


def create_line_chart(df: pd.DataFrame, x_col: str, y_col: str, title: Optional[str] = None) -> go.Figure:
    fig = px.line(
        df,
        x=x_col,
        y=y_col,
        title=title or f"{y_col.replace('_', ' ').title()} Trend",
        markers=True,
        color_discrete_sequence=[COLOR_PALETTE[1]]
    )
    fig.update_layout(**DARK_THEME_LAYOUT)
    fig.update_traces(line=dict(width=3), marker=dict(size=8))
    return fig

def create_pie_chart(df: pd.DataFrame, names_col: str, values_col: str, title: Optional[str] = None) -> go.Figure:
    fig = px.pie(
        df,
        names=names_col,
        values=values_col,
        title=title or f"{values_col.replace('_', ' ').title()} Share by {names_col.replace('_', ' ').title()}",
        color_discrete_sequence=COLOR_PALETTE,
        hole=0.4
    )
    fig.update_layout(**DARK_THEME_LAYOUT)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig

def create_scatter_chart(df: pd.DataFrame, x_col: str, y_col: str, title: Optional[str] = None) -> go.Figure:
    fig = px.scatter(
        df,
        x=x_col,
        y=y_col,
        title=title or f"{y_col.replace('_', ' ').title()} vs {x_col.replace('_', ' ').title()}",
        color_discrete_sequence=[COLOR_PALETTE[2]],
        size_max=15
    )
    fig.update_layout(**DARK_THEME_LAYOUT)
    return fig

def create_box_plot(df: pd.DataFrame, x_col: str, y_col: str, title: Optional[str] = None) -> go.Figure:
    fig = px.box(
        df,
        x=x_col,
        y=y_col,
        title=title or f"Distribution of {y_col.replace('_', ' ').title()}",
        color_discrete_sequence=[COLOR_PALETTE[4]]
    )
    fig.update_layout(**DARK_THEME_LAYOUT)
    return fig
