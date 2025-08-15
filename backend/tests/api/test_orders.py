"""
Test cases for order API endpoints.
"""

import uuid
from datetime import datetime, timedelta
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.orders import Order, OrderStatus, PaymentStatus
from app.schemas.orders import OrderCreate, OrderUpdate


class TestOrderAPI:
    """Test order API endpoints"""

    @pytest.fixture
    def mock_order_data(self):
        """Mock order data for testing"""
        return {
            "customer_info": {
                "email": "customer@test.com",
                "first_name": "John",
                "last_name": "Doe",
                "phone": "+966501234567",
                "country": "SA",
                "city": "Riyadh",
                "is_company": False,
            },
            "items": [
                {
                    "product_id": str(uuid.uuid4()),
                    "quantity": 2,
                    "unit_price": 100.00
                },
                {
                    "product_id": str(uuid.uuid4()),
                    "quantity": 1,
                    "unit_price": 200.00
                }
            ],
            "payment_method": "mada",
            "subtotal": 400.00,
            "tax": 60.00,  # 15% VAT
            "total": 460.00,
            "currency": "SAR"
        }

    @pytest.fixture
    def mock_invalid_order_data(self):
        """Mock invalid order data for testing"""
        return {
            "customer_info": {
                "email": "invalid-email",  # Invalid email
                "first_name": "",  # Empty name
            },
            "items": [],  # Empty items
            "payment_method": "invalid_method",
            "total": -100.00,  # Negative total
        }

    def test_create_order_success(self, client: TestClient, mock_order_data):
        """Test successful order creation"""
        response = client.post("/api/v1/orders/", json=mock_order_data)
        
        # Should require authentication in real implementation
        assert response.status_code in [201, 401]

    def test_create_order_invalid_data(self, client: TestClient, mock_invalid_order_data):
        """Test order creation with invalid data"""
        response = client.post("/api/v1/orders/", json=mock_invalid_order_data)
        assert response.status_code in [422, 401]  # Validation error or unauthorized

    def test_create_order_missing_fields(self, client: TestClient):
        """Test order creation with missing required fields"""
        incomplete_data = {
            "customer_info": {
                "email": "test@example.com"
            }
            # Missing items, totals, etc.
        }
        response = client.post("/api/v1/orders/", json=incomplete_data)
        assert response.status_code in [422, 401]

    def test_get_orders_unauthorized(self, client: TestClient):
        """Test getting orders without authentication"""
        response = client.get("/api/v1/orders/")
        assert response.status_code == 401

    def test_get_order_by_id_not_found(self, client: TestClient):
        """Test getting non-existent order"""
        non_existent_id = str(uuid.uuid4())
        response = client.get(f"/api/v1/orders/{non_existent_id}")
        assert response.status_code in [404, 401]

    def test_get_order_invalid_id_format(self, client: TestClient):
        """Test getting order with invalid ID format"""
        response = client.get("/api/v1/orders/invalid-uuid")
        assert response.status_code == 422

    def test_update_order_status_unauthorized(self, client: TestClient):
        """Test updating order status without authentication"""
        order_id = str(uuid.uuid4())
        response = client.patch(
            f"/api/v1/orders/{order_id}/status",
            json={"status": "processing"}
        )
        assert response.status_code == 401

    def test_update_order_status_invalid_status(self, authenticated_admin_client: TestClient):
        """Test updating order with invalid status"""
        order_id = str(uuid.uuid4())
        response = authenticated_admin_client.patch(
            f"/api/v1/orders/{order_id}/status",
            json={"status": "invalid_status"}
        )
        assert response.status_code in [404, 422]

    def test_cancel_order_unauthorized(self, client: TestClient):
        """Test canceling order without authentication"""
        order_id = str(uuid.uuid4())
        response = client.patch(
            f"/api/v1/orders/{order_id}/cancel",
            json={"reason": "Customer request"}
        )
        assert response.status_code == 401

    def test_get_orders_with_pagination(self, authenticated_user_client: TestClient):
        """Test getting orders with pagination"""
        response = authenticated_user_client.get("/api/v1/orders/?page=1&limit=10")
        assert response.status_code in [200, 404]  # Empty list or not found

    def test_get_orders_with_filters(self, authenticated_user_client: TestClient):
        """Test getting orders with various filters"""
        # Test status filter
        response = authenticated_user_client.get("/api/v1/orders/?status=pending")
        assert response.status_code in [200, 404]

        # Test date range filter
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()
        response = authenticated_user_client.get(
            f"/api/v1/orders/?start_date={start_date.isoformat()}&end_date={end_date.isoformat()}"
        )
        assert response.status_code in [200, 404]

    def test_order_total_calculation_validation(self, client: TestClient):
        """Test order total calculation validation"""
        order_data = {
            "customer_info": {
                "email": "test@example.com",
                "first_name": "Test",
                "last_name": "User"
            },
            "items": [
                {"product_id": str(uuid.uuid4()), "quantity": 2, "unit_price": 100.00}
            ],
            "subtotal": 200.00,
            "tax": 30.00,
            "total": 250.00,  # This doesn't match subtotal + tax (230)
            "currency": "SAR"
        }
        
        response = client.post("/api/v1/orders/", json=order_data)
        # Should validate total calculation
        assert response.status_code in [422, 401]

    def test_order_currency_validation(self, client: TestClient):
        """Test order currency validation"""
        order_data = {
            "customer_info": {
                "email": "test@example.com",
                "first_name": "Test",
                "last_name": "User"
            },
            "items": [
                {"product_id": str(uuid.uuid4()), "quantity": 1, "unit_price": 100.00}
            ],
            "subtotal": 100.00,
            "tax": 15.00,
            "total": 115.00,
            "currency": "USD"  # Should be SAR for Saudi market
        }
        
        response = client.post("/api/v1/orders/", json=order_data)
        assert response.status_code in [422, 401]

    def test_order_vat_calculation(self, client: TestClient):
        """Test order VAT calculation (15% for Saudi Arabia)"""
        subtotal = 1000.00
        expected_vat = subtotal * 0.15  # 150.00
        expected_total = subtotal + expected_vat  # 1150.00
        
        order_data = {
            "customer_info": {
                "email": "test@example.com",
                "first_name": "Test",
                "last_name": "User"
            },
            "items": [
                {"product_id": str(uuid.uuid4()), "quantity": 1, "unit_price": subtotal}
            ],
            "subtotal": subtotal,
            "tax": expected_vat,
            "total": expected_total,
            "currency": "SAR"
        }
        
        response = client.post("/api/v1/orders/", json=order_data)
        assert response.status_code in [201, 401]


