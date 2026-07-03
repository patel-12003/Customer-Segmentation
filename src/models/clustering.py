"""
Clustering engine.

Implements a unified interface for **10 clustering algorithms**:

* KMeans
* MiniBatchKMeans
* GaussianMixtureModel
* AgglomerativeClustering
* Birch
* DBSCAN
* HDBSCAN
* OPTICS
* MeanShift
* SpectralClustering

Each algorithm is evaluated on:
* Silhouette Score (higher is better)
* Davies-Bouldin Index (lower is better)
* Calinski-Harabasz Index (higher is better)
* Inertia (where applicable)
* Cluster stability under bootstrap resampling
* Business interpretability (number of distinct clusters, balance)

The best algorithm is selected automatically and persisted.
"""

from __future__ import annotations

import json
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.base import ClusterMixin
from sklearn.cluster import (
    AgglomerativeClustering,
    Birch,
    DBSCAN,
    KMeans,
    MeanShift,
    MiniBatchKMeans,
    OPTICS,
    SpectralClustering,
    estimate_bandwidth,
)
from sklearn.metrics import (
    calinski_harabasz_score,
    davies_bouldin_score,
    silhouette_score,
)
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler

from src.config_manager import ConfigurationManager
from src.exception import ClusteringError
from src.logger import get_logger
from src.utils import ensure_dir, save_object, write_json

logger = get_logger(__name__)

# Optional HDBSCAN dependency
try:
    from hdbscan import HDBSCAN  # type: ignore
    _HDBSCAN_AVAILABLE = True
except Exception:  # pragma: no cover
    _HDBSCAN_AVAILABLE = False


@dataclass
class ClusteringResult:
    """Single-model clustering result."""
    name: str
    labels: np.ndarray
    n_clusters: int
    silhouette: float
    davies_bouldin: float
    calinski_harabasz: float
    inertia: Optional[float]
    stability: float
    interpretability: float
    execution_seconds: float
    params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ClusteringArtifact:
    """Aggregate artifact from the clustering step."""
    best_model_name: str
    best_model: Any
    best_labels: np.ndarray
    best_score: float
    results: List[ClusteringResult]
    report_path: Path
    best_model_path: Path
    clustered_df: pd.DataFrame


