# Setup Guide: AI-Powered Dataset Upload and Reporting

This guide walks through setting up the AI-powered dataset upload and reporting feature.

## Prerequisites

- Python 3.11 or higher
- pip package manager
- Google Gemini API key (get from https://makersuite.google.com/app/apikey)

## Installation Steps

### 1. Install Dependencies

Install all required packages:

```bash
pip install -r requirements.txt
```

**New dependencies added:**
- `streamlit-icons` - Professional icon library
- `google-generativeai` - Gemini API client
- `reportlab` - PDF generation
- `fpdf2` - Alternative PDF library
- `python-docx` - DOCX generation
- `bleach` - Content sanitization

### 2. Configure Gemini API

#### Option A: Streamlit Secrets (Recommended)

1. Copy the example secrets file:
   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   ```

2. Edit `.streamlit/secrets.toml` and add your API key:
   ```toml
   GEMINI_API_KEY = "your-actual-api-key-here"
   ```

3. Verify the file is gitignored (already configured in `.gitignore`)

#### Option B: Environment Variables

Set environment variables:

**Windows (PowerShell):**
```powershell
$env:GEMINI_API_KEY = "your-api-key-here"
```

**Linux/Mac:**
```bash
export GEMINI_API_KEY="your-api-key-here"
```

### 3. Verify Installation

Check that new modules are accessible:

```python
# Test import
from src.upload import UploadHandler, SchemaValidator
from src.ai import GeminiIntegration, GeminiConfig, InsightGenerator
from src.reporting import ReportComposer, ReportConfig

print("✓ All modules imported successfully")
```

### 4. Verify Logging Configuration

Check that logging is configured for new modules:

```bash
cat logging.yaml | grep -A 3 "src.upload"
cat logging.yaml | grep -A 3 "src.ai"
cat logging.yaml | grep -A 3 "src.reporting"
```

You should see logging configurations for:
- `src.upload`
- `src.ai`
- `src.reporting`
- `google.generativeai`

### 5. Test Gemini API Connection

Create a test script:

```python
from src.ai import GeminiConfig, GeminiIntegration

# Load configuration
config = GeminiConfig.from_environment()

if not config:
    print("❌ API key not found. Check .streamlit/secrets.toml or environment variables")
    exit(1)

if not config.validate():
    print("❌ Invalid configuration")
    exit(1)

# Test authentication
gemini = GeminiIntegration(config)
if gemini.authenticate():
    print("✓ Gemini API authentication successful")
else:
    print("❌ Gemini API authentication failed")
```

## Project Structure

After setup, your project should have:

```
customer_segmentation/
├── src/
│   ├── upload/               # NEW: CSV upload and validation
│   │   ├── __init__.py
│   │   ├── upload_handler.py
│   │   ├── schema_validator.py
│   │   └── README.md
│   ├── ai/                   # NEW: AI insight generation
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── gemini_integration.py
│   │   ├── insight_generator.py
│   │   ├── markdown_sanitizer.py
│   │   └── README.md
│   └── reporting/            # NEW: Report generation
│       ├── __init__.py
│       ├── report_composer.py
│       ├── pdf_generator.py
│       ├── docx_generator.py
│       └── README.md
├── .streamlit/
│   └── secrets.toml.example  # NEW: API key template
├── docs/
│   └── ai_upload_reporting_infrastructure.md  # NEW: Infrastructure docs
├── requirements.txt          # UPDATED: New dependencies added
├── logging.yaml              # UPDATED: New module loggers
└── .gitignore               # UPDATED: Secrets excluded
```

## Configuration Reference

### Gemini API Settings

| Setting | Environment Variable | Default | Description |
|---------|---------------------|---------|-------------|
| API Key | `GEMINI_API_KEY` | (required) | Your Gemini API key |
| Model | `GEMINI_MODEL_NAME` | `gemini-1.5-flash` | Model version |
| Temperature | `GEMINI_TEMPERATURE` | `0.7` | Response randomness (0-1) |
| Max Tokens | `GEMINI_MAX_TOKENS` | `2048` | Maximum response length |
| Rate Limit | `GEMINI_RATE_LIMIT` | `10` | Requests per minute |

### Report Output Locations

Reports are saved to:
- **Persistent storage**: `artifacts/reports/`
- **File naming**: `segmentation_report_{timestamp}.{pdf|docx}`

Example:
```
artifacts/reports/segmentation_report_2024-01-15_143022.pdf
artifacts/reports/segmentation_report_2024-01-15_143022.docx
```

## Troubleshooting

### API Key Not Found

**Symptom:** "Gemini API key not found" error

**Solution:**
1. Verify `.streamlit/secrets.toml` exists and contains `GEMINI_API_KEY`
2. Or set environment variable: `export GEMINI_API_KEY="your-key"`
3. Restart Streamlit app after adding credentials

### Module Import Errors

**Symptom:** `ModuleNotFoundError: No module named 'src.upload'`

**Solution:**
1. Verify you're running from project root directory
2. Check that `__init__.py` files exist in new modules
3. Reinstall dependencies: `pip install -r requirements.txt`

### Dependency Installation Issues

**Symptom:** `streamlit-icons` installation fails

**Solution:**
```bash
pip install streamlit-icons --no-deps
```

**Symptom:** `reportlab` compilation errors on Windows

**Solution:**
1. Install Visual C++ Build Tools
2. Or use pre-built wheel: `pip install reportlab --prefer-binary`

### Logging Issues

**Symptom:** No logs appearing for new modules

**Solution:**
1. Verify `logging.yaml` includes new logger configurations
2. Check log files in `logs/` directory
3. Ensure write permissions for `logs/` directory

### Rate Limit Errors

**Symptom:** "Rate limit exceeded" from Gemini API

**Solution:**
1. Module automatically queues requests
2. Reduce `GEMINI_RATE_LIMIT` in configuration
3. Responses are cached to minimize API calls

## Next Steps

After completing setup:

1. **Read module documentation:**
   - `src/upload/README.md` - Upload and validation
   - `src/ai/README.md` - AI insight generation
   - `src/reporting/README.md` - Report generation

2. **Review infrastructure docs:**
   - `docs/ai_upload_reporting_infrastructure.md`

3. **Proceed to implementation tasks:**
   - Task 2: Icon system and Lottie components
   - Task 3: Upload handler implementation
   - Task 4: Schema validation implementation
   - And so on...

## Security Checklist

- [ ] `.streamlit/secrets.toml` is in `.gitignore`
- [ ] API key is not committed to version control
- [ ] Secrets file has restricted permissions (chmod 600 on Unix)
- [ ] Production secrets use Streamlit Cloud secrets management
- [ ] AI-generated content is sanitized before display

## Performance Expectations

After setup, the system should meet these targets:

| Operation | Target |
|-----------|--------|
| CSV upload | Up to 100MB |
| Validation | <1 second |
| Pipeline execution | <300s for 10k rows |
| AI insight generation | <10s per cluster |
| PDF report generation | <30s for 50 pages |
| DOCX report generation | <20s for 50 pages |

## Support Resources

- **Documentation**: `docs/ai_upload_reporting_infrastructure.md`
- **Module READMEs**: `src/{upload,ai,reporting}/README.md`
- **Requirements**: `.kiro/specs/ai-powered-dataset-upload-and-reporting/requirements.md`
- **Design**: `.kiro/specs/ai-powered-dataset-upload-and-reporting/design.md`
- **API Docs**: https://ai.google.dev/docs

## Verification Commands

Run these to verify setup:

```bash
# Check dependencies installed
pip list | grep -E "google-generativeai|reportlab|python-docx|bleach|streamlit-icons"

# Verify module structure
ls -R src/upload src/ai src/reporting

# Check secrets file
test -f .streamlit/secrets.toml && echo "✓ Secrets file exists" || echo "❌ Secrets file missing"

# Verify gitignore
grep "secrets.toml" .gitignore && echo "✓ Secrets gitignored" || echo "❌ Add secrets to gitignore"

# Test imports
python -c "from src.upload import UploadHandler; from src.ai import GeminiIntegration; from src.reporting import ReportComposer; print('✓ All imports successful')"
```

## Production Deployment

For Streamlit Cloud deployment:

1. **Add secrets via dashboard:**
   - Go to App Settings > Secrets
   - Add `GEMINI_API_KEY = "your-key"`

2. **Verify dependencies:**
   - Ensure `requirements.txt` includes all new packages
   - Test locally first

3. **Monitor logs:**
   - Check Streamlit Cloud logs for errors
   - Monitor Gemini API usage and quotas

4. **Set resource limits:**
   - Configure appropriate memory limits
   - Enable persistent storage if needed