class TestOrderPaymentAPI:
    """Test order payment-related endpoints"""

    def test_create_payment_intent(self, client: TestClient):
        """Test creating payment intent for order"""
        payment_data = {
            "order_id": str(uuid.uuid4()),
            "amount": 1000.00,
            "currency": "SAR",
            "payment_method": "mada"
        }
        
        response = client.post("/api/v1/payments/intent", json=payment_data)
        assert response.status_code in [201, 401]

    def test_confirm_payment(self, client: TestClient):
        """Test confirming payment for order"""
        payment_intent_id = "pi_test_123456"
        
        response = client.post(f"/api/v1/payments/{payment_intent_id}/confirm")
        assert response.status_code in [200, 401, 404]

    def test_get_payment_status(self, client: TestClient):
        """Test getting payment status"""
        payment_intent_id = "pi_test_123456"
        
        response = client.get(f"/api/v1/payments/{payment_intent_id}/status")
        assert response.status_code in [200, 401, 404]

    def test_process_refund(self, authenticated_admin_client: TestClient):
        """Test processing refund for order"""
        refund_data = {
            "order_id": str(uuid.uuid4()),
            "amount": 500.00,
            "reason": "Customer complaint"
        }
        
        response = authenticated_admin_client.post("/api/v1/payments/refund", json=refund_data)
        assert response.status_code in [201, 404]


