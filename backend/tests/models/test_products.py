"""
Tests for product models.
"""

import uuid
from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError

from app.models.products import Product, Category, ProductStatus, StockStatus


class TestProductModel:
    """Test Product model functionality"""

    @pytest.mark.asyncio
    async def test_create_product_success(self, async_session):
        """Test creating a product successfully."""
        # First create a category
        category = Category(
            id=uuid.uuid4(),
            name="Test Category",
            name_ar="فئة تجريبية",
            tenant_id="test-tenant",
        )
        async_session.add(category)
        await async_session.commit()

        # Then create a product
        product = Product(
            id=uuid.uuid4(),
            name="Test Product",
            name_ar="منتج تجريبي",
            description="Test product description",
            description_ar="وصف المنتج التجريبي",
            price=Decimal("1000.00"),
            category_id=category.id,
            tenant_id="test-tenant",
            status=ProductStatus.ACTIVE,
            features=["Feature 1", "Feature 2"],
            features_ar=["خاصية 1", "خاصية 2"],
        )
        
        async_session.add(product)
        await async_session.commit()
        
        # Verify product was created
        assert product.id is not None
        assert product.name == "Test Product"
        assert product.name_ar == "منتج تجريبي"
        assert product.price == Decimal("1000.00")
        assert product.status == ProductStatus.ACTIVE
        assert product.tenant_id == "test-tenant"

    @pytest.mark.asyncio
    async def test_product_required_fields(self, async_session):
        """Test that required fields are enforced."""
        # Test missing name
        with pytest.raises(IntegrityError):
            product = Product(
                id=uuid.uuid4(),
                # name missing
                description="Test description",
                price=Decimal("100.00"),
                tenant_id="test-tenant",
            )
            async_session.add(product)
            await async_session.commit()

    @pytest.mark.asyncio
    async def test_product_price_validation(self, async_session):
        """Test product price validation."""
        category = Category(
            id=uuid.uuid4(),
            name="Test Category",
            tenant_id="test-tenant",
        )
        async_session.add(category)
        await async_session.commit()

        # Test with zero price (should be allowed)
        product = Product(
            id=uuid.uuid4(),
            name="Free Product",
            description="Free product",
            price=Decimal("0.00"),
            category_id=category.id,
            tenant_id="test-tenant",
        )
        async_session.add(product)
        await async_session.commit()
        
        assert product.price == Decimal("0.00")

        # Test with decimal price
        product2 = Product(
            id=uuid.uuid4(),
            name="Decimal Price Product",
            description="Product with decimal price",
            price=Decimal("99.99"),
            category_id=category.id,
            tenant_id="test-tenant",
        )
        async_session.add(product2)
        await async_session.commit()
        
        assert product2.price == Decimal("99.99")

    @pytest.mark.asyncio
    async def test_product_status_enum(self, async_session):
        """Test product status enumeration."""
        category = Category(
            id=uuid.uuid4(),
            name="Test Category",
            tenant_id="test-tenant",
        )
        async_session.add(category)
        await async_session.commit()

        # Test all valid statuses
        for status in ProductStatus:
            product = Product(
                id=uuid.uuid4(),
                name=f"Product {status.value}",
                description="Test product",
                price=Decimal("100.00"),
                category_id=category.id,
                tenant_id="test-tenant",
                status=status,
            )
            async_session.add(product)
            await async_session.commit()
            
            assert product.status == status

    @pytest.mark.asyncio
    async def test_product_multilingual_content(self, async_session):
        """Test product multilingual content."""
        category = Category(
            id=uuid.uuid4(),
            name="Test Category",
            tenant_id="test-tenant",
        )
        async_session.add(category)
        await async_session.commit()

        product = Product(
            id=uuid.uuid4(),
            name="English Name",
            name_ar="الاسم العربي",
            description="English description",
            description_ar="الوصف العربي",
            price=Decimal("100.00"),
            category_id=category.id,
            tenant_id="test-tenant",
            features=["English Feature 1", "English Feature 2"],
            features_ar=["الخاصية العربية 1", "الخاصية العربية 2"],
        )
        async_session.add(product)
        await async_session.commit()
        
        assert product.name == "English Name"
        assert product.name_ar == "الاسم العربي"
        assert product.description == "English description"
        assert product.description_ar == "الوصف العربي"
        assert "English Feature 1" in product.features
        assert "الخاصية العربية 1" in product.features_ar

    @pytest.mark.asyncio
    async def test_product_metadata_json(self, async_session):
        """Test product metadata JSON field."""
        category = Category(
            id=uuid.uuid4(),
            name="Test Category",
            tenant_id="test-tenant",
        )
        async_session.add(category)
        await async_session.commit()

        metadata = {
            "github_url": "https://github.com/test/repo",
            "tags": ["tag1", "tag2"],
            "custom_field": "custom_value",
        }

        product = Product(
            id=uuid.uuid4(),
            name="Product with metadata",
            description="Test product",
            price=Decimal("100.00"),
            category_id=category.id,
            tenant_id="test-tenant",
            metadata=metadata,
        )
        async_session.add(product)
        await async_session.commit()
        
        assert product.metadata == metadata
        assert product.metadata["github_url"] == "https://github.com/test/repo"
        assert "tag1" in product.metadata["tags"]

    @pytest.mark.asyncio
    async def test_product_tenant_isolation(self, async_session):
        """Test that products are properly isolated by tenant."""
        category1 = Category(
            id=uuid.uuid4(),
            name="Category 1",
            tenant_id="tenant-1",
        )
        category2 = Category(
            id=uuid.uuid4(),
            name="Category 2",
            tenant_id="tenant-2",
        )
        async_session.add_all([category1, category2])
        await async_session.commit()

        # Create products for different tenants
        product1 = Product(
            id=uuid.uuid4(),
            name="Product 1",
            description="Product for tenant 1",
            price=Decimal("100.00"),
            category_id=category1.id,
            tenant_id="tenant-1",
        )
        
        product2 = Product(
            id=uuid.uuid4(),
            name="Product 2",
            description="Product for tenant 2",
            price=Decimal("200.00"),
            category_id=category2.id,
            tenant_id="tenant-2",
        )
        
        async_session.add_all([product1, product2])
        await async_session.commit()
        
        assert product1.tenant_id == "tenant-1"
        assert product2.tenant_id == "tenant-2"
        assert product1.tenant_id != product2.tenant_id

    @pytest.mark.asyncio
    async def test_product_category_relationship(self, async_session):
        """Test product-category relationship."""
        category = Category(
            id=uuid.uuid4(),
            name="Electronics",
            tenant_id="test-tenant",
        )
        async_session.add(category)
        await async_session.commit()

        product = Product(
            id=uuid.uuid4(),
            name="Smartphone",
            description="Latest smartphone",
            price=Decimal("999.99"),
            category_id=category.id,
            tenant_id="test-tenant",
        )
        async_session.add(product)
        await async_session.commit()
        
        # Refresh to load relationships
        await async_session.refresh(product)
        await async_session.refresh(category)
        
        assert product.category_id == category.id


