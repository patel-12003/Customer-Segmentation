"""
Data Validation component.

Validates the ingested raw dataframe against ``schema.yaml``:
* required columns present
* dtypes match
* null ratio within threshold
* duplicate ratio within threshold
* categorical columns only contain allowed values
* numeric columns within min/max bounds
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

from src.config_manager import ConfigurationManager
from src.constants import SCHEMA_FILE
from src.exception import DataValidationError
from src.logger import get_logger
from src.utils import ensure_dir, read_yaml, write_json

logger = get_logger(__name__)


@dataclass
class ValidationReport:
    """Structured validation report."""
    passed: bool
    total_checks: int
    failed_checks: int
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "passed": self.passed,
            "total_checks": self.total_checks,
            "failed_checks": self.failed_checks,
            "errors": self.errors,
            "warnings": self.warnings,
            "metrics": self.metrics,
            "timestamp": self.timestamp,
        }


class DataValidation:
    """Validate raw dataframe against the schema."""

    def __init__(self, config_manager: ConfigurationManager) -> None:
        self.config = config_manager.get_validation_config()
        self.schema = config_manager.get_schema()
        if not self.schema:
            self.schema = read_yaml(SCHEMA_FILE)
        self.report_path = Path(self.config.report_path)
        self.validated_path = Path(self.config.validated_data_path)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def initiate_validation(self, df: pd.DataFrame) -> ValidationReport:
        """Run all validation checks on ``df``.

        Args:
            df: Raw ingested dataframe.

        Returns:
            A :class:`ValidationReport` describing the outcome.
        """
        logger.info("Starting data validation ...")
        report = ValidationReport(passed=True, total_checks=0, failed_checks=0)

        self._check_min_rows(df, report)
        self._check_required_columns(df, report)
        self._check_nulls(df, report)
        self._check_duplicates(df, report)
        self._check_dtypes(df, report)
        self._check_categorical_values(df, report)
        self._check_numeric_bounds(df, report)
        self._compute_metrics(df, report)

        report.passed = report.failed_checks == 0
        ensure_dir(self.report_path.parent)
        write_json(report.to_dict(), self.report_path)

        if report.passed:
            ensure_dir(self.validated_path.parent)
            df.to_csv(self.validated_path, index=False)
            logger.info("Validation PASSED — validated data saved to %s", self.validated_path)
        else:
            logger.warning(
                "Validation FAILED with %d errors. Validated data will not be persisted.",
                len(report.errors),
            )

        logger.info(
            "Validation summary: %d checks, %d failed, %d warnings",
            report.total_checks,
            report.failed_checks,
            len(report.warnings),
        )
        return report

    # ------------------------------------------------------------------
    # Individual checks
    # ------------------------------------------------------------------
    def _check_min_rows(self, df: pd.DataFrame, report: ValidationReport) -> None:
        min_rows = self.schema.get("dataset", {}).get("min_rows", 100)
        report.total_checks += 1
        if len(df) < min_rows:
            report.errors.append(
                f"Row count {len(df)} below minimum {min_rows}."
            )
            report.failed_checks += 1

    def _check_required_columns(self, df: pd.DataFrame, report: ValidationReport) -> None:
        cols = self.schema.get("columns", [])
        required = [c["name"] for c in cols if not c.get("drop", False)]
        report.total_checks += 1
        missing = [c for c in required if c not in df.columns]
        if missing:
            report.errors.append(f"Missing required columns: {missing}")
            report.failed_checks += 1

    def _check_nulls(self, df: pd.DataFrame, report: ValidationReport) -> None:
        report.total_checks += 1
        null_ratios = df.isnull().mean()
        offenders = null_ratios[null_ratios > self.config.allowed_null_ratio]
        if not offenders.empty:
            report.errors.append(
                f"Null ratio exceeded threshold for columns: {offenders.to_dict()}"
            )
            report.failed_checks += 1
        else:
            report.metrics["null_ratios"] = null_ratios[null_ratios > 0].to_dict()

    def _check_duplicates(self, df: pd.DataFrame, report: ValidationReport) -> None:
        report.total_checks += 1
        dup_ratio = df.duplicated().mean()
        report.metrics["duplicate_ratio"] = float(dup_ratio)
        if dup_ratio > self.config.duplicate_threshold:
            report.errors.append(
                f"Duplicate ratio {dup_ratio:.3f} exceeds threshold "
                f"{self.config.duplicate_threshold}."
            )
            report.failed_checks += 1

    def _check_dtypes(self, df: pd.DataFrame, report: ValidationReport) -> None:
        for col_def in self.schema.get("columns", []):
            name = col_def["name"]
            if name not in df.columns:
                continue
            report.total_checks += 1
            expected = col_def.get("dtype")
            if not expected:
                continue
            actual = str(df[name].dtype)
            if not self._dtype_match(actual, expected):
                report.errors.append(
                    f"Column '{name}' dtype '{actual}' != expected '{expected}'."
                )
                report.failed_checks += 1

    def _check_categorical_values(self, df: pd.DataFrame, report: ValidationReport) -> None:
        for col_def in self.schema.get("columns", []):
            name = col_def["name"]
            allowed = col_def.get("allowed")
            if not allowed or name not in df.columns:
                continue
            report.total_checks += 1
            unique = set(df[name].dropna().unique())
            extra = unique - set(allowed)
            if extra:
                report.warnings.append(
                    f"Column '{name}' contains unexpected values: {extra}"
                )

    def _check_numeric_bounds(self, df: pd.DataFrame, report: ValidationReport) -> None:
        for col_def in self.schema.get("columns", []):
            name = col_def["name"]
            if name not in df.columns:
                continue
            mn = col_def.get("min")
            mx = col_def.get("max")
            if mn is None and mx is None:
                continue
            report.total_checks += 1
            try:
                if mn is not None and (df[name].min() < mn):
                    report.errors.append(
                        f"Column '{name}' has values below min {mn}."
                    )
                    report.failed_checks += 1
                if mx is not None and (df[name].max() > mx):
                    report.errors.append(
                        f"Column '{name}' has values above max {mx}."
                    )
                    report.failed_checks += 1
            except Exception as exc:  # pragma: no cover
                report.warnings.append(
                    f"Could not check bounds for '{name}': {exc}"
                )

    def _compute_metrics(self, df: pd.DataFrame, report: ValidationReport) -> None:
        report.metrics["n_rows"] = int(len(df))
        report.metrics["n_columns"] = int(df.shape[1])
        report.metrics["memory_mb"] = float(
            df.memory_usage(deep=True).sum() / 1024 ** 2
        )

    # ------------------------------------------------------------------
    @staticmethod
    def _dtype_match(actual: str, expected: str) -> bool:
        expected = expected.lower()
        if expected == "int":
            return pd.api.types.is_integer_dtype(actual)
        if expected == "float":
            return pd.api.types.is_float_dtype(actual) or pd.api.types.is_integer_dtype(actual)
        if expected in ("object", "str"):
            return pd.api.types.is_object_dtype(actual)
        return True
