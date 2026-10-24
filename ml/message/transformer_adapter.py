"""Transformer Model Adapter for ScamGraph Message Intelligence.

Wraps specialized models for standardized inference:
1. Horizon-Labs/phishing-scam-detector-base (multilingual, 307M params)
2. Local fine-tuned variants

Provides consistent interface for prediction, probability estimation, and evaluation.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import numpy as np

try:
    import torch
    from transformers import (
        AutoModelForSequenceClassification,
        AutoTokenizer,
        pipeline,
    )

    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning(
        "transformers not installed. "
        "Install with: pip install transformers torch"
    )

logger = logging.getLogger(__name__)


class TransformerMessageClassifier:
    """Unified interface for transformer-based message classification."""

    def __init__(
        self,
        model_id: str = "Horizon-Labs/phishing-scam-detector-base",
        device: str = "auto",
        batch_size: int = 32,
    ):
        """
        Args:
            model_id: HuggingFace model identifier
            device: Computation device ('auto', 'cpu', 'cuda')
            batch_size: Batch size for inference
        """
        if not TRANSFORMERS_AVAILABLE:
            raise RuntimeError(
                "transformers library not installed. "
                "Install with: pip install transformers torch"
            )

        self.model_id = model_id
        self.device = device
        self.batch_size = batch_size
        self.is_loaded = False

        self.tokenizer = None
        self.model = None
        self.pipeline = None

    def load(self) -> TransformerMessageClassifier:
        """Load model and tokenizer from HuggingFace."""
        logger.info(f"Loading transformer model: {self.model_id}")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            self.model_id, device_map=self.device
        )
        self.pipeline = pipeline(
            "text-classification",
            model=self.model,
            tokenizer=self.tokenizer,
            device_map=self.device,
            batch_size=self.batch_size,
        )
        self.is_loaded = True
        logger.info(f"Successfully loaded {self.model_id}")
        return self

    def predict(self, texts: List[str], threshold: float = 0.5) -> List[int]:
        """Predict 0 (ham) or 1 (scam) with configurable threshold.
        
        Args:
            texts: List of message texts
            threshold: Probability threshold for positive class
            
        Returns:
            List of predictions (0 or 1)
        """
        if not self.is_loaded:
            raise RuntimeError("Model not loaded. Call load() first.")

        probs = self.predict_proba(texts)[:, 1]
        return [1 if p >= threshold else 0 for p in probs]

    def predict_proba(self, texts: List[str]) -> np.ndarray:
        """Return [ham_prob, scam_prob] for each text.
        
        Args:
            texts: List of message texts
            
        Returns:
            Array of shape (len(texts), 2) with probabilities
        """
        if not self.is_loaded:
            raise RuntimeError("Model not loaded. Call load() first.")

        results = self.pipeline(texts, top_k=None)

        # Normalize scores to probabilities [0, 1]
        probs = []
        for result in results:
            # Result is a list of dicts: [{"label": "...", "score": ...}, ...]
            # Map label to index: "LABEL_0" -> class 0, "LABEL_1" -> class 1, etc.
            label_scores = {}
            for item in result:
                label_str = item["label"]  # e.g., "LABEL_0", "LABEL_1"
                score = float(item["score"])
                try:
                    # Extract numeric label
                    label_idx = int(label_str.split("_")[-1])
                    label_scores[label_idx] = score
                except (ValueError, IndexError):
                    pass

            # Ensure we have both classes (0 and 1)
            if 0 not in label_scores:
                label_scores[0] = 0.0
            if 1 not in label_scores:
                label_scores[1] = 0.0

            # Normalize so they sum to 1
            total = label_scores[0] + label_scores[1]
            if total > 0:
                probs.append(
                    [
                        label_scores[0] / total,
                        label_scores[1] / total,
                    ]
                )
            else:
                probs.append([0.5, 0.5])

        return np.array(probs)

    def predict_single(self, text: str) -> Dict[str, Any]:
        """Classify single message with detailed output."""
        if not self.is_loaded:
            raise RuntimeError("Model not loaded. Call load() first.")

        probs = self.predict_proba([text])[0]
        ham_prob = float(probs[0])
        scam_prob = float(probs[1])
        predicted_label = 1 if scam_prob >= 0.5 else 0

        confidence = float(min(1.0, abs(scam_prob - 0.5) * 2.0))

        return {
            "label": "scam" if predicted_label == 1 else "ham",
            "is_scam": bool(predicted_label == 1),
            "scam_probability": round(scam_prob, 4),
            "ham_probability": round(ham_prob, 4),
            "confidence": round(confidence, 4),
        }

    def unload(self) -> None:
        """Release model from memory."""
        if torch is not None and self.model is not None:
            self.model.cpu()
            del self.model
            del self.tokenizer
            del self.pipeline
            torch.cuda.empty_cache()
        self.is_loaded = False
        logger.info("Model unloaded from memory")


# Pre-configured model instances
RECOMMENDED_MODELS = {
    "phishing_scam_detector_base": {
        "model_id": "Horizon-Labs/phishing-scam-detector-base",
        "description": "Multilingual phishing/scam detector (307M params)",
        "languages": ["en", "hi", "hinglish", "ta_en", "te_en"],
    },
    "distilbert_scam_india": {
        "model_id": "anmolshrivastav/distilbert-scam-detector-india",
        "description": "DistilBERT fine-tuned on Indian scam SMS",
        "languages": ["en", "hi", "hinglish"],
    },
}


def load_recommended_model(
    model_key: str = "phishing_scam_detector_base",
    device: str = "auto",
) -> TransformerMessageClassifier:
    """Load a pre-configured recommended model.
    
    Args:
        model_key: Key from RECOMMENDED_MODELS
        device: Computation device
        
    Returns:
        Loaded TransformerMessageClassifier instance
    """
    if model_key not in RECOMMENDED_MODELS:
        raise ValueError(
            f"Unknown model key: {model_key}. "
            f"Available: {list(RECOMMENDED_MODELS.keys())}"
        )

    config = RECOMMENDED_MODELS[model_key]
    classifier = TransformerMessageClassifier(
        model_id=config["model_id"],
        device=device,
    )
    classifier.load()
    return classifier
