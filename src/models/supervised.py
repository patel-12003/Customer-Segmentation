"""
Supervised model trainer.

Trains and compares 11 supervised classifiers on the cluster labels:

* RandomForest
* ExtraTrees
* XGBoost
* LightGBM
* CatBoost
* HistGradientBoosting
* GradientBoosting
* AdaBoost
* Bagging
* Voting (ensemble of best 3 base learners)
* Stacking (meta-learner over best 3 base learners)

Each model is evaluated with stratified cross-validation. The best
model (highest mean CV accuracy) is selected and persisted along with
the per-model metrics.
"""

from __future__ import annotations

import time
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import (
    AdaBoostClassifier,
    BaggingClassifier,
    ExtraTreesClassifier,
    GradientBoostingClassifier,
    HistGradientBoostingClassifier,
    RandomForestClassifier,
    StackingClassifier,
    VotingClassifier,
)
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    log_loss,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_predict, train_test_split

from src.config_manager import ConfigurationManager
from src.exception import SupervisedModelError
from src.logger import get_logger
from src.utils import ensure_dir, save_object, write_json

logger = get_logger(__name__)

# Optional gradient boosting libraries
try:
    from xgboost import XGBClassifier
    _XGB_AVAILABLE = True
except Exception:  # pragma: no cover
    _XGB_AVAILABLE = False

try:
    from lightgbm import LGBMClassifier
    _LGBM_AVAILABLE = True
except Exception:  # pragma: no cover
    _LGBM_AVAILABLE = False

try:
    from catboost import CatBoostClassifier
    _CATBOOST_AVAILABLE = True
except Exception:  # pragma: no cover
    _CATBOOST_AVAILABLE = False


@dataclass
class ModelResult:
    """Single-model evaluation result."""
    name: str
    model: Any
    accuracy: float
    precision: float
    recall: float
    f1: float
    roc_auc: Optional[float]
    log_loss: Optional[float]
    cv_mean_accuracy: float
    cv_std_accuracy: float
    confusion_matrix: List[List[int]]
    classification_report: Dict[str, Any]
    execution_seconds: float
    predictions: Optional[np.ndarray] = None
    probabilities: Optional[np.ndarray] = None


@dataclass
class SupervisedArtifact:
    best_model_name: str
    best_model: Any
    best_model_result: ModelResult
    results: List[ModelResult]
    test_metrics: Dict[str, Any]
    report_path: Path
    best_model_path: Path
    train_path: Path
    test_path: Path
    feature_names: List[str]


