"""Evaluation subpackage."""

from src.evaluation.metrics import (
    compute_classification_metrics,
    compute_clustering_metrics,
    compare_models,
)

__all__ = [
    "compute_classification_metrics",
    "compute_clustering_metrics",
    "compare_models",
]
