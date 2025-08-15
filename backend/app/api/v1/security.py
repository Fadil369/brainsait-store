"""
Security management API endpoints for MFA, audit logs, and security monitoring
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_admin_user, get_current_user, get_tenant_id
from app.models.users import User
from app.services.auth_security import auth_security_service
from app.services.audit import audit_service

router = APIRouter(prefix="/security", tags=["Security Management"])


# Pydantic models for requests
class MFASetupRequest(BaseModel):
    verification_code: str


class MFADisableRequest(BaseModel):
    password: str
    verification_code: str


class SecurityEventQuery(BaseModel):
    hours: Optional[int] = 24
    severity: Optional[str] = None
    event_type: Optional[str] = None


class AuditLogQuery(BaseModel):
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    user_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    event_types: Optional[List[str]] = None
    limit: int = 100
    offset: int = 0


# MFA Endpoints
@router.post("/mfa/setup")
async def setup_mfa(
    request: Request,
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Setup Multi-Factor Authentication for the current user
    """
    try:
        mfa_data = await auth_security_service.setup_mfa(
            user_id=current_user.id,
            user_email=current_user.email
        )
        
        # Log MFA setup initiation
        await audit_service.log_event(
            event_type="mfa_setup_initiated",
            resource_type="user",
            action="mfa_setup",
            user_id=current_user.id,
            resource_id=str(current_user.id),
            tenant_id=tenant_id,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent", ""),
            success=True,
            details={"step": "initial_setup"}
        )
        
        return {
            "message": "MFA setup initiated",
            "qr_code": mfa_data['qr_code'],
            "manual_entry_key": mfa_data['manual_entry_key'],
            "backup_codes": mfa_data['backup_codes'],
            "instructions": "Scan the QR code with your authenticator app and verify with a code"
        }
        
    except Exception as e:
        await audit_service.log_event(
            event_type="mfa_setup_failed",
            resource_type="user",
            action="mfa_setup",
            user_id=current_user.id,
            resource_id=str(current_user.id),
            tenant_id=tenant_id,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent", ""),
            success=False,
            error_message=str(e)
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to setup MFA"
        )


