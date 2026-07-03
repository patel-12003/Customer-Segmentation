"""
Configuration manager.

Loads all YAML configuration files into strongly-typed dataclasses so
that downstream modules get validated, attribute-style access instead
of raw dictionary lookups.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from src.constants import (
    CONFIG_FILE,
    MODEL_FILE,
    PARAMS_FILE,
    PREDICTION_SCHEMA_FILE,
    SCHEMA_FILE,
)
from src.exception import ConfigError
from src.logger import get_logger
from src.utils import read_yaml

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Dataclasses for each YAML file
# ---------------------------------------------------------------------------
@dataclass
class DataIngestionConfig:
    raw_data_path: str
    cleaned_data_path: str
    ingested_data_path: str
    validated_data_path: str


@dataclass
class DataValidationConfig:
    validated_data_path: str
    report_path: str
    allowed_null_ratio: float
    duplicate_threshold: float


@dataclass
class DataTransformationConfig:
    transformed_data_path: str
    scaler_path: str
    preprocessor_path: str
    numerical_features: List[str]
    categorical_features: List[str]


@dataclass
class FeatureEngineeringConfig:
    engineered_data_path: str
    feature_store_path: str
    new_features: List[str]


@dataclass
class FeatureSelectionConfig:
    selected_features_path: str
    selector_path: str
    method: str
    k_features: int


@dataclass
class ClusteringConfig:
    clustered_data_path: str
    best_clusterer_path: str
    report_path: str
    n_clusters: int
    algorithms: List[str]
    random_state: int


@dataclass
class SupervisedConfig:
    train_data_path: str
    test_data_path: str
    best_classifier_path: str
    report_path: str
    models: List[str]
    test_size: float
    random_state: int
    tuning_trials: int


@dataclass
class AutoGluonConfig:
    automl_dir: str
    time_limit: int
    presets: str
    eval_metric: str


@dataclass
class ExplainabilityConfig:
    shap_path: str
    lime_path: str
    sample_size: int


@dataclass
class AppConfig:
    """Top-level config aggregator."""
    ingestion: DataIngestionConfig
    validation: DataValidationConfig
    transformation: DataTransformationConfig
    feature_engineering: FeatureEngineeringConfig
    feature_selection: FeatureSelectionConfig
    clustering: ClusteringConfig
    supervised: SupervisedConfig
    autogluon: AutoGluonConfig
    explainability: ExplainabilityConfig
    raw: Dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------
class ConfigurationManager:
    """Load and expose all project configuration objects.

    The class reads ``config.yaml`` and ``params.yaml`` (and optionally
    ``schema.yaml``, ``prediction_schema.yaml`` and ``model.yaml``) and
    returns ready-to-use dataclass instances.
    """

    def __init__(
        self,
        config_path: Optional[Union[str, Path]] = None,
        params_path: Optional[Union[str, Path]] = None,
        schema_path: Optional[Union[str, Path]] = None,
        prediction_schema_path: Optional[Union[str, Path]] = None,
        model_path: Optional[Union[str, Path]] = None,
    ) -> None:
        self.config_path = Path(config_path) if config_path else CONFIG_FILE
        self.params_path = Path(params_path) if params_path else PARAMS_FILE
        self.schema_path = Path(schema_path) if schema_path else SCHEMA_FILE
        self.prediction_schema_path = (
            Path(prediction_schema_path)
            if prediction_schema_path
            else PREDICTION_SCHEMA_FILE
        )
        self.model_path = Path(model_path) if model_path else MODEL_FILE

        if not self.config_path.exists():
            raise ConfigError(f"config.yaml not found at {self.config_path}")
        if not self.params_path.exists():
            raise ConfigError(f"params.yaml not found at {self.params_path}")

        self._config: Dict[str, Any] = read_yaml(self.config_path)
        self._params: Dict[str, Any] = read_yaml(self.params_path)
        self._schema: Dict[str, Any] = (
            read_yaml(self.schema_path) if self.schema_path.exists() else {}
        )
        self._prediction_schema: Dict[str, Any] = (
            read_yaml(self.prediction_schema_path)
            if self.prediction_schema_path.exists()
            else {}
        )
        self._model_cfg: Dict[str, Any] = (
            read_yaml(self.model_path) if self.model_path.exists() else {}
        )

    # ------------------------------------------------------------------
    # Section accessors
    # ------------------------------------------------------------------
    def get_ingestion_config(self) -> DataIngestionConfig:
        cfg = self._config["data_ingestion"]
        return DataIngestionConfig(
            raw_data_path=cfg["raw_data_path"],
            cleaned_data_path=cfg["cleaned_data_path"],
            ingested_data_path=cfg["ingested_data_path"],
            validated_data_path=cfg["validated_data_path"],
        )

    def get_validation_config(self) -> DataValidationConfig:
        cfg = self._config["data_validation"]
        return DataValidationConfig(
            validated_data_path=cfg["validated_data_path"],
            report_path=cfg["report_path"],
            allowed_null_ratio=cfg.get("allowed_null_ratio", 0.05),
            duplicate_threshold=cfg.get("duplicate_threshold", 0.1),
        )

    def get_transformation_config(self) -> DataTransformationConfig:
        cfg = self._config["data_transformation"]
        return DataTransformationConfig(
            transformed_data_path=cfg["transformed_data_path"],
            scaler_path=cfg["scaler_path"],
            preprocessor_path=cfg["preprocessor_path"],
            numerical_features=cfg.get("numerical_features", []),
            categorical_features=cfg.get("categorical_features", []),
        )

    def get_feature_engineering_config(self) -> FeatureEngineeringConfig:
        cfg = self._config["feature_engineering"]
        return FeatureEngineeringConfig(
            engineered_data_path=cfg["engineered_data_path"],
            feature_store_path=cfg["feature_store_path"],
            new_features=cfg.get("new_features", []),
        )

    def get_feature_selection_config(self) -> FeatureSelectionConfig:
        cfg = self._config["feature_selection"]
        return FeatureSelectionConfig(
            selected_features_path=cfg["selected_features_path"],
            selector_path=cfg["selector_path"],
            method=cfg.get("method", "mutual_info"),
            k_features=cfg.get("k_features", 15),
        )

    def get_clustering_config(self) -> ClusteringConfig:
        cfg = self._config["clustering"]
        params = self._params.get("clustering", {})
        return ClusteringConfig(
            clustered_data_path=cfg["clustered_data_path"],
            best_clusterer_path=cfg["best_clusterer_path"],
            report_path=cfg["report_path"],
            n_clusters=params.get("n_clusters", cfg.get("n_clusters", 3)),
            algorithms=cfg.get("algorithms", []),
            random_state=params.get("random_state", 42),
        )

    def get_supervised_config(self) -> SupervisedConfig:
        cfg = self._config["supervised"]
        params = self._params.get("supervised", {})
        return SupervisedConfig(
            train_data_path=cfg["train_data_path"],
            test_data_path=cfg["test_data_path"],
            best_classifier_path=cfg["best_classifier_path"],
            report_path=cfg["report_path"],
            models=cfg.get("models", []),
            test_size=params.get("test_size", 0.2),
            random_state=params.get("random_state", 42),
            tuning_trials=params.get("tuning_trials", 30),
        )

    def get_autogluon_config(self) -> AutoGluonConfig:
        cfg = self._config["autogluon"]
        params = self._params.get("autogluon", {})
        return AutoGluonConfig(
            automl_dir=cfg["automl_dir"],
            time_limit=params.get("time_limit", 300),
            presets=params.get("presets", "medium_quality"),
            eval_metric=params.get("eval_metric", "accuracy"),
        )

    def get_explainability_config(self) -> ExplainabilityConfig:
        cfg = self._config["explainability"]
        return ExplainabilityConfig(
            shap_path=cfg["shap_path"],
            lime_path=cfg["lime_path"],
            sample_size=cfg.get("sample_size", 200),
        )

    def get_app_config(self) -> AppConfig:
        return AppConfig(
            ingestion=self.get_ingestion_config(),
            validation=self.get_validation_config(),
            transformation=self.get_transformation_config(),
            feature_engineering=self.get_feature_engineering_config(),
            feature_selection=self.get_feature_selection_config(),
            clustering=self.get_clustering_config(),
            supervised=self.get_supervised_config(),
            autogluon=self.get_autogluon_config(),
            explainability=self.get_explainability_config(),
            raw=self._config,
        )

    # ------------------------------------------------------------------
    # Schema / model dictionaries
    # ------------------------------------------------------------------
    def get_schema(self) -> Dict[str, Any]:
        return self._schema

    def get_prediction_schema(self) -> Dict[str, Any]:
        return self._prediction_schema

    def get_model_config(self) -> Dict[str, Any]:
        return self._model_cfg

    def get_params(self) -> Dict[str, Any]:
        return self._params