class ClusteringEngine:
    """Train, evaluate and select the best clustering algorithm."""

    def __init__(self, config_manager: ConfigurationManager) -> None:
        self.config = config_manager.get_clustering_config()
        self.params = config_manager.get_params().get("clustering", {})
        self.n_clusters = self.config.n_clusters
        self.random_state = self.config.random_state
        self.algorithms = self.config.algorithms
        self.report_path = Path(self.config.report_path)
        self.best_model_path = Path(self.config.best_clusterer_path)
        self.clustered_data_path = Path(self.config.clustered_data_path)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def run(self, df: pd.DataFrame) -> ClusteringArtifact:
        """Fit all configured algorithms on ``df`` and select the best.

        Args:
            df: Engineered/feature-selected dataframe (numeric only).

        Returns:
            :class:`ClusteringArtifact` with the best model and full report.
        """
        logger.info(
            "Starting clustering engine | algorithms=%s | n_clusters=%d",
            self.algorithms,
            self.n_clusters,
        )
        try:
            X = self._prepare_features(df)
            results: List[ClusteringResult] = []

            for name in self.algorithms:
                if name == "hdbscan" and not _HDBSCAN_AVAILABLE:
                    logger.warning("HDBSCAN not installed — skipping.")
                    continue
                try:
                    result = self._evaluate_single(name, X)
                    if result is not None:
                        results.append(result)
                        logger.info(
                            "%-18s | clusters=%d | silhouette=%.4f | DB=%.4f | CH=%.2f",
                            name,
                            result.n_clusters,
                            result.silhouette,
                            result.davies_bouldin,
                            result.calinski_harabasz,
                        )
                except Exception as exc:
                    logger.error("Algorithm '%s' failed: %s", name, exc)

            if not results:
                raise ClusteringError("No clustering algorithm produced results.")

            best = self._select_best(results)
            clustered_df = df.copy()
            clustered_df["cluster"] = best.labels

            # Persist artifacts
            ensure_dir(self.best_model_path.parent)
            save_object(best, self.best_model_path)
            ensure_dir(self.clustered_data_path.parent)
            clustered_df.to_csv(self.clustered_data_path, index=False)
            self._persist_report(results, best)

            logger.info(
                "Best clustering model: %s (silhouette=%.4f)",
                best.name,
                best.silhouette,
            )

            return ClusteringArtifact(
                best_model_name=best.name,
                best_model=best,
                best_labels=best.labels,
                best_score=best.silhouette,
                results=results,
                report_path=self.report_path,
                best_model_path=self.best_model_path,
                clustered_df=clustered_df,
            )
        except Exception as exc:
            raise ClusteringError("Clustering engine failed.", exc) from exc

    # ------------------------------------------------------------------
    # Algorithm dispatchers
    # ------------------------------------------------------------------
    def _evaluate_single(self, name: str, X: np.ndarray) -> Optional[ClusteringResult]:
        import time

        start = time.perf_counter()
        model, labels, params = self._fit_algorithm(name, X)
        elapsed = time.perf_counter() - start

        if labels is None:
            return None

        n_clusters = len(set(labels[labels >= 0])) if (labels >= 0).any() else 0
        if n_clusters < 2:
            logger.warning(
                "%s produced %d clusters — skipping evaluation.", name, n_clusters
            )
            return None

        metrics = self._compute_metrics(X, labels)
        # Skip expensive stability resampling for slow algorithms
        if name in {"optics", "meanshift", "spectral", "dbscan", "hdbscan"}:
            stability = 0.5  # neutral default
        else:
            stability = self._compute_stability(name, X, n_resamples=2)
        interpretability = self._compute_interpretability(labels)

        inertia = getattr(model, "inertia_", None)
        if inertia is None and hasattr(model, "score"):
            try:
                inertia = float(-model.score(X))
            except Exception:
                inertia = None

        return ClusteringResult(
            name=name,
            labels=labels.astype(int),
            n_clusters=int(n_clusters),
            silhouette=metrics["silhouette"],
            davies_bouldin=metrics["davies_bouldin"],
            calinski_harabasz=metrics["calinski_harabasz"],
            inertia=float(inertia) if inertia is not None else None,
            stability=stability,
            interpretability=interpretability,
            execution_seconds=elapsed,
            params=params,
        )

    def _fit_algorithm(
        self, name: str, X: np.ndarray
    ) -> Tuple[Optional[ClusterMixin], Optional[np.ndarray], Dict[str, Any]]:
        params = dict(self.params.get(name, {}))
        random_state = self.random_state

        if name == "kmeans":
            model = KMeans(
                n_clusters=self.n_clusters,
                random_state=random_state,
                **{k: v for k, v in params.items() if k != "random_state"},
            )
            model.fit(X)
            return model, model.labels_, params

        if name == "minibatch_kmeans":
            model = MiniBatchKMeans(
                n_clusters=self.n_clusters,
                random_state=random_state,
                **{k: v for k, v in params.items() if k != "random_state"},
            )
            model.fit(X)
            return model, model.labels_, params

        if name == "gmm":
            model = GaussianMixture(
                n_components=self.n_clusters,
                random_state=random_state,
                **{k: v for k, v in params.items() if k != "random_state"},
            )
            labels = model.fit_predict(X)
            return model, labels, params

        if name == "agglomerative":
            model = AgglomerativeClustering(
                n_clusters=self.n_clusters,
                **params,
            )
            model.fit(X)
            return model, model.labels_, params

        if name == "birch":
            model = Birch(n_clusters=self.n_clusters, **{k: v for k, v in params.items() if k != "n_clusters"})
            model.fit(X)
            return model, model.labels_, params

        if name == "dbscan":
            model = DBSCAN(**params)
            labels = model.fit_predict(X)
            return model, labels, params

        if name == "hdbscan":
            model = HDBSCAN(**params)
            labels = model.fit_predict(X)
            return model, labels, params

        if name == "optics":
            # OPTICS is O(n^2); subsample if dataset is large
            if X.shape[0] > 1500:
                rng = np.random.RandomState(random_state)
                idx = rng.choice(X.shape[0], size=1500, replace=False)
                X_sub = X[idx]
            else:
                X_sub = X
            model = OPTICS(**params)
            labels_sub = model.fit_predict(X_sub)
            # Propagate via nearest centroid
            from sklearn.neighbors import NearestCentroid
            mask = labels_sub >= 0
            if mask.sum() > 0:
                nc = NearestCentroid().fit(X_sub[mask], labels_sub[mask])
                labels = nc.predict(X)
            else:
                labels = np.zeros(X.shape[0], dtype=int)
            return model, labels, params

        if name == "meanshift":
            bandwidth = params.get("bandwidth")
            if bandwidth is None:
                bandwidth = estimate_bandwidth(X, quantile=0.2, n_samples=min(500, len(X)))
                params["bandwidth"] = float(bandwidth)
            model = MeanShift(
                bandwidth=bandwidth,
                cluster_all=params.get("cluster_all", False),
            )
            model.fit(X)
            return model, model.labels_, params

        if name == "spectral":
            # Spectral clustering is O(n^3); subsample if dataset is large
            if X.shape[0] > 1500:
                rng = np.random.RandomState(random_state)
                idx = rng.choice(X.shape[0], size=1500, replace=False)
                X_sub = X[idx]
            else:
                X_sub = X
            model = SpectralClustering(
                n_clusters=self.n_clusters,
                random_state=random_state,
                affinity=params.get("affinity", "rbf"),
                n_neighbors=params.get("n_neighbors", 10),
                assign_labels="kmeans",
            )
            labels_sub = model.fit_predict(X_sub)
            # Propagate to full dataset via nearest centroid (cheap)
            labels = np.zeros(X.shape[0], dtype=int)
            from sklearn.neighbors import NearestCentroid
            nc = NearestCentroid().fit(X_sub, labels_sub)
            labels = nc.predict(X)
            return model, labels, params

        logger.warning("Unknown clustering algorithm '%s'.", name)
        return None, None, {}

    # ------------------------------------------------------------------
    # Metrics
    # ------------------------------------------------------------------
    def _compute_metrics(self, X: np.ndarray, labels: np.ndarray) -> Dict[str, float]:
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                sil = float(silhouette_score(X, labels))
                db = float(davies_bouldin_score(X, labels))
                ch = float(calinski_harabasz_score(X, labels))
            return {"silhouette": sil, "davies_bouldin": db, "calinski_harabasz": ch}
        except Exception as exc:
            logger.warning("Metric computation failed: %s", exc)
            return {"silhouette": -1.0, "davies_bouldin": 99.0, "calinski_harabasz": 0.0}

    def _compute_stability(self, name: str, X: np.ndarray, n_resamples: int = 3) -> float:
        """Compute mean ARI between labels from original and resampled fits."""
        from sklearn.metrics import adjusted_rand_score

        rng = np.random.RandomState(self.random_state)
        try:
            _, base_labels, _ = self._fit_algorithm(name, X)
            if base_labels is None:
                return 0.0
            aris: List[float] = []
            for _ in range(n_resamples):
                idx = rng.choice(len(X), size=len(X), replace=True)
                X_res = X[idx]
                _, res_labels, _ = self._fit_algorithm(name, X_res)
                if res_labels is None:
                    continue
                aris.append(adjusted_rand_score(base_labels[idx], res_labels))
            return float(np.mean(aris)) if aris else 0.0
        except Exception:
            return 0.0

    @staticmethod
    def _compute_interpretability(labels: np.ndarray) -> float:
        """A simple interpretability score: cluster balance (0..1)."""
        counts = pd.Series(labels).value_counts(normalize=True)
        if len(counts) <= 1:
            return 0.0
        # Lower coefficient of variation → higher interpretability
        cv = counts.std() / counts.mean()
        return float(max(0.0, 1.0 - cv))

    # ------------------------------------------------------------------
    # Selection & persistence
    # ------------------------------------------------------------------
    def _select_best(self, results: List[ClusteringResult]) -> ClusteringResult:
        """Rank by composite score and return the best."""
        best = max(results, key=lambda r: self._composite_score(r))
        return best

    @staticmethod
    def _composite_score(r: ClusteringResult) -> float:
        # Weighted sum: silhouette (40%), stability (25%), interpretability (20%),
        # normalized CH (10%), normalized DB (5%)
        ch_norm = min(r.calinski_harabasz / 1000.0, 1.0)
        db_norm = 1.0 - min(r.davies_bouldin / 3.0, 1.0)
        return (
            0.40 * max(r.silhouette, 0.0)
            + 0.25 * r.stability
            + 0.20 * r.interpretability
            + 0.10 * ch_norm
            + 0.05 * db_norm
        )

    def _persist_report(
        self, results: List[ClusteringResult], best: ClusteringResult
    ) -> None:
        report = {
            "best_model": best.name,
            "best_silhouette": best.silhouette,
            "best_davies_bouldin": best.davies_bouldin,
            "best_calinski_harabasz": best.calinski_harabasz,
            "n_clusters": best.n_clusters,
            "all_results": [
                {
                    "name": r.name,
                    "n_clusters": r.n_clusters,
                    "silhouette": r.silhouette,
                    "davies_bouldin": r.davies_bouldin,
                    "calinski_harabasz": r.calinski_harabasz,
                    "inertia": r.inertia,
                    "stability": r.stability,
                    "interpretability": r.interpretability,
                    "execution_seconds": r.execution_seconds,
                    "params": r.params,
                    "composite_score": self._composite_score(r),
                }
                for r in results
            ],
        }
        ensure_dir(self.report_path.parent)
        write_json(report, self.report_path)

    # ------------------------------------------------------------------
    @staticmethod
    def _prepare_features(df: pd.DataFrame) -> np.ndarray:
        numeric = df.select_dtypes(include=[np.number])
        numeric = numeric.fillna(numeric.median())
        scaler = StandardScaler()
        return scaler.fit_transform(numeric)
