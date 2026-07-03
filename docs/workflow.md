# Workflow

## End-to-End Training Workflow

```mermaid
flowchart TD
    A[Raw CSV Files] --> B[Data Ingestion]
    B --> C[Data Validation]
    C --> D[Data Transformation]
    D --> E[Feature Engineering]
    E --> F[Feature Selection]
    F --> G[Clustering Engine]
    
    G --> G1[KMeans]
    G --> G2[MiniBatchKMeans]
    G --> G3[GaussianMixture]
    G --> G4[Agglomerative]
    G --> G5[Birch]
    G --> G6[DBSCAN]
    G --> G7[HDBSCAN]
    G --> G8[OPTICS]
    G --> G9[MeanShift]
    G --> G10[Spectral]
    
    G1 & G2 & G3 & G4 & G5 & G6 & G7 & G8 & G9 & G10 --> H{Select Best}
    H --> I[Best Clusterer + Labels]
    
    I --> J[Supervised Trainer]
    J --> J1[RandomForest]
    J --> J2[ExtraTrees]
    J --> J3[XGBoost]
    J --> J4[LightGBM]
    J --> J5[CatBoost]
    J --> J6[HistGBM]
    J --> J7[GradientBoosting]
    J --> J8[AdaBoost]
    J --> J9[Bagging]
    J --> J10[Voting]
    J --> J11[Stacking]
    
    J1 & J2 & J3 & J4 & J5 & J6 & J7 & J8 & J9 & J10 & J11 --> K{Select Best}
    K --> L[Best Classifier]
    
    L --> M[AutoGluon AutoML]
    M --> N[Explainability - SHAP]
    N --> O[Explainability - LIME]
    O --> P[Persist Artifacts]
    P --> Q[Streamlit Dashboard]
```

## Prediction Workflow

```mermaid
sequenceDiagram
    participant U as User
    participant S as Streamlit App
    participant P as PredictPipeline
    participant M as Trained Model
    
    U->>S: Enter customer features
    S->>P: predict(features dict)
    P->>P: Validate against prediction_schema
    P->>P: Align feature columns
    P->>M: model.predict_proba(X)
    M-->>P: probabilities
    P->>P: Lookup cluster profile + recommendations
    P-->>S: PredictionResult
    S->>U: Display result + download JSON
```

## File Lifecycle

```
data/raw/marketing_campaign.csv     ← user-provided source
                │
                ▼
data/processed/ingested.csv         ← written by DataIngestion
                │
                ▼
data/processed/transformed.csv      ← written by DataTransformation
                │
                ▼
data/processed/engineered.csv       ← written by FeatureEngineer
                │
                ▼
data/processed/selected_features.csv ← written by FeatureSelector
                │
                ▼
data/processed/clustered.csv        ← written by ClusteringEngine
                │
                ▼
data/processed/train.csv            ← written by SupervisedModelTrainer
data/processed/test.csv             ← written by SupervisedModelTrainer
                │
                ▼
saved_models/best_classifier.joblib ← consumed by PredictPipeline
saved_models/best_clusterer.joblib
saved_models/preprocessor.joblib
saved_models/scaler.joblib
saved_models/feature_selector.joblib
saved_models/explainability/shap_values.joblib
saved_models/explainability/lime_explainer.joblib
                │
                ▼
artifacts/reports/clustering_report.json
artifacts/reports/supervised_report.json
artifacts/reports/validation_report.json
artifacts/reports/pipeline_summary.json
```
