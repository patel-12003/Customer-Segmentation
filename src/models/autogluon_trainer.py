"""
AutoGluon trainer.

Wraps ``autogluon.tabular.TabularPredictor`` so that AutoML fits and
persists in a dedicated directory under ``saved_models/autogluon``.
AutoGluon is an optional dependency — if it is not installed, the
trainer logs a warning and returns ``None`` instead of raising.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import pandas as pd

from src.config_manager import ConfigurationManager
from src.exception import AutoGluonTrainerError
from src.logger import get_logger
from src.utils import ensure_dir, write_json

logger = get_logger(__name__)

try:
    from autogluon.tabular import TabularPredictor  # type: ignore
    _AUTOML_AVAILABLE = True
except Exception:  # pragma: no cover
    TabularPredictor = None  # type: ignore
    _AUTOML_AVAILABLE = False


@dataclass
class AutoGluonArtifact:
    predictor: Optional[Any]
    path: Path
    leaderboard: Optional[pd.DataFrame]
    best_model: Optional[str]
    metrics: Optional[dict]


class AutoGluonTrainer:
    """Train AutoGluon TabularPredictor and persist the leaderboard."""

    def __init__(self, config_manager: ConfigurationManager) -> None:
        self.config = config_manager.get_autogluon_config()
        self.automl_dir = Path(self.config.automl_dir)
        self.time_limit = self.config.time_limit
        self.presets = self.config.presets
        self.eval_metric = self.config.eval_metric
        self.target = "cluster"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def run(self, df: pd.DataFrame) -> AutoGluonArtifact:
        """Fit AutoGluon TabularPredictor on ``df``.

        Args:
            df: Dataframe containing features + ``cluster`` target column.

        Returns:
            :class:`AutoGluonArtifact` with predictor and leaderboard.
        """
        if not _AUTOML_AVAILABLE:
            logger.warning(
                "AutoGluon is not installed. Skipping AutoML training. "
                "Install with `pip install autogluon` to enable."
            )
            return AutoGluonArtifact(
                predictor=None,
                path=self.automl_dir,
                leaderboard=None,
                best_model=None,
                metrics=None,
            )

        if self.target not in df.columns:
            raise AutoGluonTrainerError(
                f"Target column '{self.target}' not found in dataframe."
            )

        logger.info(
            "Starting AutoGluon training | time_limit=%ss | presets=%s",
            self.time_limit,
            self.presets,
        )
        try:
            ensure_dir(self.automl_dir.parent)
            predictor = TabularPredictor(
                label=self.target,
                path=str(self.automl_dir),
                eval_metric=self.eval_metric,
            )
            predictor.fit(
                df,
                time_limit=self.time_limit,
                presets=self.presets,
                verbosity=1,
            )
            leaderboard = predictor.leaderboard(df, silent=True)
            best_model = str(predictor.model_best)
            metrics = {
                "best_model": best_model,
                "eval_metric": self.eval_metric,
                "leaderboard_top5": leaderboard.head(5).to_dict(orient="records"),
            }
            report_path = self.automl_dir.parent.parent / "artifacts" / "reports" / "autogluon_report.json"
            ensure_dir(report_path.parent)
            write_json(metrics, report_path)
            logger.info("AutoGluon best model: %s", best_model)
            return AutoGluonArtifact(
                predictor=predictor,
                path=self.automl_dir,
                leaderboard=leaderboard,
                best_model=best_model,
                metrics=metrics,
            )
        except Exception as exc:
            raise AutoGluonTrainerError(
                "AutoGluon training failed.", exc
            ) from exc
