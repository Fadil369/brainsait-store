# Dashboard & Module Validation Guide

## Overview

This guide explains how to use the validation framework created for the BrainSAIT Store dashboard and module data flows.

## Quick Start

### Run Complete Validation

```bash
cd backend
python3 scripts/validate_dashboard_data_flows.py --verbose --export-report validation_report.json
```

This will:
- Validate all analytics data flows
- Check KPI calculations
- Audit alert pipeline readiness
- Review phase-2 routes
- Verify compliance patterns
- Generate detailed reports

### Check Exit Codes

```bash
# Exit code 0: All validations passed
# Exit code 1: Critical issues found
# Exit code 2: Errors found (no critical)
```

## Running Tests

### Run All Validation Tests

```bash
cd backend
python -m pytest tests/api/test_analytics_validation.py -v
python -m pytest tests/api/test_alert_pipeline_validation.py -v
python -m pytest tests/api/test_phase2_routes_validation.py -v
python -m pytest tests/test_validation_logger.py -v
```

### Run Specific Test Classes

```bash
# Analytics validation
python -m pytest tests/api/test_analytics_validation.py::TestAnalyticsDataFlowValidation -v

# Alert pipeline validation
python -m pytest tests/api/test_alert_pipeline_validation.py::TestAlertPipelineValidation -v

# Phase-2 routes validation
python -m pytest tests/api/test_phase2_routes_validation.py::TestPhase2RouteStructure -v
```

### Run Tests by Marker

```bash
# Run only API tests
python -m pytest -m api -v

# Run only integration tests
python -m pytest -m integration -v

# Run only unit tests
python -m pytest -m unit -v
```

## Using the Validation Logger

### Basic Usage

```python
from app.core.validation_logger import (
    get_validation_logger,
    ValidationSeverity,
    ValidationType
)

# Get logger instance
logger = get_validation_logger()

# Log a validation gap
logger.log_gap(
    validation_type=ValidationType.DATA_FLOW,
    severity=ValidationSeverity.ERROR,
    component="analytics_service",
    expected_value=100,
    actual_value=90,
    error_message="Revenue calculation mismatch",
    tenant_id="tenant-123",
    endpoint="/api/v1/analytics/revenue"
)
```

### Specialized Logging Methods

```python
# Log data flow gap
logger.log_data_flow_gap(
    component="order_pipeline",
    expected_value="completed",
    actual_value="pending",
    error_message="Order not completing properly"
)

# Log KPI calculation gap
logger.log_kpi_calculation_gap(
    kpi_name="total_revenue",
    expected_value=10000,
    actual_value=9500,
    error_message="Revenue calculation mismatch"
)

# Log alert pipeline gap
logger.log_alert_pipeline_gap(
    alert_type="fraud_detection",
    expected_value="triggered",
    actual_value="not_triggered",
    error_message="Fraud alert not firing"
)

# Log route readiness gap
logger.log_route_readiness_gap(
    route="/api/v1/alerts",
    expected_value="implemented",
    actual_value="planned",
    error_message="Route not yet implemented"
)

# Log compliance gap
logger.log_compliance_gap(
    compliance_check="tenant_isolation",
    expected_value="enforced",
    actual_value="bypassed",
    error_message="Tenant isolation not enforced",
    severity=ValidationSeverity.CRITICAL
)

# Log integration gap
logger.log_integration_gap(
    integration_name="givc_api",
    expected_value="connected",
    actual_value="disconnected",
    error_message="GIVC API not responding"
)
```

### Retrieving and Analyzing Gaps

```python
# Get all critical gaps
critical_gaps = logger.get_critical_gaps()

# Get all errors
error_gaps = logger.get_error_gaps()

# Get all warnings
warning_gaps = logger.get_warning_gaps()

# Get gaps by type
data_flow_gaps = logger.get_gaps_by_type(ValidationType.DATA_FLOW)
kpi_gaps = logger.get_gaps_by_type(ValidationType.KPI_CALCULATION)

# Get summary
summary = logger.get_summary()
print(f"Total gaps: {summary['total_gaps']}")
print(f"Critical: {summary['by_severity']['CRITICAL']}")
print(f"Errors: {summary['by_severity']['ERROR']}")
```

### Generating Reports

```python
# Export to JSON
logger.export_to_json("validation_results.json")

# Generate human-readable report
report = logger.generate_report()
print(report)

# Save report to file
with open("validation_report.txt", "w") as f:
    f.write(report)

# Clear gaps after reporting
logger.clear_gaps()
```

## Validation Test Structure

### Test File Organization

```
backend/tests/
├── api/
│   ├── test_analytics_validation.py      # Analytics data flow tests
│   ├── test_alert_pipeline_validation.py # Alert pipeline tests
│   └── test_phase2_routes_validation.py  # Route readiness tests
└── test_validation_logger.py             # Logger utility tests
```

### Test Classes

Each test file contains multiple test classes organized by functionality:

**test_analytics_validation.py:**
- `TestAnalyticsDataFlowValidation` - Core data flow tests
- `TestAnalyticsFixtureDataValidation` - Fixture data tests
- `TestAnalyticsValidationGapLogging` - Gap logging tests
- `TestGIVCDataIntegration` - GIVC integration tests
- `TestCompliancePatterns` - Compliance validation tests

