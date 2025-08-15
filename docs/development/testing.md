# Testing Strategy and Guidelines

## Overview

The BrainSAIT Store platform employs a comprehensive testing strategy covering unit tests, integration tests, end-to-end tests, and performance testing to ensure reliability and maintainability.

## Testing Philosophy

### Test Pyramid
```
        /\
       /  \
      /    \     End-to-End Tests (Few)
     /      \    - User journeys
    /        \   - Critical workflows
   /          \
  /____________\ Integration Tests (Some)
 /              \ - API endpoints
/________________\ - Database operations
                   Unit Tests (Many)
                   - Business logic
                   - Utilities
                   - Components
```

### Testing Principles
- **Fast Feedback**: Quick test execution for rapid development
- **Reliable**: Tests should be deterministic and not flaky
- **Maintainable**: Easy to update and understand
- **Comprehensive**: Cover critical business logic and edge cases

## Backend Testing (Python/FastAPI)

### Test Structure
```
backend/tests/
├── conftest.py              # Pytest configuration and fixtures
├── unit/                    # Unit tests
│   ├── test_models.py       # Database model tests
│   ├── test_services.py     # Business logic tests
│   └── test_utils.py        # Utility function tests
├── integration/             # Integration tests
│   ├── test_api_endpoints.py # API endpoint tests
│   ├── test_database.py    # Database operation tests
│   └── test_auth.py        # Authentication tests
├── e2e/                     # End-to-end tests
│   ├── test_user_flows.py   # Complete user journeys
│   └── test_payment_flows.py # Payment workflows
└── performance/             # Performance tests
    ├── test_load.py         # Load testing
    └── test_stress.py       # Stress testing
```

### Unit Testing

#### Test Configuration (conftest.py)
```python
import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import get_db, Base
from app.core.config import settings

# Test database
TEST_DATABASE_URL = "postgresql://user:password@localhost:5432/test_brainsait_store"
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
def db_session():
    """Create a database session for testing."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client."""
    def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

@pytest.fixture
def sample_tenant(db_session):
    """Create a sample tenant for testing."""
    from app.models.tenant import Tenant
    
    tenant = Tenant(
        name="Test Company",
        slug="test-company",
        status="active"
    )
    db_session.add(tenant)
    db_session.commit()
    db_session.refresh(tenant)
    return tenant

@pytest.fixture
def sample_user(db_session, sample_tenant):
    """Create a sample user for testing."""
    from app.models.user import User
    from app.core.security import get_password_hash
    
    user = User(
        tenant_id=sample_tenant.id,
        email="test@example.com",
        password_hash=get_password_hash("password"),
        name="Test User",
        role="admin"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user
```

#### Model Tests
```python
# tests/unit/test_models.py
import pytest
from app.models.product import Product
from app.models.order import Order, OrderItem

class TestProductModel:
    def test_create_product(self, db_session, sample_tenant):
        """Test product creation."""
        product = Product(
            tenant_id=sample_tenant.id,
            name={"en": "Test Product", "ar": "منتج تجريبي"},
            description={"en": "Test description"},
            price=99.99,
            currency="USD",
            category="software"
        )
        
        db_session.add(product)
        db_session.commit()
        db_session.refresh(product)
        
        assert product.id is not None
        assert product.name["en"] == "Test Product"
        assert product.price == 99.99
        assert product.status == "active"  # Default value

    def test_product_validation(self, db_session, sample_tenant):
        """Test product validation."""
        # Test missing required fields
        with pytest.raises(ValueError):
            product = Product(
                tenant_id=sample_tenant.id,
                # Missing name and price
                description={"en": "Test description"}
            )
            db_session.add(product)
            db_session.commit()

    def test_product_price_validation(self, db_session, sample_tenant):
        """Test price validation."""
        # Test negative price
        with pytest.raises(ValueError):
            product = Product(
                tenant_id=sample_tenant.id,
                name={"en": "Test Product"},
                price=-10.00  # Invalid negative price
            )
            db_session.add(product)
            db_session.commit()

class TestOrderModel:
    def test_create_order(self, db_session, sample_tenant, sample_user):
        """Test order creation."""
        order = Order(
            tenant_id=sample_tenant.id,
            user_id=sample_user.id,
            number="ORD-2024-001",
            total=199.98,
            currency="USD",
            customer_email="customer@example.com"
        )
        
        db_session.add(order)
        db_session.commit()
        db_session.refresh(order)
        
        assert order.id is not None
        assert order.number == "ORD-2024-001"
        assert order.status == "pending"
        assert order.total == 199.98

    def test_order_total_calculation(self, db_session, sample_tenant, sample_user):
        """Test order total calculation with items."""
        order = Order(
            tenant_id=sample_tenant.id,
            user_id=sample_user.id,
            number="ORD-2024-002",
            total=0,  # Will be calculated
            currency="USD"
        )
        db_session.add(order)
        db_session.commit()
        
        # Add order items
        item1 = OrderItem(
            order_id=order.id,
            product_name="Product 1",
            quantity=2,
            price=50.00,
            total=100.00
        )
        item2 = OrderItem(
            order_id=order.id,
            product_name="Product 2",
            quantity=1,
            price=99.99,
            total=99.99
        )
        
        db_session.add_all([item1, item2])
        db_session.commit()
        
        # Calculate total
        calculated_total = sum(item.total for item in order.items)
        order.total = calculated_total
        db_session.commit()
        
        assert order.total == 199.99
```

