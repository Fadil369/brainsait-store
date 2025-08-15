"""
Webhook Security Service for payment providers
Enhanced security, validation, and fraud detection
"""

import hashlib
import hmac
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID

import httpx
from fastapi import HTTPException, Request

from app.core.config import settings

logger = logging.getLogger(__name__)


class WebhookSecurityService:
    """Enhanced webhook security and validation"""

    def __init__(self):
        self.rate_limit_window = 300  # 5 minutes
        self.max_requests_per_window = 100
        self.webhook_attempts = {}  # Store in Redis in production
        
    async def verify_webhook_signature(
        self, 
        provider: str, 
        payload: Dict[str, Any], 
        signature: str,
        timestamp: Optional[str] = None
    ) -> bool:
        """Verify webhook signature based on provider"""
        try:
            if provider == "mada":
                return await self._verify_mada_signature(payload, signature, timestamp)
            elif provider == "stc_pay":
                return await self._verify_stc_signature(payload, signature, timestamp)
            elif provider == "stripe":
                return await self._verify_stripe_signature(payload, signature, timestamp)
            else:
                logger.warning(f"Unknown webhook provider: {provider}")
                return False
        except Exception as e:
            logger.error(f"Webhook signature verification failed for {provider}: {e}")
            return False

    async def _verify_mada_signature(
        self, 
        payload: Dict[str, Any], 
        signature: str,
        timestamp: Optional[str] = None
    ) -> bool:
        """Verify Mada webhook signature with enhanced security"""
        if not settings.MADA_WEBHOOK_SECRET:
            logger.warning("Mada webhook secret not configured")
            return False

        # Check timestamp to prevent replay attacks
        if timestamp and not self._is_timestamp_valid(timestamp):
            logger.warning("Mada webhook timestamp too old")
            return False

        # Create signature payload
        signature_payload = json.dumps(payload, separators=(',', ':'), sort_keys=True)
        
        if timestamp:
            signature_payload = f"{timestamp}.{signature_payload}"

        expected_signature = hmac.new(
            settings.MADA_WEBHOOK_SECRET.encode(),
            signature_payload.encode(),
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(signature, expected_signature)

    async def _verify_stc_signature(
        self, 
        payload: Dict[str, Any], 
        signature: str,
        timestamp: Optional[str] = None
    ) -> bool:
        """Verify STC Pay webhook signature with enhanced security"""
        if not settings.STC_PAY_WEBHOOK_SECRET:
            logger.warning("STC Pay webhook secret not configured")
            return False

        # Check timestamp
        if timestamp and not self._is_timestamp_valid(timestamp):
            logger.warning("STC Pay webhook timestamp too old")
            return False

        # Create signature payload
        signature_payload = json.dumps(payload, separators=(',', ':'), sort_keys=True)
        
        if timestamp:
            signature_payload = f"{timestamp}.{signature_payload}"

        expected_signature = hmac.new(
            settings.STC_PAY_WEBHOOK_SECRET.encode(),
            signature_payload.encode(),
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(signature, expected_signature)

    async def _verify_stripe_signature(
        self, 
        payload: Dict[str, Any], 
        signature: str,
        timestamp: Optional[str] = None
    ) -> bool:
        """Verify Stripe webhook signature"""
        if not settings.STRIPE_WEBHOOK_SECRET:
            logger.warning("Stripe webhook secret not configured")
            return False

        # Stripe uses a different signature format
        # This is a simplified implementation
        signature_payload = json.dumps(payload, separators=(',', ':'), sort_keys=True)
        
        expected_signature = hmac.new(
            settings.STRIPE_WEBHOOK_SECRET.encode(),
            signature_payload.encode(),
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(signature, expected_signature)

    def _is_timestamp_valid(self, timestamp: str, tolerance: int = 300) -> bool:
        """Check if timestamp is within tolerance (default 5 minutes)"""
        try:
            webhook_time = datetime.fromtimestamp(int(timestamp))
            current_time = datetime.utcnow()
            time_diff = abs((current_time - webhook_time).total_seconds())
            return time_diff <= tolerance
        except (ValueError, TypeError):
            return False

    async def rate_limit_webhook(self, request: Request, provider: str) -> bool:
        """Rate limit webhook requests"""
        client_ip = request.client.host
        key = f"{provider}:{client_ip}"
        
        current_time = time.time()
        window_start = current_time - self.rate_limit_window
        
        # Clean old entries
        if key in self.webhook_attempts:
            self.webhook_attempts[key] = [
                timestamp for timestamp in self.webhook_attempts[key]
                if timestamp > window_start
            ]
        else:
            self.webhook_attempts[key] = []

        # Check if rate limit exceeded
        if len(self.webhook_attempts[key]) >= self.max_requests_per_window:
            logger.warning(f"Rate limit exceeded for {provider} webhook from {client_ip}")
            return False

        # Add current request
        self.webhook_attempts[key].append(current_time)
        return True

    async def log_webhook_attempt(
        self, 
        provider: str, 
        request: Request,
        payload: Dict[str, Any],
        success: bool,
        error: Optional[str] = None
    ):
        """Log webhook attempt for monitoring and debugging"""
        log_data = {
            "provider": provider,
            "client_ip": request.client.host,
            "user_agent": request.headers.get("user-agent"),
            "timestamp": datetime.utcnow().isoformat(),
            "success": success,
            "payload_size": len(json.dumps(payload)),
            "error": error
        }
        
        if success:
            logger.info(f"Webhook processed successfully: {log_data}")
        else:
            logger.error(f"Webhook failed: {log_data}")


class FraudDetectionService:
    """Basic fraud detection patterns for payments"""

    def __init__(self):
        self.suspicious_patterns = {}
        self.velocity_limits = {
            "per_minute": 5,
            "per_hour": 50,
            "per_day": 500
        }

    async def analyze_payment(
        self, 
        payment_data: Dict[str, Any],
        user_id: Optional[UUID] = None,
        ip_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze payment for potential fraud"""
        fraud_score = 0
        flags = []

        # Check amount patterns
        amount = payment_data.get("amount", 0)
        if self._is_suspicious_amount(amount):
            fraud_score += 20
            flags.append("suspicious_amount")

        # Check velocity (if user_id provided)
        if user_id:
            velocity_flags = await self._check_velocity(user_id, amount)
            fraud_score += len(velocity_flags) * 15
            flags.extend(velocity_flags)

        # Check IP patterns (if provided)
        if ip_address:
            ip_flags = await self._check_ip_patterns(ip_address)
            fraud_score += len(ip_flags) * 10
            flags.extend(ip_flags)

        # Check time patterns
        time_flags = self._check_time_patterns()
        fraud_score += len(time_flags) * 5
        flags.extend(time_flags)

        # Determine risk level
        if fraud_score >= 50:
            risk_level = "high"
        elif fraud_score >= 25:
            risk_level = "medium"
        else:
            risk_level = "low"

        return {
            "fraud_score": fraud_score,
            "risk_level": risk_level,
            "flags": flags,
            "requires_review": fraud_score >= 40,
            "block_payment": fraud_score >= 70
        }

    def _is_suspicious_amount(self, amount: float) -> bool:
        """Check if amount follows suspicious patterns"""
        # Round numbers that are unusually high
        if amount >= 10000 and amount % 1000 == 0:
            return True
        
        # Very small amounts (potential testing)
        if amount <= 1:
            return True
            
        # Extremely high amounts
        if amount >= 50000:
            return True
            
        return False

    async def _check_velocity(self, user_id: UUID, amount: float) -> List[str]:
        """Check payment velocity patterns"""
        flags = []
        
        # This would typically check against a database
        # For now, implementing basic logic
        
        # Mock velocity check - in production, query actual payment history
        recent_payments = await self._get_recent_payments(user_id)
        
        if len(recent_payments.get("last_minute", [])) > self.velocity_limits["per_minute"]:
            flags.append("high_velocity_minute")
            
        if len(recent_payments.get("last_hour", [])) > self.velocity_limits["per_hour"]:
            flags.append("high_velocity_hour")
            
        return flags

    async def _get_recent_payments(self, user_id: UUID) -> Dict[str, List]:
        """Get recent payments for velocity check"""
        # This is a mock implementation
        # In production, this would query the database
        return {
            "last_minute": [],
            "last_hour": [],
            "last_day": []
        }

    async def _check_ip_patterns(self, ip_address: str) -> List[str]:
        """Check IP address patterns"""
        flags = []
        
        # Check if IP is from known problematic ranges
        # This would typically use a fraud detection service
        
        # Basic checks
        if ip_address.startswith("127.") or ip_address.startswith("192.168."):
            flags.append("local_ip")
            
        # In production, check against fraud databases
        # if await self._is_blacklisted_ip(ip_address):
        #     flags.append("blacklisted_ip")
            
        return flags

    def _check_time_patterns(self) -> List[str]:
        """Check timing patterns"""
        flags = []
        current_hour = datetime.now().hour
        
        # Payments at unusual hours (late night) might be suspicious
        if current_hour < 6 or current_hour > 23:
            flags.append("unusual_hour")
            
        return flags


class PaymentReconciliationService:
    """Service for reconciling payments across providers"""

    def __init__(self):
        self.reconciliation_window = timedelta(hours=24)

    async def reconcile_payments(
        self, 
        start_date: datetime, 
        end_date: datetime,
        provider: Optional[str] = None
    ) -> Dict[str, Any]:
        """Reconcile payments for a given period"""
        try:
            reconciliation_data = {
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "providers": {},
                "discrepancies": [],
                "summary": {
                    "total_payments": 0,
                    "total_amount": 0,
                    "matched_payments": 0,
                    "unmatched_payments": 0
                }
            }

            providers = [provider] if provider else ["stripe", "mada", "stc_pay"]

            for prov in providers:
                provider_data = await self._reconcile_provider(prov, start_date, end_date)
                reconciliation_data["providers"][prov] = provider_data
                
                # Update summary
                reconciliation_data["summary"]["total_payments"] += provider_data["payment_count"]
                reconciliation_data["summary"]["total_amount"] += provider_data["total_amount"]

            return reconciliation_data

        except Exception as e:
            logger.error(f"Payment reconciliation failed: {e}")
            raise

    async def _reconcile_provider(
        self, 
        provider: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
        """Reconcile payments for a specific provider"""
        # This would typically:
        # 1. Fetch payments from our database
        # 2. Fetch payments from provider's API
        # 3. Match transactions
        # 4. Identify discrepancies

        return {
            "provider": provider,
            "payment_count": 0,
            "total_amount": 0.0,
            "matched_count": 0,
            "unmatched_count": 0,
            "discrepancies": []
        }

    async def generate_reconciliation_report(
        self, 
        reconciliation_data: Dict[str, Any]
    ) -> str:
        """Generate a reconciliation report"""
        # This would generate a detailed report
        # For now, return a simple summary
        return f"Reconciliation Report for {reconciliation_data['period']['start']} to {reconciliation_data['period']['end']}"


# Global instances
webhook_security = WebhookSecurityService()
fraud_detection = FraudDetectionService()
payment_reconciliation = PaymentReconciliationService()