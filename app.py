#!/usr/bin/env python3
"""
app.py — Customer Categorizer & Intelligent Classification Dashboard
=====================================================================
A professional, dark-themed Streamlit application that showcases every
stage of the customer-segmentation ML pipeline.

Pages
-----
1. Home / Dashboard
2. About Project
3. Dataset Overview
4. EDA Dashboard
5. Cluster Visualization
6. Customer Prediction
7. Business Insights

Run with:
    streamlit run app.py
"""

from __future__ import annotations

import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from streamlit_lottie import st_lottie
import requests

# Make project root importable
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Apply matplotlib dark theme before any plots
from src.visualization.plots import apply_dark_theme as _apply_mpl_theme  # noqa: E402
_apply_mpl_theme()

from src.config_manager import ConfigurationManager  # noqa: E402
from src.constants import (  # noqa: E402
    BEST_CLASSIFIER_FILE,
    CLEAN_DATA_FILE,
    CLUSTERING_REPORT_FILE,
    PLOTS_DIR,
    PROCESSED_DATA_DIR,
    RAW_DATA_FILE,
    REPORTS_DIR,
    SAVED_MODELS_DIR,
    SUPERVISED_REPORT_FILE,
)
from src.logger import get_logger  # noqa: E402
from src.pipeline.predict_pipeline import PredictPipeline  # noqa: E402
from src.ui_components import (  # noqa: E402
    apply_dark_theme,
    card,
    footer,
    metric_card,
    pill,
    section_header,
)
from src.utils import read_json  # noqa: E402

warnings.filterwarnings("ignore")
logger = get_logger("app")


# ---------------------------------------------------------------------------
# PageRouter — pages as functions
# ---------------------------------------------------------------------------
PAGES = [
    "🏠 Home",
    "ℹ️ About Project",
    "📊 Dataset Overview",
    "🔍 EDA Dashboard",
    "🎯 Cluster Visualization",
    "🤖 Customer Prediction",
    "💡 Business Insights",
]


# ---------------------------------------------------------------------------
# Streamlit config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Customer Categorizer AI",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_dark_theme()


# ---------------------------------------------------------------------------
# Cached data loaders
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def load_raw_data() -> pd.DataFrame:
    sep = "\t" if "\t" in open(RAW_DATA_FILE, "r", encoding="utf-8").readline() else ","
    return pd.read_csv(RAW_DATA_FILE, sep=sep)


@st.cache_data(show_spinner=False)
def load_clean_data() -> pd.DataFrame:
    df = pd.read_csv(CLEAN_DATA_FILE)
    df.columns = [c.replace(" ", "_") for c in df.columns]
    return df


@st.cache_data(show_spinner=False)
def load_clustering_report():
    if CLUSTERING_REPORT_FILE.exists():
        return read_json(CLUSTERING_REPORT_FILE)
    return None


@st.cache_data(show_spinner=False)
def load_supervised_report():
    if SUPERVISED_REPORT_FILE.exists():
        return read_json(SUPERVISED_REPORT_FILE)
    return None


@st.cache_resource(show_spinner=False)
def load_predictor() -> PredictPipeline:
    return PredictPipeline()


# ---------------------------------------------------------------------------
# Plotly dark theme helpers
# ---------------------------------------------------------------------------
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(27,34,48,1)",
    font=dict(color="#e8eef5", family="Inter, sans-serif"),
    margin=dict(l=40, r=20, t=60, b=40),
)
PLOTLY_COLORS = ["#00d2ff", "#7c4dff", "#00e676", "#ffab40",
                 "#ff5252", "#26c6da", "#ec407a", "#9ccc65"]


def style_plotly_fig(fig: go.Figure) -> go.Figure:
    fig.update_layout(**PLOTLY_LAYOUT)
    fig.update_xaxes(gridcolor="#2a323f", zerolinecolor="#2a323f")
    fig.update_yaxes(gridcolor="#2a323f", zerolinecolor="#2a323f")
    return fig


# ---------------------------------------------------------------------------
# Lottie animation loader
# ---------------------------------------------------------------------------
def load_lottie_url(url: str):
    """Load a Lottie animation from a URL."""
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except Exception:
        return None


