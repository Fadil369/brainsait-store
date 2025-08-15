"""
Workflow Automation API endpoints
Manages n8n integration and business process automation
"""

from typing import Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_tenant_id, verify_rate_limit
from app.models.users import User
from app.services.workflow_automation import WorkflowAutomationService

router = APIRouter()


class WorkflowCreateRequest(BaseModel):
    """Request model for creating workflows"""
    template_id: str
    name: str
    configuration: Dict


class WorkflowUpdateRequest(BaseModel):
    """Request model for updating workflows"""
    configuration: Dict


class WorkflowTriggerRequest(BaseModel):
    """Request model for triggering workflows"""
    event_type: str
    event_data: Dict


class WorkflowTemplateResponse(BaseModel):
    """Response model for workflow templates"""
    id: str
    name: str
    description: str
    category: str
    trigger_events: List[str]
    actions: List[str]
    complexity: str
    estimated_time_saved: str
    status: str
    usage_count: int
    success_rate: float


class ActiveWorkflowResponse(BaseModel):
    """Response model for active workflows"""
    id: str
    template_id: str
    name: str
    status: str
    created_at: str
    last_run: Optional[str]
    runs_count: int
    success_rate: float


@router.get("/templates", response_model=List[WorkflowTemplateResponse])
async def get_workflow_templates(
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    category: Optional[str] = Query(None, description="Filter by category"),
):
    """Get available workflow templates"""
    
    # Rate limiting
    await verify_rate_limit(request)
    
    try:
        automation_service = WorkflowAutomationService(db, tenant_id)
        templates = await automation_service.get_workflow_templates()
        
        # Apply category filter if specified
        if category:
            templates = [t for t in templates if t['category'].lower() == category.lower()]
        
        return [
            WorkflowTemplateResponse(
                id=template['id'],
                name=template['name'],
                description=template['description'],
                category=template['category'],
                trigger_events=template['trigger_events'],
                actions=template['actions'],
                complexity=template['complexity'],
                estimated_time_saved=template['estimated_time_saved'],
                status=template['status'],
                usage_count=template['usage_count'],
                success_rate=template['success_rate']
            )
            for template in templates
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch workflow templates: {str(e)}"
        )


