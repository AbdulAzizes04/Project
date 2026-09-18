"""
Sleep Disorder AI - Prediction Coordinator Service
Coordinates ML inference, SHAP XAI calculation, Gemini recommendations,
and SQLite persistence.
"""
import json
import logging
from datetime import datetime
from ml.predict import SleepPredictor
from services.gemini_service import GeminiService
from database.models import db, Assessment, Prediction, Explanation, Recommendation

logger = logging.getLogger(__name__)

class PredictionService:
    def __init__(self):
        self.predictor = SleepPredictor()
        self.gemini_service = GeminiService()

    def validate_input(self, data):
        """
        Validates incoming data fields and ensures numeric ranges are safe.
        Returns: (is_valid, errors_dict)
        """
        errors = {}
        
        try:
            age = float(data.get("Age", 0))
            if age < 18 or age > 100:
                errors["Age"] = "Age must be between 18 and 100 years."
        except (ValueError, TypeError):
            errors["Age"] = "Age must be a valid number."

        try:
            sleep_duration = float(data.get("Sleep Duration", 0))
            if sleep_duration < 3.0 or sleep_duration > 14.0:
                errors["Sleep Duration"] = "Sleep duration must be between 3.0 and 14.0 hours."
        except (ValueError, TypeError):
            errors["Sleep Duration"] = "Sleep duration must be a valid number."

        try:
            quality = int(data.get("Quality of Sleep", 0))
            if quality < 1 or quality > 10:
                errors["Quality of Sleep"] = "Quality of Sleep must be an integer between 1 and 10."
        except (ValueError, TypeError):
            errors["Quality of Sleep"] = "Quality of Sleep must be a number."

        try:
            stress = int(data.get("Stress Level", 0))
            if stress < 1 or stress > 10:
                errors["Stress Level"] = "Stress Level must be an integer between 1 and 10."
        except (ValueError, TypeError):
            errors["Stress Level"] = "Stress Level must be a number."

        try:
            activity = int(data.get("Physical Activity Level", 0))
            if activity < 0 or activity > 300:
                errors["Physical Activity Level"] = "Physical Activity Level must be between 0 and 300 minutes/day."
        except (ValueError, TypeError):
            errors["Physical Activity Level"] = "Physical Activity Level must be a number."

        try:
            systolic = float(data.get("Systolic_BP", 0))
            if systolic < 70 or systolic > 220:
                errors["Systolic_BP"] = "Systolic BP must be between 70 and 220 mmHg."
        except (ValueError, TypeError):
            errors["Systolic_BP"] = "Systolic BP must be a valid number."

        try:
            diastolic = float(data.get("Diastolic_BP", 0))
            if diastolic < 40 or diastolic > 140:
                errors["Diastolic_BP"] = "Diastolic BP must be between 40 and 140 mmHg."
        except (ValueError, TypeError):
            errors["Diastolic_BP"] = "Diastolic BP must be a valid number."

        try:
            hr = int(data.get("Heart Rate", 0))
            if hr < 40 or hr > 160:
                errors["Heart Rate"] = "Resting Heart Rate must be between 40 and 160 bpm."
        except (ValueError, TypeError):
            errors["Heart Rate"] = "Heart Rate must be a valid number."

        try:
            steps = int(data.get("Daily Steps", 0))
            if steps < 500 or steps > 30000:
                errors["Daily Steps"] = "Daily Steps must be between 500 and 30,000."
        except (ValueError, TypeError):
            errors["Daily Steps"] = "Daily Steps must be a number."

        return len(errors) == 0, errors

    def process_assessment(self, user_id, user_input_data):
        """
        Full assessment workflow:
        1. ML Prediction
        2. SHAP Explainability
        3. Gemini Recommendation Generation
        4. DB Persistence
        """
        # 1 & 2: Inference & SHAP
        pred_result = self.predictor.predict(user_input_data, generate_shap=True)
        
        # 3: Gemini Health Recommendations
        try:
            recommendations_text = self.gemini_service.generate_recommendations(pred_result)
        except Exception as e:
            logger.error(f"Error calling Gemini: {e}")
            recommendations_text = self.gemini_service._generate_fallback_recommendations(pred_result)
            
        # 4: Save to Database
        assessment = Assessment(
            user_id=user_id,
            assessment_date=datetime.utcnow(),
            input_data=json.dumps(pred_result["input_summary"]),
            predicted_class=pred_result["predicted_class"],
            confidence=pred_result["confidence"],
            model_name=pred_result["model_used"]
        )
        db.session.add(assessment)
        db.session.flush()  # populate assessment.id
        
        # Save class probabilities
        for class_name, prob in pred_result["probabilities"].items():
            p_obj = Prediction(
                assessment_id=assessment.id,
                class_name=class_name,
                probability=prob
            )
            db.session.add(p_obj)
            
        # Save SHAP top features
        top_features = pred_result["explanation"]["top_features"]
        for feat in top_features:
            e_obj = Explanation(
                assessment_id=assessment.id,
                feature_name=feat["feature_name"],
                shap_value=feat["shap_value"],
                contribution_type=feat["direction"]
            )
            db.session.add(e_obj)
            
        # Save recommendation
        rec_obj = Recommendation(
            assessment_id=assessment.id,
            recommendation_text=recommendations_text
        )
        db.session.add(rec_obj)
        
        db.session.commit()
        
        pred_result["assessment_id"] = assessment.id
        pred_result["recommendations_text"] = recommendations_text
        return pred_result
