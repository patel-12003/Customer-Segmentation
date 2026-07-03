# AI-Powered Dataset Upload and Reporting Infrastructure

This document describes the infrastructure for the AI-powered dataset upload and reporting feature.

## Overview

The infrastructure adds three new modules to the customer segmentation system:

1. **Upload Module** (`src/upload/`): Handles CSV file uploads and validation
2. **AI Module** (`src/ai/`): Integrates with Google Gemini API for insight generation
3. **Reporting Module** (`src/reporting/`): Generates professional PDF and DOCX reports

## Module Structure

```
src/
├── upload/
│   ├── __init__.py
│   ├── upload_handler.py       # CSV file upload handling
│   ├── schema_validator.py     # Data quality validation
│   └── README.md
├── ai/
│   ├── __init__.py
│   ├── config.py               # Gemini API configuration
│   ├── gemini_integration.py   # API communication layer
│   ├── insight_generator.py    # Business insights generation
│   ├── markdown_sanitizer.py   # Security sanitization
│   └── README.md
└── reporting/
    ├── __init__.py
    ├── report_composer.py      # Report orchestration
    ├── pdf_generator.py        # PDF report generation
    ├── docx_generator.py       # DOCX report generation
    └── README.md
```

## Dependencies

The following dependencies have been added to `requirements.txt`:

### AI Integration
- `google-generativeai` - Google Gemini API client library

### Report Generation
- `reportlab` - PDF generation library
- `fpdf2` - Alternative PDF library
- `python-docx` - DOCX generation library

### Security
- `bleach` - HTML/markdown sanitization

### UI Enhancement
- `streamlit-icons` - Professional icon library (replaces emojis)

## Configuration

### Gemini API Configuration

Create `.streamlit/secrets.toml` (use `.streamlit/secrets.toml.example` as template):

```toml
# Required
GEMINI_API_KEY = "your-api-key-here"

# Optional (defaults shown)
GEMINI_MODEL_NAME = "gemini-1.5-flash"
GEMINI_TEMPERATURE = "0.7"
GEMINI_MAX_TOKENS = "2048"
GEMINI_RATE_LIMIT = "10"
```

**Getting an API Key:**
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add to `.streamlit/secrets.toml`

**Alternative:** Set as environment variables:
```bash
export GEMINI_API_KEY="your-api-key-here"
```

### Logging Configuration

Logging for new modules is configured in `logging.yaml`:

```yaml
loggers:
  src.upload:
    level: DEBUG
    handlers: [console, file]
    propagate: false
  src.ai:
    level: DEBUG
    handlers: [console, file]
    propagate: false
  src.reporting:
    level: DEBUG
    handlers: [console, file]
    propagate: false
  google.generativeai:
    level: INFO
```

Logs are written to:
- `logs/customer_segmentation.log` - All debug and info messages
- `logs/error.log` - Error messages only

## Installation

Install new dependencies:

```bash
pip install -r requirements.txt
```

**Note:** If you encounter issues with `streamlit-icons`, try:
```bash
pip install streamlit-icons --no-deps
```

## Module Responsibilities

### Upload Module

**Purpose:** Accept and validate CSV uploads from users

**Key Components:**
- `UploadHandler`: Manages file upload through Streamlit
  - Supports files up to 100MB
  - Auto-detects encoding (UTF-8, latin-1)
  - Parses CSV with automatic delimiter detection

- `SchemaValidator`: Validates data quality
  - Checks minimum features (≥3 numeric columns)
  - Detects excessive missing values (>50% null)
  - Reports data type mismatches
  - Suggests column mappings

**Requirements Validated:**
- Requirement 3: CSV Dataset Upload
- Requirement 4: Schema Validation and Data Quality Checks

### AI Module

**Purpose:** Generate business insights using Google Gemini API

**Key Components:**
- `GeminiIntegration`: API communication layer
  - Authentication and credential management
  - Rate limiting (10 requests/minute default)
  - Exponential backoff retry logic
  - Response caching

- `InsightGenerator`: Natural language insight generation
  - Cluster profile descriptions
  - Business recommendations per segment
  - Feature importance explanations
  - Executive summaries (≤500 words)

- `MarkdownSanitizer`: Security layer
  - Removes script tags
  - Validates link protocols (HTTPS only)
  - Enforces content length limits
  - Prevents injection attacks

**Requirements Validated:**
- Requirement 7: Google Gemini API Integration
- Requirement 8: AI Insight Generation for Cluster Profiles
- Requirement 9: AI Insights for Feature Importance
- Requirement 10: AI-Powered Executive Summary
- Requirement 11: Rate Limiting and Error Handling

### Reporting Module

**Purpose:** Generate professional PDF and DOCX reports