#### Service Tests
```python
# tests/unit/test_services.py
import pytest
from unittest.mock import Mock, patch
from app.services.product_service import ProductService
from app.services.order_service import OrderService
from app.schemas.product import ProductCreate

class TestProductService:
    def setup_method(self):
        self.db_mock = Mock()
        self.product_service = ProductService(self.db_mock)

    def test_create_product(self):
        """Test product creation service."""
        tenant_id = "tenant-123"
        product_data = ProductCreate(
            name={"en": "New Product"},
            price=149.99,
            currency="USD",
            category="software"
        )
        
        # Mock database response
        created_product = Mock()
        created_product.id = "prod-123"
        created_product.name = {"en": "New Product"}
        created_product.price = 149.99
        
        self.db_mock.add.return_value = None
        self.db_mock.commit.return_value = None
        self.db_mock.refresh.return_value = None
        
        with patch('app.models.product.Product') as MockProduct:
            MockProduct.return_value = created_product
            
            result = self.product_service.create_product(tenant_id, product_data)
            
            assert result.id == "prod-123"
            assert result.name["en"] == "New Product"
            assert result.price == 149.99
            self.db_mock.add.assert_called_once()
            self.db_mock.commit.assert_called_once()

    def test_get_products_with_filters(self):
        """Test product listing with filters."""
        tenant_id = "tenant-123"
        filters = {
            "category": "software",
            "min_price": 50.00,
            "max_price": 200.00
        }
        
        # Mock database query
        mock_products = [
            Mock(id="prod-1", name={"en": "Product 1"}, price=99.99),
            Mock(id="prod-2", name={"en": "Product 2"}, price=149.99)
        ]
        
        query_mock = Mock()
        query_mock.filter.return_value = query_mock
        query_mock.offset.return_value = query_mock
        query_mock.limit.return_value = query_mock
        query_mock.all.return_value = mock_products
        
        self.db_mock.query.return_value = query_mock
        
        result = self.product_service.get_products(
            tenant_id=tenant_id,
            filters=filters,
            page=1,
            limit=20
        )
        
        assert len(result) == 2
        assert result[0].id == "prod-1"
        assert result[1].id == "prod-2"

class TestOrderService:
    def setup_method(self):
        self.db_mock = Mock()
        self.order_service = OrderService(self.db_mock)

    @patch('app.services.order_service.generate_order_number')
    def test_create_order(self, mock_generate_number):
        """Test order creation with items."""
        mock_generate_number.return_value = "ORD-2024-001"
        
        tenant_id = "tenant-123"
        order_data = {
            "items": [
                {"product_id": "prod-1", "quantity": 2, "price": 50.00},
                {"product_id": "prod-2", "quantity": 1, "price": 99.99}
            ],
            "customer_email": "customer@example.com"
        }
        
        created_order = Mock()
        created_order.id = "order-123"
        created_order.number = "ORD-2024-001"
        created_order.total = 199.99
        
        self.db_mock.add.return_value = None
        self.db_mock.commit.return_value = None
        self.db_mock.refresh.return_value = None
        
        with patch('app.models.order.Order') as MockOrder:
            MockOrder.return_value = created_order
            
            result = self.order_service.create_order(tenant_id, order_data)
            
            assert result.id == "order-123"
            assert result.number == "ORD-2024-001"
            assert result.total == 199.99
            mock_generate_number.assert_called_once()
```

