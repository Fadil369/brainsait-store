"""
Workflow Automation Service
Implements n8n integration and business process automation
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


class WorkflowAutomationService:
    """Workflow automation and n8n integration service"""

    def __init__(self, db: AsyncSession, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.redis = get_redis()

    async def get_workflow_templates(self) -> List[Dict]:
        """Get available workflow templates"""
        try:
            templates = [
                {
                    "id": "customer-lifecycle-automation",
                    "name": "Customer Lifecycle Automation",
                    "description": "Automate customer onboarding, follow-ups, and retention campaigns",
                    "category": "customer_management",
                    "trigger_events": ["customer.created", "order.completed", "customer.inactive"],
                    "actions": [
                        "send_welcome_email",
                        "create_follow_up_tasks",
                        "update_crm_record",
                        "schedule_retention_campaign"
                    ],
                    "complexity": "medium",
                    "estimated_time_saved": "15 hours/month",
                    "status": "active",
                    "usage_count": 245,
                    "success_rate": 94.2,
                    "configuration": {
                        "welcome_email_delay": 5,  # minutes
                        "follow_up_schedule": [1, 7, 30],  # days
                        "retention_trigger_days": 60
                    }
                },
                {
                    "id": "order-processing-automation",
                    "name": "Order Processing Automation",
                    "description": "Automate order validation, inventory updates, and fulfillment workflows",
                    "category": "order_management",
                    "trigger_events": ["order.created", "payment.completed", "order.cancelled"],
                    "actions": [
                        "validate_order_details",
                        "update_inventory",
                        "send_confirmation_email",
                        "create_shipping_label",
                        "notify_fulfillment_team"
                    ],
                    "complexity": "advanced",
                    "estimated_time_saved": "25 hours/month",
                    "status": "active",
                    "usage_count": 189,
                    "success_rate": 97.8,
                    "configuration": {
                        "auto_validate_orders": True,
                        "inventory_threshold_check": True,
                        "shipping_integration": "enabled"
                    }
                },
                {
                    "id": "marketing-campaign-automation",
                    "name": "Marketing Campaign Automation",
                    "description": "Automate email campaigns, lead scoring, and nurturing workflows",
                    "category": "marketing",
                    "trigger_events": ["lead.created", "email.opened", "website.visit"],
                    "actions": [
                        "score_lead",
                        "segment_audience",
                        "send_nurturing_email",
                        "update_marketing_lists",
                        "track_engagement"
                    ],
                    "complexity": "medium",
                    "estimated_time_saved": "20 hours/month",
                    "status": "active",
                    "usage_count": 167,
                    "success_rate": 91.5,
                    "configuration": {
                        "lead_scoring_enabled": True,
                        "auto_segmentation": True,
                        "campaign_frequency": "weekly"
                    }
                },
                {
                    "id": "support-ticket-automation",
                    "name": "Support Ticket Automation",
                    "description": "Automate ticket routing, escalation, and customer communication",
                    "category": "customer_support",
                    "trigger_events": ["ticket.created", "ticket.updated", "customer.complaint"],
                    "actions": [
                        "categorize_ticket",
                        "assign_to_agent",
                        "send_acknowledgment",
                        "escalate_if_urgent",
                        "track_resolution_time"
                    ],
                    "complexity": "medium",
                    "estimated_time_saved": "18 hours/month",
                    "status": "active",
                    "usage_count": 134,
                    "success_rate": 93.7,
                    "configuration": {
                        "auto_categorization": True,
                        "escalation_rules": "enabled",
                        "sla_tracking": True
                    }
                },
                {
                    "id": "inventory-management-automation",
                    "name": "Inventory Management Automation",
                    "description": "Automate stock monitoring, reorder alerts, and supplier communications",
                    "category": "inventory",
                    "trigger_events": ["inventory.low", "product.out_of_stock", "order.fulfilled"],
                    "actions": [
                        "check_stock_levels",
                        "create_reorder_alert",
                        "notify_suppliers",
                        "update_product_status",
                        "forecast_demand"
                    ],
                    "complexity": "advanced",
                    "estimated_time_saved": "22 hours/month",
                    "status": "beta",
                    "usage_count": 89,
                    "success_rate": 89.3,
                    "configuration": {
                        "reorder_threshold": 10,
                        "auto_supplier_notification": True,
                        "demand_forecasting": "enabled"
                    }
                },
                {
                    "id": "social-media-automation",
                    "name": "Social Media Automation",
                    "description": "Automate social media posting, engagement tracking, and content scheduling",
                    "category": "marketing",
                    "trigger_events": ["blog.published", "product.launched", "event.scheduled"],
                    "actions": [
                        "create_social_post",
                        "schedule_across_platforms",
                        "track_engagement",
                        "respond_to_mentions",
                        "generate_analytics"
                    ],
                    "complexity": "medium",
                    "estimated_time_saved": "12 hours/month",
                    "status": "active",
                    "usage_count": 156,
                    "success_rate": 88.9,
                    "configuration": {
                        "platforms": ["twitter", "linkedin", "facebook"],
                        "auto_scheduling": True,
                        "engagement_monitoring": True
                    }
                }
            ]
            
            return templates

        except Exception as e:
            logger.error(f"Error fetching workflow templates: {e}")
            return []

    async def get_active_workflows(self, user_id: UUID) -> List[Dict]:
        """Get active workflows for the current tenant"""
        try:
            # Get from Redis cache first
            cache_key = f"active_workflows:{self.tenant_id}"
            cached_data = await self.redis.get(cache_key)
            
            if cached_data:
                return json.loads(cached_data)

            # Sample active workflows (in real implementation, this would query the database)
            active_workflows = [
                {
                    "id": "workflow-001",
                    "template_id": "customer-lifecycle-automation",
                    "name": "Customer Onboarding Flow",
                    "status": "active",
                    "created_at": "2024-01-10T08:30:00Z",
                    "last_run": "2024-01-20T15:45:00Z",
                    "runs_count": 247,
                    "success_rate": 96.4,
                    "configuration": {
                        "welcome_email_delay": 10,
                        "follow_up_schedule": [1, 3, 7, 30],
                        "retention_trigger_days": 45
                    },
                    "triggers": {
                        "customer.created": 89,
                        "order.completed": 156,
                        "customer.inactive": 2
                    },
                    "performance": {
                        "avg_execution_time": 2.3,
                        "errors_last_week": 1,
                        "time_saved_hours": 18.5
                    }
                },
                {
                    "id": "workflow-002",
                    "template_id": "order-processing-automation",
                    "name": "Order Fulfillment Pipeline",
                    "status": "active",
                    "created_at": "2024-01-12T14:20:00Z",
                    "last_run": "2024-01-20T16:22:00Z",
                    "runs_count": 178,
                    "success_rate": 98.9,
                    "configuration": {
                        "auto_validate_orders": True,
                        "inventory_threshold_check": True,
                        "shipping_integration": "enabled"
                    },
                    "triggers": {
                        "order.created": 134,
                        "payment.completed": 134,
                        "order.cancelled": 10
                    },
                    "performance": {
                        "avg_execution_time": 1.8,
                        "errors_last_week": 0,
                        "time_saved_hours": 24.2
                    }
                },
                {
                    "id": "workflow-003",
                    "template_id": "marketing-campaign-automation",
                    "name": "Lead Nurturing Campaign",
                    "status": "paused",
                    "created_at": "2024-01-08T11:15:00Z",
                    "last_run": "2024-01-18T09:30:00Z",
                    "runs_count": 92,
                    "success_rate": 94.6,
                    "configuration": {
                        "lead_scoring_enabled": True,
                        "auto_segmentation": True,
                        "campaign_frequency": "bi-weekly"
                    },
                    "triggers": {
                        "lead.created": 67,
                        "email.opened": 23,
                        "website.visit": 2
                    },
                    "performance": {
                        "avg_execution_time": 3.1,
                        "errors_last_week": 2,
                        "time_saved_hours": 12.8
                    }
                }
            ]

            # Cache for 30 minutes
            await self.redis.setex(cache_key, 1800, json.dumps(active_workflows, default=str))
            return active_workflows

        except Exception as e:
            logger.error(f"Error fetching active workflows: {e}")
            return []

    async def create_workflow(self, template_id: str, name: str, configuration: Dict, user_id: UUID) -> Dict:
        """Create a new workflow from template"""
        try:
            # Validate template exists
            templates = await self.get_workflow_templates()
            template = next((t for t in templates if t['id'] == template_id), None)
            
            if not template:
                raise ValueError(f"Template {template_id} not found")

            # Create workflow record
            workflow = {
                "id": str(uuid4()),
                "template_id": template_id,
                "name": name,
                "status": "creating",
                "created_at": datetime.utcnow().isoformat(),
                "created_by": str(user_id),
                "tenant_id": self.tenant_id,
                "configuration": configuration,
                "runs_count": 0,
                "success_rate": 0,
                "last_run": None,
                "n8n_workflow_id": None,
                "triggers": {},
                "performance": {
                    "avg_execution_time": 0,
                    "errors_last_week": 0,
                    "time_saved_hours": 0
                }
            }

            # Store workflow in Redis
            workflow_key = f"workflow:{self.tenant_id}:{workflow['id']}"
            await self.redis.setex(workflow_key, 86400 * 30, json.dumps(workflow, default=str))

            # Create n8n workflow (simplified)
            n8n_workflow_id = await self._create_n8n_workflow(template, configuration)
            workflow['n8n_workflow_id'] = n8n_workflow_id
            workflow['status'] = 'active'

            # Update stored workflow
            await self.redis.setex(workflow_key, 86400 * 30, json.dumps(workflow, default=str))

            # Clear cache
            cache_key = f"active_workflows:{self.tenant_id}"
            await self.redis.delete(cache_key)

            return {
                "success": True,
                "workflow_id": workflow['id'],
                "n8n_workflow_id": n8n_workflow_id,
                "status": workflow['status'],
                "message": f"Workflow '{name}' created successfully"
            }

        except Exception as e:
            logger.error(f"Error creating workflow: {e}")
            raise

    async def update_workflow(self, workflow_id: str, configuration: Dict, user_id: UUID) -> Dict:
        """Update an existing workflow"""
        try:
            # Get workflow
            workflow_key = f"workflow:{self.tenant_id}:{workflow_id}"
            workflow_data = await self.redis.get(workflow_key)
            
            if not workflow_data:
                raise ValueError("Workflow not found")

            workflow = json.loads(workflow_data)
            
            # Update configuration
            workflow['configuration'] = configuration
            workflow['updated_at'] = datetime.utcnow().isoformat()
            workflow['updated_by'] = str(user_id)

            # Update n8n workflow
            if workflow.get('n8n_workflow_id'):
                await self._update_n8n_workflow(workflow['n8n_workflow_id'], configuration)

            # Store updated workflow
            await self.redis.setex(workflow_key, 86400 * 30, json.dumps(workflow, default=str))

            # Clear cache
            cache_key = f"active_workflows:{self.tenant_id}"
            await self.redis.delete(cache_key)

            return {
                "success": True,
                "workflow_id": workflow_id,
                "message": "Workflow updated successfully"
            }

        except Exception as e:
            logger.error(f"Error updating workflow: {e}")
            raise

    async def delete_workflow(self, workflow_id: str, user_id: UUID) -> Dict:
        """Delete a workflow"""
        try:
            # Get workflow
            workflow_key = f"workflow:{self.tenant_id}:{workflow_id}"
            workflow_data = await self.redis.get(workflow_key)
            
            if not workflow_data:
                raise ValueError("Workflow not found")

            workflow = json.loads(workflow_data)

            # Delete n8n workflow
            if workflow.get('n8n_workflow_id'):
                await self._delete_n8n_workflow(workflow['n8n_workflow_id'])

            # Delete workflow record
            await self.redis.delete(workflow_key)

            # Clear cache
            cache_key = f"active_workflows:{self.tenant_id}"
            await self.redis.delete(cache_key)

            return {
                "success": True,
                "message": "Workflow deleted successfully"
            }

        except Exception as e:
            logger.error(f"Error deleting workflow: {e}")
            raise

    async def trigger_workflow(self, workflow_id: str, event_type: str, event_data: Dict) -> Dict:
        """Trigger a workflow execution"""
        try:
            # Get workflow
            workflow_key = f"workflow:{self.tenant_id}:{workflow_id}"
            workflow_data = await self.redis.get(workflow_key)
            
            if not workflow_data:
                raise ValueError("Workflow not found")

            workflow = json.loads(workflow_data)
            
            if workflow['status'] != 'active':
                raise ValueError(f"Workflow is {workflow['status']}, cannot trigger")

            # Create execution record
            execution = {
                "id": str(uuid4()),
                "workflow_id": workflow_id,
                "event_type": event_type,
                "event_data": event_data,
                "status": "running",
                "started_at": datetime.utcnow().isoformat(),
                "tenant_id": self.tenant_id
            }

            # Store execution
            execution_key = f"workflow_execution:{self.tenant_id}:{execution['id']}"
            await self.redis.setex(execution_key, 86400, json.dumps(execution, default=str))

            # Trigger n8n workflow (simplified)
            if workflow.get('n8n_workflow_id'):
                result = await self._trigger_n8n_workflow(workflow['n8n_workflow_id'], event_data)
                execution['status'] = 'completed' if result.get('success') else 'failed'
                execution['result'] = result
            else:
                # Simulate workflow execution
                execution['status'] = 'completed'
                execution['result'] = {
                    "success": True,
                    "actions_executed": len(workflow.get('actions', [])),
                    "execution_time": 2.1
                }

            execution['completed_at'] = datetime.utcnow().isoformat()

            # Update execution record
            await self.redis.setex(execution_key, 86400, json.dumps(execution, default=str))

            # Update workflow statistics
            workflow['runs_count'] += 1
            if execution['status'] == 'completed':
                workflow['success_rate'] = ((workflow.get('success_rate', 0) * (workflow['runs_count'] - 1)) + 100) / workflow['runs_count']
            workflow['last_run'] = execution['completed_at']

            # Update workflow
            await self.redis.setex(workflow_key, 86400 * 30, json.dumps(workflow, default=str))

            return {
                "success": True,
                "execution_id": execution['id'],
                "status": execution['status'],
                "result": execution.get('result'),
                "message": "Workflow triggered successfully"
            }

        except Exception as e:
            logger.error(f"Error triggering workflow: {e}")
            raise

    async def get_workflow_analytics(self, workflow_id: str, days: int = 30) -> Dict:
        """Get analytics for a workflow"""
        try:
            # Get workflow
            workflow_key = f"workflow:{self.tenant_id}:{workflow_id}"
            workflow_data = await self.redis.get(workflow_key)
            
            if not workflow_data:
                raise ValueError("Workflow not found")

            workflow = json.loads(workflow_data)

            # Generate analytics (in real implementation, this would query execution logs)
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)

            analytics = {
                "workflow_id": workflow_id,
                "workflow_name": workflow['name'],
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "days": days
                },
                "overview": {
                    "total_runs": workflow.get('runs_count', 0),
                    "success_rate": workflow.get('success_rate', 0),
                    "avg_execution_time": workflow.get('performance', {}).get('avg_execution_time', 0),
                    "total_time_saved": workflow.get('performance', {}).get('time_saved_hours', 0)
                },
                "trends": {
                    "daily_executions": [
                        {"date": "2024-01-20", "executions": 12, "successes": 12, "failures": 0},
                        {"date": "2024-01-19", "executions": 8, "successes": 7, "failures": 1},
                        {"date": "2024-01-18", "executions": 15, "successes": 14, "failures": 1},
                        {"date": "2024-01-17", "executions": 9, "successes": 9, "failures": 0},
                        {"date": "2024-01-16", "executions": 11, "successes": 10, "failures": 1}
                    ],
                    "trigger_distribution": workflow.get('triggers', {})
                },
                "performance": {
                    "fastest_execution": 0.8,
                    "slowest_execution": 5.2,
                    "avg_execution_time": workflow.get('performance', {}).get('avg_execution_time', 0),
                    "error_types": [
                        {"type": "timeout", "count": 2},
                        {"type": "network_error", "count": 1}
                    ]
                },
                "cost_savings": {
                    "estimated_manual_time": workflow.get('runs_count', 0) * 0.25,  # 15 minutes per execution
                    "actual_execution_time": workflow.get('runs_count', 0) * 0.03,  # 2 minutes automated
                    "time_saved_hours": workflow.get('performance', {}).get('time_saved_hours', 0),
                    "cost_per_hour": 50,  # USD
                    "total_savings": workflow.get('performance', {}).get('time_saved_hours', 0) * 50
                }
            }

            return analytics

        except Exception as e:
            logger.error(f"Error fetching workflow analytics: {e}")
            return {}

    async def get_workflow_executions(self, workflow_id: str, limit: int = 50) -> List[Dict]:
        """Get recent executions for a workflow"""
        try:
            # In a real implementation, this would query execution logs
            # For now, return sample executions
            executions = [
                {
                    "id": "exec-001",
                    "workflow_id": workflow_id,
                    "status": "completed",
                    "started_at": "2024-01-20T15:45:00Z",
                    "completed_at": "2024-01-20T15:45:02Z",
                    "execution_time": 2.1,
                    "event_type": "order.created",
                    "result": {
                        "success": True,
                        "actions_executed": 5,
                        "emails_sent": 1,
                        "records_updated": 2
                    }
                },
                {
                    "id": "exec-002",
                    "workflow_id": workflow_id,
                    "status": "completed",
                    "started_at": "2024-01-20T14:32:00Z",
                    "completed_at": "2024-01-20T14:32:01Z",
                    "execution_time": 1.8,
                    "event_type": "customer.created",
                    "result": {
                        "success": True,
                        "actions_executed": 3,
                        "emails_sent": 1,
                        "records_updated": 1
                    }
                },
                {
                    "id": "exec-003",
                    "workflow_id": workflow_id,
                    "status": "failed",
                    "started_at": "2024-01-20T13:15:00Z",
                    "completed_at": "2024-01-20T13:15:05Z",
                    "execution_time": 5.2,
                    "event_type": "order.created",
                    "error": "Email service timeout",
                    "result": {
                        "success": False,
                        "actions_executed": 2,
                        "emails_sent": 0,
                        "records_updated": 1
                    }
                }
            ]

            return executions[:limit]

        except Exception as e:
            logger.error(f"Error fetching workflow executions: {e}")
            return []

    async def _create_n8n_workflow(self, template: Dict, configuration: Dict) -> str:
        """Create n8n workflow (simplified simulation)"""
        try:
            # In a real implementation, this would call the n8n API
            # For now, simulate workflow creation
            n8n_workflow_id = f"n8n_{uuid4().hex[:8]}"
            
            logger.info(f"Created n8n workflow: {n8n_workflow_id} for template: {template['id']}")
            return n8n_workflow_id

        except Exception as e:
            logger.error(f"Error creating n8n workflow: {e}")
            raise

    async def _update_n8n_workflow(self, n8n_workflow_id: str, configuration: Dict) -> bool:
        """Update n8n workflow (simplified simulation)"""
        try:
            # In a real implementation, this would call the n8n API
            logger.info(f"Updated n8n workflow: {n8n_workflow_id}")
            return True

        except Exception as e:
            logger.error(f"Error updating n8n workflow: {e}")
            return False

    async def _delete_n8n_workflow(self, n8n_workflow_id: str) -> bool:
        """Delete n8n workflow (simplified simulation)"""
        try:
            # In a real implementation, this would call the n8n API
            logger.info(f"Deleted n8n workflow: {n8n_workflow_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting n8n workflow: {e}")
            return False

    async def _trigger_n8n_workflow(self, n8n_workflow_id: str, event_data: Dict) -> Dict:
        """Trigger n8n workflow execution (simplified simulation)"""
        try:
            # In a real implementation, this would call the n8n webhook API
            logger.info(f"Triggered n8n workflow: {n8n_workflow_id} with data: {event_data}")
            
            return {
                "success": True,
                "execution_id": f"n8n_exec_{uuid4().hex[:8]}",
                "actions_executed": 4,
                "execution_time": 2.1
            }

        except Exception as e:
            logger.error(f"Error triggering n8n workflow: {e}")
            return {
                "success": False,
                "error": str(e)
            }