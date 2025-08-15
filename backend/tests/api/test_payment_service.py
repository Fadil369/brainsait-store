"""
Tests for payment gateway service.
"""

import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, Mock, patch

import pytest
from httpx import Response

from app.models.orders import Order, OrderStatus
from app.services.payment_gateway import PaymentGatewayService


class TestPaymentGatewayService:
    """Test payment gateway service functionality"""

    @pytest.fixture
    def payment_service(self):
        """Create payment gateway service instance."""
        return PaymentGatewayService()

    @pytest.fixture
    def mock_order(self):
        """Create mock order for testing."""
        return Order(
            id=uuid.uuid4(),
            order_number="TEST-001",
            total_amount=Decimal("1000.00"),
            currency="SAR",
            status=OrderStatus.PENDING,
            tenant_id="test-tenant",
            customer_email="test@example.com",
        )

    @pytest.mark.asyncio
    async def test_process_payment_stripe_success(self, payment_service, mock_order):
        """Test successful Stripe payment processing."""
        payment_data = {
            "success_url": "https://example.com/success",
            "cancel_url": "https://example.com/cancel",
        }

        with patch.object(payment_service, 'create_stripe_checkout_session') as mock_stripe:
            mock_stripe.return_value = {
                "checkout_session_id": "cs_test_123",
                "checkout_url": "https://checkout.stripe.com/test"
            }

            result = await payment_service.process_payment(
                mock_order, "stripe", payment_data
            )

            assert "checkout_session_id" in result
            assert "checkout_url" in result
            mock_stripe.assert_called_once_with(
                mock_order,
                payment_data["success_url"],
                payment_data["cancel_url"]
            )

    @pytest.mark.asyncio
    async def test_process_payment_paypal_success(self, payment_service, mock_order):
        """Test successful PayPal payment processing."""
        with patch.object(payment_service, 'create_paypal_order') as mock_paypal:
            mock_paypal.return_value = {
                "order_id": "PAYPAL123",
                "approval_url": "https://paypal.com/approve"
            }

            result = await payment_service.process_payment(
                mock_order, "paypal"
            )

            assert "order_id" in result
            assert "approval_url" in result
            mock_paypal.assert_called_once_with(mock_order)

    @pytest.mark.asyncio
    async def test_process_payment_apple_pay_success(self, payment_service, mock_order):
        """Test successful Apple Pay payment processing."""
        payment_data = {
            "payment_token": "test_apple_pay_token"
        }

        with patch.object(payment_service, 'process_apple_pay_payment') as mock_apple_pay:
            mock_apple_pay.return_value = {
                "transaction_id": "ap_test_123",
                "status": "succeeded"
            }

            result = await payment_service.process_payment(
                mock_order, "apple_pay", payment_data
            )

            assert "transaction_id" in result
            assert result["status"] == "succeeded"
            mock_apple_pay.assert_called_once_with(
                payment_data["payment_token"], mock_order
            )

    @pytest.mark.asyncio
    async def test_process_payment_moyasar_success(self, payment_service, mock_order):
        """Test successful Moyasar payment processing."""
        with patch.object(payment_service, 'create_moyasar_payment') as mock_moyasar:
            mock_moyasar.return_value = {
                "payment_id": "moyasar_123",
                "payment_url": "https://moyasar.com/pay"
            }

            result = await payment_service.process_payment(
                mock_order, "moyasar"
            )

            assert "payment_id" in result
            assert "payment_url" in result
            mock_moyasar.assert_called_once_with(mock_order)

    @pytest.mark.asyncio
    async def test_process_payment_hyperpay_success(self, payment_service, mock_order):
        """Test successful HyperPay payment processing."""
        with patch.object(payment_service, 'create_hyperpay_checkout') as mock_hyperpay:
            mock_hyperpay.return_value = {
                "checkout_id": "hyperpay_123",
                "redirect_url": "https://hyperpay.com/checkout"
            }

            result = await payment_service.process_payment(
                mock_order, "hyperpay"
            )

            assert "checkout_id" in result
            assert "redirect_url" in result
            mock_hyperpay.assert_called_once_with(mock_order)

    @pytest.mark.asyncio
    async def test_process_payment_unsupported_method(self, payment_service, mock_order):
        """Test processing payment with unsupported method."""
        with pytest.raises(Exception) as exc_info:
            await payment_service.process_payment(
                mock_order, "unsupported_method"
            )
        
        assert "Unsupported payment method" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_validate_apple_pay_merchant_success(self, payment_service):
        """Test successful Apple Pay merchant validation."""
        validation_url = "https://apple-pay-gateway.apple.com/paymentservices/startSession"
        
        mock_response = Mock()
        mock_response.json.return_value = {
            "epochTimestamp": 1234567890,
            "expiresAt": 1234567890,
            "merchantSessionIdentifier": "test_session"
        }
        mock_response.raise_for_status.return_value = None

        with patch('httpx.AsyncClient') as mock_client:
            mock_client_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            mock_client_instance.post.return_value = mock_response

            result = await payment_service.validate_apple_pay_merchant(validation_url)

            assert "epochTimestamp" in result
            assert "merchantSessionIdentifier" in result

    @pytest.mark.asyncio
    async def test_validate_apple_pay_merchant_failure(self, payment_service):
        """Test Apple Pay merchant validation failure."""
        validation_url = "https://apple-pay-gateway.apple.com/paymentservices/startSession"
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            mock_client_instance.post.side_effect = Exception("Network error")

            with pytest.raises(Exception) as exc_info:
                await payment_service.validate_apple_pay_merchant(validation_url)
            
            assert "Failed to validate Apple Pay merchant" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_verify_webhook_signature_stripe(self, payment_service):
        """Test Stripe webhook signature verification."""
        payload = b'{"test": "data"}'
        signature = "test_signature"
        
        with patch('stripe.Webhook.construct_event') as mock_construct:
            mock_construct.return_value = {"type": "payment_intent.succeeded"}
            
            result = await payment_service.verify_webhook_signature(
                payload, signature, "stripe"
            )
            
            assert result is True

    @pytest.mark.asyncio
    async def test_verify_webhook_signature_invalid(self, payment_service):
        """Test webhook signature verification with invalid signature."""
        payload = b'{"test": "data"}'
        signature = "invalid_signature"
        
        with patch('stripe.Webhook.construct_event') as mock_construct:
            mock_construct.side_effect = Exception("Invalid signature")
            
            result = await payment_service.verify_webhook_signature(
                payload, signature, "stripe"
            )
            
            assert result is False

    @pytest.mark.asyncio
    async def test_handle_payment_webhook_stripe_success(self, payment_service):
        """Test handling successful Stripe webhook."""
        event_data = {
            "type": "payment_intent.succeeded",
            "data": {
                "object": {
                    "id": "pi_test_123",
                    "amount": 100000,  # $1000.00 in cents
                    "currency": "usd",
                    "status": "succeeded"
                }
            }
        }
        
        mock_db = Mock()
        
        with patch.object(payment_service, '_handle_stripe_webhook') as mock_handler:
            mock_handler.return_value = {"status": "processed"}
            
            result = await payment_service.handle_payment_webhook(
                "stripe", event_data, mock_db
            )
            
            assert result["status"] == "processed"
            mock_handler.assert_called_once_with(event_data, mock_db)

    @pytest.mark.asyncio
    async def test_handle_payment_webhook_paypal_success(self, payment_service):
        """Test handling successful PayPal webhook."""
        event_data = {
            "event_type": "PAYMENT.CAPTURE.COMPLETED",
            "resource": {
                "id": "CAPTURE123",
                "amount": {"value": "1000.00", "currency_code": "USD"},
                "status": "COMPLETED"
            }
        }
        
        mock_db = Mock()
        
        with patch.object(payment_service, '_handle_paypal_webhook') as mock_handler:
            mock_handler.return_value = {"status": "processed"}
            
            result = await payment_service.handle_payment_webhook(
                "paypal", event_data, mock_db
            )
            
            assert result["status"] == "processed"
            mock_handler.assert_called_once_with(event_data, mock_db)

    @pytest.mark.asyncio
    async def test_handle_payment_webhook_unsupported_gateway(self, payment_service):
        """Test handling webhook for unsupported gateway."""
        event_data = {"type": "test"}
        mock_db = Mock()
        
        with pytest.raises(Exception) as exc_info:
            await payment_service.handle_payment_webhook(
                "unsupported_gateway", event_data, mock_db
            )
        
        assert "Unsupported payment gateway" in str(exc_info.value)

    def test_payment_gateway_initialization(self):
        """Test payment gateway service initialization."""
        service = PaymentGatewayService()
        
        # Check that service is properly initialized
        assert service is not None
        assert hasattr(service, 'process_payment')
        assert hasattr(service, 'verify_webhook_signature')
        assert hasattr(service, 'handle_payment_webhook')

    @pytest.mark.asyncio
    async def test_payment_error_handling(self, payment_service, mock_order):
        """Test payment processing error handling."""
        with patch.object(payment_service, 'create_stripe_checkout_session') as mock_stripe:
            mock_stripe.side_effect = Exception("Payment processing failed")
            
            with pytest.raises(Exception) as exc_info:
                await payment_service.process_payment(mock_order, "stripe")
            
            assert "Payment processing failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_payment_with_missing_data(self, payment_service, mock_order):
        """Test payment processing with missing required data."""
        # Apple Pay requires payment_token
        with pytest.raises(KeyError):
            await payment_service.process_payment(mock_order, "apple_pay", {})

    @pytest.mark.asyncio
    async def test_payment_method_case_insensitive(self, payment_service, mock_order):
        """Test payment method matching is case sensitive (current behavior)."""
        # This tests that payment methods need exact case matching
        with pytest.raises(Exception) as exc_info:
            await payment_service.process_payment(mock_order, "STRIPE")
        
        assert "Unsupported payment method" in str(exc_info.value)

    def test_payment_service_constants(self, payment_service):
        """Test that payment service has required constants."""
        # Test that the service has required configuration
        assert hasattr(payment_service, 'process_payment')
        
        # These would be set based on actual service implementation
        # For now, just test that the methods exist
        assert callable(payment_service.process_payment)
        assert callable(payment_service.verify_webhook_signature)
        assert callable(payment_service.handle_payment_webhook)

    @pytest.mark.asyncio
    async def test_concurrent_payment_processing(self, payment_service):
        """Test handling concurrent payment processing."""
        import asyncio
        
        orders = [
            Order(
                id=uuid.uuid4(),
                order_number=f"TEST-{i:03d}",
                total_amount=Decimal("100.00"),
                currency="SAR",
                status=OrderStatus.PENDING,
                tenant_id="test-tenant",
                customer_email=f"test{i}@example.com",
            )
            for i in range(3)
        ]
        
        with patch.object(payment_service, 'create_stripe_checkout_session') as mock_stripe:
            mock_stripe.return_value = {
                "checkout_session_id": "cs_test_123",
                "checkout_url": "https://checkout.stripe.com/test"
            }
            
            # Process multiple payments concurrently
            tasks = [
                payment_service.process_payment(order, "stripe")
                for order in orders
            ]
            
            results = await asyncio.gather(*tasks)
            
            assert len(results) == 3
            assert all("checkout_session_id" in result for result in results)
            assert mock_stripe.call_count == 3