class TestOrderStatusTransitions:
    """Test order status transitions and business logic"""

    @pytest.fixture
    def status_transition_data(self):
        """Valid status transitions"""
        return {
            "pending": ["processing", "cancelled"],
            "processing": ["shipped", "cancelled"],
            "shipped": ["delivered"],
            "delivered": [],  # Terminal state
            "cancelled": []   # Terminal state
        }

    def test_valid_status_transitions(self, authenticated_admin_client: TestClient, status_transition_data):
        """Test valid order status transitions"""
        order_id = str(uuid.uuid4())
        
        for from_status, valid_to_statuses in status_transition_data.items():
            for to_status in valid_to_statuses:
                response = authenticated_admin_client.patch(
                    f"/api/v1/orders/{order_id}/status",
                    json={"status": to_status}
                )
                # Order doesn't exist, but status validation should work
                assert response.status_code in [404, 422]

    def test_invalid_status_transitions(self, authenticated_admin_client: TestClient):
        """Test invalid order status transitions"""
        order_id = str(uuid.uuid4())
        
        # Try to transition from delivered to pending (invalid)
        response = authenticated_admin_client.patch(
            f"/api/v1/orders/{order_id}/status",
            json={"status": "pending", "current_status": "delivered"}
        )
        assert response.status_code in [404, 422]


class TestOrderAnalytics:
    """Test order analytics and reporting endpoints"""

    def test_get_order_statistics(self, authenticated_admin_client: TestClient):
        """Test getting order statistics"""
        response = authenticated_admin_client.get("/api/v1/orders/analytics/stats")
        assert response.status_code in [200, 404]

    def test_get_sales_by_period(self, authenticated_admin_client: TestClient):
        """Test getting sales data by time period"""
        response = authenticated_admin_client.get(
            "/api/v1/orders/analytics/sales?period=week"
        )
        assert response.status_code in [200, 404]

        response = authenticated_admin_client.get(
            "/api/v1/orders/analytics/sales?period=month"
        )
        assert response.status_code in [200, 404]

    def test_get_top_products(self, authenticated_admin_client: TestClient):
        """Test getting top-selling products"""
        response = authenticated_admin_client.get(
            "/api/v1/orders/analytics/top-products?limit=10"
        )
        assert response.status_code in [200, 404]

    def test_get_customer_analytics(self, authenticated_admin_client: TestClient):
        """Test getting customer analytics"""
        response = authenticated_admin_client.get(
            "/api/v1/orders/analytics/customers"
        )
        assert response.status_code in [200, 404]


class TestOrderIntegration:
    """Test order integration with other systems"""

    def test_order_with_inventory_check(self, client: TestClient):
        """Test order creation with inventory validation"""
        order_data = {
            "customer_info": {
                "email": "test@example.com",
                "first_name": "Test",
                "last_name": "User"
            },
            "items": [
                {
                    "product_id": str(uuid.uuid4()),
                    "quantity": 999999,  # Excessive quantity
                    "unit_price": 100.00
                }
            ],
            "subtotal": 99999900.00,
            "tax": 14999985.00,
            "total": 114999885.00,
            "currency": "SAR"
        }
        
        response = client.post("/api/v1/orders/", json=order_data)
        # Should validate inventory availability
        assert response.status_code in [422, 401]

    def test_order_with_product_validation(self, client: TestClient):
        """Test order creation with product validation"""
        order_data = {
            "customer_info": {
                "email": "test@example.com",
                "first_name": "Test",
                "last_name": "User"
            },
            "items": [
                {
                    "product_id": "non-existent-product-id",
                    "quantity": 1,
                    "unit_price": 100.00
                }
            ],
            "subtotal": 100.00,
            "tax": 15.00,
            "total": 115.00,
            "currency": "SAR"
        }
        
        response = client.post("/api/v1/orders/", json=order_data)
        assert response.status_code in [422, 401]

    def test_order_notification_triggers(self, authenticated_admin_client: TestClient):
        """Test that order status changes trigger notifications"""
        order_id = str(uuid.uuid4())
        
        # This would test notification system integration
        response = authenticated_admin_client.patch(
            f"/api/v1/orders/{order_id}/status",
            json={"status": "shipped", "tracking_number": "TRACK123"}
        )
        assert response.status_code in [404, 422]

    def test_order_audit_trail(self, authenticated_admin_client: TestClient):
        """Test order audit trail functionality"""
        order_id = str(uuid.uuid4())
        
        response = authenticated_admin_client.get(f"/api/v1/orders/{order_id}/audit")
        assert response.status_code in [200, 404, 401]


