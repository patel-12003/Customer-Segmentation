"""
Hyperparameter tuner.

Uses Optuna (Bayesian optimization) to tune a configurable subset of
the supervised models. Optuna is an optional dependency — if missing,
the tuner returns the default model unchanged.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score

from src.config_manager import ConfigurationManager
from src.exception import SupervisedModelError
from src.logger import get_logger
from src.utils import save_object

logger = get_logger(__name__)

try:
    import optuna
    from optuna.samplers import TPESampler
    _OPTUNA_AVAILABLE = True
except Exception:  # pragma: no cover
    _OPTUNA_AVAILABLE = False


@dataclass
class TuningResult:
    best_model: Any
    best_params: Dict[str, Any]
    best_score: float
    n_trials: int
    study: Optional[Any]


class HyperparameterTuner:
    """Bayesian hyperparameter optimiser using Optuna."""

    def __init__(self, config_manager: ConfigurationManager) -> None:
        params = config_manager.get_params().get("optuna", {})
        self.n_trials = params.get("n_trials", 25)
        self.n_jobs = params.get("n_jobs", 1)
        self.timeout = params.get("timeout", 600)
        self.random_state = config_manager.get_supervised_config().random_state

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def tune(
        self,
        model_name: str,
        X: pd.DataFrame,
        y: pd.Series,
    ) -> TuningResult:
        """Tune ``model_name`` on (X, y) using Optuna TPE sampler.

        Falls back to default model if Optuna is not installed.
        """
        if not _OPTUNA_AVAILABLE:
            logger.warning(
                "Optuna not installed — returning default %s model.", model_name
            )
            model, params = self._default_model(model_name)
            model.fit(X, y)
            return TuningResult(
                best_model=model,
                best_params=params,
                best_score=0.0,
                n_trials=0,
                study=None,
            )

        logger.info(
            "Starting Optuna tuning for %s | trials=%d | timeout=%ss",
            model_name,
            self.n_trials,
            self.timeout,
        )
        try:
            optuna.logging.set_verbosity(optuna.logging.WARNING)

            def objective(trial: "optuna.Trial") -> float:
                params = self._suggest_params(trial, model_name)
                model = self._build_model(model_name, params)
                skf = __import__("sklearn.model_selection", fromlist=["StratifiedKFold"]).StratifiedKFold(
                    n_splits=5, shuffle=True, random_state=self.random_state
                )
                scores = cross_val_score(
                    model, X, y, cv=skf, scoring="accuracy", n_jobs=-1
                )
                return float(np.mean(scores))

            study = optuna.create_study(
                direction="maximize",
                sampler=TPESampler(seed=self.random_state),
            )
            study.optimize(
                objective,
                n_trials=self.n_trials,
                timeout=self.timeout,
                n_jobs=self.n_jobs,
                show_progress_bar=False,
            )
            best_params = dict(study.best_params)
            best_model = self._build_model(model_name, best_params)
            best_model.fit(X, y)
            logger.info(
                "Tuning complete | best score=%.4f | params=%s",
                study.best_value,
                best_params,
            )
            return TuningResult(
                best_model=best_model,
                best_params=best_params,
                best_score=float(study.best_value),
                n_trials=len(study.trials),
                study=study,
            )
        except Exception as exc:
            raise SupervisedModelError(
                f"Hyperparameter tuning failed for {model_name}.", exc
            ) from exc

    # ------------------------------------------------------------------
    # Search spaces
    # ------------------------------------------------------------------
    def _suggest_params(self, trial: Any, model_name: str) -> Dict[str, Any]:
        if model_name == "random_forest":
            return {
                "n_estimators": trial.suggest_int("n_estimators", 200, 800, step=100),
                "max_depth": trial.suggest_int("max_depth", 5, 30),
                "min_samples_split": trial.suggest_int("min_samples_split", 2, 10),
                "min_samples_leaf": trial.suggest_int("min_samples_leaf", 1, 4),
                "max_features": trial.suggest_categorical("max_features", ["sqrt", "log2"]),
            }
        if model_name == "xgboost":
            return {
                "n_estimators": trial.suggest_int("n_estimators", 200, 800, step=100),
                "max_depth": trial.suggest_int("max_depth", 3, 12),
                "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
                "subsample": trial.suggest_float("subsample", 0.6, 1.0),
                "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
            }
        if model_name == "lightgbm":
            return {
                "n_estimators": trial.suggest_int("n_estimators", 200, 800, step=100),
                "num_leaves": trial.suggest_int("num_leaves", 15, 127),
                "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
                "subsample": trial.suggest_float("subsample", 0.6, 1.0),
                "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
            }
        if model_name == "catboost":
            return {
                "iterations": trial.suggest_int("iterations", 200, 800, step=100),
                "depth": trial.suggest_int("depth", 3, 10),
                "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
            }
        # Default: empty params
        return {}

    @staticmethod
    def _build_model(model_name: str, params: Dict[str, Any]) -> Any:
        if model_name == "random_forest":
            return RandomForestClassifier(**params, random_state=42, n_jobs=-1, class_weight="balanced")
        if model_name == "xgboost":
            from xgboost import XGBClassifier
            return XGBClassifier(**params, random_state=42, n_jobs=-1, eval_metric="mlogloss", use_label_encoder=False)
        if model_name == "lightgbm":
            from lightgbm import LGBMClassifier
            return LGBMClassifier(**params, random_state=42, n_jobs=-1, verbose=-1)
        if model_name == "catboost":
            from catboost import CatBoostClassifier
            return CatBoostClassifier(**params, random_state=42, verbose=False)
        raise SupervisedModelError(f"Unknown model for tuning: {model_name}")

    @staticmethod
    def _default_model(model_name: str):
        params: Dict[str, Any] = {}
        if model_name == "random_forest":
            params = {"n_estimators": 400, "random_state": 42, "n_jobs": -1}
            return RandomForestClassifier(**params), params
        raise SupervisedModelError(f"Unknown model: {model_name}")
