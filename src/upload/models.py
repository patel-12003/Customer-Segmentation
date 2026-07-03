"""
Data models for dataset upload module.

This module defines data classes for representing uploaded datasets
and their associated metadata.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class UploadedDataset:
    """
    Data model representing an uploaded dataset with metadata.
    
    This class captures comprehensive information about an uploaded CSV file,
    including file metadata, structural information, and data quality metrics.
    
    Attributes:
        filename: Original name of the uploaded file
        file_size_bytes: Size of the file in bytes
        upload_timestamp: Timestamp when the file was uploaded
        row_count: Number of rows in the dataset
        column_count: Number of columns in the dataset
        numeric_columns: List of numeric column names
        categorical_columns: List of categorical/object column names
        datetime_columns: List of datetime column names
        missing_value_summary: Dictionary mapping column names to missing value counts
        missing_value_ratios: Dictionary mapping column names to missing value ratios (0-1)
        column_dtypes: Dictionary mapping column names to their data types
    """
    
    filename: str
    file_size_bytes: int
    upload_timestamp: datetime
    row_count: int
    column_count: int
    numeric_columns: List[str] = field(default_factory=list)
    categorical_columns: List[str] = field(default_factory=list)
    datetime_columns: List[str] = field(default_factory=list)
    missing_value_summary: Dict[str, int] = field(default_factory=dict)
    missing_value_ratios: Dict[str, float] = field(default_factory=dict)
    column_dtypes: Dict[str, str] = field(default_factory=dict)
    
    @property
    def file_size_mb(self) -> float:
        """Return file size in megabytes."""
        return self.file_size_bytes / (1024 * 1024)
    
    @property
    def total_cells(self) -> int:
        """Return total number of cells in the dataset."""
        return self.row_count * self.column_count
    
    @property
    def total_missing_values(self) -> int:
        """Return total number of missing values across all columns."""
        return sum(self.missing_value_summary.values())
    
    @property
    def overall_missing_ratio(self) -> float:
        """Return overall missing value ratio for the entire dataset."""
        if self.total_cells == 0:
            return 0.0
        return self.total_missing_values / self.total_cells
    
    @property
    def has_sufficient_numeric_features(self) -> bool:
        """Check if dataset has at least 3 numeric features (minimum for clustering)."""
        return len(self.numeric_columns) >= 3
    
    def get_column_type(self, column_name: str) -> Optional[str]:
        """
        Get the type classification of a column.
        
        Args:
            column_name: Name of the column
            
        Returns:
            'numeric', 'categorical', 'datetime', or None if column not found
        """
        if column_name in self.numeric_columns:
            return 'numeric'
        elif column_name in self.categorical_columns:
            return 'categorical'
        elif column_name in self.datetime_columns:
            return 'datetime'
        return None
    
    def get_columns_with_high_missing_values(self, threshold: float = 0.5) -> List[str]:
        """
        Get list of columns with missing value ratio above threshold.
        
        Args:
            threshold: Missing value ratio threshold (default 0.5 = 50%)
            
        Returns:
            List of column names with high missing values
        """
        return [
            col for col, ratio in self.missing_value_ratios.items()
            if ratio > threshold
        ]
    
    def to_dict(self) -> dict:
        """
        Convert UploadedDataset to dictionary representation.
        
        Returns:
            Dictionary with all dataset metadata
        """
        return {
            'filename': self.filename,
            'file_size_bytes': self.file_size_bytes,
            'file_size_mb': self.file_size_mb,
            'upload_timestamp': self.upload_timestamp.isoformat(),
            'row_count': self.row_count,
            'column_count': self.column_count,
            'numeric_columns': self.numeric_columns,
            'categorical_columns': self.categorical_columns,
            'datetime_columns': self.datetime_columns,
            'missing_value_summary': self.missing_value_summary,
            'missing_value_ratios': self.missing_value_ratios,
            'column_dtypes': self.column_dtypes,
            'total_missing_values': self.total_missing_values,
            'overall_missing_ratio': self.overall_missing_ratio,
            'has_sufficient_numeric_features': self.has_sufficient_numeric_features
        }
    
    def __repr__(self) -> str:
        """Return string representation of UploadedDataset."""
        return (
            f"UploadedDataset(filename='{self.filename}', "
            f"rows={self.row_count}, columns={self.column_count}, "
            f"numeric={len(self.numeric_columns)}, "
            f"categorical={len(self.categorical_columns)}, "
            f"datetime={len(self.datetime_columns)}, "
            f"missing_ratio={self.overall_missing_ratio:.2%})"
        )


@dataclass
class ValidationReport:
    """
    Data model representing validation results for an uploaded dataset.
    
    This class captures the results of schema validation and data quality checks.
    
    Attributes:
        passed: Whether validation passed overall
        errors: List of error messages for validation failures
        warnings: List of warning messages for potential issues
        dataset_statistics: Dictionary of dataset summary statistics
        data_quality_metrics: Dictionary of data quality metrics
        duplicate_ratio: Ratio of duplicate rows (0-1)
        outlier_summary: Dictionary mapping column names to outlier counts
    """
    
    passed: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    dataset_statistics: Dict[str, any] = field(default_factory=dict)
    data_quality_metrics: Dict[str, float] = field(default_factory=dict)
    duplicate_ratio: float = 0.0
    outlier_summary: Dict[str, int] = field(default_factory=dict)
    
    @property
    def has_errors(self) -> bool:
        """Check if validation has any errors."""
        return len(self.errors) > 0
    
    @property
    def has_warnings(self) -> bool:
        """Check if validation has any warnings."""
        return len(self.warnings) > 0
    
    @property
    def error_count(self) -> int:
        """Return number of errors."""
        return len(self.errors)
    
    @property
    def warning_count(self) -> int:
        """Return number of warnings."""
        return len(self.warnings)
    
    def add_error(self, error_message: str) -> None:
        """Add an error message to the validation report."""
        self.errors.append(error_message)
        self.passed = False
    
    def add_warning(self, warning_message: str) -> None:
        """Add a warning message to the validation report."""
        self.warnings.append(warning_message)
    
    def to_dict(self) -> dict:
        """
        Convert ValidationReport to dictionary representation.
        
        Returns:
            Dictionary with all validation results
        """
        return {
            'passed': self.passed,
            'errors': self.errors,
            'warnings': self.warnings,
            'error_count': self.error_count,
            'warning_count': self.warning_count,
            'dataset_statistics': self.dataset_statistics,
            'data_quality_metrics': self.data_quality_metrics,
            'duplicate_ratio': self.duplicate_ratio,
            'outlier_summary': self.outlier_summary
        }
    
    def __repr__(self) -> str:
        """Return string representation of ValidationReport."""
        status = "PASSED" if self.passed else "FAILED"
        return (
            f"ValidationReport(status={status}, "
            f"errors={self.error_count}, warnings={self.warning_count})"
        )
