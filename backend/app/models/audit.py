"""
Audit logging models for security monitoring
"""

from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class AuditEventType(str, Enum):
    # Authentication events
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILED = "login_failed"
    LOGOUT = "logout"
    PASSWORD_CHANGE = "password_change"
    MFA_ENABLED = "mfa_enabled"
    MFA_DISABLED = "mfa_disabled"
    ACCOUNT_LOCKED = "account_locked"
    ACCOUNT_UNLOCKED = "account_unlocked"
    
    # Authorization events
    ACCESS_GRANTED = "access_granted"
    ACCESS_DENIED = "access_denied"
    PERMISSION_CHANGED = "permission_changed"
    ROLE_ASSIGNED = "role_assigned"
    ROLE_REMOVED = "role_removed"
    
    # Data events
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXPORT = "export"
    IMPORT = "import"
    
    # File events
    FILE_UPLOAD = "file_upload"
    FILE_DOWNLOAD = "file_download"
    FILE_DELETE = "file_delete"
    
    # System events
    CONFIG_CHANGE = "config_change"
    BACKUP_CREATED = "backup_created"
    BACKUP_RESTORED = "backup_restored"
    
    # Security events
    SECURITY_SCAN = "security_scan"
    VULNERABILITY_DETECTED = "vulnerability_detected"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"


class AuditSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AuditLog(Base):
    """
    Comprehensive audit log for all system activities
    """
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Event information
    event_type = Column(String(50), nullable=False, index=True)
    severity = Column(String(20), default=AuditSeverity.MEDIUM, index=True)
    resource_type = Column(String(50), nullable=False, index=True)
    resource_id = Column(String(255), index=True)
    action = Column(String(100), nullable=False)
    description = Column(Text)
    
    # User and tenant context
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    tenant_id = Column(String(50), index=True)
    
    # Request context
    ip_address = Column(String(45), index=True)
    user_agent = Column(Text)
    request_id = Column(String(255), index=True)
    session_id = Column(String(255), index=True)
    
    # Result and details
    success = Column(Boolean, nullable=False, default=True, index=True)
    error_message = Column(Text)
    details = Column(JSON)  # Additional structured data
    
    # Changes tracking
    old_values = Column(JSON)  # Before state
    new_values = Column(JSON)  # After state
    
    # Timing
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    processing_time = Column(Integer)  # milliseconds
    
    # Compliance and retention
    retention_period = Column(Integer, default=2555)  # days (7 years default)
    is_sensitive = Column(Boolean, default=False, index=True)
    compliance_tags = Column(JSON)  # For regulatory compliance
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    
    # Indexes for performance
    __table_args__ = (
        Index('ix_audit_logs_user_timestamp', 'user_id', 'timestamp'),
        Index('ix_audit_logs_tenant_timestamp', 'tenant_id', 'timestamp'),
        Index('ix_audit_logs_event_timestamp', 'event_type', 'timestamp'),
        Index('ix_audit_logs_resource_timestamp', 'resource_type', 'resource_id', 'timestamp'),
        Index('ix_audit_logs_ip_timestamp', 'ip_address', 'timestamp'),
        Index('ix_audit_logs_severity_timestamp', 'severity', 'timestamp'),
    )


class SecurityEvent(Base):
    """
    Specific security events for threat monitoring
    """
    __tablename__ = "security_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Event classification
    event_type = Column(String(50), nullable=False, index=True)
    severity = Column(String(20), nullable=False, index=True)
    risk_score = Column(Integer, default=0, index=True)  # 0-100
    
    # Event details
    title = Column(String(255), nullable=False)
    description = Column(Text)
    indicators = Column(JSON)  # IOCs, patterns, etc.
    
    # Context
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    tenant_id = Column(String(50), index=True)
    ip_address = Column(String(45), index=True)
    user_agent = Column(Text)
    
    # Detection and response
    detection_method = Column(String(100))  # rule, ml, manual, etc.
    false_positive = Column(Boolean, default=False, index=True)
    resolved = Column(Boolean, default=False, index=True)
    resolved_at = Column(DateTime)
    resolved_by = Column(Integer, ForeignKey("users.id"))
    resolution_notes = Column(Text)
    
    # Timing
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    first_seen = Column(DateTime)
    last_seen = Column(DateTime)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    resolver = relationship("User", foreign_keys=[resolved_by])
    
    # Indexes
    __table_args__ = (
        Index('ix_security_events_unresolved', 'resolved', 'severity', 'timestamp'),
        Index('ix_security_events_risk_score', 'risk_score', 'timestamp'),
        Index('ix_security_events_user_timestamp', 'user_id', 'timestamp'),
    )


