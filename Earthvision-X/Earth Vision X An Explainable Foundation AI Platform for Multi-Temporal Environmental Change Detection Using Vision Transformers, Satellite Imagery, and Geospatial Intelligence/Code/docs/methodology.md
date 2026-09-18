# EARTH VISION-X: Research Methodology & System Specifications

## 1. System Overview

**EARTH VISION-X** is an IEEE-grade Explainable Foundation AI Platform designed for multi-temporal satellite imagery change detection using Vision Transformers (ViT, Swin, SegFormer), Geospatial Intelligence (Sentinel-2, Landsat, GeoTIFF), and Explainable AI (Attention Rollout, Grad-CAM, LIME, SHAP, Captum).

## 2. Multi-Temporal Siamese Vision Transformer Design

Standard convolutional networks suffer from limited receptive fields when processing global environmental changes across large satellite scenes. EARTH VISION-X solves this through a weight-sharing bitemporal Siamese Vision Transformer encoder:

$$\mathbf{F}_{T1} = \mathcal{E}_{\text{ViT}}(\mathbf{X}_{T1}), \quad \mathbf{F}_{T2} = \mathcal{E}_{\text{ViT}}(\mathbf{X}_{T2})$$

### Feature Difference Fusion & Cross-Attention
The multi-temporal feature representations are fused using difference magnitude and concatenated context:

$$\mathbf{D} = |\mathbf{F}_{T1} - \mathbf{F}_{T2}|$$
$$\mathbf{F}_{\text{fused}} = \text{Conv}_{3\times3}([\mathbf{D} \,||\, \mathbf{F}_{T2}])$$

## 3. Loss Functions & Optimization

### Hybrid Combo Loss Formulation
To mitigate extreme class imbalance (where changed pixels account for <15% of spatial frames), EARTH VISION-X optimizes a hybrid loss function combining Cross-Entropy, Focal Loss, and Dice Loss:

$$\mathcal{L}_{\text{Hybrid}} = \lambda_1 \mathcal{L}_{\text{CE}} + \lambda_2 \mathcal{L}_{\text{Dice}} + \lambda_3 \mathcal{L}_{\text{Focal}}$$

where:
- $\mathcal{L}_{\text{Dice}} = 1 - \frac{2 \sum y \hat{y}}{\sum y + \sum \hat{y}}$
- $\mathcal{L}_{\text{Focal}} = -\alpha_t (1 - p_t)^\gamma \log(p_t)$

## 4. Explainable AI (XAI) Suite

1. **Attention Rollout**: Computes matrix multiplication across transformer self-attention layers:
   $$\mathbf{A}_{\text{rollout}} = \prod_{l=1}^{L} \left(0.5 \mathbf{A}^{(l)} + 0.5 \mathbf{I}\right)$$
2. **Grad-CAM for ViT**: Computes gradient-weighted feature map activations targeting specific change classes:
   $$L_{\text{Grad-CAM}}^c = \text{ReLU}\left(\sum_k \alpha_k^c A^k\right)$$
3. **LIME Superpixel Segmentation**: Identifies local superpixel boundaries driving spatial change decisions.
4. **SHAP Feature Attributions**: Measures relative spectral channel contributions (Red, Green, Blue, NDVI, NDWI).

## 5. References

1. Dosovitskiy, A., et al. "An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale." *ICLR*, 2021.
2. Liu, Z., et al. "Swin Transformer: Hierarchical Vision Transformer using Shifted Windows." *ICCV*, 2021.
3. Xie, E., et al. "SegFormer: Simple and Efficient Design for Semantic Segmentation with Transformers." *NeurIPS*, 2021.
