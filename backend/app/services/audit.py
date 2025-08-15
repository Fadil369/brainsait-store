"""
Audit logging service for comprehensive security monitoring
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from ..core.config import settings
from ..core.database import get_db
from ..models.audit import (
    AuditLog, SecurityEvent, LoginAttempt, DataAccess, FileActivity,
    AuditEventType, AuditSeverity
)

# Redis client for real-time logging
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


class AuditService:
    """
    Comprehensive audit logging service
    """
    
    def __init__(self):
        self.batch_size = 100
        self.flush_interval = 30  # seconds
        self._buffer = []
        self._last_flush = datetime.utcnow()
    
    async def log_event(
        self,
        event_type: Union[str, AuditEventType],
        resource_type: str,
        action: str,
        user_id: Optional[int] = None,
        resource_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        request_id: Optional[str] = None,
        session_id: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        severity: Union[str, AuditSeverity] = AuditSeverity.MEDIUM,
        processing_time: Optional[int] = None,
        is_sensitive: bool = False,
        compliance_tags: Optional[List[str]] = None
    ) -> str:
        """
        Log an audit event
        """
        audit_entry = {
            'event_type': str(event_type),
            'severity': str(severity),
            'resource_type': resource_type,
            'resource_id': resource_id,
            'action': action,
            'user_id': user_id,
            'tenant_id': tenant_id,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'request_id': request_id,
            'session_id': session_id,
            'success': success,
            'error_message': error_message,
            'details': details or {},
            'old_values': old_values,
            'new_values': new_values,
            'processing_time': processing_time,
            'is_sensitive': is_sensitive,
            'compliance_tags': compliance_tags or [],
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Add to buffer for batch processing
        self._buffer.append(audit_entry)
        
        # Also store in Redis for real-time access
        await redis_client.lpush(
            "audit_events_realtime",
            json.dumps(audit_entry)
        )
        await redis_client.ltrim("audit_events_realtime", 0, 9999)
        
        # Flush if buffer is full or time interval passed
        if (len(self._buffer) >= self.batch_size or 
            (datetime.utcnow() - self._last_flush).seconds >= self.flush_interval):
            await self._flush_buffer()
        
        return audit_entry['timestamp']
    
    async def log_security_event(
        self,
        event_type: str,
        title: str,
        description: str,
        severity: Union[str, AuditSeverity] = AuditSeverity.MEDIUM,
        risk_score: int = 0,
        user_id: Optional[int] = None,
        tenant_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        indicators: Optional[Dict[str, Any]] = None,
        detection_method: str = "automated"
    ) -> str:
        """
        Log a security event
        """
        security_event = {
            'event_type': event_type,
            'severity': str(severity),
            'risk_score': risk_score,
            'title': title,
            'description': description,
            'user_id': user_id,
            'tenant_id': tenant_id,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'indicators': indicators or {},
            'detection_method': detection_method,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Store in Redis for immediate alerting
        await redis_client.lpush(
            "security_events_realtime",
            json.dumps(security_event)
        )
        await redis_client.ltrim("security_events_realtime", 0, 999)
        
        # High severity events get immediate processing
        if severity in [AuditSeverity.HIGH, AuditSeverity.CRITICAL]:
            await self._process_high_severity_event(security_event)
        
        return security_event['timestamp']
    
    async def log_login_attempt(
        self,
        email: str,
        success: bool,
        ip_address: str,
        user_agent: str,
        failure_reason: Optional[str] = None,
        auth_method: str = "password",
        mfa_used: bool = False,
        tenant_id: Optional[str] = None,
        session_id: Optional[str] = None,
        device_fingerprint: Optional[str] = None,
        risk_score: int = 0
    ):
        """
        Log a login attempt
        """
        login_attempt = {
            'email': email,
            'success': success,
            'failure_reason': failure_reason,
            'auth_method': auth_method,
            'mfa_used': mfa_used,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'tenant_id': tenant_id,
            'session_id': session_id,
            'device_fingerprint': device_fingerprint,
            'risk_score': risk_score,
            'suspicious': risk_score > 70,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Store in Redis
        await redis_client.lpush(
            "login_attempts_realtime",
            json.dumps(login_attempt)
        )
        await redis_client.ltrim("login_attempts_realtime", 0, 9999)
        
        # Check for suspicious patterns
        if not success or risk_score > 50:
            await self._analyze_login_patterns(email, ip_address)
    
    async def log_data_access(
        self,
        user_id: int,
        resource_type: str,
        resource_id: str,
        action: str,
        ip_address: str,
        user_agent: str,
        tenant_id: Optional[str] = None,
        data_sensitivity: str = "internal",
        pii_accessed: bool = False,
        records_accessed: int = 0,
        data_exported: bool = False,
        export_format: Optional[str] = None,
        compliance_scope: Optional[List[str]] = None,
        request_method: Optional[str] = None,
        request_path: Optional[str] = None,
        query_parameters: Optional[Dict[str, Any]] = None
    ):
        """
        Log data access for compliance and security monitoring
        """
        data_access = {
            'user_id': user_id,
            'resource_type': resource_type,
            'resource_id': resource_id,
            'action': action,
            'data_sensitivity': data_sensitivity,
            'pii_accessed': pii_accessed,
            'records_accessed': records_accessed,
            'data_exported': data_exported,
            'export_format': export_format,
            'compliance_scope': compliance_scope or [],
            'ip_address': ip_address,
            'user_agent': user_agent,
            'tenant_id': tenant_id,
            'request_method': request_method,
            'request_path': request_path,
            'query_parameters': query_parameters or {},
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Store in Redis
        await redis_client.lpush(
            "data_access_realtime",
            json.dumps(data_access)
        )
        await redis_client.ltrim("data_access_realtime", 0, 9999)
        
        # Alert on sensitive data access
        if pii_accessed or data_sensitivity in ["confidential", "restricted"]:
            await self._alert_sensitive_data_access(data_access)
    
    async def log_file_activity(
        self,
        file_path: str,
        file_name: str,
        activity_type: str,
        user_id: int,
        ip_address: str,
        user_agent: str,
        tenant_id: Optional[str] = None,
        file_size: Optional[int] = None,
        file_hash: Optional[str] = None,
        mime_type: Optional[str] = None,
        virus_scan_result: Optional[str] = None,
        malware_detected: bool = False,
        file_classification: str = "internal",
        contains_pii: bool = False
    ):
        """
        Log file activity
        """
        file_activity = {
            'file_path': file_path,
            'file_name': file_name,
            'activity_type': activity_type,
            'user_id': user_id,
            'file_size': file_size,
            'file_hash': file_hash,
            'mime_type': mime_type,
            'virus_scan_result': virus_scan_result,
            'malware_detected': malware_detected,
            'file_classification': file_classification,
            'contains_pii': contains_pii,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'tenant_id': tenant_id,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Store in Redis
        await redis_client.lpush(
            "file_activities_realtime",
            json.dumps(file_activity)
        )
        await redis_client.ltrim("file_activities_realtime", 0, 9999)
        
        # Alert on malware detection
        if malware_detected:
            await self.log_security_event(
                event_type="malware_detected",
                title=f"Malware detected in file: {file_name}",
                description=f"File {file_name} uploaded by user {user_id} contains malware",
                severity=AuditSeverity.CRITICAL,
                risk_score=100,
                user_id=user_id,
                tenant_id=tenant_id,
                ip_address=ip_address,
                indicators={'file_path': file_path, 'file_hash': file_hash}
            )
    
    async def get_audit_trail(
        self,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        user_id: Optional[int] = None,
        tenant_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        event_types: Optional[List[str]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Retrieve audit trail with filtering
        """
        # Try Redis first for recent events
        redis_events = await redis_client.lrange("audit_events_realtime", 0, limit - 1)
        events = []
        
        for event_data in redis_events:
            try:
                event = json.loads(event_data)
                # Apply filters
                if self._matches_filters(event, resource_type, resource_id, user_id, 
                                       tenant_id, start_date, end_date, event_types):
                    events.append(event)
            except json.JSONDecodeError:
                continue
        
        # If we need more events or older data, query database
        if len(events) < limit:
            # Database query would go here
            pass
        
        return events[:limit]
    
    async def get_security_dashboard(
        self,
        tenant_id: Optional[str] = None,
        hours: int = 24
    ) -> Dict[str, Any]:
        """
        Get security dashboard data
        """
        since = datetime.utcnow() - timedelta(hours=hours)
        
        # Get recent security events from Redis
        security_events = await redis_client.lrange("security_events_realtime", 0, -1)
        login_attempts = await redis_client.lrange("login_attempts_realtime", 0, -1)
        
        dashboard_data = {
            'total_events': 0,
            'critical_events': 0,
            'failed_logins': 0,
            'successful_logins': 0,
            'unique_ips': set(),
            'top_events': {},
            'timeline': [],
            'risk_score': 0
        }
        
        # Process security events
        for event_data in security_events:
            try:
                event = json.loads(event_data)
                event_time = datetime.fromisoformat(event['timestamp'])
                
                if event_time >= since:
                    if not tenant_id or event.get('tenant_id') == tenant_id:
                        dashboard_data['total_events'] += 1
                        
                        if event.get('severity') == 'critical':
                            dashboard_data['critical_events'] += 1
                        
                        event_type = event.get('event_type', 'unknown')
                        dashboard_data['top_events'][event_type] = dashboard_data['top_events'].get(event_type, 0) + 1
                        
                        if event.get('ip_address'):
                            dashboard_data['unique_ips'].add(event['ip_address'])
                        
                        dashboard_data['risk_score'] += event.get('risk_score', 0)
            except (json.JSONDecodeError, ValueError):
                continue
        
        # Process login attempts
        for attempt_data in login_attempts:
            try:
                attempt = json.loads(attempt_data)
                attempt_time = datetime.fromisoformat(attempt['timestamp'])
                
                if attempt_time >= since:
                    if not tenant_id or attempt.get('tenant_id') == tenant_id:
                        if attempt.get('success'):
                            dashboard_data['successful_logins'] += 1
                        else:
                            dashboard_data['failed_logins'] += 1
                        
                        if attempt.get('ip_address'):
                            dashboard_data['unique_ips'].add(attempt['ip_address'])
            except (json.JSONDecodeError, ValueError):
                continue
        
        # Calculate average risk score
        if dashboard_data['total_events'] > 0:
            dashboard_data['risk_score'] = dashboard_data['risk_score'] // dashboard_data['total_events']
        
        dashboard_data['unique_ips'] = len(dashboard_data['unique_ips'])
        
        return dashboard_data
    
    async def _flush_buffer(self):
        """
        Flush audit events buffer to database
        """
        if not self._buffer:
            return
        
        try:
            # In a real implementation, you would batch insert to database here
            # For now, we'll just clear the buffer
            self._buffer.clear()
            self._last_flush = datetime.utcnow()
        except Exception as e:
            # Log error but don't fail the request
            print(f"Failed to flush audit buffer: {e}")
    
    async def _process_high_severity_event(self, event: Dict[str, Any]):
        """
        Process high severity security events immediately
        """
        # Send alerts, notifications, etc.
        # For now, just store in a high-priority queue
        await redis_client.lpush(
            "high_severity_events",
            json.dumps(event)
        )
        await redis_client.ltrim("high_severity_events", 0, 99)
    
    async def _analyze_login_patterns(self, email: str, ip_address: str):
        """
        Analyze login patterns for suspicious activity
        """
        # Get recent login attempts for this email/IP
        login_attempts = await redis_client.lrange("login_attempts_realtime", 0, 99)
        
        email_failures = 0
        ip_failures = 0
        recent_attempts = 0
        
        cutoff_time = datetime.utcnow() - timedelta(minutes=15)
        
        for attempt_data in login_attempts:
            try:
                attempt = json.loads(attempt_data)
                attempt_time = datetime.fromisoformat(attempt['timestamp'])
                
                if attempt_time >= cutoff_time:
                    recent_attempts += 1
                    
                    if not attempt.get('success'):
                        if attempt.get('email') == email:
                            email_failures += 1
                        if attempt.get('ip_address') == ip_address:
                            ip_failures += 1
            except (json.JSONDecodeError, ValueError):
                continue
        
        # Trigger alerts based on patterns
        if email_failures >= 5:
            await self.log_security_event(
                event_type="brute_force_attack",
                title=f"Multiple failed login attempts for {email}",
                description=f"{email_failures} failed attempts in 15 minutes",
                severity=AuditSeverity.HIGH,
                risk_score=80,
                ip_address=ip_address,
                indicators={'email': email, 'failure_count': email_failures}
            )
        
        if ip_failures >= 10:
            await self.log_security_event(
                event_type="suspicious_ip_activity",
                title=f"Multiple failed login attempts from {ip_address}",
                description=f"{ip_failures} failed attempts from IP in 15 minutes",
                severity=AuditSeverity.HIGH,
                risk_score=85,
                ip_address=ip_address,
                indicators={'ip_address': ip_address, 'failure_count': ip_failures}
            )
    
    async def _alert_sensitive_data_access(self, access_data: Dict[str, Any]):
        """
        Alert on sensitive data access
        """
        await self.log_security_event(
            event_type="sensitive_data_access",
            title=f"Sensitive data accessed by user {access_data['user_id']}",
            description=f"User accessed {access_data['resource_type']} with sensitivity level {access_data['data_sensitivity']}",
            severity=AuditSeverity.MEDIUM,
            risk_score=60,
            user_id=access_data['user_id'],
            tenant_id=access_data.get('tenant_id'),
            ip_address=access_data['ip_address'],
            indicators=access_data
        )
    
    def _matches_filters(
        self,
        event: Dict[str, Any],
        resource_type: Optional[str],
        resource_id: Optional[str],
        user_id: Optional[int],
        tenant_id: Optional[str],
        start_date: Optional[datetime],
        end_date: Optional[datetime],
        event_types: Optional[List[str]]
    ) -> bool:
        """
        Check if event matches the given filters
        """
        if resource_type and event.get('resource_type') != resource_type:
            return False
        
        if resource_id and event.get('resource_id') != resource_id:
            return False
        
        if user_id and event.get('user_id') != user_id:
            return False
        
        if tenant_id and event.get('tenant_id') != tenant_id:
            return False
        
        if event_types and event.get('event_type') not in event_types:
            return False
        
        if start_date or end_date:
            try:
                event_time = datetime.fromisoformat(event['timestamp'])
                if start_date and event_time < start_date:
                    return False
                if end_date and event_time > end_date:
                    return False
            except (ValueError, KeyError):
                return False
        
        return True


# Global instance
audit_service = AuditService()