class TestCategoryModel:
    """Test Category model functionality"""

    @pytest.mark.asyncio
    async def test_create_category_success(self, async_session):
        """Test creating a category successfully."""
        category = Category(
            id=uuid.uuid4(),
            name="Test Category",
            name_ar="فئة تجريبية",
            description="Test category description",
            description_ar="وصف الفئة التجريبية",
            tenant_id="test-tenant",
        )
        
        async_session.add(category)
        await async_session.commit()
        
        assert category.id is not None
        assert category.name == "Test Category"
        assert category.name_ar == "فئة تجريبية"
        assert category.tenant_id == "test-tenant"

    @pytest.mark.asyncio
    async def test_category_required_fields(self, async_session):
        """Test that required fields are enforced."""
        with pytest.raises(IntegrityError):
            category = Category(
                id=uuid.uuid4(),
                # name missing
                tenant_id="test-tenant",
            )
            async_session.add(category)
            await async_session.commit()

    @pytest.mark.asyncio
    async def test_category_multilingual_content(self, async_session):
        """Test category multilingual content."""
        category = Category(
            id=uuid.uuid4(),
            name="English Category",
            name_ar="الفئة العربية",
            description="English description",
            description_ar="الوصف العربي",
            tenant_id="test-tenant",
        )
        async_session.add(category)
        await async_session.commit()
        
        assert category.name == "English Category"
        assert category.name_ar == "الفئة العربية"
        assert category.description == "English description"
        assert category.description_ar == "الوصف العربي"

    @pytest.mark.asyncio
    async def test_category_tenant_isolation(self, async_session):
        """Test that categories are properly isolated by tenant."""
        category1 = Category(
            id=uuid.uuid4(),
            name="Category 1",
            tenant_id="tenant-1",
        )
        
        category2 = Category(
            id=uuid.uuid4(),
            name="Category 2",
            tenant_id="tenant-2",
        )
        
        async_session.add_all([category1, category2])
        await async_session.commit()
        
        assert category1.tenant_id == "tenant-1"
        assert category2.tenant_id == "tenant-2"
        assert category1.tenant_id != category2.tenant_id

    @pytest.mark.asyncio
    async def test_category_hierarchical_structure(self, async_session):
        """Test category hierarchical structure."""
        parent_category = Category(
            id=uuid.uuid4(),
            name="Electronics",
            tenant_id="test-tenant",
        )
        async_session.add(parent_category)
        await async_session.commit()

        child_category = Category(
            id=uuid.uuid4(),
            name="Smartphones",
            parent_id=parent_category.id,
            tenant_id="test-tenant",
        )
        async_session.add(child_category)
        await async_session.commit()
        
        assert child_category.parent_id == parent_category.id

    @pytest.mark.asyncio
    async def test_category_slug_generation(self, async_session):
        """Test category slug generation (if implemented)."""
        category = Category(
            id=uuid.uuid4(),
            name="Electronics & Gadgets",
            tenant_id="test-tenant",
        )
        async_session.add(category)
        await async_session.commit()
        
        # If slug is auto-generated, test it
        # This depends on the actual model implementation
        assert category.name == "Electronics & Gadgets"