class LoginAttempt(Base):
    """
    Track all login attempts for security analysis
    """
    __tablename__ = "login_attempts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Attempt details
    email = Column(String(255), nullable=False, index=True)
    success = Column(Boolean, nullable=False, index=True)
    failure_reason = Column(String(100))  # invalid_password, account_locked, etc.
    
    # Authentication method
    auth_method = Column(String(50), default="password")  # password, sso, mfa, etc.
    mfa_used = Column(Boolean, default=False)
    
    # Context
    ip_address = Column(String(45), nullable=False, index=True)
    user_agent = Column(Text)
    country = Column(String(10))  # Country code
    city = Column(String(100))
    
    # Device fingerprinting
    device_fingerprint = Column(String(255))
    browser_fingerprint = Column(String(255))
    
    # Session information
    session_id = Column(String(255))
    tenant_id = Column(String(50), index=True)
    
    # Timing
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Risk assessment
    risk_score = Column(Integer, default=0)  # 0-100
    suspicious = Column(Boolean, default=False, index=True)
    
    # Indexes
    __table_args__ = (
        Index('ix_login_attempts_email_timestamp', 'email', 'timestamp'),
        Index('ix_login_attempts_ip_timestamp', 'ip_address', 'timestamp'),
        Index('ix_login_attempts_failed', 'success', 'timestamp'),
        Index('ix_login_attempts_suspicious', 'suspicious', 'timestamp'),
    )


class DataAccess(Base):
    """
    Track access to sensitive data
    """
    __tablename__ = "data_access_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Access details
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    resource_type = Column(String(50), nullable=False, index=True)
    resource_id = Column(String(255), nullable=False, index=True)
    action = Column(String(50), nullable=False)  # read, write, delete, export
    
    # Data classification
    data_sensitivity = Column(String(20), default="internal")  # public, internal, confidential, restricted
    pii_accessed = Column(Boolean, default=False, index=True)
    compliance_scope = Column(JSON)  # GDPR, HIPAA, PCI, etc.
    
    # Context
    ip_address = Column(String(45), index=True)
    user_agent = Column(Text)
    tenant_id = Column(String(50), index=True)
    
    # Request details
    request_method = Column(String(10))
    request_path = Column(String(500))
    query_parameters = Column(JSON)
    
    # Response details
    records_accessed = Column(Integer, default=0)
    data_exported = Column(Boolean, default=False, index=True)
    export_format = Column(String(20))
    
    # Timing
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Legal hold and retention
    legal_hold = Column(Boolean, default=False, index=True)
    retention_date = Column(DateTime)
    
    # Relationships
    user = relationship("User")
    
    # Indexes
    __table_args__ = (
        Index('ix_data_access_user_timestamp', 'user_id', 'timestamp'),
        Index('ix_data_access_resource', 'resource_type', 'resource_id'),
        Index('ix_data_access_pii', 'pii_accessed', 'timestamp'),
        Index('ix_data_access_export', 'data_exported', 'timestamp'),
        Index('ix_data_access_sensitive', 'data_sensitivity', 'timestamp'),
    )


class FileActivity(Base):
    """
    Track file upload, download, and modification activities
    """
    __tablename__ = "file_activities"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # File details
    file_path = Column(String(1000), nullable=False)
    file_name = Column(String(255), nullable=False, index=True)
    file_size = Column(Integer)
    file_hash = Column(String(128), index=True)  # SHA-256
    mime_type = Column(String(100))
    
    # Activity details
    activity_type = Column(String(20), nullable=False, index=True)  # upload, download, delete, modify
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Security scanning
    virus_scan_result = Column(String(20))  # clean, infected, error
    malware_detected = Column(Boolean, default=False, index=True)
    scan_engine = Column(String(50))
    
    # Context
    ip_address = Column(String(45), index=True)
    user_agent = Column(Text)
    tenant_id = Column(String(50), index=True)
    
    # Classification
    file_classification = Column(String(20), default="internal")
    contains_pii = Column(Boolean, default=False, index=True)
    
    # Timing
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = relationship("User")
    
    # Indexes
    __table_args__ = (
        Index('ix_file_activities_user_timestamp', 'user_id', 'timestamp'),
        Index('ix_file_activities_malware', 'malware_detected', 'timestamp'),
        Index('ix_file_activities_type', 'activity_type', 'timestamp'),
    )