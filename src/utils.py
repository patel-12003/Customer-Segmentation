"""
Reusable utility helpers used throughout the project.

Functions cover:
* YAML loading
* Object (de)serialisation via joblib
* Directory creation
* JSON I/O
* DataFrame sanity checks
* Timing context managers
"""

from __future__ import annotations

import json
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Iterable, Optional, Union

import joblib
import pandas as pd
import yaml

from src.exception import CustomerSegmentationException
from src.logger import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# YAML helpers
# ---------------------------------------------------------------------------
def read_yaml(path: Union[str, Path]) -> Dict[str, Any]:
    """Load a YAML file into a Python dict.

    Args:
        path: Path to the YAML file.

    Returns:
        Parsed YAML as a dictionary.

    Raises:
        CustomerSegmentationException: If the file cannot be read or parsed.
    """
    try:
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"YAML file not found: {path}")
        with open(path, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
        logger.info("YAML loaded from %s with keys: %s", path, list(data.keys()))
        return data
    except Exception as exc:
        logger.exception("Failed to read YAML file: %s", path)
        raise CustomerSegmentationException(
            f"Failed to read YAML file: {path}", exc
        ) from exc


def write_yaml(data: Dict[str, Any], path: Union[str, Path]) -> None:
    """Persist a dictionary to a YAML file.

    Args:
        data: Dictionary to dump.
        path: Destination path.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        yaml.safe_dump(data, fh, sort_keys=False)
    logger.info("YAML written to %s", path)


# ---------------------------------------------------------------------------
# JSON helpers
# ---------------------------------------------------------------------------
def read_json(path: Union[str, Path]) -> Any:
    """Load a JSON file."""
    path = Path(path)
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def write_json(data: Any, path: Union[str, Path], indent: int = 4) -> None:
    """Persist an object as a JSON file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=indent, default=str)
    logger.info("JSON written to %s", path)


# ---------------------------------------------------------------------------
# Object (de)serialisation
# ---------------------------------------------------------------------------
def save_object(obj: Any, path: Union[str, Path]) -> None:
    """Save any Python object using joblib.

    Args:
        obj: Object to persist.
        path: Destination path.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(obj, path)
    logger.info("Object saved to %s", path)


def load_object(path: Union[str, Path]) -> Any:
    """Load an object previously saved with ``save_object``.

    Args:
        path: Path to the saved object.

    Returns:
        The loaded object.
    """
    path = Path(path)
    if not path.exists():
        raise CustomerSegmentationException(f"Object file not found: {path}")
    obj = joblib.load(path)
    logger.info("Object loaded from %s", path)
    return obj


# ---------------------------------------------------------------------------
# Directory helpers
# ---------------------------------------------------------------------------
def ensure_dir(path: Union[str, Path]) -> Path:
    """Create the directory (and parents) if it does not exist."""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def ensure_dirs(paths: Iterable[Union[str, Path]]) -> None:
    """Create multiple directories at once."""
    for p in paths:
        ensure_dir(p)


# ---------------------------------------------------------------------------
# DataFrame helpers
# ---------------------------------------------------------------------------
def check_dataframe(
    df: pd.DataFrame,
    required_columns: Optional[Iterable[str]] = None,
    min_rows: int = 1,
) -> bool:
    """Validate basic DataFrame integrity.

    Args:
        df: DataFrame to check.
        required_columns: Columns that must be present.
        min_rows: Minimum number of rows expected.

    Returns:
        True if all checks pass.

    Raises:
        CustomerSegmentationException: If any check fails.
    """
    if df is None or not isinstance(df, pd.DataFrame):
        raise CustomerSegmentationException("Provided object is not a DataFrame.")
    if len(df) < min_rows:
        raise CustomerSegmentationException(
            f"DataFrame has only {len(df)} rows (min {min_rows} required)."
        )
    if required_columns:
        missing = set(required_columns) - set(df.columns)
        if missing:
            raise CustomerSegmentationException(
                f"DataFrame missing required columns: {missing}"
            )
    return True


def reduce_memory_usage(df: pd.DataFrame, verbose: bool = True) -> pd.DataFrame:
    """Down-cast numeric columns to reduce memory footprint.

    Args:
        df: DataFrame to optimise.
        verbose: If True, log memory reduction.

    Returns:
        Optimised DataFrame.
    """
    start_mem = df.memory_usage(deep=True).sum() / 1024 ** 2
    for col in df.columns:
        col_type = df[col].dtype
        if pd.api.types.is_integer_dtype(col_type):
            df[col] = pd.to_numeric(df[col], downcast="integer")
        elif pd.api.types.is_float_dtype(col_type):
            df[col] = pd.to_numeric(df[col], downcast="float")
    end_mem = df.memory_usage(deep=True).sum() / 1024 ** 2
    if verbose:
        reduction = (start_mem - end_mem) / start_mem * 100
        logger.info(
            "Memory reduced from %.2f MB to %.2f MB (%.1f%% reduction).",
            start_mem,
            end_mem,
            reduction,
        )
    return df


# ---------------------------------------------------------------------------
# Timing
# ---------------------------------------------------------------------------
@contextmanager
def timer(name: str = "operation"):
    """Context manager that logs elapsed time for the wrapped block.

    Args:
        name: Human-readable label for the operation.
    """
    start = time.perf_counter()
    logger.info("⏱️  Starting: %s", name)
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        logger.info("⏱️  Finished: %s in %.2f seconds", name, elapsed)


def get_timestamp(fmt: str = "%Y%m%d_%H%M%S") -> str:
    """Return a filesystem-safe timestamp string."""
    return time.strftime(fmt)
