"""
Evaluation metrics.

Pure-function helpers that wrap sklearn metrics with safe defaults so
they can be reused from training, notebooks, and the Streamlit app.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    log_loss,
    precision_score,
    recall_score,
    roc_auc_score,
    silhouette_score,
    davies_bouldin_score,
    calinski_harabasz_score,
)


def compute_classification_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_prob: Optional[np.ndarray] = None,
) -> Dict[str, Any]:
    """Compute the full classification metric suite.

    Args:
        y_true: Ground-truth labels.
        y_pred: Predicted labels.
        y_prob: Optional predicted probabilities.

    Returns:
        Dictionary of metrics and classification report.
    """
    metrics: Dict[str, Any] = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision_weighted": float(
            precision_score(y_true, y_pred, average="weighted", zero_division=0)
        ),
        "recall_weighted": float(
            recall_score(y_true, y_pred, average="weighted", zero_division=0)
        ),
        "f1_weighted": float(
            f1_score(y_true, y_pred, average="weighted", zero_division=0)
        ),
        "confusion_matrix": confusion_matrix(y_true, y_pred).tolist(),
        "classification_report": classification_report(
            y_true, y_pred, output_dict=True, zero_division=0
        ),
    }
    if y_prob is not None:
        try:
            classes = sorted(set(y_true))
            if len(classes) > 2:
                metrics["roc_auc"] = float(
                    roc_auc_score(y_true, y_prob, multi_class="ovr", average="weighted")
                )
            else:
                metrics["roc_auc"] = float(roc_auc_score(y_true, y_prob[:, 1]))
            metrics["log_loss"] = float(log_loss(y_true, y_prob))
        except Exception:
            metrics["roc_auc"] = None
            metrics["log_loss"] = None
    return metrics


def compute_clustering_metrics(
    X: np.ndarray, labels: np.ndarray
) -> Dict[str, float]:
    """Compute Silhouette, Davies-Bouldin and Calinski-Harabasz scores."""
    try:
        return {
            "silhouette": float(silhouette_score(X, labels)),
            "davies_bouldin": float(davies_bouldin_score(X, labels)),
            "calinski_harabasz": float(calinski_harabasz_score(X, labels)),
            "n_clusters": int(len(set(labels))),
        }
    except Exception:
        return {
            "silhouette": -1.0,
            "davies_bouldin": 99.0,
            "calinski_harabasz": 0.0,
            "n_clusters": int(len(set(labels))),
        }


def compare_models(results: List[Dict[str, Any]], metric: str = "accuracy") -> pd.DataFrame:
    """Build a comparison DataFrame from a list of model result dicts.

    Args:
        results: List of dicts each containing at least ``name`` and
            ``metric`` keys.
        metric: Metric to sort by (descending).

    Returns:
        Pandas DataFrame sorted by ``metric``.
    """
    df = pd.DataFrame(results)
    if metric in df.columns:
        df = df.sort_values(metric, ascending=False).reset_index(drop=True)
    return df
