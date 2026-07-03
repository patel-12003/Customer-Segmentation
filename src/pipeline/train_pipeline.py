"""
End-to-end training pipeline.

Orchestrates the full workflow:
1. Data ingestion
2. Data validation
3. Data transformation
4. Feature engineering
5. Feature selection
6. Clustering (all algorithms)
7. Supervised training (all models)
8. AutoGluon (optional)
9. Explainability (SHAP + LIME)
10. Persist artifacts
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd

from src.config_manager import ConfigurationManager
from src.constants import TARGET_COLUMN
from src.data.ingestion import DataIngestion
from src.data.transformation import DataTransformation
from src.data.validation import DataValidation
from src.exception import CustomerSegmentationException
from src.explainability.lime_explainer import LIMEExplainer
from src.explainability.shap_explainer import SHAPExplainer
from src.features.engineering import FeatureEngineer
from src.features.selection import FeatureSelector
from src.logger import get_logger
from src.models.autogluon_trainer import AutoGluonTrainer
from src.models.clustering import ClusteringEngine
from src.models.supervised import SupervisedModelTrainer
from src.utils import timer, write_json

logger = get_logger(__name__)


@dataclass
class PipelineResult:
    success: bool
    steps_completed: list
    best_clustering_model: Optional[str]
    best_supervised_model: Optional[str]
    n_clusters: Optional[int]
    best_accuracy: Optional[float]
    artifacts: Dict[str, Any]


class TrainPipeline:
    """Top-level training orchestrator."""

    def __init__(self, config_manager: Optional[ConfigurationManager] = None) -> None:
        self.config_manager = config_manager or ConfigurationManager()
        self.steps_completed: list = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def run(self, run_autogluon: bool = True, run_explainability: bool = True) -> PipelineResult:
        """Execute the full training pipeline.

        Args:
            run_autogluon: Whether to run AutoGluon (slow).
            run_explainability: Whether to compute SHAP/LIME explanations.

        Returns:
            :class:`PipelineResult` with summary.
        """
        logger.info("=" * 70)
        logger.info("Customer Segmentation — Training Pipeline Starting")
        logger.info("=" * 70)

        try:
            # ---- 1. Ingestion ----
            with timer("Data Ingestion"):
                ingestion = DataIngestion(self.config_manager)
                ingestion_artifact = ingestion.initiate_ingestion()
                self.steps_completed.append("ingestion")

            # ---- 2. Validation ----
            with timer("Data Validation"):
                validation = DataValidation(self.config_manager)
                validation_report = validation.initiate_validation(ingestion_artifact.raw_df)
                if not validation_report.passed:
                    logger.warning(
                        "Validation produced errors but pipeline will continue. "
                        "See %s", validation.report_path
                    )
                self.steps_completed.append("validation")

            # ---- 3. Transformation ----
            with timer("Data Transformation"):
                transformation = DataTransformation(self.config_manager)
                transformation_artifact = transformation.initiate_transformation(
                    ingestion_artifact.raw_df
                )
                self.steps_completed.append("transformation")

            # ---- 4. Feature Engineering ----
            with timer("Feature Engineering"):
                engineer = FeatureEngineer(self.config_manager)
                eng_artifact = engineer.initiate_feature_engineering(
                    ingestion_artifact.raw_df
                )
                self.steps_completed.append("feature_engineering")

            # ---- 5. Feature Selection (on cleaned data with clusters) ----
            with timer("Feature Selection"):
                selector = FeatureSelector(self.config_manager)
                cleaned_df = ingestion_artifact.cleaned_df.copy()
                # Rename columns to be filesystem-safe
                cleaned_df.columns = [c.replace(" ", "_") for c in cleaned_df.columns]
                selection_artifact = selector.initiate_feature_selection(
                    cleaned_df,
                    target_column=TARGET_COLUMN,
                    drop_columns=[],
                )
                self.steps_completed.append("feature_selection")

            # ---- 6. Clustering ----
            with timer("Clustering"):
                cluster_engine = ClusteringEngine(self.config_manager)
                # Use cleaned feature matrix for clustering (no target)
                cluster_features = cleaned_df.drop(columns=[TARGET_COLUMN])
                cluster_artifact = cluster_engine.run(cluster_features)
                self.steps_completed.append("clustering")

            # ---- 7. Supervised training ----
            with timer("Supervised Training"):
                trainer = SupervisedModelTrainer(self.config_manager)
                supervised_artifact = trainer.run(cleaned_df, selection_artifact.selected_features)
                self.steps_completed.append("supervised_training")

            # ---- 8. AutoGluon (optional) ----
            autogluon_artifact = None
            if run_autogluon:
                try:
                    with timer("AutoGluon"):
                        automl = AutoGluonTrainer(self.config_manager)
                        autogluon_artifact = automl.run(cleaned_df[selection_artifact.selected_features + [TARGET_COLUMN]])
                        self.steps_completed.append("autogluon")
                except Exception as exc:
                    logger.warning("AutoGluon step skipped/failed: %s", exc)

            # ---- 9. Explainability (optional) ----
            shap_artifact = None
            lime_artifact = None
            if run_explainability:
                try:
                    with timer("SHAP"):
                        shap_explainer = SHAPExplainer(self.config_manager)
                        shap_artifact = shap_explainer.explain(
                            supervised_artifact.best_model,
                            cleaned_df[selection_artifact.selected_features],
                        )
                        self.steps_completed.append("shap")
                except Exception as exc:
                    logger.warning("SHAP step skipped/failed: %s", exc)
                try:
                    with timer("LIME"):
                        lime_explainer = LIMEExplainer(self.config_manager)
                        lime_artifact = lime_explainer.explain(
                            supervised_artifact.best_model,
                            cleaned_df[selection_artifact.selected_features],
                            y=cleaned_df[TARGET_COLUMN],
                            class_names=sorted(cleaned_df[TARGET_COLUMN].unique()),
                        )
                        self.steps_completed.append("lime")
                except Exception as exc:
                    logger.warning("LIME step skipped/failed: %s", exc)

            # ---- 10. Summary ----
            result = PipelineResult(
                success=True,
                steps_completed=self.steps_completed,
                best_clustering_model=cluster_artifact.best_model_name,
                best_supervised_model=supervised_artifact.best_model_name,
                n_clusters=cluster_artifact.best_model.n_clusters,
                best_accuracy=supervised_artifact.best_model_result.accuracy,
                artifacts={
                    "ingestion": str(ingestion_artifact.ingested_path),
                    "transformation": str(transformation_artifact.transformed_path),
                    "engineered": str(eng_artifact.engineered_path),
                    "selected_features": str(selection_artifact.selected_path),
                    "clustered": str(cluster_engine.clustered_data_path),
                    "train_split": str(supervised_artifact.train_path),
                    "test_split": str(supervised_artifact.test_path),
                    "best_clusterer": str(cluster_artifact.best_model_path),
                    "best_classifier": str(supervised_artifact.best_model_path),
                    "clustering_report": str(cluster_artifact.report_path),
                    "supervised_report": str(supervised_artifact.report_path),
                    "autogluon": str(autogluon_artifact.path) if autogluon_artifact else None,
                    "shap": str(shap_artifact.path) if shap_artifact else None,
                    "lime": str(lime_artifact.path) if lime_artifact else None,
                },
            )
            self._persist_summary(result)
            logger.info("=" * 70)
            logger.info("Training Pipeline COMPLETED successfully.")
            logger.info("Steps: %s", self.steps_completed)
            logger.info("Best clustering: %s", result.best_clustering_model)
            logger.info("Best classifier: %s (acc=%.4f)",
                        result.best_supervised_model, result.best_accuracy)
            logger.info("=" * 70)
            return result

        except Exception as exc:
            logger.error("Training pipeline failed: %s", exc)
            raise CustomerSegmentationException(
                "Training pipeline failed.", exc
            ) from exc

    # ------------------------------------------------------------------
    def _persist_summary(self, result: PipelineResult) -> None:
        from src.constants import REPORTS_DIR
        from src.utils import ensure_dir
        summary_path = REPORTS_DIR / "pipeline_summary.json"
        ensure_dir(summary_path.parent)
        write_json(
            {
                "success": result.success,
                "steps_completed": result.steps_completed,
                "best_clustering_model": result.best_clustering_model,
                "best_supervised_model": result.best_supervised_model,
                "n_clusters": result.n_clusters,
                "best_accuracy": result.best_accuracy,
                "artifacts": result.artifacts,
            },
            summary_path,
        )
