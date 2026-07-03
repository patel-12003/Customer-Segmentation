# Prediction Guide

## Via Streamlit Dashboard (recommended)

```bash
streamlit run app.py
```

Navigate to the **🤖 Customer Prediction** page and either:

1. Enter customer features manually using the sliders
2. Click **🎲 Random Customer** to load a random customer from the dataset
3. Click **🔮 Predict Segment** to score the customer

The dashboard displays:

- Predicted cluster with confidence
- Probability distribution across all clusters
- Customer profile description
- Business recommendations
- Input summary
- Download prediction as JSON

## Via Python API

```python
from src.pipeline.predict_pipeline import PredictPipeline

predictor = PredictPipeline()

customer = {
    'Age': 45,
    'Education': 2,
    'Marital Status': 1,
    'Parental Status': 1,
    'Children': 2,
    'Income': 50000,
    'Total_Spending': 1000,
    'Days_as_Customer': 2500,
    'Recency': 50,
    'Wines': 300,
    'Fruits': 30,
    'Meat': 200,
    'Fish': 50,
    'Sweets': 30,
    'Gold': 50,
    'Web': 5,
    'Catalog': 3,
    'Store': 6,
    'Discount Purchases': 2,
    'Total Promo': 0,
    'NumWebVisitsMonth': 5,
}

result = predictor.predict(customer)
print(f'Predicted cluster: {result.predicted_cluster}')
print(f'Cluster name: {result.cluster_name}')
print(f'Confidence: {result.confidence:.4f}')
print(f'Probabilities: {result.probabilities}')
print(f'Recommendations: {result.recommendations}')
```

## Batch Prediction

```python
import pandas as pd
from src.pipeline.predict_pipeline import PredictPipeline

predictor = PredictPipeline()
df = pd.read_csv('data/raw/clustered_data.csv')
customers = df.drop(columns=['cluster']).head(100).to_dict(orient='records')

results = predictor.predict_batch(customers)
for r in results[:5]:
    print(f'Cluster {r.predicted_cluster} ({r.cluster_name}) — confidence {r.confidence:.2%}')
```

## Cluster Profiles

| Cluster | Name | Description | Recommendations |
|---|---|---|---|
| 0 | Budget-Conscious Families | Mid-income customers with children who look for discounts and visit the website frequently | Send targeted discount codes and family bundle offers. Promote web-only flash sales. Avoid premium-tier recommendations. |
| 1 | Premium High-Spenders | High-income customers who buy wine, meat, and gold products through catalog and store channels | Curate premium product bundles and loyalty rewards. Offer early access to new premium launches. Use personalized CRM communications. |
| 2 | Mainstream Loyalists | Mid-to-high income, low child responsibility, balanced spending across categories | Cross-sell complementary products across categories. Encourage catalog & store engagement. Introduce referral incentives. |

## Input Schema

All input features are documented in `prediction_schema.yaml`. Each feature has:

- `dtype`: int or float
- `min` / `max`: validation bounds
- `default`: default value if missing
- `description`: human-readable explanation

The `PredictPipeline._validate_input()` method coerces all input values to the expected dtype and fills missing values with their defaults.

## Adding a New Cluster Profile

Edit `prediction_schema.yaml`:

```yaml
cluster_profiles:
  3:  # new cluster
    name: "At-Risk Customers"
    description: "Low engagement, high recency, declining spend."
    recommendations:
      - "Send reactivation email with personalized offer."
      - "Survey to understand churn drivers."
```

Re-run training to discover the new cluster, then restart Streamlit.

## REST API (future work)

To expose the predictor as a REST API:

```python
# server.py (not included in this release)
from fastapi import FastAPI
from pydantic import BaseModel
from src.pipeline.predict_pipeline import PredictPipeline

app = FastAPI()
predictor = PredictPipeline()

class CustomerInput(BaseModel):
    Age: int
    Income: float
    # ... all 22 features

@app.post("/predict")
def predict(customer: CustomerInput):
    result = predictor.predict(customer.dict())
    return {
        "cluster": result.predicted_cluster,
        "cluster_name": result.cluster_name,
        "confidence": result.confidence,
        "probabilities": result.probabilities,
    }
```
