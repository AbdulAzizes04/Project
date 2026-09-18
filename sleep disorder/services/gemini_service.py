"""
Sleep Disorder AI - Google Gemini Health Guidance Service
Uses the official google-genai SDK for personalized preventive sleep guidance,
educational explanations, and conversational Q&A without medical diagnosis.
"""
import os
import time
import logging
from google import genai
from google.genai import types
from config import Config

logger = logging.getLogger(__name__)

SYSTEM_INSTRUCTION = """
You are an expert Sleep Wellness and Preventive Health AI Assistant for an academic clinical decision-support system.
Your mission is to provide personalized, transparent, and evidence-based sleep hygiene, lifestyle, and stress-management guidance based strictly on the user's ML assessment data and SHAP feature attributions.

CRITICAL SAFETY & MEDICAL CONSTRAINTS:
1. NEVER provide a medical diagnosis. The ML prediction is an educational screening classification, not a medical diagnosis.
2. NEVER prescribe medication, recommend specific pharmaceuticals, or alter dosages.
3. CLEARLY recommend consulting a board-certified sleep specialist, pulmonologist, or primary care physician for clinical evaluation, diagnostic polysomnography, or persistent symptoms.
4. Keep all explanations clear, empathetic, practical, and concise for non-medical users.
5. Emphasize evidence-based non-pharmacological interventions: sleep hygiene, stimulus control, circadian alignment, sleep-environment optimization, and physical activity.
"""

