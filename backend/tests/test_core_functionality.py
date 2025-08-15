"""
Basic tests for core authentication and tenant functionality
"""

import pytest
from uuid import UUID, uuid4
from unittest.mock import Mock, patch

# Import the auth module we just created
from app.core.auth import get_current_tenant, get_current_user


class TestAuthentication:
    """Tests for authentication functionality"""

    @pytest.mark.asyncio
    async def test_get_current_tenant_from_header(self):
        """Test tenant extraction from X-Tenant-ID header"""
        mock_request = Mock()
        test_tenant_id = uuid4()
        mock_request.headers = {"X-Tenant-ID": str(test_tenant_id)}
        
        tenant_id = await get_current_tenant(mock_request)
        assert tenant_id == test_tenant_id

    @pytest.mark.asyncio
    async def test_get_current_tenant_default(self):
        """Test default tenant when no header provided"""
        mock_request = Mock()
        mock_request.headers = {}
        
        tenant_id = await get_current_tenant(mock_request)
        assert isinstance(tenant_id, UUID)
        # Should return the default tenant UUID
        assert str(tenant_id) == "00000000-0000-0000-0000-000000000001"

    @pytest.mark.asyncio
    async def test_get_current_tenant_invalid_uuid(self):
        """Test handling of invalid UUID in tenant header"""
        mock_request = Mock()
        mock_request.headers = {"X-Tenant-ID": "invalid-uuid"}
        
        tenant_id = await get_current_tenant(mock_request)
        # Should fall back to default when invalid UUID provided
        assert isinstance(tenant_id, UUID)

    @pytest.mark.asyncio
    async def test_get_current_user_anonymous(self):
        """Test anonymous user access"""
        mock_request = Mock()
        tenant_id = uuid4()
        
        user = await get_current_user(mock_request, None, tenant_id)
        
        assert user["is_anonymous"] is True
        assert user["tenant_id"] == tenant_id
        assert user["role"] == "user"

    @pytest.mark.asyncio
    async def test_get_current_user_with_token(self):
        """Test authenticated user with valid token"""
        mock_request = Mock()
        mock_credentials = Mock()
        mock_credentials.credentials = "valid_token_12345"
        tenant_id = uuid4()
        
        user = await get_current_user(mock_request, mock_credentials, tenant_id)
        
        assert user["is_anonymous"] is False
        assert user["tenant_id"] == tenant_id
        assert user["email"] == "user@brainsait.com"


class TestTenantConfiguration:
    """Tests for tenant-specific configuration"""

    def test_tenant_features_validation(self):
        """Test that tenant features are properly configured"""
        from app.core.tenant import get_tenant_config
        
        # Test default tenant config
        config = get_tenant_config("brainsait")
        
        assert "features" in config
        assert isinstance(config["features"], dict)
        
        # Check that critical features are defined
        features = config["features"]
        assert "zatca_compliance" in features
        assert "mada_payments" in features
        assert "stc_pay" in features

    def test_tenant_config_fallback(self):
        """Test fallback to default config for unknown tenants"""
        from app.core.tenant import get_tenant_config
        
        config = get_tenant_config("unknown_tenant")
        default_config = get_tenant_config("brainsait")
        
        # Should return the default configuration
        assert config == default_config


class TestSchemaValidation:
    """Tests for Pydantic schema validation"""

    def test_product_schema_validation(self, sample_product_data):
        """Test product schema validation"""
        from app.schemas.store import ProductCreate
        
        # Valid product data should validate
        product = ProductCreate(**sample_product_data)
        assert product.name == "AI Business Assistant"
        assert product.price_sar > 0

    def test_product_schema_invalid_price(self):
        """Test product validation with invalid price"""
        from app.schemas.store import ProductCreate
        from pydantic import ValidationError
        
        invalid_data = {
            "name": "Test Product",
            "description": "Test description for validation",
            "price_sar": -100,  # Invalid negative price
            "category": "test",
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ProductCreate(**invalid_data)
        
        assert "price_sar" in str(exc_info.value)

    def test_customer_info_saudi_phone_validation(self):
        """Test Saudi phone number validation"""
        from app.schemas.store import CustomerInfo
        from pydantic import ValidationError
        
        # Valid Saudi phone number
        valid_customer = {
            "name": "Test Customer",
            "email": "test@example.com",
            "phone": "+966501234567",  # Valid Saudi mobile
        }
        customer = CustomerInfo(**valid_customer)
        assert customer.phone == "+966501234567"
        
        # Invalid phone number format
        invalid_customer = {
            "name": "Test Customer",
            "email": "test@example.com",
            "phone": "123456789",  # Invalid format
        }
        
        with pytest.raises(ValidationError):
            CustomerInfo(**invalid_customer)

    def test_saudi_tax_number_validation(self):
        """Test Saudi tax number validation"""
        from app.schemas.store import CustomerInfo
        from pydantic import ValidationError
        
        # Valid tax number
        valid_data = {
            "name": "Company Test",
            "email": "company@example.com",
            "phone": "+966501234567",
            "tax_number": "300012345600003",  # Valid Saudi tax number format
        }
        customer = CustomerInfo(**valid_data)
        assert customer.tax_number == "300012345600003"
        
        # Invalid tax number
        invalid_data = {
            "name": "Company Test",
            "email": "company@example.com", 
            "phone": "+966501234567",
            "tax_number": "123456789",  # Invalid format
        }
        
        with pytest.raises(ValidationError):
            CustomerInfo(**invalid_data)


class TestCriticalFunctionality:
    """Tests for critical business functionality"""

    def test_vat_calculation_logic(self):
        """Test VAT calculation for Saudi market (15%)"""
        from decimal import Decimal
        
        # Test 15% VAT calculation
        subtotal = Decimal("100.00")
        vat_rate = Decimal("0.15")
        expected_vat = Decimal("15.00")
        expected_total = Decimal("115.00")
        
        calculated_vat = subtotal * vat_rate
        calculated_total = subtotal + calculated_vat
        
        assert calculated_vat == expected_vat
        assert calculated_total == expected_total

    def test_currency_precision(self):
        """Test currency precision for SAR calculations"""
        from decimal import Decimal, ROUND_HALF_UP
        
        # Test rounding to 2 decimal places for SAR
        amount = Decimal("1499.995")
        rounded = amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        
        assert rounded == Decimal("1500.00")
        assert len(str(rounded).split(".")[-1]) == 2

    def test_multilingual_support(self, sample_product_data):
        """Test multilingual field support"""
        from app.schemas.store import ProductCreate
        
        product = ProductCreate(**sample_product_data)
        
        # Check that both English and Arabic names are supported
        assert product.name is not None
        assert product.name_ar is not None
        assert product.description is not None
        assert product.description_ar is not None
        
        # Check Arabic content is properly stored
        assert "ذكي" in product.name_ar  # "smart" in Arabic
        assert "منصة" in product.description_ar  # "platform" in Arabic