"""
Test cases for payment provider services (Mada, STC Pay, Stripe)
"""

import hashlib
import hmac
import json
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from httpx import Response
from fastapi import HTTPException

from app.services.payment_providers import MadaService, STCPayService, StripeService


class TestStripeService:
    """Test Stripe payment service"""

    @pytest.fixture
    def stripe_service(self):
        """Create Stripe service instance"""
        with patch('app.services.payment_providers.settings') as mock_settings:
            mock_settings.STRIPE_SECRET_KEY = "sk_test_123"
            return StripeService()

    @pytest.mark.asyncio
    async def test_create_payment_intent_success(self, stripe_service):
        """Test successful Stripe payment intent creation"""
        amount = 100.00
        currency = "SAR"
        metadata = {"order_id": str(uuid4())}

        mock_intent = MagicMock()
        mock_intent.client_secret = "pi_test_secret"
        mock_intent.id = "pi_test_123"
        mock_intent.status = "requires_payment_method"

        with patch.object(stripe_service.stripe.PaymentIntent, 'create', return_value=mock_intent):
            result = await stripe_service.create_payment_intent(amount, currency, metadata)

            assert result["client_secret"] == "pi_test_secret"
            assert result["payment_intent_id"] == "pi_test_123"
            assert result["status"] == "requires_payment_method"

    @pytest.mark.asyncio
    async def test_create_payment_intent_failure(self, stripe_service):
        """Test Stripe payment intent creation failure"""
        import stripe as stripe_lib

        with patch.object(
            stripe_service.stripe.PaymentIntent,
            'create',
            side_effect=stripe_lib.error.StripeError("Test error")
        ):
            with pytest.raises(HTTPException) as exc_info:
                await stripe_service.create_payment_intent(100.00, "SAR")

            assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_confirm_payment_success(self, stripe_service):
        """Test successful payment confirmation"""
        payment_intent_id = "pi_test_123"

        mock_intent = MagicMock()
        mock_intent.id = payment_intent_id
        mock_intent.status = "succeeded"
        mock_intent.amount = 10000  # In cents
        mock_intent.currency = "sar"

        with patch.object(stripe_service.stripe.PaymentIntent, 'retrieve', return_value=mock_intent):
            result = await stripe_service.confirm_payment(payment_intent_id)

            assert result["id"] == payment_intent_id
            assert result["status"] == "succeeded"
            assert result["amount"] == 100.00
            assert result["currency"] == "SAR"


