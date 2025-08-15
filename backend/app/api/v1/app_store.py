"""
App Store Connect API endpoints
Handles receipt validation, subscription management, and notifications
"""

import logging
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.database import get_db
from app.models.users import User
from app.services.app_store_connect import AppStoreConnectService

router = APIRouter()


class ReceiptValidationRequest(BaseModel):
    receipt_data: str
    is_sandbox: bool = False


class TransactionInfoRequest(BaseModel):
    transaction_id: str


class SubscriptionStatusRequest(BaseModel):
    original_transaction_id: str


@router.post("/validate-receipt", response_model=Dict[str, Any])
async def validate_receipt(
    request: ReceiptValidationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Validate App Store receipt"""
    app_store_service = AppStoreConnectService()

    try:
        result = await app_store_service.verify_app_store_purchase(
            receipt_data=request.receipt_data, user_id=current_user.id
        )

        return {
            "success": True,
            "data": result,
            "message": "Receipt validated successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Receipt validation failed: {str(e)}",
        )


@router.post("/transaction-info", response_model=Dict[str, Any])
async def get_transaction_info(
    request: TransactionInfoRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get transaction information"""
    app_store_service = AppStoreConnectService()

    try:
        result = await app_store_service.get_transaction_info(
            transaction_id=request.transaction_id
        )

        return {
            "success": True,
            "data": result,
            "message": "Transaction info retrieved successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transaction lookup failed: {str(e)}",
        )


@router.post("/subscription-status", response_model=Dict[str, Any])
async def get_subscription_status(
    request: SubscriptionStatusRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get subscription status and history"""
    app_store_service = AppStoreConnectService()

    try:
        result = await app_store_service.get_subscription_status(
            original_transaction_id=request.original_transaction_id
        )

        return {
            "success": True,
            "data": result,
            "message": "Subscription status retrieved successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Subscription lookup failed: {str(e)}",
        )


@router.post("/webhook/notifications")
async def handle_server_notifications(request: Request, db: Session = Depends(get_db)):
    """Handle App Store server-to-server notifications"""
    app_store_service = AppStoreConnectService()

    try:
        # Get the notification data  
        notification_data = await request.json()

        # Process the notification
        result = await app_store_service.process_server_notification(notification_data)

        return {
            "success": True,
            "data": result,
            "message": "Notification processed successfully",
        }

    except Exception as e:
        # Log the error but return 200 to prevent retries
        logging.error(f"Notification processing error: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": "Internal server error",
            "message": "Notification processing failed",
        }


@router.get("/products")
async def get_app_store_products(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get available BrainSAIT App Store products"""

    # Define your BrainSAIT store products
    products = [
        {
            "product_id": "io.brainsait.store.basic_plan",
            "name": "BrainSAIT Basic Plan",
            "description": "Basic access to BrainSAIT solutions",
            "price": "$99.99",
            "type": "subscription",
            "duration": "monthly",
        },
        {
            "product_id": "io.brainsait.store.pro_plan",
            "name": "BrainSAIT Pro Plan",
            "description": "Professional access with advanced features",
            "price": "$299.99",
            "type": "subscription",
            "duration": "monthly",
        },
        {
            "product_id": "io.brainsait.store.enterprise_plan",
            "name": "BrainSAIT Enterprise Plan",
            "description": "Full enterprise solution with source code",
            "price": "$999.99",
            "type": "subscription",
            "duration": "monthly",
        },
        {
            "product_id": "io.brainsait.store.complete_solution",
            "name": "Complete B2B Solution",
            "description": "One-time purchase of complete solution",
            "price": "$19999.99",
            "type": "non_consumable",
        },
    ]

    return {
        "success": True,
        "data": products,
        "message": "Products retrieved successfully",
    }


@router.post("/purchase/complete")
async def complete_purchase(
    request: ReceiptValidationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Complete App Store purchase and grant access"""
    app_store_service = AppStoreConnectService()

    try:
        # Validate the receipt
        validation_result = await app_store_service.verify_app_store_purchase(
            receipt_data=request.receipt_data, user_id=current_user.id
        )

        if not validation_result.get("verified"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Purchase could not be verified",
            )

        # Grant access based on purchased products
        purchases = validation_result.get("purchases", [])
        for purchase in purchases:
            product_id = purchase.get("product_id")

            # Update user access based on product
            if "basic_plan" in product_id:
                # Grant basic plan access
                current_user.subscription_tier = "basic"
            elif "pro_plan" in product_id:
                # Grant pro plan access
                current_user.subscription_tier = "pro"
            elif "enterprise_plan" in product_id:
                # Grant enterprise plan access
                current_user.subscription_tier = "enterprise"
            elif "complete_solution" in product_id:
                # Grant complete solution access
                current_user.has_complete_solution = True

        db.commit()

        return {
            "success": True,
            "data": {
                "user_id": current_user.id,
                "purchases": purchases,
                "access_granted": True,
            },
            "message": "Purchase completed and access granted",
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Purchase completion failed: {str(e)}",
        )
