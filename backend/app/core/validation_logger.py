"""
Validation Gap Logging Utility

This module provides centralized logging for validation gaps and issues
discovered during dashboard and module data flow validation.
"""

import json
import logging
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict


class ValidationSeverity(str, Enum):
    """Severity levels for validation gaps"""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ValidationType(str, Enum):
    """Types of validation performed"""
    DATA_FLOW = "DATA_FLOW"
    KPI_CALCULATION = "KPI_CALCULATION"
    ALERT_PIPELINE = "ALERT_PIPELINE"
    ROUTE_READINESS = "ROUTE_READINESS"
    COMPLIANCE = "COMPLIANCE"
    INTEGRATION = "INTEGRATION"
    FEATURE_FLAG = "FEATURE_FLAG"
    CONTENT_ADAPTER = "CONTENT_ADAPTER"


@dataclass
class ValidationGap:
    """Represents a validation gap or issue"""
    
    timestamp: str
    validation_type: str
    severity: str
    component: str
    expected_value: Any
    actual_value: Any
    error_message: str
    tenant_id: Optional[str] = None
    endpoint: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Ensure timestamp is set"""
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2)


class ValidationLogger:
    """
    Centralized validation gap logger
    
    Provides methods to log validation gaps discovered during
    dashboard and module validation processes.
    """
    
    def __init__(self, log_file: Optional[str] = None):
        """
        Initialize validation logger
        
        Args:
            log_file: Optional path to log file. If not provided,
                     defaults to logs/validation_gaps.json
        """
        self.log_file = log_file or "logs/validation_gaps.json"
        self.validation_gaps: List[ValidationGap] = []
        
        # Ensure log directory exists
        log_dir = Path(self.log_file).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up Python logger
        self.logger = logging.getLogger("validation_logger")
        self.logger.setLevel(logging.INFO)
        
        # Add file handler if not already present
        if not self.logger.handlers:
            handler = logging.FileHandler(self.log_file.replace('.json', '.log'))
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def log_gap(
        self,
        validation_type: ValidationType,
        severity: ValidationSeverity,
        component: str,
        expected_value: Any,
        actual_value: Any,
        error_message: str,
        tenant_id: Optional[str] = None,
        endpoint: Optional[str] = None,
        **metadata
    ) -> ValidationGap:
        """
        Log a validation gap
        
        Args:
            validation_type: Type of validation
            severity: Severity level
            component: Component being validated
            expected_value: Expected value
            actual_value: Actual value found
            error_message: Description of the gap
            tenant_id: Optional tenant ID
            endpoint: Optional API endpoint
            **metadata: Additional metadata
        
        Returns:
            ValidationGap object
        """
        gap = ValidationGap(
            timestamp=datetime.utcnow().isoformat(),
            validation_type=validation_type.value,
            severity=severity.value,
            component=component,
            expected_value=expected_value,
            actual_value=actual_value,
            error_message=error_message,
            tenant_id=tenant_id,
            endpoint=endpoint,
            metadata=metadata or None
        )
        
        self.validation_gaps.append(gap)
        
        # Log to standard logger as well
        log_message = (
            f"{severity.value} - {validation_type.value} - {component}: "
            f"{error_message}"
        )
        
        if severity == ValidationSeverity.CRITICAL:
            self.logger.critical(log_message)
        elif severity == ValidationSeverity.ERROR:
            self.logger.error(log_message)
        elif severity == ValidationSeverity.WARNING:
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)
        
        return gap
    
    def log_data_flow_gap(
        self,
        component: str,
        expected_value: Any,
        actual_value: Any,
        error_message: str,
        severity: ValidationSeverity = ValidationSeverity.ERROR,
        **metadata
    ) -> ValidationGap:
        """Log a data flow validation gap"""
        return self.log_gap(
            ValidationType.DATA_FLOW,
            severity,
            component,
            expected_value,
            actual_value,
            error_message,
            **metadata
        )
    
    def log_kpi_calculation_gap(
        self,
        kpi_name: str,
        expected_value: Any,
        actual_value: Any,
        error_message: str,
        severity: ValidationSeverity = ValidationSeverity.ERROR,
        **metadata
    ) -> ValidationGap:
        """Log a KPI calculation gap"""
        return self.log_gap(
            ValidationType.KPI_CALCULATION,
            severity,
            f"KPI: {kpi_name}",
            expected_value,
            actual_value,
            error_message,
            **metadata
        )
    
    def log_alert_pipeline_gap(
        self,
        alert_type: str,
        expected_value: Any,
        actual_value: Any,
        error_message: str,
        severity: ValidationSeverity = ValidationSeverity.WARNING,
        **metadata
    ) -> ValidationGap:
        """Log an alert pipeline gap"""
        return self.log_gap(
            ValidationType.ALERT_PIPELINE,
            severity,
            f"Alert: {alert_type}",
            expected_value,
            actual_value,
            error_message,
            **metadata
        )
    
    def log_route_readiness_gap(
        self,
        route: str,
        expected_value: Any,
        actual_value: Any,
        error_message: str,
        severity: ValidationSeverity = ValidationSeverity.INFO,
        **metadata
    ) -> ValidationGap:
        """Log a route readiness gap"""
        return self.log_gap(
            ValidationType.ROUTE_READINESS,
            severity,
            f"Route: {route}",
            expected_value,
            actual_value,
            error_message,
            **metadata
        )
    
    def log_compliance_gap(
        self,
        compliance_check: str,
        expected_value: Any,
        actual_value: Any,
        error_message: str,
        severity: ValidationSeverity = ValidationSeverity.CRITICAL,
        **metadata
    ) -> ValidationGap:
        """Log a compliance gap"""
        return self.log_gap(
            ValidationType.COMPLIANCE,
            severity,
            f"Compliance: {compliance_check}",
            expected_value,
            actual_value,
            error_message,
            **metadata
        )
    
    def log_integration_gap(
        self,
        integration_name: str,
        expected_value: Any,
        actual_value: Any,
        error_message: str,
        severity: ValidationSeverity = ValidationSeverity.WARNING,
        **metadata
    ) -> ValidationGap:
        """Log an integration gap"""
        return self.log_gap(
            ValidationType.INTEGRATION,
            severity,
            f"Integration: {integration_name}",
            expected_value,
            actual_value,
            error_message,
            **metadata
        )
    
    def get_gaps_by_severity(self, severity: ValidationSeverity) -> List[ValidationGap]:
        """Get all gaps of a specific severity"""
        return [gap for gap in self.validation_gaps if gap.severity == severity.value]
    
    def get_gaps_by_type(self, validation_type: ValidationType) -> List[ValidationGap]:
        """Get all gaps of a specific type"""
        return [gap for gap in self.validation_gaps if gap.validation_type == validation_type.value]
    
    def get_critical_gaps(self) -> List[ValidationGap]:
        """Get all critical gaps"""
        return self.get_gaps_by_severity(ValidationSeverity.CRITICAL)
    
    def get_error_gaps(self) -> List[ValidationGap]:
        """Get all error gaps"""
        return self.get_gaps_by_severity(ValidationSeverity.ERROR)
    
    def get_warning_gaps(self) -> List[ValidationGap]:
        """Get all warning gaps"""
        return self.get_gaps_by_severity(ValidationSeverity.WARNING)
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all validation gaps
        
        Returns:
            Dictionary with gap counts by severity and type
        """
        summary = {
            "total_gaps": len(self.validation_gaps),
            "by_severity": {
                "CRITICAL": len(self.get_gaps_by_severity(ValidationSeverity.CRITICAL)),
                "ERROR": len(self.get_gaps_by_severity(ValidationSeverity.ERROR)),
                "WARNING": len(self.get_gaps_by_severity(ValidationSeverity.WARNING)),
                "INFO": len(self.get_gaps_by_severity(ValidationSeverity.INFO))
            },
            "by_type": {},
            "latest_gap": None
        }
        
        # Count by type
        for vtype in ValidationType:
            summary["by_type"][vtype.value] = len(self.get_gaps_by_type(vtype))
        
        # Add latest gap
        if self.validation_gaps:
            summary["latest_gap"] = self.validation_gaps[-1].to_dict()
        
        return summary
    
    def export_to_json(self, filename: Optional[str] = None) -> str:
        """
        Export all validation gaps to JSON file
        
        Args:
            filename: Optional filename. If not provided, uses default log file
        
        Returns:
            Path to exported file
        """
        output_file = filename or self.log_file
        
        data = {
            "export_timestamp": datetime.utcnow().isoformat(),
            "summary": self.get_summary(),
            "validation_gaps": [gap.to_dict() for gap in self.validation_gaps]
        }
        
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        return output_file
    
    def clear_gaps(self):
        """Clear all validation gaps"""
        self.validation_gaps = []
    
    def generate_report(self) -> str:
        """
        Generate a human-readable validation report
        
        Returns:
            Formatted report string
        """
        summary = self.get_summary()
        
        report = [
            "=" * 80,
            "VALIDATION GAPS REPORT",
            "=" * 80,
            f"\nGenerated: {datetime.utcnow().isoformat()}",
            f"\nTotal Gaps: {summary['total_gaps']}",
            "\n\nGaps by Severity:",
            "-" * 40
        ]
        
        for severity, count in summary['by_severity'].items():
            report.append(f"  {severity}: {count}")
        
        report.extend([
            "\n\nGaps by Type:",
            "-" * 40
        ])
        
        for vtype, count in summary['by_type'].items():
            report.append(f"  {vtype}: {count}")
        
        # Add critical gaps details
        critical_gaps = self.get_critical_gaps()
        if critical_gaps:
            report.extend([
                "\n\nCRITICAL GAPS (Immediate Attention Required):",
                "=" * 80
            ])
            for gap in critical_gaps:
                report.append(f"\n{gap.component}")
                report.append(f"  Timestamp: {gap.timestamp}")
                report.append(f"  Type: {gap.validation_type}")
                report.append(f"  Message: {gap.error_message}")
                report.append(f"  Expected: {gap.expected_value}")
                report.append(f"  Actual: {gap.actual_value}")
                if gap.endpoint:
                    report.append(f"  Endpoint: {gap.endpoint}")
        
        # Add error gaps summary
        error_gaps = self.get_error_gaps()
        if error_gaps:
            report.extend([
                "\n\nERROR GAPS (Requires Resolution):",
                "=" * 80,
                f"Total: {len(error_gaps)} errors"
            ])
            for gap in error_gaps[:5]:  # Show first 5
                report.append(f"\n  - {gap.component}: {gap.error_message}")
        
        report.extend([
            "\n\n" + "=" * 80,
            "END OF REPORT",
            "=" * 80
        ])
        
        return "\n".join(report)


# Global validation logger instance
_validation_logger: Optional[ValidationLogger] = None


def get_validation_logger() -> ValidationLogger:
    """
    Get the global validation logger instance
    
    Returns:
        ValidationLogger instance
    """
    global _validation_logger
    if _validation_logger is None:
        _validation_logger = ValidationLogger()
    return _validation_logger
