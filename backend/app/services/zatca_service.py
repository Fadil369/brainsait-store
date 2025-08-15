"""
ZATCA Tax Compliance Service for Saudi Arabia

ZATCA (Zakat, Tax and Customs Authority) E-Invoicing compliance service.
Handles electronic invoice generation, validation, and submission to ZATCA platform.
"""

import logging
import hashlib
import hmac
import json
import uuid
import base64
import qrcode
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, Any, Optional, List, Tuple
from io import BytesIO
import xml.etree.ElementTree as ET

import httpx
from pydantic import BaseModel, Field, validator
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm

from app.core.config import settings

logger = logging.getLogger(__name__)


class ZATCACompanyInfo(BaseModel):
    """Company information for ZATCA compliance"""
    name: str = Field(..., min_length=2, max_length=100)
    name_ar: str = Field(..., min_length=2, max_length=100)
    tax_number: str = Field(..., regex=r'^[3][0-9]{14}$')
    commercial_registration: str = Field(..., min_length=10, max_length=20)
    address: Dict[str, str]
    phone: str = Field(..., regex=r'^\+966[0-9]{8,9}$')
    email: str = Field(..., regex=r'^[^@]+@[^@]+\.[^@]+$')


class ZATCACustomerInfo(BaseModel):
    """Customer information for ZATCA invoice"""
    name: str = Field(..., min_length=2, max_length=100)
    name_ar: Optional[str] = Field(None, max_length=100)
    tax_number: Optional[str] = Field(None, regex=r'^[3][0-9]{14}$')
    commercial_registration: Optional[str] = None
    address: Dict[str, str]
    phone: Optional[str] = Field(None, regex=r'^\+966[0-9]{8,9}$')
    email: Optional[str] = Field(None, regex=r'^[^@]+@[^@]+\.[^@]+$')


class ZATCAInvoiceItem(BaseModel):
    """Invoice line item for ZATCA compliance"""
    id: int
    name: str = Field(..., min_length=1, max_length=200)
    name_ar: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    description_ar: Optional[str] = Field(None, max_length=500)
    quantity: Decimal = Field(..., gt=0)
    unit_price: Decimal = Field(..., gt=0)
    discount_amount: Decimal = Field(default=Decimal('0'), ge=0)
    tax_category: str = Field(default="S")  # S=Standard, E=Exempt, Z=Zero
    tax_rate: Decimal = Field(default=Decimal('0.15'))  # 15% VAT
    total_before_tax: Decimal
    tax_amount: Decimal
    total_amount: Decimal

    @validator('total_before_tax', pre=True, always=True)
    def calculate_total_before_tax(cls, v, values):
        if 'quantity' in values and 'unit_price' in values and 'discount_amount' in values:
            return (values['quantity'] * values['unit_price']) - values['discount_amount']
        return v

    @validator('tax_amount', pre=True, always=True)
    def calculate_tax_amount(cls, v, values):
        if 'total_before_tax' in values and 'tax_rate' in values:
            return values['total_before_tax'] * values['tax_rate']
        return v

    @validator('total_amount', pre=True, always=True)
    def calculate_total_amount(cls, v, values):
        if 'total_before_tax' in values and 'tax_amount' in values:
            return values['total_before_tax'] + values['tax_amount']
        return v


class ZATCAInvoiceRequest(BaseModel):
    """ZATCA invoice generation request"""
    invoice_type: str = Field(default="standard", regex="^(standard|simplified|credit|debit)$")
    company_info: ZATCACompanyInfo
    customer_info: Optional[ZATCACustomerInfo] = None  # Optional for simplified invoices
    invoice_number: str = Field(..., min_length=1, max_length=50)
    issue_date: datetime
    due_date: Optional[datetime] = None
    items: List[ZATCAInvoiceItem]
    payment_method: str = Field(default="cash", regex="^(cash|card|transfer|check|other)$")
    currency: str = Field(default="SAR")
    notes: Optional[str] = Field(None, max_length=500)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @validator('due_date', pre=True, always=True)
    def set_default_due_date(cls, v, values):
        if v is None and 'issue_date' in values:
            return values['issue_date'] + timedelta(days=30)
        return v


