"""
Inference pipeline.

Loads the persisted best classifier + preprocessing artifacts and
scores new customer records. Used by the Streamlit app and any
batch-inference script.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import numpy as np
import pandas as pd

from src.config_manager import ConfigurationManager
from src.constants import (
    BEST_CLASSIFIER_FILE,
    FEATURE_SELECTOR_FILE,
    SAVED_MODELS_DIR,
)
from src.exception import PredictionError
from src.logger import get_logger
from src.utils import load_object, read_yaml

logger = get_logger(__name__)


@dataclass
class PredictionResult:
    predicted_cluster: int
    cluster_name: str
    probabilities: Dict[str, float]
    confidence: float
    input_features: Dict[str, Any]
    recommendations: List[str]
    cluster_profile: Dict[str, Any]


class PredictPipeline:
    """Load persisted model artifacts and score new customers."""

    def __init__(self, config_manager: Optional[ConfigurationManager] = None) -> None:
        self.config_manager = config_manager or ConfigurationManager()
        self.prediction_schema = self.config_manager.get_prediction_schema()
        self.classifier_path = BEST_CLASSIFIER_FILE
        self.selector_path = FEATURE_SELECTOR_FILE
        self._classifier = None
        self._selector_state = None
        self._feature_names: Optional[List[str]] = None

    # ------------------------------------------------------------------
    # Lazy artifact loading
    # ------------------------------------------------------------------
    @property
    def classifier(self):
        if self._classifier is None:
            if not self.classifier_path.exists():
                raise PredictionError(
                    f"Trained classifier not found at {self.classifier_path}. "
                    "Run `python training.py` first."
                )
            self._classifier = load_object(self.classifier_path)
            logger.info("Classifier loaded from %s", self.classifier_path)
        return self._classifier

    @property
    def selector_state(self):
        if self._selector_state is None:
            if self.selector_path.exists():
                self._selector_state = load_object(self.selector_path)
                self._feature_names = self._selector_state.get("selected_features")
            else:
                self._feature_names = None
        return self._selector_state

    @property
    def feature_names(self) -> List[str]:
        if self._feature_names is None:
            _ = self.selector_state  # trigger load
        if self._feature_names is None:
            # Fall back to prediction schema features
            feats = self.prediction_schema.get("features", [])
            self._feature_names = [f["name"] for f in feats]
        return self._feature_names

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def predict(self, customer: Dict[str, Any]) -> PredictionResult:
        """Predict the customer segment for a single customer record.

        Args:
            customer: Dictionary of feature_name -> value.

        Returns:
            :class:`PredictionResult` with predicted cluster, probabilities
            and business recommendations.
        """
        try:
            validated = self._validate_input(customer)
            df = pd.DataFrame([validated])
            df = self._align_features(df)

            model = self.classifier
            pred = int(model.predict(df)[0])
            try:
                probs = model.predict_proba(df)[0]
                classes = list(model.classes_)
                prob_dict = {str(c): float(p) for c, p in zip(classes, probs)}
                confidence = float(max(probs))
            except Exception:
                prob_dict = {str(pred): 1.0}
                confidence = 1.0

            cluster_profiles = self.prediction_schema.get("cluster_profiles", {})
            profile = cluster_profiles.get(str(pred), cluster_profiles.get(pred, {}))
            cluster_name = profile.get("name", f"Cluster {pred}")
            recommendations = profile.get("recommendations", [])

            return PredictionResult(
                predicted_cluster=pred,
                cluster_name=cluster_name,
                probabilities=prob_dict,
                confidence=confidence,
                input_features=validated,
                recommendations=recommendations,
                cluster_profile=profile,
            )
        except Exception as exc:
            raise PredictionError("Prediction failed.", exc) from exc

    def predict_batch(self, customers: List[Dict[str, Any]]) -> List[PredictionResult]:
        """Score a batch of customer records."""
        return [self.predict(c) for c in customers]

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _validate_input(self, customer: Dict[str, Any]) -> Dict[str, Any]:
        """Coerce input values to expected types based on prediction schema."""
        validated: Dict[str, Any] = {}
        feats = self.prediction_schema.get("features", [])
        for feat in feats:
            name = feat["name"]
            if name not in customer:
                validated[name] = feat.get("default")
                continue
            val = customer[name]
            try:
                if feat["dtype"] == "int":
                    validated[name] = int(val)
                elif feat["dtype"] == "float":
                    validated[name] = float(val)
                else:
                    validated[name] = val
            except Exception:
                validated[name] = feat.get("default")
        return validated

    def _align_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Reorder + fill missing columns to match training feature order."""
        feats = self.feature_names
        for f in feats:
            if f not in df.columns:
                df[f] = 0
        df = df[feats]
        df = df.fillna(0)
        return df
