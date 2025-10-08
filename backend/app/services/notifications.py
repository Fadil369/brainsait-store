"""
Notification Service for Payment Confirmations and Alerts
Supports Email and SMS notifications for Saudi market
"""

import logging
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

import httpx
from fastapi import HTTPException

from app.core.config import settings

logger = logging.getLogger(__name__)


class NotificationService:
    """Notification service for payment and order updates"""
    
    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.FROM_EMAIL
        self.from_name = settings.FROM_NAME
        self.from_name_ar = settings.FROM_NAME_AR
        
        # SMS configuration
        self.sms_provider = settings.SMS_PROVIDER
        self.unifonic_app_sid = settings.UNIFONIC_APP_SID
        self.unifonic_sender_id = settings.UNIFONIC_SENDER_ID
        self.taqnyat_api_key = settings.TAQNYAT_API_KEY
        self.taqnyat_sender = settings.TAQNYAT_SENDER
        
        self.http_client = httpx.AsyncClient(timeout=30.0)
        
    async def send_payment_confirmation(
        self,
        email: str,
        order_id: UUID,
        amount: float,
        language: str = "en"
    ) -> bool:
        """
        Send payment confirmation email
        
        Args:
            email: Customer email
            order_id: Order UUID
            amount: Payment amount
            language: Language code ('en' or 'ar')
            
        Returns:
            Success status
        """
        try:
            subject = self._get_subject("payment_confirmation", language)
            body = self._get_email_body(
                "payment_confirmation",
                language,
                {
                    "order_id": str(order_id),
                    "amount": f"{amount:.2f}",
                    "currency": "SAR",
                }
            )
            
            await self._send_email(email, subject, body)
            logger.info(f"Payment confirmation sent to {email} for order {order_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send payment confirmation: {e}")
            return False
            
    async def send_payment_failure(
        self,
        email: str,
        order_id: UUID,
        error_message: str,
        language: str = "en"
    ) -> bool:
        """
        Send payment failure notification
        
        Args:
            email: Customer email
            order_id: Order UUID
            error_message: Error description
            language: Language code ('en' or 'ar')
            
        Returns:
            Success status
        """
        try:
            subject = self._get_subject("payment_failure", language)
            body = self._get_email_body(
                "payment_failure",
                language,
                {
                    "order_id": str(order_id),
                    "error": error_message,
                }
            )
            
            await self._send_email(email, subject, body)
            logger.info(f"Payment failure notification sent to {email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send payment failure notification: {e}")
            return False
            
    async def send_invoice_notification(
        self,
        email: str,
        invoice_number: str,
        invoice_url: str,
        language: str = "en"
    ) -> bool:
        """
        Send invoice notification with download link
        
        Args:
            email: Customer email
            invoice_number: Invoice number
            invoice_url: URL to download invoice
            language: Language code ('en' or 'ar')
            
        Returns:
            Success status
        """
        try:
            subject = self._get_subject("invoice_ready", language)
            body = self._get_email_body(
                "invoice_ready",
                language,
                {
                    "invoice_number": invoice_number,
                    "invoice_url": invoice_url,
                }
            )
            
            await self._send_email(email, subject, body)
            logger.info(f"Invoice notification sent to {email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send invoice notification: {e}")
            return False
            
    async def send_sms(
        self,
        phone: str,
        message: str,
        language: str = "en"
    ) -> bool:
        """
        Send SMS notification
        
        Args:
            phone: Phone number (Saudi format: +966...)
            message: SMS message text
            language: Language code ('en' or 'ar')
            
        Returns:
            Success status
        """
        try:
            if self.sms_provider == "unifonic":
                return await self._send_unifonic_sms(phone, message)
            elif self.sms_provider == "taqnyat":
                return await self._send_taqnyat_sms(phone, message)
            else:
                logger.warning(f"Unknown SMS provider: {self.sms_provider}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send SMS: {e}")
            return False
            
    async def send_payment_confirmation_sms(
        self,
        phone: str,
        order_id: UUID,
        amount: float,
        language: str = "ar"
    ) -> bool:
        """
        Send payment confirmation SMS
        
        Args:
            phone: Phone number
            order_id: Order UUID
            amount: Payment amount
            language: Language code ('en' or 'ar')
            
        Returns:
            Success status
        """
        if language == "ar":
            message = f"تم استلام الدفع بنجاح. رقم الطلب: {order_id}. المبلغ: {amount:.2f} ريال"
        else:
            message = f"Payment received successfully. Order: {order_id}. Amount: {amount:.2f} SAR"
            
        return await self.send_sms(phone, message, language)
        
    async def _send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html: bool = True
    ) -> None:
        """
        Send email using SMTP
        
        Args:
            to_email: Recipient email
            subject: Email subject
            body: Email body (HTML or plain text)
            html: Whether body is HTML
        """
        # In production, use proper SMTP library like aiosmtplib
        # For now, log the email
        logger.info(
            f"Email would be sent to {to_email}\n"
            f"Subject: {subject}\n"
            f"Body: {body[:100]}..."
        )
        
        # TODO: Implement actual SMTP sending
        # Example using aiosmtplib:
        # import aiosmtplib
        # from email.message import EmailMessage
        # 
        # message = EmailMessage()
        # message["From"] = f"{self.from_name} <{self.from_email}>"
        # message["To"] = to_email
        # message["Subject"] = subject
        # if html:
        #     message.add_alternative(body, subtype="html")
        # else:
        #     message.set_content(body)
        #     
        # await aiosmtplib.send(
        #     message,
        #     hostname=self.smtp_server,
        #     port=self.smtp_port,
        #     username=self.smtp_username,
        #     password=self.smtp_password,
        #     use_tls=True,
        # )
        
    async def _send_unifonic_sms(self, phone: str, message: str) -> bool:
        """
        Send SMS using Unifonic API
        
        Args:
            phone: Phone number
            message: SMS message
            
        Returns:
            Success status
        """
        if not self.unifonic_app_sid:
            logger.warning("Unifonic credentials not configured")
            return False
            
        try:
            url = "https://api.unifonic.com/rest/Messages/Send"
            payload = {
                "AppSid": self.unifonic_app_sid,
                "SenderID": self.unifonic_sender_id,
                "Recipient": phone,
                "Body": message,
            }
            
            response = await self.http_client.post(url, data=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") == "true":
                    logger.info(f"SMS sent successfully via Unifonic to {phone}")
                    return True
                else:
                    logger.error(f"Unifonic SMS failed: {data}")
                    return False
            else:
                logger.error(f"Unifonic API error: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Unifonic SMS request failed: {e}")
            return False
            
    async def _send_taqnyat_sms(self, phone: str, message: str) -> bool:
        """
        Send SMS using Taqnyat API
        
        Args:
            phone: Phone number
            message: SMS message
            
        Returns:
            Success status
        """
        if not self.taqnyat_api_key:
            logger.warning("Taqnyat credentials not configured")
            return False
            
        try:
            url = "https://api.taqnyat.sa/v1/messages"
            headers = {
                "Authorization": f"Bearer {self.taqnyat_api_key}",
                "Content-Type": "application/json",
            }
            payload = {
                "recipients": [phone],
                "body": message,
                "sender": self.taqnyat_sender,
            }
            
            response = await self.http_client.post(
                url,
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                logger.info(f"SMS sent successfully via Taqnyat to {phone}")
                return True
            else:
                logger.error(f"Taqnyat API error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Taqnyat SMS request failed: {e}")
            return False
            
    def _get_subject(self, template: str, language: str) -> str:
        """Get email subject for template and language"""
        subjects = {
            "payment_confirmation": {
                "en": "Payment Confirmation - BrainSAIT Store",
                "ar": "تأكيد الدفع - متجر برين سايت",
            },
            "payment_failure": {
                "en": "Payment Failed - BrainSAIT Store",
                "ar": "فشل الدفع - متجر برين سايت",
            },
            "invoice_ready": {
                "en": "Your Invoice is Ready - BrainSAIT Store",
                "ar": "فاتورتك جاهزة - متجر برين سايت",
            },
        }
        return subjects.get(template, {}).get(language, subjects[template]["en"])
        
    def _get_email_body(
        self,
        template: str,
        language: str,
        data: Dict[str, Any]
    ) -> str:
        """Get email body HTML for template and language"""
        
        if template == "payment_confirmation":
            if language == "ar":
                return f"""
                <html dir="rtl">
                <body style="font-family: Arial, sans-serif;">
                    <h2>تم استلام الدفع بنجاح</h2>
                    <p>عزيزنا العميل،</p>
                    <p>تم استلام دفعتك بنجاح.</p>
                    <ul>
                        <li><strong>رقم الطلب:</strong> {data['order_id']}</li>
                        <li><strong>المبلغ:</strong> {data['amount']} {data['currency']}</li>
                    </ul>
                    <p>شكراً لتعاملك مع متجر برين سايت</p>
                </body>
                </html>
                """
            else:
                return f"""
                <html>
                <body style="font-family: Arial, sans-serif;">
                    <h2>Payment Confirmation</h2>
                    <p>Dear Customer,</p>
                    <p>Your payment has been received successfully.</p>
                    <ul>
                        <li><strong>Order ID:</strong> {data['order_id']}</li>
                        <li><strong>Amount:</strong> {data['amount']} {data['currency']}</li>
                    </ul>
                    <p>Thank you for shopping with BrainSAIT Store</p>
                </body>
                </html>
                """
                
        elif template == "payment_failure":
            if language == "ar":
                return f"""
                <html dir="rtl">
                <body style="font-family: Arial, sans-serif;">
                    <h2>فشل الدفع</h2>
                    <p>عزيزنا العميل،</p>
                    <p>لم نتمكن من معالجة دفعتك.</p>
                    <ul>
                        <li><strong>رقم الطلب:</strong> {data['order_id']}</li>
                        <li><strong>السبب:</strong> {data['error']}</li>
                    </ul>
                    <p>يرجى المحاولة مرة أخرى أو التواصل معنا</p>
                </body>
                </html>
                """
            else:
                return f"""
                <html>
                <body style="font-family: Arial, sans-serif;">
                    <h2>Payment Failed</h2>
                    <p>Dear Customer,</p>
                    <p>We were unable to process your payment.</p>
                    <ul>
                        <li><strong>Order ID:</strong> {data['order_id']}</li>
                        <li><strong>Reason:</strong> {data['error']}</li>
                    </ul>
                    <p>Please try again or contact us for assistance</p>
                </body>
                </html>
                """
                
        elif template == "invoice_ready":
            if language == "ar":
                return f"""
                <html dir="rtl">
                <body style="font-family: Arial, sans-serif;">
                    <h2>فاتورتك جاهزة</h2>
                    <p>عزيزنا العميل،</p>
                    <p>فاتورتك الضريبية جاهزة للتنزيل.</p>
                    <ul>
                        <li><strong>رقم الفاتورة:</strong> {data['invoice_number']}</li>
                    </ul>
                    <p><a href="{data['invoice_url']}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">تنزيل الفاتورة</a></p>
                    <p>شكراً لتعاملك معنا</p>
                </body>
                </html>
                """
            else:
                return f"""
                <html>
                <body style="font-family: Arial, sans-serif;">
                    <h2>Your Invoice is Ready</h2>
                    <p>Dear Customer,</p>
                    <p>Your tax invoice is ready for download.</p>
                    <ul>
                        <li><strong>Invoice Number:</strong> {data['invoice_number']}</li>
                    </ul>
                    <p><a href="{data['invoice_url']}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Download Invoice</a></p>
                    <p>Thank you for your business</p>
                </body>
                </html>
                """
                
        return ""
