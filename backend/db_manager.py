#!/usr/bin/env python3
"""
Database management script for BrainSAIT Store
Provides utilities for database initialization, migration, and management
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to the path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.core.database import init_db, close_db
from app.core.config import settings


async def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    try:
        await init_db()
        print("✓ Database tables created successfully")
    except Exception as e:
        print(f"✗ Failed to create tables: {e}")
        return False
    return True


async def validate_models():
    """Validate that all models are properly defined"""
    print("Validating database models...")
    try:
        # Import all models to check for any issues
        from app.models import (
            users, products, orders, payments, invoices, sso, analytics
        )
        print("✓ All models imported successfully")
        
        # Check that we have the expected models
        from app.models import (
            User, Product, Order, Payment, Invoice, TenantSSO, AnalyticsEvent
        )
        print("✓ Core models available")
        
        # Check for foreign key relationships
        from app.core.database import Base
        tables = Base.metadata.tables
        print(f"✓ Found {len(tables)} tables in metadata")
        
        # List all tables
        print("\nTables that will be created:")
        for table_name in sorted(tables.keys()):
            table = tables[table_name]
            print(f"  - {table_name} ({len(table.columns)} columns)")
            
        return True
    except Exception as e:
        print(f"✗ Model validation failed: {e}")
        return False


def run_alembic_command(command: str):
    """Run an Alembic command"""
    import subprocess
    try:
        result = subprocess.run(
            ["alembic"] + command.split(),
            cwd=backend_dir,
            capture_output=True,
            text=True
        )
        print(f"Running: alembic {command}")
        if result.returncode == 0:
            print("✓ Command completed successfully")
            if result.stdout:
                print(result.stdout)
        else:
            print("✗ Command failed")
            if result.stderr:
                print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"✗ Failed to run alembic command: {e}")
        return False


def show_migration_status():
    """Show current migration status"""
    print("Migration status:")
    run_alembic_command("current")
    print("\nMigration history:")
    run_alembic_command("history")


def create_migration(message: str):
    """Create a new migration"""
    print(f"Creating migration: {message}")
    return run_alembic_command(f"revision --autogenerate -m '{message}'")


def upgrade_database():
    """Upgrade database to latest migration"""
    print("Upgrading database...")
    return run_alembic_command("upgrade head")


def downgrade_database(revision: str = "-1"):
    """Downgrade database to previous revision"""
    print(f"Downgrading database to {revision}...")
    return run_alembic_command(f"downgrade {revision}")


async def full_setup():
    """Complete database setup"""
    print("=== BrainSAIT Store Database Setup ===\n")
    
    print(f"Database URL: {settings.DATABASE_URL}")
    print(f"Environment: {settings.ENVIRONMENT}\n")
    
    # Step 1: Validate models
    if not await validate_models():
        return False
    
    print("\n" + "="*50 + "\n")
    
    # Step 2: Show migration status
    show_migration_status()
    
    print("\n" + "="*50 + "\n")
    
    # For now, since we don't have a database running, we'll just validate
    print("Database setup validation completed successfully!")
    print("\nTo complete the setup with a real database:")
    print("1. Start your PostgreSQL database")
    print("2. Run: alembic upgrade head")
    print("3. Or run: python db_manager.py --create-tables")
    
    return True


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="BrainSAIT Store Database Manager")
    parser.add_argument("--validate", action="store_true", help="Validate models only")
    parser.add_argument("--create-tables", action="store_true", help="Create all tables")
    parser.add_argument("--status", action="store_true", help="Show migration status")
    parser.add_argument("--upgrade", action="store_true", help="Upgrade to latest migration")
    parser.add_argument("--downgrade", type=str, help="Downgrade to revision")
    parser.add_argument("--create-migration", type=str, help="Create new migration")
    parser.add_argument("--full-setup", action="store_true", help="Run complete setup")
    
    args = parser.parse_args()
    
    if args.validate:
        asyncio.run(validate_models())
    elif args.create_tables:
        asyncio.run(create_tables())
    elif args.status:
        show_migration_status()
    elif args.upgrade:
        upgrade_database()
    elif args.downgrade:
        downgrade_database(args.downgrade)
    elif args.create_migration:
        create_migration(args.create_migration)
    elif args.full_setup:
        asyncio.run(full_setup())
    else:
        # Default: run full setup
        asyncio.run(full_setup())


if __name__ == "__main__":
    main()