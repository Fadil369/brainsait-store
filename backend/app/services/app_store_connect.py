"""
App Store Connect API Service
Handles receipt validation, subscription management, and transaction verification
"""

import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import httpx
import jwt
from fastapi import HTTPException, status

from app.core.config import settings


class AppStoreConnectService:
    """App Store Connect API integration service"""

    def __init__(self):
        self.key_id = settings.APP_STORE_CONNECT_KEY_ID
        self.issuer_id = settings.APP_STORE_CONNECT_ISSUER_ID
        self.private_key_path = settings.APP_STORE_CONNECT_PRIVATE_KEY_PATH
        self.base_url = "https://api.storekit-itunes.apple.com"

    def _generate_jwt_token(self) -> str:
        """Generate JWT token for App Store Connect API authentication"""
        try:
            # Read private key
            with open(self.private_key_path, "r") as key_file:
                private_key = key_file.read()

            # JWT payload
            now = int(time.time())
            payload = {
                "iss": self.issuer_id,
                "iat": now,
                "exp": now + 1200,  # 20 minutes
                "aud": "appstoreconnect-v1",
                "bid": "io.brainsait.store",  # Your app bundle ID
            }

            # Generate JWT
            token = jwt.encode(
                payload, private_key, algorithm="ES256", headers={"kid": self.key_id}
            )

            return token

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate JWT token: {str(e)}",
            )

    async def validate_receipt(
        self, receipt_data: str, is_sandbox: bool = False
    ) -> Dict[str, Any]:
        """Validate App Store receipt"""
        try:
            # Choose validation URL based on environment
            validation_url = (
                "https://sandbox.itunes.apple.com/verifyReceipt"
                if is_sandbox
                else "https://buy.itunes.apple.com/verifyReceipt"
            )

            # Prepare request payload
            payload = {
                "receipt-data": receipt_data,
                "password": settings.APP_STORE_SHARED_SECRET,  # Add this to env
                "exclude-old-transactions": True,
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(validation_url, json=payload, timeout=30)

                if response.status_code != 200:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Receipt validation failed",
                    )

                result = response.json()

                # Handle sandbox fallback
                if result.get("status") == 21007 and not is_sandbox:
                    return await self.validate_receipt(receipt_data, is_sandbox=True)

                if result.get("status") != 0:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Receipt validation failed with status: {result.get('status')}",
                    )

                return result

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Receipt validation error: {str(e)}",
            )

    async def get_transaction_info(self, transaction_id: str) -> Dict[str, Any]:
        """Get transaction information using App Store Connect API"""
        try:
            token = self._generate_jwt_token()

            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }

            url = f"{self.base_url}/inApps/v1/transactions/{transaction_id}"

            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=30)

                if response.status_code != 200:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Transaction not found",
                    )

                return response.json()

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Transaction lookup error: {str(e)}",
            )

    async def get_subscription_status(
        self, original_transaction_id: str
    ) -> Dict[str, Any]:
        """Get subscription status and history"""
        try:
            token = self._generate_jwt_token()

            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }

            url = f"{self.base_url}/inApps/v1/subscriptions/{original_transaction_id}"

            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=30)

                if response.status_code != 200:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Subscription not found",
                    )

                return response.json()

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Subscription lookup error: {str(e)}",
            )

    async def process_server_notification(
        self, notification_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process App Store server-to-server notifications"""
        try:
            notification_type = notification_data.get("notificationType")

            if notification_type == "SUBSCRIBED":
                # Handle new subscription
                return await self._handle_subscription_started(notification_data)
            elif notification_type == "DID_RENEW":
                # Handle subscription renewal
                return await self._handle_subscription_renewed(notification_data)
            elif notification_type == "EXPIRED":
                # Handle subscription expiry
                return await self._handle_subscription_expired(notification_data)
            elif notification_type == "DID_CHANGE_RENEWAL_STATUS":
                # Handle renewal status change
                return await self._handle_renewal_status_change(notification_data)
            elif notification_type == "REFUND":
                # Handle refund
                return await self._handle_refund(notification_data)
            else:
                # Log unknown notification type
                return {
                    "status": "unknown_notification_type",
                    "type": notification_type,
                }

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Notification processing error: {str(e)}",
            )

    async def _handle_subscription_started(
        self, notification_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle new subscription"""
        # Extract transaction info
        transaction_info = notification_data.get("data", {}).get("transactionInfo", {})

        # Update user subscription status in database
        # This would integrate with your user/subscription models

        return {"status": "subscription_started", "transaction_info": transaction_info}

    async def _handle_subscription_renewed(
        self, notification_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle subscription renewal"""
        transaction_info = notification_data.get("data", {}).get("transactionInfo", {})

        # Update subscription expiry date
        # This would integrate with your subscription models

        return {"status": "subscription_renewed", "transaction_info": transaction_info}

    async def _handle_subscription_expired(
        self, notification_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle subscription expiry"""
        transaction_info = notification_data.get("data", {}).get("transactionInfo", {})

        # Mark subscription as expired
        # This would integrate with your subscription models

        return {"status": "subscription_expired", "transaction_info": transaction_info}

    async def _handle_renewal_status_change(
        self, notification_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle subscription renewal status change"""
        renewal_info = notification_data.get("data", {}).get("renewalInfo", {})

        # Update auto-renewal status
        # This would integrate with your subscription models

        return {"status": "renewal_status_changed", "renewal_info": renewal_info}

    async def _handle_refund(self, notification_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle refund notification"""
        transaction_info = notification_data.get("data", {}).get("transactionInfo", {})

        # Process refund in your system
        # This would integrate with your order/payment models

        return {"status": "refund_processed", "transaction_info": transaction_info}

    async def verify_app_store_purchase(
        self, receipt_data: str, user_id: int
    ) -> Dict[str, Any]:
        """Verify App Store purchase and update user access"""
        try:
            # Validate receipt
            receipt_info = await self.validate_receipt(receipt_data)

            # Extract purchase information
            receipt = receipt_info.get("receipt", {})
            in_app = receipt.get("in_app", [])

            if not in_app:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No in-app purchases found in receipt",
                )

            # Process each purchase
            purchases = []
            for purchase in in_app:
                product_id = purchase.get("product_id")
                transaction_id = purchase.get("transaction_id")
                purchase_date = purchase.get("purchase_date_ms")

                # Verify this is a valid BrainSAIT product
                if product_id and product_id.startswith("io.brainsait.store."):
                    purchases.append(
                        {
                            "product_id": product_id,
                            "transaction_id": transaction_id,
                            "purchase_date": purchase_date,
                            "verified": True,
                        }
                    )

            return {
                "verified": True,
                "user_id": user_id,
                "purchases": purchases,
                "receipt_info": receipt_info,
            }

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Purchase verification error: {str(e)}",
            )
