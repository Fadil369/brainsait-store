# 📊 Advanced Analytics and Monitoring Dashboard

## Overview

The BrainSAIT store now includes a comprehensive analytics and monitoring dashboard that provides real-time insights into system performance, business metrics, and financial compliance.

## 🚀 New Features

### 1. System Monitoring Dashboard (`/dashboard/admin`)

**Real-time Infrastructure Monitoring:**
- CPU, Memory, and Disk usage with color-coded alerts
- Database health monitoring with connection time and slow query detection
- Network I/O metrics and system resource utilization
- Automated alerting system with configurable thresholds

**Application Performance Monitoring:**
- Response time metrics (avg, p50, p95, p99)
- Error rate tracking and application health status
- Request throughput and volume analysis
- Real-time performance charts with 30-second auto-refresh

### 2. Enhanced Business Analytics

**Financial Analytics with ZATCA Compliance:**
- Saudi VAT (15%) calculation and reporting
- ZATCA compliance validation and status
- Monthly financial breakdown with tax analysis
- Payment method reconciliation and billing metrics

**Comprehensive Business Metrics:**
- Revenue analytics with growth tracking
- Customer behavior and lifetime value analysis
- Product performance and sales analytics
- Payment method distribution and success rates

### 3. API Endpoints

**New Monitoring APIs:**
```
GET /api/v1/monitoring/health        # System health metrics
GET /api/v1/monitoring/performance   # Application performance data
GET /api/v1/monitoring/uptime        # System uptime and availability
GET /api/v1/monitoring/alerts        # Active system alerts
```

**Enhanced Analytics APIs:**
```
GET /api/v1/analytics/financial      # ZATCA-compliant financial data
GET /api/v1/analytics/real-time      # Live dashboard metrics
GET /api/v1/analytics/export         # Report export functionality
```

## 🎯 Key Features

### Real-time Monitoring
- Live system metrics with automatic refresh
- Visual indicators for system health status
- Interactive charts and graphs using Recharts
- Mobile-responsive dashboard design

### Automated Alerting
- CPU usage > 80% (Warning)
- Memory usage > 85% (Warning)  
- Disk usage > 90% (Critical)
- Error rate > 5% (Warning)

### ZATCA Compliance
- Automatic VAT calculation (15% Saudi rate)
- Compliance status validation
- Financial record archiving (7-year retention)
- Export functionality for tax reporting

### Multi-tenant Support
- Tenant-specific analytics and monitoring
- Role-based access control integration
- Scalable architecture for enterprise use

## 🛠️ Technical Implementation

### Backend Services
- **MonitoringService**: System resource monitoring using `psutil`
- **Enhanced AnalyticsService**: Financial analytics with VAT calculations
- **API Router Integration**: New monitoring endpoints in FastAPI

### Frontend Components
- **MonitoringDashboard.tsx**: Real-time system monitoring interface
- **FinancialAnalytics.tsx**: ZATCA-compliant financial reporting
- **Enhanced AnalyticsDashboard.tsx**: Unified analytics interface

### Dependencies Added
- `psutil`: System monitoring and resource utilization
- Enhanced Recharts integration for data visualization
- Real-time WebSocket support for live updates

## 📱 User Interface

### Dashboard Navigation
1. **System Monitoring**: Real-time infrastructure and application metrics
2. **Business Analytics**: Revenue, customer, and product analytics
3. **Financial & VAT**: ZATCA-compliant financial reporting
4. **System Settings**: Configuration and retention policies

### Visual Features
- Color-coded status indicators (Green/Yellow/Red)
- Interactive charts with hover tooltips
- Progress bars for resource utilization
- Alert badges with severity levels
- Export functionality with multiple formats

## 🔧 Configuration

### Environment Variables
```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Monitoring Settings
MONITORING_REFRESH_INTERVAL=30000  # 30 seconds
ALERT_THRESHOLDS_CPU=80           # CPU percentage
ALERT_THRESHOLDS_MEMORY=85        # Memory percentage
ALERT_THRESHOLDS_DISK=90          # Disk percentage
```

### Backend Configuration
```python
# Monitoring service thresholds
alert_thresholds = {
    "cpu_usage": 80.0,
    "memory_usage": 85.0, 
    "disk_usage": 90.0,
    "error_rate": 5.0,
    "response_time": 2000,  # milliseconds
}
```

## 🚦 Getting Started

1. **Access the Admin Dashboard:**
   ```
   Navigate to: /dashboard/admin
   ```

2. **View System Health:**
   - Check the System Monitoring tab for real-time metrics
   - Monitor alerts in the top banner if any issues exist

3. **Review Financial Reports:**
   - Switch to Financial & VAT tab
   - Export ZATCA-compliant reports as needed

4. **Monitor Application Performance:**
   - View response times and error rates
   - Track throughput and system utilization

## 📊 Sample Screenshots

The dashboard provides:
- Real-time system metrics with live charts
- ZATCA-compliant financial reporting
- Interactive analytics with export capabilities
- Mobile-responsive design for all devices

## 🔒 Security & Compliance

- **Authentication**: Role-based access control
- **Data Security**: Encrypted data transmission
- **ZATCA Compliance**: Saudi tax authority requirements
- **Data Retention**: Configurable retention policies
- **Audit Trail**: Comprehensive activity logging

---

**Status**: ✅ Production Ready  
**Last Updated**: December 2024  
**Version**: 1.0.0