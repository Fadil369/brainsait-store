"""
Test cases for order service layer.
"""

import uuid
from decimal import Decimal
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.order_service import OrderService
from app.models.orders import Order, OrderItem, OrderStatus, PaymentStatus
from app.schemas.orders import OrderCreate, OrderItemCreate


class TestOrderService:
    """Test OrderService functionality"""

    @pytest.fixture
    def order_service(self):
        """Create OrderService instance for testing"""
        return OrderService()

    @pytest.fixture
    def mock_order_create_data(self):
        """Mock order creation data"""
        return OrderCreate(
            customer_info={
                "email": "customer@test.com",
                "first_name": "John",
                "last_name": "Doe",
                "phone": "+966501234567",
                "country": "SA",
                "city": "Riyadh",
                "is_company": False
            },
            items=[
                OrderItemCreate(
                    product_id=str(uuid.uuid4()),
                    quantity=2,
                    unit_price=Decimal("100.00")
                ),
                OrderItemCreate(
                    product_id=str(uuid.uuid4()),
                    quantity=1,
                    unit_price=Decimal("200.00")
                )
            ],
            payment_method="mada",
            currency="SAR"
        )

    @pytest.fixture
    def mock_products_data(self):
        """Mock product data for validation"""
        return [
            {
                "id": str(uuid.uuid4()),
                "name": "Test Product 1",
                "price": Decimal("100.00"),
                "status": "active",
                "inventory": 10
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Test Product 2", 
                "price": Decimal("200.00"),
                "status": "active",
                "inventory": 5
            }
        ]

    async def test_create_order_success(self, order_service: OrderService, mock_order_create_data, mock_products_data):
        """Test successful order creation"""
        with patch('app.services.order_service.OrderService._validate_products') as mock_validate, \
             patch('app.services.order_service.OrderService._calculate_totals') as mock_calculate, \
             patch('app.services.order_service.OrderService._create_order_record') as mock_create:
            
            mock_validate.return_value = True
            mock_calculate.return_value = {
                "subtotal": Decimal("400.00"),
                "tax": Decimal("60.00"),
                "total": Decimal("460.00")
            }
            mock_create.return_value = Order(
                id=str(uuid.uuid4()),
                customer_email=mock_order_create_data.customer_info["email"],
                total=Decimal("460.00"),
                status=OrderStatus.PENDING
            )
            
            result = await order_service.create_order(mock_order_create_data, "test-tenant")
            
            assert result is not None
            assert result.customer_email == mock_order_create_data.customer_info["email"]
            assert result.status == OrderStatus.PENDING
            
            mock_validate.assert_called_once()
            mock_calculate.assert_called_once()
            mock_create.assert_called_once()

    async def test_create_order_invalid_products(self, order_service: OrderService, mock_order_create_data):
        """Test order creation with invalid products"""
        with patch('app.services.order_service.OrderService._validate_products') as mock_validate:
            mock_validate.side_effect = ValueError("Product not found")
            
            with pytest.raises(ValueError, match="Product not found"):
                await order_service.create_order(mock_order_create_data, "test-tenant")

    async def test_calculate_order_totals(self, order_service: OrderService):
        """Test order totals calculation"""
        items = [
            {"quantity": 2, "unit_price": Decimal("100.00")},
            {"quantity": 1, "unit_price": Decimal("200.00")}
        ]
        
        totals = order_service._calculate_totals(items)
        
        expected_subtotal = Decimal("400.00")  # (2*100) + (1*200)
        expected_tax = Decimal("60.00")        # 15% VAT
        expected_total = Decimal("460.00")     # subtotal + tax
        
        assert totals["subtotal"] == expected_subtotal
        assert totals["tax"] == expected_tax
        assert totals["total"] == expected_total

    async def test_calculate_order_totals_edge_cases(self, order_service: OrderService):
        """Test order totals calculation edge cases"""
        # Test with zero amounts
        zero_items = []
        zero_totals = order_service._calculate_totals(zero_items)
        
        assert zero_totals["subtotal"] == Decimal("0.00")
        assert zero_totals["tax"] == Decimal("0.00")
        assert zero_totals["total"] == Decimal("0.00")
        
        # Test with decimal precision
        decimal_items = [
            {"quantity": 1, "unit_price": Decimal("33.33")},
            {"quantity": 2, "unit_price": Decimal("66.67")}
        ]
        
        decimal_totals = order_service._calculate_totals(decimal_items)
        
        expected_subtotal = Decimal("166.67")
        expected_tax = expected_subtotal * Decimal("0.15")
        expected_total = expected_subtotal + expected_tax
        
        assert decimal_totals["subtotal"] == expected_subtotal
        assert abs(decimal_totals["tax"] - expected_tax) < Decimal("0.01")
        assert abs(decimal_totals["total"] - expected_total) < Decimal("0.01")

    async def test_validate_products_success(self, order_service: OrderService):
        """Test successful product validation"""
        mock_products = [
            MagicMock(id="prod-1", status="active", inventory=10),
            MagicMock(id="prod-2", status="active", inventory=5)
        ]
        
        items = [
            {"product_id": "prod-1", "quantity": 2},
            {"product_id": "prod-2", "quantity": 1}
        ]
        
        with patch('app.services.order_service.ProductService.get_products_by_ids') as mock_get_products:
            mock_get_products.return_value = mock_products
            
            # Should not raise exception
            await order_service._validate_products(items, AsyncMock())

    async def test_validate_products_not_found(self, order_service: OrderService):
        """Test product validation with non-existent products"""
        mock_products = []  # No products found
        
        items = [
            {"product_id": "non-existent", "quantity": 1}
        ]
        
        with patch('app.services.order_service.ProductService.get_products_by_ids') as mock_get_products:
            mock_get_products.return_value = mock_products
            
            with pytest.raises(ValueError, match="Product .* not found"):
                await order_service._validate_products(items, AsyncMock())

    async def test_validate_products_insufficient_inventory(self, order_service: OrderService):
        """Test product validation with insufficient inventory"""
        mock_products = [
            MagicMock(id="prod-1", status="active", inventory=1)  # Only 1 in stock
        ]
        
        items = [
            {"product_id": "prod-1", "quantity": 5}  # Requesting 5
        ]
        
        with patch('app.services.order_service.ProductService.get_products_by_ids') as mock_get_products:
            mock_get_products.return_value = mock_products
            
            with pytest.raises(ValueError, match="Insufficient inventory"):
                await order_service._validate_products(items, AsyncMock())

    async def test_validate_products_inactive_product(self, order_service: OrderService):
        """Test product validation with inactive products"""
        mock_products = [
            MagicMock(id="prod-1", status="inactive", inventory=10)
        ]
        
        items = [
            {"product_id": "prod-1", "quantity": 1}
        ]
        
        with patch('app.services.order_service.ProductService.get_products_by_ids') as mock_get_products:
            mock_get_products.return_value = mock_products
            
            with pytest.raises(ValueError, match="Product .* is not available"):
                await order_service._validate_products(items, AsyncMock())

    async def test_update_order_status_valid_transition(self, order_service: OrderService):
        """Test updating order status with valid transition"""
        mock_order = MagicMock()
        mock_order.status = OrderStatus.PENDING
        mock_order.updated_at = datetime.utcnow()
        
        with patch('app.services.order_service.OrderService._get_order_by_id') as mock_get, \
             patch('app.services.order_service.OrderService._save_order') as mock_save:
            
            mock_get.return_value = mock_order
            
            result = await order_service.update_order_status(
                "order-id", 
                OrderStatus.PROCESSING, 
                AsyncMock(), 
                "test-tenant"
            )
            
            assert result.status == OrderStatus.PROCESSING
            mock_save.assert_called_once()

    async def test_update_order_status_invalid_transition(self, order_service: OrderService):
        """Test updating order status with invalid transition"""
        mock_order = MagicMock()
        mock_order.status = OrderStatus.DELIVERED  # Terminal state
        
        with patch('app.services.order_service.OrderService._get_order_by_id') as mock_get:
            mock_get.return_value = mock_order
            
            with pytest.raises(ValueError, match="Invalid status transition"):
                await order_service.update_order_status(
                    "order-id",
                    OrderStatus.PENDING,
                    AsyncMock(),
                    "test-tenant"
                )

    async def test_cancel_order_valid(self, order_service: OrderService):
        """Test canceling an order that can be canceled"""
        mock_order = MagicMock()
        mock_order.status = OrderStatus.PENDING
        mock_order.payment_status = PaymentStatus.PENDING
        
        with patch('app.services.order_service.OrderService._get_order_by_id') as mock_get, \
             patch('app.services.order_service.OrderService._save_order') as mock_save:
            
            mock_get.return_value = mock_order
            
            result = await order_service.cancel_order(
                "order-id",
                "Customer request",
                AsyncMock(),
                "test-tenant"
            )
            
            assert result.status == OrderStatus.CANCELLED
            mock_save.assert_called_once()

    async def test_cancel_order_invalid_status(self, order_service: OrderService):
        """Test canceling an order that cannot be canceled"""
        mock_order = MagicMock()
        mock_order.status = OrderStatus.DELIVERED
        
        with patch('app.services.order_service.OrderService._get_order_by_id') as mock_get:
            mock_get.return_value = mock_order
            
            with pytest.raises(ValueError, match="Cannot cancel order"):
                await order_service.cancel_order(
                    "order-id",
                    "Customer request",
                    AsyncMock(),
                    "test-tenant"
                )

    async def test_get_orders_with_pagination(self, order_service: OrderService):
        """Test getting orders with pagination"""
        mock_orders = [MagicMock() for _ in range(5)]
        mock_total = 25
        
        with patch('app.services.order_service.OrderService._query_orders') as mock_query:
            mock_query.return_value = (mock_orders, mock_total)
            
            result = await order_service.get_orders(
                page=1,
                limit=5,
                db=AsyncMock(),
                tenant_id="test-tenant"
            )
            
            assert len(result["orders"]) == 5
            assert result["total"] == 25
            assert result["page"] == 1
            assert result["pages"] == 5

    async def test_get_orders_with_filters(self, order_service: OrderService):
        """Test getting orders with various filters"""
        filters = {
            "status": OrderStatus.PENDING,
            "customer_email": "customer@test.com",
            "start_date": datetime.utcnow() - timedelta(days=30),
            "end_date": datetime.utcnow()
        }
        
        with patch('app.services.order_service.OrderService._query_orders') as mock_query:
            mock_query.return_value = ([], 0)
            
            await order_service.get_orders(
                filters=filters,
                db=AsyncMock(),
                tenant_id="test-tenant"
            )
            
            # Verify filters were passed to query
            mock_query.assert_called_once()
            call_args = mock_query.call_args[1]
            assert "status" in call_args.get("filters", {})

    async def test_get_order_analytics(self, order_service: OrderService):
        """Test getting order analytics"""
        mock_analytics = {
            "total_orders": 100,
            "total_revenue": Decimal("50000.00"),
            "average_order_value": Decimal("500.00"),
            "orders_by_status": {
                "pending": 10,
                "processing": 20,
                "delivered": 65,
                "cancelled": 5
            }
        }
        
        with patch('app.services.order_service.OrderService._calculate_analytics') as mock_calc:
            mock_calc.return_value = mock_analytics
            
            result = await order_service.get_order_analytics(
                start_date=datetime.utcnow() - timedelta(days=30),
                end_date=datetime.utcnow(),
                db=AsyncMock(),
                tenant_id="test-tenant"
            )
            
            assert result["total_orders"] == 100
            assert result["total_revenue"] == Decimal("50000.00")
            assert result["orders_by_status"]["delivered"] == 65

    async def test_process_order_payment(self, order_service: OrderService):
        """Test processing order payment"""
        mock_order = MagicMock()
        mock_order.payment_status = PaymentStatus.PENDING
        mock_order.total = Decimal("1000.00")
        
        with patch('app.services.order_service.OrderService._get_order_by_id') as mock_get, \
             patch('app.services.order_service.PaymentService.process_payment') as mock_payment, \
             patch('app.services.order_service.OrderService._save_order') as mock_save:
            
            mock_get.return_value = mock_order
            mock_payment.return_value = {"status": "completed", "transaction_id": "txn-123"}
            
            result = await order_service.process_order_payment(
                "order-id",
                "pi_test_123",
                AsyncMock(),
                "test-tenant"
            )
            
            assert result.payment_status == PaymentStatus.COMPLETED
            mock_payment.assert_called_once()
            mock_save.assert_called_once()

    async def test_process_order_refund(self, order_service: OrderService):
        """Test processing order refund"""
        mock_order = MagicMock()
        mock_order.payment_status = PaymentStatus.COMPLETED
        mock_order.total = Decimal("1000.00")
        
        with patch('app.services.order_service.OrderService._get_order_by_id') as mock_get, \
             patch('app.services.order_service.PaymentService.process_refund') as mock_refund, \
             patch('app.services.order_service.OrderService._save_order') as mock_save:
            
            mock_get.return_value = mock_order
            mock_refund.return_value = {"status": "refunded", "refund_id": "ref-123"}
            
            result = await order_service.process_order_refund(
                "order-id",
                Decimal("500.00"),  # Partial refund
                "Customer complaint",
                AsyncMock(),
                "test-tenant"
            )
            
            mock_refund.assert_called_once()
            mock_save.assert_called_once()

    async def test_send_order_notifications(self, order_service: OrderService):
        """Test sending order status notifications"""
        mock_order = MagicMock()
        mock_order.customer_email = "customer@test.com"
        mock_order.status = OrderStatus.SHIPPED
        
        with patch('app.services.order_service.NotificationService.send_order_notification') as mock_notify:
            await order_service._send_order_notification(mock_order, "status_updated")
            
            mock_notify.assert_called_once_with(
                mock_order.customer_email,
                "status_updated",
                {"order": mock_order}
            )

    async def test_inventory_integration(self, order_service: OrderService):
        """Test order creation with inventory updates"""
        mock_order_data = MagicMock()
        mock_order_data.items = [
            MagicMock(product_id="prod-1", quantity=2),
            MagicMock(product_id="prod-2", quantity=1)
        ]
        
        with patch('app.services.order_service.InventoryService.reserve_inventory') as mock_reserve, \
             patch('app.services.order_service.OrderService._create_order_record') as mock_create:
            
            mock_create.return_value = MagicMock()
            
            await order_service.create_order_with_inventory(
                mock_order_data,
                AsyncMock(),
                "test-tenant"
            )
            
            # Should reserve inventory for each item
            assert mock_reserve.call_count == 2

    async def test_order_audit_trail(self, order_service: OrderService):
        """Test order audit trail functionality"""
        mock_order = MagicMock()
        mock_order.id = "order-123"
        
        with patch('app.services.order_service.AuditService.log_order_event') as mock_audit:
            await order_service._log_order_event(
                mock_order,
                "status_changed",
                {"from": "pending", "to": "processing"},
                "admin-user"
            )
            
            mock_audit.assert_called_once_with(
                "order-123",
                "status_changed",
                {"from": "pending", "to": "processing"},
                "admin-user"
            )

    async def test_order_service_error_handling(self, order_service: OrderService):
        """Test error handling in order service"""
        with patch('app.services.order_service.OrderService._get_order_by_id') as mock_get:
            mock_get.side_effect = Exception("Database error")
            
            with pytest.raises(Exception, match="Database error"):
                await order_service.get_order_by_id(
                    "order-id",
                    AsyncMock(),
                    "test-tenant"
                )

    async def test_concurrent_order_processing(self, order_service: OrderService):
        """Test handling concurrent order processing"""
        # This would test race conditions and locking mechanisms
        # For now, test that the service handles concurrent requests gracefully
        
        mock_order_data = MagicMock()
        
        with patch('app.services.order_service.OrderService._acquire_order_lock') as mock_lock, \
             patch('app.services.order_service.OrderService._create_order_record') as mock_create:
            
            mock_lock.return_value = True
            mock_create.return_value = MagicMock()
            
            result = await order_service.create_order_with_lock(
                mock_order_data,
                AsyncMock(),
                "test-tenant"
            )
            
            mock_lock.assert_called_once()
            assert result is not None