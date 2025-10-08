"""
ZATCA E-Invoicing Service (Phase 2)
Saudi Arabia Tax Authority Compliance
Implements QR code generation, XML/JSON invoicing, and ZATCA portal integration
"""

import base64
import hashlib
import json
import logging
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

import httpx
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.invoices import Invoice, InvoiceStatus, ZATCAStatus, ZATCASubmission

logger = logging.getLogger(__name__)


class ZATCAService:
    """ZATCA e-invoicing service for Phase 2 compliance"""
    
    # ZATCA API endpoints (sandbox/production)
    ZATCA_SANDBOX_URL = "https://gw-fatoora.zatca.gov.sa/e-invoicing/developer-portal"
    ZATCA_PRODUCTION_URL = "https://gw-fatoora.zatca.gov.sa/e-invoicing/core"
    
    # VAT rate for Saudi Arabia
    VAT_RATE = Decimal("0.15")  # 15%
    
    def __init__(self):
        self.enabled = settings.ZATCA_ENABLED
        self.vat_number = settings.ZATCA_VAT_NUMBER
        self.cr_number = settings.ZATCA_CR_NUMBER
        self.seller_name = settings.ZATCA_SELLER_NAME
        self.seller_name_ar = settings.ZATCA_SELLER_NAME_AR
        self.endpoint = self.ZATCA_SANDBOX_URL if not settings.PRODUCTION else self.ZATCA_PRODUCTION_URL
        self.client = httpx.AsyncClient(timeout=30.0)
        
    async def generate_invoice(
        self,
        order_id: UUID,
        payment_id: UUID,
        db: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        Generate ZATCA compliant invoice
        
        Args:
            order_id: Order UUID
            payment_id: Payment UUID
            db: Database session (optional)
            
        Returns:
            Invoice data with ZATCA QR code and hash
        """
        if not self.enabled:
            logger.warning("ZATCA is disabled, skipping invoice generation")
            return {"status": "disabled"}
            
        # Generate invoice number
        invoice_number = await self._generate_invoice_number(db)
        
        # Create invoice UUID
        invoice_uuid = str(UUID(int=int(str(order_id).replace('-', ''), 16)))
        
        # Calculate amounts (placeholder - should fetch from order)
        subtotal = Decimal("1000.00")
        tax_amount = subtotal * self.VAT_RATE
        total_amount = subtotal + tax_amount
        
        # Generate ZATCA QR code
        qr_code = self._generate_zatca_qr_code(
            seller_name=self.seller_name,
            vat_number=self.vat_number,
            timestamp=datetime.utcnow(),
            total_amount=total_amount,
            tax_amount=tax_amount,
            invoice_hash="",  # Will be updated after hash generation
        )
        
        # Generate invoice hash
        invoice_hash = self._generate_invoice_hash(
            invoice_number=invoice_number,
            issue_date=datetime.utcnow(),
            total_amount=total_amount,
        )
        
        # Update QR code with hash
        qr_code = self._generate_zatca_qr_code(
            seller_name=self.seller_name,
            vat_number=self.vat_number,
            timestamp=datetime.utcnow(),
            total_amount=total_amount,
            tax_amount=tax_amount,
            invoice_hash=invoice_hash,
        )
        
        # Generate XML (UBL 2.1 format)
        xml_invoice = self._generate_ubl_xml(
            invoice_number=invoice_number,
            invoice_uuid=invoice_uuid,
            issue_date=datetime.utcnow(),
            subtotal=subtotal,
            tax_amount=tax_amount,
            total_amount=total_amount,
            invoice_hash=invoice_hash,
        )
        
        return {
            "invoice_number": invoice_number,
            "invoice_uuid": invoice_uuid,
            "qr_code": qr_code,
            "invoice_hash": invoice_hash,
            "xml_invoice": xml_invoice,
            "zatca_status": ZATCAStatus.PENDING.value,
            "subtotal": float(subtotal),
            "tax_amount": float(tax_amount),
            "total_amount": float(total_amount),
        }
        
    def _generate_zatca_qr_code(
        self,
        seller_name: str,
        vat_number: str,
        timestamp: datetime,
        total_amount: Decimal,
        tax_amount: Decimal,
        invoice_hash: str,
    ) -> str:
        """
        Generate ZATCA compliant QR code in TLV format
        
        TLV Structure:
        Tag 1: Seller Name (UTF-8)
        Tag 2: VAT Registration Number
        Tag 3: Timestamp (ISO 8601)
        Tag 4: Total Amount (with VAT)
        Tag 5: VAT Amount
        Tag 6: Invoice Hash (Base64)
        """
        def tlv_encode(tag: int, value: str) -> bytes:
            """Encode value in TLV format"""
            value_bytes = value.encode('utf-8')
            length = len(value_bytes)
            return bytes([tag, length]) + value_bytes
            
        # Build TLV structure
        tlv_data = b''
        tlv_data += tlv_encode(1, seller_name)
        tlv_data += tlv_encode(2, vat_number)
        tlv_data += tlv_encode(3, timestamp.isoformat())
        tlv_data += tlv_encode(4, f"{total_amount:.2f}")
        tlv_data += tlv_encode(5, f"{tax_amount:.2f}")
        
        if invoice_hash:
            tlv_data += tlv_encode(6, invoice_hash)
            
        # Base64 encode the TLV data
        qr_code = base64.b64encode(tlv_data).decode('utf-8')
        return qr_code
        
    def _generate_invoice_hash(
        self,
        invoice_number: str,
        issue_date: datetime,
        total_amount: Decimal,
    ) -> str:
        """
        Generate SHA-256 hash for invoice
        
        Args:
            invoice_number: Invoice number
            issue_date: Invoice issue date
            total_amount: Total invoice amount
            
        Returns:
            Base64 encoded SHA-256 hash
        """
        # Create hash input string
        hash_input = f"{invoice_number}|{issue_date.isoformat()}|{total_amount:.2f}"
        
        # Generate SHA-256 hash
        hash_bytes = hashlib.sha256(hash_input.encode('utf-8')).digest()
        
        # Base64 encode
        invoice_hash = base64.b64encode(hash_bytes).decode('utf-8')
        return invoice_hash
        
    def _generate_ubl_xml(
        self,
        invoice_number: str,
        invoice_uuid: str,
        issue_date: datetime,
        subtotal: Decimal,
        tax_amount: Decimal,
        total_amount: Decimal,
        invoice_hash: str,
    ) -> str:
        """
        Generate UBL 2.1 compliant XML invoice
        
        Args:
            invoice_number: Invoice number
            invoice_uuid: Invoice UUID
            issue_date: Invoice issue date
            subtotal: Subtotal amount (before VAT)
            tax_amount: VAT amount
            total_amount: Total amount (with VAT)
            invoice_hash: Invoice cryptographic hash
            
        Returns:
            XML invoice string
        """
        # Simplified UBL 2.1 XML structure
        # In production, use proper XML library like lxml
        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
         xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
         xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
    <cbc:ID>{invoice_number}</cbc:ID>
    <cbc:UUID>{invoice_uuid}</cbc:UUID>
    <cbc:IssueDate>{issue_date.strftime('%Y-%m-%d')}</cbc:IssueDate>
    <cbc:IssueTime>{issue_date.strftime('%H:%M:%S')}</cbc:IssueTime>
    <cbc:InvoiceTypeCode>388</cbc:InvoiceTypeCode>
    <cbc:DocumentCurrencyCode>SAR</cbc:DocumentCurrencyCode>
    <cbc:TaxCurrencyCode>SAR</cbc:TaxCurrencyCode>
    
    <!-- Invoice Hash -->
    <cbc:ProfileID>reporting:1.0</cbc:ProfileID>
    <cbc:ProfileExecutionID>Standard</cbc:ProfileExecutionID>
    
    <!-- Seller Information -->
    <cac:AccountingSupplierParty>
        <cac:Party>
            <cac:PartyIdentification>
                <cbc:ID schemeID="CRN">{self.cr_number}</cbc:ID>
            </cac:PartyIdentification>
            <cac:PartyTaxScheme>
                <cbc:CompanyID>{self.vat_number}</cbc:CompanyID>
                <cac:TaxScheme>
                    <cbc:ID>VAT</cbc:ID>
                </cac:TaxScheme>
            </cac:PartyTaxScheme>
            <cac:PartyLegalEntity>
                <cbc:RegistrationName>{self.seller_name}</cbc:RegistrationName>
            </cac:PartyLegalEntity>
        </cac:Party>
    </cac:AccountingSupplierParty>
    
    <!-- Tax Total -->
    <cac:TaxTotal>
        <cbc:TaxAmount currencyID="SAR">{tax_amount:.2f}</cbc:TaxAmount>
        <cac:TaxSubtotal>
            <cbc:TaxableAmount currencyID="SAR">{subtotal:.2f}</cbc:TaxableAmount>
            <cbc:TaxAmount currencyID="SAR">{tax_amount:.2f}</cbc:TaxAmount>
            <cac:TaxCategory>
                <cbc:ID>S</cbc:ID>
                <cbc:Percent>15.00</cbc:Percent>
                <cac:TaxScheme>
                    <cbc:ID>VAT</cbc:ID>
                </cac:TaxScheme>
            </cac:TaxCategory>
        </cac:TaxSubtotal>
    </cac:TaxTotal>
    
    <!-- Legal Monetary Total -->
    <cac:LegalMonetaryTotal>
        <cbc:LineExtensionAmount currencyID="SAR">{subtotal:.2f}</cbc:LineExtensionAmount>
        <cbc:TaxExclusiveAmount currencyID="SAR">{subtotal:.2f}</cbc:TaxExclusiveAmount>
        <cbc:TaxInclusiveAmount currencyID="SAR">{total_amount:.2f}</cbc:TaxInclusiveAmount>
        <cbc:PayableAmount currencyID="SAR">{total_amount:.2f}</cbc:PayableAmount>
    </cac:LegalMonetaryTotal>
</Invoice>"""
        return xml
        
    async def submit_to_zatca(
        self,
        invoice_id: UUID,
        submission_type: str,
        db: AsyncSession,
    ) -> Dict[str, Any]:
        """
        Submit invoice to ZATCA portal (Phase 2)
        
        Args:
            invoice_id: Invoice UUID
            submission_type: 'reporting' or 'clearance'
            db: Database session
            
        Returns:
            ZATCA submission response
        """
        if not self.enabled:
            logger.warning("ZATCA is disabled, skipping submission")
            return {"status": "disabled"}
            
        # Fetch invoice from database
        result = await db.execute(
            select(Invoice).where(Invoice.id == invoice_id)
        )
        invoice = result.scalar_one_or_none()
        
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
            
        # Prepare submission payload
        payload = {
            "invoiceHash": invoice.zatca_hash,
            "uuid": invoice.zatca_uuid,
            "invoice": invoice.zatca_xml,
        }
        
        # Add to ZATCA submission tracking
        submission = ZATCASubmission(
            invoice_id=invoice_id,
            tenant_id=invoice.tenant_id,
            submission_type=submission_type,
            zatca_uuid=invoice.zatca_uuid,
            request_payload=json.dumps(payload),
            status=ZATCAStatus.PENDING,
        )
        
        try:
            # Submit to ZATCA (in production, include proper authentication)
            headers = {
                "Accept-Version": "V2",
                "Content-Type": "application/json",
            }
            
            endpoint = f"{self.endpoint}/{submission_type}"
            response = await self.client.post(
                endpoint,
                json=payload,
                headers=headers,
            )
            
            # Update submission record
            submission.response_payload = response.text
            submission.status_code = response.status_code
            
            if response.status_code == 200:
                submission.status = ZATCAStatus.APPROVED
                invoice.zatca_status = ZATCAStatus.APPROVED
                
                result_data = response.json()
                return {
                    "status": "approved",
                    "zatca_response": result_data,
                    "clearance_status": result_data.get("clearanceStatus"),
                }
            else:
                submission.status = ZATCAStatus.REJECTED
                submission.error_message = response.text
                invoice.zatca_status = ZATCAStatus.REJECTED
                
                logger.error(f"ZATCA submission failed: {response.text}")
                return {
                    "status": "rejected",
                    "error": response.text,
                }
                
        except httpx.RequestError as e:
            submission.status = ZATCAStatus.REJECTED
            submission.error_message = str(e)
            logger.error(f"ZATCA submission request failed: {e}")
            
            return {
                "status": "error",
                "error": str(e),
            }
        finally:
            db.add(submission)
            await db.commit()
            
    async def validate_invoice(
        self,
        invoice_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate invoice data before ZATCA submission
        
        Args:
            invoice_data: Invoice data dictionary
            
        Returns:
            Validation result
        """
        errors = []
        warnings = []
        
        # Required fields validation
        required_fields = [
            "seller_name", "seller_vat_number", "seller_cr_number",
            "buyer_name", "total_amount", "tax_amount", "invoice_number"
        ]
        
        for field in required_fields:
            if not invoice_data.get(field):
                errors.append(f"Missing required field: {field}")
                
        # VAT number format validation
        vat_number = invoice_data.get("seller_vat_number", "")
        if not vat_number.startswith("3") or len(vat_number) != 15:
            errors.append("Invalid VAT number format. Must be 15 digits starting with 3")
            
        # CR number validation
        cr_number = invoice_data.get("seller_cr_number", "")
        if not cr_number or len(cr_number) < 7:
            errors.append("Invalid CR number. Must be at least 7 digits")
            
        # Amount validation
        total_amount = Decimal(str(invoice_data.get("total_amount", 0)))
        tax_amount = Decimal(str(invoice_data.get("tax_amount", 0)))
        
        if total_amount <= 0:
            errors.append("Total amount must be greater than zero")
            
        # Check if tax calculation is correct (15%)
        expected_tax = (total_amount / Decimal("1.15")) * self.VAT_RATE
        if abs(tax_amount - expected_tax) > Decimal("0.01"):
            warnings.append(f"Tax amount may be incorrect. Expected: {expected_tax:.2f}, Got: {tax_amount:.2f}")
            
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
        }
        
    async def _generate_invoice_number(self, db: Optional[AsyncSession] = None) -> str:
        """
        Generate sequential invoice number
        Format: INV-YYYY-MM-NNNNNN
        """
        now = datetime.utcnow()
        # In production, use database sequence
        # For now, generate based on timestamp
        return f"INV-{now.strftime('%Y-%m')}-{now.strftime('%d%H%M%S')}"
        
    def calculate_vat(
        self,
        amount: Decimal,
        vat_inclusive: bool = False
    ) -> Dict[str, Decimal]:
        """
        Calculate VAT amounts
        
        Args:
            amount: Amount (with or without VAT)
            vat_inclusive: Whether amount includes VAT
            
        Returns:
            Dictionary with subtotal, vat_amount, and total
        """
        if vat_inclusive:
            # Extract VAT from total
            subtotal = amount / (Decimal("1") + self.VAT_RATE)
            vat_amount = amount - subtotal
            total = amount
        else:
            # Add VAT to subtotal
            subtotal = amount
            vat_amount = amount * self.VAT_RATE
            total = amount + vat_amount
            
        return {
            "subtotal": subtotal.quantize(Decimal("0.01")),
            "vat_amount": vat_amount.quantize(Decimal("0.01")),
            "total": total.quantize(Decimal("0.01")),
        }
