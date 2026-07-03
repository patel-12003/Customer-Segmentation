# Architecture

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CONFIGURATION LAYER                          │
│                                                                      │
│   config.yaml     params.yaml     schema.yaml     prediction_schema  │
│   model.yaml      logging.yaml                                     │
└──────────────────────────────────┬──────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          TRAINING PIPELINE                           │
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │  Ingestion   │→ │  Validation  │→ │  Transformation           │  │
│  │              │  │              │  │  (impute + scale + OHE)   │  │
│  └──────────────┘  └──────────────┘  └──────────┬───────────────┘  │
│                                                  │                   │
│                                                  ▼                   │
│                                       ┌──────────────────────┐     │
│                                       │  Feature Engineering │     │
│                                       │  (Age, Spend, etc.)  │     │
│                                       └──────────┬───────────┘     │
│                                                  │                   │
│                                                  ▼                   │
│                                       ┌──────────────────────┐     │
│                                       │  Feature Selection   │     │
│                                       │  (Mutual Info top-15)│     │
│                                       └──────────┬───────────┘     │
│                                                  │                   │
│                                                  ▼                   │
│                              ┌─────────────────────────────────┐    │
│                              │   Clustering Engine             │    │
│                              │   (10 algorithms evaluated)     │    │
│                              │   → Best model selected         │    │
│                              └────────────┬────────────────────┘    │
│                                           │                          │
│                                           ▼                          │
│                              ┌─────────────────────────────────┐    │
│                              │   Supervised Trainer            │    │
│                              │   (11 models + Voting/Stacking) │    │
│                              │   → Best classifier selected    │    │
│                              └────────────┬────────────────────┘    │
│                                           │                          │
│                                           ▼                          │
│                              ┌─────────────────────────────────┐    │
│                              │   AutoGluon AutoML (optional)   │    │
│                              └────────────┬────────────────────┘    │
│                                           │                          │
│                                           ▼                          │
│                              ┌─────────────────────────────────┐    │
│                              │   Explainability                │    │
│                              │   (SHAP global + LIME local)    │    │
│                              └────────────┬────────────────────┘    │
│                                           │                          │
└───────────────────────────────────────────┼──────────────────────────┘
                                            │
                                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          ARTIFACT LAYER                              │
│                                                                      │
│   saved_models/                    artifacts/                        │
│   ├── best_classifier.joblib       ├── models/                       │
│   ├── best_clusterer.joblib        ├── trained_models/ (11 .joblib)  │
│   ├── preprocessor.joblib          ├── reports/ (4 JSON reports)     │
│   ├── scaler.joblib                └── plots/                        │
│   ├── feature_selector.joblib                                       │
│   ├── feature_store.joblib                                          │
│   ├── autogluon/                                                    │
│   └── explainability/                                               │
└──────────────────────────────────┬──────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       INFERENCE & DEPLOYMENT                         │
│                                                                      │
│   ┌────────────────────┐        ┌───────────────────────────────┐   │
│   │   PredictPipeline  │◄───────│      Streamlit Dashboard      │   │
│   │   (loads artifacts)│        │  • Home / Dashboard           │   │
│   └─────────┬──────────┘        │  • About Project              │   │
│             │                   │  • Dataset Overview           │   │
│             ▼                   │  • EDA Dashboard              │   │
│   ┌────────────────────┐        │  • Cluster Visualization      │   │
│   │  PredictionResult  │───────►│  • Customer Prediction        │   │
│   │  • cluster         │        │  • Business Insights          │   │
│   │  • probabilities   │        └───────────────────────────────┘   │
│   │  • recommendations │                                           │
│   └────────────────────┘                                           │
└─────────────────────────────────────────────────────────────────────┘
```

## SOLID Principles Applied

| Principle | Implementation |
|---|---|
| **S**ingle Responsibility | Each module has one job: `ingestion.py` only ingests, `validation.py` only validates, etc. |
| **O**pen/Closed | Add new clustering algorithms by editing `params.yaml` + adding a case in `clustering.py` — no other code changes |
| **L**iskov Substitution | All clustering algorithms conform to sklearn's `ClusterMixin` interface |
| **I**nterface Segregation | Small, focused dataclasses for each artifact (`IngestionArtifact`, `ValidationReport`, etc.) |
| **D**ependency Inversion | Pipeline depends on `ConfigurationManager` abstraction (dataclass), not YAML files directly |

## Design Patterns Used

| Pattern | Where |
|---|---|
| **Strategy** | Clustering algorithm selection, feature selection method |
| **Template Method** | `TrainPipeline.run()` orchestrates the workflow |
| **Factory** | `_build_models()` creates model instances from config |
| **Adapter** | `PredictPipeline` wraps the raw model + preprocessing for inference |
| **Data Transfer Object** | All `*Artifact` dataclasses |
| **Singleton (lazy)** | `PredictPipeline.classifier` property loads model once |

## Data Flow

```
CSV ──► DataFrame ──► Validated DataFrame ──► Transformed Array
                                                    │
                                                    ▼
                                          Engineered DataFrame
                                                    │
                                                    ▼
                                          Selected Features (15)
                                                    │
                                                    ▼
                                          Cluster Labels (0/1/2)
                                                    │
                                  ┌─────────────────┴─────────────────┐
                                  ▼                                   ▼
                          Train/Test Split                    SHAP Values
                                  │                                   │
                                  ▼                                   ▼
                          11 Classifiers                     LIME Explanations
                                  │
                                  ▼
                          Best Classifier
                                  │
                                  ▼
                          Persisted Artifacts
                                  │
                                  ▼
                          Streamlit Dashboard
```
