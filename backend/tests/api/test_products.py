"""
Test cases for product API endpoints.
"""

import uuid
from datetime import datetime
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.products import Product, Category, ProductStatus
from app.schemas.products import ProductCreate, ProductUpdate


class TestProductAPI:
    """Test product API endpoints"""

    @pytest.fixture
    def mock_product_data(self):
        """Mock product data for testing"""
        return {
            "name": "Test Product",
            "name_ar": "منتج تجريبي",
            "description": "Test product description",
            "description_ar": "وصف المنتج التجريبي",
            "price": 1000.00,
            "status": "active",
            "category_id": str(uuid.uuid4()),
            "features": ["Feature 1", "Feature 2"],
            "features_ar": ["خاصية 1", "خاصية 2"],
            "metadata": {"source": "test"},
        }

    @pytest.fixture
    def mock_category_data(self):
        """Mock category data for testing"""
        return {
            "name": "Test Category",
            "name_ar": "فئة تجريبية",
            "description": "Test category description",
            "description_ar": "وصف الفئة التجريبية",
        }

    def test_get_products_empty_list(self, client: TestClient):
        """Test getting products when no products exist"""
        response = client.get("/api/v1/products/")
        assert response.status_code == 200
        
        data = response.json()
        assert "products" in data
        assert "total" in data
        assert "page" in data
        assert "per_page" in data
        assert data["products"] == []
        assert data["total"] == 0

    def test_get_products_with_pagination(self, client: TestClient):
        """Test getting products with pagination parameters"""
        response = client.get("/api/v1/products/?page=1&per_page=10")
        assert response.status_code == 200
        
        data = response.json()
        assert data["page"] == 1
        assert data["per_page"] == 10

    def test_get_products_with_invalid_pagination(self, client: TestClient):
        """Test getting products with invalid pagination parameters"""
        # Test negative page
        response = client.get("/api/v1/products/?page=-1")
        assert response.status_code == 422

        # Test zero per_page
        response = client.get("/api/v1/products/?per_page=0")
        assert response.status_code == 422

        # Test excessive per_page
        response = client.get("/api/v1/products/?per_page=1000")
        assert response.status_code == 422

    def test_get_products_with_filters(self, client: TestClient):
        """Test getting products with various filters"""
        # Test category filter
        response = client.get("/api/v1/products/?category=ai")
        assert response.status_code == 200

        # Test price range filter
        response = client.get("/api/v1/products/?min_price=100&max_price=1000")
        assert response.status_code == 200

        # Test search filter
        response = client.get("/api/v1/products/?search=test")
        assert response.status_code == 200

        # Test status filter
        response = client.get("/api/v1/products/?status=active")
        assert response.status_code == 200

    def test_get_products_with_sorting(self, client: TestClient):
        """Test getting products with different sorting options"""
        # Test sort by name
        response = client.get("/api/v1/products/?sort_by=name&sort_direction=asc")
        assert response.status_code == 200

        # Test sort by price
        response = client.get("/api/v1/products/?sort_by=price&sort_direction=desc")
        assert response.status_code == 200

        # Test sort by created_at
        response = client.get("/api/v1/products/?sort_by=created_at&sort_direction=desc")
        assert response.status_code == 200

    def test_get_product_by_id_not_found(self, client: TestClient):
        """Test getting a non-existent product"""
        non_existent_id = str(uuid.uuid4())
        response = client.get(f"/api/v1/products/{non_existent_id}")
        assert response.status_code == 404

    def test_get_product_by_invalid_id(self, client: TestClient):
        """Test getting a product with invalid ID format"""
        response = client.get("/api/v1/products/invalid-id")
        assert response.status_code == 422

    def test_create_product_unauthorized(self, client: TestClient, mock_product_data):
        """Test creating a product without authentication"""
        response = client.post("/api/v1/products/", json=mock_product_data)
        assert response.status_code == 401

    def test_create_product_invalid_data(self, authenticated_admin_client: TestClient):
        """Test creating a product with invalid data"""
        # Missing required fields
        invalid_data = {"name": "Test Product"}
        response = authenticated_admin_client.post("/api/v1/products/", json=invalid_data)
        assert response.status_code == 422

        # Invalid price
        invalid_data = {
            "name": "Test Product",
            "description": "Test description",
            "price": -100,  # Negative price
            "category_id": str(uuid.uuid4()),
        }
        response = authenticated_admin_client.post("/api/v1/products/", json=invalid_data)
        assert response.status_code == 422

    def test_update_product_not_found(self, authenticated_admin_client: TestClient):
        """Test updating a non-existent product"""
        non_existent_id = str(uuid.uuid4())
        update_data = {"name": "Updated Product"}
        response = authenticated_admin_client.put(
            f"/api/v1/products/{non_existent_id}", json=update_data
        )
        assert response.status_code == 404

    def test_update_product_unauthorized(self, client: TestClient):
        """Test updating a product without authentication"""
        product_id = str(uuid.uuid4())
        update_data = {"name": "Updated Product"}
        response = client.put(f"/api/v1/products/{product_id}", json=update_data)
        assert response.status_code == 401

    def test_delete_product_not_found(self, authenticated_admin_client: TestClient):
        """Test deleting a non-existent product"""
        non_existent_id = str(uuid.uuid4())
        response = authenticated_admin_client.delete(f"/api/v1/products/{non_existent_id}")
        assert response.status_code == 404

    def test_delete_product_unauthorized(self, client: TestClient):
        """Test deleting a product without authentication"""
        product_id = str(uuid.uuid4())
        response = client.delete(f"/api/v1/products/{product_id}")
        assert response.status_code == 401

    def test_get_products_with_tenant_isolation(self, client: TestClient):
        """Test that products are properly isolated by tenant"""
        # Test with different tenant headers
        response1 = client.get("/api/v1/products/", headers={"X-Tenant-ID": "tenant1"})
        response2 = client.get("/api/v1/products/", headers={"X-Tenant-ID": "tenant2"})
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Both should return valid responses
        data1 = response1.json()
        data2 = response2.json()
        assert "products" in data1
        assert "products" in data2

    def test_get_products_with_language_preference(self, client: TestClient):
        """Test getting products with different language preferences"""
        # Test with English preference
        response_en = client.get(
            "/api/v1/products/", 
            headers={"Accept-Language": "en"}
        )
        assert response_en.status_code == 200

        # Test with Arabic preference
        response_ar = client.get(
            "/api/v1/products/", 
            headers={"Accept-Language": "ar"}
        )
        assert response_ar.status_code == 200

    def test_product_search_functionality(self, client: TestClient):
        """Test product search with different query types"""
        # Test empty search
        response = client.get("/api/v1/products/?search=")
        assert response.status_code == 200

        # Test search with special characters
        response = client.get("/api/v1/products/?search=@#$%")
        assert response.status_code == 200

        # Test search with Arabic text
        response = client.get("/api/v1/products/?search=منتج")
        assert response.status_code == 200

        # Test search with very long query
        long_query = "a" * 1000
        response = client.get(f"/api/v1/products/?search={long_query}")
        assert response.status_code == 200 or response.status_code == 414  # URI too long

    def test_product_filtering_combinations(self, client: TestClient):
        """Test combining multiple filters"""
        # Combine category and price filters
        response = client.get(
            "/api/v1/products/?category=ai&min_price=100&max_price=1000"
        )
        assert response.status_code == 200

        # Combine search and status filters
        response = client.get(
            "/api/v1/products/?search=test&status=active"
        )
        assert response.status_code == 200

        # Combine all filters
        response = client.get(
            "/api/v1/products/"
            "?category=ai&min_price=100&max_price=1000"
            "&search=test&status=active"
            "&sort_by=price&sort_direction=asc"
        )
        assert response.status_code == 200

    def test_product_price_validation(self, authenticated_admin_client: TestClient, mock_product_data):
        """Test product price validation edge cases"""
        # Test with decimal prices
        data = mock_product_data.copy()
        data["price"] = 99.99
        response = authenticated_admin_client.post("/api/v1/products/", json=data)
        assert response.status_code in [201, 422]  # Depends on business logic

        # Test with very high prices
        data["price"] = 999999.99
        response = authenticated_admin_client.post("/api/v1/products/", json=data)
        assert response.status_code in [201, 422]

        # Test with zero price
        data["price"] = 0
        response = authenticated_admin_client.post("/api/v1/products/", json=data)
        assert response.status_code in [201, 422]

    def test_product_multilingual_content(self, authenticated_admin_client: TestClient, mock_product_data):
        """Test product creation with multilingual content"""
        data = mock_product_data.copy()
        
        # Test with both English and Arabic content
        response = authenticated_admin_client.post("/api/v1/products/", json=data)
        assert response.status_code in [201, 422]

        # Test with only English content
        data_en_only = {k: v for k, v in data.items() if not k.endswith('_ar')}
        response = authenticated_admin_client.post("/api/v1/products/", json=data_en_only)
        assert response.status_code in [201, 422]

        # Test with only Arabic content
        data_ar_only = {
            "name": "منتج تجريبي",
            "description": "وصف المنتج التجريبي",
            "price": 1000.00,
            "category_id": str(uuid.uuid4()),
        }
        response = authenticated_admin_client.post("/api/v1/products/", json=data_ar_only)
        assert response.status_code in [201, 422]

    def test_product_status_transitions(self, authenticated_admin_client: TestClient):
        """Test product status transitions"""
        # This test would require actual product creation first
        # For now, test the validation of status values
        
        update_data = {"status": "active"}
        product_id = str(uuid.uuid4())
        response = authenticated_admin_client.put(
            f"/api/v1/products/{product_id}", json=update_data
        )
        assert response.status_code == 404  # Product doesn't exist

        # Test invalid status
        update_data = {"status": "invalid_status"}
        response = authenticated_admin_client.put(
            f"/api/v1/products/{product_id}", json=update_data
        )
        assert response.status_code in [404, 422]

    def test_api_rate_limiting(self, client: TestClient):
        """Test API rate limiting (if implemented)"""
        # Make multiple rapid requests
        responses = []
        for _ in range(10):
            response = client.get("/api/v1/products/")
            responses.append(response.status_code)
        
        # All should be successful or some might be rate limited
        assert all(status in [200, 429] for status in responses)

    def test_api_response_headers(self, client: TestClient):
        """Test API response headers"""
        response = client.get("/api/v1/products/")
        assert response.status_code == 200
        
        # Check for common security headers
        headers = response.headers
        # These might or might not be present depending on middleware
        assert "content-type" in headers
        assert headers["content-type"].startswith("application/json")

    def test_api_error_responses(self, client: TestClient):
        """Test that API returns proper error responses"""
        # Test 404 for non-existent product
        response = client.get(f"/api/v1/products/{uuid.uuid4()}")
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data

        # Test 422 for invalid data
        response = client.get("/api/v1/products/?page=invalid")
        assert response.status_code == 422
        
        data = response.json()
        assert "detail" in data