### Integration Testing

#### API Endpoint Tests
```python
# tests/integration/test_api_endpoints.py
import pytest
from fastapi.testclient import TestClient

class TestProductAPI:
    def test_create_product_endpoint(self, client, sample_tenant, auth_headers):
        """Test product creation endpoint."""
        product_data = {
            "name": {"en": "Test Product", "ar": "منتج تجريبي"},
            "description": {"en": "Test description"},
            "price": 99.99,
            "currency": "USD",
            "category": "software",
            "tags": ["test", "software"]
        }
        
        response = client.post(
            "/api/v1/store/products",
            json=product_data,
            headers={**auth_headers, "X-Tenant-ID": str(sample_tenant.id)}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"]["en"] == "Test Product"
        assert data["price"] == 99.99
        assert data["status"] == "active"

    def test_get_products_endpoint(self, client, sample_tenant, auth_headers):
        """Test product listing endpoint."""
        # Create test products first
        self._create_test_products(client, sample_tenant, auth_headers)
        
        response = client.get(
            "/api/v1/store/products?page=1&limit=10&category=software",
            headers={**auth_headers, "X-Tenant-ID": str(sample_tenant.id)}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "pagination" in data
        assert len(data["data"]) > 0

    def test_unauthorized_access(self, client, sample_tenant):
        """Test unauthorized access to protected endpoints."""
        response = client.get(
            "/api/v1/store/products",
            headers={"X-Tenant-ID": str(sample_tenant.id)}
        )
        
        assert response.status_code == 401

class TestOrderAPI:
    def test_create_order_endpoint(self, client, sample_tenant, sample_user, auth_headers):
        """Test order creation endpoint."""
        # Create products first
        product1 = self._create_test_product(client, sample_tenant, auth_headers)
        product2 = self._create_test_product(client, sample_tenant, auth_headers)
        
        order_data = {
            "items": [
                {"product_id": product1["id"], "quantity": 2},
                {"product_id": product2["id"], "quantity": 1}
            ],
            "customer_email": "customer@example.com",
            "customer_name": "John Doe"
        }
        
        response = client.post(
            "/api/v1/orders",
            json=order_data,
            headers={**auth_headers, "X-Tenant-ID": str(sample_tenant.id)}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["customer_email"] == "customer@example.com"
        assert len(data["items"]) == 2
        assert data["status"] == "pending"

class TestAuthAPI:
    def test_login_endpoint(self, client, sample_user, sample_tenant):
        """Test user login endpoint."""
        login_data = {
            "email": "test@example.com",
            "password": "password"
        }
        
        response = client.post(
            "/api/v1/auth/login",
            json=login_data,
            headers={"X-Tenant-ID": str(sample_tenant.id)}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_invalid_login(self, client, sample_tenant):
        """Test login with invalid credentials."""
        login_data = {
            "email": "invalid@example.com",
            "password": "wrongpassword"
        }
        
        response = client.post(
            "/api/v1/auth/login",
            json=login_data,
            headers={"X-Tenant-ID": str(sample_tenant.id)}
        )
        
        assert response.status_code == 401
```

