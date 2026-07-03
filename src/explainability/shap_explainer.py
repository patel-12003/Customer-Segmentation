"""
SHAP explainer.

Wraps ``shap.TreeExplainer`` (preferred for tree-based models) and
``shap.KernelExplainer`` (model-agnostic fallback) so that the
Streamlit app can render global and local feature attribution plots.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, Tuple

import numpy as np
import pandas as pd

from src.config_manager import ConfigurationManager
from src.exception import ExplainabilityError
from src.logger import get_logger
from src.utils import ensure_dir, save_object

logger = get_logger(__name__)

try:
    import shap
    _SHAP_AVAILABLE = True
except Exception:  # pragma: no cover
    _SHAP_AVAILABLE = False


@dataclass
class SHAPArtifact:
    shap_values: Any
    explainer: Any
    background: pd.DataFrame
    sample: pd.DataFrame
    path: Path


class SHAPExplainer:
    """Generate and persist SHAP values for a trained classifier."""

    def __init__(self, config_manager: ConfigurationManager) -> None:
        self.config = config_manager.get_explainability_config()
        self.sample_size = self.config.sample_size
        self.shap_path = Path(self.config.shap_path)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def explain(
        self,
        model: Any,
        X: pd.DataFrame,
        sample_size: Optional[int] = None,
    ) -> SHAPArtifact:
        """Compute SHAP values for ``model`` on ``X``.

        Args:
            model: Trained classifier (preferably tree-based).
            X: Feature dataframe.
            sample_size: Override default sample size.

        Returns:
            :class:`SHAPArtifact`.
        """
        if not _SHAP_AVAILABLE:
            logger.warning("SHAP not installed — explainability disabled.")
            return SHAPArtifact(
                shap_values=None,
                explainer=None,
                background=X.iloc[:1],
                sample=X.iloc[:1],
                path=self.shap_path,
            )

        try:
            n = sample_size or min(self.sample_size, len(X))
            sample = X.sample(n=n, random_state=42) if len(X) > n else X.copy()
            background = X.sample(n=min(100, len(X)), random_state=0)

            explainer = self._build_explainer(model, background)
            shap_values = explainer.shap_values(sample)

            ensure_dir(self.shap_path.parent)
            save_object(
                {
                    "shap_values": shap_values,
                    "feature_names": list(sample.columns),
                    "sample_index": sample.index.tolist(),
                },
                self.shap_path,
            )
            logger.info("SHAP values computed for %d samples.", len(sample))
            return SHAPArtifact(
                shap_values=shap_values,
                explainer=explainer,
                background=background,
                sample=sample,
                path=self.shap_path,
            )
        except Exception as exc:
            raise ExplainabilityError(
                "SHAP explanation failed.", exc
            ) from exc

    # ------------------------------------------------------------------
    def _build_explainer(self, model: Any, background: pd.DataFrame) -> Any:
        """Prefer TreeExplainer for tree-based models, else KernelExplainer."""
        try:
            # TreeExplainer supports most tree-based models
            return shap.TreeExplainer(model)
        except Exception:
            try:
                # Use a small background dataset for KernelExplainer
                bg = background.sample(n=min(50, len(background)), random_state=0)
                return shap.KernelExplainer(model.predict_proba, bg)
            except Exception as exc:
                raise ExplainabilityError(
                    "Could not build any SHAP explainer.", exc
                ) from exc

    # ------------------------------------------------------------------
    @staticmethod
    def global_importance(shap_values: Any, feature_names: list) -> pd.DataFrame:
        """Return a DataFrame of mean |SHAP| per feature (global importance)."""
        if shap_values is None:
            return pd.DataFrame(columns=["feature", "importance"])
        try:
            # shap_values can be a list (per class) or a 3-D array
            if isinstance(shap_values, list):
                arr = np.mean([np.abs(sv) for sv in shap_values], axis=0)
            else:
                arr = np.abs(np.asarray(shap_values))
                if arr.ndim == 3:
                    arr = arr.mean(axis=-1)
            means = arr.mean(axis=0)
            return (
                pd.DataFrame({"feature": feature_names, "importance": means})
                .sort_values("importance", ascending=False)
                .reset_index(drop=True)
            )
        except Exception as exc:
            logger.warning("Could not compute SHAP global importance: %s", exc)
            return pd.DataFrame(columns=["feature", "importance"])
