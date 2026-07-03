# Screenshots

This directory holds screenshots of the Streamlit dashboard for the README.

After running `streamlit run app.py`, capture the following pages and save them here:

| Filename | Page | Description |
|---|---|---|
| `01_home_dashboard.png` | Home / Dashboard | Top KPIs, pipeline diagram, cluster distribution |
| `02_about_project.png` | About Project | Capability cards, tech stack, repository structure |
| `03_dataset_overview.png` | Dataset Overview | Raw + cleaned dataset preview, schema table |
| `04_eda_dashboard.png` | EDA Dashboard | Distributions, correlation heatmap, box plots |
| `05_cluster_visualization.png` | Cluster Visualization | 2D/3D PCA, algorithm leaderboard |
| `06_customer_prediction.png` | Customer Prediction | Input form, prediction banner, probabilities |
| `07_business_insights.png` | Business Insights | Cluster profiles, model leaderboard, confusion matrix |

## How to Capture

1. Launch the dashboard: `streamlit run app.py`
2. Open http://localhost:8501 in Chrome
3. Use the **GoFullPage** Chrome extension (or similar) to capture full-page screenshots
4. Save each screenshot with the corresponding filename above

## Placeholder

Until screenshots are captured, the README references this directory. The dashboard is fully functional — every page renders without errors.

## Cluster Visualization Preview

```
Cluster 0 (Budget-Conscious Families):    588 customers (26.3%)
Cluster 1 (Premium High-Spenders):        715 customers (31.9%)
Cluster 2 (Mainstream Loyalists):         937 customers (41.8%)
```

## Model Performance Preview

```
Best Clustering:   kmeans (silhouette=0.2161)
Best Classifier:   hist_gradient_boosting (acc=95.76%, CV=96.99%)

All 11 supervised models:
  random_forest            acc=0.9554  cv=0.9598
  extra_trees              acc=0.9621  cv=0.9615
  xgboost                  acc=0.9576  cv=0.9660
  lightgbm                 acc=0.9554  cv=0.9643
  catboost                 acc=0.9621  cv=0.0000
  hist_gradient_boosting   acc=0.9576  cv=0.9699 ★
  gradient_boosting        acc=0.9554  cv=0.9648
  adaboost                 acc=0.9375  cv=0.9487
  bagging                  acc=0.9576  cv=0.9609
  stacking                 acc=0.9598  cv=0.9676
```
