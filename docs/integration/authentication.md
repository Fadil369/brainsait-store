# Authentication Guide

## Overview

The BrainSAIT Store API uses JWT (JSON Web Tokens) for authentication with support for refresh tokens and API keys for server-to-server communication.

## Authentication Methods

### 1. JWT Token Authentication (Recommended for Web Apps)

#### Login Flow
```javascript
// Step 1: Login with credentials
const loginResponse = await fetch('/api/v1/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-Tenant-ID': 'your-tenant-id'
  },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'password'
  })
});

const { access_token, refresh_token } = await loginResponse.json();

// Step 2: Store tokens securely
localStorage.setItem('access_token', access_token);
localStorage.setItem('refresh_token', refresh_token);
```

#### Making Authenticated Requests
```javascript
// Include token in Authorization header
const response = await fetch('/api/v1/store/products', {
  headers: {
    'Authorization': `Bearer ${access_token}`,
    'X-Tenant-ID': 'your-tenant-id'
  }
});
```

#### Token Refresh
```javascript
// Check if token is expired and refresh if needed
async function refreshTokenIfNeeded() {
  const token = localStorage.getItem('access_token');
  
  // Decode token to check expiration (simplified)
  const payload = JSON.parse(atob(token.split('.')[1]));
  const isExpired = payload.exp * 1000 < Date.now();
  
  if (isExpired) {
    const refreshToken = localStorage.getItem('refresh_token');
    
    const response = await fetch('/api/v1/auth/refresh', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Tenant-ID': 'your-tenant-id'
      },
      body: JSON.stringify({
        refresh_token: refreshToken
      })
    });
    
    const { access_token } = await response.json();
    localStorage.setItem('access_token', access_token);
    
    return access_token;
  }
  
  return token;
}
```

### 2. API Key Authentication (For Server-to-Server)

#### Getting API Keys
1. Login to admin panel
2. Navigate to Settings → API Keys
3. Generate new API key with required scopes
4. Store API key securely

#### Using API Keys
```python
# Python example
import requests

headers = {
    'Authorization': f'Bearer {API_KEY}',
    'X-Tenant-ID': 'your-tenant-id',
    'Content-Type': 'application/json'
}

response = requests.get(
    'https://brainsait-api-gateway.fadil.workers.dev/api/v1/analytics/overview',
    headers=headers
)
```

## Security Best Practices

### Token Storage
- **Web Apps**: Use httpOnly cookies or secure localStorage
- **Mobile Apps**: Use secure keychain/keystore
- **Server Apps**: Use environment variables or secret management

### Token Validation
```javascript
// Validate token before making requests
function isTokenValid(token) {
  if (!token) return false;
  
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    return payload.exp * 1000 > Date.now();
  } catch {
    return false;
  }
}
```

### Error Handling
```javascript
async function authenticatedRequest(url, options = {}) {
  let token = await getValidToken();
  
  const response = await fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': `Bearer ${token}`,
      'X-Tenant-ID': 'your-tenant-id'
    }
  });
  
  if (response.status === 401) {
    // Try to refresh token
    token = await refreshToken();
    
    // Retry request with new token
    return fetch(url, {
      ...options,
      headers: {
        ...options.headers,
        'Authorization': `Bearer ${token}`,
        'X-Tenant-ID': 'your-tenant-id'
      }
    });
  }
  
  return response;
}
```

## Multi-Tenant Authentication

### Tenant Context
All API requests require a tenant ID in the header:

```javascript
headers: {
  'X-Tenant-ID': 'your-tenant-id',
  'Authorization': 'Bearer your-token'
}
```

### Tenant-Specific Tokens
Tokens are bound to specific tenants and cannot be used across tenants.

```json
{
  "sub": "user_123",
  "tenant_id": "company_xyz",
  "role": "admin",
  "permissions": ["read:products", "write:products"],
  "exp": 1643723400
}
```

## Permission System

