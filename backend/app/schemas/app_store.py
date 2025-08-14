"""
App Store Connect API schemas
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class ReceiptValidationRequest(BaseModel):
    receipt_data: str
    is_sandbox: bool = False


class ReceiptValidationResponse(BaseModel):
    verified: bool
    user_id: int
    purchases: List[Dict[str, Any]]
    receipt_info: Dict[str, Any]


class TransactionInfoRequest(BaseModel):
    transaction_id: str


class TransactionInfoResponse(BaseModel):
    transaction_id: str
    product_id: str
    purchase_date: Optional[datetime]
    expires_date: Optional[datetime]
    is_trial_period: bool = False


class SubscriptionStatusRequest(BaseModel):
    original_transaction_id: str


class SubscriptionStatusResponse(BaseModel):
    original_transaction_id: str
    auto_renew_status: bool
    expiration_intent: Optional[str]
    is_in_billing_retry_period: bool = False
    product_id: str


class ServerNotificationRequest(BaseModel):
    notification_type: str
    data: Dict[str, Any]


class AppStoreProduct(BaseModel):
    product_id: str
    name: str
    description: str
    price: str
    type: str  # subscription, consumable, non_consumable
    duration: Optional[str] = None  # for subscriptions


class PurchaseCompletionRequest(BaseModel):
    receipt_data: str
    transaction_id: str
    product_id: str


class PurchaseCompletionResponse(BaseModel):
    success: bool
    user_id: int
    product_id: str
    access_granted: bool
    expires_at: Optional[datetime] = None
