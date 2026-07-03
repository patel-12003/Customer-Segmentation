# AI Module

This module provides Google Gemini API integration for generating AI-powered business insights from segmentation results.

## Components

### GeminiIntegration
Handles communication with the Google Gemini API:
- API authentication and configuration
- Rate limiting (configurable requests per minute)
- Exponential backoff retry logic
- Response caching for efficiency
- Error handling with graceful fallbacks

### InsightGenerator
Generates natural language insights:
- **Cluster profiles**: Business-focused descriptions and recommendations for each segment
- **Feature importance**: Explanations of key differentiating features
- **Executive summaries**: High-level overviews for decision-makers (max 500 words)

### MarkdownSanitizer
Secures AI-generated content:
- Removes script tags and dangerous protocols
- Validates link protocols (HTTPS only)
- Enforces content length limits
- Preserves standard markdown formatting

## Configuration

### Environment Variables
Set these in your environment or `.streamlit/secrets.toml`:

```toml
GEMINI_API_KEY = "your-api-key-here"
GEMINI_MODEL_NAME = "gemini-1.5-flash"  # optional
GEMINI_TEMPERATURE = "0.7"              # optional
GEMINI_MAX_TOKENS = "2048"              # optional
GEMINI_RATE_LIMIT = "10"                # optional
```

### Getting an API Key
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to your secrets configuration

## Usage

```python
from src.ai import GeminiIntegration, GeminiConfig, InsightGenerator

# Load configuration
config = GeminiConfig.from_environment()

if config and config.validate():
    # Initialize Gemini integration
    gemini = GeminiIntegration(config)
    
    if gemini.authenticate():
        # Generate insights
        insight_gen = InsightGenerator(gemini)
        
        cluster_insights = insight_gen.generate_cluster_insights(cluster_profiles)
        feature_insights = insight_gen.generate_feature_importance_insights(importances)
        executive_summary = insight_gen.generate_executive_summary(
            n_clusters, dataset_info, cluster_insights
        )
```

## Requirements

This module requires:
- google-generativeai
- bleach
- streamlit (for secrets management)

These are included in the main requirements.txt.

## Rate Limiting

The module implements rate limiting to stay within API quotas:
- Default: 10 requests per minute
- Configurable via `GEMINI_RATE_LIMIT` environment variable
- Automatic queuing when rate limit approached
- Exponential backoff for transient errors (1s, 2s, 4s)

## Security

All AI-generated content is sanitized before display:
- Script injection prevention
- Protocol validation (HTTPS only)
- Maximum length enforcement (10,000 chars)
- HTML tag whitelisting
