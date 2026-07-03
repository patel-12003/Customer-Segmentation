# Future Scope

## 1. Real-time Streaming Inference

**Current**: Batch prediction via Streamlit form.

**Future**: Stream customer events from Kafka/Redpanda, score in real time via Spark Structured Streaming or Flink, push segment updates to a CRM.

```
[Customer event] → [Kafka topic] → [Spark consumer] → [PredictPipeline] → [CRM webhook]
```

## 2. A/B Testing Framework

**Current**: Static cluster → recommendation mapping.

**Future**: Bayesian multi-armed bandit that automatically learns which recommendation works best per cluster and updates the mapping.

## 3. Time-Series Segmentation

**Current**: Snapshot segmentation based on aggregated features.

**Future**: Recurrent clustering (e.g., TimeSeriesKMeans with DTW) over 12-month rolling windows to capture customer lifecycle stage transitions.

## 4. Multi-Modal Features

**Current**: Tabular features only.

**Future**: Concatenate:
- Product image embeddings (via ResNet)
- Customer service transcript embeddings (via BERT)
- Browsing sequence embeddings (via Transformer)

into a unified customer representation before clustering.

## 5. Federated Learning

**Current**: Centralized training on a single CSV.

**Future**: Train across multiple regional databases without sharing raw data using FedAvg or FedProx, so each region's privacy is preserved while still benefiting from global patterns.

## 6. Active Learning

**Current**: Predict and trust.

**Future**: Flag low-confidence predictions for human review, incorporate the corrected label back into training, and retrain online.

## 7. Model Monitoring

**Current**: One-shot training.

**Future**: Continuous drift detection using:
- **Evidently AI**: statistical drift tests on feature distributions
- **Alibi Detect**: KS test, MMD, classifier-based drift
- Auto-retrain trigger when drift score exceeds threshold

## 8. REST API & Microservice

**Current**: Streamlit-only UI.

**Future**: FastAPI microservice with:
- `/predict` — single-customer inference
- `/predict/batch` — batch inference
- `/explain` — return SHAP values for a given customer
- `/health` — model version + uptime

## 9. Docker / Kubernetes

**Current**: Local Python only.

**Future**: 
- Multi-stage Dockerfile (slim runtime image)
- Helm chart for K8s deployment
- Horizontal Pod Autoscaler based on inference latency
- Model registry integration (MLflow)

## 10. Causal Inference & Uplift Modeling

**Current**: Correlation-based segmentation.

**Future**: Per-segment uplift modeling to estimate the causal effect of each marketing campaign on each segment, enabling true ROI optimization.

## 11. Graph-Based Segmentation

**Current**: Feature-based clustering.

**Future**: Build a customer-product bipartite graph, run GNN clustering (e.g., GraphSAGE + k-means on embeddings) to leverage social/collaborative signal.

## 12. Multi-Objective Optimization

**Current**: Single composite score (weighted sum).

**Future**: Pareto frontier of silhouette vs. interpretability vs. business value, letting stakeholders pick the trade-off interactively in the dashboard.
