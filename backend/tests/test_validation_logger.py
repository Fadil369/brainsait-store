"""
Tests for validation gap logging utility.
"""

import pytest
import json
from pathlib import Path
from backend.app.core.validation_logger import (
    ValidationLogger,
    ValidationSeverity,
    ValidationType,
    ValidationGap,
    get_validation_logger
)


@pytest.mark.unit
class TestValidationGap:
    """Test ValidationGap dataclass"""
    
    def test_validation_gap_creation(self):
        """Test creating a validation gap"""
        gap = ValidationGap(
            timestamp="2024-01-01T00:00:00",
            validation_type=ValidationType.DATA_FLOW.value,
            severity=ValidationSeverity.ERROR.value,
            component="analytics_service",
            expected_value=100,
            actual_value=90,
            error_message="Revenue mismatch"
        )
        
        assert gap.timestamp == "2024-01-01T00:00:00"
        assert gap.validation_type == ValidationType.DATA_FLOW.value
        assert gap.severity == ValidationSeverity.ERROR.value
        assert gap.component == "analytics_service"
        assert gap.expected_value == 100
        assert gap.actual_value == 90
        assert gap.error_message == "Revenue mismatch"
    
    def test_validation_gap_to_dict(self):
        """Test converting validation gap to dict"""
        gap = ValidationGap(
            timestamp="2024-01-01T00:00:00",
            validation_type=ValidationType.KPI_CALCULATION.value,
            severity=ValidationSeverity.WARNING.value,
            component="kpi_calculator",
            expected_value="positive",
            actual_value="negative",
            error_message="Unexpected negative growth"
        )
        
        gap_dict = gap.to_dict()
        assert isinstance(gap_dict, dict)
        assert gap_dict["component"] == "kpi_calculator"
        assert gap_dict["severity"] == ValidationSeverity.WARNING.value