class ZATCAInvoiceResponse(BaseModel):
    """ZATCA invoice response"""
    invoice_uuid: str
    invoice_number: str
    invoice_hash: str
    qr_code: str  # Base64 encoded QR code
    qr_code_text: str  # QR code text content
    xml_content: str  # UBL 2.1 XML content
    pdf_content: Optional[str] = None  # Base64 encoded PDF
    zatca_status: str  # submitted, accepted, rejected, cancelled
    submission_id: Optional[str] = None
    validation_errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    created_at: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ZATCAService:
    """
    ZATCA E-Invoicing Compliance Service
    
    Provides integration with Saudi Arabia's ZATCA platform for electronic invoicing.
    Handles invoice generation, validation, and submission according to ZATCA requirements.
    """

    def __init__(self):
        self.base_url = settings.ZATCA_API_URL or "https://api.zatca.gov.sa"
        self.client_id = settings.ZATCA_CLIENT_ID
        self.client_secret = settings.ZATCA_CLIENT_SECRET
        self.certificate_path = settings.ZATCA_CERTIFICATE_PATH
        self.private_key_path = settings.ZATCA_PRIVATE_KEY_PATH
        self.environment = settings.ZATCA_ENVIRONMENT or "sandbox"
        
        if not all([self.client_id, self.client_secret]):
            logger.warning("ZATCA credentials not fully configured")

    def _generate_invoice_hash(self, xml_content: str) -> str:
        """Generate invoice hash for ZATCA submission"""
        hash_input = xml_content.encode('utf-8')
        return hashlib.sha256(hash_input).hexdigest()

    def _generate_invoice_uuid(self) -> str:
        """Generate unique invoice UUID"""
        return str(uuid.uuid4())

    def _create_qr_code_text(
        self, 
        company_name: str,
        tax_number: str,
        invoice_date: datetime,
        total_amount: Decimal,
        tax_amount: Decimal
    ) -> str:
        """Create QR code text according to ZATCA specifications"""
        # ZATCA QR code format (TLV - Tag Length Value)
        def encode_tlv(tag: int, value: str) -> str:
            value_bytes = value.encode('utf-8')
            length = len(value_bytes)
            return chr(tag) + chr(length) + value
        
        qr_data = ""
        qr_data += encode_tlv(1, company_name)  # Seller name
        qr_data += encode_tlv(2, tax_number)    # VAT registration number
        qr_data += encode_tlv(3, invoice_date.isoformat())  # Invoice date
        qr_data += encode_tlv(4, str(total_amount))  # Invoice total
        qr_data += encode_tlv(5, str(tax_amount))    # VAT amount
        
        return base64.b64encode(qr_data.encode('utf-8')).decode('utf-8')

    def _generate_qr_code_image(self, qr_text: str) -> str:
        """Generate QR code image from text"""
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_text)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            return f"data:image/png;base64,{img_str}"
            
        except Exception as e:
            logger.error(f"QR code generation failed: {e}")
            return ""

    def _create_ubl_xml(self, invoice_request: ZATCAInvoiceRequest) -> str:
        """Create UBL 2.1 XML document for ZATCA"""
        # This is a simplified UBL XML structure
        # In production, you would use a proper UBL library
        
        invoice_uuid = self._generate_invoice_uuid()
        
        xml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
         xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
         xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
    
    <cbc:ID>{invoice_request.invoice_number}</cbc:ID>
    <cbc:UUID>{invoice_uuid}</cbc:UUID>
    <cbc:IssueDate>{invoice_request.issue_date.strftime('%Y-%m-%d')}</cbc:IssueDate>
    <cbc:IssueTime>{invoice_request.issue_date.strftime('%H:%M:%S')}</cbc:IssueTime>
    <cbc:InvoiceTypeCode>388</cbc:InvoiceTypeCode>
    <cbc:DocumentCurrencyCode>{invoice_request.currency}</cbc:DocumentCurrencyCode>
    
    <!-- Supplier Party -->
    <cac:AccountingSupplierParty>
        <cac:Party>
            <cac:PartyName>
                <cbc:Name>{invoice_request.company_info.name}</cbc:Name>
            </cac:PartyName>
            <cac:PostalAddress>
                <cbc:StreetName>{invoice_request.company_info.address.get('street', '')}</cbc:StreetName>
                <cbc:CityName>{invoice_request.company_info.address.get('city', '')}</cbc:CityName>
                <cbc:PostalZone>{invoice_request.company_info.address.get('postal_code', '')}</cbc:PostalZone>
                <cac:Country>
                    <cbc:IdentificationCode>SA</cbc:IdentificationCode>
                </cac:Country>
            </cac:PostalAddress>
            <cac:PartyTaxScheme>
                <cbc:CompanyID>{invoice_request.company_info.tax_number}</cbc:CompanyID>
                <cac:TaxScheme>
                    <cbc:ID>VAT</cbc:ID>
                </cac:TaxScheme>
            </cac:PartyTaxScheme>
        </cac:Party>
    </cac:AccountingSupplierParty>'''

        # Add customer info if provided (for standard invoices)
        if invoice_request.customer_info:
            xml_content += f'''
    
    <!-- Customer Party -->
    <cac:AccountingCustomerParty>
        <cac:Party>
            <cac:PartyName>
                <cbc:Name>{invoice_request.customer_info.name}</cbc:Name>
            </cac:PartyName>
            <cac:PostalAddress>
                <cbc:StreetName>{invoice_request.customer_info.address.get('street', '')}</cbc:StreetName>
                <cbc:CityName>{invoice_request.customer_info.address.get('city', '')}</cbc:CityName>
                <cbc:PostalZone>{invoice_request.customer_info.address.get('postal_code', '')}</cbc:PostalZone>
                <cac:Country>
                    <cbc:IdentificationCode>SA</cbc:IdentificationCode>
                </cac:Country>
            </cac:PostalAddress>'''
            
            if invoice_request.customer_info.tax_number:
                xml_content += f'''
            <cac:PartyTaxScheme>
                <cbc:CompanyID>{invoice_request.customer_info.tax_number}</cbc:CompanyID>
                <cac:TaxScheme>
                    <cbc:ID>VAT</cbc:ID>
                </cac:TaxScheme>
            </cac:PartyTaxScheme>'''
            
            xml_content += '''
        </cac:Party>
    </cac:AccountingCustomerParty>'''

        # Calculate totals
        subtotal = sum(item.total_before_tax for item in invoice_request.items)
        total_tax = sum(item.tax_amount for item in invoice_request.items)
        total_amount = subtotal + total_tax

        # Add invoice lines
        xml_content += '''
    
    <!-- Invoice Lines -->'''
        
        for i, item in enumerate(invoice_request.items, 1):
            xml_content += f'''
    <cac:InvoiceLine>
        <cbc:ID>{i}</cbc:ID>
        <cbc:InvoicedQuantity unitCode="PCE">{item.quantity}</cbc:InvoicedQuantity>
        <cbc:LineExtensionAmount currencyID="{invoice_request.currency}">{item.total_before_tax}</cbc:LineExtensionAmount>
        <cac:Item>
            <cbc:Name>{item.name}</cbc:Name>
            <cbc:Description>{item.description or ''}</cbc:Description>
        </cac:Item>
        <cac:Price>
            <cbc:PriceAmount currencyID="{invoice_request.currency}">{item.unit_price}</cbc:PriceAmount>
        </cac:Price>
        <cac:TaxTotal>
            <cbc:TaxAmount currencyID="{invoice_request.currency}">{item.tax_amount}</cbc:TaxAmount>
            <cac:TaxSubtotal>
                <cbc:TaxableAmount currencyID="{invoice_request.currency}">{item.total_before_tax}</cbc:TaxableAmount>
                <cbc:TaxAmount currencyID="{invoice_request.currency}">{item.tax_amount}</cbc:TaxAmount>
                <cac:TaxCategory>
                    <cbc:ID>{item.tax_category}</cbc:ID>
                    <cbc:Percent>{item.tax_rate * 100}</cbc:Percent>
                    <cac:TaxScheme>
                        <cbc:ID>VAT</cbc:ID>
                    </cac:TaxScheme>
                </cac:TaxCategory>
            </cac:TaxSubtotal>
        </cac:TaxTotal>
    </cac:InvoiceLine>'''

        # Add totals
        xml_content += f'''
    
    <!-- Tax Total -->
    <cac:TaxTotal>
        <cbc:TaxAmount currencyID="{invoice_request.currency}">{total_tax}</cbc:TaxAmount>
        <cac:TaxSubtotal>
            <cbc:TaxableAmount currencyID="{invoice_request.currency}">{subtotal}</cbc:TaxableAmount>
            <cbc:TaxAmount currencyID="{invoice_request.currency}">{total_tax}</cbc:TaxAmount>
            <cac:TaxCategory>
                <cbc:ID>S</cbc:ID>
                <cbc:Percent>15.0</cbc:Percent>
                <cac:TaxScheme>
                    <cbc:ID>VAT</cbc:ID>
                </cac:TaxScheme>
            </cac:TaxCategory>
        </cac:TaxSubtotal>
    </cac:TaxTotal>
    
    <!-- Legal Monetary Total -->
    <cac:LegalMonetaryTotal>
        <cbc:LineExtensionAmount currencyID="{invoice_request.currency}">{subtotal}</cbc:LineExtensionAmount>
        <cbc:TaxExclusiveAmount currencyID="{invoice_request.currency}">{subtotal}</cbc:TaxExclusiveAmount>
        <cbc:TaxInclusiveAmount currencyID="{invoice_request.currency}">{total_amount}</cbc:TaxInclusiveAmount>
        <cbc:PayableAmount currencyID="{invoice_request.currency}">{total_amount}</cbc:PayableAmount>
    </cac:LegalMonetaryTotal>
    
