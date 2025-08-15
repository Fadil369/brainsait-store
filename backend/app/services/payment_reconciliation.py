"""
Payment Reconciliation Service

Handles payment reconciliation across multiple providers, transaction matching,
and payment reporting for the BrainSAIT Store platform.
"""

import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum

from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class ReconciliationStatus(str, Enum):
    """Reconciliation status values"""
    MATCHED = "matched"
    UNMATCHED = "unmatched"
    DISPUTED = "disputed"
    PENDING = "pending"
    FAILED = "failed"


class PaymentProvider(str, Enum):
    """Supported payment providers"""
    STRIPE = "stripe"
    MADA = "mada"
    STC_PAY = "stc_pay"
    PAYPAL = "paypal"
    APPLE_PAY = "apple_pay"


class TransactionRecord(BaseModel):
    """Payment transaction record"""
    id: str
    provider: PaymentProvider
    transaction_id: str
    order_id: str
    amount: Decimal
    currency: str = "SAR"
    status: str
    created_at: datetime
    settled_at: Optional[datetime] = None
    fees: Optional[Decimal] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ReconciliationRecord(BaseModel):
    """Reconciliation record"""
    id: str
    provider: PaymentProvider
    transaction_id: str
    order_id: str
    internal_amount: Decimal
    provider_amount: Decimal
    difference: Decimal
    status: ReconciliationStatus
    reconciled_at: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ReconciliationSummary(BaseModel):
    """Reconciliation summary report"""
    period_start: datetime
    period_end: datetime
    total_transactions: int
    matched_transactions: int
    unmatched_transactions: int
    disputed_transactions: int
    total_amount_internal: Decimal
    total_amount_provider: Decimal
    total_difference: Decimal
    match_rate: float
    by_provider: Dict[str, Dict[str, Any]]


class FraudIndicator(BaseModel):
    """Fraud detection indicator"""
    type: str
    severity: str  # low, medium, high, critical
    score: float  # 0-100
    description: str
    detected_at: datetime


class FraudAnalysis(BaseModel):
    """Fraud analysis result"""
    transaction_id: str
    risk_score: float  # 0-100
    risk_level: str  # low, medium, high, critical
    indicators: List[FraudIndicator]
    recommended_action: str
    analyzed_at: datetime