@pytest.mark.unit
class TestValidationLogger:
    """Test ValidationLogger class"""
    
    def test_logger_initialization(self, tmp_path):
        """Test initializing validation logger"""
        log_file = tmp_path / "test_validation.json"
        logger = ValidationLogger(str(log_file))
        
        assert logger.log_file == str(log_file)
        assert len(logger.validation_gaps) == 0
    
    def test_log_gap(self, tmp_path):
        """Test logging a validation gap"""
        log_file = tmp_path / "test_validation.json"
        logger = ValidationLogger(str(log_file))
        
        gap = logger.log_gap(
            ValidationType.DATA_FLOW,
            ValidationSeverity.ERROR,
            "test_component",
            expected_value=100,
            actual_value=90,
            error_message="Test error"
        )
        
        assert len(logger.validation_gaps) == 1
        assert gap.component == "test_component"
        assert gap.severity == ValidationSeverity.ERROR.value
    
    def test_log_data_flow_gap(self, tmp_path):
        """Test logging data flow gap"""
        log_file = tmp_path / "test_validation.json"
        logger = ValidationLogger(str(log_file))
        
        gap = logger.log_data_flow_gap(
            component="analytics_pipeline",
            expected_value="completed",
            actual_value="failed",
            error_message="Pipeline failed"
        )
        
        assert gap.validation_type == ValidationType.DATA_FLOW.value
        assert gap.component == "analytics_pipeline"
    
    def test_log_kpi_calculation_gap(self, tmp_path):
        """Test logging KPI calculation gap"""
        log_file = tmp_path / "test_validation.json"
        logger = ValidationLogger(str(log_file))
        
        gap = logger.log_kpi_calculation_gap(
            kpi_name="total_revenue",
            expected_value=10000,
            actual_value=9500,
            error_message="Revenue calculation mismatch"
        )
        
        assert gap.validation_type == ValidationType.KPI_CALCULATION.value
        assert "total_revenue" in gap.component
    
    def test_get_gaps_by_severity(self, tmp_path):
        """Test filtering gaps by severity"""
        log_file = tmp_path / "test_validation.json"
        logger = ValidationLogger(str(log_file))
        
        # Log gaps with different severities
        logger.log_gap(
            ValidationType.DATA_FLOW,
            ValidationSeverity.ERROR,
            "component1",
            expected_value=1,
            actual_value=2,
            error_message="Error 1"
        )
        logger.log_gap(
            ValidationType.DATA_FLOW,
            ValidationSeverity.WARNING,
            "component2",
            expected_value=1,
            actual_value=2,
            error_message="Warning 1"
        )
        logger.log_gap(
            ValidationType.DATA_FLOW,
            ValidationSeverity.ERROR,
            "component3",
            expected_value=1,
            actual_value=2,
            error_message="Error 2"
        )
        
        error_gaps = logger.get_gaps_by_severity(ValidationSeverity.ERROR)
        warning_gaps = logger.get_gaps_by_severity(ValidationSeverity.WARNING)
        
        assert len(error_gaps) == 2
        assert len(warning_gaps) == 1
    
    def test_get_gaps_by_type(self, tmp_path):
        """Test filtering gaps by type"""
        log_file = tmp_path / "test_validation.json"
        logger = ValidationLogger(str(log_file))
        
        # Log gaps with different types
        logger.log_data_flow_gap(
            "component1",
            expected_value=1,
            actual_value=2,
            error_message="Data flow error"
        )
        logger.log_kpi_calculation_gap(
            "kpi1",
            expected_value=100,
            actual_value=90,
            error_message="KPI error"
        )
        logger.log_data_flow_gap(
            "component2",
            expected_value=1,
            actual_value=2,
            error_message="Another data flow error"
        )
        
        data_flow_gaps = logger.get_gaps_by_type(ValidationType.DATA_FLOW)
        kpi_gaps = logger.get_gaps_by_type(ValidationType.KPI_CALCULATION)
        
        assert len(data_flow_gaps) == 2
        assert len(kpi_gaps) == 1
    
    def test_get_summary(self, tmp_path):
        """Test getting validation summary"""
        log_file = tmp_path / "test_validation.json"
        logger = ValidationLogger(str(log_file))
        
        # Log multiple gaps
        logger.log_gap(
            ValidationType.DATA_FLOW,
            ValidationSeverity.ERROR,
            "component1",
            expected_value=1,
            actual_value=2,
            error_message="Error 1"
        )
        logger.log_gap(
            ValidationType.KPI_CALCULATION,
            ValidationSeverity.WARNING,
            "component2",
            expected_value=1,
            actual_value=2,
            error_message="Warning 1"
        )
        logger.log_gap(
            ValidationType.COMPLIANCE,
            ValidationSeverity.CRITICAL,
            "component3",
            expected_value=1,
            actual_value=2,
            error_message="Critical 1"
        )
        
        summary = logger.get_summary()
        
        assert summary["total_gaps"] == 3
        assert summary["by_severity"]["ERROR"] == 1
        assert summary["by_severity"]["WARNING"] == 1
        assert summary["by_severity"]["CRITICAL"] == 1
        assert summary["by_type"][ValidationType.DATA_FLOW.value] == 1
        assert summary["by_type"][ValidationType.KPI_CALCULATION.value] == 1
        assert summary["by_type"][ValidationType.COMPLIANCE.value] == 1
    
    def test_export_to_json(self, tmp_path):
        """Test exporting gaps to JSON"""
        log_file = tmp_path / "test_validation.json"
        logger = ValidationLogger(str(log_file))
        
        # Log a gap
        logger.log_data_flow_gap(
            "test_component",
            expected_value=100,
            actual_value=90,
            error_message="Test error"
        )
        
        # Export to JSON
        output_file = logger.export_to_json()
        
        # Verify file exists and contains valid JSON
        assert Path(output_file).exists()
        with open(output_file, 'r') as f:
            data = json.load(f)
        
        assert "export_timestamp" in data
        assert "summary" in data
        assert "validation_gaps" in data
        assert len(data["validation_gaps"]) == 1
    
    def test_generate_report(self, tmp_path):
        """Test generating validation report"""
        log_file = tmp_path / "test_validation.json"
        logger = ValidationLogger(str(log_file))
        
        # Log multiple gaps
        logger.log_gap(
            ValidationType.DATA_FLOW,
            ValidationSeverity.CRITICAL,
            "critical_component",
            expected_value=1,
            actual_value=2,
            error_message="Critical error"
        )
        logger.log_gap(
            ValidationType.KPI_CALCULATION,
            ValidationSeverity.ERROR,
            "error_component",
            expected_value=1,
            actual_value=2,
            error_message="Error"
        )
        
        report = logger.generate_report()
        
        assert "VALIDATION GAPS REPORT" in report
        assert "Total Gaps: 2" in report
        assert "CRITICAL" in report
        assert "ERROR" in report
        assert "critical_component" in report
    
    def test_clear_gaps(self, tmp_path):
        """Test clearing validation gaps"""
        log_file = tmp_path / "test_validation.json"
        logger = ValidationLogger(str(log_file))
        
        # Log gaps
        logger.log_data_flow_gap(
            "component1",
            expected_value=1,
            actual_value=2,
            error_message="Error 1"
        )
        logger.log_data_flow_gap(
            "component2",
            expected_value=1,
            actual_value=2,
            error_message="Error 2"
        )
        
        assert len(logger.validation_gaps) == 2
        
        # Clear gaps
        logger.clear_gaps()
        
        assert len(logger.validation_gaps) == 0


@pytest.mark.unit
class TestGlobalValidationLogger:
    """Test global validation logger"""
    
    def test_get_validation_logger(self):
        """Test getting global validation logger"""
        logger1 = get_validation_logger()
        logger2 = get_validation_logger()
        
        # Should return the same instance
        assert logger1 is logger2