#### Database Integration Tests
```python
# tests/integration/test_database.py
import pytest
from sqlalchemy import text

class TestDatabaseOperations:
    def test_tenant_isolation(self, db_session):
        """Test that tenants are properly isolated."""
        from app.models.tenant import Tenant
        from app.models.product import Product
        
        # Create two tenants
        tenant1 = Tenant(name="Tenant 1", slug="tenant-1")
        tenant2 = Tenant(name="Tenant 2", slug="tenant-2")
        db_session.add_all([tenant1, tenant2])
        db_session.commit()
        
        # Create products for each tenant
        product1 = Product(
            tenant_id=tenant1.id,
            name={"en": "Product 1"},
            price=99.99
        )
        product2 = Product(
            tenant_id=tenant2.id,
            name={"en": "Product 2"},
            price=149.99
        )
        db_session.add_all([product1, product2])
        db_session.commit()
        
        # Query products for tenant1
        tenant1_products = db_session.query(Product).filter(
            Product.tenant_id == tenant1.id
        ).all()
        
        # Query products for tenant2
        tenant2_products = db_session.query(Product).filter(
            Product.tenant_id == tenant2.id
        ).all()
        
        assert len(tenant1_products) == 1
        assert len(tenant2_products) == 1
        assert tenant1_products[0].name["en"] == "Product 1"
        assert tenant2_products[0].name["en"] == "Product 2"

    def test_database_constraints(self, db_session):
        """Test database constraints."""
        from app.models.user import User
        from app.models.tenant import Tenant
        
        tenant = Tenant(name="Test Tenant", slug="test-tenant")
        db_session.add(tenant)
        db_session.commit()
        
        # Test unique email constraint within tenant
        user1 = User(
            tenant_id=tenant.id,
            email="user@example.com",
            name="User 1"
        )
        user2 = User(
            tenant_id=tenant.id,
            email="user@example.com",  # Same email
            name="User 2"
        )
        
        db_session.add(user1)
        db_session.commit()
        
        # This should fail due to unique constraint
        with pytest.raises(Exception):
            db_session.add(user2)
            db_session.commit()

    def test_cascade_deletes(self, db_session):
        """Test cascade delete operations."""
        from app.models.tenant import Tenant
        from app.models.user import User
        from app.models.product import Product
        
        # Create tenant with users and products
        tenant = Tenant(name="Test Tenant", slug="test-tenant")
        db_session.add(tenant)
        db_session.commit()
        
        user = User(
            tenant_id=tenant.id,
            email="user@example.com",
            name="Test User"
        )
        product = Product(
            tenant_id=tenant.id,
            name={"en": "Test Product"},
            price=99.99
        )
        
        db_session.add_all([user, product])
        db_session.commit()
        
        user_id = user.id
        product_id = product.id
        
        # Delete tenant
        db_session.delete(tenant)
        db_session.commit()
        
        # Check that related records are deleted
        assert db_session.query(User).filter(User.id == user_id).first() is None
        assert db_session.query(Product).filter(Product.id == product_id).first() is None
```

## Frontend Testing (React/Next.js)

### Test Structure
```
frontend/tests/
├── __mocks__/               # Mock files
│   ├── next-router.js       # Next.js router mock
│   └── api.js              # API client mock
├── components/              # Component tests
│   ├── ProductCard.test.tsx
│   └── OrderForm.test.tsx
├── pages/                   # Page tests
│   ├── products.test.tsx
│   └── admin.test.tsx
├── hooks/                   # Custom hook tests
│   ├── useAuth.test.tsx
│   └── useProducts.test.tsx
├── utils/                   # Utility tests
│   ├── formatters.test.ts
│   └── validators.test.ts
└── e2e/                     # End-to-end tests
    ├── auth.spec.ts
    └── checkout.spec.ts
```

### Component Testing with Jest and React Testing Library
```typescript
// tests/components/ProductCard.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { ProductCard } from '@/components/ProductCard';
import { Product } from '@/types';

const mockProduct: Product = {
  id: 'prod-123',
  name: { en: 'Test Product', ar: 'منتج تجريبي' },
  description: { en: 'Test description' },
  price: 99.99,
  currency: 'USD',
  category: 'software',
  images: ['https://example.com/image.jpg'],
  status: 'active',
  created_at: '2024-01-15T10:30:00Z',
  updated_at: '2024-01-15T10:30:00Z'
};

describe('ProductCard', () => {
  test('renders product information', () => {
    const onAddToCart = jest.fn();
    
    render(
      <ProductCard 
        product={mockProduct} 
        onAddToCart={onAddToCart}
        locale="en"
      />
    );
    
    expect(screen.getByText('Test Product')).toBeInTheDocument();
    expect(screen.getByText('$99.99')).toBeInTheDocument();
    expect(screen.getByText('Test description')).toBeInTheDocument();
  });

  test('calls onAddToCart when button clicked', () => {
    const onAddToCart = jest.fn();
    
    render(
      <ProductCard 
        product={mockProduct} 
        onAddToCart={onAddToCart}
        locale="en"
      />
    );
    
    const addButton = screen.getByRole('button', { name: /add to cart/i });
    fireEvent.click(addButton);
    
    expect(onAddToCart).toHaveBeenCalledWith(mockProduct);
  });

  test('displays Arabic content when locale is ar', () => {
    const onAddToCart = jest.fn();
    
    render(
      <ProductCard 
        product={mockProduct} 
        onAddToCart={onAddToCart}
        locale="ar"
      />
    );
    
    expect(screen.getByText('منتج تجريبي')).toBeInTheDocument();
  });
});
```