# ===========================================================================
# PAGE 1 — Home / Dashboard
# ===========================================================================
def page_home():
    st.markdown("# <span style='font-size:1.8rem;'>🛍️</span>  Customer Categorizer & Intelligent Classification", unsafe_allow_html=True)
    st.markdown(
        "<p style='color:#9aa6b2;font-size:1.05rem;margin-top:-10px;'>"
        "An end-to-end, production-grade machine-learning system that "
        "automatically identifies customer segments and predicts the segment "
        "of any new customer in real time."
        "</p>",
        unsafe_allow_html=True,
    )

    # Top KPI row
    raw = load_raw_data()
    clean = load_clean_data()
    clu_report = load_clustering_report()
    sup_report = load_supervised_report()

    n_customers = len(raw)
    n_features_raw = raw.shape[1]
    n_features_clean = clean.shape[1] - 1  # exclude cluster
    n_clusters = clu_report.get("n_clusters", 3) if clu_report else clean["cluster"].nunique()
    best_model = sup_report.get("best_model", "—") if sup_report else "—"
    best_acc = sup_report.get("best_metrics", {}).get("accuracy", 0) if sup_report else 0

    cols = st.columns(6)
    with cols[0]:
        metric_card("Customers", f"{n_customers:,}", color="cyan")
    with cols[1]:
        metric_card("Raw Features", n_features_raw, color="purple")
    with cols[2]:
        metric_card("Engineered Features", n_features_clean, color="green")
    with cols[3]:
        metric_card("Segments", n_clusters, color="orange")
    with cols[4]:
        metric_card("Best Model", best_model.split("_")[0].title() if best_model != "—" else "—", color="pink")
    with cols[5]:
        metric_card("Accuracy", f"{best_acc:.1%}" if best_acc else "—", color="cyan")

    st.markdown("<br>", unsafe_allow_html=True)

    # Quick-start cards
    cols = st.columns(3)
    with cols[0]:
        card(
            "🎯 Unsupervised Segmentation",
            "Compared <b>10 clustering algorithms</b> (KMeans, GMM, DBSCAN, "
            "HDBSCAN, OPTICS, MeanShift, Spectral, Birch, Agglomerative, "
            "MiniBatchKMeans) and selected the best using Silhouette, "
            "Davies-Bouldin, Calinski-Harabasz and stability metrics.",
            color="cyan",
        )
    with cols[1]:
        card(
            "🤖 Supervised Classification",
            "Trained <b>11 supervised models</b> (Random Forest, XGBoost, "
            "LightGBM, CatBoost, HistGBM, GradientBoosting, AdaBoost, "
            "Bagging, Voting, Stacking) + AutoGluon to predict the segment "
            "of any new customer with calibrated probabilities.",
            color="purple",
        )
    with cols[2]:
        card(
            "💡 Explainable AI",
            "Every prediction is explained with <b>SHAP</b> (global + local "
            "feature attribution) and <b>LIME</b> (instance-level explanation) "
            "so business stakeholders can trust the model.",
            color="green",
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Pipeline diagram
    section_header("Pipeline Architecture", "End-to-end ML workflow", "🔧")
    pipeline_steps = [
        ("1. Ingestion", "Load raw CSV"),
        ("2. Validation", "Schema + range checks"),
        ("3. Transformation", "Impute + scale + encode"),
        ("4. Feature Eng.", "Derive business features"),
        ("5. Selection", "Mutual-info top-K"),
        ("6. Clustering", "10 algos compared"),
        ("7. Supervised", "11 models trained"),
        ("8. AutoML", "AutoGluon"),
        ("9. Explain", "SHAP + LIME"),
    ]
    cols = st.columns(len(pipeline_steps))
    for col, (title, desc) in zip(cols, pipeline_steps):
        col.markdown(
            f"""
            <div style='background:#1b2230;border:1px solid #2a323f;
                        border-radius:10px;padding:14px 8px;text-align:center;
                        height:100%;transition:all 0.2s ease;'>
                <div style='color:#00d2ff;font-weight:700;font-size:0.95rem;'>{title}</div>
                <div style='color:#9aa6b2;font-size:0.75rem;margin-top:6px;'>{desc}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br><br>", unsafe_allow_html=True)
    section_header("Cluster Distribution at a Glance", "Customers per segment", "📊")
    cluster_counts = clean["cluster"].value_counts().sort_index()
    fig = px.bar(
        x=cluster_counts.index.astype(str),
        y=cluster_counts.values,
        color=cluster_counts.index.astype(str),
        color_discrete_sequence=PLOTLY_COLORS,
        labels={"x": "Cluster", "y": "Number of Customers"},
    )
    fig.update_traces(text=cluster_counts.values, textposition="outside",
                      textfont=dict(color="#e8eef5", size=14))
    style_plotly_fig(fig)
    st.plotly_chart(fig, width='stretch')

    footer()


# ===========================================================================
# PAGE 2 — About
# ===========================================================================
def page_about():
    section_header("About This Project", "Mission, scope & tech stack", "ℹ️")
    st.markdown("""
    <div style='background:#1b2230;border:1px solid #2a323f;border-radius:14px;
                padding:24px 28px;color:#e8eef5;line-height:1.7;'>
    This project delivers an <b>end-to-end, production-ready Machine Learning system</b>
    for Customer Categorizer and intelligent customer classification. It is built as
    part of a <b>Master's in Data Science</b> capstone and is structured to be
    suitable for GitHub, academic evaluation, industry portfolios, and research
    publication.
    <br><br>
    The system performs <b>unsupervised segmentation</b> of customers based on
    demographic, behavioral and purchasing information, then trains
    <b>supervised classifiers</b> on the discovered segments so that any new
    customer can be assigned to a segment in real time.
    </div>
    """, unsafe_allow_html=True)

    section_header("Key Capabilities", "What the system can do", "✨")
    capabilities = [
        ("🎯", "Multi-Algorithm Clustering", "10 clustering algorithms evaluated in parallel"),
        ("🤖", "Multi-Model Classification", "11 supervised models + AutoGluon ensemble"),
        ("🧠", "Explainable AI", "SHAP + LIME global and local explanations"),
        ("📊", "Interactive Dashboard", "Dark-themed, responsive Streamlit UI"),
        ("💾", "Reproducible Pipelines", "Config-driven, modular, persisted artifacts"),
        ("📈", "Business Insights", "Cluster profiles with actionable recommendations"),
        ("⚡", "Real-time Inference", "Sub-second prediction for new customers"),
        ("🔧", "Config-Driven", "All knobs in YAML — no code changes to retune"),
    ]
    cols = st.columns(4)
    for i, (icon, title, desc) in enumerate(capabilities):
        with cols[i % 4]:
            st.markdown(
                f"""
                <div class='custom-card' style='text-align:center;height:100%;'>
                    <div style='font-size:2rem;'>{icon}</div>
                    <div style='color:#00d2ff;font-weight:700;margin-top:8px;font-size:0.95rem;'>{title}</div>
                    <div style='color:#9aa6b2;font-size:0.8rem;margin-top:6px;'>{desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    section_header("Technology Stack", "Tools & libraries", "🧰")
    stack = [
        ("Language", ["Python 3.11+"]),
        ("Data", ["pandas", "numpy", "pyyaml"]),
        ("ML Core", ["scikit-learn", "xgboost", "lightgbm", "catboost", "hdbscan"]),
        ("AutoML", ["AutoGluon"]),
        ("Tuning", ["Optuna"]),
        ("Explainability", ["SHAP", "LIME"]),
        ("Visualization", ["matplotlib", "seaborn", "plotly"]),
        ("App", ["Streamlit"]),
        ("Notebooks", ["Jupyter Lab"]),
    ]
    for category, items in stack:
        st.markdown(
            f"**{category}**: " + " • ".join(items)
        )

    section_header("Repository Structure", "Modular & enterprise-grade", "📁")
    st.code("""
customer_segmentation/
├── app.py                       # Streamlit dashboard
├── training.py                  # End-to-end pipeline orchestrator
├── config.yaml  params.yaml  schema.yaml  prediction_schema.yaml
├── model.yaml  logging.yaml
├── requirements.txt  setup.py  README.md
├── src/
│   ├── exception.py  logger.py  utils.py  constants.py  config_manager.py
│   ├── ui_components.py
│   ├── data/        { ingestion.py  validation.py  transformation.py }
│   ├── features/    { engineering.py  selection.py }
│   ├── models/      { clustering.py  supervised.py  autogluon_trainer.py  tuner.py }
│   ├── evaluation/  { metrics.py }
│   ├── explainability/ { shap_explainer.py  lime_explainer.py }
│   ├── pipeline/    { train_pipeline.py  predict_pipeline.py }
│   └── visualization/  { plots.py }
├── notebooks/                   # 9 executable notebooks
├── data/{raw, processed}/
├── artifacts/{models, trained_models, reports, plots}/
├── saved_models/                # best classifier, scaler, shap, lime, autogluon
├── reports/  assets/  tests/  docs/
""", language="text")

    footer()


# ===========================================================================
# PAGE 3 — Dataset Overview
# ===========================================================================
def page_dataset():
    section_header("Dataset Overview", "Source, schema & statistics", "📊")
    raw = load_raw_data()
    clean = load_clean_data()

    tab1, tab2, tab3 = st.tabs(["📁 Raw Dataset", "✨ Cleaned / Engineered", "📋 Schema"])

    with tab1:
        st.markdown(f"**marketing_campaign.csv** — `{raw.shape[0]:,}` rows × `{raw.shape[1]}` columns")
        st.dataframe(raw.head(50), width='stretch', height=400)
        st.markdown("#### Descriptive Statistics")
        st.dataframe(raw.describe(include="all").T.fillna("—"), width='stretch')
        st.markdown("#### Missing Values")
        nulls = raw.isnull().sum()
        nulls = nulls[nulls > 0]
        if len(nulls) > 0:
            st.dataframe(nulls.to_frame("missing_count"), width='stretch')
        else:
            st.success("No missing values found.")

    with tab2:
        st.markdown(f"**clustered_data.csv** — `{clean.shape[0]:,}` rows × `{clean.shape[1]}` columns (incl. cluster label)")
        st.dataframe(clean.head(50), width='stretch', height=400)
        st.markdown("#### Descriptive Statistics")
        st.dataframe(clean.describe().T, width='stretch')
        st.markdown("#### Cluster Distribution")
        counts = clean["cluster"].value_counts().sort_index()
        fig = px.pie(
            values=counts.values,
            names=[f"Cluster {c}" for c in counts.index],
            color_discrete_sequence=PLOTLY_COLORS,
            hole=0.55,
        )
        style_plotly_fig(fig)
        st.plotly_chart(fig, width='stretch')

    with tab3:
        st.markdown("#### Raw Dataset Schema")
        schema_df = pd.DataFrame([
            {"column": c, "dtype": str(raw[c].dtype),
             "non-null": int(raw[c].count()),
             "unique": int(raw[c].nunique())}
            for c in raw.columns
        ])
        st.dataframe(schema_df, width='stretch')
        st.markdown("#### Engineered Dataset Schema")
        schema_clean = pd.DataFrame([
            {"column": c, "dtype": str(clean[c].dtype),
             "non-null": int(clean[c].count()),
             "unique": int(clean[c].nunique())}
            for c in clean.columns
        ])
        st.dataframe(schema_clean, width='stretch')

    footer()


# ===========================================================================
# PAGE 4 — EDA
# ===========================================================================
def page_eda():
    section_header("Exploratory Data Analysis", "Distributions, correlations & segment profiles", "🔍")
    clean = load_clean_data()

    numeric_cols = [c for c in clean.select_dtypes(include="number").columns if c != "cluster"]

    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Distributions", "🔗 Correlations", "📦 Box by Cluster", "🎯 Pair Plot"
    ])

    with tab1:
        col = st.selectbox("Select feature", numeric_cols, index=numeric_cols.index("Income") if "Income" in numeric_cols else 0)
        fig = px.histogram(
            clean, x=col, color="cluster", nbins=40,
            color_discrete_sequence=PLOTLY_COLORS,
            marginal="box",
        )
        style_plotly_fig(fig)
        st.plotly_chart(fig, width='stretch')

    with tab2:
        corr = clean[numeric_cols].corr()
        fig = px.imshow(
            corr,
            color_continuous_scale="RdBu",
            zmin=-1, zmax=1,
            title="Correlation Heatmap",
        )
        fig.update_layout(**PLOTLY_LAYOUT)
        st.plotly_chart(fig, width='stretch')

    with tab3:
        col = st.selectbox("Pick feature for box plot", numeric_cols, index=numeric_cols.index("Total_Spending") if "Total_Spending" in numeric_cols else 0)
        fig = px.box(
            clean, x="cluster", y=col, color="cluster",
            color_discrete_sequence=PLOTLY_COLORS,
        )
        style_plotly_fig(fig)
        st.plotly_chart(fig, width='stretch')

    with tab4:
        default_cols = ["Income", "Total_Spending", "Recency", "Age"][:4]
        default_cols = [c for c in default_cols if c in clean.columns][:3]
        cols_sel = st.multiselect("Pick features for scatter matrix", numeric_cols, default=default_cols)
        if len(cols_sel) >= 2:
            fig = px.scatter_matrix(
                clean, dimensions=cols_sel, color="cluster",
                color_discrete_sequence=PLOTLY_COLORS,
                opacity=0.6, height=600,
            )
            fig.update_layout(**PLOTLY_LAYOUT)
            st.plotly_chart(fig, width='stretch')
        else:
            st.info("Select at least 2 features.")

    footer()


# ===========================================================================
# PAGE 5 — Cluster Visualization
# ===========================================================================
def page_clusters():
    section_header("Cluster Visualization", "2D / 3D projections and cluster profiles", "🎯")
    clean = load_clean_data()
    clu_report = load_clustering_report()

    feature_cols = [c for c in clean.columns if c != "cluster"]

    tab1, tab2, tab3, tab4 = st.tabs([
        "🛰️ 2D PCA", "🌐 3D PCA", "📊 Cluster Comparison", "🏆 Algorithm Leaderboard"
    ])

    with tab1:
        from sklearn.decomposition import PCA
        from sklearn.preprocessing import StandardScaler

        X = clean[feature_cols].fillna(0)
        X_scaled = StandardScaler().fit_transform(X)
        pca = PCA(n_components=2, random_state=42)
        comps = pca.fit_transform(X_scaled)
        plot_df = pd.DataFrame({"PC1": comps[:, 0], "PC2": comps[:, 1], "cluster": clean["cluster"]})
        fig = px.scatter(
            plot_df, x="PC1", y="PC2", color=plot_df["cluster"].astype(str),
            color_discrete_sequence=PLOTLY_COLORS, opacity=0.7,
            title=f"PCA 2D — explained variance: {pca.explained_variance_ratio_.sum():.1%}",
        )
        style_plotly_fig(fig)
        st.plotly_chart(fig, width='stretch')

    with tab2:
        from sklearn.decomposition import PCA
        from sklearn.preprocessing import StandardScaler
        X = clean[feature_cols].fillna(0)
        X_scaled = StandardScaler().fit_transform(X)
        pca = PCA(n_components=3, random_state=42)
        comps = pca.fit_transform(X_scaled)
        plot_df = pd.DataFrame({
            "PC1": comps[:, 0], "PC2": comps[:, 1], "PC3": comps[:, 2],
            "cluster": clean["cluster"].astype(str),
        })
        fig = px.scatter_3d(
            plot_df, x="PC1", y="PC2", z="PC3", color="cluster",
            color_discrete_sequence=PLOTLY_COLORS, opacity=0.7,
            title=f"PCA 3D — explained variance: {pca.explained_variance_ratio_.sum():.1%}",
        )
        fig.update_layout(**PLOTLY_LAYOUT, scene=dict(
            xaxis=dict(backgroundcolor="#1b2230", gridcolor="#2a323f", showbackground=True),
            yaxis=dict(backgroundcolor="#1b2230", gridcolor="#2a323f", showbackground=True),
            zaxis=dict(backgroundcolor="#1b2230", gridcolor="#2a323f", showbackground=True),
        ))
        st.plotly_chart(fig, width='stretch')

    with tab3:
        # Cluster profile means
        profile = clean.groupby("cluster").mean().reset_index()
        st.markdown("#### Mean feature values per cluster")
        st.dataframe(profile.style.format("{:.2f}"), width='stretch')
        # Compare two features
        c1, c2 = st.columns(2)
        with c1:
            fx = st.selectbox("X axis", feature_cols, index=feature_cols.index("Income") if "Income" in feature_cols else 0)
        with c2:
            fy = st.selectbox("Y axis", feature_cols, index=feature_cols.index("Total_Spending") if "Total_Spending" in feature_cols else 1)
        fig = px.scatter(
            clean, x=fx, y=fy, color=clean["cluster"].astype(str),
            color_discrete_sequence=PLOTLY_COLORS, opacity=0.7,
            title=f"{fy} vs {fx} by Cluster",
        )
        style_plotly_fig(fig)
        st.plotly_chart(fig, width='stretch')

    with tab4:
        if clu_report:
            results = clu_report.get("all_results", [])
            df = pd.DataFrame(results)
            best_algo = clu_report.get('best_model', 'N/A')
            st.markdown(
                f"<h4 style='color:#00d2ff !important;margin-bottom:16px;'>"
                f"<span style='font-size:1.3em;margin-right:8px;'>🏆</span> Best Algorithm: "
                f"<span style='background:rgba(0,210,255,0.15);color:#00d2ff;padding:4px 10px;"
                f"border-radius:6px;font-family:monospace;font-size:0.95em;'>{best_algo}</span></h4>",
                unsafe_allow_html=True
            )
            cols = st.columns(4)
            with cols[0]:
                metric_card("Silhouette", f"{clu_report.get('best_silhouette', 0):.4f}", color="cyan")
            with cols[1]:
                metric_card("Davies-Bouldin", f"{clu_report.get('best_davies_bouldin', 0):.4f}", color="purple")
            with cols[2]:
                metric_card("Calinski-Harabasz", f"{clu_report.get('best_calinski_harabasz', 0):.1f}", color="green")
            with cols[3]:
                metric_card("# Clusters", clu_report.get("n_clusters", 3), color="orange")
            st.markdown("#### All Clustering Algorithms")
            display_cols = ["name", "n_clusters", "silhouette", "davies_bouldin", "calinski_harabasz", "stability", "interpretability", "execution_seconds"]
            st.dataframe(df[display_cols].style.format({
                "silhouette": "{:.4f}",
                "davies_bouldin": "{:.4f}",
                "calinski_harabasz": "{:.2f}",
                "stability": "{:.4f}",
                "interpretability": "{:.4f}",
                "execution_seconds": "{:.2f}",
            }), width='stretch')
            # Bar chart
            fig = px.bar(
                df, x="silhouette", y="name", orientation="h",
                color="silhouette", color_continuous_scale="Viridis",
                title="Silhouette Score by Algorithm",
            )
            style_plotly_fig(fig)
            st.plotly_chart(fig, width='stretch')
        else:
            st.warning("Clustering report not found. Run `python training.py` first.")

    footer()


# ===========================================================================
# PAGE 6 — Customer Prediction
# ===========================================================================
def page_predict():
    section_header("Customer Segment Prediction", "Score a new customer in real time", "🤖")
    clean = load_clean_data()
    predictor = load_predictor()

    # Build sliders/inputs from prediction_schema features
    from src.constants import PREDICTION_SCHEMA_FILE
    from src.utils import read_yaml
    schema = read_yaml(PREDICTION_SCHEMA_FILE)
    feats = schema.get("features", [])
    profiles = schema.get("cluster_profiles", {})

    st.markdown("#### Enter customer details")
    inputs: dict = {}
    # Use 3-column grid
    cols = st.columns(3)
    for i, feat in enumerate(feats):
        with cols[i % 3]:
            name = feat["name"]
            default = feat.get("default", 0)
            mn = feat.get("min", 0)
            mx = feat.get("max", 100)
            help_txt = feat.get("description", "")
            if feat["dtype"] == "int":
                inputs[name] = st.slider(
                    name, min_value=int(mn), max_value=int(mx),
                    value=int(default), help=help_txt,
                )
            else:
                inputs[name] = st.slider(
                    name, min_value=float(mn), max_value=float(mx),
                    value=float(default), step=(mx - mn) / 100.0, help=help_txt,
                )

    st.markdown("<br>", unsafe_allow_html=True)
    col_btn1, col_btn2, _ = st.columns([1, 1, 4])
    predict_clicked = col_btn1.button("🔮 Predict Segment", type="primary")
    use_random = col_btn2.button("🎲 Random Customer")

    if use_random:
        sample = clean.sample(n=1, random_state=None).iloc[0]
        for feat in feats:
            if feat["name"] in sample.index:
                inputs[feat["name"]] = sample[feat["name"]]
        st.info(f"Loaded a random customer (index {sample.name}).")

    if predict_clicked or use_random:
        with st.spinner("Predicting..."):
            result = predictor.predict(inputs)

        # Result card
        st.markdown("<br>", unsafe_allow_html=True)
        cluster_name = result.cluster_name
        profile = result.cluster_profile

        # Big result banner
        st.markdown(
            f"""
            <div style='background:linear-gradient(135deg,#1b2230 0%,#242c3b 100%);
                        border:1px solid #00d2ff;border-radius:16px;padding:28px 32px;
                        box-shadow:0 8px 32px rgba(0,210,255,0.15);'>
                <div style='color:#9aa6b2;font-size:0.8rem;text-transform:uppercase;
                            letter-spacing:0.1em;font-weight:600;'>Predicted Segment</div>
                <div style='font-size:2.2rem;font-weight:800;
                            background:linear-gradient(90deg,#00d2ff,#7c4dff);
                            -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                            background-clip:text;margin-top:6px;'>
                    Cluster {result.predicted_cluster} — {cluster_name}
                </div>
                <div style='color:#9aa6b2;font-size:0.95rem;margin-top:8px;'>
                    Confidence: <b style='color:#00e676;'>{result.confidence:.1%}</b>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Probabilities
        st.markdown("#### Prediction Probabilities")
        prob_df = pd.DataFrame([
            {"cluster": k, "probability": v} for k, v in result.probabilities.items()
        ])
        fig = px.bar(
            prob_df, x="cluster", y="probability",
            color="cluster", color_discrete_sequence=PLOTLY_COLORS,
        )
        style_plotly_fig(fig)
        st.plotly_chart(fig, width='stretch')

        # Customer profile + recommendations
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### 📋 Customer Profile")
            desc = profile.get("description", "")
            st.markdown(
                f"""
                <div class='custom-card'>
                    <h3 style='color:#00d2ff;margin-top:0;'>{cluster_name}</h3>
                    <p style='color:#e8eef5;'>{desc}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown("#### 💡 Recommendations")
            recs = result.recommendations
            if recs:
                for r in recs:
                    st.markdown(f"- {r}")
            else:
                st.info("No recommendations configured for this segment.")

        # Input summary + download
        st.markdown("#### 📝 Input Summary")
        input_df = pd.DataFrame([
            {"feature": k, "value": v} for k, v in result.input_features.items()
        ])
        st.dataframe(input_df, width='stretch', height=300)

        # Download button
        result_dict = {
            "predicted_cluster": result.predicted_cluster,
            "cluster_name": result.cluster_name,
            "confidence": result.confidence,
            "probabilities": result.probabilities,
            "input_features": result.input_features,
            "recommendations": result.recommendations,
        }
        st.download_button(
            "⬇️ Download Prediction (JSON)",
            data=pd.Series(result_dict).to_json(indent=2),
            file_name="prediction_result.json",
            mime="application/json",
        )

    footer()


# ===========================================================================
# Customer Analytics helper — dynamic visualizations matching reference assets
# ===========================================================================
def _render_customer_analytics(clean: "pd.DataFrame") -> None:
    """
    Renders 5 interactive Plotly charts that mirror the reference static images:
      1. Cluster Sizes (bar/donut)
      2. Income Distribution by Cluster (violin/box)
      3. Spending Distribution by Cluster (violin/box)
      4. Cluster Radar (spider chart of normalised feature means)
    All charts have working filters and rich tooltips.
    """
    clusters = sorted(clean["cluster"].unique().tolist())
    cluster_labels = [f"Cluster {c}" for c in clusters]
    color_seq = PLOTLY_COLORS[: len(clusters)]

    # ── Global filter ─────────────────────────────────────────────────────
    selected_clusters = st.multiselect(
        "Filter clusters",
        options=clusters,
        default=clusters,
        format_func=lambda c: f"Cluster {c}",
        key="analytics_cluster_filter",
    )
    if not selected_clusters:
        st.info("Select at least one cluster above.")
        return

    filtered = clean[clean["cluster"].isin(selected_clusters)].copy()
    filtered["Cluster"] = filtered["cluster"].apply(lambda c: f"Cluster {c}")
    sel_colors = [PLOTLY_COLORS[c % len(PLOTLY_COLORS)] for c in selected_clusters]

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Row 1: Cluster Sizes ──────────────────────────────────────────────
    col_a, col_b = st.columns(2)

    with col_a:
        counts = filtered["cluster"].value_counts().reset_index()
        counts.columns = ["cluster", "count"]
        counts["label"] = counts["cluster"].apply(lambda c: f"Cluster {c}")
        counts = counts.sort_values("cluster")
        fig_bar = px.bar(
            counts, x="label", y="count",
            color="label",
            color_discrete_sequence=sel_colors,
            title="Cluster Sizes — Customer Count",
            labels={"label": "Cluster", "count": "Customers"},
            text="count",
        )
        fig_bar.update_traces(
            texttemplate="%{text:,}",
            textposition="outside",
            textfont=dict(color="#e8eef5", size=13),
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Customers: <b>%{y:,}</b><br>"
                "Share: <b>%{customdata:.1%}</b>"
                "<extra></extra>"
            ),
            customdata=counts["count"] / counts["count"].sum(),
        )
        style_plotly_fig(fig_bar)
        fig_bar.update_layout(showlegend=False, title_font_size=14)
        st.plotly_chart(fig_bar, width='stretch')

    with col_b:
        fig_pie = px.pie(
            counts, values="count", names="label",
            color_discrete_sequence=sel_colors,
            title="Cluster Share (%)",
            hole=0.52,
        )
        fig_pie.update_traces(
            textinfo="percent+label",
            hovertemplate=(
                "<b>%{label}</b><br>"
                "Customers: <b>%{value:,}</b><br>"
                "Share: <b>%{percent}</b>"
                "<extra></extra>"
            ),
            textfont=dict(size=12, color="#e8eef5"),
        )
        style_plotly_fig(fig_pie)
        fig_pie.update_layout(title_font_size=14)
        st.plotly_chart(fig_pie, width='stretch')

    # ── Row 2: Income & Spending Distribution ─────────────────────────────
    chart_type = st.radio(
        "Chart style for distributions",
        ["Violin", "Box"],
        horizontal=True,
        key="dist_chart_type",
    )

    income_col = next((c for c in clean.columns if "income" in c.lower()), None)
    spend_col = next((c for c in clean.columns if "spending" in c.lower() or "spend" in c.lower()), None)

    col_c, col_d = st.columns(2)

    with col_c:
        if income_col:
            if chart_type == "Violin":
                fig_inc = px.violin(
                    filtered, x="Cluster", y=income_col,
                    color="Cluster", color_discrete_sequence=sel_colors,
                    box=True, points="outliers",
                    title=f"Income Distribution by Cluster",
                    labels={income_col: "Annual Income ($)", "Cluster": ""},
                    hover_data={income_col: ":.0f"},
                )
            else:
                fig_inc = px.box(
                    filtered, x="Cluster", y=income_col,
                    color="Cluster", color_discrete_sequence=sel_colors,
                    title=f"Income Distribution by Cluster",
                    labels={income_col: "Annual Income ($)", "Cluster": ""},
                    points="outliers",
                )
            fig_inc.update_traces(
                hovertemplate=(
                    "<b>%{x}</b><br>"
                    f"{income_col}: <b>$%{{y:,.0f}}</b>"
                    "<extra></extra>"
                )
            )
            style_plotly_fig(fig_inc)
            fig_inc.update_layout(showlegend=False, title_font_size=14)
            st.plotly_chart(fig_inc, width='stretch')
        else:
            st.info("Income column not found.")

    with col_d:
        if spend_col:
            if chart_type == "Violin":
                fig_sp = px.violin(
                    filtered, x="Cluster", y=spend_col,
                    color="Cluster", color_discrete_sequence=sel_colors,
                    box=True, points="outliers",
                    title=f"Spending Distribution by Cluster",
                    labels={spend_col: "Total Spending ($)", "Cluster": ""},
                    hover_data={spend_col: ":.0f"},
                )
            else:
                fig_sp = px.box(
                    filtered, x="Cluster", y=spend_col,
                    color="Cluster", color_discrete_sequence=sel_colors,
                    title=f"Spending Distribution by Cluster",
                    labels={spend_col: "Total Spending ($)", "Cluster": ""},
                    points="outliers",
                )
            fig_sp.update_traces(
                hovertemplate=(
                    "<b>%{x}</b><br>"
                    f"{spend_col}: <b>$%{{y:,.0f}}</b>"
                    "<extra></extra>"
                )
            )
            style_plotly_fig(fig_sp)
            fig_sp.update_layout(showlegend=False, title_font_size=14)
            st.plotly_chart(fig_sp, width='stretch')
        else:
            st.info("Spending column not found.")

    # ── Row 3: Cluster Radar ───────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        "<div style='color:#9aa6b2;font-size:0.82rem;margin-bottom:4px;'>"
        "Select features for the radar chart</div>",
        unsafe_allow_html=True,
    )
    numeric_cols = [c for c in clean.select_dtypes(include="number").columns if c != "cluster"]
    default_radar = [c for c in ["Income", "Total_Spending", "Recency", "Age", "Children",
                                  "Wines", "Meat", "Gold"] if c in numeric_cols][:6]
    radar_features = st.multiselect(
        "Radar features",
        options=numeric_cols,
        default=default_radar,
        key="radar_features",
        label_visibility="collapsed",
    )

    if len(radar_features) >= 3:
        profile_means = filtered.groupby("cluster")[radar_features].mean()

        # Normalise 0-1 per feature for fair radar
        mins = profile_means.min()
        maxs = profile_means.max()
        diffs = (maxs - mins).replace(0, 1)
        normalised = (profile_means - mins) / diffs

        fig_radar = go.Figure()
        for i, c in enumerate(selected_clusters):
            if c not in normalised.index:
                continue
            vals = normalised.loc[c].tolist()
            raw_vals = profile_means.loc[c].tolist()
            vals += vals[:1]
            raw_vals_display = raw_vals + raw_vals[:1]
            features_loop = radar_features + [radar_features[0]]
            color = PLOTLY_COLORS[c % len(PLOTLY_COLORS)]
            r_int = int(color[1:3], 16)
            g_int = int(color[3:5], 16)
            b_int = int(color[5:7], 16)
            fig_radar.add_trace(go.Scatterpolar(
                r=vals,
                theta=features_loop,
                fill="toself",
                name=f"Cluster {c}",
                line=dict(color=color, width=2),
                fillcolor=f"rgba({r_int},{g_int},{b_int},0.15)",
                hovertemplate=(
                    "<b>Cluster " + str(c) + "</b><br>"
                    "%{theta}: <b>%{customdata:.2f}</b> (normalised: %{r:.2f})"
                    "<extra></extra>"
                ),
                customdata=raw_vals_display,
            ))

        fig_radar.update_layout(
            **PLOTLY_LAYOUT,
            polar=dict(
                bgcolor="rgba(27,34,48,0.9)",
                radialaxis=dict(
                    visible=True,
                    range=[0, 1],
                    tickfont=dict(color="#9aa6b2", size=9),
                    gridcolor="#2a323f",
                    linecolor="#2a323f",
                ),
                angularaxis=dict(
                    tickfont=dict(color="#e8eef5", size=11),
                    gridcolor="#2a323f",
                    linecolor="#2a323f",
                ),
            ),
            title=dict(
                text="Cluster Radar — Normalised Feature Profiles",
                font=dict(color="#e8eef5", size=15),
            ),
            legend=dict(
                font=dict(color="#e8eef5"),
                bgcolor="rgba(0,0,0,0)",
            ),
            height=520,
        )
        st.plotly_chart(fig_radar, width='stretch')
    else:
        st.info("Select at least 3 features for the radar chart.")

    # ── Row 4: Summary stats table ─────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### Cluster Summary Statistics")
    summary_cols = [c for c in ["Income", "Total_Spending", "Age", "Recency",
                                  "Children", "Wines", "Meat"] if c in clean.columns]
    if summary_cols:
        summary = filtered.groupby("Cluster")[summary_cols].agg(["mean", "median", "std"]).round(2)
        summary.columns = [f"{col}_{stat}" for col, stat in summary.columns]
        st.dataframe(summary, width='stretch')


