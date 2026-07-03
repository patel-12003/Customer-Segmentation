"""Smoke tests for the customer-segmentation pipeline."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.config_manager import ConfigurationManager
from src.constants import CLEAN_DATA_FILE, RAW_DATA_FILE
from src.data.ingestion import DataIngestion
from src.features.engineering import FeatureEngineer
from src.utils import read_yaml


@pytest.fixture(scope="module")
def config_manager():
    return ConfigurationManager()


def test_raw_data_exists():
    assert RAW_DATA_FILE.exists(), "marketing_campaign.csv not found"
    df = pd.read_csv(RAW_DATA_FILE)
    assert len(df) > 1000


def test_clean_data_exists():
    assert CLEAN_DATA_FILE.exists()
    df = pd.read_csv(CLEAN_DATA_FILE)
    assert "cluster" in df.columns


def test_yaml_configs_load(config_manager):
    assert config_manager.get_app_config() is not None
    assert config_manager.get_params() is not None
    assert config_manager.get_schema() is not None


def test_ingestion_runs(config_manager):
    ingestion = DataIngestion(config_manager)
    artifact = ingestion.initiate_ingestion()
    assert artifact.raw_df.shape[0] > 1000
    assert artifact.cleaned_df.shape[0] > 1000


def test_feature_engineering_runs(config_manager):
    engineer = FeatureEngineer(config_manager)
    raw = pd.read_csv(RAW_DATA_FILE)
    artifact = engineer.initiate_feature_engineering(raw)
    assert "Age" in artifact.engineered_df.columns
    assert "Total_Spending" in artifact.engineered_df.columns
    assert "Children" in artifact.engineered_df.columns


def test_prediction_schema_valid():
    schema = read_yaml("prediction_schema.yaml")
    assert "features" in schema
    assert "cluster_profiles" in schema
    assert len(schema["features"]) > 0
