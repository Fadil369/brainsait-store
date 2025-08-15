# Database Migration System Documentation

This document provides comprehensive documentation for the BrainSAIT Store database migration system.

## Overview

The database migration system is built using Alembic and SQLAlchemy, providing a robust and versioned approach to database schema management. The system supports:

- **Automated schema migrations**
- **Data backup and restore procedures**
- **Database performance monitoring**
- **Data integrity validation**
- **Multi-environment support**

## Quick Start

### Prerequisites

1. PostgreSQL database server running
2. Python dependencies installed (`pip install -r requirements.txt`)
3. Database connection configured in `app/core/config.py`

### Basic Commands

```bash
# Validate database models
python db_manager.py --validate

# Create a new migration
python db_manager.py --create-migration "Description of changes"

# Apply migrations
python db_manager.py --upgrade

# Check migration status
python db_manager.py --status

# Create data backup
python data_migration_manager.py --backup

# Validate data integrity
python data_migration_manager.py --validate
```

## Database Schema

### Core Tables

The system includes 36 tables organized into the following categories:

#### User Management
- `users` - User accounts and profiles
- `user_sessions` - User authentication sessions
- `user_preferences` - User-specific settings
- `user_payment_methods` - Saved payment methods

#### Product Catalog
- `products` - Product information
- `categories` - Product categories
- `brands` - Product brands
- `product_variants` - Product variations
- `product_reviews` - Customer reviews

#### Order Management
- `orders` - Customer orders
- `order_items` - Order line items
- `cart_items` - Shopping cart contents
- `order_status_history` - Order status tracking

#### Payment Processing
- `payments` - Payment transactions
- `payment_refunds` - Refund records
- `payment_webhooks` - Payment provider webhooks
- `payment_audit_logs` - Payment audit trail
- `payment_reconciliations` - Payment reconciliation
- `fraud_detection_logs` - Fraud detection records

#### Invoicing & Compliance
- `invoices` - Tax invoices
- `invoice_line_items` - Invoice details
- `zatca_submissions` - ZATCA compliance records
- `invoice_sequences` - Invoice numbering

#### Analytics
- `analytics_events` - Event tracking
- `product_analytics` - Product performance metrics
- `user_behavior_analytics` - User behavior data
- `business_metrics` - Business KPIs
- `retention_analytics` - Customer retention data

#### SSO & Authentication
- `tenant_sso` - SSO configuration
- `sso_sessions` - SSO sessions
- `sso_user_mappings` - User identity mapping
- `sso_audit_logs` - SSO audit trail

## Migration Management

### Creating Migrations

#### Automatic Migration Generation

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Add new analytics tables"
```

#### Manual Migration Creation

```bash
# Create empty migration template
alembic revision -m "Custom data migration"
```

### Migration Structure

```python
"""Migration template

Revision ID: abc123
Revises: def456
Create Date: 2024-01-01 12:00:00.000000
"""

def upgrade() -> None:
    # Migration code here
    pass

def downgrade() -> None:
    # Rollback code here
    pass
```

### Best Practices

1. **Always review auto-generated migrations** before applying
2. **Test migrations in staging** before production
3. **Include data migrations** when schema changes affect existing data
4. **Document complex migrations** with clear comments
5. **Create rollback procedures** for critical changes

## Data Backup & Recovery

### Automated Backups

```bash
# Create full database backup
python data_migration_manager.py --backup

# Create named backup
python data_migration_manager.py --backup --backup-name "pre_v2_migration"

# List all backups
python data_migration_manager.py --list-backups
```

### Backup Structure

```
data_backups/
├── backup_20240101_120000/
│   ├── metadata.json          # Backup metadata
│   ├── users.json            # User data
│   ├── products.json         # Product data
│   └── ...                   # Other tables
└── pre_v2_migration/
    └── ...
```

### Data Validation

```bash
# Validate data integrity
python data_migration_manager.py --validate

# Generate migration report
python data_migration_manager.py --report

