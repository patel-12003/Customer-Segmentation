# Requirements Document

## Introduction

This specification defines an advanced AI-powered enhancement for the Customer Categorizer system. The enhancement enables users to upload their own customer datasets, automatically process them through the complete segmentation pipeline, receive AI-generated business insights using Google Gemini API, visualize results with advanced interactive charts, and generate comprehensive professional reports in PDF and DOCX formats. Additionally, the system replaces all emoji-based icons with a professional icon library and fixes Lottie animation rendering issues.

## Glossary

- **Segmentation_System**: The existing Customer Categorizer and classification ML pipeline
- **Upload_Handler**: Component responsible for accepting and validating CSV file uploads
- **Pipeline_Executor**: Component that orchestrates the complete segmentation workflow
- **Gemini_Integration**: Component interfacing with Google Gemini API for AI insights
- **Visualization_Engine**: Component generating interactive charts and visualizations
- **Report_Generator**: Component producing PDF and DOCX reports
- **Icon_Manager**: Component managing professional icon display across the UI
- **Lottie_Component**: Sidebar animation component
- **Session_State**: Streamlit session storage for maintaining processing state
- **Schema_Validator**: Component that validates uploaded CSV structure and data quality
- **Feature_Engineer**: Component creating derived features from raw data
- **Cluster_Analyzer**: Component performing unsupervised clustering
- **Model_Trainer**: Component training supervised classification models
- **Insight_Generator**: Component generating natural language insights via AI
- **Chart_Exporter**: Component exporting visualizations to image formats
- **Markdown_Sanitizer**: Component cleaning and sanitizing AI-generated markdown content

## Requirements

### Requirement 1: Professional Icon System Replacement

**User Story:** As a user, I want to see professional icons throughout the application instead of emojis, so that the interface appears more polished and enterprise-ready.

#### Acceptance Criteria

