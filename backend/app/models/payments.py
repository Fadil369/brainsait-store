"""
Payment models for different payment methods
"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class PaymentMethod(str, enum.Enum):
    STRIPE = "stripe"
    MADA = "mada"
    STC_PAY = "stc_pay"
    BANK_TRANSFER = "bank_transfer"
    CASH_ON_DELIVERY = "cash_on_delivery"
    WALLET = "wallet"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"


class RefundStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    PROCESSED = "processed"
    REJECTED = "rejected"


class Payment(Base):
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False)
    tenant_id = Column(String(50), nullable=False, index=True)

    # Payment Information
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    status = Column(Enum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING)

    # Amount
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="SAR")

    # Payment Gateway Information
    gateway_transaction_id = Column(String(255), nullable=True, index=True)
    gateway_response = Column(JSON, nullable=True)

    # Stripe specific
    stripe_payment_intent_id = Column(String(255), nullable=True, index=True)
    stripe_charge_id = Column(String(255), nullable=True, index=True)

    # Mada specific
    mada_transaction_id = Column(String(255), nullable=True, index=True)
    mada_reference_number = Column(String(255), nullable=True)

    # STC Pay specific
    stc_pay_transaction_id = Column(String(255), nullable=True, index=True)
    stc_pay_reference = Column(String(255), nullable=True)

    # Bank Transfer specific
    bank_reference = Column(String(255), nullable=True)
    bank_name = Column(String(100), nullable=True)

    # Failure Information
    failure_reason = Column(Text, nullable=True)
    failure_code = Column(String(50), nullable=True)

    # Metadata
    payment_metadata = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    failed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    order = relationship("Order", back_populates="payments")
    refunds = relationship("PaymentRefund", back_populates="payment")

    # Indexes
    __table_args__ = (
        Index("idx_payments_order", "order_id"),
        Index("idx_payments_tenant", "tenant_id"),
        Index("idx_payments_status", "status"),
        Index("idx_payments_method", "payment_method"),
        Index("idx_payments_gateway_id", "gateway_transaction_id"),
    )

    def __repr__(self):
        return f"<Payment {self.amount} {self.currency} via {self.payment_method}>"


class PaymentRefund(Base):
    __tablename__ = "payment_refunds"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    payment_id = Column(UUID(as_uuid=True), ForeignKey("payments.id"), nullable=False)
    tenant_id = Column(String(50), nullable=False, index=True)

    # Refund Information
    amount = Column(Numeric(10, 2), nullable=False)
    reason = Column(Text, nullable=True)
    status = Column(Enum(RefundStatus), nullable=False, default=RefundStatus.PENDING)

    # Gateway Information
    gateway_refund_id = Column(String(255), nullable=True, index=True)
    gateway_response = Column(JSON, nullable=True)

    # Processing Information
    processed_by_user_id = Column(UUID(as_uuid=True), nullable=True)
    rejection_reason = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    payment = relationship("Payment", back_populates="refunds")

    # Indexes
    __table_args__ = (
        Index("idx_payment_refunds_payment", "payment_id"),
        Index("idx_payment_refunds_tenant", "tenant_id"),
        Index("idx_payment_refunds_status", "status"),
    )

    def __repr__(self):
        return f"<PaymentRefund {self.amount}>"


class PaymentWebhook(Base):
    __tablename__ = "payment_webhooks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(String(50), nullable=False, index=True)

    # Webhook Information
    provider = Column(String(50), nullable=False)  # stripe, mada, stc_pay
    event_type = Column(String(100), nullable=False)
    webhook_id = Column(String(255), nullable=True, index=True)

    # Payload
    payload = Column(JSON, nullable=False)
    headers = Column(JSON, nullable=True)

    # Processing
    processed = Column(Boolean, nullable=False, default=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    processing_error = Column(Text, nullable=True)
    retry_count = Column(Integer, nullable=False, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Indexes
    __table_args__ = (
        Index("idx_payment_webhooks_tenant", "tenant_id"),
        Index("idx_payment_webhooks_provider", "provider"),
        Index("idx_payment_webhooks_processed", "processed"),
        Index("idx_payment_webhooks_webhook_id", "webhook_id"),
    )

    def __repr__(self):
        return f"<PaymentWebhook {self.provider} {self.event_type}>"


class UserPaymentMethod(Base):
    __tablename__ = "user_payment_methods"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    tenant_id = Column(String(50), nullable=False, index=True)

    # Payment Method Information
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    is_default = Column(Boolean, nullable=False, default=False)

    # Card Information (for Stripe/Mada)
    card_last4 = Column(String(4), nullable=True)
    card_brand = Column(String(20), nullable=True)
    card_exp_month = Column(Integer, nullable=True)
    card_exp_year = Column(Integer, nullable=True)

    # Stripe specific
    stripe_payment_method_id = Column(String(255), nullable=True, index=True)
    stripe_customer_id = Column(String(255), nullable=True, index=True)

    # Mada specific
    mada_token = Column(String(255), nullable=True)

    # STC Pay specific
    stc_pay_phone = Column(String(20), nullable=True)

    # Bank Transfer specific
    bank_account_info = Column(JSON, nullable=True)

    # Status
    is_active = Column(Boolean, nullable=False, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Indexes
    __table_args__ = (
        Index("idx_user_payment_methods_user", "user_id"),
        Index("idx_user_payment_methods_tenant", "tenant_id"),
        Index("idx_user_payment_methods_default", "is_default"),
        Index("idx_user_payment_methods_stripe_pm", "stripe_payment_method_id"),
    )

    def __repr__(self):
        return f"<UserPaymentMethod {self.payment_method}>"


class PaymentAuditLog(Base):
    """Audit trail for all payment-related actions"""
    __tablename__ = "payment_audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(String(50), nullable=False, index=True)
    payment_id = Column(UUID(as_uuid=True), ForeignKey("payments.id"), nullable=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=True, index=True)

    # Audit Information
    action = Column(String(100), nullable=False, index=True)  # created, updated, authorized, captured, failed, refunded
    entity_type = Column(String(50), nullable=False)  # payment, refund, webhook, method
    entity_id = Column(String(255), nullable=False, index=True)
    
    # Changes tracking
    old_values = Column(JSON, nullable=True)  # Previous state
    new_values = Column(JSON, nullable=True)  # New state
    changes = Column(JSON, nullable=True)     # What changed
    
    # Context
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    admin_user_id = Column(UUID(as_uuid=True), nullable=True)  # If action was performed by admin
    reason = Column(Text, nullable=True)  # Reason for manual actions
    
    # Metadata
    audit_metadata = Column(JSON, nullable=True)
    risk_score = Column(Numeric(5, 4), nullable=True)  # Fraud risk score if applicable
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    payment = relationship("Payment", backref="audit_logs")
    user = relationship("User", backref="payment_audit_logs")

    # Indexes
    __table_args__ = (
        Index("idx_payment_audit_tenant_date", "tenant_id", "created_at"),
        Index("idx_payment_audit_payment", "payment_id"),
        Index("idx_payment_audit_user", "user_id"),
        Index("idx_payment_audit_action", "action"),
        Index("idx_payment_audit_entity", "entity_type", "entity_id"),
    )

    def __repr__(self):
        return f"<PaymentAuditLog {self.action} {self.entity_type}>"


class PaymentReconciliation(Base):
    """Payment reconciliation records"""
    __tablename__ = "payment_reconciliations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(String(50), nullable=False, index=True)
    payment_id = Column(UUID(as_uuid=True), ForeignKey("payments.id"), nullable=False, index=True)

    # Reconciliation Information
    provider_transaction_id = Column(String(255), nullable=False, index=True)
    provider_name = Column(String(50), nullable=False)
    settlement_date = Column(DateTime(timezone=True), nullable=True)
    settlement_amount = Column(Numeric(10, 2), nullable=False)
    settlement_currency = Column(String(3), nullable=False, default="SAR")
    
    # Fees and charges
    provider_fee = Column(Numeric(10, 2), nullable=False, default=0)
    gateway_fee = Column(Numeric(10, 2), nullable=False, default=0)
    processing_fee = Column(Numeric(10, 2), nullable=False, default=0)
    net_amount = Column(Numeric(10, 2), nullable=False)
    
    # Status
    reconciliation_status = Column(String(50), nullable=False, default="pending")  # pending, matched, disputed, resolved
    discrepancy_amount = Column(Numeric(10, 2), nullable=True)
    discrepancy_reason = Column(Text, nullable=True)
    
    # Additional data
    provider_data = Column(JSON, nullable=True)  # Raw data from provider
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    reconciled_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    payment = relationship("Payment", backref="reconciliation_records")

    # Indexes
    __table_args__ = (
        Index("idx_payment_recon_tenant", "tenant_id"),
        Index("idx_payment_recon_payment", "payment_id"),
        Index("idx_payment_recon_provider", "provider_name", "provider_transaction_id"),
        Index("idx_payment_recon_status", "reconciliation_status"),
        Index("idx_payment_recon_settlement", "settlement_date"),
    )

    def __repr__(self):
        return f"<PaymentReconciliation {self.provider_transaction_id}>"


class FraudDetectionLog(Base):
    """Fraud detection and prevention logs"""
    __tablename__ = "fraud_detection_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(String(50), nullable=False, index=True)
    payment_id = Column(UUID(as_uuid=True), ForeignKey("payments.id"), nullable=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=True, index=True)

    # Fraud Detection Information
    rule_name = Column(String(255), nullable=False, index=True)
    rule_type = Column(String(50), nullable=False)  # velocity, amount, location, device, behavior
    risk_score = Column(Numeric(5, 4), nullable=False, index=True)
    risk_level = Column(String(20), nullable=False, index=True)  # low, medium, high, critical
    
    # Decision
    decision = Column(String(20), nullable=False)  # allow, block, review, challenge
    action_taken = Column(String(100), nullable=True)  # specific action taken
    
    # Detection details
    triggered_values = Column(JSON, nullable=True)  # Values that triggered the rule
    threshold_values = Column(JSON, nullable=True)  # Threshold values for the rule
    additional_context = Column(JSON, nullable=True)
    
    # Device and location
    ip_address = Column(String(45), nullable=True, index=True)
    country = Column(String(2), nullable=True)
    device_fingerprint = Column(String(255), nullable=True, index=True)
    
    # Resolution
    is_false_positive = Column(Boolean, nullable=True)
    reviewed_by = Column(UUID(as_uuid=True), nullable=True)  # Admin who reviewed
    review_notes = Column(Text, nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    payment = relationship("Payment", backref="fraud_logs")
    user = relationship("User", backref="fraud_detection_logs")

    # Indexes
    __table_args__ = (
        Index("idx_fraud_detection_tenant_date", "tenant_id", "created_at"),
        Index("idx_fraud_detection_payment", "payment_id"),
        Index("idx_fraud_detection_user", "user_id"),
        Index("idx_fraud_detection_risk", "risk_level", "risk_score"),
        Index("idx_fraud_detection_rule", "rule_name"),
        Index("idx_fraud_detection_ip", "ip_address"),
        Index("idx_fraud_detection_device", "device_fingerprint"),
    )

    def __repr__(self):
        return f"<FraudDetectionLog {self.rule_name} {self.risk_level}>"