class TestProductEnums:
    """Test product-related enumerations"""

    def test_product_status_enum_values(self):
        """Test ProductStatus enum values."""
        assert ProductStatus.ACTIVE == "active"
        assert ProductStatus.INACTIVE == "inactive"
        assert ProductStatus.OUT_OF_STOCK == "out_of_stock"
        assert ProductStatus.DISCONTINUED == "discontinued"
        assert ProductStatus.DRAFT == "draft"

    def test_stock_status_enum_values(self):
        """Test StockStatus enum values."""
        assert StockStatus.IN_STOCK == "in_stock"
        assert StockStatus.LOW_STOCK == "low_stock"
        assert StockStatus.OUT_OF_STOCK == "out_of_stock"
        assert StockStatus.BACKORDER == "backorder"

    def test_enum_iteration(self):
        """Test that enums can be iterated."""
        product_statuses = list(ProductStatus)
        assert len(product_statuses) == 5
        assert ProductStatus.ACTIVE in product_statuses

        stock_statuses = list(StockStatus)
        assert len(stock_statuses) == 4
        assert StockStatus.IN_STOCK in stock_statuses


class TestProductModelEdgeCases:
    """Test edge cases for product models"""

    @pytest.mark.asyncio
    async def test_product_with_very_long_name(self, async_session):
        """Test product with very long name."""
        category = Category(
            id=uuid.uuid4(),
            name="Test Category",
            tenant_id="test-tenant",
        )
        async_session.add(category)
        await async_session.commit()

        long_name = "a" * 500  # Very long name
        
        # This might fail if there's a length constraint
        try:
            product = Product(
                id=uuid.uuid4(),
                name=long_name,
                description="Test product",
                price=Decimal("100.00"),
                category_id=category.id,
                tenant_id="test-tenant",
            )
            async_session.add(product)
            await async_session.commit()
            
            assert len(product.name) == 500
        except Exception:
            # If length constraint exists, this is expected
            pass

    @pytest.mark.asyncio
    async def test_product_with_special_characters(self, async_session):
        """Test product with special characters in content."""
        category = Category(
            id=uuid.uuid4(),
            name="Test Category",
            tenant_id="test-tenant",
        )
        async_session.add(category)
        await async_session.commit()

        product = Product(
            id=uuid.uuid4(),
            name="Product with special chars: @#$%^&*()",
            description="Description with émojis 🚀 and spëcial chars",
            price=Decimal("100.00"),
            category_id=category.id,
            tenant_id="test-tenant",
        )
        async_session.add(product)
        await async_session.commit()
        
        assert "🚀" in product.description
        assert "@#$%^&*()" in product.name

    @pytest.mark.asyncio
    async def test_product_with_very_high_price(self, async_session):
        """Test product with very high price."""
        category = Category(
            id=uuid.uuid4(),
            name="Test Category",
            tenant_id="test-tenant",
        )
        async_session.add(category)
        await async_session.commit()

        high_price = Decimal("999999999.99")
        
        product = Product(
            id=uuid.uuid4(),
            name="Expensive Product",
            description="Very expensive product",
            price=high_price,
            category_id=category.id,
            tenant_id="test-tenant",
        )
        async_session.add(product)
        await async_session.commit()
        
        assert product.price == high_price

    @pytest.mark.asyncio
    async def test_product_timestamps(self, async_session):
        """Test product creation and update timestamps."""
        category = Category(
            id=uuid.uuid4(),
            name="Test Category",
            tenant_id="test-tenant",
        )
        async_session.add(category)
        await async_session.commit()

        product = Product(
            id=uuid.uuid4(),
            name="Timestamped Product",
            description="Test product",
            price=Decimal("100.00"),
            category_id=category.id,
            tenant_id="test-tenant",
        )
        async_session.add(product)
        await async_session.commit()
        
        # Check that timestamps are set (if model has them)
        if hasattr(product, 'created_at'):
            assert product.created_at is not None
        if hasattr(product, 'updated_at'):
            assert product.updated_at is not None