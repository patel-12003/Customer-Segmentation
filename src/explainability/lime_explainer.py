"""
LIME explainer.

Provides local, instance-level explanations using ``lime.lime_tabular``.
LIME is an optional dependency — if missing, the explainer returns
``None`` for the explanation object.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import numpy as np
import pandas as pd

from src.config_manager import ConfigurationManager
from src.exception import ExplainabilityError
from src.logger import get_logger
from src.utils import ensure_dir, save_object

logger = get_logger(__name__)

try:
    from lime.lime_tabular import LimeTabularExplainer
    _LIME_AVAILABLE = True
except Exception:  # pragma: no cover
    _LIME_AVAILABLE = False


@dataclass
class LIMEArtifact:
    explainer: Optional[Any]
    path: Path
    sample_explanations: list


class LIMEExplainer:
    """Build a LIME explainer and produce per-instance explanations."""

    def __init__(self, config_manager: ConfigurationManager) -> None:
        self.config = config_manager.get_explainability_config()
        params = config_manager.get_params().get("explainability", {})
        self.sample_size = params.get("shap_sample_size", 200)
        self.num_features = params.get("lime_num_features", 10)
        self.lime_path = Path(self.config.lime_path)

    # ------------------------------------------------------------------
    def explain(
        self,
        model: Any,
        X: pd.DataFrame,
        y: Optional[pd.Series] = None,
        class_names: Optional[list] = None,
        n_instances: int = 5,
    ) -> LIMEArtifact:
        """Build LIME explainer and explain ``n_instances`` samples.

        Args:
            model: Trained classifier with ``predict_proba``.
            X: Feature dataframe.
            y: Optional target series.
            class_names: Optional list of class name strings.
            n_instances: Number of instances to explain.

        Returns:
            :class:`LIMEArtifact`.
        """
        if not _LIME_AVAILABLE:
            logger.warning("LIME not installed — explainability disabled.")
            return LIMEArtifact(
                explainer=None,
                path=self.lime_path,
                sample_explanations=[],
            )
        try:
            feature_names = list(X.columns)
            training_data = X.fillna(0).values
            mode = "classification"
            explainer = LimeTabularExplainer(
                training_data=training_data,
                feature_names=feature_names,
                class_names=class_names or sorted(set(y if y is not None else [])),
                mode=mode,
                discretize_continuous=True,
                random_state=42,
            )

            sample = X.sample(n=min(n_instances, len(X)), random_state=42).fillna(0)
            explanations: list = []
            for idx, row in sample.iterrows():
                arr = row.values.reshape(1, -1)
                try:
                    exp = explainer.explain_instance(
                        data_row=row.values,
                        predict_fn=lambda x: model.predict_proba(pd.DataFrame(x, columns=feature_names)),
                        num_features=min(self.num_features, len(feature_names)),
                        top_labels=1,
                    )
                    pred_class = int(np.argmax(model.predict_proba(arr)[0]))
                    explanations.append(
                        {
                            "index": int(idx),
                            "as_list": exp.as_list(),
                            "as_pyplot_figure": None,
                            "predicted_class": pred_class,
                        }
                    )
                except Exception as exc:
                    logger.warning("LIME failed for instance %s: %s", idx, exc)
                    continue
            ensure_dir(self.lime_path.parent)
            # Only persist the explanations (the explainer contains unpicklable lambdas)
            save_object(
                {"explanations": explanations, "feature_names": feature_names},
                self.lime_path,
            )
            logger.info("LIME explained %d instances.", len(explanations))
            return LIMEArtifact(
                explainer=explainer,
                path=self.lime_path,
                sample_explanations=explanations,
            )
        except Exception as exc:
            raise ExplainabilityError(
                "LIME explanation failed.", exc
            ) from exc
