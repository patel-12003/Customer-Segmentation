"""
Plotting helpers.

Centralised matplotlib/seaborn helpers used by the training pipeline
and the Streamlit app. All figures use a dark, professional palette
so they look great on the dashboard.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import matplotlib
matplotlib.use("Agg")  # non-interactive default
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from src.constants import PLOTS_DIR
from src.logger import get_logger
from src.utils import ensure_dir

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Theme — dark, professional, dashboard-ready
# ---------------------------------------------------------------------------
DARK_PALETTE = {
    "background": "#0e1117",
    "panel": "#1b2230",
    "text": "#e8eef5",
    "grid": "#2a323f",
    "primary": "#00d2ff",
    "secondary": "#7c4dff",
    "accent": "#00e676",
    "warning": "#ffab40",
    "danger": "#ff5252",
    "palette": ["#00d2ff", "#7c4dff", "#00e676", "#ffab40", "#ff5252",
                "#26c6da", "#ec407a", "#9ccc65"],
}


def apply_dark_theme() -> None:
    """Apply the project dark theme to matplotlib + seaborn."""
    plt.rcParams.update({
        "figure.facecolor": DARK_PALETTE["background"],
        "axes.facecolor": DARK_PALETTE["panel"],
        "axes.edgecolor": DARK_PALETTE["grid"],
        "axes.labelcolor": DARK_PALETTE["text"],
        "axes.titlecolor": DARK_PALETTE["text"],
        "xtick.color": DARK_PALETTE["text"],
        "ytick.color": DARK_PALETTE["text"],
        "grid.color": DARK_PALETTE["grid"],
        "grid.alpha": 0.4,
        "legend.facecolor": DARK_PALETTE["panel"],
        "legend.edgecolor": DARK_PALETTE["grid"],
        "text.color": DARK_PALETTE["text"],
        "font.family": "DejaVu Sans",
        "axes.titlesize": 14,
        "axes.labelsize": 11,
        "axes.spines.top": False,
        "axes.spines.right": False,
    })
    sns.set_palette(DARK_PALETTE["palette"])


apply_dark_theme()


class Plotter:
    """Collection of static plotting helpers used across the project."""

    # ------------------------------------------------------------------
    # Clustering
    # ------------------------------------------------------------------
    @staticmethod
    def cluster_scatter(
        df: pd.DataFrame,
        x: str,
        y: str,
        cluster_col: str = "cluster",
        title: Optional[str] = None,
        save_path: Optional[Union[str, Path]] = None,
    ) -> matplotlib.figure.Figure:
        fig, ax = plt.subplots(figsize=(8, 5.5), constrained_layout=True)
        sns.scatterplot(
            data=df,
            x=x,
            y=y,
            hue=cluster_col,
            palette=DARK_PALETTE["palette"],
            s=45,
            alpha=0.85,
            edgecolor="none",
            ax=ax,
        )
        ax.set_title(title or f"{y} vs {x} by Cluster", weight="bold")
        ax.legend(title=cluster_col, loc="best", frameon=True)
        if save_path:
            ensure_dir(Path(save_path).parent)
            fig.savefig(save_path, dpi=140, facecolor=fig.get_facecolor())
        return fig

    @staticmethod
    def cluster_2d_pca(
        X: np.ndarray,
        labels: np.ndarray,
        title: str = "Customer Segments (PCA 2D)",
        save_path: Optional[Union[str, Path]] = None,
    ) -> matplotlib.figure.Figure:
        from sklearn.decomposition import PCA

        pca = PCA(n_components=2, random_state=42)
        comps = pca.fit_transform(X)
        fig, ax = plt.subplots(figsize=(8, 5.5), constrained_layout=True)
        for c in sorted(set(labels)):
            mask = labels == c
            ax.scatter(
                comps[mask, 0],
                comps[mask, 1],
                s=35,
                alpha=0.8,
                label=f"Cluster {c}",
                color=DARK_PALETTE["palette"][c % len(DARK_PALETTE["palette"])],
                edgecolor="none",
            )
        ax.set_xlabel(f"PC1 ({pca.explained_variance_ratio_[0]:.1%})")
        ax.set_ylabel(f"PC2 ({pca.explained_variance_ratio_[1]:.1%})")
        ax.set_title(title, weight="bold")
        ax.legend(frameon=True)
        if save_path:
            ensure_dir(Path(save_path).parent)
            fig.savefig(save_path, dpi=140, facecolor=fig.get_facecolor())
        return fig

    # ------------------------------------------------------------------
    # Model comparison
    # ------------------------------------------------------------------
    @staticmethod
    def model_comparison_bar(
        results: List[Dict[str, Any]],
        metric: str = "accuracy",
        title: Optional[str] = None,
        save_path: Optional[Union[str, Path]] = None,
    ) -> matplotlib.figure.Figure:
        df = pd.DataFrame(results).sort_values(metric, ascending=True)
        fig, ax = plt.subplots(figsize=(9, max(4, 0.4 * len(df))), constrained_layout=True)
        colors = [DARK_PALETTE["primary"]] * len(df)
        if len(df) > 0:
            colors[-1] = DARK_PALETTE["accent"]
        ax.barh(df["name"], df[metric], color=colors, edgecolor="none")
        for i, (name, val) in enumerate(zip(df["name"], df[metric])):
            ax.text(val + 0.005, i, f"{val:.4f}", color=DARK_PALETTE["text"], va="center", fontsize=9)
        ax.set_xlabel(metric.replace("_", " ").title())
        ax.set_title(title or f"Model Comparison — {metric}", weight="bold")
        ax.grid(True, axis="x", alpha=0.3)
        if save_path:
            ensure_dir(Path(save_path).parent)
            fig.savefig(save_path, dpi=140, facecolor=fig.get_facecolor())
        return fig

    @staticmethod
    def confusion_matrix_heatmap(
        cm: List[List[int]],
        labels: Optional[List[str]] = None,
        title: str = "Confusion Matrix",
        save_path: Optional[Union[str, Path]] = None,
    ) -> matplotlib.figure.Figure:
        cm_arr = np.array(cm)
        if labels is None:
            labels = [str(i) for i in range(len(cm_arr))]
        fig, ax = plt.subplots(figsize=(6, 5), constrained_layout=True)
        sns.heatmap(
            cm_arr,
            annot=True,
            fmt="d",
            cmap="viridis",
            xticklabels=labels,
            yticklabels=labels,
            cbar=False,
            ax=ax,
            linewidths=0.5,
            linecolor=DARK_PALETTE["background"],
        )
        ax.set_xlabel("Predicted")
        ax.set_ylabel("Actual")
        ax.set_title(title, weight="bold")
        if save_path:
            ensure_dir(Path(save_path).parent)
            fig.savefig(save_path, dpi=140, facecolor=fig.get_facecolor())
        return fig

    # ------------------------------------------------------------------
    # EDA
    # ------------------------------------------------------------------
    @staticmethod
    def distribution_plot(
        df: pd.DataFrame,
        column: str,
        hue: Optional[str] = None,
        save_path: Optional[Union[str, Path]] = None,
    ) -> matplotlib.figure.Figure:
        fig, ax = plt.subplots(figsize=(8, 5), constrained_layout=True)
        if hue and hue in df.columns:
            for i, lvl in enumerate(sorted(df[hue].unique())):
                sub = df[df[hue] == lvl][column].dropna()
                if len(sub) == 0:
                    continue
                sns.kdeplot(sub, ax=ax, label=f"{hue}={lvl}",
                            color=DARK_PALETTE["palette"][i % len(DARK_PALETTE["palette"])],
                            fill=True, alpha=0.35)
            ax.legend(frameon=True)
        else:
            sns.histplot(df[column].dropna(), ax=ax, kde=True,
                         color=DARK_PALETTE["primary"], edgecolor="none", alpha=0.7)
        ax.set_title(f"Distribution of {column}", weight="bold")
        ax.grid(True, alpha=0.3)
        if save_path:
            ensure_dir(Path(save_path).parent)
            fig.savefig(save_path, dpi=140, facecolor=fig.get_facecolor())
        return fig

    @staticmethod
    def correlation_heatmap(
        df: pd.DataFrame,
        title: str = "Feature Correlation",
        save_path: Optional[Union[str, Path]] = None,
    ) -> matplotlib.figure.Figure:
        numeric = df.select_dtypes(include=[np.number])
        corr = numeric.corr()
        fig, ax = plt.subplots(figsize=(10, 8), constrained_layout=True)
        sns.heatmap(
            corr,
            cmap="coolwarm",
            center=0,
            annot=False,
            cbar_kws={"shrink": 0.7},
            ax=ax,
            linewidths=0.3,
            linecolor=DARK_PALETTE["background"],
        )
        ax.set_title(title, weight="bold")
        if save_path:
            ensure_dir(Path(save_path).parent)
            fig.savefig(save_path, dpi=140, facecolor=fig.get_facecolor())
        return fig

    @staticmethod
    def feature_importance_plot(
        importance_df: pd.DataFrame,
        top_n: int = 20,
        title: str = "Feature Importance",
        save_path: Optional[Union[str, Path]] = None,
    ) -> matplotlib.figure.Figure:
        df = importance_df.head(top_n).sort_values("importance", ascending=True)
        fig, ax = plt.subplots(figsize=(9, max(4, 0.35 * len(df))), constrained_layout=True)
        ax.barh(df["feature"], df["importance"], color=DARK_PALETTE["primary"], edgecolor="none")
        for i, val in enumerate(df["importance"]):
            ax.text(val + 0.002, i, f"{val:.4f}", color=DARK_PALETTE["text"], va="center", fontsize=8)
        ax.set_xlabel("Importance")
        ax.set_title(title, weight="bold")
        ax.grid(True, axis="x", alpha=0.3)
        if save_path:
            ensure_dir(Path(save_path).parent)
            fig.savefig(save_path, dpi=140, facecolor=fig.get_facecolor())
        return fig

    @staticmethod
    def cluster_profile_radar(
        profile_df: pd.DataFrame,
        cluster_col: str = "cluster",
        title: str = "Cluster Profiles",
        save_path: Optional[Union[str, Path]] = None,
    ) -> matplotlib.figure.Figure:
        """Radar chart comparing normalised cluster means."""
        if cluster_col not in profile_df.columns:
            return plt.figure()
        features = [c for c in profile_df.columns if c != cluster_col]
        # Normalise 0..1 per feature
        norm = profile_df.copy()
        for f in features:
            mn, mx = profile_df[f].min(), profile_df[f].max()
            norm[f] = (profile_df[f] - mn) / (mx - mn) if mx > mn else 0.5

        n_feat = len(features)
        angles = np.linspace(0, 2 * np.pi, n_feat, endpoint=False).tolist()
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True), constrained_layout=True)
        for i, (_, row) in enumerate(norm.iterrows()):
            vals = row[features].tolist()
            vals += vals[:1]
            ax.plot(angles, vals, color=DARK_PALETTE["palette"][i % len(DARK_PALETTE["palette"])],
                    linewidth=2, label=f"Cluster {row[cluster_col]}")
            ax.fill(angles, vals, color=DARK_PALETTE["palette"][i % len(DARK_PALETTE["palette"])],
                    alpha=0.18)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(features, fontsize=9)
        ax.set_title(title, weight="bold", pad=20)
        ax.legend(loc="upper right", bbox_to_anchor=(1.25, 1.05))
        if save_path:
            ensure_dir(Path(save_path).parent)
            fig.savefig(save_path, dpi=140, facecolor=fig.get_facecolor())
        return fig

    @staticmethod
    def cluster_count_bar(
        df: pd.DataFrame,
        cluster_col: str = "cluster",
        save_path: Optional[Union[str, Path]] = None,
    ) -> matplotlib.figure.Figure:
        counts = df[cluster_col].value_counts().sort_index()
        fig, ax = plt.subplots(figsize=(7, 4.5), constrained_layout=True)
        bars = ax.bar(counts.index.astype(str), counts.values,
                      color=DARK_PALETTE["palette"][:len(counts)], edgecolor="none")
        for bar in bars:
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height(),
                    f"{int(bar.get_height())}",
                    ha="center", va="bottom",
                    color=DARK_PALETTE["text"], fontsize=10, weight="bold")
        ax.set_xlabel("Cluster")
        ax.set_ylabel("Number of Customers")
        ax.set_title("Cluster Size Distribution", weight="bold")
        ax.grid(True, axis="y", alpha=0.3)
        if save_path:
            ensure_dir(Path(save_path).parent)
            fig.savefig(save_path, dpi=140, facecolor=fig.get_facecolor())
        return fig