class TestMadaService:
    """Test Mada payment service"""

    @pytest.fixture
    def mada_service(self):
        """Create Mada service instance"""
        with patch('app.services.payment_providers.settings') as mock_settings:
            mock_settings.MADA_MERCHANT_ID = "test_merchant"
            mock_settings.MADA_API_KEY = "test_api_key"
            mock_settings.MADA_ENDPOINT = "https://api.mada.test"
            mock_settings.API_BASE_URL = "http://localhost:8000"
            return MadaService()

    @pytest.mark.asyncio
    async def test_create_payment_intent_success(self, mada_service):
        """Test successful Mada payment intent creation"""
        amount = 100.00
        order_id = uuid4()
        customer_info = {
            "name": "Test Customer",
            "email": "test@example.com",
            "phone": "+966501234567"
        }

        mock_response = Response(
            status_code=200,
            json={
                "payment_id": "mada_test_123",
                "redirect_url": "https://mada.test/pay/123",
                "status": "pending",
                "expires_at": "2024-01-01T12:00:00Z"
            }
        )

        with patch.object(mada_service.client, 'post', return_value=mock_response):
            result = await mada_service.create_payment_intent(
                amount=amount,
                order_id=order_id,
                customer_info=customer_info
            )

            assert result["payment_id"] == "mada_test_123"
            assert result["redirect_url"] == "https://mada.test/pay/123"
            assert result["status"] == "pending"

    @pytest.mark.asyncio
    async def test_verify_payment_success(self, mada_service):
        """Test successful Mada payment verification"""
        payment_id = "mada_test_123"

        mock_response = Response(
            status_code=200,
            json={
                "payment_id": payment_id,
                "status": "success",
                "amount": "100.00",
                "currency": "SAR",
                "paid_at": "2024-01-01T12:00:00Z",
                "card": {"last4": "1234"}
            }
        )

        with patch.object(mada_service.client, 'get', return_value=mock_response):
            result = await mada_service.verify_payment(payment_id)

            assert result["payment_id"] == payment_id
            assert result["status"] == "success"
            assert result["amount"] == 100.00
            assert result["card_last4"] == "1234"
            assert result["card_brand"] == "mada"

    @pytest.mark.asyncio
    async def test_create_payment_intent_api_error(self, mada_service):
        """Test Mada payment intent creation with API error"""
        mock_response = Response(
            status_code=400,
            text="Invalid request"
        )

        with patch.object(mada_service.client, 'post', return_value=mock_response):
            with pytest.raises(HTTPException) as exc_info:
                await mada_service.create_payment_intent(
                    amount=100.00,
                    order_id=uuid4(),
                    customer_info={"name": "Test", "email": "test@example.com", "phone": "+966501234567"}
                )

            assert exc_info.value.status_code == 400

    def test_generate_signature(self, mada_service):
        """Test Mada signature generation"""
        payload = {"merchant_id": "test", "amount": "100.00"}

        signature = mada_service._generate_signature(payload)

        assert isinstance(signature, str)
        assert len(signature) == 64  # SHA-256 hex digest length

        # Verify signature is consistent
        signature_2 = mada_service._generate_signature(payload)
        assert signature == signature_2

    def test_verify_webhook_signature_valid(self, mada_service):
        """Test webhook signature verification with valid signature"""
        payload = {"payment_id": "123", "status": "success"}
        signature = mada_service._generate_signature(payload)

        result = mada_service.verify_webhook_signature(payload, signature)

        assert result is True

    def test_verify_webhook_signature_invalid(self, mada_service):
        """Test webhook signature verification with invalid signature"""
        payload = {"payment_id": "123", "status": "success"}
        invalid_signature = "invalid_signature_123"

        result = mada_service.verify_webhook_signature(payload, invalid_signature)

        assert result is False


