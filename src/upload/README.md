# Upload Module

This module handles CSV file uploads and validation for custom customer datasets.

## Components

### UploadHandler
Manages CSV file uploads through Streamlit's file uploader component with support for:
- Files up to 100MB
- Multiple character encodings (UTF-8, latin-1)
- Automatic delimiter detection
- Comprehensive error reporting

### SchemaValidator
Validates uploaded datasets for quality and structure:
- Minimum feature requirements (at least 3 numeric columns)
- Missing value detection (max 50% null per column)
- Data type detection and reporting
- Column mapping suggestions

## Usage

```python
from src.upload import UploadHandler, SchemaValidator

# Handle file upload
result = UploadHandler.accept_upload()

if result and result.success:
    # Validate the uploaded data
    validator = SchemaValidator(result.dataframe)
    validation = validator.validate()
    
    if validation.passed:
        # Proceed with processing
        pass
    else:
        # Display errors
        for error in validation.errors:
            st.error(error)
```

## Requirements

This module requires:
- pandas
- streamlit

These are already included in the main requirements.txt.