class SupervisedModelTrainer:
    """Train, evaluate and select the best supervised classifier."""

    def __init__(self, config_manager: ConfigurationManager) -> None:
        self.config = config_manager.get_supervised_config()
        self.params = config_manager.get_params().get("supervised", {})
        self.test_size = self.config.test_size
        self.random_state = self.config.random_state
        self.models_to_train = self.config.models
        self.report_path = Path(self.config.report_path)
        self.best_model_path = Path(self.config.best_classifier_path)
        self.train_path = Path(self.config.train_data_path)
        self.test_path = Path(self.config.test_data_path)
        self.target = "cluster"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def run(
        self,
        df: pd.DataFrame,
        feature_names: Optional[List[str]] = None,
    ) -> SupervisedArtifact:
        """Train all configured models on ``df`` and select the best.

        Args:
            df: Dataframe containing features + ``cluster`` target column.
            feature_names: Optional explicit list of feature columns.

        Returns:
            :class:`SupervisedArtifact` with best model and full report.
        """
        logger.info("Starting supervised training | models=%s", self.models_to_train)
        try:
            X_train, X_test, y_train, y_test, feats = self._split(df, feature_names)
            self._persist_splits(X_train, X_test, y_train, y_test, feats)

            results: List[ModelResult] = []
            for name in self.models_to_train:
                try:
                    result = self._train_single(name, X_train, X_test, y_train, y_test)
                    results.append(result)
                    logger.info(
                        "%-22s | acc=%.4f | f1=%.4f | cv=%.4f±%.4f",
                        name,
                        result.accuracy,
                        result.f1,
                        result.cv_mean_accuracy,
                        result.cv_std_accuracy,
                    )
                except Exception as exc:
                    logger.error("Model '%s' failed: %s", name, exc)

            if not results:
                raise SupervisedModelError("No supervised model trained successfully.")

            best = max(results, key=lambda r: r.cv_mean_accuracy)
            ensure_dir(self.best_model_path.parent)
            save_object(best.model, self.best_model_path)

            self._persist_report(results, best, feats)

            logger.info(
                "Best supervised model: %s (CV acc=%.4f)",
                best.name,
                best.cv_mean_accuracy,
            )

            return SupervisedArtifact(
                best_model_name=best.name,
                best_model=best.model,
                best_model_result=best,
                results=results,
                test_metrics={
                    "accuracy": best.accuracy,
                    "f1": best.f1,
                    "roc_auc": best.roc_auc,
                },
                report_path=self.report_path,
                best_model_path=self.best_model_path,
                train_path=self.train_path,
                test_path=self.test_path,
                feature_names=feats,
            )
        except Exception as exc:
            raise SupervisedModelError("Supervised training failed.", exc) from exc

    # ------------------------------------------------------------------
    # Splitting
    # ------------------------------------------------------------------
    def _split(
        self, df: pd.DataFrame, feature_names: Optional[List[str]]
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, List[str]]:
        if self.target not in df.columns:
            raise SupervisedModelError(
                f"Target column '{self.target}' not found in dataframe."
            )
        if feature_names is None:
            feature_names = [
                c for c in df.columns if c != self.target and df[c].dtype != object
            ]
        X = df[feature_names].copy()
        y = df[self.target].copy()
        X = X.fillna(X.median())
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=self.test_size, random_state=self.random_state, stratify=y
        )
        return X_train, X_test, y_train, y_test, feature_names

    def _persist_splits(
        self,
        X_train: pd.DataFrame,
        X_test: pd.DataFrame,
        y_train: pd.Series,
        y_test: pd.Series,
        feats: List[str],
    ) -> None:
        train_df = X_train.copy()
        train_df[self.target] = y_train
        test_df = X_test.copy()
        test_df[self.target] = y_test
        ensure_dir(self.train_path.parent)
        train_df.to_csv(self.train_path, index=False)
        test_df.to_csv(self.test_path, index=False)

    # ------------------------------------------------------------------
    # Model factories
    # ------------------------------------------------------------------
    def _build_models(self) -> Dict[str, Any]:
        models: Dict[str, Any] = {}
        p = self.params

        if "random_forest" in self.models_to_train:
            models["random_forest"] = RandomForestClassifier(
                **{**p.get("random_forest", {}), "random_state": self.random_state, "n_jobs": -1}
            )
        if "extra_trees" in self.models_to_train:
            models["extra_trees"] = ExtraTreesClassifier(
                **{**p.get("extra_trees", {}), "random_state": self.random_state, "n_jobs": -1}
            )
        if "xgboost" in self.models_to_train and _XGB_AVAILABLE:
            models["xgboost"] = XGBClassifier(
                **{**p.get("xgboost", {}), "random_state": self.random_state, "n_jobs": -1}
            )
        if "lightgbm" in self.models_to_train and _LGBM_AVAILABLE:
            models["lightgbm"] = LGBMClassifier(
                **{**p.get("lightgbm", {}), "random_state": self.random_state, "n_jobs": -1, "verbose": -1}
            )
        if "catboost" in self.models_to_train and _CATBOOST_AVAILABLE:
            models["catboost"] = CatBoostClassifier(
                **{**p.get("catboost", {}), "random_state": self.random_state}
            )
        if "hist_gradient_boosting" in self.models_to_train:
            models["hist_gradient_boosting"] = HistGradientBoostingClassifier(
                **{**p.get("hist_gradient_boosting", {}), "random_state": self.random_state}
            )
        if "gradient_boosting" in self.models_to_train:
            models["gradient_boosting"] = GradientBoostingClassifier(
                **{**p.get("gradient_boosting", {}), "random_state": self.random_state}
            )
        if "adaboost" in self.models_to_train:
            models["adaboost"] = AdaBoostClassifier(
                **{**p.get("adaboost", {}), "random_state": self.random_state}
            )
        if "bagging" in self.models_to_train:
            models["bagging"] = BaggingClassifier(
                **{**p.get("bagging", {}), "random_state": self.random_state, "n_jobs": -1}
            )
        return models

    def _build_ensemble_models(self, base_models: Dict[str, Any]) -> Dict[str, Any]:
        ensembles: Dict[str, Any] = {}
        if not base_models:
            return ensembles
        ranked = sorted(
            base_models.items(),
            key=lambda kv: getattr(kv[1], "n_estimators", 100),
            reverse=True,
        )[:3]
        top_estimators = [(name, model) for name, model in ranked]

        if "voting" in self.models_to_train:
            ensembles["voting"] = VotingClassifier(
                estimators=top_estimators,
                voting="soft",
                n_jobs=-1,
            )
        if "stacking" in self.models_to_train:
            ensembles["stacking"] = StackingClassifier(
                estimators=top_estimators,
                final_estimator=LogisticRegression(max_iter=1000),
                passthrough=False,
                n_jobs=-1,
            )
        return ensembles

    # ------------------------------------------------------------------
    # Training & evaluation
    # ------------------------------------------------------------------
    def _train_single(
        self,
        name: str,
        X_train: pd.DataFrame,
        X_test: pd.DataFrame,
        y_train: pd.Series,
        y_test: pd.Series,
    ) -> ModelResult:
        start = time.perf_counter()
        base_models = self._build_models()
        ensembles = self._build_ensemble_models(base_models)
        all_models = {**base_models, **ensembles}
        if name not in all_models:
            raise SupervisedModelError(f"Model '{name}' not implemented.")

        model = all_models[name]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            model.fit(X_train, y_train)
            preds = model.predict(X_test)
            try:
                probs = model.predict_proba(X_test)
            except Exception:
                probs = None

        cv_mean, cv_std = self._cross_validate(model, X_train, y_train)

        accuracy = float(accuracy_score(y_test, preds))
        precision = float(precision_score(y_test, preds, average="weighted", zero_division=0))
        recall = float(recall_score(y_test, preds, average="weighted", zero_division=0))
        f1 = float(f1_score(y_test, preds, average="weighted", zero_division=0))
        roc = self._safe_roc_auc(y_test, probs)
        ll = self._safe_log_loss(y_test, probs)
        cm = confusion_matrix(y_test, preds).tolist()
        report = classification_report(
            y_test, preds, output_dict=True, zero_division=0
        )
        elapsed = time.perf_counter() - start
        return ModelResult(
            name=name,
            model=model,
            accuracy=accuracy,
            precision=precision,
            recall=recall,
            f1=f1,
            roc_auc=roc,
            log_loss=ll,
            cv_mean_accuracy=cv_mean,
            cv_std_accuracy=cv_std,
            confusion_matrix=cm,
            classification_report=report,
            execution_seconds=elapsed,
            predictions=preds,
            probabilities=probs,
        )

    def _cross_validate(self, model: Any, X: pd.DataFrame, y: pd.Series) -> Tuple[float, float]:
        try:
            from sklearn.model_selection import cross_val_score

            skf = StratifiedKFold(n_splits=3, shuffle=True, random_state=self.random_state)
            # Use n_jobs=1 to avoid loky worker overhead for small datasets
            scores = cross_val_score(
                model, X, y, cv=skf, scoring="accuracy", n_jobs=1
            )
            return float(np.mean(scores)), float(np.std(scores))
        except Exception as exc:
            logger.warning("CV failed for %s: %s", type(model).__name__, exc)
            return 0.0, 0.0

    @staticmethod
    def _safe_roc_auc(y_true: pd.Series, probs: Optional[np.ndarray]) -> Optional[float]:
        if probs is None:
            return None
        try:
            classes = sorted(set(y_true))
            if len(classes) > 2:
                return float(roc_auc_score(y_true, probs, multi_class="ovr", average="weighted"))
            return float(roc_auc_score(y_true, probs[:, 1]))
        except Exception:
            return None

    @staticmethod
    def _safe_log_loss(y_true: pd.Series, probs: Optional[np.ndarray]) -> Optional[float]:
        if probs is None:
            return None
        try:
            return float(log_loss(y_true, probs))
        except Exception:
            return None

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------
    def _persist_report(
        self,
        results: List[ModelResult],
        best: ModelResult,
        feature_names: List[str],
    ) -> None:
        report = {
            "best_model": best.name,
            "best_metrics": {
                "accuracy": best.accuracy,
                "precision": best.precision,
                "recall": best.recall,
                "f1": best.f1,
                "roc_auc": best.roc_auc,
                "log_loss": best.log_loss,
                "cv_mean_accuracy": best.cv_mean_accuracy,
                "cv_std_accuracy": best.cv_std_accuracy,
            },
            "feature_names": feature_names,
            "all_results": [
                {
                    "name": r.name,
                    "accuracy": r.accuracy,
                    "precision": r.precision,
                    "recall": r.recall,
                    "f1": r.f1,
                    "roc_auc": r.roc_auc,
                    "log_loss": r.log_loss,
                    "cv_mean_accuracy": r.cv_mean_accuracy,
                    "cv_std_accuracy": r.cv_std_accuracy,
                    "execution_seconds": r.execution_seconds,
                    "confusion_matrix": r.confusion_matrix,
                    "classification_report": r.classification_report,
                }
                for r in results
            ],
        }
        ensure_dir(self.report_path.parent)
        write_json(report, self.report_path)

        # Also save per-model artifacts (for inspection / SHAP)
        for r in results:
            model_path = self.best_model_path.parent / f"{r.name}.joblib"
            save_object(r.model, model_path)