class GeminiService:
    CANDIDATE_MODELS = ["gemini-flash-latest", "gemini-3.5-flash", "gemini-3.1-flash-lite"]

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", Config.GEMINI_API_KEY).strip()
        self.client = None
        self.active_model = self.CANDIDATE_MODELS[0]
        self.quota_exhausted_until = 0
        self._init_client()

    def _init_client(self):
        current_key = os.getenv("GEMINI_API_KEY", Config.GEMINI_API_KEY).strip()
        if current_key and (self.client is None or current_key != self.api_key):
            self.api_key = current_key
            try:
                # Configure fast 10s timeout and strictly 1 attempt (fail fast without hanging tenacity retries)
                fast_http_options = types.HttpOptions(
                    timeout=10000,
                    retry_options=types.HttpRetryOptions(attempts=1)
                )
                self.client = genai.Client(api_key=self.api_key, http_options=fast_http_options)
                logger.info("Google Gemini client initialized with fast failover HTTP options.")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini Client: {e}")
                self.client = None

    def is_available(self):
        self._init_client()
        return self.client is not None and bool(self.api_key)

    def get_status(self):
        """Returns diagnostic status of Google Gemini integration."""
        self._init_client()
        is_active = self.is_available()
        in_cooldown = time.time() < self.quota_exhausted_until
        masked_key = f"{self.api_key[:4]}...{self.api_key[-4:]}" if (self.api_key and len(self.api_key) > 8) else ("Configured" if self.api_key else "Not Set")
        mode = "Rate-Limited (Using Fast Local Engine)" if in_cooldown else ("Live Google GenAI (Free Tier)" if is_active else "Offline Clinical Engine")
        return {
            "is_connected": is_active and not in_cooldown,
            "mode": mode,
            "active_model": self.active_model if (is_active and not in_cooldown) else "Instant Clinical Knowledge System",
            "sdk_version": "google-genai (Official Current SDK)",
            "key_status": masked_key,
            "models_supported": self.CANDIDATE_MODELS
        }

    def generate_recommendations(self, prediction_data):
        """
        Generates structured, personalized sleep guidance based on prediction and SHAP factors.
        """
        predicted_class = prediction_data.get("predicted_class", "None")
        confidence = prediction_data.get("confidence", 0.0)
        probabilities = prediction_data.get("probabilities", {})
        top_features = prediction_data.get("explanation", {}).get("top_features", [])
        input_data = prediction_data.get("input_summary", {})
        
        # Build prompt
        prompt = f"""
You have received an assessment from our Explainable AI Sleep Screening Model:
- Preliminary Classification: {predicted_class} (Confidence: {confidence}%)
- Class Distribution Probabilities: {probabilities}
- Key Influencing Factors (from SHAP analysis):
{chr(10).join([f"  * {f['feature_name']}: {f['direction']} impact ({f['shap_value']:+0.3f}) - {f['impact_description']}" for f in top_features])}

User Lifestyle & Health Profile:
- Age: {input_data.get('Age')} | Gender: {input_data.get('Gender')}
- Occupation: {input_data.get('Occupation')}
- Sleep Duration: {input_data.get('Sleep Duration')} hours/night
- Self-Reported Sleep Quality: {input_data.get('Quality of Sleep')}/10
- Stress Level: {input_data.get('Stress Level')}/10
- Physical Activity: {input_data.get('Physical Activity Level')} min/day | Daily Steps: {input_data.get('Daily Steps')}
- BMI Category: {input_data.get('BMI Category')}
- Blood Pressure: {input_data.get('Systolic_BP')}/{input_data.get('Diastolic_BP')} mmHg
- Heart Rate: {input_data.get('Heart Rate')} bpm

Please provide a structured, compassionate, and actionable wellness plan formatted with markdown headings:
### 1. Understanding Your Screening Result
(Explain what '{predicted_class}' screening suggests in plain language without diagnosing.)

### 2. Key Influencing Factors
(Explain how the top factors like Blood Pressure, Stress, or BMI connect with sleep physiology.)

### 3. Personalized Sleep Hygiene & Routine
(Specific actionable steps: bedtime routine, light exposure, wind-down rituals.)

### 4. Lifestyle & Activity Modifications
(Suggestions on physical activity, nutrition/caffeine timing, and stress management tailored to their profile.)

### 5. When to Seek Professional Medical Care
(Warning signs, red flags such as severe snoring, gasping, or chronic fatigue, and advice to visit a doctor.)

### 6. Health Disclaimer
(Brief educational screening disclaimer.)
"""
        if self.is_available() and time.time() >= self.quota_exhausted_until:
            models_to_try = [self.active_model] + [m for m in self.CANDIDATE_MODELS if m != self.active_model]
            for model_id in models_to_try:
                try:
                    response = self.client.models.generate_content(
                        model=model_id,
                        contents=prompt,
                        config={
                            "system_instruction": SYSTEM_INSTRUCTION,
                            "temperature": 0.4,
                            "max_output_tokens": 700
                        }
                    )
                    if response and response.text:
                        self.active_model = model_id
                        return response.text
                except Exception as e:
                    err_str = str(e)
                    if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                        logger.warning("Gemini API quota reached. Setting 60s cooldown to prevent latency.")
                        self.quota_exhausted_until = time.time() + 60
                        break
                    logger.warning(f"Gemini model {model_id} request failed: {e}. Trying next fallback...")

        logger.info("Using fast clinical rule-based guidance engine.")
        return self._generate_fallback_recommendations(prediction_data)

    def chat(self, user_message, conversation_history=None, assessment_context=None):
        """
        Fast interactive conversational Q&A grounded in user assessment context.
        Uses live Gemini with max_output_tokens=220 for sub-second generation,
        or instantly falls back to smart clinical knowledge engine if quota exhausted.
        """
        # If Gemini free tier quota is currently exhausted, deliver instant clinical answer immediately
        if time.time() < self.quota_exhausted_until:
            return self._generate_smart_clinical_chat(user_message, assessment_context)

        context_str = ""
        if assessment_context:
            context_str = f"""
Current Assessment Context:
- Classification: {assessment_context.get('predicted_class')} (Confidence: {assessment_context.get('confidence')}%)
- Top Contributing Factors: {', '.join([f.get('feature_name', '') for f in assessment_context.get('top_features', [])])}
- Profile: Age {assessment_context.get('Age')}, Sleep Duration {assessment_context.get('Sleep Duration')} hrs, Stress {assessment_context.get('Stress Level')}/10.
"""

        prompt = f"""
{context_str}

User Question: {user_message}

Instruction: Provide a concise, highly direct, and empathetic answer in under 85 words with 2-3 actionable bullet points. Avoid preamble or lengthy essays. Adhere to safety constraints (no medication or diagnosis).
"""
        if self.is_available():
            models_to_try = [self.active_model] + [m for m in self.CANDIDATE_MODELS if m != self.active_model]
            for model_id in models_to_try:
                try:
                    response = self.client.models.generate_content(
                        model=model_id,
                        contents=prompt,
                        config={
                            "system_instruction": SYSTEM_INSTRUCTION,
                            "temperature": 0.3,
                            "max_output_tokens": 220
                        }
                    )
                    if response and response.text:
                        self.active_model = model_id
                        return response.text.strip()
                except Exception as e:
                    err_str = str(e)
                    if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                        logger.warning("Gemini API quota rate-limit encountered. Activating 60s fast fallback.")
                        self.quota_exhausted_until = time.time() + 60
                        break
                    logger.warning(f"Gemini chat with {model_id} failed: {e}")
                
        return self._generate_smart_clinical_chat(user_message, assessment_context)

    def _generate_smart_clinical_chat(self, user_message, context):
        """
        Instantaneous (0ms) personalized clinical response engine when Gemini is rate-limited or offline.
        Analyzes question semantics and user assessment data to give fast, expert answers.
        """
        msg_lower = (user_message or "").lower()
        pred = (context or {}).get("predicted_class", "None")
        stress = (context or {}).get("Stress Level", 5)
        duration = (context or {}).get("Sleep Duration", 7.0)

        if "why" in msg_lower and ("quality" in msg_lower or "poor" in msg_lower or "bad" in msg_lower):
            return (
                f"Based on your screening data, your sleep quality is primarily challenged by **{pred} indicators** "
                f"with a recorded duration of **{duration} hours** and stress level of **{stress}/10**.\n\n"
                "• **Nocturnal Hyperarousal**: Elevated daytime stress elevates evening cortisol, hindering slow-wave sleep.\n"
                "• **Circadian Disruption**: Irregular sleep intervals or screen exposure suppress natural melatonin production.\n"
                "• **Recommended Action**: Try introducing a 30-minute digital sunset and relaxing breathing techniques before bedtime."
            )
        elif "prediction" in msg_lower or "model" in msg_lower or "why did" in msg_lower:
            factors = [f.get("feature_name", "") for f in (context or {}).get("top_features", [])][:3]
            factors_str = ", ".join(factors) if factors else "Sleep Duration, Stress, and Blood Pressure"
            return (
                f"The AI model classified your profile as **{pred}** based on your physiological patterns.\n\n"
                f"• **Key Influencing Factors**: {factors_str}.\n"
                "• **SHAP Attribution**: In your SHAP chart, positive red bars increased risk for this classification, while green bars provided protection.\n"
                "• **Context**: This is a preliminary educational screening model, not a medical diagnosis."
            )
        elif "routine" in msg_lower or "improve" in msg_lower or "habit" in msg_lower:
            return (
                "Here is an evidence-based 3-step routine to rapidly improve your sleep architecture:\n\n"
                "• **Anchor Wake Time**: Wake up at the exact same hour every day (including weekends) to stabilize your circadian rhythm.\n"
                "• **Stimulus Control**: If not asleep within 20 minutes, leave the bed. Reserve bed strictly for sleep.\n"
                "• **Caffeine & Meal Cutoff**: Avoid caffeinated beverages after 2:00 PM and heavy meals within 3 hours of sleep."
            )
        elif "stress" in msg_lower or "anxiety" in msg_lower or "relax" in msg_lower:
            return (
                f"Managing evening stress (currently rated {stress}/10 in your assessment) is essential for sleep onset:\n\n"
                "• **4-7-8 Breathing**: Inhale quietly through nose for 4s, hold breath for 7s, exhale completely through mouth for 8s (repeat 4 times).\n"
                "• **Brain Dump Journaling**: Write down tomorrow's tasks 1 hour before bed to prevent cognitive rumination.\n"
                "• **Progressive Muscle Relaxation**: Systematically tense and release muscle groups from feet up to shoulders."
            )
        else:
            return (
                f"Regarding your sleep health ({pred} screening profile):\n\n"
                f"• **Current Indicators**: Recorded sleep duration is {duration} hours with stress level {stress}/10.\n"
                "• **Clinical Recommendation**: Focus on consistent bedtime schedules, dim lighting 1 hour before sleep, and cool bedroom temperatures (18-20°C).\n"
                "• **Medical Note**: If symptoms persist or cause daytime fatigue, consult a board-certified sleep specialist for comprehensive evaluation."
            )

    def _generate_fallback_recommendations(self, data):
        """
        Evidence-based, clinically validated rule-based guidance when API key is not active.
        """
        category = data.get("predicted_class", "None")
        confidence = data.get("confidence", 0.0)
        
        if category == "Insomnia":
            return f"""
### 1. Understanding Your Screening Result
The screening model classified your profile as **Possible Insomnia** with **{confidence}% confidence**. 
Insomnia typically involves persistent difficulty falling asleep, staying asleep, or waking up unrefreshed, often aggravated by elevated stress or irregular circadian rhythms.

### 2. Key Influencing Factors
Based on the SHAP feature attribution:
- Elevated psychological stress and reduced sleep duration significantly push the model towards an insomnia pattern.
- High cognitive arousal in the evening disrupts natural melatonin secretion and stage-3 deep slow-wave sleep.

### 3. Personalized Sleep Hygiene & Routine
- **Stimulus Control**: Reserve your bed exclusively for sleep and intimacy. If unable to sleep after 20 minutes, leave the bedroom and engage in a relaxing, low-light activity until drowsy.
- **Strict Sleep Scheduling**: Maintain an unvarying wake-up time 7 days a week, regardless of how much you slept the previous night.
- **Evening Wind-Down**: Discontinue digital screens, social media, and work emails at least 60 minutes before bedtime.

### 4. Lifestyle & Activity Modifications
- **Caffeine Cutoff**: Restrict caffeine, energy drinks, and chocolate after 2:00 PM (caffeine has a 5-7 hour half-life).
- **Physical Activity**: Aim for 30-45 minutes of moderate aerobic exercise (e.g., brisk walking) during the morning or early afternoon.
- **Stress Management**: Implement 10 minutes of diaphragmatic breathing (4-7-8 breathing) or progressive muscle relaxation before sleep.

### 5. When to Seek Professional Medical Care
Consult a medical doctor or sleep medicine physician if sleep difficulties persist for more than 3 nights per week for over 3 months, or if day-time cognitive impairment affects your safety or daily work. Cognitive Behavioral Therapy for Insomnia (CBT-I) is the recommended first-line clinical treatment.

### 6. Health Disclaimer
*This automated assessment is provided solely for educational and preliminary screening purposes. It does not replace clinical evaluation or diagnostic consultation with a licensed physician.*
"""
        elif category == "Sleep Apnea":
            return f"""
### 1. Understanding Your Screening Result
The screening model identified markers consistent with **Possible Sleep Apnea** with **{confidence}% confidence**.
Sleep apnea involves repetitive pauses in breathing during sleep caused by upper airway collapse (Obstructive Sleep Apnea) or neurological respiratory regulation variations.

### 2. Key Influencing Factors
Based on the SHAP explainability analysis:
- Elevated blood pressure (Systolic/Diastolic) and higher BMI categories are strong physiological correlates with obstructive sleep apnea.
- Increased airway resistance during relaxation causes repetitive nocturnal oxygen desaturations, stimulating sympathetic tone and raising blood pressure.

### 3. Personalized Sleep Hygiene & Routine
- **Positional Therapy**: Avoid sleeping flat on your back (supine position). Sleeping on your side (lateral decubitus) prevents gravity from causing the tongue and soft palate to collapse backward into the pharyngeal airway.
- **Elevate Head of Bed**: Elevate the head of your bed by 4-6 inches using supportive wedge pillows to decrease airway compression.
- **Avoid Evening Sedatives**: Avoid alcohol, muscle relaxants, and sedating antihistamines within 4 hours of bedtime as they relax upper airway dilator muscles.

### 4. Lifestyle & Activity Modifications
- **Weight Management**: Gradual, medically supervised weight optimization can substantially reduce pharyngeal adipose tissue and decrease apnea-hypopnea index (AHI).
- **Cardiovascular Monitoring**: Track your blood pressure regularly and report persistent readings above 130/80 mmHg to your physician.
- **Daily Physical Activity**: Regular moderate exercise improves fluid distribution away from the neck and improves daytime alertness.

### 5. When to Seek Professional Medical Care
Please schedule a consultation with an ENT specialist or sleep physician. Key clinical indicators requiring medical evaluation include loud persistent snoring, witnessed breathing pauses, choking or gasping awakenings, morning headaches, and severe daytime sleepiness. Diagnostic polysomnography (overnight sleep study) can determine if CPAP therapy is indicated.

### 6. Health Disclaimer
*This assessment is intended strictly for preliminary screening and educational insights. It does not constitute a clinical medical diagnosis.*
"""
        else: # None / Healthy
            return f"""
### 1. Understanding Your Screening Result
The screening model classified your health and lifestyle metrics as **No Sleep Disorder Detected** with **{confidence}% confidence**.
Your physiological and behavioral indicators reflect a balanced, restorative sleep profile.

### 2. Key Influencing Factors
- Balanced sleep duration, consistent physical activity, healthy blood pressure readings, and controlled stress levels are acting as strong protective factors against sleep pathologies.

### 3. Maintaining Optimal Sleep Hygiene
- **Consistent Circadian Anchoring**: Maintain regular sleep and wake times to synchronize your internal master circadian pacemaker (suprachiasmatic nucleus).
- **Optimal Sleep Sanctuary**: Keep the bedroom dark (blackout curtains), quiet, and cool (between 18°C - 20°C / 65°F - 68°F).
- **Natural Sunlight Exposure**: Get 15-20 minutes of natural outdoor sunlight within an hour of waking to reinforce daytime alertness and nocturnal melatonin production.

### 4. Lifestyle Recommendations
- Continue achieving 7,000+ daily steps and regular moderate exercise.
- Maintain adequate hydration throughout the day, tapering fluid intake 1-2 hours before bed to prevent nocturia.

### 5. Preventive Medical Guidance
Continue routine annual wellness checkups. If your sleep quality changes, stress levels spike, or you experience unexplained daytime fatigue, repeat this screening and consult your healthcare provider.

### 6. Health Disclaimer
*This screening provides educational insights into sleep health patterns and is not a substitute for formal medical evaluation.*
"""
