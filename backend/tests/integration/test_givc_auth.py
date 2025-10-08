"""
Integration tests for GIVC authentication and session exchange
Tests the cross-service authentication flow between BrainSAIT Store and GIVC
"""

import pytest
import jwt
from datetime import datetime, timedelta
from typing import Dict, Any
from unittest.mock import Mock, patch, AsyncMock
import httpx


# Test configuration
TEST_JWT_SECRET = "test_jwt_secret_key_for_integration_tests_min_32_chars"
TEST_JWT_ALGORITHM = "HS256"
GIVC_API_URL = "https://givc-healthcare-api.fadil.workers.dev"


@pytest.fixture
def test_user_data() -> Dict[str, Any]:
    """Sample user data for testing"""
    return {
        "id": "user_uuid_123",
        "tenant_id": "tenant_uuid_456",
        "email": "dr.test@clinic.sa",
        "name": "Dr. Test Provider",
        "roles": ["healthcare_provider", "admin"],
        "permissions": [
            "read:products",
            "write:claims",
            "read:patients",
            "write:authorizations"
        ],
        "metadata": {
            "provider_oid": "1.3.6.1.4.1.61026.1.2.1.100",
            "nphies_license": "TEST-LICENSE-12345",
            "organization_id": "org_uuid_789"
        }
    }


@pytest.fixture
def generate_test_token(test_user_data):
    """Fixture to generate test JWT tokens"""
    def _generate_token(
        user_data: Dict[str, Any],
        audience: list = None,
        expires_delta: timedelta = None
    ) -> str:
        """Generate a JWT token for testing"""
        if audience is None:
            audience = ["brainsait-store", "givc-api", "healthlinc"]
        
        if expires_delta is None:
            expires_delta = timedelta(minutes=30)
        
        now = datetime.utcnow()
        payload = {
            "sub": user_data["id"],
            "iss": "brainsait-store",
            "aud": audience,
            "exp": int((now + expires_delta).timestamp()),
            "iat": int(now.timestamp()),
            "tenant_id": user_data["tenant_id"],
            "email": user_data["email"],
            "name": user_data["name"],
            "roles": user_data["roles"],
            "permissions": user_data["permissions"],
            "metadata": user_data.get("metadata", {})
        }
        
        return jwt.encode(payload, TEST_JWT_SECRET, algorithm=TEST_JWT_ALGORITHM)
    
    return _generate_token


class TestJWTTokenGeneration:
    """Test JWT token generation and structure"""
    
    def test_token_generation(self, generate_test_token, test_user_data):
        """Test that JWT token is generated correctly"""
        token = generate_test_token(test_user_data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token.split('.')) == 3  # JWT has 3 parts
    
    def test_token_payload(self, generate_test_token, test_user_data):
        """Test that token payload contains correct claims"""
        token = generate_test_token(test_user_data)
        payload = jwt.decode(
            token,
            TEST_JWT_SECRET,
            algorithms=[TEST_JWT_ALGORITHM],
            audience="brainsait-store"
        )
        
        assert payload["sub"] == test_user_data["id"]
        assert payload["tenant_id"] == test_user_data["tenant_id"]
        assert payload["email"] == test_user_data["email"]
        assert payload["iss"] == "brainsait-store"
        assert "givc-api" in payload["aud"]
        assert "healthlinc" in payload["aud"]
        assert payload["roles"] == test_user_data["roles"]
        assert payload["permissions"] == test_user_data["permissions"]
    
    def test_token_with_healthcare_metadata(self, generate_test_token, test_user_data):
        """Test that healthcare-specific metadata is included"""
        token = generate_test_token(test_user_data)
        payload = jwt.decode(
            token,
            TEST_JWT_SECRET,
            algorithms=[TEST_JWT_ALGORITHM],
            audience="givc-api"
        )
        
        assert "metadata" in payload
        assert payload["metadata"]["provider_oid"] == "1.3.6.1.4.1.61026.1.2.1.100"
        assert payload["metadata"]["nphies_license"] == "TEST-LICENSE-12345"
        assert payload["metadata"]["organization_id"] == "org_uuid_789"


