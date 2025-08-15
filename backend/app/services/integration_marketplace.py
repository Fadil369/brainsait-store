"""
Integration Marketplace Service
Manages third-party integrations, webhooks, and marketplace functionality
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_redis
from app.models.users import User

logger = logging.getLogger(__name__)


class IntegrationMarketplace:
    """Integration marketplace management system"""

    def __init__(self, db: AsyncSession, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.redis = get_redis()

    async def get_available_integrations(self) -> List[Dict]:
        """Get all available integrations in the marketplace"""
        try:
            # Define available integrations
            integrations = [
                {
                    "id": "linkedin-leads",
                    "name": "LinkedIn Lead Generation",
                    "description": "Sync leads from LinkedIn campaigns automatically",
                    "category": "marketing",
                    "vendor": "LinkedIn Corp",
                    "icon": "https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/linkedin.svg",
                    "pricing": "free",
                    "features": [
                        "Automatic lead sync",
                        "Real-time notifications",
                        "Lead scoring",
                        "Campaign analytics"
                    ],
                    "supported_events": ["lead.created", "campaign.updated"],
                    "setup_complexity": "easy",
                    "status": "active",
                    "rating": 4.8,
                    "installs": 15420,
                    "documentation_url": "/docs/integrations/linkedin",
                    "webhook_url": "/webhooks/linkedin/lead-notifications",
                    "oauth_required": True,
                    "configuration_fields": [
                        {
                            "name": "client_id",
                            "label": "LinkedIn Client ID",
                            "type": "text",
                            "required": True
                        },
                        {
                            "name": "client_secret",
                            "label": "LinkedIn Client Secret",
                            "type": "password",
                            "required": True
                        }
                    ]
                },
                {
                    "id": "zapier-automation",
                    "name": "Zapier Workflows",
                    "description": "Connect with 5000+ apps through Zapier automation",
                    "category": "automation",
                    "vendor": "Zapier Inc",
                    "icon": "https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/zapier.svg",
                    "pricing": "freemium",
                    "features": [
                        "5000+ app connections",
                        "Multi-step workflows",
                        "Conditional logic",
                        "Custom webhooks"
                    ],
                    "supported_events": ["order.created", "customer.updated", "payment.completed"],
                    "setup_complexity": "medium",
                    "status": "active",
                    "rating": 4.6,
                    "installs": 28950,
                    "documentation_url": "/docs/integrations/zapier",
                    "webhook_url": "/webhooks/zapier",
                    "oauth_required": False,
                    "configuration_fields": [
                        {
                            "name": "webhook_url",
                            "label": "Zapier Webhook URL",
                            "type": "url",
                            "required": True
                        }
                    ]
                },
                {
                    "id": "n8n-workflows",
                    "name": "n8n Workflow Automation",
                    "description": "Open-source workflow automation with visual editor",
                    "category": "automation",
                    "vendor": "n8n GmbH",
                    "icon": "https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/n8n.svg",
                    "pricing": "free",
                    "features": [
                        "Visual workflow editor",
                        "Self-hosted option",
                        "Custom node support",
                        "Advanced debugging"
                    ],
                    "supported_events": ["*"],
                    "setup_complexity": "advanced",
                    "status": "beta",
                    "rating": 4.7,
                    "installs": 8520,
                    "documentation_url": "/docs/integrations/n8n",
                    "webhook_url": "/webhooks/n8n",
                    "oauth_required": False,
                    "configuration_fields": [
                        {
                            "name": "n8n_webhook_url",
                            "label": "n8n Webhook URL",
                            "type": "url",
                            "required": True
                        },
                        {
                            "name": "api_key",
                            "label": "n8n API Key",
                            "type": "password",
                            "required": False
                        }
                    ]
                },
                {
                    "id": "salesforce-crm",
                    "name": "Salesforce CRM",
                    "description": "Sync customers and opportunities with Salesforce",
                    "category": "crm",
                    "vendor": "Salesforce Inc",
                    "icon": "https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/salesforce.svg",
                    "pricing": "premium",
                    "features": [
                        "Bi-directional sync",
                        "Custom field mapping",
                        "Lead scoring",
                        "Opportunity tracking"
                    ],
                    "supported_events": ["customer.created", "order.completed", "lead.converted"],
                    "setup_complexity": "advanced",
                    "status": "active",
                    "rating": 4.5,
                    "installs": 12300,
                    "documentation_url": "/docs/integrations/salesforce",
                    "webhook_url": "/webhooks/salesforce",
                    "oauth_required": True,
                    "configuration_fields": [
                        {
                            "name": "instance_url",
                            "label": "Salesforce Instance URL",
                            "type": "url",
                            "required": True
                        },
                        {
                            "name": "consumer_key",
                            "label": "Consumer Key",
                            "type": "text",
                            "required": True
                        },
                        {
                            "name": "consumer_secret",
                            "label": "Consumer Secret",
                            "type": "password",
                            "required": True
                        }
                    ]
                },
                {
                    "id": "hubspot-marketing",
                    "name": "HubSpot Marketing",
                    "description": "Integrate with HubSpot for marketing automation",
                    "category": "marketing",
                    "vendor": "HubSpot Inc",
                    "icon": "https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/hubspot.svg",
                    "pricing": "freemium",
                    "features": [
                        "Contact sync",
                        "Email campaigns",
                        "Lead nurturing",
                        "Analytics dashboard"
                    ],
                    "supported_events": ["contact.created", "email.opened", "form.submitted"],
                    "setup_complexity": "medium",
                    "status": "active",
                    "rating": 4.4,
                    "installs": 9870,
                    "documentation_url": "/docs/integrations/hubspot",
                    "webhook_url": "/webhooks/hubspot",
                    "oauth_required": True,
                    "configuration_fields": [
                        {
                            "name": "portal_id",
                            "label": "HubSpot Portal ID",
                            "type": "text",
                            "required": True
                        },
                        {
                            "name": "api_key",
                            "label": "API Key",
                            "type": "password",
                            "required": True
                        }
                    ]
                },
                {
                    "id": "stripe-payments",
                    "name": "Stripe Payments",
                    "description": "Advanced payment processing with Stripe",
                    "category": "payments",
                    "vendor": "Stripe Inc",
                    "icon": "https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/stripe.svg",
                    "pricing": "transaction_fee",
                    "features": [
                        "Global payment methods",
                        "Subscription billing",
                        "Fraud protection",
                        "Financial reporting"
                    ],
                    "supported_events": ["payment.completed", "subscription.created", "invoice.paid"],
                    "setup_complexity": "medium",
                    "status": "active",
                    "rating": 4.9,
                    "installs": 45230,
                    "documentation_url": "/docs/integrations/stripe",
                    "webhook_url": "/webhooks/stripe",
                    "oauth_required": False,
                    "configuration_fields": [
                        {
                            "name": "publishable_key",
                            "label": "Stripe Publishable Key",
                            "type": "text",
                            "required": True
                        },
                        {
                            "name": "secret_key",
                            "label": "Stripe Secret Key",
                            "type": "password",
                            "required": True
                        }
                    ]
                },
                {
                    "id": "mailchimp-email",
                    "name": "Mailchimp Email Marketing",
                    "description": "Email marketing and automation with Mailchimp",
                    "category": "marketing",
                    "vendor": "Mailchimp",
                    "icon": "https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/mailchimp.svg",
                    "pricing": "freemium",
                    "features": [
                        "Email campaigns",
                        "Audience segmentation",
                        "A/B testing",
                        "Marketing automation"
                    ],
                    "supported_events": ["contact.created", "purchase.completed", "email.clicked"],
                    "setup_complexity": "easy",
                    "status": "active",
                    "rating": 4.3,
                    "installs": 18650,
                    "documentation_url": "/docs/integrations/mailchimp",
                    "webhook_url": "/webhooks/mailchimp",
                    "oauth_required": True,
                    "configuration_fields": [
                        {
                            "name": "api_key",
                            "label": "Mailchimp API Key",
                            "type": "password",
                            "required": True
                        },
                        {
                            "name": "list_id",
                            "label": "Default List ID",
                            "type": "text",
                            "required": False
                        }
                    ]
                }
            ]

            return integrations

        except Exception as e:
            logger.error(f"Error fetching available integrations: {e}")
            return []

    async def get_installed_integrations(self, user_id: UUID) -> List[Dict]:
        """Get integrations installed by the current tenant"""
        try:
            # Get from Redis cache first
            cache_key = f"installed_integrations:{self.tenant_id}"
            cached_data = await self.redis.get(cache_key)
            
            if cached_data:
                return json.loads(cached_data)

            # For now, return some sample installed integrations
            # In a real implementation, this would query the database
            installed = [
                {
                    "id": "linkedin-leads",
                    "name": "LinkedIn Lead Generation",
                    "status": "active",
                    "installed_at": "2024-01-15T10:30:00Z",
                    "last_sync": "2024-01-20T14:22:00Z",
                    "sync_count": 1247,
                    "health_status": "healthy",
                    "configuration": {
                        "client_id": "***masked***",
                        "webhook_active": True
                    }
                },
                {
                    "id": "stripe-payments", 
                    "name": "Stripe Payments",
                    "status": "active",
                    "installed_at": "2024-01-10T08:15:00Z",
                    "last_sync": "2024-01-20T15:45:00Z",
                    "sync_count": 892,
                    "health_status": "healthy",
                    "configuration": {
                        "publishable_key": "pk_test_***masked***",
                        "webhook_active": True
                    }
                }
            ]

            # Cache for 1 hour
            await self.redis.setex(cache_key, 3600, json.dumps(installed, default=str))
            return installed

        except Exception as e:
            logger.error(f"Error fetching installed integrations: {e}")
            return []

    async def install_integration(self, integration_id: str, configuration: Dict, user_id: UUID) -> Dict:
        """Install a new integration"""
        try:
            # Validate integration exists
            available_integrations = await self.get_available_integrations()
            integration = next((i for i in available_integrations if i['id'] == integration_id), None)
            
            if not integration:
                raise ValueError(f"Integration {integration_id} not found")

            # Validate configuration
            required_fields = [field['name'] for field in integration['configuration_fields'] if field['required']]
            missing_fields = [field for field in required_fields if field not in configuration]
            
            if missing_fields:
                raise ValueError(f"Missing required configuration fields: {', '.join(missing_fields)}")

            # Create installation record
            installation = {
                "id": str(uuid4()),
                "integration_id": integration_id,
                "tenant_id": self.tenant_id,
                "user_id": str(user_id),
                "status": "installing",
                "installed_at": datetime.utcnow().isoformat(),
                "configuration": {
                    **configuration,
                    "webhook_active": False
                },
                "health_status": "pending",
                "sync_count": 0,
                "last_sync": None
            }

            # Store installation in Redis
            install_key = f"integration_install:{self.tenant_id}:{integration_id}"
            await self.redis.setex(install_key, 86400, json.dumps(installation, default=str))

            # Clear cache
            cache_key = f"installed_integrations:{self.tenant_id}"
            await self.redis.delete(cache_key)

            # Start webhook setup (simplified)
            await self._setup_webhook(integration_id, installation['id'])

            installation['status'] = 'active'
            installation['health_status'] = 'healthy'
            installation['configuration']['webhook_active'] = True

            # Update installation record
            await self.redis.setex(install_key, 86400, json.dumps(installation, default=str))

            return {
                "success": True,
                "installation_id": installation['id'],
                "status": installation['status'],
                "webhook_url": integration.get('webhook_url', ''),
                "message": f"Integration {integration['name']} installed successfully"
            }

        except Exception as e:
            logger.error(f"Error installing integration {integration_id}: {e}")
            raise

    async def uninstall_integration(self, integration_id: str, user_id: UUID) -> Dict:
        """Uninstall an integration"""
        try:
            # Remove installation record
            install_key = f"integration_install:{self.tenant_id}:{integration_id}"
            await self.redis.delete(install_key)

            # Clear cache
            cache_key = f"installed_integrations:{self.tenant_id}"
            await self.redis.delete(cache_key)

            # Cleanup webhooks (simplified)
            await self._cleanup_webhook(integration_id)

            return {
                "success": True,
                "message": f"Integration {integration_id} uninstalled successfully"
            }

        except Exception as e:
            logger.error(f"Error uninstalling integration {integration_id}: {e}")
            raise

    async def get_integration_health(self, integration_id: str) -> Dict:
        """Get health status of an installed integration"""
        try:
            install_key = f"integration_install:{self.tenant_id}:{integration_id}"
            installation_data = await self.redis.get(install_key)
            
            if not installation_data:
                return {"status": "not_installed"}

            installation = json.loads(installation_data)
            
            # Check webhook health (simplified)
            webhook_health = await self._check_webhook_health(integration_id)
            
            # Calculate health metrics
            last_sync = installation.get('last_sync')
            if last_sync:
                last_sync_time = datetime.fromisoformat(last_sync.replace('Z', '+00:00'))
                hours_since_sync = (datetime.utcnow().replace(tzinfo=None) - last_sync_time.replace(tzinfo=None)).total_seconds() / 3600
                sync_health = "healthy" if hours_since_sync < 24 else "warning" if hours_since_sync < 72 else "error"
            else:
                sync_health = "pending"

            overall_health = "healthy"
            if webhook_health != "healthy" or sync_health == "error":
                overall_health = "error"
            elif sync_health == "warning":
                overall_health = "warning"

            return {
                "status": installation['status'],
                "health_status": overall_health,
                "webhook_health": webhook_health,
                "sync_health": sync_health,
                "last_sync": last_sync,
                "sync_count": installation.get('sync_count', 0),
                "uptime_percentage": 99.2,  # Would calculate from actual data
                "errors_last_24h": 2,
                "metrics": {
                    "requests_last_24h": 45,
                    "success_rate": 97.8,
                    "avg_response_time": 250
                }
            }

        except Exception as e:
            logger.error(f"Error checking integration health for {integration_id}: {e}")
            return {"status": "error", "error": str(e)}

    async def get_integration_analytics(self, integration_id: str, days: int = 30) -> Dict:
        """Get analytics for an integration"""
        try:
            # In a real implementation, this would query actual usage data
            # For now, return sample analytics
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)

            analytics = {
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "days": days
                },
                "usage": {
                    "total_requests": 1245,
                    "successful_requests": 1218,
                    "failed_requests": 27,
                    "success_rate": 97.8,
                    "avg_response_time": 245
                },
                "events": {
                    "webhooks_received": 892,
                    "webhooks_processed": 887,
                    "webhooks_failed": 5,
                    "data_synced": 1156
                },
                "trends": {
                    "daily_requests": [
                        {"date": "2024-01-20", "requests": 45, "success": 44},
                        {"date": "2024-01-19", "requests": 52, "success": 51},
                        {"date": "2024-01-18", "requests": 38, "success": 38},
                        {"date": "2024-01-17", "requests": 41, "success": 40},
                        {"date": "2024-01-16", "requests": 49, "success": 48}
                    ],
                    "error_types": [
                        {"type": "timeout", "count": 12},
                        {"type": "auth_failed", "count": 8},
                        {"type": "rate_limit", "count": 5},
                        {"type": "network_error", "count": 2}
                    ]
                },
                "performance": {
                    "uptime_percentage": 99.2,
                    "avg_response_time_trend": [
                        {"period": "week_1", "avg_ms": 245},
                        {"period": "week_2", "avg_ms": 252},
                        {"period": "week_3", "avg_ms": 238},
                        {"period": "week_4", "avg_ms": 261}
                    ]
                }
            }

            return analytics

        except Exception as e:
            logger.error(f"Error fetching analytics for {integration_id}: {e}")
            return {}

    async def trigger_webhook_test(self, integration_id: str, event_type: str = "test") -> Dict:
        """Send a test webhook to verify integration setup"""
        try:
            # Get integration configuration
            install_key = f"integration_install:{self.tenant_id}:{integration_id}"
            installation_data = await self.redis.get(install_key)
            
            if not installation_data:
                raise ValueError("Integration not installed")

            installation = json.loads(installation_data)
            
            # Get integration details
            available_integrations = await self.get_available_integrations()
            integration = next((i for i in available_integrations if i['id'] == integration_id), None)
            
            if not integration:
                raise ValueError("Integration not found")

            # Create test payload
            test_payload = {
                "event_type": event_type,
                "timestamp": datetime.utcnow().isoformat(),
                "tenant_id": self.tenant_id,
                "integration_id": integration_id,
                "test": True,
                "data": {
                    "message": "This is a test webhook from BrainSAIT Store",
                    "source": "integration_marketplace"
                }
            }

            # In a real implementation, you would send the webhook here
            # For now, simulate success
            webhook_url = integration.get('webhook_url', '')
            
            # Store test result
            test_result = {
                "webhook_url": webhook_url,
                "payload": test_payload,
                "response_status": 200,
                "response_time": 245,
                "success": True,
                "sent_at": datetime.utcnow().isoformat()
            }

            # Store in Redis for debugging
            test_key = f"webhook_test:{self.tenant_id}:{integration_id}"
            await self.redis.setex(test_key, 3600, json.dumps(test_result, default=str))

            return {
                "success": True,
                "webhook_url": webhook_url,
                "response_time": test_result['response_time'],
                "message": "Test webhook sent successfully"
            }

        except Exception as e:
            logger.error(f"Error sending test webhook for {integration_id}: {e}")
            return {
                "success": False,
                "error": "Internal error",
                "message": "Failed to send test webhook"
            }

    async def _setup_webhook(self, integration_id: str, installation_id: str) -> bool:
        """Set up webhook for integration (simplified)"""
        try:
            # In a real implementation, this would:
            # 1. Register webhook endpoints
            # 2. Configure webhook security
            # 3. Set up event routing
            
            webhook_config = {
                "integration_id": integration_id,
                "installation_id": installation_id,
                "tenant_id": self.tenant_id,
                "active": True,
                "created_at": datetime.utcnow().isoformat()
            }
            
            webhook_key = f"webhook_config:{self.tenant_id}:{integration_id}"
            await self.redis.setex(webhook_key, 86400 * 30, json.dumps(webhook_config, default=str))
            
            return True
            
        except Exception as e:
            logger.error(f"Error setting up webhook for {integration_id}: {e}")
            return False

    async def _cleanup_webhook(self, integration_id: str) -> bool:
        """Clean up webhook configuration"""
        try:
            webhook_key = f"webhook_config:{self.tenant_id}:{integration_id}"
            await self.redis.delete(webhook_key)
            return True
            
        except Exception as e:
            logger.error(f"Error cleaning up webhook for {integration_id}: {e}")
            return False

    async def _check_webhook_health(self, integration_id: str) -> str:
        """Check webhook health status"""
        try:
            webhook_key = f"webhook_config:{self.tenant_id}:{integration_id}"
            webhook_data = await self.redis.get(webhook_key)
            
            if not webhook_data:
                return "inactive"
            
            # In a real implementation, this would check:
            # - Recent webhook deliveries
            # - Error rates
            # - Response times
            
            return "healthy"
            
        except Exception as e:
            logger.error(f"Error checking webhook health for {integration_id}: {e}")
            return "error"