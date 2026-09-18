"""
Inference Business Service Layer.
Orchestrates model predictions, XAI attributions, AI Insights synthesis,
database recording, and PDF report generation.
"""

from typing import Dict, Any
import numpy as np

from earth_vision_x.app.config.constants import SupportedModels
from earth_vision_x.app.config.logging_config import logger
from earth_vision_x.app.models.factory import ModelFactory
from earth_vision_x.app.inference.engine import InferenceEngine
from earth_vision_x.app.explainability.attention_rollout import AttentionRolloutExplainer
from earth_vision_x.app.explainability.grad_cam import ViTGradCAM
from earth_vision_x.app.explainability.lime_explainer import LimeSuperpixelExplainer
from earth_vision_x.app.explainability.shap_explainer import ShapFeatureExplainer
from earth_vision_x.app.explainability.captum_explainer import CaptumExplainer
from earth_vision_x.app.explainability.ai_insights import AIInsightsGenerator
from earth_vision_x.app.visualization.change_maps import ChangeMapVisualizer
from earth_vision_x.app.reports.pdf_generator import PDFReportGenerator
from earth_vision_x.app.database.db import SessionLocal
from earth_vision_x.app.database.repository import PredictionRepository
from earth_vision_x.app.database.models import PredictionRecord

class InferenceService:
    def __init__(self, model_name: str = SupportedModels.VIT_BASE, device: str = "cpu"):
        self.model_name = model_name
        self.device = device
        self.model = ModelFactory.create_model(model_type=model_name, device=device)
        self.engine = InferenceEngine(self.model, device=device)

    def run_full_pipeline(
        self,
        t1_source: str | np.ndarray,
        t2_source: str | np.ndarray,
        use_tta: bool = False,
        generate_pdf: bool = True
    ) -> Dict[str, Any]:
        """
        Executes end-to-end change detection, XAI, insights, and report generation.
        """
        # 1. Base Prediction
        result = self.engine.predict_pair(t1_source, t2_source, use_tta=use_tta)
        
        t1_tensor = self.engine.transform(result["img_t1"], result["img_t2"])[0].unsqueeze(0).to(self.device)
        t2_tensor = self.engine.transform(result["img_t1"], result["img_t2"])[1].unsqueeze(0).to(self.device)

        # 2. XAI Visualizations
        att_rollout = AttentionRolloutExplainer.compute_rollout(self.model, t1_tensor, t2_tensor)
        grad_cam = ViTGradCAM(self.model).generate_cam(t1_tensor, t2_tensor)
        lime_overlay, _ = LimeSuperpixelExplainer.explain_instance(result["img_t1"], result["img_t2"], result["change_mask"])
        shap_scores = ShapFeatureExplainer.compute_shap_attributions(result["img_t1"], result["img_t2"], result["primary_change"])
        ig_map = CaptumExplainer.integrated_gradients(self.model, t1_tensor, t2_tensor)

        result["attention_rollout"] = att_rollout
        result["grad_cam"] = grad_cam
        result["lime_overlay"] = lime_overlay
        result["shap_scores"] = shap_scores
        result["integrated_gradients"] = ig_map

        # 3. AI Insights Synthesis
        ai_narrative = AIInsightsGenerator.generate_narrative(
            primary_change=result["primary_change"],
            affected_percentage=result["affected_percentage"],
            affected_area_sqkm=result["affected_area_sqkm"],
            confidence_score=result["confidence_score"],
            model_name=str(self.model_name)
        )
        result["ai_insights"] = ai_narrative

        # 4. Color Overlays & Difference Map
        result["color_mask"] = ChangeMapVisualizer.create_color_mask(result["change_mask"])
        result["overlay"] = ChangeMapVisualizer.create_overlay(result["img_t2"], result["change_mask"])
        result["difference_map"] = ChangeMapVisualizer.create_difference_map(result["img_t1"], result["img_t2"])

        # 5. Report Generation & DB Recording
        if generate_pdf:
            pdf_path = PDFReportGenerator.generate_report(result)
            result["report_pdf_path"] = pdf_path

        try:
            db = SessionLocal()
            repo = PredictionRepository(db)
            rec = PredictionRecord(
                t1_filename=str(t1_source) if isinstance(t1_source, str) else "uploaded_t1.png",
                t2_filename=str(t2_source) if isinstance(t2_source, str) else "uploaded_t2.png",
                model_used=str(self.model_name),
                primary_change_detected=result["primary_change"],
                confidence_score=result["confidence_score"],
                affected_area_sqkm=result["affected_area_sqkm"],
                affected_percentage=result["affected_percentage"],
                ai_explanation=ai_narrative,
                report_pdf_path=result.get("report_pdf_path")
            )
            repo.create(rec)
            db.close()
        except Exception as e:
            logger.warning(f"Database logging failed: {e}")

        return result