@router.post("/mfa/confirm")
async def confirm_mfa_setup(
    setup_request: MFASetupRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Confirm MFA setup with verification code
    """
    try:
        success = await auth_security_service.confirm_mfa_setup(
            user_id=current_user.id,
            verification_code=setup_request.verification_code
        )
        
        if success:
            # Log successful MFA setup
            await audit_service.log_event(
                event_type="mfa_enabled",
                resource_type="user",
                action="mfa_confirm",
                user_id=current_user.id,
                resource_id=str(current_user.id),
                tenant_id=tenant_id,
                ip_address=request.client.host,
                user_agent=request.headers.get("user-agent", ""),
                success=True,
                details={"mfa_enabled": True}
            )
            
            return {"message": "MFA enabled successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification code"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        await audit_service.log_event(
            event_type="mfa_setup_failed",
            resource_type="user",
            action="mfa_confirm",
            user_id=current_user.id,
            resource_id=str(current_user.id),
            tenant_id=tenant_id,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent", ""),
            success=False,
            error_message=str(e)
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to confirm MFA setup"
        )


@router.post("/mfa/disable")
async def disable_mfa(
    disable_request: MFADisableRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Disable MFA for the current user
    """
    try:
        success = await auth_security_service.disable_mfa(
            user_id=current_user.id,
            password=disable_request.password,
            verification_code=disable_request.verification_code
        )
        
        if success:
            # Log MFA disable
            await audit_service.log_event(
                event_type="mfa_disabled",
                resource_type="user",
                action="mfa_disable",
                user_id=current_user.id,
                resource_id=str(current_user.id),
                tenant_id=tenant_id,
                ip_address=request.client.host,
                user_agent=request.headers.get("user-agent", ""),
                success=True,
                details={"mfa_enabled": False}
            )
            
            return {"message": "MFA disabled successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to disable MFA"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        await audit_service.log_event(
            event_type="mfa_disable_failed",
            resource_type="user",
            action="mfa_disable",
            user_id=current_user.id,
            resource_id=str(current_user.id),
            tenant_id=tenant_id,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent", ""),
            success=False,
            error_message=str(e)
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to disable MFA"
        )


# Session Management Endpoints
@router.get("/sessions")
async def get_active_sessions(
    current_user: User = Depends(get_current_user)
):
    """
    Get all active sessions for the current user
    """
    try:
        sessions = await auth_security_service.get_active_sessions(current_user.id)
        return {
            "active_sessions": sessions,
            "total_count": len(sessions)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve sessions"
        )


@router.delete("/sessions/{session_id}")
async def revoke_session(
    session_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Revoke a specific session
    """
    try:
        success = await auth_security_service.revoke_session(current_user.id, session_id)
        
        if success:
            # Log session revocation
            await audit_service.log_event(
                event_type="session_revoked",
                resource_type="session",
                action="revoke",
                user_id=current_user.id,
                resource_id=session_id,
                tenant_id=tenant_id,
                ip_address=request.client.host,
                user_agent=request.headers.get("user-agent", ""),
                success=True
            )
            
            return {"message": "Session revoked successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to revoke session"
        )


@router.delete("/sessions/all")
async def revoke_all_sessions(
    request: Request,
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Revoke all sessions for the current user
    """
    try:
        count = await auth_security_service.revoke_all_sessions(current_user.id)
        
        # Log bulk session revocation
        await audit_service.log_event(
            event_type="all_sessions_revoked",
            resource_type="session",
            action="revoke_all",
            user_id=current_user.id,
            tenant_id=tenant_id,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent", ""),
            success=True,
            details={"sessions_revoked": count}
        )
        
        return {
            "message": f"Revoked {count} sessions successfully",
            "sessions_revoked": count
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to revoke sessions"
        )


# Audit and Monitoring Endpoints (Admin only)
@router.get("/audit/logs")
async def get_audit_logs(
    query: AuditLogQuery,
    current_user: User = Depends(get_current_admin_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Get audit logs (Admin only)
    """
    try:
        logs = await audit_service.get_audit_trail(
            resource_type=query.resource_type,
            resource_id=query.resource_id,
            user_id=query.user_id,
            tenant_id=tenant_id,
            start_date=query.start_date,
            end_date=query.end_date,
            event_types=query.event_types,
            limit=query.limit,
            offset=query.offset
        )
        
        return {
            "audit_logs": logs,
            "total_count": len(logs),
            "query_parameters": query.dict()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve audit logs"
        )


@router.get("/dashboard")
async def get_security_dashboard(
    hours: int = 24,
    current_user: User = Depends(get_current_admin_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Get security dashboard data (Admin only)
    """
    try:
        dashboard_data = await audit_service.get_security_dashboard(
            tenant_id=tenant_id,
            hours=hours
        )
        
        return {
            "dashboard": dashboard_data,
            "time_range_hours": hours,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate security dashboard"
        )


@router.get("/events")
async def get_security_events(
    hours: int = 24,
    severity: Optional[str] = None,
    event_type: Optional[str] = None,
    current_user: User = Depends(get_current_admin_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Get recent security events (Admin only)
    """
    try:
        # This would typically query the security events from the audit service
        # For now, return a placeholder response
        
        events = await audit_service.get_audit_trail(
            tenant_id=tenant_id,
            start_date=datetime.utcnow() - timedelta(hours=hours),
            event_types=[event_type] if event_type else None,
            limit=100
        )
        
        # Filter by severity if specified
        if severity:
            events = [e for e in events if e.get('severity') == severity]
        
        return {
            "security_events": events,
            "total_count": len(events),
            "filters": {
                "hours": hours,
                "severity": severity,
                "event_type": event_type
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve security events"
        )


@router.post("/scan/user/{user_id}")
async def scan_user_activity(
    user_id: int,
    request: Request,
    current_user: User = Depends(get_current_admin_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Scan a specific user's activity for suspicious patterns (Admin only)
    """
    try:
        # Get user's recent activity
        user_logs = await audit_service.get_audit_trail(
            user_id=user_id,
            tenant_id=tenant_id,
            start_date=datetime.utcnow() - timedelta(days=7),
            limit=1000
        )
        
        # Basic suspicious activity analysis
        suspicious_indicators = []
        
        # Check for unusual login times
        login_hours = []
        for log in user_logs:
            if log.get('event_type') == 'login_success':
                try:
                    timestamp = datetime.fromisoformat(log['timestamp'])
                    hour = timestamp.hour
                    login_hours.append(hour)
                except:
                    continue
        
        if login_hours:
            # Check for logins outside normal business hours
            unusual_hours = [h for h in login_hours if h < 6 or h > 22]
            if len(unusual_hours) > len(login_hours) * 0.3:  # More than 30% unusual
                suspicious_indicators.append("Frequent logins outside business hours")
        
        # Check for multiple failed logins
        failed_logins = [log for log in user_logs if log.get('event_type') == 'login_failed']
        if len(failed_logins) > 10:
            suspicious_indicators.append("Multiple failed login attempts")
        
        # Check for data export activity
        exports = [log for log in user_logs if 'export' in log.get('action', '').lower()]
        if len(exports) > 5:
            suspicious_indicators.append("High volume of data exports")
        
        # Calculate risk score
        risk_score = min(len(suspicious_indicators) * 25, 100)
        
        # Log the security scan
        await audit_service.log_security_event(
            event_type="user_activity_scan",
            title=f"Security scan performed on user {user_id}",
            description=f"Admin {current_user.id} performed security scan on user {user_id}",
            severity="medium",
            risk_score=risk_score,
            user_id=current_user.id,
            tenant_id=tenant_id,
            ip_address=request.client.host,
            indicators={
                "target_user_id": user_id,
                "suspicious_indicators": suspicious_indicators,
                "total_events_analyzed": len(user_logs)
            }
        )
        
        return {
            "user_id": user_id,
            "scan_results": {
                "risk_score": risk_score,
                "suspicious_indicators": suspicious_indicators,
                "total_events_analyzed": len(user_logs),
                "scan_timestamp": datetime.utcnow().isoformat()
            },
            "recommendations": [
                "Monitor user activity closely" if risk_score > 50 else "Normal activity pattern",
                "Consider requiring password change" if risk_score > 75 else None,
                "Enable MFA if not already active" if risk_score > 60 else None
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to scan user activity"
        )