"""
Custom exception hierarchy for the Customer Categorizer project.

Provides a single ``CustomerSegmentationException`` that captures rich
context (file name, line number, custom error message) so that the
caller can quickly pinpoint the root cause of any failure.
"""

import sys
import traceback
from typing import Any, Optional


class CustomerSegmentationException(Exception):
    """Base exception for all project-specific errors.

    Attributes:
        message: Human-readable error description.
        error_details: Original exception raised by the interpreter.
    """

    def __init__(
        self,
        message: str = "A Customer Categorizer error occurred.",
        error_details: Optional[Any] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.error_details = error_details

        # Capture caller info
        exc_type, exc_value, exc_tb = sys.exc_info()
        self._exc_type = exc_type
        self._exc_value = exc_value
        self._exc_tb = exc_tb

    def _extract_error_info(self) -> str:
        """Build a formatted string with file name and line number."""
        try:
            tb = traceback.extract_tb(self._exc_tb)
            if tb:
                last = tb[-1]
                return (
                    f"Error occurred in script: [{last.filename}] "
                    f"line number: [{last.lineno}] "
                    f"error message: [{str(self._exc_value or self.message)}]"
                )
        except Exception:  # pragma: no cover - defensive
            pass
        return f"Error message: [{self.message}]"

    def __str__(self) -> str:
        return self._extract_error_info()

    def to_dict(self) -> dict:
        """Return a serialisable representation for logging/JSON APIs."""
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "details": str(self.error_details) if self.error_details else None,
            "traceback": traceback.format_exc(),
        }


class DataIngestionError(CustomerSegmentationException):
    """Raised when data ingestion fails."""


class DataValidationError(CustomerSegmentationException):
    """Raised when dataset fails schema or business validation."""


class DataTransformationError(CustomerSegmentationException):
    """Raised when feature transformation fails."""


class FeatureEngineeringError(CustomerSegmentationException):
    """Raised when feature engineering fails."""


class FeatureSelectionError(CustomerSegmentationException):
    """Raised when feature selection fails."""


class ClusteringError(CustomerSegmentationException):
    """Raised when clustering training fails."""


class SupervisedModelError(CustomerSegmentationException):
    """Raised when supervised model training fails."""


class AutoGluonTrainerError(CustomerSegmentationException):
    """Raised when AutoGluon training fails."""


class ExplainabilityError(CustomerSegmentationException):
    """Raised when SHAP/LIME explanation generation fails."""


class PredictionError(CustomerSegmentationException):
    """Raised when the prediction pipeline fails."""


class ConfigError(CustomerSegmentationException):
    """Raised when configuration files are missing or invalid."""
