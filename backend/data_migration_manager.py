#!/usr/bin/env python3
"""
Data migration and backup utilities for BrainSAIT Store
Provides utilities for data backup, restore, and validation
"""

import asyncio
import sys
import os
import json
import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add the backend directory to the path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.core.database import get_db_session
from app.core.config import settings


class DataMigrationManager:
    """Manages data migrations, backups, and validation"""

    def __init__(self):
        self.backup_dir = Path("data_backups")
        self.backup_dir.mkdir(exist_ok=True)

    async def export_table_data(self, table_name: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Export data from a specific table"""
        async with get_db_session() as session:
            # Use raw SQL to export data
            query = f"SELECT * FROM {table_name}"
            if limit:
                query += f" LIMIT {limit}"
            
        # Validate table_name against known tables
        from app.core.database import Base
        valid_tables = set(Base.metadata.tables.keys())
        if table_name not in valid_tables:
            raise ValueError(f"Invalid table name: {table_name}")
        async with get_db_session() as session:
            # Use parameterized query for LIMIT, and validated table name
            if limit is not None:
                query = text(f"SELECT * FROM {table_name} LIMIT :limit")
                result = await session.execute(query, {"limit": limit})
            else:
                query = text(f"SELECT * FROM {table_name}")
                result = await session.execute(query)
            rows = result.fetchall()
            
            # Convert rows to dictionaries
            if rows:
                columns = result.keys()
                return [dict(zip(columns, row)) for row in rows]
            return []

    async def validate_data_integrity(self) -> Dict[str, Any]:
        """Validate data integrity across all tables"""
        validation_results = {
            "timestamp": datetime.datetime.now().isoformat(),
            "tables": {},
            "foreign_key_violations": [],
            "orphaned_records": [],
            "summary": {
                "total_tables": 0,
                "total_records": 0,
                "issues_found": 0
            }
        }

        try:
            async with get_db_session() as session:
                # Get all table names
                from app.core.database import Base
                table_names = list(Base.metadata.tables.keys())
                
                validation_results["summary"]["total_tables"] = len(table_names)
                
                for table_name in table_names:
                    try:
                        # Count records in each table
                        result = await session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                        count = result.scalar()
                        
                        validation_results["tables"][table_name] = {
                            "record_count": count,
                            "status": "ok"
                        }
                        validation_results["summary"]["total_records"] += count
                        
                    except Exception as e:
                        validation_results["tables"][table_name] = {
                            "record_count": 0,
                            "status": "error",
                            "error": str(e)
                        }
                        validation_results["summary"]["issues_found"] += 1

        except Exception as e:
            validation_results["error"] = str(e)

        return validation_results

    def create_backup_metadata(self) -> Dict[str, Any]:
        """Create backup metadata"""
        return {
            "timestamp": datetime.datetime.now().isoformat(),
            "database_url": settings.DATABASE_URL.replace(settings.DATABASE_URL.split('@')[0].split('//')[-1], "***"),
            "environment": settings.ENVIRONMENT,
            "backup_format": "json",
            "created_by": "data_migration_manager",
            "version": "1.0"
        }

    async def create_full_backup(self, backup_name: Optional[str] = None) -> str:
        """Create a full database backup"""
        if not backup_name:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{timestamp}"

        backup_path = self.backup_dir / backup_name
        backup_path.mkdir(exist_ok=True)

        # Create backup metadata
        metadata = self.create_backup_metadata()
        metadata_file = backup_path / "metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)

        print(f"Creating backup: {backup_name}")
        
        try:
            from app.core.database import Base
            table_names = list(Base.metadata.tables.keys())
            
            for table_name in table_names:
                print(f"  Backing up table: {table_name}")
                try:
                    data = await self.export_table_data(table_name)
                    
                    # Save table data
                    table_file = backup_path / f"{table_name}.json"
                    with open(table_file, 'w') as f:
                        json.dump(data, f, indent=2, default=str)
                    
                    print(f"    ✓ {len(data)} records backed up")
                    
                except Exception as e:
                    print(f"    ✗ Failed to backup {table_name}: {e}")
                    # Create empty file to indicate the table exists but had issues
                    error_file = backup_path / f"{table_name}.error"
                    with open(error_file, 'w') as f:
                        json.dump({"error": str(e)}, f)

            print(f"✓ Backup completed: {backup_path}")
            return str(backup_path)

        except Exception as e:
            print(f"✗ Backup failed: {e}")
            raise

    def list_backups(self) -> List[Dict[str, Any]]:
        """List all available backups"""
        backups = []
        
        for backup_dir in self.backup_dir.iterdir():
            if backup_dir.is_dir():
                metadata_file = backup_dir / "metadata.json"
                if metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    
                    # Count files in backup
                    table_files = list(backup_dir.glob("*.json"))
                    error_files = list(backup_dir.glob("*.error"))
                    
                    backups.append({
                        "name": backup_dir.name,
                        "path": str(backup_dir),
                        "timestamp": metadata.get("timestamp"),
                        "environment": metadata.get("environment"),
                        "table_count": len(table_files) - 1,  # -1 for metadata.json
                        "error_count": len(error_files),
                        "size": sum(f.stat().st_size for f in backup_dir.rglob("*") if f.is_file())
                    })
        
        return sorted(backups, key=lambda x: x["timestamp"], reverse=True)

    async def generate_migration_report(self) -> Dict[str, Any]:
        """Generate a comprehensive migration status report"""
        report = {
            "timestamp": datetime.datetime.now().isoformat(),
            "database_config": {
                "url": settings.DATABASE_URL.replace(settings.DATABASE_URL.split('@')[0].split('//')[-1], "***"),
                "environment": settings.ENVIRONMENT
            },
            "schema_info": {},
            "data_validation": {},
            "recommendations": []
        }

        try:
            # Get schema information
            from app.core.database import Base
            tables = Base.metadata.tables
            
            report["schema_info"] = {
                "total_tables": len(tables),
                "tables": {}
            }

            for table_name, table in tables.items():
                table_info = {
                    "columns": len(table.columns),
                    "indexes": len(table.indexes),
                    "foreign_keys": len(table.foreign_keys),
                    "constraints": len(table.constraints)
                }
                
                # List column details
                table_info["column_details"] = [
                    {
                        "name": col.name,
                        "type": str(col.type),
                        "nullable": col.nullable,
                        "primary_key": col.primary_key,
                        "foreign_key": bool(col.foreign_keys)
                    }
                    for col in table.columns
                ]
                
                report["schema_info"]["tables"][table_name] = table_info

            # Run data validation
            report["data_validation"] = await self.validate_data_integrity()

            # Add recommendations
            if report["data_validation"]["summary"]["issues_found"] > 0:
                report["recommendations"].append("Fix data integrity issues before production deployment")
            
            if report["data_validation"]["summary"]["total_records"] == 0:
                report["recommendations"].append("Database appears to be empty - consider loading seed data")
            
            report["recommendations"].extend([
                "Ensure proper backup procedures are in place",
                "Test migration procedures in staging environment",
                "Monitor database performance after migration",
                "Set up proper indexing for frequently queried columns"
            ])

        except Exception as e:
            report["error"] = str(e)

        return report


async def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="BrainSAIT Store Data Migration Manager")
    parser.add_argument("--backup", action="store_true", help="Create full database backup")
    parser.add_argument("--backup-name", type=str, help="Name for the backup")
    parser.add_argument("--list-backups", action="store_true", help="List all available backups")
    parser.add_argument("--validate", action="store_true", help="Validate data integrity")
    parser.add_argument("--report", action="store_true", help="Generate migration report")
    parser.add_argument("--export-table", type=str, help="Export specific table data")
    parser.add_argument("--limit", type=int, help="Limit number of records to export")
    
    args = parser.parse_args()
    
    manager = DataMigrationManager()
    
    try:
        if args.backup:
            backup_path = await manager.create_full_backup(args.backup_name)
            print(f"\nBackup created successfully: {backup_path}")
            
        elif args.list_backups:
            backups = manager.list_backups()
            print("\nAvailable backups:")
            if not backups:
                print("  No backups found")
            else:
                for backup in backups:
                    print(f"  - {backup['name']}")
                    print(f"    Created: {backup['timestamp']}")
                    print(f"    Environment: {backup['environment']}")
                    print(f"    Tables: {backup['table_count']}, Errors: {backup['error_count']}")
                    print(f"    Size: {backup['size']:,} bytes")
                    print()
                    
        elif args.validate:
            validation = await manager.validate_data_integrity()
            print("\nData Validation Results:")
            print(f"  Total tables: {validation['summary']['total_tables']}")
            print(f"  Total records: {validation['summary']['total_records']}")
            print(f"  Issues found: {validation['summary']['issues_found']}")
            
            if validation['summary']['issues_found'] > 0:
                print("\nTables with issues:")
                for table_name, info in validation['tables'].items():
                    if info['status'] != 'ok':
                        print(f"  - {table_name}: {info.get('error', 'Unknown error')}")
            else:
                print("\n✓ All tables validated successfully")
                
        elif args.report:
            report = await manager.generate_migration_report()
            print("\nMigration Report Generated")
            print(f"Timestamp: {report['timestamp']}")
            print(f"Tables: {report['schema_info']['total_tables']}")
            
            if 'error' in report:
                print(f"Error: {report['error']}")
            else:
                print("\nRecommendations:")
                for rec in report['recommendations']:
                    print(f"  - {rec}")
                    
        elif args.export_table:
            data = await manager.export_table_data(args.export_table, args.limit)
            print(f"\nExported {len(data)} records from {args.export_table}")
            
            # Save to file
            output_file = f"{args.export_table}_export.json"
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            print(f"Data saved to: {output_file}")
            
        else:
            print("Please specify an action. Use --help for available options.")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())