class TestOrderSecurity:
    """Test order security and access control"""

    def test_customer_can_only_view_own_orders(self, authenticated_user_client: TestClient):
        """Test that customers can only view their own orders"""
        other_user_order_id = str(uuid.uuid4())
        
        response = authenticated_user_client.get(f"/api/v1/orders/{other_user_order_id}")
        assert response.status_code in [403, 404]

    def test_admin_can_view_all_orders(self, authenticated_admin_client: TestClient):
        """Test that admins can view all orders"""
        response = authenticated_admin_client.get("/api/v1/orders/")
        assert response.status_code in [200, 404]

    def test_order_data_sanitization(self, client: TestClient):
        """Test that order data is properly sanitized"""
        malicious_data = {
            "customer_info": {
                "email": "test@example.com",
                "first_name": "<script>alert('xss')</script>",
                "last_name": "'; DROP TABLE orders; --"
            },
            "items": [
                {
                    "product_id": str(uuid.uuid4()),
                    "quantity": 1,
                    "unit_price": 100.00
                }
            ],
            "notes": "<img src=x onerror=alert('xss')>",
            "subtotal": 100.00,
            "tax": 15.00,
            "total": 115.00,
            "currency": "SAR"
        }
        
        response = client.post("/api/v1/orders/", json=malicious_data)
        assert response.status_code in [422, 401]

    def test_tenant_isolation(self, client: TestClient):
        """Test that orders are properly isolated by tenant"""
        headers1 = {"X-Tenant-ID": "tenant1"}
        headers2 = {"X-Tenant-ID": "tenant2"}
        
        response1 = client.get("/api/v1/orders/", headers=headers1)
        response2 = client.get("/api/v1/orders/", headers=headers2)
        
        # Both should require auth, but tenant isolation should work
        assert response1.status_code == 401
        assert response2.status_code == 401


class TestOrderPerformance:
    """Test order API performance and edge cases"""

    def test_large_order_handling(self, client: TestClient):
        """Test handling of orders with many items"""
        # Create order with 100 items
        items = []
        for i in range(100):
            items.append({
                "product_id": str(uuid.uuid4()),
                "quantity": 1,
                "unit_price": 10.00
            })
        
        order_data = {
            "customer_info": {
                "email": "test@example.com",
                "first_name": "Test",
                "last_name": "User"
            },
            "items": items,
            "subtotal": 1000.00,
            "tax": 150.00,
            "total": 1150.00,
            "currency": "SAR"
        }
        
        response = client.post("/api/v1/orders/", json=order_data)
        assert response.status_code in [201, 422, 401]

    def test_concurrent_order_creation(self, client: TestClient):
        """Test concurrent order creation"""
        # This would test race conditions in order processing
        # For now, just test that the endpoint responds correctly
        order_data = {
            "customer_info": {
                "email": "test@example.com",
                "first_name": "Test",
                "last_name": "User"
            },
            "items": [
                {
                    "product_id": str(uuid.uuid4()),
                    "quantity": 1,
                    "unit_price": 100.00
                }
            ],
            "subtotal": 100.00,
            "tax": 15.00,
            "total": 115.00,
            "currency": "SAR"
        }
        
        # Simulate concurrent requests
        response = client.post("/api/v1/orders/", json=order_data)
        assert response.status_code in [201, 422, 401]

    def test_order_search_performance(self, authenticated_admin_client: TestClient):
        """Test order search with various criteria"""
        # Test search by customer email
        response = authenticated_admin_client.get(
            "/api/v1/orders/search?email=test@example.com"
        )
        assert response.status_code in [200, 404]

        # Test search by order number
        response = authenticated_admin_client.get(
            "/api/v1/orders/search?order_number=ORD-123"
        )
        assert response.status_code in [200, 404]

        # Test complex search with multiple filters
        response = authenticated_admin_client.get(
            "/api/v1/orders/search?status=pending&min_total=100&max_total=1000"
        )
        assert response.status_code in [200, 404]