class TestSTCPayService:
    """Test STC Pay payment service"""

    @pytest.fixture
    def stc_service(self):
        """Create STC Pay service instance"""
        with patch('app.services.payment_providers.settings') as mock_settings:
            mock_settings.STC_PAY_MERCHANT_ID = "test_merchant"
            mock_settings.STC_PAY_API_KEY = "test_api_key"
            mock_settings.STC_PAY_ENDPOINT = "https://api.stcpay.test"
            mock_settings.API_BASE_URL = "http://localhost:8000"
            return STCPayService()

    @pytest.mark.asyncio
    async def test_create_payment_intent_success(self, stc_service):
        """Test successful STC Pay payment intent creation"""
        amount = 100.00
        order_id = uuid4()
        customer_info = {
            "name": "Test Customer",
            "phone": "+966501234567"
        }

        mock_response = Response(
            status_code=200,
            json={
                "transaction_id": "stc_test_123",
                "qr_code": "base64_qr_code_data",
                "payment_url": "https://stcpay.test/pay/123",
                "status": "pending",
                "expires_at": "2024-01-01T12:00:00Z"
            }
        )

        with patch.object(stc_service.client, 'post', return_value=mock_response):
            result = await stc_service.create_payment_intent(
                amount=amount,
                order_id=order_id,
                customer_info=customer_info
            )

            assert result["transaction_id"] == "stc_test_123"
            assert result["qr_code"] == "base64_qr_code_data"
            assert result["payment_url"] == "https://stcpay.test/pay/123"
            assert result["status"] == "pending"

    @pytest.mark.asyncio
    async def test_verify_payment_success(self, stc_service):
        """Test successful STC Pay transaction verification"""
        transaction_id = "stc_test_123"

        mock_response = Response(
            status_code=200,
            json={
                "transaction_id": transaction_id,
                "status": "completed",
                "amount": "100.00",
                "currency": "SAR",
                "payment_time": "2024-01-01T12:00:00Z",
                "reference_id": str(uuid4())
            }
        )

        with patch.object(stc_service.client, 'get', return_value=mock_response):
            result = await stc_service.verify_payment(transaction_id)

            assert result["transaction_id"] == transaction_id
            assert result["status"] == "completed"
            assert result["amount"] == 100.00
            assert result["currency"] == "SAR"

    @pytest.mark.asyncio
    async def test_generate_qr_code_success(self, stc_service):
        """Test STC Pay QR code generation"""
        amount = 100.00
        order_id = uuid4()

        mock_response = Response(
            status_code=200,
            json={
                "qr_code": "base64_qr_code_data",
                "qr_code_url": "https://stcpay.test/qr/123.png",
                "expires_at": "2024-01-01T12:00:00Z"
            }
        )

        with patch.object(stc_service.client, 'post', return_value=mock_response):
            result = await stc_service.generate_qr_code(amount, order_id)

            assert result["qr_code"] == "base64_qr_code_data"
            assert result["qr_code_url"] == "https://stcpay.test/qr/123.png"
            assert "expires_at" in result

    @pytest.mark.asyncio
    async def test_create_payment_intent_api_error(self, stc_service):
        """Test STC Pay payment intent creation with API error"""
        mock_response = Response(
            status_code=500,
            text="Internal server error"
        )

        with patch.object(stc_service.client, 'post', return_value=mock_response):
            with pytest.raises(HTTPException) as exc_info:
                await stc_service.create_payment_intent(
                    amount=100.00,
                    order_id=uuid4(),
                    customer_info={"name": "Test", "phone": "+966501234567"}
                )

            assert exc_info.value.status_code == 500

    def test_generate_signature(self, stc_service):
        """Test STC Pay signature generation"""
        payload = {"merchant_id": "test", "amount": "100.00"}

        signature = stc_service._generate_signature(payload)

        assert isinstance(signature, str)
        assert len(signature) == 64  # SHA-256 hex digest length

    def test_verify_webhook_signature_valid(self, stc_service):
        """Test webhook signature verification with valid signature"""
        payload = {"transaction_id": "123", "status": "completed"}
        signature = stc_service._generate_signature(payload)

        result = stc_service.verify_webhook_signature(payload, signature)

        assert result is True

    def test_verify_webhook_signature_invalid(self, stc_service):
        """Test webhook signature verification with invalid signature"""
        payload = {"transaction_id": "123", "status": "completed"}
        invalid_signature = "invalid_signature_123"

        result = stc_service.verify_webhook_signature(payload, invalid_signature)

        assert result is False


class TestPaymentProvidersIntegration:
    """Integration tests for payment providers"""

    @pytest.mark.asyncio
    async def test_all_services_initialize(self):
        """Test that all payment services can be initialized"""
        with patch('app.services.payment_providers.settings') as mock_settings:
            mock_settings.STRIPE_SECRET_KEY = "sk_test_123"
            mock_settings.MADA_MERCHANT_ID = "test_merchant"
            mock_settings.MADA_API_KEY = "test_api_key"
            mock_settings.MADA_ENDPOINT = "https://api.mada.test"
            mock_settings.STC_PAY_MERCHANT_ID = "test_merchant"
            mock_settings.STC_PAY_API_KEY = "test_api_key"
            mock_settings.STC_PAY_ENDPOINT = "https://api.stcpay.test"
            mock_settings.API_BASE_URL = "http://localhost:8000"

            stripe_service = StripeService()
            mada_service = MadaService()
            stc_service = STCPayService()

            assert stripe_service is not None
            assert mada_service is not None
            assert stc_service is not None
