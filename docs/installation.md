# Installation Guide

## Prerequisites

| Requirement | Minimum | Recommended |
|---|---|---|
| Python | 3.11 | 3.12 |
| RAM | 4 GB | 8 GB |
| Disk | 1 GB | 2 GB (with AutoGluon) |
| OS | Linux / macOS / Windows | Linux / macOS |

## Step 1: Clone & enter the project

```bash
git clone <your-repo-url> customer_segmentation
cd customer_segmentation
```

## Step 2: Create a virtual environment (recommended)

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

### Windows

```powershell
python -m venv venv
venv\Scripts\activate
```

### Using `uv` (faster alternative)

```bash
uv venv
source .venv/bin/activate
```

## Step 3: Install dependencies

### Full install (with AutoGluon)

```bash
pip install -r requirements.txt
```

### Light install (without AutoGluon)

Edit `requirements.txt` and comment out the `autogluon.tabular` line, then:

```bash
pip install -r requirements.txt
```

## Step 4: Verify installation

```bash
python -c "from src.config_manager import ConfigurationManager; print('OK')"
```

You should see `OK` with no errors.

## Step 5: Train models

```bash
python training.py
```

Or skip heavy steps:

```bash
python training.py --skip-autogluon --skip-explainability
```

## Step 6: Launch the dashboard

```bash
streamlit run app.py
```

Open http://localhost:8501

## Troubleshooting

### `ModuleNotFoundError: No module named 'src'`

Run all commands from the project root directory. If using notebooks, ensure the first cell contains:

```python
import sys, os
sys.path.insert(0, os.path.abspath('..'))
```

### AutoGluon install fails

AutoGluon has heavy native dependencies. Try:

```bash
pip install autogluon.tabular==1.0.0 --no-cache-dir
```

Or skip AutoGluon entirely — the pipeline will gracefully skip the AutoML step.

### SHAP / LIME slow on large datasets

Reduce the sample size in `params.yaml`:

```yaml
explainability:
  shap_sample_size: 100  # default 200
```

### Streamlit port already in use

```bash
streamlit run app.py --server.port 8502
```

### Permission denied on logs/

```bash
chmod -R u+w logs/ saved_models/ artifacts/ data/processed/
```
