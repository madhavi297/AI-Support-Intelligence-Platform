"""
Inference service for ticket classification using Scikit-learn model artifact.
Loads the serialized pipeline (TF-IDF + LogisticRegression) and computes category probabilities.
"""

import os
import joblib
from pathlib import Path
from typing import Dict, Any, Tuple
from app.config import settings

MODEL_PATH = settings.MODELS_DIR / "classifier.joblib"


class TicketClassifierService:
    """
    Manages model loading and prediction inference for support ticket categorization.
    """

    def __init__(self, model_path: Path = MODEL_PATH):
        self.model_path = model_path
        self.model = None
        self._load_model()

    def _load_model(self) -> None:
        """Loads serialized model pipeline from disk if available."""
        if self.model_path.exists():
            try:
                self.model = joblib.load(self.model_path)
            except Exception as e:
                print(f"[ClassifierService] Error loading model artifact from {self.model_path}: {e}")
                self.model = None
        else:
            print(f"[ClassifierService] Warning: Model artifact not found at {self.model_path}")
            self.model = None

    def is_ready(self) -> bool:
        """Returns True if the ML model pipeline is loaded and ready for inference."""
        return self.model is not None

    def predict(self, title: str, description: str) -> Dict[str, Any]:
        """
        Predicts ticket category and class probability distribution.
        
        Args:
            title: Ticket subject line
            description: Detailed problem description
            
        Returns:
            Dictionary containing:
                - predicted_category: str
                - confidence: float (0.0 to 1.0)
                - probabilities: Dict[str, float]
        """
        combined_text = f"{title.strip()} {description.strip()}"
        if not combined_text.strip():
            return {
                "predicted_category": "General Inquiry",
                "confidence": 0.25,
                "probabilities": {
                    "Account Access": 0.25,
                    "Billing": 0.25,
                    "General Inquiry": 0.25,
                    "Technical Issue": 0.25
                }
            }

        if self.model is None:
            self._load_model()
            if self.model is None:
                # Safe baseline heuristic fallback if model file is missing
                return {
                    "predicted_category": "General Inquiry",
                    "confidence": 0.5,
                    "probabilities": {"General Inquiry": 1.0}
                }

        # Predict probabilities
        classes = self.model.classes_
        probs = self.model.predict_proba([combined_text])[0]
        
        prob_dict = {str(cls_name): round(float(prob), 4) for cls_name, prob in zip(classes, probs)}
        best_idx = probs.argmax()
        predicted_category = str(classes[best_idx])
        confidence = round(float(probs[best_idx]), 4)

        return {
            "predicted_category": predicted_category,
            "confidence": confidence,
            "probabilities": prob_dict
        }


# Global singleton instance for memory-efficient inference
_classifier_instance: TicketClassifierService = None


def get_classifier() -> TicketClassifierService:
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = TicketClassifierService()
    return _classifier_instance
