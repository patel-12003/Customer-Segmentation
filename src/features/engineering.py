"""
Feature Engineering component.

Derives business-meaningful features from the raw marketing_campaign
data so that downstream clustering and supervised models operate on
the same feature space as the provided ``clustered_data.csv``.

Derived features
----------------
* ``Age`` — derived from ``Year_Birth``
* ``Children`` — ``Kidhome + Teenhome``
* ``Parental_Status`` — 1 if ``Children > 0`` else 0
* ``Total_Spending`` — sum of all ``Mnt*`` columns
* ``Total_Purchases`` — web + catalog + store purchases
* ``Total_Promo`` — sum of accepted campaigns
* ``Days_as_Customer`` — days since ``Dt_Customer``
* ``Avg_Order_Value`` — ``Total_Spending / Total_Purchases``
* ``Spending_Per_Child`` — ``Total_Spending / (Children + 1)``
* ``Income_Per_Family_Member`` — ``Income / (Children + 1)``
* ``Education_Encoded`` — ordinal encoding
* ``Marital_Encoded`` — binary partner indicator
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd

from src.config_manager import ConfigurationManager
from src.exception import FeatureEngineeringError
from src.logger import get_logger
from src.utils import ensure_dir, save_object

logger = get_logger(__name__)


EDUCATION_MAP = {
    "Basic": 0,
    "2n Cycle": 1,
    "Graduation": 2,
    "Master": 3,
    "PhD": 4,
}

PARTNER_STATUSES = {"Together", "Married"}


@dataclass
class FeatureEngineeringArtifact:
    engineered_df: pd.DataFrame
    feature_store_path: Path
    engineered_path: Path
    feature_names: List[str]


class FeatureEngineer:
    """Create derived features from the raw marketing dataset."""

    def __init__(self, config_manager: ConfigurationManager) -> None:
        self.config = config_manager.get_feature_engineering_config()
        self.engineered_path = Path(self.config.engineered_data_path)
        self.feature_store_path = Path(self.config.feature_store_path)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def initiate_feature_engineering(
        self, df: pd.DataFrame
    ) -> FeatureEngineeringArtifact:
        """Build engineered features from raw dataframe.

        Args:
            df: Validated raw dataframe (must contain marketing_campaign columns).

        Returns:
            :class:`FeatureEngineeringArtifact` with engineered dataframe
            and the persisted feature store.
        """
        logger.info("Starting feature engineering ...")
        try:
            engineered = df.copy()

            engineered = self._engineer_age(engineered)
            engineered = self._engineer_family(engineered)
            engineered = self._engineer_spending(engineered)
            engineered = self._engineer_purchases(engineered)
            engineered = self._engineer_promo(engineered)
            engineered = self._engineer_customer_tenure(engineered)
            engineered = self._engineer_ratios(engineered)
            engineered = self._encode_categorical(engineered)

            engineered = engineered.replace([np.inf, -np.inf], np.nan)
            engineered = engineered.fillna(0)

            feature_names = list(engineered.columns)
            self._persist(engineered, feature_names)

            logger.info(
                "Feature engineering complete — shape=%s, features=%d",
                engineered.shape,
                len(feature_names),
            )
            return FeatureEngineeringArtifact(
                engineered_df=engineered,
                feature_store_path=self.feature_store_path,
                engineered_path=self.engineered_path,
                feature_names=feature_names,
            )
        except Exception as exc:
            raise FeatureEngineeringError(
                "Feature engineering failed.", exc
            ) from exc

    # ------------------------------------------------------------------
    # Individual feature builders
    # ------------------------------------------------------------------
    @staticmethod
    def _engineer_age(df: pd.DataFrame) -> pd.DataFrame:
        if "Year_Birth" in df.columns:
            df["Age"] = datetime.now().year - df["Year_Birth"]
            df.loc[df["Age"] > 100, "Age"] = np.nan
            df["Age"] = df["Age"].fillna(df["Age"].median()).astype(int)
            df.loc[df["Age"] < 18, "Age"] = 18
        return df

    @staticmethod
    def _engineer_family(df: pd.DataFrame) -> pd.DataFrame:
        kid = df.get("Kidhome", pd.Series(0, index=df.index))
        teen = df.get("Teenhome", pd.Series(0, index=df.index))
        df["Children"] = kid + teen
        df["Parental_Status"] = (df["Children"] > 0).astype(int)
        return df

    @staticmethod
    def _engineer_spending(df: pd.DataFrame) -> pd.DataFrame:
        mnt_cols = [
            "MntWines", "MntFruits", "MntMeatProducts",
            "MntFishProducts", "MntSweetProducts", "MntGoldProds",
        ]
        present = [c for c in mnt_cols if c in df.columns]
        df["Total_Spending"] = df[present].sum(axis=1) if present else 0
        return df

    @staticmethod
    def _engineer_purchases(df: pd.DataFrame) -> pd.DataFrame:
        cols = ["NumWebPurchases", "NumCatalogPurchases", "NumStorePurchases"]
        present = [c for c in cols if c in df.columns]
        df["Total_Purchases"] = df[present].sum(axis=1) if present else 0
        return df

    @staticmethod
    def _engineer_promo(df: pd.DataFrame) -> pd.DataFrame:
        cmp_cols = [
            "AcceptedCmp1", "AcceptedCmp2", "AcceptedCmp3",
            "AcceptedCmp4", "AcceptedCmp5",
        ]
        present = [c for c in cmp_cols if c in df.columns]
        df["Total_Promo"] = df[present].sum(axis=1) if present else 0
        return df

    @staticmethod
    def _engineer_customer_tenure(df: pd.DataFrame) -> pd.DataFrame:
        if "Dt_Customer" in df.columns:
            try:
                dt = pd.to_datetime(df["Dt_Customer"], errors="coerce")
                df["Days_as_Customer"] = (
                    pd.Timestamp(datetime.now()) - dt
                ).dt.days
                df["Days_as_Customer"] = df["Days_as_Customer"].fillna(
                    df["Days_as_Customer"].median()
                )
            except Exception as exc:
                logger.warning("Could not parse Dt_Customer: %s", exc)
                df["Days_as_Customer"] = 0
        else:
            df["Days_as_Customer"] = 0
        return df

    @staticmethod
    def _engineer_ratios(df: pd.DataFrame) -> pd.DataFrame:
        df["Avg_Order_Value"] = np.where(
            df["Total_Purchases"] > 0,
            df["Total_Spending"] / df["Total_Purchases"],
            0,
        )
        df["Spending_Per_Child"] = df["Total_Spending"] / (df["Children"] + 1)
        df["Income_Per_Family_Member"] = df.get(
            "Income", pd.Series(0, index=df.index)
        ) / (df["Children"] + 1)
        return df

    @staticmethod
    def _encode_categorical(df: pd.DataFrame) -> pd.DataFrame:
        if "Education" in df.columns:
            df["Education_Encoded"] = df["Education"].map(EDUCATION_MAP).fillna(2).astype(int)
        if "Marital_Status" in df.columns:
            df["Marital_Encoded"] = df["Marital_Status"].apply(
                lambda s: 1 if s in PARTNER_STATUSES else 0
            )
        return df

    # ------------------------------------------------------------------
    def _persist(self, df: pd.DataFrame, feature_names: List[str]) -> None:
        ensure_dir(self.engineered_path.parent)
        df.to_csv(self.engineered_path, index=False)
        ensure_dir(self.feature_store_path.parent)
        save_object(
            {"feature_names": feature_names, "engineered_shape": df.shape},
            self.feature_store_path,
        )
