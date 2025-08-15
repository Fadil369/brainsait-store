# Admin User Guide - BrainSAIT Store

## Overview

The BrainSAIT Store admin interface provides comprehensive tools for managing your B2B platform, including tenant management, user administration, product catalog, analytics, and system configuration.

## Getting Started

### Accessing the Admin Panel

1. **Login URL**: `https://store.brainsait.io/admin`
2. **Credentials**: Use your admin account credentials
3. **Multi-Factor Authentication**: Required for admin access

### Dashboard Overview

The admin dashboard provides a comprehensive view of your platform:

- **System Health**: Real-time system status
- **Key Metrics**: Revenue, users, orders
- **Recent Activity**: Latest transactions and user activity
- **Alerts**: System notifications and warnings

## Tenant Management

### Creating a New Tenant

1. Navigate to **Tenants** → **Add New Tenant**
2. Fill in the required information:
   - **Tenant Name**: Display name for the tenant
   - **Tenant ID**: Unique identifier (auto-generated)
   - **Domain**: Custom domain (optional)
   - **Plan**: Subscription plan selection
   - **Billing Information**: Payment details

3. Configure tenant settings:
   - **Language**: Default language (Arabic/English)
   - **Currency**: Primary currency
   - **Time Zone**: Tenant time zone
   - **Features**: Enable/disable specific features

### Managing Existing Tenants

#### Tenant Overview
- **Status**: Active, suspended, or disabled
- **Subscription**: Current plan and billing status
- **Usage Statistics**: Resource utilization
- **Custom Settings**: Tenant-specific configurations

#### Tenant Configuration
```yaml
# Example tenant configuration
tenant_id: "company-xyz"
name: "Company XYZ"
settings:
  language: "ar"
  currency: "SAR"
  timezone: "Asia/Riyadh"
  features:
    analytics: true
    payments: true
    integrations: true
```

### Tenant Billing Management

1. **Subscription Plans**:
   - Enterprise: $19,999 (Full features)
   - Professional: $9,999 (Standard features)
   - Starter: $4,999 (Basic features)

2. **Payment Management**:
   - View payment history
   - Update payment methods
   - Generate invoices
   - Handle billing disputes

## User Management

### User Roles and Permissions

#### Admin Roles
- **Super Admin**: Full system access
- **Tenant Admin**: Tenant-specific administration
- **Support Admin**: Customer support access
- **Finance Admin**: Billing and payments access

#### User Roles
- **Owner**: Full tenant access
- **Manager**: Management access within tenant
- **User**: Standard user access
- **Guest**: Limited read-only access

### Creating User Accounts

1. Navigate to **Users** → **Add New User**
2. Enter user information:
   - **Name**: Full name
   - **Email**: Primary email address
   - **Role**: Select appropriate role
   - **Tenant**: Assign to tenant
   - **Permissions**: Custom permissions if needed

3. Account settings:
   - **Status**: Active/Inactive
   - **Email Verification**: Require email verification
   - **MFA**: Enable multi-factor authentication
   - **Password Policy**: Set password requirements

### User Access Control

#### Permission Matrix
| Feature | Owner | Manager | User | Guest |
|---------|-------|---------|------|-------|
| User Management | ✅ | ✅ | ❌ | ❌ |
| Product Management | ✅ | ✅ | ✅ | ❌ |
| Analytics | ✅ | ✅ | ✅ | ✅ |
| Billing | ✅ | ❌ | ❌ | ❌ |
| Settings | ✅ | ❌ | ❌ | ❌ |

#### Custom Permissions
```json
{
  "permissions": {
    "products": ["read", "write", "delete"],
    "analytics": ["read"],
    "users": ["read", "write"],
    "billing": ["read"]
  }
}
```

## Product Management

### Adding Products

1. Navigate to **Products** → **Add Product**
2. Product information:
   - **Name**: Product name (English/Arabic)
   - **Description**: Detailed description
   - **Category**: Product category
   - **Price**: Pricing in multiple currencies
   - **Images**: Product images and media

3. Product settings:
   - **Availability**: Stock management
   - **Tags**: Product tags for search
   - **SEO**: Meta descriptions and keywords
   - **Attributes**: Custom product attributes

### Managing Product Catalog

#### Categories
```
Digital Products
├── Software Tools
├── eBooks & Guides
├── Templates
└── Courses

Physical Products
├── Hardware
├── Accessories
└── Merchandise
```

#### Bulk Operations
- **Import**: CSV/Excel bulk import
- **Export**: Export product catalog
- **Update**: Bulk price updates
- **Delete**: Bulk deletion with confirmation

### Inventory Management

1. **Stock Tracking**:
   - Real-time inventory levels
   - Low stock alerts
   - Automatic reorder points

2. **Warehouses**:
   - Multiple warehouse support
   - Location-based inventory
   - Transfer management

## Analytics and Reporting

### Dashboard Metrics

