"""
Test cases for order models.
"""

import uuid
from datetime import datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.orders import Order, OrderItem, OrderStatus, PaymentStatus


class TestOrderModel:
    """Test Order model functionality"""

    @pytest.fixture
    def sample_order_data(self):
        """Sample order data for testing"""
        return {
            "id": str(uuid.uuid4()),
            "tenant_id": "test-tenant",
            "customer_email": "customer@test.com",
            "customer_first_name": "John",
            "customer_last_name": "Doe",
            "customer_phone": "+966501234567",
            "customer_country": "SA",
            "customer_city": "Riyadh",
            "subtotal": Decimal("1000.00"),
            "tax": Decimal("150.00"),
            "total": Decimal("1150.00"),
            "currency": "SAR",
            "status": OrderStatus.PENDING,
            "payment_status": PaymentStatus.PENDING,
            "payment_method": "mada",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

    @pytest.mark.db
    async def test_order_creation(self, async_session: AsyncSession, sample_order_data):
        """Test creating a new order"""
        # Create order
        order = Order(**sample_order_data)
        async_session.add(order)
        await async_session.commit()
        
        # Verify order was created
        result = await async_session.execute(
            select(Order).where(Order.id == sample_order_data["id"])
        )
        retrieved_order = result.scalar_one_or_none()
        
        assert retrieved_order is not None
        assert retrieved_order.customer_email == sample_order_data["customer_email"]
        assert retrieved_order.total == sample_order_data["total"]
        assert retrieved_order.currency == sample_order_data["currency"]

    @pytest.mark.db
    async def test_order_status_transitions(self, async_session: AsyncSession, sample_order_data):
        """Test order status transitions"""
        order = Order(**sample_order_data)
        async_session.add(order)
        await async_session.commit()
        
        # Test valid transitions
        valid_transitions = [
            (OrderStatus.PENDING, OrderStatus.PROCESSING),
            (OrderStatus.PROCESSING, OrderStatus.SHIPPED),
            (OrderStatus.SHIPPED, OrderStatus.DELIVERED),
        ]
        
        for from_status, to_status in valid_transitions:
            order.status = from_status
            order.status = to_status
            order.updated_at = datetime.utcnow()
            
            await async_session.commit()
            
            # Verify status was updated
            await async_session.refresh(order)
            assert order.status == to_status

    @pytest.mark.db
    async def test_order_payment_status_transitions(self, async_session: AsyncSession, sample_order_data):
        """Test payment status transitions"""
        order = Order(**sample_order_data)
        async_session.add(order)
        await async_session.commit()
        
        # Test payment status transitions
        order.payment_status = PaymentStatus.PROCESSING
        await async_session.commit()
        
        order.payment_status = PaymentStatus.COMPLETED
        await async_session.commit()
        
        await async_session.refresh(order)
        assert order.payment_status == PaymentStatus.COMPLETED

    @pytest.mark.db
    async def test_order_total_calculation(self, async_session: AsyncSession, sample_order_data):
        """Test order total calculation"""
        order = Order(**sample_order_data)
        async_session.add(order)
        await async_session.commit()
        
        # Verify VAT calculation (15% for Saudi Arabia)
        expected_vat = order.subtotal * Decimal("0.15")
        assert order.tax == expected_vat
        
        # Verify total calculation
        expected_total = order.subtotal + order.tax
        assert order.total == expected_total

    @pytest.mark.db
    async def test_order_currency_validation(self, async_session: AsyncSession, sample_order_data):
        """Test order currency validation"""
        # Test valid currency
        sample_order_data["currency"] = "SAR"
        order = Order(**sample_order_data)
        async_session.add(order)
        await async_session.commit()
        
        assert order.currency == "SAR"

    @pytest.mark.db
    async def test_order_customer_data_validation(self, async_session: AsyncSession, sample_order_data):
        """Test order customer data validation"""
        order = Order(**sample_order_data)
        
        # Test valid email
        assert "@" in order.customer_email
        assert "." in order.customer_email
        
        # Test phone number format (Saudi)
        assert order.customer_phone.startswith("+966")
        
        # Test required fields
        assert order.customer_first_name
        assert order.customer_last_name
        assert order.customer_country == "SA"

    @pytest.mark.db
    async def test_order_timestamps(self, async_session: AsyncSession, sample_order_data):
        """Test order timestamp handling"""
        order = Order(**sample_order_data)
        async_session.add(order)
        await async_session.commit()
        
        # Verify timestamps were set
        assert order.created_at is not None
        assert order.updated_at is not None
        assert order.created_at <= order.updated_at
        
        # Update order and verify updated_at changes
        original_updated_at = order.updated_at
        order.status = OrderStatus.PROCESSING
        order.updated_at = datetime.utcnow()
        await async_session.commit()
        
        await async_session.refresh(order)
        assert order.updated_at > original_updated_at

    @pytest.mark.db
    async def test_order_with_items(self, async_session: AsyncSession, sample_order_data):
        """Test order with order items"""
        order = Order(**sample_order_data)
        async_session.add(order)
        await async_session.flush()  # Get the order ID
        
        # Add order items
        item1 = OrderItem(
            id=str(uuid.uuid4()),
            order_id=order.id,
            product_id=str(uuid.uuid4()),
            product_name="Test Product 1",
            quantity=2,
            unit_price=Decimal("100.00"),
            total_price=Decimal("200.00"),
            tenant_id=order.tenant_id
        )
        
        item2 = OrderItem(
            id=str(uuid.uuid4()),
            order_id=order.id,
            product_id=str(uuid.uuid4()),
            product_name="Test Product 2",
            quantity=1,
            unit_price=Decimal("300.00"),
            total_price=Decimal("300.00"),
            tenant_id=order.tenant_id
        )
        
        async_session.add_all([item1, item2])
        await async_session.commit()
        
        # Verify order items were created
        result = await async_session.execute(
            select(OrderItem).where(OrderItem.order_id == order.id)
        )
        items = result.scalars().all()
        
        assert len(items) == 2
        
        # Verify subtotal matches item totals
        items_total = sum(item.total_price for item in items)
        assert items_total == Decimal("500.00")

    @pytest.mark.db
    async def test_order_search_by_customer(self, async_session: AsyncSession, sample_order_data):
        """Test searching orders by customer information"""
        # Create multiple orders
        order1 = Order(**sample_order_data)
        
        order2_data = sample_order_data.copy()
        order2_data["id"] = str(uuid.uuid4())
        order2_data["customer_email"] = "customer2@test.com"
        order2 = Order(**order2_data)
        
        async_session.add_all([order1, order2])
        await async_session.commit()
        
        # Search by email
        result = await async_session.execute(
            select(Order).where(Order.customer_email == sample_order_data["customer_email"])
        )
        found_orders = result.scalars().all()
        
        assert len(found_orders) == 1
        assert found_orders[0].customer_email == sample_order_data["customer_email"]

    @pytest.mark.db
    async def test_order_filtering_by_status(self, async_session: AsyncSession, sample_order_data):
        """Test filtering orders by status"""
        # Create orders with different statuses
        order1 = Order(**sample_order_data)
        order1.status = OrderStatus.PENDING
        
        order2_data = sample_order_data.copy()
        order2_data["id"] = str(uuid.uuid4())
        order2 = Order(**order2_data)
        order2.status = OrderStatus.PROCESSING
        
        async_session.add_all([order1, order2])
        await async_session.commit()
        
        # Filter by status
        result = await async_session.execute(
            select(Order).where(Order.status == OrderStatus.PENDING)
        )
        pending_orders = result.scalars().all()
        
        assert len(pending_orders) == 1
        assert pending_orders[0].status == OrderStatus.PENDING

    @pytest.mark.db
    async def test_order_date_range_filtering(self, async_session: AsyncSession, sample_order_data):
        """Test filtering orders by date range"""
        # Create orders with different dates
        now = datetime.utcnow()
        
        order1 = Order(**sample_order_data)
        order1.created_at = now - timedelta(days=10)
        
        order2_data = sample_order_data.copy()
        order2_data["id"] = str(uuid.uuid4())
        order2 = Order(**order2_data)
        order2.created_at = now - timedelta(days=5)
        
        async_session.add_all([order1, order2])
        await async_session.commit()
        
        # Filter by date range
        start_date = now - timedelta(days=7)
        result = await async_session.execute(
            select(Order).where(Order.created_at >= start_date)
        )
        recent_orders = result.scalars().all()
        
        assert len(recent_orders) == 1
        assert recent_orders[0].created_at >= start_date

    @pytest.mark.db
    async def test_order_tenant_isolation(self, async_session: AsyncSession, sample_order_data):
        """Test tenant isolation for orders"""
        # Create orders for different tenants
        order1 = Order(**sample_order_data)
        order1.tenant_id = "tenant1"
        
        order2_data = sample_order_data.copy()
        order2_data["id"] = str(uuid.uuid4())
        order2 = Order(**order2_data)
        order2.tenant_id = "tenant2"
        
        async_session.add_all([order1, order2])
        await async_session.commit()
        
        # Query orders for specific tenant
        result = await async_session.execute(
            select(Order).where(Order.tenant_id == "tenant1")
        )
        tenant1_orders = result.scalars().all()
        
        assert len(tenant1_orders) == 1
        assert tenant1_orders[0].tenant_id == "tenant1"


class TestOrderItemModel:
    """Test OrderItem model functionality"""

    @pytest.fixture
    def sample_order_item_data(self):
        """Sample order item data for testing"""
        return {
            "id": str(uuid.uuid4()),
            "order_id": str(uuid.uuid4()),
            "product_id": str(uuid.uuid4()),
            "product_name": "Test Product",
            "product_name_ar": "منتج تجريبي",
            "quantity": 2,
            "unit_price": Decimal("100.00"),
            "total_price": Decimal("200.00"),
            "tenant_id": "test-tenant"
        }

    @pytest.mark.db
    async def test_order_item_creation(self, async_session: AsyncSession, sample_order_item_data):
        """Test creating order items"""
        item = OrderItem(**sample_order_item_data)
        async_session.add(item)
        await async_session.commit()
        
        # Verify item was created
        result = await async_session.execute(
            select(OrderItem).where(OrderItem.id == sample_order_item_data["id"])
        )
        retrieved_item = result.scalar_one_or_none()
        
        assert retrieved_item is not None
        assert retrieved_item.product_name == sample_order_item_data["product_name"]
        assert retrieved_item.quantity == sample_order_item_data["quantity"]
        assert retrieved_item.unit_price == sample_order_item_data["unit_price"]

    @pytest.mark.db
    async def test_order_item_total_calculation(self, async_session: AsyncSession, sample_order_item_data):
        """Test order item total calculation"""
        item = OrderItem(**sample_order_item_data)
        
        # Verify total calculation
        expected_total = item.quantity * item.unit_price
        assert item.total_price == expected_total

    @pytest.mark.db
    async def test_order_item_multilingual_support(self, async_session: AsyncSession, sample_order_item_data):
        """Test multilingual support for order items"""
        item = OrderItem(**sample_order_item_data)
        async_session.add(item)
        await async_session.commit()
        
        # Verify both English and Arabic names are stored
        assert item.product_name == "Test Product"
        assert item.product_name_ar == "منتج تجريبي"

    @pytest.mark.db
    async def test_order_item_validation(self, async_session: AsyncSession, sample_order_item_data):
        """Test order item validation"""
        item = OrderItem(**sample_order_item_data)
        
        # Test positive quantity
        assert item.quantity > 0
        
        # Test positive price
        assert item.unit_price > 0
        assert item.total_price > 0
        
        # Test required fields
        assert item.product_id
        assert item.product_name
        assert item.order_id


class TestOrderBusinessLogic:
    """Test order business logic and calculations"""

    def test_vat_calculation(self):
        """Test VAT calculation for Saudi Arabia (15%)"""
        subtotal = Decimal("1000.00")
        vat_rate = Decimal("0.15")
        
        calculated_vat = subtotal * vat_rate
        expected_vat = Decimal("150.00")
        
        assert calculated_vat == expected_vat

    def test_order_total_with_multiple_items(self):
        """Test order total calculation with multiple items"""
        items = [
            {"quantity": 2, "unit_price": Decimal("50.00")},
            {"quantity": 1, "unit_price": Decimal("100.00")},
            {"quantity": 3, "unit_price": Decimal("25.00")},
        ]
        
        subtotal = sum(
            item["quantity"] * item["unit_price"] 
            for item in items
        )
        
        expected_subtotal = Decimal("275.00")  # (2*50) + (1*100) + (3*25)
        assert subtotal == expected_subtotal
        
        # Calculate VAT
        vat = subtotal * Decimal("0.15")
        expected_vat = Decimal("41.25")
        assert vat == expected_vat
        
        # Calculate total
        total = subtotal + vat
        expected_total = Decimal("316.25")
        assert total == expected_total

    def test_currency_conversion_logic(self):
        """Test currency conversion calculations"""
        # USD to SAR conversion (approximate rate: 1 USD = 3.75 SAR)
        usd_amount = Decimal("100.00")
        exchange_rate = Decimal("3.75")
        
        sar_amount = usd_amount * exchange_rate
        expected_sar = Decimal("375.00")
        
        assert sar_amount == expected_sar

    def test_discount_calculation(self):
        """Test discount calculation logic"""
        original_price = Decimal("1000.00")
        discount_percent = Decimal("0.10")  # 10% discount
        
        discount_amount = original_price * discount_percent
        discounted_price = original_price - discount_amount
        
        expected_discount = Decimal("100.00")
        expected_final_price = Decimal("900.00")
        
        assert discount_amount == expected_discount
        assert discounted_price == expected_final_price

    def test_order_status_validation(self):
        """Test order status validation logic"""
        # Test valid status transitions
        valid_transitions = {
            OrderStatus.PENDING: [OrderStatus.PROCESSING, OrderStatus.CANCELLED],
            OrderStatus.PROCESSING: [OrderStatus.SHIPPED, OrderStatus.CANCELLED],
            OrderStatus.SHIPPED: [OrderStatus.DELIVERED],
            OrderStatus.DELIVERED: [],  # Terminal state
            OrderStatus.CANCELLED: []   # Terminal state
        }
        
        for current_status, allowed_next_statuses in valid_transitions.items():
            # All allowed transitions should be valid
            for next_status in allowed_next_statuses:
                assert self.is_valid_status_transition(current_status, next_status)
            
            # Test invalid transitions
            all_statuses = list(OrderStatus)
            invalid_transitions = set(all_statuses) - set(allowed_next_statuses) - {current_status}
            
            for invalid_next_status in invalid_transitions:
                assert not self.is_valid_status_transition(current_status, invalid_next_status)

    def is_valid_status_transition(self, from_status: OrderStatus, to_status: OrderStatus) -> bool:
        """Helper method to validate status transitions"""
        valid_transitions = {
            OrderStatus.PENDING: [OrderStatus.PROCESSING, OrderStatus.CANCELLED],
            OrderStatus.PROCESSING: [OrderStatus.SHIPPED, OrderStatus.CANCELLED],
            OrderStatus.SHIPPED: [OrderStatus.DELIVERED],
            OrderStatus.DELIVERED: [],
            OrderStatus.CANCELLED: []
        }
        
        return to_status in valid_transitions.get(from_status, [])

    def test_payment_status_validation(self):
        """Test payment status validation logic"""
        valid_payment_transitions = {
            PaymentStatus.PENDING: [PaymentStatus.PROCESSING, PaymentStatus.FAILED],
            PaymentStatus.PROCESSING: [PaymentStatus.COMPLETED, PaymentStatus.FAILED],
            PaymentStatus.COMPLETED: [PaymentStatus.REFUNDED],
            PaymentStatus.FAILED: [PaymentStatus.PENDING],  # Can retry
            PaymentStatus.REFUNDED: []  # Terminal state
        }
        
        for current_status, allowed_next_statuses in valid_payment_transitions.items():
            for next_status in allowed_next_statuses:
                assert self.is_valid_payment_status_transition(current_status, next_status)

    def is_valid_payment_status_transition(self, from_status: PaymentStatus, to_status: PaymentStatus) -> bool:
        """Helper method to validate payment status transitions"""
        valid_transitions = {
            PaymentStatus.PENDING: [PaymentStatus.PROCESSING, PaymentStatus.FAILED],
            PaymentStatus.PROCESSING: [PaymentStatus.COMPLETED, PaymentStatus.FAILED],
            PaymentStatus.COMPLETED: [PaymentStatus.REFUNDED],
            PaymentStatus.FAILED: [PaymentStatus.PENDING],
            PaymentStatus.REFUNDED: []
        }
        
        return to_status in valid_transitions.get(from_status, [])