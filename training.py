#!/usr/bin/env python3
"""
training.py — End-to-end training orchestrator.

Run with:
    python training.py

This script executes the full pipeline:
1. Data ingestion
2. Data validation
3. Data transformation
4. Feature engineering
5. Feature selection
6. Clustering (10 algorithms)
7. Supervised training (11 models)
8. AutoGluon (optional)
9. Explainability (SHAP + LIME)

All artifacts are written under ``artifacts/`` and ``saved_models/``.
After training completes you can launch the Streamlit app with:
    streamlit run app.py
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure project root is importable
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config_manager import ConfigurationManager  # noqa: E402
from src.logger import get_logger  # noqa: E402
from src.pipeline.train_pipeline import TrainPipeline  # noqa: E402

logger = get_logger("training")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Customer Categorizer — end-to-end training pipeline"
    )
    parser.add_argument(
        "--skip-autogluon",
        action="store_true",
        help="Skip the AutoGluon AutoML step (faster).",
    )
    parser.add_argument(
        "--skip-explainability",
        action="store_true",
        help="Skip SHAP/LIME explainability steps.",
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="Path to config.yaml",
    )
    parser.add_argument(
        "--params",
        type=str,
        default="params.yaml",
        help="Path to params.yaml",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        config_manager = ConfigurationManager(
            config_path=args.config, params_path=args.params
        )
        pipeline = TrainPipeline(config_manager=config_manager)
        result = pipeline.run(
            run_autogluon=not args.skip_autogluon,
            run_explainability=not args.skip_explainability,
        )
        if result.success:
            print("\n" + "=" * 70)
            print("✅ Training completed successfully!")
            print(f"   Best clustering model : {result.best_clustering_model}")
            print(f"   Best classifier       : {result.best_supervised_model}")
            print(f"   Number of clusters    : {result.n_clusters}")
            print(f"   Best accuracy         : {result.best_accuracy:.4f}")
            print("=" * 70)
            print("\n🚀 Launch the dashboard with:")
            print("   streamlit run app.py\n")
            return 0
        else:
            print("❌ Training did not complete successfully. Check logs.")
            return 1
    except Exception as exc:
        logger.exception("Training failed: %s", exc)
        print(f"\n❌ Training failed: {exc}")
        print("   See logs/customer_segmentation.log for details.\n")
        return 2


if __name__ == "__main__":
    sys.exit(main())
