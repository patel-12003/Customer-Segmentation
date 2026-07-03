# Implementation Plan: AI-Powered Dataset Upload and Reporting

## Overview

This implementation plan breaks down the AI-powered dataset upload and reporting feature into discrete, actionable coding tasks. The feature enables users to upload custom CSV datasets, automatically process them through the complete segmentation pipeline, receive AI-generated insights via Google Gemini API, visualize results with advanced interactive charts, and generate professional reports in PDF and DOCX formats. Additionally, the system replaces emoji-based icons with a professional icon system and resolves Lottie animation rendering issues.

The implementation leverages existing pipeline components while adding new layers for AI integration, advanced visualization, and report generation. All tasks reference specific requirements from the requirements document.

## Tasks

- [x] 1. Set up project infrastructure and dependencies
  - Create new module structure under `src/` for upload, AI, and reporting components
  - Add required dependencies to requirements.txt: `streamlit-icons`, `google-generativeai`, `reportlab` or `fpdf2`, `python-docx`, `bleach`, `plotly`
  - Create configuration file for Gemini API settings
  - Set up logging configuration for new components
  - _Requirements: 30.1, 30.2, 30.3, 30.4, 30.5_

- [ ] 2. Implement Icon Manager for professional icon system
  - [-] 2.1 Create IconManager class in `src/ui/icon_manager.py`
    - Implement `get_icon()` method to return professional icons from streamlit-icons or Material Icons
    - Implement `render_icon_button()` method for icon buttons
    - Define icon mappings from emoji to professional icon names
    - Support sizing (sm, md, lg, xl) and color customization
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

  - [~] 2.2 Replace all emoji icons throughout the application
    - Update sidebar navigation icons in `app.py`
    - Update page header icons across all pages
    - Update section icons in dashboard, EDA, insights pages
    - Ensure consistent sizing and theme color palette (#00d2ff, #7c4dff, #00e676, #ffab40, #ff4081)
    - _Requirements: 1.1, 1.2, 1.3, 1.5_

- [ ] 3. Implement Lottie Animation Component with fallback
  - [-] 3.1 Create LottieComponent class in `src/ui/lottie_component.py`
    - Implement `load()` method with 2-second timeout
    - Implement `render()` method with fallback to IconManager
    - Add caching in session state for loaded animations
    - Handle loading errors gracefully
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

  - [~] 3.2 Update sidebar animation in `app.py`
    - Replace existing Lottie implementation with LottieComponent
    - Configure fallback icon for animation failures
    - Test smooth 30 FPS playback
    - _Requirements: 2.1, 2.2, 2.3, 2.4_


- [ ] 4. Implement CSV Upload Handler
  - [-] 4.1 Create UploadHandler class in `src/upload/upload_handler.py`
    - Implement `accept_upload()` method using Streamlit file uploader
    - Implement `parse_csv()` method with UTF-8 and latin-1 encoding fallback
    - Support files up to 100MB
    - Detect CSV delimiter automatically (comma, tab, semicolon)
    - Return UploadResult dataclass with success status, dataframe, error messages
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

  - [-] 4.2 Create UploadedDataset data model in `src/upload/models.py`
    - Define UploadedDataset dataclass with metadata fields
    - Include filename, file size, upload timestamp, row/column counts
    - Classify columns by type (numeric, categorical, datetime)
    - Calculate missing value summary
    - _Requirements: 3.1, 3.2, 3.5_

- [ ] 5. Implement Schema Validator
  - [ ] 5.1 Create SchemaValidator class in `src/upload/schema_validator.py`
    - Implement `validate()` method to run all validation checks
    - Implement `_check_minimum_features()` to ensure at least 3 numeric columns
    - Implement `_check_null_ratios()` to detect excessive missing values (>50%)
    - Implement `_detect_data_types()` for data type detection
    - Implement `suggest_column_mapping()` for flexible column mapping
    - Return ValidationResult dataclass with pass/fail status, errors, warnings, summary
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6_

  - [~] 5.2 Create ValidationReport data model in `src/upload/models.py`
    - Define ValidationReport dataclass with validation results
    - Include errors list, warnings list, dataset statistics
    - Include data quality metrics (missing value ratio, duplicate ratio, outlier summary)
    - _Requirements: 4.4, 4.5, 27.2_

- [ ] 6. Implement Pipeline Executor
  - [~] 6.1 Create PipelineExecutor class in `src/upload/pipeline_executor.py`
    - Implement `execute()` method to orchestrate complete pipeline
    - Implement `_execute_cleaning()` to invoke existing data cleaning components
    - Implement `_execute_feature_engineering()` to invoke existing FeatureEngineer
    - Implement `_execute_clustering()` to invoke existing ClusteringEngine
    - Implement `_execute_supervised()` to invoke existing SupervisedModelTrainer
    - Support progress callback for real-time updates
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 30.1, 30.2, 30.3, 30.4, 30.5_

  - [~] 6.2 Add progress tracking to PipelineExecutor
    - Define PipelineStage enum for all pipeline stages
    - Implement progress calculation and callback invocation
    - Track execution time for each stage
    - Return PipelineResult dataclass with all outputs and metrics
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_


- [~] 7. Checkpoint - Verify upload and pipeline integration
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 8. Implement Google Gemini API Integration
  - [~] 8.1 Create GeminiIntegration class in `src/ai/gemini_integration.py`
    - Implement `authenticate()` method using google-generativeai SDK
    - Implement `generate_insight()` method with prompt and caching
    - Implement `_rate_limit_check()` to enforce 10 requests per minute
    - Implement `_retry_with_backoff()` for exponential backoff retry logic
    - Implement `load_config_from_env()` to load API key from environment or Streamlit secrets
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 11.1, 11.2, 11.3, 11.4, 11.5_

  - [~] 8.2 Create GeminiConfig and GeminiResponse data models in `src/ai/models.py`
    - Define GeminiConfig dataclass with API key, model name, temperature, max tokens
    - Define GeminiResponse dataclass with success status, content, error message
    - _Requirements: 7.1, 7.2_

- [ ] 9. Implement Markdown Sanitizer
  - [~] 9.1 Create MarkdownSanitizer class in `src/ai/markdown_sanitizer.py`
    - Implement `sanitize()` method using bleach library
    - Implement `_validate_links()` to ensure HTTPS protocol only
    - Implement `_remove_script_tags()` to remove any script tags or javascript protocols
    - Define allowed HTML tags and attributes
    - Limit maximum text length to 10,000 characters
    - _Requirements: 7.5_

- [ ] 10. Implement AI Insight Generator
  - [~] 10.1 Create InsightGenerator class in `src/ai/insight_generator.py`
    - Implement `generate_cluster_insights()` to create natural language cluster profiles
    - Implement `generate_feature_importance_insights()` for top 5 features
    - Implement `generate_executive_summary()` for high-level overview (max 500 words)
    - Implement prompt building methods: `_build_cluster_prompt()`, `_build_feature_prompt()`, `_build_executive_prompt()`
    - Integrate with GeminiIntegration and MarkdownSanitizer
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 9.1, 9.2, 9.3, 9.4, 10.1, 10.2, 10.3, 10.4, 10.5_

  - [~] 10.2 Create ClusterInsight and FeatureInsight data models in `src/ai/models.py`
    - Define ClusterInsight dataclass with cluster ID, description, characteristics, recommendations
    - Define FeatureInsight dataclass with feature name, importance score, explanation
    - Define AIInsights dataclass to aggregate all AI-generated insights
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 9.1, 9.2, 9.3_


- [~] 11. Checkpoint - Verify AI integration
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 12. Implement Visualization Engine
  - [~] 12.1 Create VisualizationEngine class in `src/visualization/visualization_engine.py`
    - Implement `generate_radar_chart()` for cluster comparison across features (max 8 features)
    - Implement `generate_heatmap()` for 2D customer distribution with cluster boundaries
    - Implement `generate_sankey_diagram()` for segment transitions over time (if temporal data present)
    - Implement `generate_correlation_network()` for feature correlation network (threshold 0.5)
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 13.1, 13.2, 13.3, 13.4, 14.1, 14.2, 14.3, 14.4, 15.1, 15.2, 15.3, 15.4, 15.5_

  - [~] 12.2 Add time-series and geographic visualizations to VisualizationEngine
    - Implement `generate_timeseries_chart()` for segment evolution over time
    - Implement `generate_geographic_map()` for choropleth or scatter maps
    - Handle missing temporal/geographic data gracefully
    - _Requirements: 16.1, 16.2, 16.3, 16.4, 17.1, 17.2, 17.3, 17.4_

  - [~] 12.3 Add interactive filtering and drill-down to VisualizationEngine
    - Add multi-select cluster filters to all visualizations
    - Add date range sliders for temporal filtering
    - Implement real-time chart updates when filters change
    - Add reset button to restore default view
    - _Requirements: 18.1, 18.2, 18.3, 18.4_

- [ ] 13. Implement Chart Exporter
  - [~] 13.1 Create ChartExporter class in `src/visualization/chart_exporter.py`
    - Implement `export_to_png()` method for PNG export (1920x1080, transparent background)
    - Implement `export_to_svg()` method for SVG export
    - Preserve dark theme styling in exported images
    - Add export buttons to all visualizations
    - _Requirements: 19.1, 19.2, 19.3, 19.4_

  - [~] 13.2 Create VisualizationConfig and ChartMetadata data models in `src/visualization/models.py`
    - Define VisualizationConfig dataclass with theme, color palette, dimensions
    - Define ChartMetadata dataclass with chart details and export formats
    - Define ChartType enum for all visualization types
    - _Requirements: 12.1, 12.2, 12.3, 19.1, 19.2_


- [~] 14. Checkpoint - Verify visualizations
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 15. Implement PDF Report Generator
  - [~] 15.1 Create PDFGenerator class in `src/reporting/pdf_generator.py`
    - Implement `generate()` method to create PDF reports using reportlab or fpdf2
    - Implement `_add_title_page()` for report title, date, dataset summary
    - Implement `_add_table_of_contents()` with hyperlinks to sections
    - Implement `_add_section()` to add report sections with text and charts
    - Implement `_add_chart()` to embed PNG images at 300 DPI
    - _Requirements: 21.1, 21.2, 21.3, 21.4, 21.5_

  - [~] 15.2 Create ReportConfig data model in `src/reporting/models.py`
    - Define ReportConfig dataclass with title, author, section toggles
    - Define ReportSection dataclass with title, content, chart references
    - Define ReportMetadata dataclass for generated report metadata
    - _Requirements: 21.1, 21.2, 23.1, 23.2, 23.3, 24.1, 24.2, 24.3_

- [ ] 16. Implement DOCX Report Generator
  - [~] 16.1 Create DOCXGenerator class in `src/reporting/docx_generator.py`
    - Implement `generate()` method to create DOCX reports using python-docx
    - Implement `_apply_template_styles()` for professional formatting
    - Implement `_add_title_page()` for document title page
    - Implement `_add_table_of_contents()` for navigation
    - Implement `_add_section()` to add sections with formatted text and inline images
    - Implement `_add_chart()` to embed images in document
    - _Requirements: 22.1, 22.2, 22.3, 22.4, 22.5_

- [ ] 17. Implement Report Composer
  - [~] 17.1 Create ReportComposer class in `src/reporting/report_composer.py`
    - Implement `compose_sections()` to assemble all report sections
    - Implement `_compose_executive_summary()` using AI insights
    - Implement `_compose_dataset_overview()` with statistics
    - Implement `_compose_data_quality()` with quality assessment
    - Implement `_compose_methodology()` describing algorithms
    - _Requirements: 23.1, 23.2, 23.3, 23.4_

  - [~] 17.2 Add remaining report sections to ReportComposer
    - Implement `_compose_cluster_profiles()` for detailed cluster sections
    - Implement `_compose_model_performance()` with metrics and confusion matrix
    - Implement `_compose_feature_importance()` with rankings and AI explanations
    - Implement `_compose_recommendations()` with AI-generated suggestions
    - Implement `_compose_technical_appendix()` with configuration details
    - Implement `_compose_glossary()` with technical terms
    - _Requirements: 23.5, 23.6, 23.7, 23.8, 23.9, 23.10_


  - [~] 17.3 Add configurable section selection to ReportComposer
    - Support section enable/disable based on ReportConfig
    - Update table of contents to reflect only included sections
    - Handle optional sections gracefully
    - _Requirements: 24.1, 24.2, 24.3, 24.4, 24.5_

  - [~] 17.4 Implement report generation performance optimization
    - Display progress spinner during report generation
    - Target PDF generation within 30 seconds for reports under 50 pages
    - Target DOCX generation within 20 seconds for reports under 50 pages
    - Provide download button upon completion
    - _Requirements: 25.1, 25.2, 25.3, 25.4_

  - [~] 17.5 Add report download and storage functionality
    - Implement download button with browser download trigger
    - Name files using pattern "segmentation_report_{timestamp}.{pdf|docx}"
    - Optionally save reports to artifacts/reports directory
    - Display success message with file path
    - _Requirements: 26.1, 26.2, 26.3, 26.4_

- [~] 18. Checkpoint - Verify report generation
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 19. Implement Session State Manager
  - [~] 19.1 Create SessionStateManager class in `src/ui/session_state_manager.py`
    - Implement `set_uploaded_data()` to store uploaded dataframe
    - Implement `get_uploaded_data()` to retrieve uploaded dataframe
    - Implement `set_pipeline_results()` to store pipeline execution results
    - Implement `get_pipeline_results()` to retrieve pipeline results
    - Implement `set_ai_insights()` and `get_ai_insights()` for AI-generated content
    - Implement `set_chart()` and `get_chart()` for visualization storage
    - Implement `has_results()` to check if results available
    - Implement `clear_results()` to reset state when new data uploaded
    - _Requirements: 28.1, 28.2, 28.3, 28.4, 28.5_

- [ ] 20. Create dedicated "Upload & Analyze" page
  - [~] 20.1 Create upload_analyze_page.py in pages directory
    - Create page layout with file upload component at top
    - Display empty state when no data uploaded
    - Integrate UploadHandler for file upload
    - Integrate SchemaValidator for validation feedback
    - Display validation results (success with summary or errors)
    - _Requirements: 29.1, 29.2, 29.3, 29.4, 29.5_


  - [~] 20.2 Add pipeline execution UI to upload_analyze_page.py
    - Add "Start Analysis" button after successful validation
    - Integrate PipelineExecutor with progress callback
    - Display progress bar with overall completion percentage
    - Display current stage name (Data Cleaning, Feature Engineering, etc.)
    - Display execution time upon completion
    - Handle errors with clear messages indicating failure stage
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 6.1, 6.2, 6.3, 6.4, 6.5_

  - [~] 20.3 Add results display to upload_analyze_page.py
    - Create tabbed sections for Cluster Profiles, Visualizations, AI Insights, Report Generation
    - Display cluster profiles with statistics and AI-generated descriptions
    - Render all visualizations (radar, heatmap, network, timeseries, geographic) with interactive filters
    - Display AI insights with executive summary, cluster insights, feature importance
    - Add report generation section with section selection checkboxes and PDF/DOCX generation buttons
    - _Requirements: 29.3, 8.1, 8.2, 8.3, 12.1, 12.2, 13.1, 15.1, 16.1, 17.1_

  - [~] 20.4 Integrate error handling throughout upload_analyze_page.py
    - Display clear error messages for upload failures
    - Display all validation errors in formatted list
    - Display pipeline execution errors with stage information
    - Display API call failures with fallback messages
    - Display report generation errors with partial results if available
    - _Requirements: 27.1, 27.2, 27.3, 27.4, 27.5_

- [~] 21. Add navigation item for "Upload & Analyze" page
  - Update app.py sidebar navigation to include new page
  - Use professional icon from IconManager
  - Position page appropriately in navigation menu
  - Maintain dark theme styling
  - _Requirements: 29.1, 1.2_

- [~] 22. Update existing app.py with icon and animation improvements
  - Apply IconManager to replace all emoji icons in main app
  - Update LottieComponent for sidebar animation
  - Ensure consistent styling across all pages
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 2.1, 2.2, 2.3, 2.4_

- [ ] 23. Create comprehensive error handling module
  - [~] 23.1 Create error_handler.py in `src/utils/`
    - Define error message constants for all common error scenarios
    - Implement error logging with context information
    - Implement user-friendly error message formatting
    - Add troubleshooting suggestions for common errors
    - _Requirements: 27.1, 27.2, 27.3, 27.4, 27.5_


- [ ] 24. Final integration and testing
  - [~] 24.1 Integration testing for end-to-end upload workflow
    - Test complete workflow: upload → validation → pipeline → insights → visualization → report
    - Verify session state persistence across page navigations
    - Test with various dataset sizes (100 rows, 1000 rows, 10000 rows)
    - Test with edge cases (high missing values, outliers, categorical only)
    - _Requirements: 3.1, 4.1, 5.1, 8.1, 12.1, 21.1, 22.1_

  - [~] 24.2 Performance testing and optimization
    - Verify 100MB file upload completes within 10 seconds
    - Verify pipeline execution for 10000 rows completes within 300 seconds
    - Verify AI insight generation completes within 60 seconds for 5 clusters
    - Verify report generation completes within 30 seconds for PDF, 20 seconds for DOCX
    - _Requirements: 3.2, 5.6, 8.5, 25.1, 25.2_

  - [~] 24.3 UI/UX polish and dark theme consistency
    - Verify all icons are professional and consistent
    - Verify Lottie animation loads smoothly or fallback displays
    - Verify progress indicators update smoothly
    - Verify dark theme styling (#00d2ff, #7c4dff, #00e676, #ffab40, #ff4081) applied consistently
    - Verify responsive layout on different screen sizes
    - _Requirements: 1.4, 1.5, 2.1, 2.3, 2.4, 6.3, 29.4_

- [~] 25. Final checkpoint - Complete feature verification
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- All tasks reference specific requirements from the requirements document for traceability
- Checkpoint tasks ensure incremental validation and allow for user feedback
- The implementation reuses existing pipeline components from `src/data`, `src/features`, `src/models`, `src/evaluation` to maintain consistency
- Error handling is prioritized throughout with graceful degradation when AI features fail
- Progress indicators provide real-time feedback during long-running operations
- Session state management ensures data persistence during user navigation
- Professional icon system and Lottie animation improvements enhance UI polish
- AI integration with Google Gemini API requires proper API key configuration via environment variables or Streamlit secrets
- Visualizations leverage Plotly for interactivity and dark theme compatibility
- Report generation supports both PDF (reportlab/fpdf2) and DOCX (python-docx) formats with professional formatting
- All components follow modular design for maintainability and testability


## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1"] },
    { "id": 1, "tasks": ["2.1", "3.1", "4.1", "4.2", "5.1", "5.2", "8.1", "8.2", "9.1", "19.1"] },
    { "id": 2, "tasks": ["2.2", "3.2", "6.1", "10.1", "10.2", "12.1", "13.2", "15.2"] },
    { "id": 3, "tasks": ["6.2", "12.2", "13.1", "15.1", "16.1", "17.1", "23.1"] },
    { "id": 4, "tasks": ["12.3", "17.2"] },
    { "id": 5, "tasks": ["17.3", "17.4", "17.5", "20.1"] },
    { "id": 6, "tasks": ["20.2"] },
    { "id": 7, "tasks": ["20.3", "20.4", "21", "22"] },
    { "id": 8, "tasks": ["24.1", "24.2", "24.3"] }
  ]
}
```
