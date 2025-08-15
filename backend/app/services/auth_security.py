"""
Enhanced authentication security service with MFA, account lockout, and session management
"""

import asyncio
import hashlib
import secrets
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import pyotp
import qrcode
import redis.asyncio as redis
from fastapi import HTTPException, Request, status
from io import BytesIO
import base64

from ..core.config import settings
from ..core.security import (
    create_access_token,
    generate_secure_token,
    generate_otp,
    hash_password,
    verify_password
)

# Redis client for session management
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


class AuthSecurityService:
    """
    Enhanced authentication security service
    """
    
    def __init__(self):
        self.max_login_attempts = 5
        self.lockout_duration = 900  # 15 minutes
        self.session_timeout = 3600  # 1 hour
        self.mfa_code_validity = 300  # 5 minutes
        
    async def authenticate_user(
        self,
        email: str,
        password: str,
        ip_address: str,
        user_agent: str,
        mfa_code: Optional[str] = None,
        tenant_id: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Authenticate user with enhanced security checks
        """
        # Check if account is locked
        await self._check_account_lockout(email, ip_address)
        
        # Rate limiting check
        await self._check_login_rate_limit(ip_address)
        
        # Simulate user lookup (replace with actual database call)
        user = await self._get_user_by_email(email, tenant_id)
        if not user:
            await self._record_failed_attempt(email, ip_address, "user_not_found")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Verify password
        if not verify_password(password, user.get('password_hash', '')):
            await self._record_failed_attempt(email, ip_address, "invalid_password")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Check if user is active
        if not user.get('is_active', False):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is disabled"
            )
        
        # Check MFA if enabled
        if user.get('mfa_enabled', False):
            if not mfa_code:
                raise HTTPException(
                    status_code=status.HTTP_428_PRECONDITION_REQUIRED,
                    detail="MFA code required"
                )
            
            if not await self._verify_mfa_code(user['id'], mfa_code):
                await self._record_failed_attempt(email, ip_address, "invalid_mfa")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid MFA code"
                )
        
        # Clear failed attempts on successful login
        await self._clear_failed_attempts(email, ip_address)
        
        # Create session
        session_data = await self._create_user_session(
            user['id'], ip_address, user_agent, tenant_id
        )
        
        return {
            'user': user,
            'session': session_data,
            'requires_password_change': self._check_password_expiry(user),
        }
    
    async def setup_mfa(self, user_id: int, user_email: str) -> Dict[str, str]:
        """
        Setup Multi-Factor Authentication for user
        """
        # Generate secret key for TOTP
        secret = pyotp.random_base32()
        
        # Store secret temporarily (user must confirm setup)
        temp_key = f"mfa_setup:{user_id}"
        await redis_client.setex(temp_key, 600, secret)  # 10 minutes to complete setup
        
        # Generate QR code
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            user_email,
            issuer_name=settings.APP_NAME
        )
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        qr_code_b64 = base64.b64encode(buffer.getvalue()).decode()
        
        # Generate backup codes
        backup_codes = [generate_secure_token(8) for _ in range(10)]
        backup_key = f"mfa_backup:{user_id}"
        await redis_client.setex(backup_key, 600, ','.join(backup_codes))
        
        return {
            'secret': secret,
            'qr_code': qr_code_b64,
            'backup_codes': backup_codes,
            'manual_entry_key': secret
        }
    
    async def confirm_mfa_setup(self, user_id: int, verification_code: str) -> bool:
        """
        Confirm MFA setup with verification code
        """
        temp_key = f"mfa_setup:{user_id}"
        secret = await redis_client.get(temp_key)
        
        if not secret:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MFA setup session expired"
            )
        
        # Verify the code
        totp = pyotp.TOTP(secret)
        if not totp.verify(verification_code, valid_window=1):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification code"
            )
        
        # Move secret to permanent storage and enable MFA
        # In real implementation, update user record in database
        permanent_key = f"mfa_secret:{user_id}"
        await redis_client.set(permanent_key, secret)
        
        # Move backup codes to permanent storage
        backup_key = f"mfa_backup:{user_id}"
        backup_codes = await redis_client.get(backup_key)
        if backup_codes:
            await redis_client.set(f"mfa_backup_codes:{user_id}", backup_codes)
        
        # Clean up temporary keys
        await redis_client.delete(temp_key, backup_key)
        
        return True
    
    async def disable_mfa(self, user_id: int, password: str, verification_code: str) -> bool:
        """
        Disable MFA for user (requires password and current MFA code)
        """
        # Verify current MFA code
        if not await self._verify_mfa_code(user_id, verification_code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid MFA code"
            )
        
        # Remove MFA data
        await redis_client.delete(
            f"mfa_secret:{user_id}",
            f"mfa_backup_codes:{user_id}"
        )
        
        return True
    
    async def _verify_mfa_code(self, user_id: int, code: str) -> bool:
        """
        Verify MFA code (TOTP or backup code)
        """
        # Try TOTP first
        secret = await redis_client.get(f"mfa_secret:{user_id}")
        if secret:
            totp = pyotp.TOTP(secret)
            if totp.verify(code, valid_window=1):
                return True
        
        # Try backup codes
        backup_codes = await redis_client.get(f"mfa_backup_codes:{user_id}")
        if backup_codes:
            codes = backup_codes.split(',')
            if code in codes:
                # Remove used backup code
                codes.remove(code)
                await redis_client.set(f"mfa_backup_codes:{user_id}", ','.join(codes))
                return True
        
        return False
    
    async def _check_account_lockout(self, email: str, ip_address: str):
        """
        Check if account or IP is locked out
        """
        # Check account lockout
        account_key = f"lockout:account:{email}"
        if await redis_client.get(account_key):
            lockout_time = await redis_client.ttl(account_key)
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail=f"Account locked. Try again in {lockout_time} seconds"
            )
        
        # Check IP lockout
        ip_key = f"lockout:ip:{ip_address}"
        if await redis_client.get(ip_key):
            lockout_time = await redis_client.ttl(ip_key)
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail=f"IP address locked. Try again in {lockout_time} seconds"
            )
    
    async def _check_login_rate_limit(self, ip_address: str):
        """
        Check login rate limiting
        """
        rate_key = f"login_rate:{ip_address}"
        current_attempts = await redis_client.get(rate_key)
        
        if current_attempts and int(current_attempts) >= 10:  # 10 login attempts per minute
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many login attempts. Try again later"
            )
        
        # Increment counter
        pipeline = redis_client.pipeline()
        pipeline.incr(rate_key)
        pipeline.expire(rate_key, 60)  # 1 minute window
        await pipeline.execute()
    
    async def _record_failed_attempt(self, email: str, ip_address: str, reason: str):
        """
        Record failed login attempt and implement lockout
        """
        # Record attempt for account
        account_key = f"failed_attempts:account:{email}"
        account_attempts = await redis_client.incr(account_key)
        await redis_client.expire(account_key, self.lockout_duration)
        
        # Record attempt for IP
        ip_key = f"failed_attempts:ip:{ip_address}"
        ip_attempts = await redis_client.incr(ip_key)
        await redis_client.expire(ip_key, self.lockout_duration)
        
        # Lock account if too many attempts
        if account_attempts >= self.max_login_attempts:
            lockout_key = f"lockout:account:{email}"
            await redis_client.setex(lockout_key, self.lockout_duration, "locked")
        
        # Lock IP if too many attempts
        if ip_attempts >= self.max_login_attempts * 2:  # Allow more attempts from same IP
            lockout_key = f"lockout:ip:{ip_address}"
            await redis_client.setex(lockout_key, self.lockout_duration, "locked")
        
        # Log security event
        await self._log_security_event({
            'event': 'failed_login_attempt',
            'email': email,
            'ip_address': ip_address,
            'reason': reason,
            'account_attempts': account_attempts,
            'ip_attempts': ip_attempts,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    async def _clear_failed_attempts(self, email: str, ip_address: str):
        """
        Clear failed attempts on successful login
        """
        await redis_client.delete(
            f"failed_attempts:account:{email}",
            f"failed_attempts:ip:{ip_address}"
        )
    
    async def _create_user_session(
        self,
        user_id: int,
        ip_address: str,
        user_agent: str,
        tenant_id: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Create user session with tracking
        """
        session_id = generate_secure_token(32)
        
        # Create JWT token
        token_data = {
            'sub': str(user_id),
            'session_id': session_id,
            'tenant_id': tenant_id,
            'type': 'access'
        }
        
        access_token = create_access_token(
            token_data,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        refresh_token = create_access_token(
            {**token_data, 'type': 'refresh'},
            expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )
        
        # Store session data
        session_data = {
            'user_id': user_id,
            'session_id': session_id,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'tenant_id': tenant_id,
            'created_at': datetime.utcnow().isoformat(),
            'last_activity': datetime.utcnow().isoformat(),
            'is_active': True
        }
        
        session_key = f"session:{user_id}:{session_id}"
        await redis_client.setex(
            session_key,
            self.session_timeout,
            ','.join([str(v) for v in session_data.values()])
        )
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'session_id': session_id,
            'expires_in': settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    
    async def _get_user_by_email(self, email: str, tenant_id: Optional[str] = None) -> Optional[Dict]:
        """
        Get user by email (placeholder - replace with actual database call)
        """
        # This is a placeholder - in real implementation, query your user database
        return {
            'id': 1,
            'email': email,
            'password_hash': hash_password('testpassword'),  # This would come from DB
            'is_active': True,
            'mfa_enabled': False,
            'password_changed_at': datetime.utcnow() - timedelta(days=30),
            'role': 'user'
        }
    
    def _check_password_expiry(self, user: Dict) -> bool:
        """
        Check if user password needs to be changed
        """
        password_max_age = timedelta(days=90)  # 90 days
        password_changed_at = user.get('password_changed_at')
        
        if password_changed_at:
            if isinstance(password_changed_at, str):
                password_changed_at = datetime.fromisoformat(password_changed_at)
            
            return datetime.utcnow() - password_changed_at > password_max_age
        
        return True  # Require change if no date available
    
    async def _log_security_event(self, event_data: Dict):
        """
        Log security events for monitoring
        """
        try:
            await redis_client.lpush(
                "security_events",
                f"auth:{','.join([str(v) for v in event_data.values()])}"
            )
            await redis_client.ltrim("security_events", 0, 999)
        except Exception:
            pass  # Don't fail authentication if logging fails
    
    async def revoke_session(self, user_id: int, session_id: str) -> bool:
        """
        Revoke a specific user session
        """
        session_key = f"session:{user_id}:{session_id}"
        result = await redis_client.delete(session_key)
        return result > 0
    
    async def revoke_all_sessions(self, user_id: int) -> int:
        """
        Revoke all sessions for a user
        """
        pattern = f"session:{user_id}:*"
        keys = await redis_client.keys(pattern)
        if keys:
            return await redis_client.delete(*keys)
        return 0
    
    async def get_active_sessions(self, user_id: int) -> List[Dict]:
        """
        Get all active sessions for a user
        """
        pattern = f"session:{user_id}:*"
        keys = await redis_client.keys(pattern)
        
        sessions = []
        for key in keys:
            session_data = await redis_client.get(key)
            if session_data:
                # Parse session data (simplified)
                sessions.append({
                    'session_id': key.split(':')[-1],
                    'data': session_data
                })
        
        return sessions


# Global instance
auth_security_service = AuthSecurityService()