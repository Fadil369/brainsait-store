"""
Test cases for ZATCA e-invoicing service
"""

import base64
import json
from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

import pytest
from httpx import Response

from app.services.zatca_service import ZATCAService
from app.models.invoices import Invoice, InvoiceStatus, ZATCAStatus


class TestZATCAService:
    """Test ZATCA service functionality"""

    @pytest.fixture
    def zatca_service(self):
        """Create ZATCA service instance"""
        with patch('app.services.zatca_service.settings') as mock_settings:
            mock_settings.ZATCA_ENABLED = True
            mock_settings.ZATCA_VAT_NUMBER = "300000000000003"
            mock_settings.ZATCA_CR_NUMBER = "1234567890"
            mock_settings.ZATCA_SELLER_NAME = "Test Company"
            mock_settings.ZATCA_SELLER_NAME_AR = "شركة اختبار"
            mock_settings.PRODUCTION = False
            return ZATCAService()

    @pytest.fixture
    def sample_order_id(self):
        """Sample order UUID"""
        return uuid4()

    @pytest.fixture
    def sample_payment_id(self):
        """Sample payment UUID"""
        return uuid4()

    def test_zatca_service_initialization(self, zatca_service):
        """Test ZATCA service initializes correctly"""
        assert zatca_service.enabled is True
        assert zatca_service.vat_number == "300000000000003"
        assert zatca_service.cr_number == "1234567890"
        assert zatca_service.VAT_RATE == Decimal("0.15")

    @pytest.mark.asyncio
    async def test_generate_invoice(self, zatca_service, sample_order_id, sample_payment_id):
        """Test invoice generation"""
        result = await zatca_service.generate_invoice(
            order_id=sample_order_id,
            payment_id=sample_payment_id,
            db=None
        )

        assert "invoice_number" in result
        assert "invoice_uuid" in result
        assert "qr_code" in result
        assert "invoice_hash" in result
        assert "xml_invoice" in result
        assert result["zatca_status"] == ZATCAStatus.PENDING.value
        assert result["subtotal"] > 0
        assert result["tax_amount"] > 0
        assert result["total_amount"] > 0

    def test_generate_zatca_qr_code(self, zatca_service):
        """Test ZATCA QR code generation in TLV format"""
        seller_name = "Test Company"
        vat_number = "300000000000003"
        timestamp = datetime.utcnow()
        total_amount = Decimal("115.00")
        tax_amount = Decimal("15.00")
        invoice_hash = "test_hash_123"

        qr_code = zatca_service._generate_zatca_qr_code(
            seller_name=seller_name,
            vat_number=vat_number,
            timestamp=timestamp,
            total_amount=total_amount,
            tax_amount=tax_amount,
            invoice_hash=invoice_hash,
        )

        # QR code should be base64 encoded
        assert isinstance(qr_code, str)
        assert len(qr_code) > 0

        # Decode and verify TLV structure
        decoded = base64.b64decode(qr_code)
        assert len(decoded) > 0

        # Verify TLV tags are present
        # Tag 1: Seller Name
        assert decoded[0] == 1
        # Tag 2: VAT Number should follow
        assert 2 in decoded
        # Tag 3: Timestamp should follow
        assert 3 in decoded

    def test_generate_invoice_hash(self, zatca_service):
        """Test invoice hash generation"""
        invoice_number = "INV-2024-001"
        issue_date = datetime.utcnow()
        total_amount = Decimal("115.00")

        invoice_hash = zatca_service._generate_invoice_hash(
            invoice_number=invoice_number,
            issue_date=issue_date,
            total_amount=total_amount,
        )

        # Hash should be base64 encoded SHA-256
        assert isinstance(invoice_hash, str)
        assert len(invoice_hash) > 0

        # Should be consistent for same input
        invoice_hash_2 = zatca_service._generate_invoice_hash(
            invoice_number=invoice_number,
            issue_date=issue_date,
            total_amount=total_amount,
        )
        assert invoice_hash == invoice_hash_2

    def test_generate_ubl_xml(self, zatca_service):
        """Test UBL 2.1 XML invoice generation"""
        invoice_number = "INV-2024-001"
        invoice_uuid = str(uuid4())
        issue_date = datetime.utcnow()
        subtotal = Decimal("100.00")
        tax_amount = Decimal("15.00")
        total_amount = Decimal("115.00")
        invoice_hash = "test_hash"

        xml = zatca_service._generate_ubl_xml(
            invoice_number=invoice_number,
            invoice_uuid=invoice_uuid,
            issue_date=issue_date,
            subtotal=subtotal,
            tax_amount=tax_amount,
            total_amount=total_amount,
            invoice_hash=invoice_hash,
        )

        # Verify XML structure
        assert '<?xml version="1.0" encoding="UTF-8"?>' in xml
        assert '<Invoice xmlns=' in xml
        assert f'<cbc:ID>{invoice_number}</cbc:ID>' in xml
        assert f'<cbc:UUID>{invoice_uuid}</cbc:UUID>' in xml
        assert '<cbc:InvoiceTypeCode>388</cbc:InvoiceTypeCode>' in xml
        assert f'<cbc:TaxAmount currencyID="SAR">{tax_amount:.2f}</cbc:TaxAmount>' in xml
        assert '<cbc:Percent>15.00</cbc:Percent>' in xml

    @pytest.mark.asyncio
    async def test_validate_invoice_valid(self, zatca_service):
        """Test invoice validation with valid data"""
        invoice_data = {
            "seller_name": "Test Company",
            "seller_vat_number": "300000000000003",
            "seller_cr_number": "1234567890",
            "buyer_name": "Customer Name",
            "total_amount": "115.00",
            "tax_amount": "15.00",
            "invoice_number": "INV-2024-001",
        }

        result = await zatca_service.validate_invoice(invoice_data)

        assert result["valid"] is True
        assert len(result["errors"]) == 0

    @pytest.mark.asyncio
    async def test_validate_invoice_missing_fields(self, zatca_service):
        """Test invoice validation with missing required fields"""
        invoice_data = {
            "seller_name": "Test Company",
            # Missing other required fields
        }

        result = await zatca_service.validate_invoice(invoice_data)

        assert result["valid"] is False
        assert len(result["errors"]) > 0
        assert any("Missing required field" in error for error in result["errors"])

    @pytest.mark.asyncio
    async def test_validate_invoice_invalid_vat_number(self, zatca_service):
        """Test invoice validation with invalid VAT number"""
        invoice_data = {
            "seller_name": "Test Company",
            "seller_vat_number": "123",  # Invalid - should be 15 digits starting with 3
            "seller_cr_number": "1234567890",
            "buyer_name": "Customer Name",
            "total_amount": "115.00",
            "tax_amount": "15.00",
            "invoice_number": "INV-2024-001",
        }

        result = await zatca_service.validate_invoice(invoice_data)

        assert result["valid"] is False
        assert any("Invalid VAT number" in error for error in result["errors"])

    def test_calculate_vat_from_subtotal(self, zatca_service):
        """Test VAT calculation from subtotal"""
        subtotal = Decimal("100.00")

        result = zatca_service.calculate_vat(subtotal, vat_inclusive=False)

        assert result["subtotal"] == Decimal("100.00")
        assert result["vat_amount"] == Decimal("15.00")
        assert result["total"] == Decimal("115.00")

    def test_calculate_vat_from_total(self, zatca_service):
        """Test VAT extraction from total amount"""
        total = Decimal("115.00")

        result = zatca_service.calculate_vat(total, vat_inclusive=True)

        assert result["subtotal"] == Decimal("100.00")
        assert result["vat_amount"] == Decimal("15.00")
        assert result["total"] == Decimal("115.00")

    @pytest.mark.asyncio
    async def test_generate_invoice_disabled(self, sample_order_id, sample_payment_id):
        """Test invoice generation when ZATCA is disabled"""
        with patch('app.services.zatca_service.settings') as mock_settings:
            mock_settings.ZATCA_ENABLED = False
            service = ZATCAService()

            result = await service.generate_invoice(
                order_id=sample_order_id,
                payment_id=sample_payment_id,
                db=None
            )

            assert result["status"] == "disabled"

    @pytest.mark.asyncio
    async def test_submit_to_zatca_success(self, zatca_service):
        """Test successful ZATCA portal submission"""
        invoice_id = uuid4()

        # Mock database session
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_invoice = MagicMock(spec=Invoice)
        mock_invoice.id = invoice_id
        mock_invoice.zatca_hash = "test_hash"
        mock_invoice.zatca_uuid = str(uuid4())
        mock_invoice.zatca_xml = "<Invoice></Invoice>"
        mock_invoice.tenant_id = "test-tenant"

        mock_result.scalar_one_or_none.return_value = mock_invoice
        mock_db.execute.return_value = mock_result

        # Mock HTTP response
        mock_response = Response(
            status_code=200,
            json={"clearanceStatus": "CLEARED", "status": "approved"}
        )

        with patch.object(zatca_service.client, 'post', return_value=mock_response):
            result = await zatca_service.submit_to_zatca(
                invoice_id=invoice_id,
                submission_type="reporting",
                db=mock_db
            )

            assert result["status"] == "approved"
            assert "zatca_response" in result

    @pytest.mark.asyncio
    async def test_submit_to_zatca_disabled(self, sample_order_id):
        """Test ZATCA submission when disabled"""
        with patch('app.services.zatca_service.settings') as mock_settings:
            mock_settings.ZATCA_ENABLED = False
            service = ZATCAService()

            result = await service.submit_to_zatca(
                invoice_id=uuid4(),
                submission_type="reporting",
                db=AsyncMock()
            )

            assert result["status"] == "disabled"
