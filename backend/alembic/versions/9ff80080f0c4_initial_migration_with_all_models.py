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
    # Import column/type definitions for each table
    # Define tables explicitly using op.create_table()
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('username', sa.String(length=255), nullable=False, unique=True),
        sa.Column('email', sa.String(length=255), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False),
    )
    op.create_table(
        'products',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('price', sa.Numeric(10, 2), nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False),
    )
    op.create_table(
        'orders',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
    )
    op.create_table(
        'payments',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('order_id', sa.Integer, sa.ForeignKey('orders.id'), nullable=False),
        sa.Column('amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('paid_at', sa.DateTime, nullable=True),
    )
    op.create_table(
        'invoices',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('order_id', sa.Integer, sa.ForeignKey('orders.id'), nullable=False),
        sa.Column('issued_at', sa.DateTime, nullable=False),
        sa.Column('due_date', sa.DateTime, nullable=False),
        sa.Column('amount', sa.Numeric(10, 2), nullable=False),
    )
    op.create_table(
        'sso',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=False),
        sa.Column('provider_user_id', sa.String(length=255), nullable=False),
    )
    op.create_table(
        'analytics',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=True),
        sa.Column('event', sa.String(length=255), nullable=False),
        sa.Column('timestamp', sa.DateTime, nullable=False),
    )

def downgrade() -> None:
    """Drop all database tables"""
    # Drop tables in reverse order to handle dependencies
    op.drop_table('analytics')
    op.drop_table('sso')
    op.drop_table('invoices')
    op.drop_table('payments')
    op.drop_table('orders')
    op.drop_table('products')
    op.drop_table('users')
