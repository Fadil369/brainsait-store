"""
ZATCA (Zakat, Tax and Customs Authority) Compliance Service
Saudi Arabia tax invoice generation and e-invoicing compliance
"""

import base64
import hashlib
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

import httpx
import qrcode
from io import BytesIO

from app.core.config import settings
from app.models.orders import Order
from app.models.invoices import Invoice


logger = logging.getLogger(__name__)


class ZATCAService:
    """ZATCA compliance service for Saudi tax invoices"""

    def __init__(self):
        self.vat_number = settings.ZATCA_VAT_NUMBER
        self.cr_number = settings.ZATCA_CR_NUMBER
        self.seller_name = settings.ZATCA_SELLER_NAME
        self.seller_name_ar = settings.ZATCA_SELLER_NAME_AR
        self.enabled = settings.ZATCA_ENABLED
        self.client = httpx.AsyncClient()

    async def generate_invoice(
        self, 
        order_id: UUID, 
        payment_id: UUID,
        order_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate ZATCA compliant invoice"""
        try:
            # Generate unique invoice data
            invoice_uuid = str(uuid4())
            invoice_number = f"INV-{datetime.now().strftime('%Y%m%d')}-{str(order_id)[:8]}"
            
            # Get current timestamp
            invoice_date = datetime.utcnow()
            
            # Calculate tax amounts (15% VAT for Saudi Arabia)
            vat_rate = 0.15
            
            # Mock order data if not provided
            if not order_data:
                order_data = await self._get_order_data(order_id)
            
            subtotal = order_data.get("subtotal", 100.0)
            vat_amount = subtotal * vat_rate
            total_amount = subtotal + vat_amount

            # Create invoice structure
            invoice_data = {
                "invoice_uuid": invoice_uuid,
                "invoice_number": invoice_number,
                "invoice_date": invoice_date.isoformat(),
                "order_id": str(order_id),
                "payment_id": str(payment_id),
                "seller_info": {
                    "name": self.seller_name or "BrainSAIT Store",
                    "name_ar": self.seller_name_ar or "متجر برين سايت",
                    "vat_number": self.vat_number or "300000000000003",
                    "cr_number": self.cr_number or "1010000001",
                },
                "amounts": {
                    "subtotal": subtotal,
                    "vat_amount": vat_amount,
                    "total_amount": total_amount,
                    "currency": "SAR",
                },
                "line_items": order_data.get("line_items", []),
                "qr_code": None,  # Will be generated below
            }

            # Generate QR code for ZATCA compliance
            qr_code_data = self._generate_qr_code_data(invoice_data)
            invoice_data["qr_code"] = qr_code_data

            # Generate PDF URL (mock for now)
            pdf_url = f"/api/v1/invoices/{order_id}/pdf"
            invoice_data["pdf_url"] = pdf_url

            if self.enabled and self.vat_number:
                # Submit to ZATCA if enabled
                zatca_response = await self._submit_to_zatca(invoice_data)
                invoice_data.update(zatca_response)

            return invoice_data

        except Exception as e:
            logger.error(f"ZATCA invoice generation failed: {e}")
            # Return minimal invoice data even if ZATCA fails
            return {
                "invoice_uuid": str(uuid4()),
                "invoice_number": f"INV-{datetime.now().strftime('%Y%m%d')}-{str(order_id)[:8]}",
                "status": "failed",
                "error": str(e),
            }

    async def _get_order_data(self, order_id: UUID) -> Dict[str, Any]:
        """Get order data for invoice generation"""
        # Mock order data - in real implementation, fetch from database
        return {
            "subtotal": 100.0,
            "line_items": [
                {
                    "name": "Product Item",
                    "name_ar": "عنصر المنتج",
                    "quantity": 1,
                    "unit_price": 100.0,
                    "vat_rate": 0.15,
                    "vat_amount": 15.0,
                    "total": 115.0,
                }
            ],
        }

    def _generate_qr_code_data(self, invoice_data: Dict[str, Any]) -> str:
        """Generate QR code data for ZATCA compliance"""
        try:
            # ZATCA QR code format (TLV - Tag Length Value)
            seller_name = invoice_data["seller_info"]["name"]
            vat_number = invoice_data["seller_info"]["vat_number"]
            timestamp = invoice_data["invoice_date"]
            total_amount = invoice_data["amounts"]["total_amount"]
            vat_amount = invoice_data["amounts"]["vat_amount"]

            # Create TLV structure
            tlv_data = ""
            
            # Tag 1: Seller Name
            tlv_data += self._create_tlv_field(1, seller_name)
            
            # Tag 2: VAT Number
            tlv_data += self._create_tlv_field(2, vat_number)
            
            # Tag 3: Timestamp
            tlv_data += self._create_tlv_field(3, timestamp)
            
            # Tag 4: Total Amount
            tlv_data += self._create_tlv_field(4, str(total_amount))
            
            # Tag 5: VAT Amount
            tlv_data += self._create_tlv_field(5, str(vat_amount))

            # Encode to base64
            qr_data = base64.b64encode(tlv_data.encode()).decode()

            # Generate QR code image
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(qr_data)
            qr.make(fit=True)

            return qr_data

        except Exception as e:
            logger.error(f"QR code generation failed: {e}")
            return ""

    def _create_tlv_field(self, tag: int, value: str) -> str:
        """Create TLV (Tag Length Value) field"""
        tag_byte = chr(tag)
        length_byte = chr(len(value.encode('utf-8')))
        return tag_byte + length_byte + value

    async def _submit_to_zatca(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit invoice to ZATCA for compliance"""
        try:
            # This is a mock implementation
            # In production, you would submit to actual ZATCA endpoints
            
            # Mock ZATCA submission
            zatca_response = {
                "zatca_status": "approved",
                "zatca_hash": hashlib.sha256(
                    invoice_data["invoice_uuid"].encode()
                ).hexdigest(),
                "zatca_signature": "mock_signature",
                "submission_date": datetime.utcnow().isoformat(),
            }

            logger.info(f"Mock ZATCA submission for invoice {invoice_data['invoice_uuid']}")
            return zatca_response

        except Exception as e:
            logger.error(f"ZATCA submission failed: {e}")
            return {
                "zatca_status": "failed",
                "zatca_error": str(e),
            }

    def validate_vat_number(self, vat_number: str) -> bool:
        """Validate Saudi VAT number format"""
        if not vat_number:
            return False
        
        # Remove spaces and special characters
        clean_vat = "".join(filter(str.isdigit, vat_number))
        
        # Saudi VAT numbers are 15 digits
        if len(clean_vat) != 15:
            return False
        
        # Should start with 3 and end with 3
        if not (clean_vat.startswith("3") and clean_vat.endswith("3")):
            return False
        
        return True

    def calculate_vat(self, amount: float, vat_rate: float = 0.15) -> Dict[str, float]:
        """Calculate VAT amounts"""
        vat_amount = amount * vat_rate
        total_amount = amount + vat_amount
        
        return {
            "subtotal": amount,
            "vat_rate": vat_rate,
            "vat_amount": round(vat_amount, 2),
            "total_amount": round(total_amount, 2),
        }

    async def generate_simplified_invoice(
        self, 
        order_id: UUID,
        amount: float,
        customer_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate simplified tax invoice (B2C)"""
        try:
            invoice_uuid = str(uuid4())
            invoice_number = f"SINV-{datetime.now().strftime('%Y%m%d')}-{str(order_id)[:8]}"
            
            vat_calc = self.calculate_vat(amount)
            
            invoice_data = {
                "invoice_uuid": invoice_uuid,
                "invoice_number": invoice_number,
                "invoice_type": "simplified",
                "invoice_date": datetime.utcnow().isoformat(),
                "order_id": str(order_id),
                "seller_info": {
                    "name": self.seller_name or "BrainSAIT Store",
                    "vat_number": self.vat_number or "300000000000003",
                },
                "customer_info": customer_info or {},
                "amounts": vat_calc,
                "qr_code": None,
            }

            # Generate QR code
            qr_code_data = self._generate_qr_code_data(invoice_data)
            invoice_data["qr_code"] = qr_code_data

            return invoice_data

        except Exception as e:
            logger.error(f"Simplified invoice generation failed: {e}")
            raise

    async def get_invoice_pdf(self, invoice_uuid: str) -> bytes:
        """Generate PDF for invoice (mock implementation)"""
        # This would typically generate an actual PDF
        # For now, return a mock PDF content
        pdf_content = f"Mock PDF for invoice {invoice_uuid}".encode()
        return pdf_content