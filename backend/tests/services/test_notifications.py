"""
Test cases for notification service
"""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from httpx import Response

from app.services.notifications import NotificationService


class TestNotificationService:
    """Test notification service functionality"""

    @pytest.fixture
    def notification_service(self):
        """Create notification service instance"""
        with patch('app.services.notifications.settings') as mock_settings:
            mock_settings.SMTP_SERVER = "smtp.test.com"
            mock_settings.SMTP_PORT = 587
            mock_settings.SMTP_USERNAME = "test@example.com"
            mock_settings.SMTP_PASSWORD = "test_password"
            mock_settings.FROM_EMAIL = "noreply@brainsait.com"
            mock_settings.FROM_NAME = "BrainSAIT Store"
            mock_settings.FROM_NAME_AR = "متجر برين سايت"
            mock_settings.SMS_PROVIDER = "unifonic"
            mock_settings.UNIFONIC_APP_SID = "test_app_sid"
            mock_settings.UNIFONIC_SENDER_ID = "test_sender"
            mock_settings.TAQNYAT_API_KEY = "test_api_key"
            mock_settings.TAQNYAT_SENDER = "test_sender"
            return NotificationService()

    @pytest.mark.asyncio
    async def test_send_payment_confirmation_success(self, notification_service):
        """Test successful payment confirmation email"""
        email = "customer@example.com"
        order_id = uuid4()
        amount = 100.00

        result = await notification_service.send_payment_confirmation(
            email=email,
            order_id=order_id,
            amount=amount,
            language="en"
        )

        assert result is True

    @pytest.mark.asyncio
    async def test_send_payment_confirmation_arabic(self, notification_service):
        """Test payment confirmation email in Arabic"""
        email = "customer@example.com"
        order_id = uuid4()
        amount = 100.00

        result = await notification_service.send_payment_confirmation(
            email=email,
            order_id=order_id,
            amount=amount,
            language="ar"
        )

        assert result is True

    @pytest.mark.asyncio
    async def test_send_payment_failure_success(self, notification_service):
        """Test payment failure notification"""
        email = "customer@example.com"
        order_id = uuid4()
        error_message = "Payment declined"

        result = await notification_service.send_payment_failure(
            email=email,
            order_id=order_id,
            error_message=error_message,
            language="en"
        )

        assert result is True

    @pytest.mark.asyncio
    async def test_send_invoice_notification_success(self, notification_service):
        """Test invoice notification email"""
        email = "customer@example.com"
        invoice_number = "INV-2024-001"
        invoice_url = "https://example.com/invoices/123.pdf"

        result = await notification_service.send_invoice_notification(
            email=email,
            invoice_number=invoice_number,
            invoice_url=invoice_url,
            language="en"
        )

        assert result is True

    @pytest.mark.asyncio
    async def test_send_unifonic_sms_success(self, notification_service):
        """Test successful SMS sending via Unifonic"""
        phone = "+966501234567"
        message = "Payment received successfully"

        mock_response = Response(
            status_code=200,
            json={"success": "true", "message_id": "123"}
        )

        with patch.object(notification_service.http_client, 'post', return_value=mock_response):
            result = await notification_service._send_unifonic_sms(phone, message)

            assert result is True

    @pytest.mark.asyncio
    async def test_send_unifonic_sms_failure(self, notification_service):
        """Test SMS sending failure via Unifonic"""
        phone = "+966501234567"
        message = "Test message"

        mock_response = Response(
            status_code=200,
            json={"success": "false", "error": "Invalid recipient"}
        )

        with patch.object(notification_service.http_client, 'post', return_value=mock_response):
            result = await notification_service._send_unifonic_sms(phone, message)

            assert result is False

    @pytest.mark.asyncio
    async def test_send_unifonic_sms_no_credentials(self):
        """Test SMS sending when credentials are not configured"""
        with patch('app.services.notifications.settings') as mock_settings:
            mock_settings.UNIFONIC_APP_SID = None
            mock_settings.SMS_PROVIDER = "unifonic"
            service = NotificationService()

            result = await service._send_unifonic_sms("+966501234567", "Test")

            assert result is False

    @pytest.mark.asyncio
    async def test_send_taqnyat_sms_success(self, notification_service):
        """Test successful SMS sending via Taqnyat"""
        phone = "+966501234567"
        message = "Payment received successfully"

        mock_response = Response(
            status_code=200,
            json={"statusCode": 200, "messageId": "123"}
        )

        with patch.object(notification_service.http_client, 'post', return_value=mock_response):
            result = await notification_service._send_taqnyat_sms(phone, message)

            assert result is True

    @pytest.mark.asyncio
    async def test_send_taqnyat_sms_failure(self, notification_service):
        """Test SMS sending failure via Taqnyat"""
        phone = "+966501234567"
        message = "Test message"

        mock_response = Response(
            status_code=400,
            text="Invalid request"
        )

        with patch.object(notification_service.http_client, 'post', return_value=mock_response):
            result = await notification_service._send_taqnyat_sms(phone, message)

            assert result is False

    @pytest.mark.asyncio
    async def test_send_payment_confirmation_sms_arabic(self, notification_service):
        """Test payment confirmation SMS in Arabic"""
        phone = "+966501234567"
        order_id = uuid4()
        amount = 100.00

        mock_response = Response(
            status_code=200,
            json={"success": "true", "message_id": "123"}
        )

        with patch.object(notification_service.http_client, 'post', return_value=mock_response):
            result = await notification_service.send_payment_confirmation_sms(
                phone=phone,
                order_id=order_id,
                amount=amount,
                language="ar"
            )

            assert result is True

    @pytest.mark.asyncio
    async def test_send_payment_confirmation_sms_english(self, notification_service):
        """Test payment confirmation SMS in English"""
        phone = "+966501234567"
        order_id = uuid4()
        amount = 100.00

        mock_response = Response(
            status_code=200,
            json={"success": "true", "message_id": "123"}
        )

        with patch.object(notification_service.http_client, 'post', return_value=mock_response):
            result = await notification_service.send_payment_confirmation_sms(
                phone=phone,
                order_id=order_id,
                amount=amount,
                language="en"
            )

            assert result is True

    def test_get_subject_english(self, notification_service):
        """Test email subject generation in English"""
        subject = notification_service._get_subject("payment_confirmation", "en")
        assert "Payment Confirmation" in subject
        assert "BrainSAIT Store" in subject

    def test_get_subject_arabic(self, notification_service):
        """Test email subject generation in Arabic"""
        subject = notification_service._get_subject("payment_confirmation", "ar")
        assert "تأكيد الدفع" in subject
        assert "متجر برين سايت" in subject

    def test_get_email_body_payment_confirmation_english(self, notification_service):
        """Test email body generation for payment confirmation in English"""
        data = {
            "order_id": str(uuid4()),
            "amount": "100.00",
            "currency": "SAR"
        }

        body = notification_service._get_email_body("payment_confirmation", "en", data)

        assert "Payment Confirmation" in body
        assert data["order_id"] in body
        assert data["amount"] in body
        assert "BrainSAIT Store" in body

    def test_get_email_body_payment_confirmation_arabic(self, notification_service):
        """Test email body generation for payment confirmation in Arabic"""
        data = {
            "order_id": str(uuid4()),
            "amount": "100.00",
            "currency": "SAR"
        }

        body = notification_service._get_email_body("payment_confirmation", "ar", data)

        assert "تم استلام الدفع بنجاح" in body
        assert data["order_id"] in body
        assert 'dir="rtl"' in body

    def test_get_email_body_payment_failure_english(self, notification_service):
        """Test email body generation for payment failure in English"""
        data = {
            "order_id": str(uuid4()),
            "error": "Payment declined"
        }

        body = notification_service._get_email_body("payment_failure", "en", data)

        assert "Payment Failed" in body
        assert data["order_id"] in body
        assert data["error"] in body

    def test_get_email_body_invoice_ready_arabic(self, notification_service):
        """Test email body generation for invoice notification in Arabic"""
        data = {
            "invoice_number": "INV-2024-001",
            "invoice_url": "https://example.com/invoice.pdf"
        }

        body = notification_service._get_email_body("invoice_ready", "ar", data)

        assert "فاتورتك جاهزة" in body
        assert data["invoice_number"] in body
        assert data["invoice_url"] in body
        assert 'dir="rtl"' in body