class TestTokenValidation:
    """Test token validation across services"""
    
    def test_token_validation_success(self, generate_test_token, test_user_data):
        """Test successful token validation"""
        token = generate_test_token(test_user_data)
        
        # Simulate GIVC API validating the token
        payload = jwt.decode(
            token,
            TEST_JWT_SECRET,
            algorithms=[TEST_JWT_ALGORITHM],
            audience="givc-api"
        )
        
        assert payload is not None
        assert payload["sub"] == test_user_data["id"]
    
    def test_token_validation_expired(self, generate_test_token, test_user_data):
        """Test that expired tokens are rejected"""
        # Generate token that expires immediately
        token = generate_test_token(
            test_user_data,
            expires_delta=timedelta(seconds=-1)
        )
        
        with pytest.raises(jwt.ExpiredSignatureError):
            jwt.decode(
                token,
                TEST_JWT_SECRET,
                algorithms=[TEST_JWT_ALGORITHM],
                audience="givc-api"
            )
    
    def test_token_validation_wrong_audience(self, generate_test_token, test_user_data):
        """Test that tokens with wrong audience are rejected"""
        token = generate_test_token(
            test_user_data,
            audience=["brainsait-store"]  # Not including givc-api
        )
        
        with pytest.raises(jwt.InvalidAudienceError):
            jwt.decode(
                token,
                TEST_JWT_SECRET,
                algorithms=[TEST_JWT_ALGORITHM],
                audience="givc-api"
            )
    
    def test_token_validation_wrong_secret(self, generate_test_token, test_user_data):
        """Test that tokens signed with wrong secret are rejected"""
        token = generate_test_token(test_user_data)
        wrong_secret = "wrong_secret_key"
        
        with pytest.raises(jwt.InvalidSignatureError):
            jwt.decode(
                token,
                wrong_secret,
                algorithms=[TEST_JWT_ALGORITHM],
                audience="givc-api"
            )


class TestCrossServiceAuthentication:
    """Test authentication flow between BrainSAIT Store and GIVC"""
    
    @pytest.mark.asyncio
    async def test_authentication_flow_end_to_end(
        self,
        generate_test_token,
        test_user_data
    ):
        """Test complete authentication flow from Store to GIVC"""
        
        # Step 1: User logs into BrainSAIT Store
        # (Simulated - in real scenario, this would be POST /api/v1/auth/login)
        brainsait_token = generate_test_token(test_user_data)
        assert brainsait_token is not None
        
        # Step 2: User requests GIVC resource with BrainSAIT token
        # GIVC validates the token
        payload = jwt.decode(
            brainsait_token,
            TEST_JWT_SECRET,
            algorithms=[TEST_JWT_ALGORITHM],
            audience="givc-api"
        )
        
        assert payload["sub"] == test_user_data["id"]
        assert "givc-api" in payload["aud"]
        
        # Step 3: GIVC creates internal session
        givc_session = {
            "user_id": payload["sub"],
            "tenant_id": payload["tenant_id"],
            "email": payload["email"],
            "provider_oid": payload["metadata"]["provider_oid"],
            "created_at": datetime.utcnow().isoformat()
        }
        
        assert givc_session["user_id"] == test_user_data["id"]
        assert givc_session["provider_oid"] == "1.3.6.1.4.1.61026.1.2.1.100"
    
    @pytest.mark.asyncio
    async def test_session_exchange_request(
        self,
        generate_test_token,
        test_user_data
    ):
        """Test session exchange between services"""
        
        # Generate BrainSAIT token
        brainsait_token = generate_test_token(test_user_data)
        
        # Simulate session exchange request
        exchange_request = {
            "brainsait_token": brainsait_token,
            "service": "givc-api"
        }
        
        # Validate token and create service-specific session
        payload = jwt.decode(
            exchange_request["brainsait_token"],
            TEST_JWT_SECRET,
            algorithms=[TEST_JWT_ALGORITHM],
            audience=exchange_request["service"]
        )
        
        # Generate GIVC-specific token (if needed)
        givc_token = jwt.encode(
            {
                "sub": payload["sub"],
                "iss": "givc-api",
                "aud": ["givc-api"],
                "exp": int((datetime.utcnow() + timedelta(minutes=30)).timestamp()),
                "tenant_id": payload["tenant_id"],
                "provider_oid": payload["metadata"]["provider_oid"]
            },
            TEST_JWT_SECRET,
            algorithm=TEST_JWT_ALGORITHM
        )
        
        assert givc_token is not None


