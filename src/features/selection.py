"""
Feature Selection component.

Selects the top-K most informative features for the supervised
classification task using one of:
* ``mutual_info`` — Mutual Information Classification
* ``chi2`` — Chi-squared test (requires non-negative features)
* ``anova`` — ANOVA F-value
* ``rf_importance`` — Random Forest feature importances
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import (
    SelectKBest,
    mutual_info_classif,
    f_classif,
    chi2,
)

from src.config_manager import ConfigurationManager
from src.constants import TARGET_COLUMN
from src.exception import FeatureSelectionError
from src.logger import get_logger
from src.utils import ensure_dir, save_object

logger = get_logger(__name__)


@dataclass
class FeatureSelectionArtifact:
    selected_features: List[str]
    selector_path: Path
    selected_path: Path
    scores: dict


class FeatureSelector:
    """Rank and select features using a configurable method."""

    SUPPORTED_METHODS = {"mutual_info", "chi2", "anova", "rf_importance"}

    def __init__(self, config_manager: ConfigurationManager) -> None:
        self.config = config_manager.get_feature_selection_config()
        self.method = self.config.method
        self.k_features = self.config.k_features
        self.selected_path = Path(self.config.selected_features_path)
        self.selector_path = Path(self.config.selector_path)
        if self.method not in self.SUPPORTED_METHODS:
            raise FeatureSelectionError(
                f"Unsupported feature selection method '{self.method}'. "
                f"Supported: {self.SUPPORTED_METHODS}"
            )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def initiate_feature_selection(
        self,
        df: pd.DataFrame,
        target_column: str = TARGET_COLUMN,
        drop_columns: Optional[List[str]] = None,
    ) -> FeatureSelectionArtifact:
        """Run feature selection on ``df``.

        Args:
            df: Dataframe containing features + target.
            target_column: Name of the target column.
            drop_columns: Columns to drop before selection (e.g. IDs).

        Returns:
            :class:`FeatureSelectionArtifact` with selected feature list.
        """
        logger.info("Starting feature selection (method=%s, k=%d)", self.method, self.k_features)
        try:
            drop_columns = drop_columns or []
            drop_cols = [c for c in drop_columns if c in df.columns]
            features_df = df.drop(columns=drop_cols, errors="ignore")

            if target_column not in features_df.columns:
                raise FeatureSelectionError(
                    f"Target column '{target_column}' not found in dataframe."
                )

            y = features_df[target_column]
            X = features_df.drop(columns=[target_column])
            # Keep only numeric features for selection
            X = X.select_dtypes(include=[np.number])
            X = X.fillna(X.median())

            scores = self._compute_scores(X, y)
            ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
            k = min(self.k_features, len(ranked))
            selected = [name for name, _ in ranked[:k]]

            selector_state = {
                "method": self.method,
                "k": k,
                "selected_features": selected,
                "scores": scores,
            }
            ensure_dir(self.selector_path.parent)
            save_object(selector_state, self.selector_path)

            selected_df = df[selected + [target_column]]
            ensure_dir(self.selected_path.parent)
            selected_df.to_csv(self.selected_path, index=False)

            logger.info("Selected %d features: %s", len(selected), selected)
            return FeatureSelectionArtifact(
                selected_features=selected,
                selector_path=self.selector_path,
                selected_path=self.selected_path,
                scores=scores,
            )
        except Exception as exc:
            raise FeatureSelectionError(
                "Feature selection failed.", exc
            ) from exc

    # ------------------------------------------------------------------
    def _compute_scores(self, X: pd.DataFrame, y: pd.Series) -> dict:
        if self.method == "mutual_info":
            scores = mutual_info_classif(X, y, random_state=42)
        elif self.method == "chi2":
            X_pos = X.clip(lower=0)
            scores, _ = chi2(X_pos, y)
        elif self.method == "anova":
            scores, _ = f_classif(X.fillna(0), y)
        elif self.method == "rf_importance":
            rf = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)
            rf.fit(X, y)
            scores = rf.feature_importances_
        else:  # pragma: no cover
            raise FeatureSelectionError(f"Method {self.method} not implemented")
        return {col: float(score) for col, score in zip(X.columns, scores)}
