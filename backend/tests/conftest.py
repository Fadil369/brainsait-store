"""
Simplified test configuration for backend testing
"""

import pytest
from unittest.mock import Mock, AsyncMock
from uuid import uuid4
from decimal import Decimal


@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    return AsyncMock()


@pytest.fixture
def test_tenant_id():
    """Generate a test tenant ID."""
    return uuid4()


@pytest.fixture
def test_user_id():
    """Generate a test user ID."""
    return uuid4()


@pytest.fixture
def mock_current_user(test_user_id):
    """Mock current user data."""
    return {
        "id": test_user_id,
        "email": "test@brainsait.com",
        "name": "Test User",
        "tenant_id": uuid4(),
        "role": "user",
        "is_active": True,
    }


@pytest.fixture
def sample_product_data():
    """Sample product data for testing."""
    return {
        "name": "AI Business Assistant",
        "name_ar": "مساعد الأعمال الذكي",
        "description": "Advanced AI-powered business automation platform",
        "description_ar": "منصة أتمتة الأعمال المدعومة بالذكاء الاصطناعي المتقدمة",
        "price_sar": Decimal("1499.99"),
        "category": "ai",
        "status": "active",
        "features": [
            "GPT-4 Integration",
            "Multi-language Support",
            "Custom Training",
            "API Access"
        ],
        "features_ar": [
            "تكامل GPT-4",
            "دعم متعدد اللغات",
            "تدريب مخصص",
            "الوصول إلى API"
        ],
        "tags": ["ai", "automation", "business", "gpt"],
        "metadata": {
            "difficulty": "intermediate",
            "support_level": "premium",
            "deployment_time": "1-2 days"
        },
    }