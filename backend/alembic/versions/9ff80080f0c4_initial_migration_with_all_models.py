"""Initial migration with all models

Revision ID: 9ff80080f0c4
Revises: 
Create Date: 2025-08-15 14:07:16.584642

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9ff80080f0c4'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create initial database schema"""
    # This migration creates the complete database schema
    # Since we're setting up a new migration system, we'll create all tables at once
    
    # We'll use reflection to generate the schema from our models
    # This is a practical approach for the initial migration
    from app.core.database import Base
    # Import all models to ensure they are registered
    from app.models import users, products, orders, payments, invoices, sso, analytics
    
    # Create all tables using the metadata
    Base.metadata.create_all(bind=op.get_bind())


def downgrade() -> None:
    """Drop all database tables"""
    from app.core.database import Base
    from app.models import users, products, orders, payments, invoices, sso, analytics
    
    # Drop all tables
    Base.metadata.drop_all(bind=op.get_bind())
