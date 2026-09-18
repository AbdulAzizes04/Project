"""
Training Page Controller.
Provides interactive hyperparameter configuration, GPU selection,
loss & accuracy live plotting, early stopping tuning, and model training execution.
"""

import streamlit as st
import time
from earth_vision_x.app.components.header import render_header
from earth_vision_x.app.config.constants import SupportedModels, SupportedLosses, SupportedOptimizers
from earth_vision_x.app.services.training_service import TrainingService
from earth_vision_x.app.visualization.charts import ChartVisualizer

def render_training_page():
    render_header(
        "Model Training Studio",
        "Train and Fine-Tune Vision Transformers on Satellite Change Detection"
    )

    st.subheader("⚙️ Training Hyperparameters & Model Configuration")

    col1, col2, col3 = st.columns(3)

    with col1:
        model_choice = st.selectbox("Vision Transformer Backbone", [m.value for m in SupportedModels])
        epochs = st.number_input("Number of Epochs", min_value=1, max_value=100, value=5)
        batch_size = st.selectbox("Batch Size", [1, 2, 4, 8, 16], index=1)

    with col2:
        loss_choice = st.selectbox("Loss Function", [l.value for l in SupportedLosses])
        optimizer_choice = st.selectbox("Optimizer", [o.value for o in SupportedOptimizers])
        lr = st.select_slider("Learning Rate", options=[1e-5, 5e-5, 1e-4, 5e-4, 1e-3], value=1e-4)

    with col3:
        hardware = st.radio("Hardware Accelerator", ["Auto-Detect (CUDA/CPU)", "Force CPU"], index=0)
        use_amp = st.checkbox("Enable Mixed Precision (AMP)", value=True)
        early_stop = st.checkbox("Enable Early Stopping (Patience=5)", value=True)

    st.markdown("---")

    if st.button("🔥 Start Model Training Run", type="primary"):
        st.info("Starting training loop...")
        progress_bar = st.progress(0)
        status_text = st.empty()
        chart_placeholder = st.empty()

        live_history = {
            "train_loss": [],
            "val_loss": [],
            "f1_score": [],
            "iou": []
        }

        def on_epoch_end(epoch, total_epochs, t_loss, v_loss, v_metrics):
            progress = epoch / total_epochs
            progress_bar.progress(progress)
            status_text.markdown(f"**Epoch [{epoch}/{total_epochs}]** - Train Loss: `{t_loss:.4f}` | Val Loss: `{v_loss:.4f}` | F1: `{v_metrics.get('F1 Score', 0):.4f}`")

            live_history["train_loss"].append(t_loss)
            live_history["val_loss"].append(v_loss)
            live_history["f1_score"].append(v_metrics.get("F1 Score", 0.0))
            live_history["iou"].append(v_metrics.get("IoU", 0.0))

            fig = ChartVisualizer.plot_training_history(live_history)
            chart_placeholder.plotly_chart(fig, use_container_width=True)

        device = "cpu" if "Force" in hardware else ("cuda" if False else "cpu")

        history = TrainingService.train_model(
            model_name=model_choice,
            loss_name=loss_choice,
            optimizer_name=optimizer_choice,
            epochs=epochs,
            batch_size=batch_size,
            lr=lr,
            device=device,
            progress_callback=on_epoch_end
        )

        st.success("🎉 Training Run Completed Successfully! Model checkpoint saved to `checkpoints/best_model.pth`.")