**test_alert_pipeline_validation.py:**
- `TestAlertPipelineValidation` - Core pipeline tests
- `TestAlertBandRendering` - UI rendering tests
- `TestAlertPipelineIntegration` - End-to-end tests

**test_phase2_routes_validation.py:**
- `TestPhase2RouteStructure` - Route structure tests
- `TestModuleReadinessValidation` - Module readiness tests
- `TestAPIVersioningConsistency` - API versioning tests
- `TestRouteDocumentation` - Documentation tests

## Custom Validation Scripts

### Creating a Custom Validator

```python
#!/usr/bin/env python3
import asyncio
from app.core.validation_logger import get_validation_logger, ValidationSeverity, ValidationType

class CustomValidator:
    def __init__(self):
        self.logger = get_validation_logger()
    
    async def validate_custom_feature(self):
        """Validate a custom feature"""
        # Perform validation
        expected = "some_value"
        actual = "other_value"
        
        if expected != actual:
            self.logger.log_gap(
                ValidationType.DATA_FLOW,
                ValidationSeverity.ERROR,
                "custom_component",
                expected,
                actual,
                "Custom validation failed"
            )
            return False
        return True
    
    async def run(self):
        """Run all custom validations"""
        result = await self.validate_custom_feature()
        
        # Generate report
        summary = self.logger.get_summary()
        print(f"Validation complete: {summary['total_gaps']} gaps found")
        
        return result

async def main():
    validator = CustomValidator()
    success = await validator.run()
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Validate Dashboard Data Flows

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  validate:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.12'
    
    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run validation tests
      run: |
        cd backend
        python -m pytest tests/api/test_analytics_validation.py -v
        python -m pytest tests/api/test_alert_pipeline_validation.py -v
        python -m pytest tests/api/test_phase2_routes_validation.py -v
    
    - name: Run validation script
      run: |
        cd backend
        python3 scripts/validate_dashboard_data_flows.py --verbose --export-report validation_report.json
    
    - name: Upload validation report
      uses: actions/upload-artifact@v2
      if: always()
      with:
        name: validation-report
        path: backend/validation_report.*
```

## Validation Checklist

Use this checklist when adding new features:

### For New Analytics Endpoints

- [ ] Endpoint structure follows existing patterns
- [ ] Response includes `success`, `data`, and `message` fields
- [ ] Tenant isolation is enforced
- [ ] Date range parameters are validated
- [ ] Data types are correct (numerics, strings, dates)
- [ ] Aggregations are calculated correctly
- [ ] Tests added to `test_analytics_validation.py`
- [ ] Validation gaps logged if any issues found

### For New Alert Types

- [ ] Alert type is defined (fraud, compliance, system)
- [ ] Severity levels are appropriate
- [ ] Trigger conditions are clear
- [ ] Alert staging works correctly
- [ ] Deduplication is implemented
- [ ] Tests added to `test_alert_pipeline_validation.py`
- [ ] Validation gaps logged if any issues found

### For New Routes (Phase 2)

- [ ] Route path follows convention
- [ ] Authentication requirements defined
- [ ] Authorization/permissions specified
- [ ] Rate limiting configured
- [ ] Dependencies identified
- [ ] Documentation complete
- [ ] Tests added to `test_phase2_routes_validation.py`
- [ ] Validation gaps logged if any issues found

## Troubleshooting

### Common Issues

**Issue: Tests not found**
```bash
# Make sure you're in the backend directory
cd backend

# Verify Python path
python3 -c "import sys; print(sys.path)"

# Run with explicit module path
python -m pytest tests/api/test_analytics_validation.py
```

**Issue: Validation logger import error**
```bash
# Ensure you're importing from the correct path
from app.core.validation_logger import get_validation_logger

# Or add backend to path
import sys
sys.path.insert(0, '/path/to/backend')
```

**Issue: No validation gaps logged**
```bash
# Check if logger is initialized
logger = get_validation_logger()
print(f"Logger initialized: {logger is not None}")

# Verify gaps are being logged
logger.log_data_flow_gap("test", "expected", "actual", "Test gap")
print(f"Gaps logged: {len(logger.validation_gaps)}")
```

## Best Practices

1. **Always use the validation logger** when discovering issues
2. **Choose appropriate severity levels**:
   - CRITICAL: Security issues, data corruption
   - ERROR: Functional failures, incorrect calculations
   - WARNING: Potential issues, deprecated usage
   - INFO: Informational, planned features

3. **Include context** in validation gaps:
   - Component name
   - Expected vs actual values
   - Clear error messages
   - Relevant metadata (tenant_id, endpoint, etc.)

4. **Run validations regularly**:
   - Before commits
   - In CI/CD pipelines
   - After major changes
   - Before releases

5. **Review validation reports**:
   - Check summary statistics
   - Address critical and error-level gaps
   - Plan fixes for warnings
   - Track informational items

## Support

For issues or questions about the validation framework:
1. Check the test files for examples
2. Review `VALIDATION_REPORT.md` for validation results
3. Check validation logs in `backend/logs/validation_gaps.log`
4. Review generated reports in `backend/validation_report.*`

## Contributing

When adding new validation capabilities:
1. Add tests to appropriate test file
2. Update validation logger if needed
3. Document new validation types
4. Update this guide
5. Run full validation suite before committing
