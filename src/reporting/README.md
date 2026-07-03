# Reporting Module

This module generates professional PDF and DOCX reports from segmentation results.

## Components

### ReportComposer
Orchestrates report generation:
- Assembles report sections from segmentation results
- Manages configurable section inclusion
- Coordinates PDF and DOCX generators
- Handles chart embedding and formatting

### PDFGenerator
Creates professional PDF reports:
- Title page with metadata
- Table of contents with hyperlinks
- Embedded visualizations at 300 DPI
- Dark theme styling support
- Professional typography

### DOCXGenerator
Creates editable Word documents:
- Microsoft Word / LibreOffice compatible
- Professional template styling
- Inline chart embedding
- Fully editable content
- Consistent heading hierarchy

## Report Sections

Reports can include:
1. **Title Page**: Report title, author, generation date
2. **Table of Contents**: Auto-generated with hyperlinks
3. **Executive Summary**: AI-generated overview
4. **Dataset Overview**: Row counts, columns, data types
5. **Data Quality Assessment**: Missing values, outliers, duplicates
6. **Segmentation Methodology**: Algorithms used and selection criteria
7. **Cluster Profiles**: Statistics, characteristics, AI insights per segment
8. **Model Performance**: Accuracy, precision, recall, F1-score
9. **Feature Importance**: Rankings and AI explanations
10. **Business Recommendations**: Actionable AI-generated suggestions
11. **Technical Appendix**: Hyperparameters, configuration, environment
12. **Glossary**: Technical terms used in the report

All sections are configurable through `ReportConfig`.

## Usage

```python
from src.reporting import ReportComposer, ReportConfig
from pathlib import Path

# Prepare segmentation results
results = {
    'dataframe': processed_df,
    'cluster_labels': labels,
    'clustering_report': cluster_report,
    'supervised_report': model_report,
    'ai_insights': insights,
    'charts': chart_objects
}

# Configure report
config = ReportConfig(
    title="Customer Segmentation Analysis",
    include_executive_summary=True,
    include_cluster_profiles=True,
    include_business_recommendations=True
)

# Generate report
composer = ReportComposer(results)

# Generate PDF
pdf_path = Path("artifacts/reports/segmentation_report.pdf")
composer.generate_pdf(config, pdf_path)

# Generate DOCX
docx_path = Path("artifacts/reports/segmentation_report.docx")
composer.generate_docx(config, docx_path)
```

## Report Configuration

```python
@dataclass
class ReportConfig:
    title: str
    author: str = "Customer Segmentation System"
    include_toc: bool = True
    include_executive_summary: bool = True
    include_dataset_overview: bool = True
    include_data_quality: bool = True
    include_methodology: bool = True
    include_cluster_profiles: bool = True
    include_model_performance: bool = True
    include_feature_importance: bool = True
    include_business_recommendations: bool = True
    include_technical_appendix: bool = True
    include_glossary: bool = True
```

## Requirements

This module requires:
- reportlab (for PDF generation)
- fpdf2 (alternative PDF library)
- python-docx (for DOCX generation)
- plotly (for chart export)

These are included in the main requirements.txt.

## Performance

Report generation targets:
- **PDF**: < 30 seconds for reports under 50 pages
- **DOCX**: < 20 seconds for reports under 50 pages
- Charts are embedded at 300 DPI for print quality

## File Naming

Reports are automatically named with timestamps:
```
segmentation_report_2024-01-15_143022.pdf
segmentation_report_2024-01-15_143022.docx
```

Reports can be saved to:
- `artifacts/reports/` directory for persistent storage
- Temporary locations for immediate download
