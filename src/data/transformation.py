"""
Data Transformation component.

Builds a reusable scikit-learn ``Pipeline`` containing:
* numeric imputer + scaler
* categorical imputer + one-hot encoder
The fitted pipeline is persisted so the same transformation can be
applied at inference time.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.config_manager import ConfigurationManager
from src.exception import DataTransformationError
from src.logger import get_logger
from src.utils import ensure_dir, save_object

logger = get_logger(__name__)


@dataclass
class TransformationArtifact:
    """Container for transformation outputs."""
    transformed_df: pd.DataFrame
    preprocessor: ColumnTransformer
    feature_names: List[str]
    preprocessor_path: Path
    scaler_path: Path
    transformed_path: Path


class DataTransformation:
    """Fit and apply the preprocessing pipeline."""

    def __init__(self, config_manager: ConfigurationManager) -> None:
        self.config = config_manager.get_transformation_config()
        self.transformed_path = Path(self.config.transformed_data_path)
        self.scaler_path = Path(self.config.scaler_path)
        self.preprocessor_path = Path(self.config.preprocessor_path)
        self.numerical_features = list(self.config.numerical_features)
        self.categorical_features = list(self.config.categorical_features)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def initiate_transformation(
        self, df: pd.DataFrame
    ) -> TransformationArtifact:
        """Fit the preprocessor on ``df`` and return transformed data.

        Args:
            df: Validated raw dataframe.

        Returns:
            :class:`TransformationArtifact` with transformed array and
            fitted preprocessor.
        """
        logger.info("Starting data transformation ...")
        try:
            available_num = [
                c for c in self.numerical_features if c in df.columns
            ]
            available_cat = [
                c for c in self.categorical_features if c in df.columns
            ]
            logger.info(
                "Numeric features (%d): %s",
                len(available_num),
                available_num,
            )
            logger.info(
                "Categorical features (%d): %s",
                len(available_cat),
                available_cat,
            )

            preprocessor = self._build_preprocessor(available_num, available_cat)
            transformed_array = preprocessor.fit_transform(df)
            feature_names = self._get_feature_names(preprocessor)

            transformed_df = pd.DataFrame(
                transformed_array,
                columns=feature_names,
                index=df.index,
            )

            # Persist artifacts
            ensure_dir(self.transformed_path.parent)
            transformed_df.to_csv(self.transformed_path, index=False)
            ensure_dir(self.preprocessor_path.parent)
            save_object(preprocessor, self.preprocessor_path)

            # Also save a standalone scaler for inference convenience
            scaler = StandardScaler()
            numeric_df = df[available_num].fillna(df[available_num].median())
            scaler.fit(numeric_df)
            save_object(scaler, self.scaler_path)

            logger.info("Transformed data shape: %s", transformed_df.shape)
            logger.info("Preprocessor saved to %s", self.preprocessor_path)

            return TransformationArtifact(
                transformed_df=transformed_df,
                preprocessor=preprocessor,
                feature_names=feature_names,
                preprocessor_path=self.preprocessor_path,
                scaler_path=self.scaler_path,
                transformed_path=self.transformed_path,
            )
        except Exception as exc:
            raise DataTransformationError(
                "Data transformation failed.", exc
            ) from exc

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _build_preprocessor(
        self, num_cols: List[str], cat_cols: List[str]
    ) -> ColumnTransformer:
        numeric_pipeline = Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
            ]
        )
        categorical_pipeline = Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
            ]
        )
        return ColumnTransformer(
            transformers=[
                ("num", numeric_pipeline, num_cols),
                ("cat", categorical_pipeline, cat_cols),
            ],
            remainder="drop",
            n_jobs=-1,
        )

    @staticmethod
    def _get_feature_names(preprocessor: ColumnTransformer) -> List[str]:
        names: List[str] = []
        for name, transformer, cols in preprocessor.transformers_:
            if transformer == "drop":
                continue
            if hasattr(transformer, "get_feature_names_out"):
                try:
                    out = transformer.get_feature_names_out(cols)
                    names.extend([f"{name}__{c}" for c in out])
                except Exception:
                    names.extend([f"{name}__{c}" for c in cols])
            else:
                names.extend([f"{name}__{c}" for c in cols])
        return names
