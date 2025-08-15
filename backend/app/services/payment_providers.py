"""
Payment Providers Module

Unified interface for all payment services and providers.
Provides centralized access to Mada, STC Pay, Stripe, and other payment gateways.
"""

from typing import Dict, Any, Optional, List
from decimal import Decimal
from datetime import datetime

# Import all payment services
from .mada_service import MadaService, mada_service
from .stc_pay_service import STCPayService, stc_pay_service
from .zatca_service import ZATCAService, zatca_service
from .payment_reconciliation import (
    PaymentReconciliationService,
    FraudDetectionService, 
    fraud_detection_service,
    PaymentProvider
)

# Import existing services
try:
    from .payment_gateway import StripeService  # If it exists
except ImportError:
    class StripeService:
        """Mock Stripe service"""
        def __init__(self):
            pass


class PaymentProvidersManager:
    """
    Centralized payment providers manager
    
    Provides unified interface to all payment services and handles
    provider selection, routing, and coordination.
    """
    
    def __init__(self):
        self.providers = {
            "mada": mada_service,
            "stc_pay": stc_pay_service,
            "stripe": StripeService(),
            "zatca": zatca_service
        }
        self.fraud_service = fraud_detection_service
    
    def get_provider(self, provider_name: str) -> Any:
        """Get payment provider service by name"""
        return self.providers.get(provider_name)
    
    def get_available_providers(self) -> List[str]:
        """Get list of available payment providers"""
        return list(self.providers.keys())
    
    async def process_payment(
        self,
        provider: str,
        payment_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process payment through specified provider
        
        Args:
            provider: Payment provider name
            payment_data: Payment details
            
        Returns:
            Payment result from provider
        """
        service = self.get_provider(provider)
        if not service:
            raise ValueError(f"Unknown payment provider: {provider}")
        
        # Add fraud detection
        fraud_analysis = await self.fraud_service.analyze_transaction(
            payment_data, 
            []  # Customer history would be fetched here
        )
        
        if fraud_analysis.risk_level == "critical":
            raise Exception("Transaction blocked due to fraud risk")
        
        # Process payment based on provider
        if provider == "mada":
            from .mada_service import MadaPaymentRequest
            request = MadaPaymentRequest(**payment_data)
            return await service.process_payment(request)
        
        elif provider == "stc_pay":
            from .stc_pay_service import STCPayPaymentRequest
            request = STCPayPaymentRequest(**payment_data)
            return await service.create_payment(request)
        
        elif provider == "stripe":
            # Handle Stripe payments
            return await self._process_stripe_payment(service, payment_data)
        
        else:
            raise ValueError(f"Payment processing not implemented for {provider}")
    
    async def _process_stripe_payment(
        self, 
        service: StripeService, 
        payment_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process Stripe payment"""
        # This would implement Stripe payment processing
        # For now, return mock response
        return {
            "payment_id": "pi_stripe_mock",
            "status": "succeeded",
            "amount": payment_data["amount"],
            "currency": payment_data.get("currency", "SAR")
        }
    
    def is_saudi_provider(self, provider: str) -> bool:
        """Check if provider is Saudi-specific"""
        return provider in ["mada", "stc_pay", "zatca"]
    
    def get_supported_currencies(self, provider: str) -> List[str]:
        """Get supported currencies for provider"""
        if self.is_saudi_provider(provider):
            return ["SAR"]
        elif provider == "stripe":
            return ["SAR", "USD", "EUR", "GBP"]
        else:
            return ["SAR"]
    
    def get_provider_fees(self, provider: str, amount: Decimal) -> Decimal:
        """Calculate provider fees for amount"""
        # This would implement actual fee calculation
        fee_rates = {
            "mada": Decimal("0.025"),      # 2.5%
            "stc_pay": Decimal("0.02"),    # 2.0%
            "stripe": Decimal("0.029"),    # 2.9% + 0.30 SAR
            "zatca": Decimal("0.00"),      # No fee for tax service
        }
        
        rate = fee_rates.get(provider, Decimal("0.03"))
        base_fee = amount * rate
        
        # Add fixed fee for some providers
        if provider == "stripe":
            base_fee += Decimal("0.30")
        
        return base_fee


# Global instance
payment_providers = PaymentProvidersManager()


# Export all services for direct access
__all__ = [
    'MadaService',
    'mada_service',
    'STCPayService', 
    'stc_pay_service',
    'ZATCAService',
    'zatca_service',
    'PaymentReconciliationService',
    'FraudDetectionService',
    'fraud_detection_service',
    'PaymentProvidersManager',
    'payment_providers',
    'PaymentProvider'
]