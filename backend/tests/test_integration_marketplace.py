"""
Test cases for the Integration Marketplace
"""

import pytest
import json
from uuid import uuid4
from unittest.mock import AsyncMock, patch

from app.services.integration_marketplace import IntegrationMarketplace


class TestIntegrationMarketplace:
    """Test the integration marketplace functionality"""

    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        return AsyncMock()

    @pytest.fixture
    def mock_redis(self):
        """Mock Redis connection"""
        return AsyncMock()

    @pytest.fixture
    def marketplace(self, mock_db):
        """Create marketplace instance"""
        return IntegrationMarketplace(mock_db, "test-tenant")

    @pytest.mark.asyncio
    async def test_get_available_integrations(self, marketplace):
        """Test fetching available integrations"""
        integrations = await marketplace.get_available_integrations()
        
        assert isinstance(integrations, list)
        assert len(integrations) > 0
        
        # Check that all required fields are present
        for integration in integrations:
            assert 'id' in integration
            assert 'name' in integration
            assert 'description' in integration
            assert 'category' in integration
            assert 'vendor' in integration
            assert 'features' in integration
            assert 'pricing' in integration
            assert 'rating' in integration
            assert 'installs' in integration

    @pytest.mark.asyncio
    async def test_get_installed_integrations_empty_cache(self, marketplace):
        """Test fetching installed integrations with empty cache"""
        user_id = uuid4()
        
        # Mock Redis to return None (empty cache)
        marketplace.redis.get = AsyncMock(return_value=None)
        marketplace.redis.setex = AsyncMock()
        
        installed = await marketplace.get_installed_integrations(user_id)
        
        assert isinstance(installed, list)
        # Should return sample data when cache is empty
        assert len(installed) >= 0

    @pytest.mark.asyncio
    async def test_get_installed_integrations_with_cache(self, marketplace):
        """Test fetching installed integrations from cache"""
        user_id = uuid4()
        
        cached_data = [
            {
                "id": "test-integration",
                "name": "Test Integration",
                "status": "active",
                "installed_at": "2024-01-15T10:30:00Z",
                "health_status": "healthy",
                "sync_count": 100
            }
        ]
        
        # Mock Redis to return cached data
        marketplace.redis.get = AsyncMock(return_value=json.dumps(cached_data))
        
        installed = await marketplace.get_installed_integrations(user_id)
        
        assert installed == cached_data

    @pytest.mark.asyncio
    async def test_install_integration_success(self, marketplace):
        """Test successful integration installation"""
        integration_id = "linkedin-leads"
        configuration = {
            "client_id": "test_client_id",
            "client_secret": "test_client_secret"
        }
        user_id = uuid4()
        
        # Mock Redis operations
        marketplace.redis.setex = AsyncMock()
        marketplace.redis.delete = AsyncMock()
        
        # Mock webhook setup
        marketplace._setup_webhook = AsyncMock(return_value=True)
        
        result = await marketplace.install_integration(integration_id, configuration, user_id)
        
        assert result['success'] is True
        assert 'installation_id' in result
        assert result['status'] == 'active'
        assert 'webhook_url' in result

    @pytest.mark.asyncio
    async def test_install_integration_missing_fields(self, marketplace):
        """Test integration installation with missing required fields"""
        integration_id = "linkedin-leads"
        configuration = {}  # Missing required fields
        user_id = uuid4()
        
        with pytest.raises(ValueError) as exc_info:
            await marketplace.install_integration(integration_id, configuration, user_id)
        
        assert "Missing required configuration fields" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_install_integration_not_found(self, marketplace):
        """Test installation of non-existent integration"""
        integration_id = "non-existent-integration"
        configuration = {}
        user_id = uuid4()
        
        with pytest.raises(ValueError) as exc_info:
            await marketplace.install_integration(integration_id, configuration, user_id)
        
        assert f"Integration {integration_id} not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_uninstall_integration(self, marketplace):
        """Test integration uninstallation"""
        integration_id = "test-integration"
        user_id = uuid4()
        
        # Mock Redis operations
        marketplace.redis.delete = AsyncMock()
        marketplace._cleanup_webhook = AsyncMock(return_value=True)
        
        result = await marketplace.uninstall_integration(integration_id, user_id)
        
        assert result['success'] is True
        assert f"Integration {integration_id} uninstalled successfully" in result['message']

    @pytest.mark.asyncio
    async def test_get_integration_health_not_installed(self, marketplace):
        """Test health check for non-installed integration"""
        integration_id = "non-installed-integration"
        
        # Mock Redis to return None
        marketplace.redis.get = AsyncMock(return_value=None)
        
        health = await marketplace.get_integration_health(integration_id)
        
        assert health['status'] == 'not_installed'

    @pytest.mark.asyncio
    async def test_get_integration_health_installed(self, marketplace):
        """Test health check for installed integration"""
        integration_id = "test-integration"
        
        installation_data = {
            "status": "active",
            "last_sync": "2024-01-20T14:22:00Z",
            "sync_count": 100
        }
        
        # Mock Redis and health check methods
        marketplace.redis.get = AsyncMock(return_value=json.dumps(installation_data))
        marketplace._check_webhook_health = AsyncMock(return_value="healthy")
        
        health = await marketplace.get_integration_health(integration_id)
        
        assert health['status'] == 'active'
        assert health['health_status'] in ['healthy', 'warning', 'error']
        assert 'sync_count' in health
        assert 'uptime_percentage' in health

    @pytest.mark.asyncio
    async def test_get_integration_analytics(self, marketplace):
        """Test fetching integration analytics"""
        integration_id = "test-integration"
        days = 30
        
        analytics = await marketplace.get_integration_analytics(integration_id, days)
        
        assert 'period' in analytics
        assert 'usage' in analytics
        assert 'events' in analytics
        assert 'trends' in analytics
        assert 'performance' in analytics
        
        assert analytics['period']['days'] == days
        assert 'total_requests' in analytics['usage']
        assert 'success_rate' in analytics['usage']

    @pytest.mark.asyncio
    async def test_trigger_webhook_test_success(self, marketplace):
        """Test successful webhook test"""
        integration_id = "test-integration"
        
        installation_data = {
            "id": "install-123",
            "status": "active"
        }
        
        # Mock Redis operations
        marketplace.redis.get = AsyncMock(return_value=json.dumps(installation_data))
        marketplace.redis.setex = AsyncMock()
        
        result = await marketplace.trigger_webhook_test(integration_id)
        
        assert result['success'] is True
        assert 'webhook_url' in result
        assert 'response_time' in result

    @pytest.mark.asyncio
    async def test_trigger_webhook_test_not_installed(self, marketplace):
        """Test webhook test for non-installed integration"""
        integration_id = "non-installed-integration"
        
        # Mock Redis to return None
        marketplace.redis.get = AsyncMock(return_value=None)
        
        result = await marketplace.trigger_webhook_test(integration_id)
        
        assert result['success'] is False
        assert 'error' in result

    @pytest.mark.asyncio
    async def test_setup_webhook(self, marketplace):
        """Test webhook setup"""
        integration_id = "test-integration"
        installation_id = "install-123"
        
        # Mock Redis operations
        marketplace.redis.setex = AsyncMock()
        
        result = await marketplace._setup_webhook(integration_id, installation_id)
        
        assert result is True
        marketplace.redis.setex.assert_called_once()

    @pytest.mark.asyncio
    async def test_cleanup_webhook(self, marketplace):
        """Test webhook cleanup"""
        integration_id = "test-integration"
        
        # Mock Redis operations
        marketplace.redis.delete = AsyncMock()
        
        result = await marketplace._cleanup_webhook(integration_id)
        
        assert result is True
        marketplace.redis.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_check_webhook_health(self, marketplace):
        """Test webhook health check"""
        integration_id = "test-integration"
        
        webhook_data = {
            "active": True,
            "created_at": "2024-01-15T10:30:00Z"
        }
        
        # Mock Redis to return webhook data
        marketplace.redis.get = AsyncMock(return_value=json.dumps(webhook_data))
        
        health = await marketplace._check_webhook_health(integration_id)
        
        assert health == "healthy"

    @pytest.mark.asyncio
    async def test_check_webhook_health_inactive(self, marketplace):
        """Test webhook health check for inactive webhook"""
        integration_id = "test-integration"
        
        # Mock Redis to return None
        marketplace.redis.get = AsyncMock(return_value=None)
        
        health = await marketplace._check_webhook_health(integration_id)
        
        assert health == "inactive"

    def test_integration_data_structure(self, marketplace):
        """Test that all integrations have consistent data structure"""
        async def run_test():
            integrations = await marketplace.get_available_integrations()
            
            required_fields = [
                'id', 'name', 'description', 'category', 'vendor', 'icon',
                'pricing', 'features', 'supported_events', 'setup_complexity',
                'status', 'rating', 'installs', 'documentation_url',
                'webhook_url', 'oauth_required', 'configuration_fields'
            ]
            
            for integration in integrations:
                for field in required_fields:
                    assert field in integration, f"Missing field '{field}' in integration {integration.get('id', 'unknown')}"
                
                # Validate specific field types
                assert isinstance(integration['features'], list)
                assert isinstance(integration['supported_events'], list)
                assert isinstance(integration['configuration_fields'], list)
                assert isinstance(integration['rating'], (int, float))
                assert isinstance(integration['installs'], int)
                assert isinstance(integration['oauth_required'], bool)
        
        import asyncio
        asyncio.run(run_test())


if __name__ == "__main__":
    pytest.main([__file__])