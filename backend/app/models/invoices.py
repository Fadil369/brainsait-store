"""
Invoice models for ZATCA compliance (Saudi Arabia)
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


class InvoiceType(str, enum.Enum):
    TAX_INVOICE = "tax_invoice"  # Standard tax invoice
    SIMPLIFIED_INVOICE = "simplified_invoice"  # Simplified tax invoice for B2C
    CREDIT_NOTE = "credit_note"  # Credit note for returns
    DEBIT_NOTE = "debit_note"  # Debit note for additional charges


class InvoiceStatus(str, enum.Enum):
    DRAFT = "draft"
    ISSUED = "issued"
    SENT = "sent"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"
    VOID = "void"


class ZATCAStatus(str, enum.Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    CLEARED = "cleared"


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False)
    tenant_id = Column(String(50), nullable=False, index=True)

    # Invoice Identification
    invoice_number = Column(String(50), nullable=False, unique=True, index=True)
    invoice_type = Column(
        Enum(InvoiceType), nullable=False, default=InvoiceType.TAX_INVOICE
    )
    status = Column(Enum(InvoiceStatus), nullable=False, default=InvoiceStatus.DRAFT)

    # ZATCA Compliance
    zatca_status = Column(
        Enum(ZATCAStatus), nullable=False, default=ZATCAStatus.PENDING
    )
    zatca_uuid = Column(String(255), nullable=True, index=True)
    zatca_hash = Column(String(255), nullable=True)
    zatca_qr_code = Column(Text, nullable=True)
    zatca_xml = Column(Text, nullable=True)
    zatca_response = Column(JSON, nullable=True)

    # Seller Information (from tenant config)
    seller_name = Column(String(255), nullable=False)
    seller_name_ar = Column(String(255), nullable=False)
    seller_vat_number = Column(String(20), nullable=False)
    seller_cr_number = Column(String(20), nullable=False)
    seller_address = Column(JSON, nullable=False)

    # Buyer Information
    buyer_name = Column(String(255), nullable=False)
    buyer_name_ar = Column(String(255), nullable=True)
    buyer_vat_number = Column(String(20), nullable=True)
    buyer_address = Column(JSON, nullable=False)

    # Invoice Details
    issue_date = Column(DateTime(timezone=True), nullable=False)
    due_date = Column(DateTime(timezone=True), nullable=True)
    supply_date = Column(DateTime(timezone=True), nullable=True)

    # Currency
    currency = Column(String(3), nullable=False, default="SAR")
    exchange_rate = Column(Numeric(10, 6), nullable=False, default=1.0)

    # Amounts
    subtotal = Column(Numeric(15, 2), nullable=False)
    discount_amount = Column(Numeric(15, 2), nullable=False, default=0)
    taxable_amount = Column(Numeric(15, 2), nullable=False)
    tax_amount = Column(Numeric(15, 2), nullable=False)
    total_amount = Column(Numeric(15, 2), nullable=False)

    # Payment Information
    payment_method = Column(String(50), nullable=True)
    payment_terms = Column(Text, nullable=True)

    # Additional Information
    notes = Column(Text, nullable=True)
    notes_ar = Column(Text, nullable=True)
    internal_notes = Column(Text, nullable=True)

    # Files
    pdf_url = Column(String(500), nullable=True)
    xml_url = Column(String(500), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    sent_at = Column(DateTime(timezone=True), nullable=True)
    paid_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    order = relationship("Order", back_populates="invoices")
    line_items = relationship("InvoiceLineItem", back_populates="invoice")

    # Indexes
    __table_args__ = (
        Index("idx_invoices_order", "order_id"),
        Index("idx_invoices_tenant", "tenant_id"),
        Index("idx_invoices_status", "status"),
        Index("idx_invoices_zatca_status", "zatca_status"),
        Index("idx_invoices_issue_date", "issue_date"),
        Index("idx_invoices_zatca_uuid", "zatca_uuid"),
    )

    def __repr__(self):
        return f"<Invoice {self.invoice_number}>"


class InvoiceLineItem(Base):
    __tablename__ = "invoice_line_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoices.id"), nullable=False)
    order_item_id = Column(
        UUID(as_uuid=True), ForeignKey("order_items.id"), nullable=True
    )
    tenant_id = Column(String(50), nullable=False, index=True)

    # Product Information
    product_name = Column(String(255), nullable=False)
    product_name_ar = Column(String(255), nullable=True)
    product_description = Column(Text, nullable=True)
    product_description_ar = Column(Text, nullable=True)
    product_sku = Column(String(100), nullable=False)

    # Quantity and Pricing
    quantity = Column(Numeric(10, 3), nullable=False)
    unit_of_measure = Column(
        String(20), nullable=False, default="PCE"
    )  # Piece, KG, etc.
    unit_price = Column(Numeric(15, 2), nullable=False)
    discount_amount = Column(Numeric(15, 2), nullable=False, default=0)
    taxable_amount = Column(Numeric(15, 2), nullable=False)

    # Tax Information
    tax_rate = Column(Numeric(5, 2), nullable=False)
    tax_amount = Column(Numeric(15, 2), nullable=False)
    tax_category = Column(
        String(50), nullable=False, default="S"
    )  # S=Standard, Z=Zero, E=Exempt

    # Total
    line_total = Column(Numeric(15, 2), nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    invoice = relationship("Invoice", back_populates="line_items")
    order_item = relationship("OrderItem")

    # Indexes
    __table_args__ = (
        Index("idx_invoice_line_items_invoice", "invoice_id"),
        Index("idx_invoice_line_items_tenant", "tenant_id"),
    )

    def __repr__(self):
        return f"<InvoiceLineItem {self.product_name}>"


class InvoiceSequence(Base):
    __tablename__ = "invoice_sequences"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(String(50), nullable=False, index=True)

    # Sequence Configuration
    prefix = Column(String(20), nullable=False)  # e.g., "INV", "CN", "DN"
    current_number = Column(Integer, nullable=False, default=0)
    padding = Column(Integer, nullable=False, default=6)  # Number of digits

    # Date-based sequences
    year = Column(Integer, nullable=True)
    month = Column(Integer, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Indexes
    __table_args__ = (
        Index(
            "idx_invoice_sequences_tenant_prefix",
            "tenant_id",
            "prefix",
            "year",
            "month",
            unique=True,
        ),
    )

    def generate_number(self) -> str:
        """Generate next invoice number"""
        self.current_number += 1

        if self.year and self.month:
            return f"{self.prefix}-{self.year:04d}{self.month:02d}-{self.current_number:0{self.padding}d}"
        elif self.year:
            return (
                f"{self.prefix}-{self.year:04d}-{self.current_number:0{self.padding}d}"
            )
        else:
            return f"{self.prefix}-{self.current_number:0{self.padding}d}"

    def __repr__(self):
        return f"<InvoiceSequence {self.prefix}>"


class ZATCASubmission(Base):
    __tablename__ = "zatca_submissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoices.id"), nullable=False)
    tenant_id = Column(String(50), nullable=False, index=True)

    # Submission Information
    submission_type = Column(String(50), nullable=False)  # reporting, clearance
    zatca_uuid = Column(String(255), nullable=False, index=True)

    # Request/Response
    request_payload = Column(Text, nullable=False)
    response_payload = Column(Text, nullable=True)
    status_code = Column(Integer, nullable=True)

    # Status
    status = Column(Enum(ZATCAStatus), nullable=False, default=ZATCAStatus.PENDING)
    error_message = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    submitted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    invoice = relationship("Invoice")

    # Indexes
    __table_args__ = (
        Index("idx_zatca_submissions_invoice", "invoice_id"),
        Index("idx_zatca_submissions_tenant", "tenant_id"),
        Index("idx_zatca_submissions_uuid", "zatca_uuid"),
        Index("idx_zatca_submissions_status", "status"),
    )

    def __repr__(self):
        return f"<ZATCASubmission {self.zatca_uuid}>"
