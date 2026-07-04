"""Setup script — makes the project pip-installable as a package."""

from setuptools import find_packages, setup

setup(
    name="customer_segmentation",
    version="1.0.0",
    description="End-to-end Customer Categorizer & Intelligent Customer Classification System",
    author="Senior ML Engineering Team",
    author_email="team@example.com",
    license="MIT",
    python_requires=">=3.11",
    packages=find_packages(include=["src", "src.*"]),
    install_requires=[
        "numpy>=1.26",
        "pandas>=2.0",
        "scikit-learn>=1.4",
        "pyyaml>=6.0",
        "matplotlib>=3.8",
        "seaborn>=0.13",
        "plotly>=5.20",
        "streamlit>=1.30",
        "joblib>=1.3",
        "xgboost>=2.0",
        "lightgbm>=4.0",
        "catboost>=1.2",
        "hdbscan>=0.8.30",
        "shap>=0.44",
        "lime>=0.2",
        "optuna>=3.5",
    ],
    classifiers=[
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Intended Audience :: Science/Research",
    ],
)