#### Key Performance Indicators
- **Revenue**: Total and trending revenue
- **Conversion Rate**: Order conversion metrics
- **Customer Acquisition**: New customer metrics
- **Average Order Value**: AOV trends

#### Real-time Metrics
```json
{
  "revenue": {
    "today": "$12,450",
    "month": "$445,280",
    "growth": "+15.3%"
  },
  "orders": {
    "today": 47,
    "pending": 12,
    "completed": 35
  },
  "customers": {
    "active": 1247,
    "new_today": 8,
    "retention_rate": "87%"
  }
}
```

### Custom Reports

1. **Revenue Reports**:
   - By time period
   - By product category
   - By customer segment
   - By geographic region

2. **User Analytics**:
   - User engagement metrics
   - Feature usage statistics
   - Login and activity patterns
   - Support ticket trends

### Exporting Data

#### Export Formats
- **CSV**: Spreadsheet format
- **JSON**: API-friendly format
- **PDF**: Formatted reports
- **Excel**: Advanced spreadsheet format

#### Automated Reports
```yaml
scheduled_reports:
  - name: "Weekly Revenue Report"
    schedule: "every monday 9:00 AM"
    format: "pdf"
    recipients: ["finance@company.com"]
  
  - name: "Monthly Analytics"
    schedule: "first day of month"
    format: "excel"
    recipients: ["management@company.com"]
```

## Payment Management

### Payment Providers

#### Configured Providers
- **Stripe**: Live environment
- **PayPal**: Business account
- **Apple Pay**: Domain verified
- **Saudi Payments**: Mada, STC Pay

#### Provider Configuration
```json
{
  "stripe": {
    "environment": "live",
    "webhook_endpoint": "/webhooks/stripe",
    "supported_currencies": ["USD", "SAR", "AED"]
  },
  "paypal": {
    "environment": "live",
    "webhook_endpoint": "/webhooks/paypal",
    "supported_currencies": ["USD", "EUR", "SAR"]
  }
}
```

### Transaction Management

1. **Transaction Overview**:
   - Recent transactions
   - Payment status tracking
   - Refund processing
   - Dispute management

2. **Payment Analytics**:
   - Success rates by provider
   - Transaction volumes
   - Average transaction values
   - Geographic distribution

## System Configuration

### General Settings

1. **Platform Settings**:
   - **Site Name**: Platform branding
   - **Default Language**: System default
   - **Time Zone**: System time zone
   - **Maintenance Mode**: Enable/disable

2. **Feature Flags**:
   ```json
   {
     "features": {
       "analytics": true,
       "payments": true,
       "multi_tenant": true,
       "integrations": true,
       "notifications": true
     }
   }
   ```

### Security Configuration

1. **Authentication Settings**:
   - Password policies
   - Session timeouts
   - MFA requirements
   - Login attempt limits

2. **API Security**:
   - Rate limiting configuration
   - CORS settings
   - API key management
   - Webhook security

### Integration Management

#### LinkedIn Integration
- **OAuth Configuration**: Client ID and secret
- **Lead Notifications**: Webhook endpoint
- **Data Sync**: Automatic profile synchronization

#### OID System Integration
- **Connection Status**: Real-time status
- **Data Synchronization**: Automatic product sync
- **API Endpoints**: Integration endpoints

## Monitoring and Maintenance

### System Health

1. **Health Checks**:
   - Database connectivity
   - Redis cache status
   - External API status
   - Storage availability

2. **Performance Metrics**:
   - Response times
   - Error rates
   - Resource utilization
   - Queue processing

### Backup and Recovery

1. **Database Backups**:
   - Automated daily backups
   - Point-in-time recovery
   - Cross-region replication
   - Backup verification

2. **Application Backups**:
   - Configuration backups
   - Media file backups
   - Code repository backups
   - Recovery procedures

## Help and Support

### Common Tasks

#### Password Reset for Users
1. Navigate to **Users** → Find user
2. Click **Reset Password**
3. Send reset email or set temporary password

#### Refund Processing
1. Navigate to **Payments** → Find transaction
2. Click **Process Refund**
3. Enter refund amount and reason
4. Confirm refund processing

#### Tenant Suspension
1. Navigate to **Tenants** → Select tenant
2. Change status to **Suspended**
3. Add suspension reason
4. Notify tenant administrators

### Troubleshooting

#### Common Issues
- **Login Problems**: Check user status and permissions
- **Payment Failures**: Verify payment provider configuration
- **Data Sync Issues**: Check integration status and logs
- **Performance Issues**: Monitor system resources

#### Support Resources
- **Documentation**: [docs.brainsait.io](https://docs.brainsait.io)
- **Support Portal**: [support.brainsait.io](https://support.brainsait.io)
- **Emergency Contact**: support@brainsait.io
- **Status Page**: [status.brainsait.io](https://status.brainsait.io)

## Next Steps

- [API Integration Guide](../integration/README.md)
- [Security Best Practices](../security/README.md)
- [Developer Documentation](../development/README.md)
- [System Architecture](../architecture/README.md)