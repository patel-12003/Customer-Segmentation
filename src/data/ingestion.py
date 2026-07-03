"""
Data Ingestion component.

Reads the raw ``marketing_campaign.csv`` and the cleaned
``clustered_data.csv`` from disk, performs light normalisation
(strip whitespace, dedupe header names, type coercion) and writes
intermediate artifacts to ``data/processed/``.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

import pandas as pd

from src.config_manager import ConfigurationManager
from src.exception import DataIngestionError
from src.logger import get_logger
from src.utils import ensure_dir, reduce_memory_usage

logger = get_logger(__name__)


@dataclass
class IngestionArtifact:
    """Container for ingestion outputs."""
    raw_df: pd.DataFrame
    cleaned_df: pd.DataFrame
    raw_path: Path
    cleaned_path: Path
    ingested_path: Path


class DataIngestion:
    """Load raw and cleaned datasets into the project pipeline.

    The class is intentionally small and side-effect-free: it reads
    files, normalises them, persists them to the processed directory
    and returns an :class:`IngestionArtifact`.
    """

    def __init__(self, config_manager: ConfigurationManager) -> None:
        self.config = config_manager.get_ingestion_config()
        self.raw_path = Path(self.config.raw_data_path)
        self.cleaned_path = Path(self.config.cleaned_data_path)
        self.ingested_path = Path(self.config.ingested_data_path)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def initiate_ingestion(self) -> IngestionArtifact:
        """Run the full ingestion step and return the artifact.

        Raises:
            DataIngestionError: If either file cannot be loaded.
        """
        logger.info("Starting data ingestion ...")
        raw_df = self._load_raw()
        cleaned_df = self._load_cleaned()

        raw_df = self._normalise(raw_df, "raw")
        cleaned_df = self._normalise(cleaned_df, "cleaned")

        # Persist the ingested raw view
        ensure_dir(self.ingested_path.parent)
        raw_df.to_csv(self.ingested_path, index=False)
        logger.info("Ingested raw data saved to %s", self.ingested_path)

        artifact = IngestionArtifact(
            raw_df=raw_df,
            cleaned_df=cleaned_df,
            raw_path=self.raw_path,
            cleaned_path=self.cleaned_path,
            ingested_path=self.ingested_path,
        )
        logger.info(
            "Ingestion complete | raw shape=%s | cleaned shape=%s",
            raw_df.shape,
            cleaned_df.shape,
        )
        return artifact

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _load_raw(self) -> pd.DataFrame:
        if not self.raw_path.exists():
            raise DataIngestionError(f"Raw data file not found: {self.raw_path}")
        try:
            # The marketing_campaign file is tab-separated in the wild but
            # the uploaded copy is comma separated — auto-detect.
            sep = self._detect_separator(self.raw_path)
            df = pd.read_csv(self.raw_path, sep=sep)
            logger.info("Raw dataset loaded: %s (separator=%s)", df.shape, sep)
            return df
        except Exception as exc:
            raise DataIngestionError(
                f"Failed to read raw data: {self.raw_path}", exc
            ) from exc

    def _load_cleaned(self) -> pd.DataFrame:
        if not self.cleaned_path.exists():
            raise DataIngestionError(
                f"Cleaned data file not found: {self.cleaned_path}"
            )
        try:
            df = pd.read_csv(self.cleaned_path)
            logger.info("Cleaned dataset loaded: %s", df.shape)
            return df
        except Exception as exc:
            raise DataIngestionError(
                f"Failed to read cleaned data: {self.cleaned_path}", exc
            ) from exc

    @staticmethod
    def _detect_separator(path: Path) -> str:
        """Detect whether a CSV is comma or tab separated."""
        with open(path, "r", encoding="utf-8") as fh:
            first_line = fh.readline()
        if "\t" in first_line and first_line.count("\t") > first_line.count(","):
            return "\t"
        return ","

    @staticmethod
    def _normalise(df: pd.DataFrame, label: str) -> pd.DataFrame:
        """Strip column whitespace, dedupe columns, reduce memory."""
        df.columns = [str(c).strip() for c in df.columns]
        # Drop fully empty columns
        df = df.dropna(axis=1, how="all")
        # Strip whitespace from string cells
        for col in df.select_dtypes(include="object").columns:
            df[col] = df[col].astype(str).str.strip()
        df = reduce_memory_usage(df, verbose=False)
        logger.debug("[%s] normalised to shape %s", label, df.shape)
        return df