# ===========================================================================
# PAGE 7 — Business Insights
# ===========================================================================
def page_insights():
    section_header("Business Insights", "Cluster profiles, recommendations & model explainability", "💡")
    clean = load_clean_data()
    sup_report = load_supervised_report()
    clu_report = load_clustering_report()

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "👥 Segment Profiles",
        "📈 Customer Analytics",
        "🏆 Model Leaderboard",
        "📊 Confusion Matrix",
        "🔑 Feature Importance",
    ])

    with tab1:
        from src.constants import PREDICTION_SCHEMA_FILE
        from src.utils import read_yaml
        schema = read_yaml(PREDICTION_SCHEMA_FILE)
        profiles = schema.get("cluster_profiles", {})

        for cluster_id, info in profiles.items():
            cluster_data = clean[clean["cluster"] == int(cluster_id)]
            if cluster_data.empty:
                continue
            st.markdown(
                f"""
                <div class='custom-card'>
                    <h3 style='color:#00d2ff;margin-top:0;'>Cluster {cluster_id} — {info['name']}</h3>
                    <p style='color:#9aa6b2;font-size:0.9rem;'>{info['description']}</p>
                    <div style='color:#e8eef5;'>
                        <b>Size:</b> {len(cluster_data):,} customers ({len(cluster_data)/len(clean):.1%})
                        • <b>Avg Income:</b> ${cluster_data['Income'].mean():,.0f}
                        • <b>Avg Spending:</b> ${cluster_data['Total_Spending'].mean():,.0f}
                        • <b>Avg Age:</b> {cluster_data['Age'].mean():.0f}
                    </div>
                    <div style='margin-top:14px;color:#e8eef5;'><b>Recommendations:</b></div>
                    <ul style='color:#e8eef5;'>
                        {''.join(f'<li>{r}</li>' for r in info['recommendations'])}
                    </ul>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # ── Tab 2: Customer Analytics ──────────────────────────────────────────
    with tab2:
        _render_customer_analytics(clean)

    with tab3:
        if sup_report:
            results = sup_report.get("all_results", [])
            df = pd.DataFrame(results)
            best_mdl = sup_report.get('best_model', 'N/A')
            st.markdown(
                f"<h4 style='color:#00d2ff !important;margin-bottom:16px;'>"
                f"<span style='font-size:1.3em;margin-right:8px;'>🏆</span> Best Model: "
                f"<span style='background:rgba(0,210,255,0.15);color:#00d2ff;padding:4px 10px;"
                f"border-radius:6px;font-family:monospace;font-size:0.95em;'>{best_mdl}</span></h4>",
                unsafe_allow_html=True
            )
            cols = st.columns(4)
            best_metrics = sup_report.get("best_metrics", {})
            with cols[0]:
                metric_card("Accuracy", f"{best_metrics.get('accuracy', 0):.4f}", color="cyan")
            with cols[1]:
                metric_card("F1 Score", f"{best_metrics.get('f1', 0):.4f}", color="purple")
            with cols[2]:
                metric_card("Precision", f"{best_metrics.get('precision', 0):.4f}", color="green")
            with cols[3]:
                metric_card("ROC AUC", f"{best_metrics.get('roc_auc', 0):.4f}" if best_metrics.get("roc_auc") else "—", color="orange")

            st.markdown("#### All Models")
            display_cols = ["name", "accuracy", "precision", "recall", "f1", "cv_mean_accuracy", "cv_std_accuracy", "roc_auc"]
            st.dataframe(df[display_cols].style.format({
                "accuracy": "{:.4f}", "precision": "{:.4f}", "recall": "{:.4f}",
                "f1": "{:.4f}", "cv_mean_accuracy": "{:.4f}",
                "cv_std_accuracy": "{:.4f}",
                "roc_auc": "{:.4f}",
            }, na_rep="—"), width='stretch')

            fig = px.bar(
                df, x="accuracy", y="name", orientation="h",
                color="accuracy", color_continuous_scale="Viridis",
                title="Model Accuracy Comparison",
            )
            style_plotly_fig(fig)
            st.plotly_chart(fig, width='stretch')
        else:
            st.warning("Supervised report not found. Run `python training.py` first.")

    with tab4:
        if sup_report:
            results = sup_report.get("all_results", [])
            best_name = sup_report.get("best_model")
            model_names = [r["name"] for r in results if r.get("confusion_matrix")]
            if not model_names:
                st.info("No confusion matrix data found in report.")
            else:
                default_idx = model_names.index(best_name) if best_name in model_names else 0
                selected_model = st.selectbox(
                    "Select model", model_names, index=default_idx,
                    key="cm_model_select",
                )
                selected_result = next((r for r in results if r["name"] == selected_model), None)
                if selected_result and selected_result.get("confusion_matrix"):
                    cm = selected_result["confusion_matrix"]
                    labels = sorted(clean["cluster"].unique().tolist())
                    label_strs = [str(l) for l in labels]
                    if len(cm) != len(labels):
                        labels = list(range(len(cm)))
                        label_strs = [str(l) for l in labels]
                    # Create confusion matrix with smart text color
                    fig = px.imshow(
                        cm,
                        x=[f"Pred {l}" for l in label_strs],
                        y=[f"Actual {l}" for l in label_strs],
                        color_continuous_scale="Blues",
                        text_auto="d",
                        title=f"Confusion Matrix — {selected_model}",
                        labels=dict(color="Count"),
                    )
                    fig.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=True)
                    
                    # Smart text coloring: dark text on light cells, white on dark cells
                    cm_array = np.array(cm)
                    cm_max = cm_array.max()
                    text_colors = []
                    for i in range(len(cm_array)):
                        row_colors = []
                        for j in range(len(cm_array[i])):
                            # Use white text for values > 50% of max, dark text otherwise
                            if cm_array[i][j] > cm_max * 0.5:
                                row_colors.append("white")
                            else:
                                row_colors.append("#0e1117")
                        text_colors.append(row_colors)
                    
                    fig.update_traces(
                        textfont=dict(size=16),
                        texttemplate="%{z}",
                    )
                    # Apply color array to annotations
                    for i, row in enumerate(text_colors):
                        for j, color in enumerate(row):
                            fig.add_annotation(
                                x=j, y=i,
                                text=str(cm_array[i][j]),
                                showarrow=False,
                                font=dict(size=16, color=color, family="monospace"),
                            )
                    st.plotly_chart(fig, width='stretch')
                    cr = selected_result.get("classification_report", {})
                    if cr:
                        cr_rows = []
                        for cls_key in label_strs:
                            if cls_key in cr:
                                row = cr[cls_key]
                                cr_rows.append({
                                    "Class": f"Cluster {cls_key}",
                                    "Precision": row.get("precision", 0),
                                    "Recall": row.get("recall", 0),
                                    "F1-Score": row.get("f1-score", 0),
                                    "Support": int(row.get("support", 0)),
                                })
                        if cr_rows:
                            cr_df = pd.DataFrame(cr_rows)
                            st.markdown("#### Per-Class Metrics")
                            st.dataframe(
                                cr_df.style.format({
                                    "Precision": "{:.4f}",
                                    "Recall": "{:.4f}",
                                    "F1-Score": "{:.4f}",
                                }),
                                width='stretch',
                            )
                else:
                    st.info("Confusion matrix not available for this model.")
        else:
            st.warning("Supervised report not found. Run `python training.py` first.")

    with tab5:
        if sup_report:
            results = sup_report.get("all_results", [])
            best_name = sup_report.get("best_model", "")
            feature_names = sup_report.get("feature_names", [])

            # Find models with native feature_importances_ (tree-based, not hist_gb or stacking)
            IMPORTANCE_MODELS = [
                "random_forest", "extra_trees", "gradient_boosting",
                "adaboost", "bagging", "xgboost", "lightgbm", "catboost",
            ]

            from src.utils import load_object

            # Build selector: prefer best if it supports importances
            candidate = best_name if best_name in IMPORTANCE_MODELS else next(
                (m for m in IMPORTANCE_MODELS if (ROOT / "saved_models" / f"{m}.joblib").exists()), None
            )
            available = [m for m in IMPORTANCE_MODELS
                         if (ROOT / "saved_models" / f"{m}.joblib").exists()]

            if not available:
                st.info("No saved tree-based models found.")
            else:
                default_idx = available.index(candidate) if candidate in available else 0
                selected_fi_model = st.selectbox(
                    "Select model for feature importance", available,
                    index=default_idx, key="fi_model_select"
                )
                model_path = ROOT / "saved_models" / f"{selected_fi_model}.joblib"
                try:
                    fi_model = load_object(model_path)
                    importances = None
                    if hasattr(fi_model, "feature_importances_"):
                        importances = fi_model.feature_importances_
                    elif hasattr(fi_model, "estimators_"):
                        # Bagging / voting — average sub-estimator importances
                        try:
                            all_imp = [
                                e.feature_importances_
                                for e in fi_model.estimators_
                                if hasattr(e, "feature_importances_")
                            ]
                            if all_imp:
                                importances = np.mean(all_imp, axis=0)
                        except Exception:
                            pass

                    if importances is not None and len(feature_names) == len(importances):
                        import pandas as _pd
                        imp_df = _pd.DataFrame({
                            "Feature": feature_names,
                            "Importance": importances,
                        }).sort_values("Importance", ascending=False).reset_index(drop=True)

                        top_n = st.slider("Top N features", 5, len(imp_df), min(20, len(imp_df)),
                                          key="fi_top_n")
                        plot_df = imp_df.head(top_n)

                        fig = px.bar(
                            plot_df, x="Importance", y="Feature",
                            orientation="h",
                            color="Importance",
                            color_continuous_scale="Viridis",
                            title=f"Feature Importance — {selected_fi_model}",
                            hover_data={"Importance": ":.4f"},
                        )
                        style_plotly_fig(fig)
                        fig.update_layout(yaxis=dict(autorange="reversed"))
                        st.plotly_chart(fig, width='stretch')

                        st.markdown("#### Importance Table")
                        st.dataframe(
                            imp_df.style.format({"Importance": "{:.6f}"}),
                            width='stretch',
                        )
                    elif importances is not None:
                        st.warning(
                            f"Feature name count ({len(feature_names)}) doesn't match "
                            f"importance count ({len(importances)}). "
                            "Using index labels."
                        )
                        import pandas as _pd
                        imp_df = _pd.DataFrame({
                            "Feature": [f"f{i}" for i in range(len(importances))],
                            "Importance": importances,
                        }).sort_values("Importance", ascending=False).reset_index(drop=True)
                        fig = px.bar(
                            imp_df, x="Importance", y="Feature", orientation="h",
                            color="Importance", color_continuous_scale="Viridis",
                        )
                        style_plotly_fig(fig)
                        st.plotly_chart(fig, width='stretch')
                    else:
                        st.info(
                            f"Model `{selected_fi_model}` does not expose `feature_importances_`. "
                            "Try random_forest or extra_trees."
                        )
                except Exception as exc:
                    st.warning(f"Could not load model `{selected_fi_model}`: {exc}")
        else:
            st.warning("Supervised report not found. Run `python training.py` first.")

    footer()


# ---------------------------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------------------------
NAV_ITEMS = [
    ("🏠", "Home",                "🏠 Home"),
    ("ℹ️", "About Project",       "ℹ️ About Project"),
    ("📊", "Dataset Overview",    "📊 Dataset Overview"),
    ("🔍", "EDA Dashboard",       "🔍 EDA Dashboard"),
    ("🎯", "Cluster Visualization","🎯 Cluster Visualization"),
    ("🤖", "Customer Prediction", "🤖 Customer Prediction"),
    ("💡", "Business Insights",   "💡 Business Insights"),
]


def render_sidebar() -> str:
    # Initialise page state
    if "current_page" not in st.session_state:
        st.session_state.current_page = NAV_ITEMS[0][2]

    with st.sidebar:
        # ── Brand header ─────────────────────────────────────────────────
        st.markdown(
            """
            <div style='padding:24px 16px 12px 16px;'>
                <div style='font-size:1.55rem;font-weight:800;
                            background:linear-gradient(90deg,#00d2ff 0%,#7c4dff 100%);
                            -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                            background-clip:text;line-height:1.2;'>
                    🛍️ Customer<br>Segmentation AI
                </div>
                <div style='color:#4a5568;font-size:0.75rem;margin-top:8px;
                            letter-spacing:0.04em;font-weight:500;'>
                    End-to-end ML system for customer intelligence
                </div>
            </div>
            <div style='height:1px;background:linear-gradient(90deg,
                        rgba(0,210,255,0.4) 0%,rgba(124,77,255,0.3) 60%,transparent 100%);
                        margin:0 16px 16px 16px;'></div>
            """,
            unsafe_allow_html=True,
        )

        # ── Lottie Animation ─────────────────────────────────────────────
        lottie_url = "https://lottie.host/fb5ca4e1-d09d-45f2-a0c8-f0eb7c5f97e5/ZYjhXxXYRz.json"
        lottie_animation = load_lottie_url(lottie_url)
        if lottie_animation:
            st_lottie(
                lottie_animation,
                height=180,
                key="sidebar_animation",
                quality="high",
                speed=1,
            )
        
        st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

        # ── Navigation label ─────────────────────────────────────────────
        st.markdown(
            "<div class='sidebar-section-label'>Navigation</div>",
            unsafe_allow_html=True,
        )

        # ── Nav buttons ───────────────────────────────────────────────────
        st.markdown("<div style='padding:0 10px;'>", unsafe_allow_html=True)
        for icon, label, page_key in NAV_ITEMS:
            is_active = st.session_state.current_page == page_key
            clicked = st.button(
                f"{icon}  {label}",
                key=f"nav_{page_key}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
            )
            if clicked:
                st.session_state.current_page = page_key
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        # ── Divider ────────────────────────────────────────────────────────
        st.markdown(
            "<div style='height:1px;background:rgba(255,255,255,0.06);"
            "margin:16px 16px;'></div>",
            unsafe_allow_html=True,
        )

        # ── System Status ─────────────────────────────────────────────────
        st.markdown(
            "<div class='sidebar-section-label'>System Status</div>",
            unsafe_allow_html=True,
        )
        classifier_ok = BEST_CLASSIFIER_FILE.exists()
        clust_ok = CLUSTERING_REPORT_FILE.exists()
        sup_ok = SUPERVISED_REPORT_FILE.exists()

        def _status(label: str, ok: bool) -> str:
            dot_cls = "ok" if ok else "warn"
            text = label if ok else f"{label} (missing)"
            return (
                f"<div class='status-item'>"
                f"<span class='status-dot {dot_cls}'></span>"
                f"<span>{text}</span>"
                f"</div>"
            )

        st.markdown(
            "<div style='padding:0 10px;'>"
            + _status("Classifier: Ready", classifier_ok)
            + _status("Clustering report", clust_ok)
            + _status("Supervised report", sup_ok)
            + "</div>",
            unsafe_allow_html=True,
        )

        if not classifier_ok:
            st.markdown(
                "<div style='margin:10px 10px 0 10px;padding:10px 12px;"
                "background:rgba(255,171,64,0.1);border:1px solid rgba(255,171,64,0.3);"
                "border-radius:8px;font-size:0.78rem;color:#ffab40;'>"
                "⚠️ Run <code>python training.py</code> to enable predictions."
                "</div>",
                unsafe_allow_html=True,
            )

        # ── Footer ─────────────────────────────────────────────────────────
        st.markdown(
            "<div style='height:1px;background:rgba(255,255,255,0.06);"
            "margin:16px 16px 8px 16px;'></div>"
            "<div style='padding:8px 16px 20px 16px;color:#2d3748;"
            "font-size:0.72rem;letter-spacing:0.04em;'>"
            "v1.0.0 • Master's in Data Science"
            "</div>",
            unsafe_allow_html=True,
        )

    # Style the nav buttons to look like pills/nav items
    st.markdown(
        """
        <style>
        /* ── Inactive nav buttons ── */
        section[data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="secondary"] {
            background: transparent !important;
            border: 1px solid transparent !important;
            border-radius: 10px !important;
            color: #9aa6b2 !important;
            font-size: 0.88rem !important;
            font-weight: 500 !important;
            text-align: left !important;
            padding: 10px 14px !important;
            margin-bottom: 3px !important;
            box-shadow: none !important;
            transition: all 0.2s ease !important;
        }
        section[data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="secondary"]:hover {
            background: rgba(0,210,255,0.08) !important;
            border-color: rgba(0,210,255,0.25) !important;
            color: #e8eef5 !important;
            transform: translateX(3px) translateY(0) !important;
            box-shadow: none !important;
        }
        /* ── Active nav buttons ── */
        section[data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="primary"] {
            background: linear-gradient(135deg,
                rgba(0,210,255,0.2) 0%, rgba(124,77,255,0.2) 100%) !important;
            border: 1px solid rgba(0,210,255,0.5) !important;
            border-radius: 10px !important;
            color: #ffffff !important;
            font-size: 0.88rem !important;
            font-weight: 700 !important;
            text-align: left !important;
            padding: 10px 14px !important;
            margin-bottom: 3px !important;
            box-shadow: 0 2px 12px rgba(0,210,255,0.15) !important;
            transition: all 0.2s ease !important;
        }
        section[data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="primary"]:hover {
            background: linear-gradient(135deg,
                rgba(0,210,255,0.3) 0%, rgba(124,77,255,0.3) 100%) !important;
            transform: translateX(2px) translateY(0) !important;
            box-shadow: 0 4px 18px rgba(0,210,255,0.22) !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    return st.session_state.current_page


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------
def main():
    page = render_sidebar()
    if page.startswith("🏠"):
        page_home()
    elif page.startswith("ℹ️"):
        page_about()
    elif page.startswith("📊"):
        page_dataset()
    elif page.startswith("🔍"):
        page_eda()
    elif page.startswith("🎯"):
        page_clusters()
    elif page.startswith("🤖"):
        page_predict()
    elif page.startswith("💡"):
        page_insights()


if __name__ == "__main__":
    main()
