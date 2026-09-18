"""
About Page Controller.
Presents system architecture, IEEE methodology, mathematical formulations, and research references.
"""

import streamlit as st
from earth_vision_x.app.components.header import render_header

def render_about_page():
    render_header(
        title="EARTH VISION-X | Platform Architecture & IEEE Methodology",
        active_model="IEEE Research Specification",
        confidence="Enterprise Specification v1.0.0"
    )

    st.markdown(
        """
        ### 🏛️ Platform Architecture & IEEE Methodology Overview
        
        **EARTH VISION-X** is an enterprise-grade, foundation AI platform designed for multi-temporal satellite imagery change detection using Vision Transformers (ViT-Base, Swin, SegFormer) and Explainable AI (XAI).
        
        #### 🔬 Key Innovations:
        1. **Siamese Vision Transformer Encoder**: Shared-weight dual branch encoding bitemporal satellite pairs $(X_{T1}, X_{T2})$ to capture global long-range spatial context without receptive field limitations of standard CNNs.
        2. **Patch Cross-Attention Difference Fusion**: Explicit multi-scale feature difference tensor computation:
           $$\Delta F = |F_{T1} - F_{T2}|$$
        3. **Multi-Method XAI Framework**: Integrated Attention Rollout, Grad-CAM, LIME Superpixels, SHAP attributions, and Captum Integrated Gradients for complete model transparency.
        4. **Natural Language Insights**: Automated Natural Language Generation (NLG) synthesizing spatial area metrics, confidence scores, and transformer attention focus into executive reports.

        #### 📚 Primary Change Target Categories:
        - **Deforestation** | **Urban Expansion** | **Flood Detection** | **Water Body Changes**
        - **Agricultural Changes** | **Vegetation Loss** | **Mining Activity** | **Wildfire Burn Areas**
        - **Land Cover Change** | **Infrastructure Development**

        #### 📜 Research References & Citation Standard:
        - Dosovitskiy et al., *"An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale"*, ICLR 2021.
        - Liu et al., *"Swin Transformer: Hierarchical Vision Transformer using Shifted Windows"*, ICCV 2021.
        - Xie et al., *"SegFormer: Simple and Efficient Design for Semantic Segmentation with Transformers"*, NeurIPS 2021.
        - Abnar & Zuidema, *"Quantifying Attention Flow in Transformers"*, ACL 2020.
        """
    )