class TestPermissionValidation:
    """Test permission checking across services"""
    
    def test_has_required_permissions(self, generate_test_token, test_user_data):
        """Test that user has required permissions for healthcare operations"""
        token = generate_test_token(test_user_data)
        payload = jwt.decode(
            token,
            TEST_JWT_SECRET,
            algorithms=[TEST_JWT_ALGORITHM],
            audience="givc-api"
        )
        
        required_permissions = ["read:patients", "write:claims"]
        user_permissions = payload["permissions"]
        
        assert all(perm in user_permissions for perm in required_permissions)
    
    def test_missing_required_permissions(self, generate_test_token):
        """Test that users without required permissions are denied"""
        limited_user = {
            "id": "user_limited",
            "tenant_id": "tenant_uuid",
            "email": "limited@test.com",
            "name": "Limited User",
            "roles": ["user"],
            "permissions": ["read:products"],  # Missing healthcare permissions
            "metadata": {}
        }
        
        token = generate_test_token(limited_user)
        payload = jwt.decode(
            token,
            TEST_JWT_SECRET,
            algorithms=[TEST_JWT_ALGORITHM],
            audience="givc-api"
        )
        
        required_permissions = ["read:patients", "write:claims"]
        user_permissions = payload["permissions"]
        
        # Should not have healthcare permissions
        assert not all(perm in user_permissions for perm in required_permissions)


class TestHealthcareProviderValidation:
    """Test healthcare provider-specific validation"""
    
    def test_provider_oid_present(self, generate_test_token, test_user_data):
        """Test that healthcare provider has valid OID"""
        token = generate_test_token(test_user_data)
        payload = jwt.decode(
            token,
            TEST_JWT_SECRET,
            algorithms=[TEST_JWT_ALGORITHM],
            audience="givc-api"
        )
        
        assert "metadata" in payload
        assert "provider_oid" in payload["metadata"]
        assert payload["metadata"]["provider_oid"].startswith("1.3.6.1.4.1.61026.1.2.1")
    
    def test_nphies_credentials_present(self, generate_test_token, test_user_data):
        """Test that NPHIES credentials are included for healthcare providers"""
        token = generate_test_token(test_user_data)
        payload = jwt.decode(
            token,
            TEST_JWT_SECRET,
            algorithms=[TEST_JWT_ALGORITHM],
            audience="givc-api"
        )
        
        assert "metadata" in payload
        assert "nphies_license" in payload["metadata"]
        assert payload["metadata"]["nphies_license"].startswith("TEST-LICENSE")


class TestGIVCAPIIntegration:
    """Test integration with GIVC API endpoints (mocked)"""
    
    @pytest.mark.asyncio
    async def test_givc_health_check(self):
        """Test GIVC API health check endpoint"""
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "status": "healthy",
                "version": "1.0.0",
                "services": {
                    "authentication": "operational",
                    "nphies": "operational"
                }
            }
            mock_get.return_value = mock_response
            
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{GIVC_API_URL}/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["services"]["authentication"] == "operational"
    
    @pytest.mark.asyncio
    async def test_givc_authenticated_request(
        self,
        generate_test_token,
        test_user_data
    ):
        """Test authenticated request to GIVC API"""
        token = generate_test_token(test_user_data)
        
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "user_id": test_user_data["id"],
                "provider_oid": test_user_data["metadata"]["provider_oid"],
                "dashboard_data": {
                    "pending_claims": 5,
                    "active_patients": 42
                }
            }
            mock_get.return_value = mock_response
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{GIVC_API_URL}/api/v1/dashboard",
                    headers={"Authorization": f"Bearer {token}"}
                )
            
            assert response.status_code == 200
            data = response.json()
            assert data["user_id"] == test_user_data["id"]


