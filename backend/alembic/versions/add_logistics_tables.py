"""add_logistics_tables

Revision ID: add_logistics_001
Revises: 9ff80080f0c4
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_logistics_001'
down_revision = '9ff80080f0c4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum types
    op.execute("""
        CREATE TYPE driverstatus AS ENUM ('available', 'on_route', 'on_break', 'offline', 'suspended');
        CREATE TYPE vehicletype AS ENUM ('motorcycle', 'car', 'van', 'truck_small', 'truck_medium', 'truck_large');
        CREATE TYPE routestatus AS ENUM ('planned', 'in_progress', 'completed', 'cancelled', 'failed');
        CREATE TYPE deliverystatus AS ENUM ('pending', 'in_transit', 'delivered', 'failed', 'returned');
        CREATE TYPE incidenttype AS ENUM ('accident', 'vehicle_breakdown', 'traffic_delay', 'weather_delay', 'customer_unavailable', 'package_damage', 'security_issue', 'other');
        CREATE TYPE incidentseverity AS ENUM ('low', 'medium', 'high', 'critical');
    """)
    
    # Create drivers table
    op.create_table(
        'drivers',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', sa.String(100), nullable=False, index=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        
        # Personal Information
        sa.Column('driver_code', sa.String(50), unique=True, nullable=False, index=True),
        sa.Column('full_name', sa.String(200), nullable=False),
        sa.Column('phone', sa.String(20), nullable=False),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('national_id', sa.String(50), nullable=True),
        
        # License Information
        sa.Column('license_number', sa.String(100), nullable=False),
        sa.Column('license_type', sa.String(50), nullable=False),
        sa.Column('license_expiry', sa.DateTime, nullable=False),
        
        # Vehicle Information
        sa.Column('vehicle_type', postgresql.ENUM('motorcycle', 'car', 'van', 'truck_small', 'truck_medium', 'truck_large', name='vehicletype'), nullable=False),
        sa.Column('vehicle_make', sa.String(100), nullable=True),
        sa.Column('vehicle_model', sa.String(100), nullable=True),
        sa.Column('vehicle_year', sa.Integer, nullable=True),
        sa.Column('vehicle_plate', sa.String(50), nullable=False),
        sa.Column('vehicle_capacity_kg', sa.Float, nullable=True),
        sa.Column('vehicle_capacity_m3', sa.Float, nullable=True),
        
        # Status and Performance
        sa.Column('status', postgresql.ENUM('available', 'on_route', 'on_break', 'offline', 'suspended', name='driverstatus'), nullable=False, default='available'),
        sa.Column('rating', sa.Float, default=5.0),
        sa.Column('total_deliveries', sa.Integer, default=0),
        sa.Column('successful_deliveries', sa.Integer, default=0),
        
        # Safety and Compliance
        sa.Column('last_safety_training', sa.DateTime, nullable=True),
        sa.Column('last_health_check', sa.DateTime, nullable=True),
        sa.Column('fatigue_alert_count', sa.Integer, default=0),
        
        # Financial
        sa.Column('hourly_rate', sa.Float, nullable=True),
        sa.Column('per_delivery_rate', sa.Float, nullable=True),
        sa.Column('total_earnings', sa.Float, default=0.0),
        
        # Metadata
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False),
        sa.Column('is_active', sa.Boolean, default=True),
        
        # Additional data
        sa.Column('preferences', postgresql.JSON, default={}),
        sa.Column('emergency_contact', postgresql.JSON, nullable=True),
    )
    
    # Create routes table
    op.create_table(
        'routes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', sa.String(100), nullable=False, index=True),
        sa.Column('driver_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('drivers.id'), nullable=False),
        
        # Route Information
        sa.Column('route_number', sa.String(50), unique=True, nullable=False, index=True),
        sa.Column('route_name', sa.String(200), nullable=True),
        sa.Column('planned_date', sa.DateTime, nullable=False),
        
        # Route Details
        sa.Column('start_location', postgresql.JSON, nullable=False),
        sa.Column('end_location', postgresql.JSON, nullable=True),
        sa.Column('waypoints', postgresql.JSON, default=[]),
        
        # Optimization Constraints
        sa.Column('max_weight_kg', sa.Float, nullable=True),
        sa.Column('max_volume_m3', sa.Float, nullable=True),
        sa.Column('time_window_start', sa.Time, nullable=True),
        sa.Column('time_window_end', sa.Time, nullable=True),
        sa.Column('priority_deliveries', postgresql.JSON, default=[]),
        
        # Route Metrics
        sa.Column('total_distance_km', sa.Float, nullable=True),
        sa.Column('estimated_duration_min', sa.Integer, nullable=True),
        sa.Column('actual_duration_min', sa.Integer, nullable=True),
        sa.Column('total_stops', sa.Integer, default=0),
        sa.Column('completed_stops', sa.Integer, default=0),
        
        # Status
        sa.Column('status', postgresql.ENUM('planned', 'in_progress', 'completed', 'cancelled', 'failed', name='routestatus'), nullable=False, default='planned'),
        sa.Column('started_at', sa.DateTime, nullable=True),
        sa.Column('completed_at', sa.DateTime, nullable=True),
        
        # AI Optimization
        sa.Column('optimization_score', sa.Float, nullable=True),
        sa.Column('optimization_algorithm', sa.String(100), nullable=True),
        sa.Column('optimization_constraints', postgresql.JSON, default={}),
        
        # Metadata
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False),
    )
    
    # Create deliveries table
    op.create_table(
        'deliveries',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', sa.String(100), nullable=False, index=True),
        sa.Column('route_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('routes.id'), nullable=False),
        sa.Column('driver_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('drivers.id'), nullable=False),
        sa.Column('order_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('orders.id'), nullable=True),
        
        # Delivery Information
        sa.Column('tracking_number', sa.String(100), unique=True, nullable=False, index=True),
        sa.Column('sequence_number', sa.Integer, nullable=False),
        
        # Package Details
        sa.Column('package_weight_kg', sa.Float, nullable=True),
        sa.Column('package_dimensions', postgresql.JSON, nullable=True),
        sa.Column('package_description', sa.Text, nullable=True),
        sa.Column('special_instructions', sa.Text, nullable=True),
        
        # Location
        sa.Column('delivery_location', postgresql.JSON, nullable=False),
        sa.Column('delivery_contact', postgresql.JSON, nullable=False),
        
        # Time Windows
        sa.Column('estimated_arrival', sa.DateTime, nullable=True),
        sa.Column('actual_arrival', sa.DateTime, nullable=True),
        sa.Column('delivery_window_start', sa.Time, nullable=True),
        sa.Column('delivery_window_end', sa.Time, nullable=True),
        
        # Status
        sa.Column('status', postgresql.ENUM('pending', 'in_transit', 'delivered', 'failed', 'returned', name='deliverystatus'), nullable=False, default='pending'),
        sa.Column('delivered_at', sa.DateTime, nullable=True),
        
        # Proof of Delivery
        sa.Column('pod_signature', sa.String(500), nullable=True),
        sa.Column('pod_photo', sa.String(500), nullable=True),
        sa.Column('pod_gps_location', postgresql.JSON, nullable=True),
        sa.Column('pod_recipient_name', sa.String(200), nullable=True),
        sa.Column('pod_notes', sa.Text, nullable=True),
        
        # Delivery Attempt Tracking
        sa.Column('attempt_count', sa.Integer, default=0),
        sa.Column('last_attempt_at', sa.DateTime, nullable=True),
        sa.Column('failure_reason', sa.Text, nullable=True),
        
        # Metadata
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False),
    )
    
    # Create incidents table
    op.create_table(
        'incidents',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', sa.String(100), nullable=False, index=True),
        sa.Column('driver_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('drivers.id'), nullable=False),
        sa.Column('route_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('routes.id'), nullable=True),
        sa.Column('delivery_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('deliveries.id'), nullable=True),
        
        # Incident Details
        sa.Column('incident_number', sa.String(50), unique=True, nullable=False, index=True),
        sa.Column('incident_type', postgresql.ENUM('accident', 'vehicle_breakdown', 'traffic_delay', 'weather_delay', 'customer_unavailable', 'package_damage', 'security_issue', 'other', name='incidenttype'), nullable=False),
        sa.Column('severity', postgresql.ENUM('low', 'medium', 'high', 'critical', name='incidentseverity'), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text, nullable=False),
        
        # Location and Time
        sa.Column('location', postgresql.JSON, nullable=True),
        sa.Column('occurred_at', sa.DateTime, nullable=False),
        
        # Media
        sa.Column('photos', postgresql.JSON, default=[]),
        sa.Column('videos', postgresql.JSON, default=[]),
        
        # AI Analysis
        sa.Column('ai_suggested_category', sa.String(100), nullable=True),
        sa.Column('ai_suggested_actions', postgresql.JSON, default=[]),
        sa.Column('ai_confidence_score', sa.Float, nullable=True),
        
        # Resolution
        sa.Column('is_resolved', sa.Boolean, default=False),
        sa.Column('resolved_at', sa.DateTime, nullable=True),
        sa.Column('resolution_notes', sa.Text, nullable=True),
        
        # Impact
        sa.Column('estimated_delay_min', sa.Integer, nullable=True),
        sa.Column('affected_deliveries', postgresql.JSON, default=[]),
        
        # Metadata
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False),
    )
    
    # Create driver_earnings table
    op.create_table(
        'driver_earnings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', sa.String(100), nullable=False, index=True),
        sa.Column('driver_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('drivers.id'), nullable=False),
        sa.Column('route_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('routes.id'), nullable=True),
        
        # Earnings Details
        sa.Column('date', sa.DateTime, nullable=False, index=True),
        sa.Column('base_amount', sa.Float, nullable=False),
        sa.Column('bonus_amount', sa.Float, default=0.0),
        sa.Column('deduction_amount', sa.Float, default=0.0),
        sa.Column('total_amount', sa.Float, nullable=False),
        
        # Breakdown
        sa.Column('hours_worked', sa.Float, nullable=True),
        sa.Column('deliveries_completed', sa.Integer, default=0),
        sa.Column('distance_traveled_km', sa.Float, nullable=True),
        
        # Performance Bonuses
        sa.Column('on_time_bonus', sa.Float, default=0.0),
        sa.Column('rating_bonus', sa.Float, default=0.0),
        sa.Column('efficiency_bonus', sa.Float, default=0.0),
        
        # Payment Status
        sa.Column('is_paid', sa.Boolean, default=False),
        sa.Column('paid_at', sa.DateTime, nullable=True),
        sa.Column('payment_method', sa.String(50), nullable=True),
        sa.Column('payment_reference', sa.String(200), nullable=True),
        
        # Metadata
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False),
    )
    
    # Create load_plans table
    op.create_table(
        'load_plans',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', sa.String(100), nullable=False, index=True),
        sa.Column('route_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('routes.id'), nullable=False),
        
        # Vehicle Capacity
        sa.Column('vehicle_length_m', sa.Float, nullable=False),
        sa.Column('vehicle_width_m', sa.Float, nullable=False),
        sa.Column('vehicle_height_m', sa.Float, nullable=False),
        sa.Column('max_weight_kg', sa.Float, nullable=False),
        
        # Load Details
        sa.Column('items', postgresql.JSON, nullable=False),
        sa.Column('total_weight_kg', sa.Float, nullable=False),
        sa.Column('weight_utilization_pct', sa.Float, nullable=False),
        sa.Column('volume_utilization_pct', sa.Float, nullable=False),
        
        # 3D Layout
        sa.Column('layout_3d', postgresql.JSON, nullable=True),
        sa.Column('loading_sequence', postgresql.JSON, nullable=False),
        
        # Optimization
        sa.Column('optimization_score', sa.Float, nullable=True),
        sa.Column('balance_score', sa.Float, nullable=True),
        sa.Column('accessibility_score', sa.Float, nullable=True),
        
        # Metadata
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False),
    )
    
    # Create safety_alerts table
    op.create_table(
        'safety_alerts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', sa.String(100), nullable=False, index=True),
        sa.Column('driver_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('drivers.id'), nullable=False),
        
        # Alert Details
        sa.Column('alert_type', sa.String(100), nullable=False),
        sa.Column('severity', sa.String(20), nullable=False),
        sa.Column('message', sa.Text, nullable=False),
        
        # Context
        sa.Column('location', postgresql.JSON, nullable=True),
        sa.Column('triggered_at', sa.DateTime, nullable=False),
        
        # Driver Response
        sa.Column('acknowledged', sa.Boolean, default=False),
        sa.Column('acknowledged_at', sa.DateTime, nullable=True),
        sa.Column('action_taken', sa.Text, nullable=True),
        
        # Metadata
        sa.Column('alert_metadata', postgresql.JSON, default={}),
        sa.Column('created_at', sa.DateTime, nullable=False),
    )
    
    # Create indexes
    op.create_index('idx_drivers_tenant_status', 'drivers', ['tenant_id', 'status'])
    op.create_index('idx_routes_tenant_driver', 'routes', ['tenant_id', 'driver_id'])
    op.create_index('idx_deliveries_tenant_route', 'deliveries', ['tenant_id', 'route_id'])
    op.create_index('idx_incidents_tenant_driver', 'incidents', ['tenant_id', 'driver_id'])
    op.create_index('idx_earnings_driver_date', 'driver_earnings', ['driver_id', 'date'])


def downgrade() -> None:
    # Drop tables
    op.drop_table('safety_alerts')
    op.drop_table('load_plans')
    op.drop_table('driver_earnings')
    op.drop_table('incidents')
    op.drop_table('deliveries')
    op.drop_table('routes')
    op.drop_table('drivers')
    
    # Drop enum types
    op.execute("""
        DROP TYPE IF EXISTS driverstatus;
        DROP TYPE IF EXISTS vehicletype;
        DROP TYPE IF EXISTS routestatus;
        DROP TYPE IF EXISTS deliverystatus;
        DROP TYPE IF EXISTS incidenttype;
        DROP TYPE IF EXISTS incidentseverity;
    """)
