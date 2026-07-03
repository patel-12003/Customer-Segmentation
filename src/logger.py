"""
Centralised logging configuration.

Reads ``logging.yaml`` if present, otherwise falls back to a sensible
default. Every module should call ``logging.getLogger(__name__)``;
the project-wide configuration is applied here.
"""

import logging
import logging.config
import os
from pathlib import Path
from typing import Optional

import yaml

from src.constants import (
    ARTIFACTS_ROOT,
    LOGS_DIR,
    LOGS_FILE_NAME,
    LOGGING_CONFIG_FILE,
)


_PROJECT_LOGGER_NAME = "customer_segmentation"


def _ensure_logs_dir() -> Path:
    """Make sure the logs directory exists."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    return LOGS_DIR


def _default_logging_dict(log_file: Path) -> dict:
    """Sensible default logging configuration used when no YAML present."""
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "detailed": {
                "format": (
                    "[%(asctime)s] [%(levelname)s] [%(name)s] "
                    "[%(filename)s:%(lineno)d] %(message)s"
                ),
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "standard",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "DEBUG",
                "formatter": "detailed",
                "filename": str(log_file),
                "maxBytes": 10 * 1024 * 1024,
                "backupCount": 5,
                "encoding": "utf-8",
            },
        },
        "loggers": {
            _PROJECT_LOGGER_NAME: {
                "level": "DEBUG",
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "root": {
                "level": "WARNING",
                "handlers": ["console"],
            },
        },
    }


def configure_logging(
    config_path: Optional[Path] = None,
    log_file: Optional[Path] = None,
) -> logging.Logger:
    """Configure project-wide logging.

    Args:
        config_path: Optional path to ``logging.yaml``. If absent, the
            project-level default location is used.
        log_file: Optional override for the log file path.

    Returns:
        The configured project logger.
    """
    _ensure_logs_dir()
    if log_file is None:
        log_file = LOGS_DIR / LOGS_FILE_NAME

    cfg_path = config_path or LOGGING_CONFIG_FILE
    try:
        if cfg_path.exists():
            with open(cfg_path, "r", encoding="utf-8") as fh:
                cfg = yaml.safe_load(fh)
            # Patch dynamic log file path
            file_handler = (
                cfg.get("handlers", {}).get("file", {})
            )
            if file_handler:
                file_handler["filename"] = str(log_file)
            logging.config.dictConfig(cfg)
        else:
            logging.config.dictConfig(_default_logging_dict(log_file))
    except Exception:  # pragma: no cover - defensive
        logging.basicConfig(level=logging.INFO)
        logging.warning("Falling back to basicConfig due to logging config error.")

    return logging.getLogger(_PROJECT_LOGGER_NAME)


def get_logger(name: str) -> logging.Logger:
    """Return a child logger under the project's main logger.

    Args:
        name: Typically ``__name__`` of the calling module.

    Returns:
        A configured ``logging.Logger`` instance.
    """
    # Make sure the root project logger exists / is configured
    if not logging.getLogger(_PROJECT_LOGGER_NAME).handlers:
        configure_logging()
    if name == _PROJECT_LOGGER_NAME or name.startswith(_PROJECT_LOGGER_NAME + "."):
        return logging.getLogger(name)
    return logging.getLogger(f"{_PROJECT_LOGGER_NAME}.{name}")