@router.get("/active", response_model=List[ActiveWorkflowResponse])
async def get_active_workflows(
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """Get active workflows for the current tenant"""
    
    # Rate limiting
    await verify_rate_limit(request)
    
    try:
        automation_service = WorkflowAutomationService(db, tenant_id)
        workflows = await automation_service.get_active_workflows(current_user.id)
        
        return [
            ActiveWorkflowResponse(
                id=workflow['id'],
                template_id=workflow['template_id'],
                name=workflow['name'],
                status=workflow['status'],
                created_at=workflow['created_at'],
                last_run=workflow.get('last_run'),
                runs_count=workflow['runs_count'],
                success_rate=workflow['success_rate']
            )
            for workflow in workflows
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch active workflows: {str(e)}"
        )


@router.post("/create")
async def create_workflow(
    workflow_request: WorkflowCreateRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """Create a new workflow from template"""
    
    # Rate limiting
    await verify_rate_limit(request)
    
    try:
        automation_service = WorkflowAutomationService(db, tenant_id)
        result = await automation_service.create_workflow(
            template_id=workflow_request.template_id,
            name=workflow_request.name,
            configuration=workflow_request.configuration,
            user_id=current_user.id
        )
        
        return {
            "success": True,
            "data": result,
            "message": f"Workflow '{workflow_request.name}' created successfully"
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create workflow: {str(e)}"
        )


@router.put("/{workflow_id}")
async def update_workflow(
    workflow_id: str,
    workflow_request: WorkflowUpdateRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """Update an existing workflow"""
    
    # Rate limiting
    await verify_rate_limit(request)
    
    try:
        automation_service = WorkflowAutomationService(db, tenant_id)
        result = await automation_service.update_workflow(
            workflow_id=workflow_id,
            configuration=workflow_request.configuration,
            user_id=current_user.id
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Workflow updated successfully"
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update workflow: {str(e)}"
        )


@router.delete("/{workflow_id}")
async def delete_workflow(
    workflow_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """Delete a workflow"""
    
    # Rate limiting
    await verify_rate_limit(request)
    
    try:
        automation_service = WorkflowAutomationService(db, tenant_id)
        result = await automation_service.delete_workflow(
            workflow_id=workflow_id,
            user_id=current_user.id
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Workflow deleted successfully"
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete workflow: {str(e)}"
        )


@router.post("/{workflow_id}/trigger")
async def trigger_workflow(
    workflow_id: str,
    trigger_request: WorkflowTriggerRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """Trigger a workflow execution"""
    
    # Rate limiting
    await verify_rate_limit(request)
    
    try:
        automation_service = WorkflowAutomationService(db, tenant_id)
        result = await automation_service.trigger_workflow(
            workflow_id=workflow_id,
            event_type=trigger_request.event_type,
            event_data=trigger_request.event_data
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Workflow triggered successfully"
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger workflow: {str(e)}"
        )


@router.get("/{workflow_id}/analytics")
async def get_workflow_analytics(
    workflow_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
    days: int = Query(30, ge=1, le=365, description="Number of days for analytics"),
):
    """Get analytics for a workflow"""
    
    # Rate limiting
    await verify_rate_limit(request)
    
    try:
        automation_service = WorkflowAutomationService(db, tenant_id)
        analytics = await automation_service.get_workflow_analytics(workflow_id, days)
        
        return {
            "success": True,
            "data": analytics,
            "message": "Workflow analytics retrieved successfully"
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get workflow analytics: {str(e)}"
        )


@router.get("/{workflow_id}/executions")
async def get_workflow_executions(
    workflow_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=100, description="Number of executions to return"),
):
    """Get recent executions for a workflow"""
    
    # Rate limiting
    await verify_rate_limit(request)
    
    try:
        automation_service = WorkflowAutomationService(db, tenant_id)
        executions = await automation_service.get_workflow_executions(workflow_id, limit)
        
        return {
            "success": True,
            "data": executions,
            "message": "Workflow executions retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get workflow executions: {str(e)}"
        )


@router.get("/categories")
async def get_workflow_categories(
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Get all available workflow categories"""
    
    # Rate limiting
    await verify_rate_limit(request)
    
    try:
        automation_service = WorkflowAutomationService(db, tenant_id)
        templates = await automation_service.get_workflow_templates()
        
        # Extract unique categories with counts
        categories = {}
        for template in templates:
            category = template['category']
            if category not in categories:
                categories[category] = {
                    'name': category,
                    'count': 0,
                    'description': {
                        'customer_management': 'Automate customer lifecycle and engagement workflows',
                        'order_management': 'Streamline order processing and fulfillment',
                        'marketing': 'Automate marketing campaigns and lead nurturing',
                        'customer_support': 'Optimize support ticket handling and resolution',
                        'inventory': 'Manage inventory levels and supplier communications',
                        'finance': 'Automate invoicing, payments, and financial workflows'
                    }.get(category, f'{category.title().replace("_", " ")} workflows')
                }
            categories[category]['count'] += 1
        
        return {
            "success": True,
            "data": list(categories.values()),
            "message": "Workflow categories retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get workflow categories: {str(e)}"
        )


@router.get("/stats")
async def get_automation_stats(
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """Get workflow automation statistics"""
    
    # Rate limiting
    await verify_rate_limit(request)
    
    try:
        automation_service = WorkflowAutomationService(db, tenant_id)
        
        # Get templates and active workflows
        templates = await automation_service.get_workflow_templates()
        active_workflows = await automation_service.get_active_workflows(current_user.id)
        
        # Calculate statistics
        total_runs = sum(w['runs_count'] for w in active_workflows)
        avg_success_rate = sum(w['success_rate'] for w in active_workflows) / len(active_workflows) if active_workflows else 0
        total_time_saved = sum(w.get('performance', {}).get('time_saved_hours', 0) for w in active_workflows)
        
        stats = {
            "overview": {
                "total_templates": len(templates),
                "active_workflows": len(active_workflows),
                "total_executions": total_runs,
                "average_success_rate": round(avg_success_rate, 1),
                "total_time_saved_hours": round(total_time_saved, 1)
            },
            "categories": {
                category: len([t for t in templates if t['category'] == category])
                for category in set(t['category'] for t in templates)
            },
            "recent_activity": {
                "workflows_created_this_month": len([w for w in active_workflows if '2024-01' in w['created_at']]),
                "executions_today": sum(1 for w in active_workflows if w.get('last_run') and '2024-01-20' in w['last_run']),
                "most_used_templates": sorted(
                    templates, 
                    key=lambda x: x['usage_count'], 
                    reverse=True
                )[:3]
            },
            "performance": {
                "workflows_by_status": {
                    "active": len([w for w in active_workflows if w['status'] == 'active']),
                    "paused": len([w for w in active_workflows if w['status'] == 'paused']),
                    "error": len([w for w in active_workflows if w['status'] == 'error'])
                },
                "cost_savings": {
                    "estimated_cost_per_hour": 50,  # USD
                    "total_savings": round(total_time_saved * 50, 2),
                    "monthly_savings": round(total_time_saved * 50 / 3, 2)  # Assuming 3 months of data
                }
            }
        }
        
        return {
            "success": True,
            "data": stats,
            "message": "Automation statistics retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get automation stats: {str(e)}"
        )