### Hook Testing
```typescript
// tests/hooks/useAuth.test.tsx
import { renderHook, act } from '@testing-library/react';
import { useAuth } from '@/hooks/useAuth';
import { AuthProvider } from '@/contexts/AuthContext';

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <AuthProvider>{children}</AuthProvider>
);

describe('useAuth', () => {
  test('should login successfully', async () => {
    const { result } = renderHook(() => useAuth(), { wrapper });
    
    await act(async () => {
      await result.current.login('test@example.com', 'password');
    });
    
    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.user).toEqual({
      email: 'test@example.com',
      name: 'Test User'
    });
  });

  test('should handle login error', async () => {
    const { result } = renderHook(() => useAuth(), { wrapper });
    
    await act(async () => {
      try {
        await result.current.login('invalid@example.com', 'wrong');
      } catch (error) {
        expect(error.message).toBe('Invalid credentials');
      }
    });
    
    expect(result.current.isAuthenticated).toBe(false);
  });
});
```

## End-to-End Testing with Playwright

### E2E Test Setup
```typescript
// tests/e2e/auth.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Authentication', () => {
  test('should login successfully', async ({ page }) => {
    await page.goto('/login');
    
    await page.fill('input[name="email"]', 'admin@example.com');
    await page.fill('input[name="password"]', 'password');
    await page.click('button[type="submit"]');
    
    await expect(page).toHaveURL('/dashboard');
    await expect(page.locator('text=Welcome back')).toBeVisible();
  });

  test('should logout successfully', async ({ page }) => {
    // Login first
    await page.goto('/login');
    await page.fill('input[name="email"]', 'admin@example.com');
    await page.fill('input[name="password"]', 'password');
    await page.click('button[type="submit"]');
    
    // Logout
    await page.click('[data-testid="user-menu"]');
    await page.click('text=Logout');
    
    await expect(page).toHaveURL('/login');
  });
});

test.describe('Product Management', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/login');
    await page.fill('input[name="email"]', 'admin@example.com');
    await page.fill('input[name="password"]', 'password');
    await page.click('button[type="submit"]');
  });

  test('should create new product', async ({ page }) => {
    await page.goto('/admin/products');
    await page.click('text=Add Product');
    
    await page.fill('input[name="name.en"]', 'Test Product');
    await page.fill('input[name="name.ar"]', 'منتج تجريبي');
    await page.fill('textarea[name="description.en"]', 'Test description');
    await page.fill('input[name="price"]', '99.99');
    await page.selectOption('select[name="category"]', 'software');
    
    await page.click('button[type="submit"]');
    
    await expect(page.locator('text=Product created successfully')).toBeVisible();
    await expect(page.locator('text=Test Product')).toBeVisible();
  });
});
```

## Performance Testing

### Load Testing with Locust
```python
# tests/performance/test_load.py
from locust import HttpUser, task, between
import random

class BrainSAITStoreUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Login before starting tasks."""
        self.login()
    
    def login(self):
        """Authenticate user."""
        response = self.client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "password"
        }, headers={
            "X-Tenant-ID": "test-tenant"
        })
        
        if response.status_code == 200:
            token = response.json()["access_token"]
            self.client.headers.update({
                "Authorization": f"Bearer {token}",
                "X-Tenant-ID": "test-tenant"
            })
    
    @task(3)
    def get_products(self):
        """Get products list."""
        self.client.get("/api/v1/store/products")
    
    @task(2)
    def get_product_detail(self):
        """Get specific product."""
        product_id = random.choice(self.product_ids)
        self.client.get(f"/api/v1/store/products/{product_id}")
    
    @task(1)
    def create_order(self):
        """Create new order."""
        order_data = {
            "items": [
                {"product_id": "prod-123", "quantity": 1}
            ],
            "customer_email": "customer@example.com"
        }
        self.client.post("/api/v1/orders", json=order_data)
    
    @task(1)
    def get_analytics(self):
        """Get analytics data."""
        self.client.get("/api/v1/analytics/overview")
```