**Key Components:**
- `ReportComposer`: Orchestrates report generation
  - Assembles sections from segmentation results
  - Manages configurable section inclusion
  - Coordinates PDF/DOCX generators

- `PDFGenerator`: Creates professional PDFs
  - Title page with metadata
  - Table of contents with hyperlinks
  - 300 DPI chart embedding
  - Professional typography

- `DOCXGenerator`: Creates editable Word documents
  - Microsoft Word compatible
  - Professional template styling
  - Inline chart embedding
  - Fully editable content

**Report Sections:**
1. Title Page
2. Table of Contents
3. Executive Summary
4. Dataset Overview
5. Data Quality Assessment
6. Segmentation Methodology
7. Cluster Profiles
8. Model Performance
9. Feature Importance
10. Business Recommendations
11. Technical Appendix
12. Glossary

**Requirements Validated:**
- Requirement 21: PDF Report Generation
- Requirement 22: DOCX Report Generation
- Requirement 23: Report Content Structure
- Requirement 24: Configurable Report Sections
- Requirement 25: Report Generation Performance
- Requirement 26: Report Download and Storage

## Integration Points

The new modules integrate with existing pipeline components:

### Data Flow
```
User Upload (CSV)
    ↓
UploadHandler → SchemaValidator
    ↓
Existing Pipeline Components (src.data, src.features, src.models)
    ↓
Results → InsightGenerator (via Gemini API)
    ↓
Results + AI Insights → ReportComposer
    ↓
PDF/DOCX Reports
```

### Existing Component Reuse

**From `src.data`:**
- Data cleaning and imputation
- Outlier handling
- Data transformation

**From `src.features`:**
- Feature engineering
- Feature selection

**From `src.models`:**
- Clustering algorithms
- Supervised model training
- Model evaluation

**From `src.evaluation`:**
- Performance metrics
- Model comparison

**From `src.visualization`:**
- Chart generation
- Plotly visualizations

## Performance Targets

### Upload & Processing
- CSV upload: Up to 100MB
- Pipeline execution: <300 seconds for datasets <10,000 rows
- Validation: Near-instant (<1 second)

### AI Insights
- Gemini API: 10 insights/minute (rate limited)
- Insight generation: <10 seconds per cluster
- Executive summary: <15 seconds

### Report Generation
- PDF: <30 seconds for <50 pages
- DOCX: <20 seconds for <50 pages
- Chart embedding: 300 DPI resolution

## Security Considerations

### API Key Security
- Never commit secrets to version control
- Use `.streamlit/secrets.toml` (gitignored)
- For production: Use Streamlit Cloud secrets management

### Content Sanitization
- All AI-generated content is sanitized
- Script tags removed
- Only HTTPS links allowed
- Maximum content length enforced (10,000 chars)

### Data Privacy
- Uploaded data stored only in session state
- No persistent storage of user data
- Data cleared when session ends

## Error Handling

### Upload Errors
- File too large: Clear error with size limit
- Invalid format: Specific parsing error message
- Encoding issues: Automatic fallback to latin-1

### Validation Errors
- Missing features: List required columns
- Excessive nulls: Report problematic columns
- Type mismatches: Suggest data corrections

### API Errors
- Missing API key: Disable AI features gracefully
- Rate limit exceeded: Queue requests automatically
- Transient errors: Retry with exponential backoff
- Non-retryable errors: Display fallback message

### Report Generation Errors
- Chart export failure: Continue with available charts
- Section generation failure: Skip section, continue report
- File write failure: Display error, retry option

## Testing

Each module includes:
- Unit tests for individual components
- Integration tests with existing pipeline
- Error handling validation
- Performance benchmarking

Test files will be located in:
- `tests/test_upload/`
- `tests/test_ai/`
- `tests/test_reporting/`

## Future Enhancements

Potential future additions:
1. Support for Excel file uploads
2. Multiple AI model backends (OpenAI, Claude, etc.)
3. Interactive report builder UI
4. Custom report templates
5. Scheduled report generation
6. Email delivery of reports
7. Report versioning and history

## References

### Requirements
- See `requirements.md` for detailed acceptance criteria (Req 1-30)

### Design
- See `design.md` for technical architecture and interfaces

### API Documentation
- [Google Gemini API Docs](https://ai.google.dev/docs)
- [ReportLab User Guide](https://www.reportlab.com/docs/reportlab-userguide.pdf)
- [python-docx Documentation](https://python-docx.readthedocs.io/)
- [Streamlit Secrets Management](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management)

## Support

For issues or questions:
1. Check module README files in each `src/*/` directory
2. Review logs in `logs/customer_segmentation.log`
3. Verify API credentials in `.streamlit/secrets.toml`
4. Ensure all dependencies are installed: `pip install -r requirements.txt`
