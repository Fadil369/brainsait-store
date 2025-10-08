"""Add field sales tables

Revision ID: add_field_sales_001
Revises: 9ff80080f0c4
Create Date: 2025-12-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_field_sales_001'
down_revision = '9ff80080f0c4'
branch_labels = None
depends_on = None


def upgrade():
    # Create sales_reps table
    op.create_table(
        'sales_reps',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('tenant_id', sa.String(50), nullable=False, index=True),
        sa.Column('rep_code', sa.String(20), nullable=False, unique=True, index=True),
        sa.Column('territory', sa.String(100), nullable=True),
        sa.Column('manager_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('sales_reps.id'), nullable=True),
        sa.Column('status', sa.Enum('active', 'inactive', 'on_leave', 'suspended', name='salesrepstatus'), nullable=False),
        sa.Column('monthly_target', sa.Numeric(12, 2), nullable=False, server_default='0'),
        sa.Column('current_month_sales', sa.Numeric(12, 2), nullable=False, server_default='0'),
        sa.Column('total_sales', sa.Numeric(12, 2), nullable=False, server_default='0'),
        sa.Column('commission_rate', sa.Float, nullable=False, server_default='0.05'),
        sa.Column('total_commission', sa.Numeric(12, 2), nullable=False, server_default='0'),
        sa.Column('points', sa.Integer, nullable=False, server_default='0'),
        sa.Column('level', sa.Integer, nullable=False, server_default='1'),
        sa.Column('badges', postgresql.JSON, nullable=True),
        sa.Column('achievements', postgresql.JSON, nullable=True),
        sa.Column('csat_score', sa.Float, nullable=True),
        sa.Column('total_visits', sa.Integer, nullable=False, server_default='0'),
        sa.Column('successful_visits', sa.Integer, nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.Column('last_active_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('idx_sales_reps_tenant_code', 'sales_reps', ['tenant_id', 'rep_code'], unique=True)
    op.create_index('idx_sales_reps_status', 'sales_reps', ['status'])
    op.create_index('idx_sales_reps_territory', 'sales_reps', ['territory'])

    # Create outlet_checkins table
    op.create_table(
        'outlet_checkins',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('sales_rep_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('sales_reps.id'), nullable=False),
        sa.Column('tenant_id', sa.String(50), nullable=False, index=True),
        sa.Column('outlet_name', sa.String(255), nullable=False),
        sa.Column('outlet_id', sa.String(100), nullable=True, index=True),
        sa.Column('latitude', sa.Float, nullable=False),
        sa.Column('longitude', sa.Float, nullable=False),
        sa.Column('address', sa.Text, nullable=True),
        sa.Column('geofence_verified', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('distance_from_outlet', sa.Float, nullable=True),
        sa.Column('photo_url', sa.String(500), nullable=True),
        sa.Column('photo_metadata', postgresql.JSON, nullable=True),
        sa.Column('check_in_time', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('check_out_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('duration_minutes', sa.Integer, nullable=True),
        sa.Column('status', sa.Enum('pending', 'approved', 'rejected', name='checkinstatus'), nullable=False),
        sa.Column('visit_notes', sa.Text, nullable=True),
        sa.Column('products_discussed', postgresql.JSON, nullable=True),
        sa.Column('orders_placed', postgresql.JSON, nullable=True),
        sa.Column('device_info', postgresql.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )
    op.create_index('idx_checkins_rep_date', 'outlet_checkins', ['sales_rep_id', 'check_in_time'])
    op.create_index('idx_checkins_outlet', 'outlet_checkins', ['outlet_id'])
    op.create_index('idx_checkins_status', 'outlet_checkins', ['status'])

    # Create voice_orders table
    op.create_table(
        'voice_orders',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('sales_rep_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('sales_reps.id'), nullable=False),
        sa.Column('tenant_id', sa.String(50), nullable=False, index=True),
        sa.Column('audio_url', sa.String(500), nullable=True),
        sa.Column('audio_duration_seconds', sa.Integer, nullable=True),
        sa.Column('language', sa.String(5), nullable=False, server_default='ar'),
        sa.Column('raw_transcription', sa.Text, nullable=True),
        sa.Column('processed_text', sa.Text, nullable=True),
        sa.Column('confidence_score', sa.Float, nullable=True),
        sa.Column('extracted_products', postgresql.JSON, nullable=True),
        sa.Column('extracted_customer', postgresql.JSON, nullable=True),
        sa.Column('order_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('processing_status', sa.Enum('pending', 'processing', 'completed', 'failed', name='processingstatus'), nullable=False, server_default='pending'),
        sa.Column('error_message', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('idx_voice_orders_rep', 'voice_orders', ['sales_rep_id'])
    op.create_index('idx_voice_orders_status', 'voice_orders', ['processing_status'])

    # Create credit_requests table
    op.create_table(
        'credit_requests',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('sales_rep_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('sales_reps.id'), nullable=False),
        sa.Column('tenant_id', sa.String(50), nullable=False, index=True),
        sa.Column('customer_name', sa.String(255), nullable=False),
        sa.Column('customer_email', sa.String(255), nullable=True),
        sa.Column('customer_phone', sa.String(20), nullable=False),
        sa.Column('customer_business', sa.String(255), nullable=True),
        sa.Column('requested_amount', sa.Numeric(12, 2), nullable=False),
        sa.Column('credit_term_days', sa.Integer, nullable=False, server_default='30'),
        sa.Column('purpose', sa.Text, nullable=True),
        sa.Column('ai_score', sa.Float, nullable=True),
        sa.Column('ai_recommendation', sa.String(20), nullable=True),
        sa.Column('risk_factors', postgresql.JSON, nullable=True),
        sa.Column('ai_analysis', postgresql.JSON, nullable=True),
        sa.Column('status', sa.Enum('pending', 'approved', 'rejected', 'expired', name='creditstatus'), nullable=False),
        sa.Column('approved_amount', sa.Numeric(12, 2), nullable=True),
        sa.Column('approved_term_days', sa.Integer, nullable=True),
        sa.Column('decision_notes', sa.Text, nullable=True),
        sa.Column('decided_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('decided_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('idx_credit_requests_rep', 'credit_requests', ['sales_rep_id'])
    op.create_index('idx_credit_requests_status', 'credit_requests', ['status'])
    op.create_index('idx_credit_requests_customer', 'credit_requests', ['customer_phone'])

    # Create leaderboards table
    op.create_table(
        'leaderboards',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('sales_rep_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('sales_reps.id'), nullable=False),
        sa.Column('tenant_id', sa.String(50), nullable=False, index=True),
        sa.Column('period_type', sa.String(20), nullable=False),
        sa.Column('period_start', sa.DateTime(timezone=True), nullable=False),
        sa.Column('period_end', sa.DateTime(timezone=True), nullable=False),
        sa.Column('total_sales', sa.Numeric(12, 2), nullable=False, server_default='0'),
        sa.Column('total_orders', sa.Integer, nullable=False, server_default='0'),
        sa.Column('total_visits', sa.Integer, nullable=False, server_default='0'),
        sa.Column('points_earned', sa.Integer, nullable=False, server_default='0'),
        sa.Column('rank', sa.Integer, nullable=False),
        sa.Column('territory_rank', sa.Integer, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )
    op.create_index('idx_leaderboard_period', 'leaderboards', ['period_type', 'period_start', 'period_end'])
    op.create_index('idx_leaderboard_rank', 'leaderboards', ['rank'])

    # Create achievements table
    op.create_table(
        'achievements',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', sa.String(50), nullable=False, index=True),
        sa.Column('code', sa.String(50), nullable=False, unique=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('name_ar', sa.String(100), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('description_ar', sa.Text, nullable=True),
        sa.Column('badge_type', sa.Enum('bronze', 'silver', 'gold', 'platinum', name='badgetype'), nullable=False),
        sa.Column('badge_icon', sa.String(500), nullable=True),
        sa.Column('requirement_type', sa.String(50), nullable=False),
        sa.Column('requirement_value', sa.Integer, nullable=False),
        sa.Column('points_reward', sa.Integer, nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )
    op.create_index('idx_achievements_code', 'achievements', ['code'], unique=True)
    op.create_index('idx_achievements_type', 'achievements', ['requirement_type'])


def downgrade():
    # Drop tables in reverse order
    op.drop_table('achievements')
    op.drop_table('leaderboards')
    op.drop_table('credit_requests')
    op.drop_table('voice_orders')
    op.drop_table('outlet_checkins')
    op.drop_table('sales_reps')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS badgetype')
    op.execute('DROP TYPE IF EXISTS creditstatus')
    op.execute('DROP TYPE IF EXISTS checkinstatus')
    op.execute('DROP TYPE IF EXISTS salesrepstatus')
    op.execute('DROP TYPE IF EXISTS processingstatus')