# Export specific table
python data_migration_manager.py --export-table users --limit 100
```

## Performance Optimization

### Indexing Strategy

The system includes optimized indexes for:

#### User Tables
- `idx_users_tenant_email` - Tenant-scoped email lookup
- `idx_users_status` - User status filtering
- `idx_users_role` - Role-based queries

#### Product Tables
- `idx_products_tenant_category` - Category browsing
- `idx_products_search` - Full-text search
- `idx_products_price` - Price range queries

#### Order Tables
- `idx_orders_user_status` - User order history
- `idx_orders_date_range` - Date range queries
- `idx_orders_payment_status` - Payment tracking

#### Analytics Tables
- `idx_analytics_tenant_date` - Time-series queries
- `idx_analytics_event_type` - Event filtering
- `idx_analytics_user_session` - User journey tracking

### Query Optimization Guidelines

1. **Use tenant-aware queries** for multi-tenant isolation
2. **Leverage composite indexes** for complex filters
3. **Implement query pagination** for large datasets
4. **Monitor slow query logs** regularly
5. **Use appropriate data types** for better performance

## Security Considerations

### Data Protection

1. **Audit Logging** - All critical operations are logged
2. **Encryption at Rest** - Sensitive data encrypted in database
3. **Access Controls** - Row-level security for tenant isolation
4. **Backup Encryption** - Backup files are encrypted

### Migration Security

1. **Review all migrations** before deployment
2. **Test in isolated environments** first
3. **Backup before major changes**
4. **Use least-privilege database accounts**

## Multi-Environment Setup

### Development
```bash
# Local development with SQLite
export DATABASE_URL="sqlite:///./dev.db"
alembic upgrade head
```

### Staging
```bash
# Staging environment
export DATABASE_URL="postgresql://user:pass@staging-db:5432/brainsait_staging"
alembic upgrade head
```

### Production
```bash
# Production deployment
export DATABASE_URL="postgresql://user:pass@prod-db:5432/brainsait_prod"
alembic upgrade head
```

## Troubleshooting

### Common Issues

#### Migration Conflicts
```bash
# Check current revision
alembic current

# View migration history
alembic history

# Resolve conflicts by merging
alembic merge -m "Merge conflicting revisions" head1 head2
```

#### Database Connection Issues
```bash
# Test database connection
python db_manager.py --validate

# Check configuration
python -c "from app.core.config import settings; print(settings.DATABASE_URL)"
```

#### Performance Issues
```bash
# Analyze query performance
python data_migration_manager.py --report

# Check index usage
EXPLAIN ANALYZE SELECT * FROM products WHERE tenant_id = 'xxx';
```

### Recovery Procedures

#### Schema Recovery
1. Identify the last known good migration
2. Rollback to that revision: `alembic downgrade <revision>`
3. Fix the issue and create new migration
4. Apply the corrected migration

#### Data Recovery
1. Stop application services
2. Restore from latest backup
3. Apply any missing migrations
4. Validate data integrity
5. Restart services

## Monitoring & Maintenance

### Regular Maintenance Tasks

1. **Weekly**: Review migration logs and performance metrics
2. **Monthly**: Validate data integrity and optimize queries
3. **Quarterly**: Archive old data and update indexes
4. **Annually**: Review security and backup procedures

### Monitoring Metrics

- Migration execution time
- Database size growth
- Query performance trends
- Error rates and types
- Backup success rates

## API Integration

The migration system integrates with the FastAPI application through:

```python
# app/core/database.py
from app.core.database import init_db

# Initialize database on startup
await init_db()
```

### Health Checks

```python
# Database health check endpoint
@app.get("/health/database")
async def database_health():
    try:
        async with get_db_session() as session:
            await session.execute("SELECT 1")
        return {"status": "healthy"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

## Future Enhancements

### Planned Features

1. **Automated backup scheduling**
2. **Real-time migration monitoring**
3. **Database sharding support**
4. **Advanced analytics dashboards**
5. **Integration with CI/CD pipelines**

### Scalability Considerations

1. **Read replicas** for analytics queries
2. **Connection pooling** optimization
3. **Query result caching**
4. **Horizontal partitioning** for large tables

## Support & Resources

### Documentation
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

### Scripts and Tools
- `db_manager.py` - Database management utilities
- `data_migration_manager.py` - Data backup and validation
- `alembic/` - Migration files and configuration

### Contact Information
For technical support with the migration system, please contact the development team or create an issue in the project repository.