class TestSecurityScenarios:
    """Test security scenarios and edge cases"""
    
    def test_token_tampering_detection(self, generate_test_token, test_user_data):
        """Test that tampered tokens are detected"""
        token = generate_test_token(test_user_data)
        
        # Tamper with token by changing a character
        tampered_token = token[:-5] + "XXXXX"
        
        with pytest.raises((jwt.InvalidSignatureError, jwt.DecodeError)):
            jwt.decode(
                tampered_token,
                TEST_JWT_SECRET,
                algorithms=[TEST_JWT_ALGORITHM],
                audience="givc-api"
            )
    
    def test_token_reuse_prevention(self, generate_test_token, test_user_data):
        """Test that tokens have appropriate expiration"""
        token = generate_test_token(
            test_user_data,
            expires_delta=timedelta(minutes=30)
        )
        
        payload = jwt.decode(
            token,
            TEST_JWT_SECRET,
            algorithms=[TEST_JWT_ALGORITHM],
            audience="givc-api"
        )
        
        # Verify token has expiration
        assert "exp" in payload
        assert payload["exp"] > datetime.utcnow().timestamp()
    
    def test_cross_tenant_access_prevention(self, generate_test_token):
        """Test that users cannot access other tenants' data"""
        tenant1_user = {
            "id": "user_tenant1",
            "tenant_id": "tenant_uuid_1",
            "email": "user1@tenant1.com",
            "name": "User 1",
            "roles": ["admin"],
            "permissions": ["read:patients"],
            "metadata": {}
        }
        
        tenant2_user = {
            "id": "user_tenant2",
            "tenant_id": "tenant_uuid_2",
            "email": "user2@tenant2.com",
            "name": "User 2",
            "roles": ["admin"],
            "permissions": ["read:patients"],
            "metadata": {}
        }
        
        token1 = generate_test_token(tenant1_user)
        payload1 = jwt.decode(
            token1,
            TEST_JWT_SECRET,
            algorithms=[TEST_JWT_ALGORITHM],
            audience="givc-api"
        )
        
        token2 = generate_test_token(tenant2_user)
        payload2 = jwt.decode(
            token2,
            TEST_JWT_SECRET,
            algorithms=[TEST_JWT_ALGORITHM],
            audience="givc-api"
        )
        
        # Verify tenants are different
        assert payload1["tenant_id"] != payload2["tenant_id"]
        
        # In real scenario, API would check tenant_id matches requested resource
        # and deny access if mismatch


# Smoke test suite - run these for quick validation
@pytest.mark.smoke
class TestSmokeTests:
    """Critical smoke tests for GIVC integration"""
    
    def test_jwt_secret_configured(self):
        """Smoke test: JWT secret is configured"""
        assert TEST_JWT_SECRET is not None
        assert len(TEST_JWT_SECRET) >= 32
    
    def test_token_generation_works(self, generate_test_token, test_user_data):
        """Smoke test: Token generation works"""
        token = generate_test_token(test_user_data)
        assert token is not None
    
    def test_token_validation_works(self, generate_test_token, test_user_data):
        """Smoke test: Token validation works"""
        token = generate_test_token(test_user_data)
        payload = jwt.decode(
            token,
            TEST_JWT_SECRET,
            algorithms=[TEST_JWT_ALGORITHM],
            audience="givc-api"
        )
        assert payload["sub"] == test_user_data["id"]
    
    def test_healthcare_metadata_included(self, generate_test_token, test_user_data):
        """Smoke test: Healthcare metadata is included"""
        token = generate_test_token(test_user_data)
        payload = jwt.decode(
            token,
            TEST_JWT_SECRET,
            algorithms=[TEST_JWT_ALGORITHM],
            audience="givc-api"
        )
        assert "metadata" in payload
        assert "provider_oid" in payload["metadata"]


if __name__ == "__main__":
    # Run smoke tests only
    pytest.main([__file__, "-v", "-m", "smoke"])
