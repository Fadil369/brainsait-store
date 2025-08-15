# API Reference - Endpoint Details

## Authentication Endpoints

### POST /api/v1/auth/login
Authenticate user and obtain access token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### POST /api/v1/auth/refresh
Refresh expired access token.

**Request Body:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

## Products Endpoints

### GET /api/v1/store/products
List products with pagination and filtering.

**Query Parameters:**
- `page` (integer): Page number (default: 1)
- `limit` (integer): Items per page (default: 20, max: 100)
- `category` (string): Filter by category
- `tags` (array): Filter by tags
- `search` (string): Search in name and description

**Response:**
```json
{
  "data": [
    {
      "id": "prod_123",
      "name": {
        "en": "AI Marketing Tool",
        "ar": "أداة التسويق بالذكاء الاصطناعي"
      },
      "description": {
        "en": "Advanced AI-powered marketing automation",
        "ar": "أتمتة التسويق المتقدمة بالذكاء الاصطناعي"
      },
      "price": 299.99,
      "currency": "USD",
      "category": "ai-tools",
      "tags": ["ai", "marketing", "automation"],
      "images": ["https://example.com/image1.jpg"],
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 50,
    "pages": 3
  }
}
```

### POST /api/v1/store/products
Create a new product.

**Request Body:**
```json
{
  "name": {
    "en": "New Product",
    "ar": "منتج جديد"
  },
  "description": {
    "en": "Product description",
    "ar": "وصف المنتج"
  },
  "price": 199.99,
  "currency": "USD",
  "category": "software",
  "tags": ["new", "featured"],
  "images": ["https://example.com/image1.jpg"]
}
```

## Analytics Endpoints

### GET /api/v1/analytics/overview
Get analytics overview for specified date range.

**Query Parameters:**
- `start_date` (string): Start date (ISO 8601 format)
- `end_date` (string): End date (ISO 8601 format)
- `granularity` (string): Data granularity (hour, day, week, month)

**Response:**
```json
{
  "summary": {
    "total_revenue": 125430.50,
    "total_orders": 432,
    "average_order_value": 290.35,
    "conversion_rate": 3.2
  },
  "revenue_trend": [
    {
      "date": "2024-01-15",
      "revenue": 5240.20,
      "orders": 18
    }
  ],
  "top_products": [
    {
      "product_id": "prod_123",
      "name": "AI Marketing Tool",
      "revenue": 12450.80,
      "units_sold": 42
    }
  ]
}
```

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "detail": "Validation error",
  "type": "validation_error",
  "code": "VALIDATION_001",
  "errors": [
    {
      "field": "email",
      "message": "Invalid email format"
    }
  ]
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication required",
  "type": "authentication_error",
  "code": "AUTH_001"
}
```

### 403 Forbidden
```json
{
  "detail": "Insufficient permissions",
  "type": "permission_error",
  "code": "PERM_001"
}
```

### 429 Too Many Requests
```json
{
  "detail": "Rate limit exceeded",
  "type": "rate_limit_error",
  "code": "RATE_001",
  "retry_after": 60
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error",
  "type": "server_error",
  "code": "SERVER_001"
}
```