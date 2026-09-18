"""
Explainability (XAI) Package.

Contains SHAP and LIME explainer wrapper interfaces, visualization plotters,
and human-readable natural language narrative summary generators.
"""

from explainability.shap_explainer import (
    load_model_artifacts,
    initialize_shap,
    generate_shap_values,
    generate_force_plot,
    generate_waterfall_plot,
    generate_bar_plot,
    generate_summary_plot,
    generate_human_readable_summary,
    save_shap_visualizations,
)

from explainability.lime_explainer import (
    initialize_lime,
    generate_lime_explanation,
    plot_lime_features,
    explain_prediction,
    save_lime_visualization,
)

__all__ = [
    "load_model_artifacts",
    "initialize_shap",
    "generate_shap_values",
    "generate_force_plot",
    "generate_waterfall_plot",
    "generate_bar_plot",
    "generate_summary_plot",
    "generate_human_readable_summary",
    "save_shap_visualizations",
    "initialize_lime",
    "generate_lime_explanation",
    "plot_lime_features",
    "explain_prediction",
    "save_lime_visualization",
]