### Role-Based Access Control
```json
{
  "roles": {
    "owner": {
      "permissions": ["*"]
    },
    "admin": {
      "permissions": [
        "read:*",
        "write:products",
        "write:orders",
        "read:analytics"
      ]
    },
    "user": {
      "permissions": [
        "read:products",
        "write:orders"
      ]
    }
  }
}
```

### Permission Checking
```javascript
// Check permissions before making requests
function hasPermission(token, permission) {
  const payload = JSON.parse(atob(token.split('.')[1]));
  return payload.permissions.includes(permission) || 
         payload.permissions.includes('*');
}

// Usage
if (hasPermission(token, 'write:products')) {
  // Allow product creation
}
```

## OAuth 2.0 Integration

### LinkedIn OAuth
```javascript
// Redirect to LinkedIn OAuth
const linkedinAuthUrl = `https://www.linkedin.com/oauth/v2/authorization?` +
  `response_type=code&` +
  `client_id=${LINKEDIN_CLIENT_ID}&` +
  `redirect_uri=${REDIRECT_URI}&` +
  `scope=r_liteprofile,r_emailaddress`;

window.location.href = linkedinAuthUrl;

// Handle callback
const urlParams = new URLSearchParams(window.location.search);
const code = urlParams.get('code');

// Exchange code for token
const response = await fetch('/api/v1/auth/linkedin/callback', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-Tenant-ID': 'your-tenant-id'
  },
  body: JSON.stringify({ code })
});
```

## Rate Limiting

### Rate Limit Headers
```javascript
function handleRateLimit(response) {
  const remaining = response.headers.get('X-Rate-Limit-Remaining');
  const resetTime = response.headers.get('X-Rate-Limit-Reset');
  
  if (remaining && parseInt(remaining) < 10) {
    console.warn(`Rate limit warning: ${remaining} requests remaining`);
  }
  
  if (response.status === 429) {
    const retryAfter = response.headers.get('Retry-After');
    throw new Error(`Rate limited. Retry after ${retryAfter} seconds`);
  }
}
```

### Authenticated Rate Limits
- **Anonymous**: 60 requests per hour
- **Authenticated**: 1000 requests per hour
- **API Key**: 5000 requests per hour
- **Enterprise**: 10000 requests per hour

## Testing Authentication

### Unit Tests
```javascript
// Jest test example
describe('Authentication', () => {
  test('should login successfully', async () => {
    const response = await request(app)
      .post('/api/v1/auth/login')
      .send({
        email: 'test@example.com',
        password: 'password'
      })
      .expect(200);
    
    expect(response.body).toHaveProperty('access_token');
    expect(response.body).toHaveProperty('refresh_token');
  });
  
  test('should refresh token', async () => {
    const refreshToken = 'valid-refresh-token';
    
    const response = await request(app)
      .post('/api/v1/auth/refresh')
      .send({ refresh_token: refreshToken })
      .expect(200);
    
    expect(response.body).toHaveProperty('access_token');
  });
});
```

### Integration Tests
```python
# Python test example
def test_authenticated_request():
    # Login first
    login_response = client.post('/api/v1/auth/login', json={
        'email': 'test@example.com',
        'password': 'password'
    })
    
    token = login_response.json()['access_token']
    
    # Make authenticated request
    response = client.get('/api/v1/store/products', headers={
        'Authorization': f'Bearer {token}',
        'X-Tenant-ID': 'test-tenant'
    })
    
    assert response.status_code == 200
```

## Security Considerations

### Token Security
- Use HTTPS for all communications
- Implement token blacklisting for logout
- Set appropriate token expiration times
- Use secure token storage methods

### API Key Security
- Rotate API keys regularly
- Use minimal required scopes
- Monitor API key usage
- Implement IP restrictions when possible

### Common Vulnerabilities
- **Token in URLs**: Never include tokens in URLs
- **XSS Attacks**: Sanitize all inputs
- **CSRF Attacks**: Use CSRF tokens for state-changing operations
- **Token Theft**: Implement proper token invalidation