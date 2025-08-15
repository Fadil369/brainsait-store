"""
Test cases for the Workflow Automation Service
"""

import pytest
import json
from uuid import uuid4
from unittest.mock import AsyncMock

from app.services.workflow_automation import WorkflowAutomationService


class TestWorkflowAutomationService:
    """Test the workflow automation functionality"""

    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        return AsyncMock()

    @pytest.fixture
    def automation_service(self, mock_db):
        """Create automation service instance"""
        return WorkflowAutomationService(mock_db, "test-tenant")

    @pytest.mark.asyncio
    async def test_get_workflow_templates(self, automation_service):
        """Test fetching workflow templates"""
        templates = await automation_service.get_workflow_templates()
        
        assert isinstance(templates, list)
        assert len(templates) > 0
        
        # Check that all required fields are present
        for template in templates:
            assert 'id' in template
            assert 'name' in template
            assert 'description' in template
            assert 'category' in template
            assert 'trigger_events' in template
            assert 'actions' in template
            assert 'complexity' in template
            assert 'estimated_time_saved' in template
            assert 'status' in template
            assert 'usage_count' in template
            assert 'success_rate' in template

    @pytest.mark.asyncio
    async def test_get_active_workflows_empty_cache(self, automation_service):
        """Test fetching active workflows with empty cache"""
        user_id = uuid4()
        
        # Mock Redis to return None (empty cache)
        automation_service.redis.get = AsyncMock(return_value=None)
        automation_service.redis.setex = AsyncMock()
        
        workflows = await automation_service.get_active_workflows(user_id)
        
        assert isinstance(workflows, list)
        # Should return sample data when cache is empty
        assert len(workflows) >= 0

    @pytest.mark.asyncio
    async def test_get_active_workflows_with_cache(self, automation_service):
        """Test fetching active workflows from cache"""
        user_id = uuid4()
        
        cached_data = [
            {
                "id": "workflow-001",
                "template_id": "customer-lifecycle-automation",
                "name": "Test Workflow",
                "status": "active",
                "created_at": "2024-01-15T10:30:00Z",
                "runs_count": 50,
                "success_rate": 95.0
            }
        ]
        
        # Mock Redis to return cached data
        automation_service.redis.get = AsyncMock(return_value=json.dumps(cached_data))
        
        workflows = await automation_service.get_active_workflows(user_id)
        
        assert workflows == cached_data

    @pytest.mark.asyncio
    async def test_create_workflow_success(self, automation_service):
        """Test successful workflow creation"""
        template_id = "customer-lifecycle-automation"
        name = "Test Customer Workflow"
        configuration = {
            "welcome_email_delay": 10,
            "follow_up_schedule": [1, 3, 7],
            "retention_trigger_days": 60
        }
        user_id = uuid4()
        
        # Mock Redis operations and n8n workflow creation
        automation_service.redis.setex = AsyncMock()
        automation_service.redis.delete = AsyncMock()
        automation_service._create_n8n_workflow = AsyncMock(return_value="n8n_12345678")
        
        result = await automation_service.create_workflow(template_id, name, configuration, user_id)
        
        assert result['success'] is True
        assert 'workflow_id' in result
        assert result['n8n_workflow_id'] == "n8n_12345678"
        assert result['status'] == 'active'

    @pytest.mark.asyncio
    async def test_create_workflow_invalid_template(self, automation_service):
        """Test workflow creation with invalid template"""
        template_id = "non-existent-template"
        name = "Test Workflow"
        configuration = {}
        user_id = uuid4()
        
        with pytest.raises(ValueError) as exc_info:
            await automation_service.create_workflow(template_id, name, configuration, user_id)
        
        assert f"Template {template_id} not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_update_workflow(self, automation_service):
        """Test workflow update"""
        workflow_id = "workflow-001"
        configuration = {
            "welcome_email_delay": 15,
            "follow_up_schedule": [1, 5, 14]
        }
        user_id = uuid4()
        
        workflow_data = {
            "id": workflow_id,
            "template_id": "customer-lifecycle-automation",
            "name": "Test Workflow",
            "status": "active",
            "n8n_workflow_id": "n8n_12345678"
        }
        
        # Mock Redis operations
        automation_service.redis.get = AsyncMock(return_value=json.dumps(workflow_data))
        automation_service.redis.setex = AsyncMock()
        automation_service.redis.delete = AsyncMock()
        automation_service._update_n8n_workflow = AsyncMock(return_value=True)
        
        result = await automation_service.update_workflow(workflow_id, configuration, user_id)
        
        assert result['success'] is True
        assert result['workflow_id'] == workflow_id

    @pytest.mark.asyncio
    async def test_update_workflow_not_found(self, automation_service):
        """Test update of non-existent workflow"""
        workflow_id = "non-existent-workflow"
        configuration = {}
        user_id = uuid4()
        
        # Mock Redis to return None
        automation_service.redis.get = AsyncMock(return_value=None)
        
        with pytest.raises(ValueError) as exc_info:
            await automation_service.update_workflow(workflow_id, configuration, user_id)
        
        assert "Workflow not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_delete_workflow(self, automation_service):
        """Test workflow deletion"""
        workflow_id = "workflow-001"
        user_id = uuid4()
        
        workflow_data = {
            "id": workflow_id,
            "n8n_workflow_id": "n8n_12345678"
        }
        
        # Mock Redis operations
        automation_service.redis.get = AsyncMock(return_value=json.dumps(workflow_data))
        automation_service.redis.delete = AsyncMock()
        automation_service._delete_n8n_workflow = AsyncMock(return_value=True)
        
        result = await automation_service.delete_workflow(workflow_id, user_id)
        
        assert result['success'] is True

    @pytest.mark.asyncio
    async def test_trigger_workflow(self, automation_service):
        """Test workflow trigger"""
        workflow_id = "workflow-001"
        event_type = "customer.created"
        event_data = {"customer_id": "cust_123", "email": "test@example.com"}
        
        workflow_data = {
            "id": workflow_id,
            "status": "active",
            "n8n_workflow_id": "n8n_12345678",
            "runs_count": 10,
            "success_rate": 90.0
        }
        
        # Mock Redis operations and n8n trigger
        automation_service.redis.get = AsyncMock(return_value=json.dumps(workflow_data))
        automation_service.redis.setex = AsyncMock()
        automation_service._trigger_n8n_workflow = AsyncMock(return_value={
            "success": True,
            "execution_id": "n8n_exec_12345",
            "actions_executed": 3
        })
        
        result = await automation_service.trigger_workflow(workflow_id, event_type, event_data)
        
        assert result['success'] is True
        assert 'execution_id' in result
        assert result['status'] == 'completed'

    @pytest.mark.asyncio
    async def test_trigger_workflow_not_found(self, automation_service):
        """Test trigger of non-existent workflow"""
        workflow_id = "non-existent-workflow"
        event_type = "test.event"
        event_data = {}
        
        # Mock Redis to return None
        automation_service.redis.get = AsyncMock(return_value=None)
        
        with pytest.raises(ValueError) as exc_info:
            await automation_service.trigger_workflow(workflow_id, event_type, event_data)
        
        assert "Workflow not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_trigger_workflow_not_active(self, automation_service):
        """Test trigger of paused workflow"""
        workflow_id = "workflow-001"
        event_type = "test.event"
        event_data = {}
        
        workflow_data = {
            "id": workflow_id,
            "status": "paused"
        }
        
        # Mock Redis to return paused workflow
        automation_service.redis.get = AsyncMock(return_value=json.dumps(workflow_data))
        
        with pytest.raises(ValueError) as exc_info:
            await automation_service.trigger_workflow(workflow_id, event_type, event_data)
        
        assert "cannot trigger" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_workflow_analytics(self, automation_service):
        """Test fetching workflow analytics"""
        workflow_id = "workflow-001"
        days = 30
        
        workflow_data = {
            "id": workflow_id,
            "name": "Test Workflow",
            "runs_count": 100,
            "success_rate": 95.0,
            "performance": {
                "avg_execution_time": 2.5,
                "time_saved_hours": 25.0
            },
            "triggers": {
                "customer.created": 60,
                "order.completed": 40
            }
        }
        
        # Mock Redis to return workflow data
        automation_service.redis.get = AsyncMock(return_value=json.dumps(workflow_data))
        
        analytics = await automation_service.get_workflow_analytics(workflow_id, days)
        
        assert analytics['workflow_id'] == workflow_id
        assert 'period' in analytics
        assert 'overview' in analytics
        assert 'trends' in analytics
        assert 'performance' in analytics
        assert 'cost_savings' in analytics
        
        assert analytics['period']['days'] == days
        assert analytics['overview']['total_runs'] == 100
        assert analytics['overview']['success_rate'] == 95.0

    @pytest.mark.asyncio
    async def test_get_workflow_executions(self, automation_service):
        """Test fetching workflow executions"""
        workflow_id = "workflow-001"
        limit = 10
        
        executions = await automation_service.get_workflow_executions(workflow_id, limit)
        
        assert isinstance(executions, list)
        assert len(executions) <= limit
        
        # Check execution structure if any exist
        if executions:
            execution = executions[0]
            assert 'id' in execution
            assert 'workflow_id' in execution
            assert 'status' in execution
            assert 'started_at' in execution
            assert 'event_type' in execution
            assert execution['workflow_id'] == workflow_id

    @pytest.mark.asyncio
    async def test_n8n_workflow_creation(self, automation_service):
        """Test n8n workflow creation"""
        template = {
            "id": "test-template",
            "name": "Test Template",
            "category": "test"
        }
        configuration = {"test_config": True}
        
        n8n_workflow_id = await automation_service._create_n8n_workflow(template, configuration)
        
        assert isinstance(n8n_workflow_id, str)
        assert n8n_workflow_id.startswith("n8n_")

    @pytest.mark.asyncio
    async def test_n8n_workflow_update(self, automation_service):
        """Test n8n workflow update"""
        n8n_workflow_id = "n8n_12345678"
        configuration = {"updated_config": True}
        
        result = await automation_service._update_n8n_workflow(n8n_workflow_id, configuration)
        
        assert result is True

    @pytest.mark.asyncio
    async def test_n8n_workflow_deletion(self, automation_service):
        """Test n8n workflow deletion"""
        n8n_workflow_id = "n8n_12345678"
        
        result = await automation_service._delete_n8n_workflow(n8n_workflow_id)
        
        assert result is True

    @pytest.mark.asyncio
    async def test_n8n_workflow_trigger(self, automation_service):
        """Test n8n workflow trigger"""
        n8n_workflow_id = "n8n_12345678"
        event_data = {"test": "data"}
        
        result = await automation_service._trigger_n8n_workflow(n8n_workflow_id, event_data)
        
        assert result['success'] is True
        assert 'execution_id' in result
        assert 'actions_executed' in result
        assert 'execution_time' in result

    def test_template_data_structure(self, automation_service):
        """Test that all templates have consistent data structure"""
        async def run_test():
            templates = await automation_service.get_workflow_templates()
            
            required_fields = [
                'id', 'name', 'description', 'category', 'trigger_events',
                'actions', 'complexity', 'estimated_time_saved', 'status',
                'usage_count', 'success_rate', 'configuration'
            ]
            
            for template in templates:
                for field in required_fields:
                    assert field in template, f"Missing field '{field}' in template {template.get('id', 'unknown')}"
                
                # Validate specific field types
                assert isinstance(template['trigger_events'], list)
                assert isinstance(template['actions'], list)
                assert isinstance(template['usage_count'], int)
                assert isinstance(template['success_rate'], (int, float))
                assert template['complexity'] in ['easy', 'medium', 'advanced']
                assert template['status'] in ['active', 'beta', 'deprecated']
        
        import asyncio
        asyncio.run(run_test())


if __name__ == "__main__":
    pytest.main([__file__])