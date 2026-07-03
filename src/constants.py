"""
Project-wide constants.

All path references used across the project resolve from the repository
root. Keeping them in a single place prevents drift between modules.
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# Repository root
# ---------------------------------------------------------------------------
ROOT_DIR: Path = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Configuration files
# ---------------------------------------------------------------------------
CONFIGS_DIR: Path = ROOT_DIR / "configs"
if not CONFIGS_DIR.exists():
    # Allow YAMLs to live at the repo root as well (back-compat)
    CONFIGS_DIR = ROOT_DIR

CONFIG_FILE: Path = CONFIGS_DIR / "config.yaml"
PARAMS_FILE: Path = CONFIGS_DIR / "params.yaml"
SCHEMA_FILE: Path = CONFIGS_DIR / "schema.yaml"
PREDICTION_SCHEMA_FILE: Path = CONFIGS_DIR / "prediction_schema.yaml"
MODEL_FILE: Path = CONFIGS_DIR / "model.yaml"
LOGGING_CONFIG_FILE: Path = CONFIGS_DIR / "logging.yaml"

# ---------------------------------------------------------------------------
# Data directories
# ---------------------------------------------------------------------------
DATA_DIR: Path = ROOT_DIR / "data"
RAW_DATA_DIR: Path = DATA_DIR / "raw"
PROCESSED_DATA_DIR: Path = DATA_DIR / "processed"

RAW_DATA_FILE: Path = RAW_DATA_DIR / "marketing_campaign.csv"
CLEAN_DATA_FILE: Path = RAW_DATA_DIR / "clustered_data.csv"

INGESTED_DATA_FILE: Path = PROCESSED_DATA_DIR / "ingested.csv"
VALIDATED_DATA_FILE: Path = PROCESSED_DATA_DIR / "validated.csv"
TRANSFORMED_DATA_FILE: Path = PROCESSED_DATA_DIR / "transformed.csv"
ENGINEERED_DATA_FILE: Path = PROCESSED_DATA_DIR / "engineered.csv"
SELECTED_FEATURES_FILE: Path = PROCESSED_DATA_DIR / "selected_features.csv"
CLUSTERED_DATA_FILE: Path = PROCESSED_DATA_DIR / "clustered.csv"
TRAIN_FILE: Path = PROCESSED_DATA_DIR / "train.csv"
TEST_FILE: Path = PROCESSED_DATA_DIR / "test.csv"

# ---------------------------------------------------------------------------
# Artifacts
# ---------------------------------------------------------------------------
ARTIFACTS_ROOT: Path = ROOT_DIR / "artifacts"
MODELS_DIR: Path = ARTIFACTS_ROOT / "models"
TRAINED_MODELS_DIR: Path = ARTIFACTS_ROOT / "trained_models"
REPORTS_DIR: Path = ARTIFACTS_ROOT / "reports"
PLOTS_DIR: Path = ARTIFACTS_ROOT / "plots"

SAVED_MODELS_DIR: Path = ROOT_DIR / "saved_models"
AUTOML_DIR: Path = SAVED_MODELS_DIR / "autogluon"
EXPLAINABILITY_DIR: Path = SAVED_MODELS_DIR / "explainability"

LOGS_DIR: Path = ROOT_DIR / "logs"
LOGS_FILE_NAME: str = "customer_segmentation.log"

# Reports
CLUSTERING_REPORT_FILE: Path = REPORTS_DIR / "clustering_report.json"
SUPERVISED_REPORT_FILE: Path = REPORTS_DIR / "supervised_report.json"
AUTOML_REPORT_FILE: Path = REPORTS_DIR / "autogluon_report.json"
FEATURE_IMPORTANCE_FILE: Path = REPORTS_DIR / "feature_importance.csv"
CLUSTER_PROFILE_FILE: Path = REPORTS_DIR / "cluster_profiles.json"
BEST_MODEL_FILE: Path = REPORTS_DIR / "best_model.json"

# Preprocessors / encoders
PREPROCESSOR_FILE: Path = SAVED_MODELS_DIR / "preprocessor.joblib"
SCALER_FILE: Path = SAVED_MODELS_DIR / "scaler.joblib"
PCA_FILE: Path = SAVED_MODELS_DIR / "pca.joblib"
FEATURE_SELECTOR_FILE: Path = SAVED_MODELS_DIR / "feature_selector.joblib"
LABEL_ENCODER_FILE: Path = SAVED_MODELS_DIR / "label_encoder.joblib"
BEST_CLUSTERER_FILE: Path = SAVED_MODELS_DIR / "best_clusterer.joblib"
BEST_CLASSIFIER_FILE: Path = SAVED_MODELS_DIR / "best_classifier.joblib"

# Reports / docs
EDA_REPORT_DIR: Path = ROOT_DIR / "reports"
ASSETS_DIR: Path = ROOT_DIR / "assets"

# ---------------------------------------------------------------------------
# Target & identifier columns
# ---------------------------------------------------------------------------
TARGET_COLUMN: str = "cluster"
ID_COLUMN: str = "ID"

# Default random state
RANDOM_STATE: int = 42