class PaymentReconciliationService:
    """
    Payment Reconciliation Service
    
    Handles reconciliation of payments across different providers,
    transaction matching, and discrepancy reporting.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def reconcile_transactions(
        self, 
        provider: PaymentProvider,
        start_date: datetime,
        end_date: datetime
    ) -> List[ReconciliationRecord]:
        """
        Reconcile transactions for a specific provider and date range
        
        Args:
            provider: Payment provider to reconcile
            start_date: Start date for reconciliation
            end_date: End date for reconciliation
            
        Returns:
            List of reconciliation records
        """
        logger.info(f"Starting reconciliation for {provider} from {start_date} to {end_date}")
        
        try:
            # Fetch internal transactions
            internal_transactions = await self._get_internal_transactions(
                provider, start_date, end_date
            )
            
            # Fetch provider transactions
            provider_transactions = await self._get_provider_transactions(
                provider, start_date, end_date
            )
            
            # Match transactions
            reconciliation_records = []
            
            for internal_tx in internal_transactions:
                provider_tx = self._find_matching_transaction(
                    internal_tx, provider_transactions
                )
                
                if provider_tx:
                    # Calculate difference
                    difference = abs(internal_tx.amount - provider_tx.amount)
                    
                    # Determine status
                    if difference == 0:
                        status = ReconciliationStatus.MATCHED
                    elif difference <= Decimal('0.01'):  # Allow 1 halala tolerance
                        status = ReconciliationStatus.MATCHED
                    else:
                        status = ReconciliationStatus.DISPUTED
                    
                    record = ReconciliationRecord(
                        id=f"rec_{internal_tx.id}_{provider_tx.id}",
                        provider=provider,
                        transaction_id=internal_tx.transaction_id,
                        order_id=internal_tx.order_id,
                        internal_amount=internal_tx.amount,
                        provider_amount=provider_tx.amount,
                        difference=difference,
                        status=status,
                        reconciled_at=datetime.utcnow() if status == ReconciliationStatus.MATCHED else None,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    
                    # Remove matched transaction from provider list
                    provider_transactions.remove(provider_tx)
                else:
                    # Unmatched internal transaction
                    record = ReconciliationRecord(
                        id=f"rec_{internal_tx.id}_unmatched",
                        provider=provider,
                        transaction_id=internal_tx.transaction_id,
                        order_id=internal_tx.order_id,
                        internal_amount=internal_tx.amount,
                        provider_amount=Decimal('0'),
                        difference=internal_tx.amount,
                        status=ReconciliationStatus.UNMATCHED,
                        reconciled_at=None,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                
                reconciliation_records.append(record)
            
            # Add remaining unmatched provider transactions
            for provider_tx in provider_transactions:
                record = ReconciliationRecord(
                    id=f"rec_provider_{provider_tx.id}_unmatched",
                    provider=provider,
                    transaction_id=provider_tx.transaction_id,
                    order_id=provider_tx.order_id,
                    internal_amount=Decimal('0'),
                    provider_amount=provider_tx.amount,
                    difference=provider_tx.amount,
                    status=ReconciliationStatus.UNMATCHED,
                    reconciled_at=None,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                reconciliation_records.append(record)
            
            # Save reconciliation records to database
            await self._save_reconciliation_records(reconciliation_records)
            
            logger.info(f"Reconciliation completed: {len(reconciliation_records)} records processed")
            return reconciliation_records
            
        except Exception as e:
            logger.error(f"Reconciliation failed: {e}")
            raise

    async def generate_reconciliation_summary(
        self,
        start_date: datetime,
        end_date: datetime,
        provider: Optional[PaymentProvider] = None
    ) -> ReconciliationSummary:
        """
        Generate reconciliation summary report
        
        Args:
            start_date: Report start date
            end_date: Report end date
            provider: Optional specific provider filter
            
        Returns:
            ReconciliationSummary with aggregated data
        """
        logger.info(f"Generating reconciliation summary from {start_date} to {end_date}")
        
        try:
            # Fetch reconciliation records
            records = await self._get_reconciliation_records(start_date, end_date, provider)
            
            # Calculate summary statistics
            total_transactions = len(records)
            matched = len([r for r in records if r.status == ReconciliationStatus.MATCHED])
            unmatched = len([r for r in records if r.status == ReconciliationStatus.UNMATCHED])
            disputed = len([r for r in records if r.status == ReconciliationStatus.DISPUTED])
            
            total_internal = sum(r.internal_amount for r in records)
            total_provider = sum(r.provider_amount for r in records)
            total_difference = sum(abs(r.difference) for r in records)
            
            match_rate = (matched / total_transactions * 100) if total_transactions > 0 else 0
            
            # Group by provider
            by_provider = {}
            for provider_type in PaymentProvider:
                provider_records = [r for r in records if r.provider == provider_type]
                if provider_records:
                    by_provider[provider_type.value] = {
                        "total_transactions": len(provider_records),
                        "matched": len([r for r in provider_records if r.status == ReconciliationStatus.MATCHED]),
                        "unmatched": len([r for r in provider_records if r.status == ReconciliationStatus.UNMATCHED]),
                        "disputed": len([r for r in provider_records if r.status == ReconciliationStatus.DISPUTED]),
                        "total_amount": sum(r.internal_amount for r in provider_records),
                        "total_difference": sum(abs(r.difference) for r in provider_records),
                        "match_rate": (len([r for r in provider_records if r.status == ReconciliationStatus.MATCHED]) / len(provider_records) * 100) if provider_records else 0
                    }
            
            return ReconciliationSummary(
                period_start=start_date,
                period_end=end_date,
                total_transactions=total_transactions,
                matched_transactions=matched,
                unmatched_transactions=unmatched,
                disputed_transactions=disputed,
                total_amount_internal=total_internal,
                total_amount_provider=total_provider,
                total_difference=total_difference,
                match_rate=match_rate,
                by_provider=by_provider
            )
            
        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            raise

    def _find_matching_transaction(
        self, 
        internal_tx: TransactionRecord,
        provider_transactions: List[TransactionRecord]
    ) -> Optional[TransactionRecord]:
        """Find matching transaction from provider list"""
        
        # Try exact match by transaction ID
        for tx in provider_transactions:
            if tx.transaction_id == internal_tx.transaction_id:
                return tx
        
        # Try match by order ID and amount
        for tx in provider_transactions:
            if (tx.order_id == internal_tx.order_id and 
                abs(tx.amount - internal_tx.amount) <= Decimal('0.01')):
                return tx
        
        # Try match by amount and date (within 1 hour)
        for tx in provider_transactions:
            time_diff = abs((tx.created_at - internal_tx.created_at).total_seconds())
            if (abs(tx.amount - internal_tx.amount) <= Decimal('0.01') and 
                time_diff <= 3600):  # 1 hour tolerance
                return tx
        
        return None

    async def _get_internal_transactions(
        self,
        provider: PaymentProvider,
        start_date: datetime,
        end_date: datetime
    ) -> List[TransactionRecord]:
        """Fetch internal transactions from database"""
        # This would query your internal transactions table
        # For now, return mock data
        return [
            TransactionRecord(
                id="internal_001",
                provider=provider,
                transaction_id=f"{provider}_tx_123456",
                order_id="ORD-2023-001",
                amount=Decimal("150.00"),
                currency="SAR",
                status="completed",
                created_at=datetime.utcnow() - timedelta(days=1),
                settled_at=datetime.utcnow() - timedelta(hours=2),
                metadata={}
            )
        ]

    async def _get_provider_transactions(
        self,
        provider: PaymentProvider,
        start_date: datetime,
        end_date: datetime
    ) -> List[TransactionRecord]:
        """Fetch transactions from payment provider"""
        # This would fetch from provider APIs
        # For now, return mock data
        return [
            TransactionRecord(
                id="provider_001",
                provider=provider,
                transaction_id=f"{provider}_tx_123456",
                order_id="ORD-2023-001",
                amount=Decimal("150.00"),
                currency="SAR",
                status="settled",
                created_at=datetime.utcnow() - timedelta(days=1),
                settled_at=datetime.utcnow() - timedelta(hours=2),
                fees=Decimal("4.50"),
                metadata={}
            )
        ]

    async def _get_reconciliation_records(
        self,
        start_date: datetime,
        end_date: datetime,
        provider: Optional[PaymentProvider] = None
    ) -> List[ReconciliationRecord]:
        """Fetch reconciliation records from database"""
        # This would query reconciliation records table
        # For now, return mock data
        return []

    async def _save_reconciliation_records(
        self, 
        records: List[ReconciliationRecord]
    ) -> None:
        """Save reconciliation records to database"""
        # This would save to database
        logger.info(f"Saving {len(records)} reconciliation records")


class FraudDetectionService:
    """
    Fraud Detection Service
    
    Implements basic fraud detection patterns for payment transactions.
    """

    def __init__(self):
        self.risk_rules = self._initialize_risk_rules()

    def _initialize_risk_rules(self) -> Dict[str, Any]:
        """Initialize fraud detection rules"""
        return {
            "velocity_rules": {
                "max_transactions_per_hour": 10,
                "max_transactions_per_day": 50,
                "max_amount_per_hour": Decimal("5000.00"),
                "max_amount_per_day": Decimal("20000.00")
            },
            "amount_rules": {
                "high_amount_threshold": Decimal("10000.00"),
                "suspicious_amounts": [
                    Decimal("9999.99"),
                    Decimal("999.99"),
                    Decimal("99.99")
                ]
            },
            "geographic_rules": {
                "restricted_countries": ["XX"],  # Add restricted country codes
                "high_risk_regions": ["XX"]
            },
            "behavioral_rules": {
                "new_customer_limit": Decimal("1000.00"),
                "failed_attempts_threshold": 3,
                "card_testing_pattern": 5  # Multiple small transactions
            }
        }

    async def analyze_transaction(
        self,
        transaction_data: Dict[str, Any],
        customer_history: List[Dict[str, Any]]
    ) -> FraudAnalysis:
        """
        Analyze transaction for fraud indicators
        
        Args:
            transaction_data: Current transaction details
            customer_history: Customer's transaction history
            
        Returns:
            FraudAnalysis with risk assessment
        """
        logger.info(f"Analyzing transaction: {transaction_data.get('transaction_id')}")
        
        indicators = []
        risk_score = 0
        
        # Check velocity rules
        velocity_indicators = self._check_velocity_rules(transaction_data, customer_history)
        indicators.extend(velocity_indicators)
        risk_score += sum(i.score for i in velocity_indicators)
        
        # Check amount rules
        amount_indicators = self._check_amount_rules(transaction_data)
        indicators.extend(amount_indicators)
        risk_score += sum(i.score for i in amount_indicators)
        
        # Check geographic rules
        geo_indicators = self._check_geographic_rules(transaction_data)
        indicators.extend(geo_indicators)
        risk_score += sum(i.score for i in geo_indicators)
        
        # Check behavioral patterns
        behavioral_indicators = self._check_behavioral_patterns(transaction_data, customer_history)
        indicators.extend(behavioral_indicators)
        risk_score += sum(i.score for i in behavioral_indicators)
        
        # Determine risk level and recommendation
        risk_level, recommendation = self._calculate_risk_level(risk_score)
        
        return FraudAnalysis(
            transaction_id=transaction_data["transaction_id"],
            risk_score=min(risk_score, 100),  # Cap at 100
            risk_level=risk_level,
            indicators=indicators,
            recommended_action=recommendation,
            analyzed_at=datetime.utcnow()
        )

    def _check_velocity_rules(
        self, 
        transaction_data: Dict[str, Any],
        customer_history: List[Dict[str, Any]]
    ) -> List[FraudIndicator]:
        """Check transaction velocity rules"""
        indicators = []
        now = datetime.utcnow()
        one_hour_ago = now - timedelta(hours=1)
        one_day_ago = now - timedelta(days=1)
        
        # Recent transactions
        recent_hour = [tx for tx in customer_history if tx["created_at"] >= one_hour_ago]
        recent_day = [tx for tx in customer_history if tx["created_at"] >= one_day_ago]
        
        # Check transaction count
        if len(recent_hour) > self.risk_rules["velocity_rules"]["max_transactions_per_hour"]:
            indicators.append(FraudIndicator(
                type="velocity_count_hour",
                severity="high",
                score=30,
                description=f"Too many transactions in past hour: {len(recent_hour)}",
                detected_at=now
            ))
        
        if len(recent_day) > self.risk_rules["velocity_rules"]["max_transactions_per_day"]:
            indicators.append(FraudIndicator(
                type="velocity_count_day",
                severity="medium",
                score=20,
                description=f"High transaction count in past day: {len(recent_day)}",
                detected_at=now
            ))
        
        # Check amount velocity
        hour_amount = sum(Decimal(str(tx["amount"])) for tx in recent_hour)
        day_amount = sum(Decimal(str(tx["amount"])) for tx in recent_day)
        
        if hour_amount > self.risk_rules["velocity_rules"]["max_amount_per_hour"]:
            indicators.append(FraudIndicator(
                type="velocity_amount_hour",
                severity="high",
                score=25,
                description=f"High transaction volume in past hour: {hour_amount} SAR",
                detected_at=now
            ))
        
        if day_amount > self.risk_rules["velocity_rules"]["max_amount_per_day"]:
            indicators.append(FraudIndicator(
                type="velocity_amount_day",
                severity="medium",
                score=15,
                description=f"High transaction volume in past day: {day_amount} SAR",
                detected_at=now
            ))
        
        return indicators

    def _check_amount_rules(self, transaction_data: Dict[str, Any]) -> List[FraudIndicator]:
        """Check transaction amount rules"""
        indicators = []
        amount = Decimal(str(transaction_data["amount"]))
        
        # High amount check
        if amount > self.risk_rules["amount_rules"]["high_amount_threshold"]:
            indicators.append(FraudIndicator(
                type="high_amount",
                severity="medium",
                score=20,
                description=f"High transaction amount: {amount} SAR",
                detected_at=datetime.utcnow()
            ))
        
        # Suspicious amount patterns
        if amount in self.risk_rules["amount_rules"]["suspicious_amounts"]:
            indicators.append(FraudIndicator(
                type="suspicious_amount",
                severity="low",
                score=10,
                description=f"Suspicious amount pattern: {amount} SAR",
                detected_at=datetime.utcnow()
            ))
        
        return indicators

    def _check_geographic_rules(self, transaction_data: Dict[str, Any]) -> List[FraudIndicator]:
        """Check geographic fraud rules"""
        indicators = []
        
        # This would check IP geolocation, billing address, etc.
        # For now, return empty list
        return indicators

    def _check_behavioral_patterns(
        self, 
        transaction_data: Dict[str, Any],
        customer_history: List[Dict[str, Any]]
    ) -> List[FraudIndicator]:
        """Check behavioral fraud patterns"""
        indicators = []
        
        # New customer with high amount
        if len(customer_history) == 0:
            amount = Decimal(str(transaction_data["amount"]))
            if amount > self.risk_rules["behavioral_rules"]["new_customer_limit"]:
                indicators.append(FraudIndicator(
                    type="new_customer_high_amount",
                    severity="medium",
                    score=25,
                    description=f"New customer with high amount: {amount} SAR",
                    detected_at=datetime.utcnow()
                ))
        
        # Card testing pattern (multiple small amounts)
        small_transactions = [
            tx for tx in customer_history[-10:]  # Last 10 transactions
            if Decimal(str(tx["amount"])) < Decimal("50.00")
        ]
        
        if len(small_transactions) >= self.risk_rules["behavioral_rules"]["card_testing_pattern"]:
            indicators.append(FraudIndicator(
                type="card_testing",
                severity="high",
                score=35,
                description=f"Potential card testing: {len(small_transactions)} small transactions",
                detected_at=datetime.utcnow()
            ))
        
        return indicators

    def _calculate_risk_level(self, risk_score: float) -> Tuple[str, str]:
        """Calculate risk level and recommendation"""
        if risk_score >= 80:
            return "critical", "block_transaction"
        elif risk_score >= 60:
            return "high", "manual_review"
        elif risk_score >= 30:
            return "medium", "additional_verification"
        else:
            return "low", "approve"


# Global instances
def get_reconciliation_service(db: AsyncSession) -> PaymentReconciliationService:
    return PaymentReconciliationService(db)

fraud_detection_service = FraudDetectionService()