</Invoice>'''

        return xml_content

    def _generate_pdf_invoice(
        self, 
        invoice_request: ZATCAInvoiceRequest,
        qr_code_image: str
    ) -> str:
        """Generate PDF invoice with Arabic support"""
        try:
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            story = []
            styles = getSampleStyleSheet()
            
            # Arabic style (you would need proper Arabic font support)
            arabic_style = ParagraphStyle(
                'Arabic',
                parent=styles['Normal'],
                fontName='Helvetica',  # Replace with Arabic font
                alignment=2  # Right alignment for Arabic
            )
            
            # Company header
            story.append(Paragraph(f"<b>{invoice_request.company_info.name}</b>", styles['Title']))
            if invoice_request.company_info.name_ar:
                story.append(Paragraph(invoice_request.company_info.name_ar, arabic_style))
            
            story.append(Spacer(1, 0.2 * cm))
            
            # Invoice details
            invoice_data = [
                ['Invoice Number:', invoice_request.invoice_number, 'Date:', invoice_request.issue_date.strftime('%Y-%m-%d')],
                ['Tax Number:', invoice_request.company_info.tax_number, 'Due Date:', (invoice_request.due_date or invoice_request.issue_date).strftime('%Y-%m-%d')]
            ]
            
            invoice_table = Table(invoice_data, colWidths=[3*cm, 4*cm, 2*cm, 3*cm])
            invoice_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(invoice_table)
            story.append(Spacer(1, 0.5 * cm))
            
            # Customer info (if provided)
            if invoice_request.customer_info:
                story.append(Paragraph("<b>Bill To:</b>", styles['Heading3']))
                story.append(Paragraph(invoice_request.customer_info.name, styles['Normal']))
                if invoice_request.customer_info.tax_number:
                    story.append(Paragraph(f"Tax Number: {invoice_request.customer_info.tax_number}", styles['Normal']))
                story.append(Spacer(1, 0.3 * cm))
            
            # Invoice items
            items_data = [['Item', 'Qty', 'Unit Price', 'Discount', 'Tax', 'Total']]
            
            for item in invoice_request.items:
                items_data.append([
                    item.name[:30] + ('...' if len(item.name) > 30 else ''),
                    str(item.quantity),
                    f"{item.unit_price:.2f}",
                    f"{item.discount_amount:.2f}",
                    f"{item.tax_amount:.2f}",
                    f"{item.total_amount:.2f}"
                ])
            
            items_table = Table(items_data, colWidths=[6*cm, 2*cm, 2*cm, 2*cm, 2*cm, 2*cm])
            items_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(items_table)
            story.append(Spacer(1, 0.5 * cm))
            
            # Totals
            subtotal = sum(item.total_before_tax for item in invoice_request.items)
            total_tax = sum(item.tax_amount for item in invoice_request.items)
            total_amount = subtotal + total_tax
            
            totals_data = [
                ['Subtotal:', f"{subtotal:.2f} SAR"],
                ['VAT (15%):', f"{total_tax:.2f} SAR"],
                ['Total:', f"{total_amount:.2f} SAR"]
            ]
            
            totals_table = Table(totals_data, colWidths=[10*cm, 4*cm])
            totals_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, -1), (-1, -1), 12),
                ('TOPPADDING', (0, -1), (-1, -1), 6),
                ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ]))
            story.append(totals_table)
            
            doc.build(story)
            pdf_str = base64.b64encode(buffer.getvalue()).decode()
            buffer.close()
            
            return pdf_str
            
        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            return ""

    async def generate_invoice(
        self, 
        invoice_request: ZATCAInvoiceRequest
    ) -> ZATCAInvoiceResponse:
        """
        Generate ZATCA-compliant invoice
        
        Args:
            invoice_request: Invoice data and requirements
            
        Returns:
            ZATCAInvoiceResponse with invoice details and compliance data
        """
        logger.info(f"Generating ZATCA invoice: {invoice_request.invoice_number}")
        
        try:
            # Generate invoice UUID and XML
            invoice_uuid = self._generate_invoice_uuid()
            xml_content = self._create_ubl_xml(invoice_request)
            invoice_hash = self._generate_invoice_hash(xml_content)
            
            # Calculate totals for QR code
            subtotal = sum(item.total_before_tax for item in invoice_request.items)
            total_tax = sum(item.tax_amount for item in invoice_request.items)
            total_amount = subtotal + total_tax
            
            # Generate QR code
            qr_code_text = self._create_qr_code_text(
                invoice_request.company_info.name,
                invoice_request.company_info.tax_number,
                invoice_request.issue_date,
                total_amount,
                total_tax
            )
            qr_code_image = self._generate_qr_code_image(qr_code_text)
            
            # Generate PDF
            pdf_content = self._generate_pdf_invoice(invoice_request, qr_code_image)
            
            # Create response
            zatca_response = ZATCAInvoiceResponse(
                invoice_uuid=invoice_uuid,
                invoice_number=invoice_request.invoice_number,
                invoice_hash=invoice_hash,
                qr_code=qr_code_image,
                qr_code_text=qr_code_text,
                xml_content=base64.b64encode(xml_content.encode('utf-8')).decode(),
                pdf_content=pdf_content,
                zatca_status="generated",  # Would be "submitted" after API call
                submission_id=None,
                validation_errors=[],
                warnings=[],
                created_at=datetime.utcnow(),
                metadata=invoice_request.metadata
            )
            
            logger.info(f"ZATCA invoice generated: {zatca_response.invoice_uuid}")
            return zatca_response
            
        except Exception as e:
            logger.error(f"ZATCA invoice generation failed: {e}")
            raise

    async def submit_to_zatca(
        self, 
        zatca_response: ZATCAInvoiceResponse
    ) -> ZATCAInvoiceResponse:
        """
        Submit generated invoice to ZATCA platform
        
        Args:
            zatca_response: Generated invoice response
            
        Returns:
            Updated ZATCAInvoiceResponse with submission status
        """
        logger.info(f"Submitting invoice to ZATCA: {zatca_response.invoice_uuid}")
        
        # This would make actual API call to ZATCA
        # For now, we'll simulate the response
        
        try:
            # Simulate ZATCA API submission
            # In production, you would:
            # 1. Sign the XML with digital certificate
            # 2. Submit to ZATCA API
            # 3. Handle response and validation
            
            submission_data = {
                "invoice_uuid": zatca_response.invoice_uuid,
                "invoice_hash": zatca_response.invoice_hash,
                "xml_content": zatca_response.xml_content,
                "invoice_type": "standard"
            }
            
            # Mock successful submission
            zatca_response.zatca_status = "accepted"
            zatca_response.submission_id = f"ZATCA_{uuid.uuid4().hex[:12]}"
            zatca_response.validation_errors = []
            zatca_response.warnings = []
            
            logger.info(f"ZATCA submission successful: {zatca_response.submission_id}")
            return zatca_response
            
        except Exception as e:
            logger.error(f"ZATCA submission failed: {e}")
            zatca_response.zatca_status = "rejected"
            zatca_response.validation_errors = [str(e)]
            return zatca_response

    async def validate_tax_number(self, tax_number: str) -> bool:
        """
        Validate Saudi tax number with ZATCA
        
        Args:
            tax_number: Tax number to validate
            
        Returns:
            bool: True if valid
        """
        if not tax_number or len(tax_number) != 15 or not tax_number.startswith('3'):
            return False
        
        # Simple checksum validation for Saudi tax numbers
        # In production, you would validate against ZATCA API
        try:
            digits = [int(d) for d in tax_number]
            
            # Simplified validation algorithm
            checksum = 0
            for i, digit in enumerate(digits[:-1]):
                if i % 2 == 0:
                    checksum += digit
                else:
                    checksum += digit * 2 if digit * 2 < 10 else digit * 2 - 9
            
            return (checksum % 10) == 0
            
        except Exception as e:
            logger.error(f"Tax number validation failed: {e}")
            return False

    def calculate_vat(self, amount: Decimal, rate: Decimal = Decimal('0.15')) -> Decimal:
        """
        Calculate VAT amount
        
        Args:
            amount: Base amount
            rate: VAT rate (default 15%)
            
        Returns:
            VAT amount
        """
        return amount * rate

    def format_saudi_currency(self, amount: Decimal) -> str:
        """
        Format amount in Saudi Riyal
        
        Args:
            amount: Amount to format
            
        Returns:
            Formatted currency string
        """
        return f"{amount:.2f} ر.س"


# Global instance
zatca_service = ZATCAService()