# Training Guide

## Quick Start

```bash
python training.py
```

This runs the full end-to-end pipeline:

1. Data Ingestion
2. Data Validation
3. Data Transformation
4. Feature Engineering
5. Feature Selection
6. Clustering (10 algorithms)
7. Supervised Training (11 models)
8. AutoGluon AutoML
9. Explainability (SHAP + LIME)

## Command-Line Options

| Flag | Effect |
|---|---|
| `--skip-autogluon` | Skip the AutoGluon AutoML step (saves ~5 minutes) |
| `--skip-explainability` | Skip SHAP/LIME explainability |
| `--config PATH` | Override `config.yaml` location |
| `--params PATH` | Override `params.yaml` location |

## What Gets Created

After a successful run, you'll have:

```
saved_models/
├── best_classifier.joblib        # The winning supervised model
├── best_clusterer.joblib         # The winning clustering algorithm
├── preprocessor.joblib           # Fitted ColumnTransformer
├── scaler.joblib                 # Fitted StandardScaler
├── feature_selector.joblib       # Selector state (selected feature list)
├── feature_store.joblib          # Feature engineering metadata
├── adaboost.joblib               # Per-model artifacts
├── bagging.joblib
├── catboost.joblib
├── extra_trees.joblib
├── gradient_boosting.joblib
├── hist_gradient_boosting.joblib
├── lightgbm.joblib
├── random_forest.joblib
├── stacking.joblib
├── xgboost.joblib
├── autogluon/                    # AutoGluon predictor artifacts
└── explainability/
    ├── shap_values.joblib
    └── lime_explainer.joblib

artifacts/
├── models/
├── trained_models/
├── reports/
│   ├── clustering_report.json    # All 10 algorithms' metrics
│   ├── supervised_report.json    # All 11 models' metrics
│   ├── autogluon_report.json     # AutoGluon leaderboard
│   ├── validation_report.json    # Data validation results
│   └── pipeline_summary.json     # End-to-end summary
└── plots/

data/processed/
├── ingested.csv
├── transformed.csv
├── engineered.csv
├── selected_features.csv
├── clustered.csv
├── train.csv
└── test.csv
```

## Customizing the Pipeline

### Change number of clusters

Edit `params.yaml`:

```yaml
clustering:
  n_clusters: 4   # was 3
```

### Add/remove a clustering algorithm

Edit `config.yaml`:

```yaml
clustering:
  algorithms:
    - kmeans
    - gmm
    # - dbscan    # comment out to skip
```

### Add/remove a supervised model

Edit `config.yaml`:

```yaml
supervised:
  models:
    - random_forest
    - xgboost
    - lightgbm
    # - catboost    # comment out to skip
```

### Tune hyperparameters

Edit `params.yaml`:

```yaml
supervised:
  xgboost:
    n_estimators: 600     # was 200
    max_depth: 8           # was 6
    learning_rate: 0.03    # was 0.05
```

### Use Optuna hyperparameter tuning

```python
from src.config_manager import ConfigurationManager
from src.models.tuner import HyperparameterTuner
from src.constants import CLEAN_DATA_FILE
import pandas as pd

cm = ConfigurationManager()
df = pd.read_csv(CLEAN_DATA_FILE)
df.columns = [c.replace(' ', '_') for c in df.columns]

tuner = HyperparameterTuner(cm)
result = tuner.tune('random_forest', df.drop(columns=['cluster']), df['cluster'])
print(result.best_params, result.best_score)
```

## Monitoring Training

The pipeline logs everything to:

- Console (stdout) — INFO level
- `logs/customer_segmentation.log` — DEBUG level (rotating, 10 MB max)
- `logs/error.log` — ERROR level only

Tail the log in real time:

```bash
tail -f logs/customer_segmentation.log
```

## Re-running Specific Stages

Each stage is independently runnable:

```python
from src.config_manager import ConfigurationManager
from src.data.ingestion import DataIngestion

cm = ConfigurationManager()
ingestion = DataIngestion(cm)
artifact = ingestion.initiate_ingestion()
print(artifact.raw_df.shape)
```

See the individual notebooks in `notebooks/` for examples of each stage.

## Expected Output

After training completes, you should see:

```
======================================================================
✅ Training completed successfully!
   Best clustering model : kmeans
   Best classifier       : hist_gradient_boosting
   Number of clusters    : 3
   Best accuracy         : 0.9576
======================================================================

🚀 Launch the dashboard with:
   streamlit run app.py
```
