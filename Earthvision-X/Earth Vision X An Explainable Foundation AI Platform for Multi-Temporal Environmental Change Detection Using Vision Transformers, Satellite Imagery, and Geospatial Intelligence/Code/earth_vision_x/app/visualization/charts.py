"""
Plotly Charting Suite for Training Progress, Confusion Matrix, ROC-AUC, and Evaluation Metrics.
"""

import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from typing import Dict, List, Any

class ChartVisualizer:
    @staticmethod
    def plot_training_history(history: Dict[str, List[float]]) -> go.Figure:
        """
        Plots Loss and Accuracy / Metric curves over training epochs.
        """
        epochs = list(range(1, len(history.get("train_loss", [])) + 1))
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=epochs, y=history.get("train_loss", []), mode='lines+markers', name='Train Loss', line=dict(color='#EF4444', width=2)))
        fig.add_trace(go.Scatter(x=epochs, y=history.get("val_loss", []), mode='lines+markers', name='Val Loss', line=dict(color='#3B82F6', width=2)))
        fig.add_trace(go.Scatter(x=epochs, y=history.get("f1_score", []), mode='lines+markers', name='Val F1 Score', line=dict(color='#10B981', width=2)))
        fig.add_trace(go.Scatter(x=epochs, y=history.get("iou", []), mode='lines+markers', name='Val IoU', line=dict(color='#F59E0B', width=2)))

        fig.update_layout(
            title="<b>Training Optimization Trajectory</b>",
            xaxis_title="Epoch",
            yaxis_title="Metric Value",
            template="plotly_white",
            hovermode="x unified",
            margin=dict(l=40, r=40, t=60, b=40)
        )
        return fig

    @staticmethod
    def plot_confusion_matrix(cm: List[List[int]], class_names: List[str] = None) -> go.Figure:
        """
        Renders annotated confusion matrix heatmap.
        """
        if class_names is None:
            class_names = [f"Class {i}" for i in range(len(cm))]

        fig = px.imshow(
            cm,
            x=class_names,
            y=class_names,
            color_continuous_scale="Blues",
            aspect="auto",
            text_auto=True,
            title="<b>Multi-Class Change Detection Confusion Matrix</b>"
        )
        fig.update_layout(xaxis_title="Predicted Class", yaxis_title="Ground Truth Class", template="plotly_white")
        return fig

    @staticmethod
    def plot_class_distribution(distribution: Dict[str, float]) -> go.Figure:
        """
        Plots bar chart of environmental change percentage breakdown.
        """
        df = pd.DataFrame(list(distribution.items()), columns=["Category", "Percentage"])
        fig = px.bar(
            df,
            x="Category",
            y="Percentage",
            color="Category",
            title="<b>Spatial Area Change Distribution (%)</b>",
            text_auto='.1f'
        )
        fig.update_layout(template="plotly_white", showlegend=False)
        return fig