1. THE Icon_Manager SHALL replace all emoji icons with icons from streamlit-icons or Material Icons library
2. THE Icon_Manager SHALL update all sidebar navigation icons to use the professional icon library
3. THE Icon_Manager SHALL update all section header icons throughout all pages
4. THE Icon_Manager SHALL maintain the current dark theme color scheme (#00d2ff, #7c4dff, #00e676, #ffab40, #ff4081)
5. FOR ALL icons displayed, THE Icon_Manager SHALL ensure consistent sizing and alignment

### Requirement 2: Lottie Animation Rendering

**User Story:** As a user, I want the sidebar Lottie animation to load smoothly and reliably, so that I have a polished visual experience.

#### Acceptance Criteria

1. THE Lottie_Component SHALL render animations without flickering or stuttering
2. WHEN the Lottie animation fails to load, THE Lottie_Component SHALL display a fallback static icon or placeholder
3. THE Lottie_Component SHALL complete animation loading within 2 seconds
4. THE Lottie_Component SHALL maintain smooth playback at 30 frames per second minimum

### Requirement 3: CSV Dataset Upload

**User Story:** As a business analyst, I want to upload my own customer data CSV file, so that I can perform segmentation on my specific dataset.

#### Acceptance Criteria

1. THE Upload_Handler SHALL accept CSV files via Streamlit file uploader component
2. THE Upload_Handler SHALL support CSV files up to 100MB in size
3. WHEN a CSV file is uploaded, THE Upload_Handler SHALL parse it using UTF-8 encoding with fallback to latin-1
4. WHEN CSV parsing fails, THE Upload_Handler SHALL return a descriptive error message indicating the specific parsing issue
5. THE Upload_Handler SHALL store the uploaded dataframe in Session_State for pipeline processing

### Requirement 4: Schema Validation and Data Quality Checks

**User Story:** As a user, I want the system to validate my uploaded data and report any quality issues, so that I can correct problems before processing.

#### Acceptance Criteria

1. THE Schema_Validator SHALL check for minimum required columns (at least 3 numeric features)
2. THE Schema_Validator SHALL detect and report columns with excessive missing values (more than 50% null)
3. THE Schema_Validator SHALL identify data type mismatches and type conversion failures
4. WHEN validation succeeds, THE Schema_Validator SHALL display a success message with dataset summary statistics
5. WHEN validation fails, THE Schema_Validator SHALL display specific error messages for each validation failure
6. THE Schema_Validator SHALL allow flexible column mapping (user can specify which columns to use for segmentation)

### Requirement 5: Automatic Segmentation Pipeline Execution

**User Story:** As a user, I want the system to automatically run the complete segmentation pipeline on my uploaded data, so that I receive results without manual configuration.

#### Acceptance Criteria

1. WHEN validation succeeds, THE Pipeline_Executor SHALL execute data cleaning operations (imputation, outlier handling)
2. THE Pipeline_Executor SHALL execute feature engineering to create derived business metrics
3. THE Pipeline_Executor SHALL execute clustering using auto-selected best algorithm from the 10 available algorithms
4. THE Pipeline_Executor SHALL execute supervised model training on the discovered clusters
5. THE Pipeline_Executor SHALL execute model evaluation and store performance metrics
6. THE Pipeline_Executor SHALL complete the entire pipeline within 300 seconds for datasets under 10000 rows

### Requirement 6: Processing Progress Indicators

**User Story:** As a user, I want to see progress indicators during pipeline execution, so that I understand processing status and estimated completion time.

#### Acceptance Criteria

1. THE Pipeline_Executor SHALL display a progress bar indicating overall completion percentage
2. THE Pipeline_Executor SHALL display the current stage name (Data Cleaning, Feature Engineering, Clustering, Model Training, Evaluation)
3. THE Pipeline_Executor SHALL update progress indicators in real-time as each stage completes
4. WHEN processing completes successfully, THE Pipeline_Executor SHALL display a success message with total execution time
5. WHEN processing fails, THE Pipeline_Executor SHALL display an error message indicating which stage failed and why

### Requirement 7: Google Gemini API Integration for AI Insights

**User Story:** As a business stakeholder, I want AI-generated natural language insights about my customer segments, so that I can understand the business implications without technical expertise.

#### Acceptance Criteria

1. THE Gemini_Integration SHALL authenticate with Google Gemini API using an API key from environment variables or Streamlit secrets
2. WHEN the API key is missing or invalid, THE Gemini_Integration SHALL display an error message and disable AI insight features
3. THE Gemini_Integration SHALL send cluster profile data and feature importance to Gemini API for analysis
4. THE Gemini_Integration SHALL receive and parse markdown-formatted insights from the API response
5. THE Markdown_Sanitizer SHALL sanitize AI-generated markdown to prevent injection attacks before rendering

### Requirement 8: AI Insight Generation for Cluster Profiles

**User Story:** As a user, I want AI-generated insights for each customer segment, so that I understand the characteristics and business value of each cluster.

#### Acceptance Criteria

1. FOR EACH cluster discovered, THE Insight_Generator SHALL generate a natural language profile description
2. FOR EACH cluster discovered, THE Insight_Generator SHALL generate actionable business recommendations
3. THE Insight_Generator SHALL include key differentiating features in the cluster description
4. THE Insight_Generator SHALL format insights in markdown with bullet points and emphasis
5. THE Insight_Generator SHALL generate insights within 10 seconds per cluster

### Requirement 9: AI Insights for Feature Importance

**User Story:** As a data scientist, I want AI explanations of which features drive segment differentiation, so that I can understand the model's decision-making process.

#### Acceptance Criteria

1. THE Insight_Generator SHALL analyze feature importance scores from the trained model
2. THE Insight_Generator SHALL generate natural language explanations for the top 5 most important features
3. THE Insight_Generator SHALL explain how each important feature contributes to segment differentiation
4. THE Insight_Generator SHALL format feature importance insights in markdown with numbered lists

### Requirement 10: AI-Powered Executive Summary

**User Story:** As an executive, I want an AI-generated executive summary of the segmentation results, so that I can quickly understand high-level findings.

#### Acceptance Criteria

1. THE Insight_Generator SHALL generate an executive summary containing the number of segments discovered
2. THE Insight_Generator SHALL include high-level business characteristics of each segment in the summary
3. THE Insight_Generator SHALL include overall data quality assessment in the summary
4. THE Insight_Generator SHALL recommend next steps for business action based on the segmentation
5. THE Insight_Generator SHALL limit the executive summary to 500 words maximum

### Requirement 11: Rate Limiting and Error Handling for API Calls

**User Story:** As a system administrator, I want API calls to be rate-limited and handle errors gracefully, so that the system remains stable under various conditions.

#### Acceptance Criteria

1. THE Gemini_Integration SHALL implement exponential backoff retry logic for transient API failures
2. THE Gemini_Integration SHALL limit API requests to 10 requests per minute maximum
3. WHEN the API rate limit is exceeded, THE Gemini_Integration SHALL queue requests and process them sequentially
4. WHEN an API error occurs, THE Gemini_Integration SHALL log the error details and display a user-friendly fallback message
5. THE Gemini_Integration SHALL cache AI responses in Session_State to avoid redundant API calls during the same session

### Requirement 12: Cluster Comparison Radar Charts

**User Story:** As an analyst, I want interactive radar charts comparing clusters across multiple dimensions, so that I can quickly visualize segment differences.

#### Acceptance Criteria

1. THE Visualization_Engine SHALL generate radar charts with normalized feature values for all clusters
2. THE Visualization_Engine SHALL display up to 8 features on each radar chart
3. THE Visualization_Engine SHALL use distinct colors from the theme palette for each cluster overlay
4. THE Visualization_Engine SHALL render radar charts using Plotly with hover tooltips showing exact values
5. THE Visualization_Engine SHALL allow users to select which features to include in the radar chart

### Requirement 13: Customer Distribution Heatmaps

**User Story:** As a user, I want heatmaps showing customer distribution patterns, so that I can identify concentration areas and patterns.

#### Acceptance Criteria

1. THE Visualization_Engine SHALL generate 2D heatmaps showing customer density across two selected features
2. THE Visualization_Engine SHALL overlay cluster boundaries on the heatmap visualization
3. THE Visualization_Engine SHALL use a perceptually-uniform color scale for density visualization
4. THE Visualization_Engine SHALL render heatmaps using Plotly with zoom and pan capabilities

### Requirement 14: Segment Journey Flow Diagrams

**User Story:** As a marketing manager, I want flow diagrams showing how customers might transition between segments, so that I can design targeted campaigns.

#### Acceptance Criteria

1. WHEN temporal data is present in the uploaded dataset, THE Visualization_Engine SHALL generate Sankey diagrams showing segment transitions
2. THE Visualization_Engine SHALL calculate transition probabilities between segments based on sequential records
3. THE Visualization_Engine SHALL display flow thickness proportional to transition volume
4. WHEN temporal data is absent, THE Visualization_Engine SHALL display a message indicating this visualization requires temporal columns

### Requirement 15: Feature Correlation Network Graphs

**User Story:** As a data scientist, I want network graphs showing feature correlations, so that I can understand feature relationships and multicollinearity.

#### Acceptance Criteria

1. THE Visualization_Engine SHALL generate network graphs with nodes representing features and edges representing correlations
2. THE Visualization_Engine SHALL display edges only for correlations with absolute value above 0.5
3. THE Visualization_Engine SHALL use edge thickness to represent correlation strength
4. THE Visualization_Engine SHALL use edge color to represent positive (blue) versus negative (red) correlations
5. THE Visualization_Engine SHALL render network graphs using Plotly with interactive node positioning

### Requirement 16: Time-Series Trend Visualization

**User Story:** As an analyst, I want time-series charts showing segment evolution, so that I can identify trends and seasonality in customer behavior.

#### Acceptance Criteria

1. WHEN temporal columns are detected in the uploaded dataset, THE Visualization_Engine SHALL generate line charts showing segment sizes over time
2. THE Visualization_Engine SHALL generate line charts showing feature value trends by segment over time
3. THE Visualization_Engine SHALL allow users to select the date column and aggregation period (daily, weekly, monthly)
4. WHEN no temporal columns exist, THE Visualization_Engine SHALL hide time-series visualizations

### Requirement 17: Geographic Distribution Maps

**User Story:** As a regional manager, I want geographic maps showing customer segment distribution, so that I can plan location-based strategies.

#### Acceptance Criteria

1. WHEN geographic columns (latitude/longitude or country/state/city) are detected, THE Visualization_Engine SHALL generate choropleth or scatter maps
2. THE Visualization_Engine SHALL color-code map regions or points by dominant segment
3. THE Visualization_Engine SHALL display hover tooltips with segment distribution statistics for each geographic area
4. WHEN no geographic data is present, THE Visualization_Engine SHALL hide geographic visualizations

### Requirement 18: Interactive Chart Filtering and Drill-Down

**User Story:** As a user, I want to filter visualizations by segment, date range, and features, so that I can explore specific subsets of data.

#### Acceptance Criteria

1. THE Visualization_Engine SHALL provide multi-select filters for cluster selection on all visualizations
2. WHEN date columns exist, THE Visualization_Engine SHALL provide date range sliders for temporal filtering
3. THE Visualization_Engine SHALL update all charts in real-time when filters change
4. THE Visualization_Engine SHALL provide a reset button to clear all filters and restore default view

### Requirement 19: Chart Export Functionality

**User Story:** As a user, I want to export individual charts as image files, so that I can include them in presentations and reports.

#### Acceptance Criteria

1. THE Chart_Exporter SHALL provide export buttons for PNG format on all visualizations
2. THE Chart_Exporter SHALL provide export buttons for SVG format on all visualizations
3. WHEN export is clicked, THE Chart_Exporter SHALL download the chart with transparent background and resolution of 1920x1080 pixels minimum
4. THE Chart_Exporter SHALL preserve dark theme styling in exported images

### Requirement 20: AI-Enhanced Visualization Tooltips

**User Story:** As a user, I want tooltips on visualizations to include AI-generated explanations, so that I understand what I'm looking at without extensive domain knowledge.

#### Acceptance Criteria

1. THE Visualization_Engine SHALL generate concise (under 50 words) AI explanations for tooltip content on cluster visualizations
2. THE Visualization_Engine SHALL include the AI explanation in the Plotly hover template
3. THE Visualization_Engine SHALL cache tooltip explanations to minimize API calls

### Requirement 21: PDF Report Generation

**User Story:** As a manager, I want to generate PDF reports of segmentation results, so that I can share findings with stakeholders who prefer document formats.

#### Acceptance Criteria

1. THE Report_Generator SHALL create PDF reports using reportlab or fpdf2 library
2. THE Report_Generator SHALL include a title page with report title, generation date, and dataset summary
3. THE Report_Generator SHALL include a table of contents with hyperlinks to sections
4. THE Report_Generator SHALL embed all key visualizations as PNG images at 300 DPI resolution
5. THE Report_Generator SHALL format AI-generated insights with proper typography and spacing

### Requirement 22: DOCX Report Generation

**User Story:** As a user, I want to generate editable Word documents of segmentation results, so that I can customize reports before distribution.

#### Acceptance Criteria

1. THE Report_Generator SHALL create DOCX reports using python-docx library
2. THE Report_Generator SHALL apply a professional template with consistent heading styles
3. THE Report_Generator SHALL embed all visualizations as inline images
4. THE Report_Generator SHALL format tables with appropriate borders and shading
5. THE Report_Generator SHALL generate reports that are fully editable in Microsoft Word or LibreOffice

### Requirement 23: Report Content Structure

**User Story:** As a user, I want comprehensive reports covering all aspects of the analysis, so that I have complete documentation of the segmentation project.

#### Acceptance Criteria

1. THE Report_Generator SHALL include an executive summary section with AI-generated overview
2. THE Report_Generator SHALL include a dataset overview section with row counts, column counts, and data types
3. THE Report_Generator SHALL include a data quality assessment section with missing value analysis and outlier detection
4. THE Report_Generator SHALL include a segmentation methodology section describing algorithms used and selection criteria
5. THE Report_Generator SHALL include detailed cluster profile sections with statistics, characteristics, and AI insights for each segment
6. THE Report_Generator SHALL include a model performance section with accuracy, precision, recall, and F1-score metrics
7. THE Report_Generator SHALL include a feature importance section with rankings and AI explanations
8. THE Report_Generator SHALL include business recommendations sections with actionable AI-generated suggestions per segment
9. THE Report_Generator SHALL include a technical appendix with hyperparameters, configuration, and environment details
10. THE Report_Generator SHALL include a glossary of technical terms used in the report

### Requirement 24: Configurable Report Sections

**User Story:** As a user, I want to select which sections to include in my report, so that I can generate customized reports for different audiences.

#### Acceptance Criteria

1. THE Report_Generator SHALL display checkboxes for each report section before generation
2. THE Report_Generator SHALL enable all sections by default
3. THE Report_Generator SHALL allow users to deselect any optional section (all sections except title page and table of contents are optional)
4. WHEN a section is deselected, THE Report_Generator SHALL exclude that section and its visualizations from the generated report
5. THE Report_Generator SHALL update the table of contents to reflect only included sections

### Requirement 25: Report Generation Performance

**User Story:** As a user, I want reports to generate quickly, so that I can iterate on report customization efficiently.

#### Acceptance Criteria

1. THE Report_Generator SHALL generate PDF reports within 30 seconds for reports under 50 pages
2. THE Report_Generator SHALL generate DOCX reports within 20 seconds for reports under 50 pages
3. THE Report_Generator SHALL display a progress spinner during report generation
4. WHEN report generation completes, THE Report_Generator SHALL provide a download button for the generated file

### Requirement 26: Report Download and Storage

**User Story:** As a user, I want to download generated reports and optionally store them for later access, so that I can maintain a library of analysis results.

#### Acceptance Criteria

1. THE Report_Generator SHALL provide a download button that triggers browser download of the report file
2. THE Report_Generator SHALL name report files using pattern "segmentation_report_{timestamp}.{pdf|docx}"
3. WHERE storage is enabled, THE Report_Generator SHALL save reports to the artifacts/reports directory
4. THE Report_Generator SHALL display a success message with the file path after successful report generation

### Requirement 27: Error Handling for Upload and Processing

**User Story:** As a user, I want clear error messages when issues occur during upload or processing, so that I can take corrective action.

#### Acceptance Criteria

1. WHEN file upload fails, THE Upload_Handler SHALL display an error message indicating the specific failure reason
2. WHEN schema validation fails, THE Schema_Validator SHALL display all validation errors in a formatted list
3. WHEN pipeline execution fails, THE Pipeline_Executor SHALL display the error message and the stage at which failure occurred
4. WHEN API calls fail, THE Gemini_Integration SHALL display a fallback message and continue with non-AI features
5. WHEN report generation fails, THE Report_Generator SHALL display an error message and provide a partial report if possible

### Requirement 28: Session State Management for Uploaded Data

**User Story:** As a user, I want my uploaded data and results to persist during my session, so that I can navigate between pages without losing my work.

#### Acceptance Criteria

1. THE Session_State SHALL store the uploaded raw dataframe across page navigations
2. THE Session_State SHALL store the processed dataframe with cluster labels across page navigations
3. THE Session_State SHALL store all pipeline results (reports, metrics, model artifacts) across page navigations
4. THE Session_State SHALL store all AI-generated insights across page navigations
5. WHEN a new file is uploaded, THE Session_State SHALL clear previous results and replace with new results

### Requirement 29: Dedicated Upload and Results Page

**User Story:** As a user, I want a dedicated page for dataset upload and viewing results, so that I have a clear workflow for analyzing my own data.

#### Acceptance Criteria

1. THE Segmentation_System SHALL add a new navigation page titled "Upload & Analyze Your Data"
2. THE new page SHALL display the file upload component prominently at the top
3. WHEN results are available in Session_State, THE new page SHALL display tabbed sections for Cluster Profiles, Visualizations, AI Insights, and Report Generation
4. THE new page SHALL maintain the dark theme aesthetic and styling conventions
5. THE new page SHALL display appropriate empty states when no data has been uploaded yet

### Requirement 30: Integration with Existing Pipeline Components

**User Story:** As a developer, I want the new upload feature to reuse existing pipeline code, so that segmentation logic remains consistent and maintainable.

#### Acceptance Criteria

1. THE Pipeline_Executor SHALL invoke existing data transformation components from src.data
2. THE Pipeline_Executor SHALL invoke existing feature engineering components from src.features
3. THE Pipeline_Executor SHALL invoke existing clustering components from src.models.clustering
4. THE Pipeline_Executor SHALL invoke existing supervised model components from src.models.supervised
5. THE Pipeline_Executor SHALL invoke existing evaluation components from src.evaluation