### Database Performance Testing
```python
# tests/performance/test_database.py
import pytest
import time
from sqlalchemy import text
from concurrent.futures import ThreadPoolExecutor

class TestDatabasePerformance:
    def test_product_query_performance(self, db_session):
        """Test product query performance."""
        # Create test data
        self._create_test_products(db_session, count=1000)
        
        start_time = time.time()
        
        # Execute query
        result = db_session.execute(text("""
            SELECT * FROM products 
            WHERE tenant_id = :tenant_id 
            AND status = 'active'
            ORDER BY created_at DESC 
            LIMIT 20
        """), {"tenant_id": "test-tenant"})
        
        products = result.fetchall()
        end_time = time.time()
        
        query_time = end_time - start_time
        
        assert len(products) == 20
        assert query_time < 0.1  # Should complete in under 100ms

    def test_concurrent_orders(self, db_session):
        """Test concurrent order creation."""
        def create_order(order_num):
            # Create order in separate transaction
            return self._create_test_order(f"ORD-{order_num}")
        
        start_time = time.time()
        
        # Create 50 concurrent orders
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(create_order, i) 
                for i in range(50)
            ]
            
            results = [future.result() for future in futures]
        
        end_time = time.time()
        
        assert len(results) == 50
        assert end_time - start_time < 5  # Should complete in under 5 seconds
```

## Test Automation and CI/CD

### GitHub Actions Workflow
```yaml
# .github/workflows/test.yml
name: Test Suite

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_brainsait_store
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest-cov pytest-xdist
      
      - name: Run tests
        run: |
          cd backend
          pytest tests/ -v --cov=app --cov-report=xml
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_brainsait_store
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./backend/coverage.xml

  frontend-tests:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
      
      - name: Run tests
        run: |
          cd frontend
          npm run test:ci
      
      - name: Run E2E tests
        run: |
          cd frontend
          npx playwright install
          npm run test:e2e

  performance-tests:
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install Locust
        run: pip install locust
      
      - name: Run load tests
        run: |
          locust -f tests/performance/test_load.py \
                 --host=https://staging-api.brainsait.io \
                 --users=50 \
                 --spawn-rate=5 \
                 --run-time=5m \
                 --headless
```

### Test Reports and Coverage

#### Coverage Configuration
```ini
# backend/.coveragerc
[run]
source = app
omit = 
    */tests/*
    */venv/*
    */__pycache__/*
    */migrations/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError

[html]
directory = htmlcov
```

#### Test Report Generation
```bash
# Generate test reports
pytest tests/ --html=reports/backend-test-report.html --self-contained-html
npm run test:ci -- --coverage --coverageReporters=html
```

## Best Practices

### Test Organization
- **Group related tests** in classes or describe blocks
- **Use descriptive test names** that explain what is being tested
- **Follow AAA pattern**: Arrange, Act, Assert
- **Keep tests independent** and isolated

### Test Data Management
- **Use factories** for creating test data
- **Clean up after tests** to avoid side effects
- **Use realistic test data** that represents actual usage
- **Separate test data** from production data

### Mocking and Stubbing
- **Mock external dependencies** (APIs, databases, file systems)
- **Use dependency injection** to make testing easier
- **Verify interactions** with mocks when important
- **Keep mocks simple** and focused

### Performance Testing
- **Set performance budgets** and fail tests when exceeded
- **Test realistic scenarios** with appropriate data volumes
- **Monitor key metrics** (response time, throughput, resource usage)
- **Run performance tests regularly** in CI/CD pipeline

## Next Steps

- [API Documentation](../api/README.md)
- [Development Guide](./README.md)
- [Deployment Guide](../deployment/README.md)
- [Monitoring Guide](../deployment/monitoring.md)