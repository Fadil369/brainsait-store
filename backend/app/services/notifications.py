"""
Notification Service for payment confirmations and alerts
Supporting email, SMS, and push notifications
"""

import logging
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict, Optional
from uuid import UUID

import httpx

from app.core.config import settings
logger = logging.getLogger(__name__)


class NotificationService:
    """Service for sending various types of notifications"""

    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD
        self.client = httpx.AsyncClient()

    async def send_payment_confirmation(
        self, 
        email: str, 
        order_id: UUID, 
        amount: float,
        payment_method: str = "card"
    ) -> bool:
        """Send payment confirmation email"""
        try:
            subject = "Payment Confirmation - BrainSAIT Store"
            
            # Create email content
            html_content = self._create_payment_confirmation_html(
                order_id, amount, payment_method
            )
            
            text_content = self._create_payment_confirmation_text(
                order_id, amount, payment_method
            )

            # Send email
            success = await self._send_email(
                to_email=email,
                subject=subject,
                html_content=html_content,
                text_content=text_content
            )

            if success:
                logger.info(f"Payment confirmation sent to {email} for order {order_id}")
            else:
                logger.error(f"Failed to send payment confirmation to {email}")

            return success

        except Exception as e:
            logger.error(f"Payment confirmation email failed: {e}")
            return False

    async def send_payment_failure(
        self, 
        email: str, 
        order_id: UUID, 
        error_message: str
    ) -> bool:
        """Send payment failure notification"""
        try:
            subject = "Payment Failed - BrainSAIT Store"
            
            html_content = self._create_payment_failure_html(order_id, error_message)
            text_content = self._create_payment_failure_text(order_id, error_message)

            success = await self._send_email(
                to_email=email,
                subject=subject,
                html_content=html_content,
                text_content=text_content
            )

            if success:
                logger.info(f"Payment failure notification sent to {email} for order {order_id}")
            else:
                logger.error(f"Failed to send payment failure notification to {email}")

            return success

        except Exception as e:
            logger.error(f"Payment failure notification failed: {e}")
            return False

    async def send_invoice_notification(
        self, 
        email: str, 
        order_id: UUID, 
        invoice_number: str,
        pdf_url: Optional[str] = None
    ) -> bool:
        """Send invoice notification with PDF attachment"""
        try:
            subject = f"Invoice {invoice_number} - BrainSAIT Store"
            
            html_content = self._create_invoice_notification_html(
                order_id, invoice_number, pdf_url
            )
            
            text_content = self._create_invoice_notification_text(
                order_id, invoice_number, pdf_url
            )

            success = await self._send_email(
                to_email=email,
                subject=subject,
                html_content=html_content,
                text_content=text_content
            )

            if success:
                logger.info(f"Invoice notification sent to {email} for order {order_id}")

            return success

        except Exception as e:
            logger.error(f"Invoice notification failed: {e}")
            return False

    async def _send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str,
        from_email: Optional[str] = None
    ) -> bool:
        """Send email using SMTP"""
        try:
            # Skip if SMTP not configured
            if not self.smtp_username or not self.smtp_password:
                logger.warning("SMTP not configured, skipping email send")
                return True  # Return True to not break the flow

            from_email = from_email or self.smtp_username

            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = from_email
            msg['To'] = to_email

            # Attach text and HTML versions
            text_part = MIMEText(text_content, 'plain', 'utf-8')
            html_part = MIMEText(html_content, 'html', 'utf-8')
            
            msg.attach(text_part)
            msg.attach(html_part)

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)

            return True

        except Exception as e:
            logger.error(f"SMTP email send failed: {e}")
            return False

    def _create_payment_confirmation_html(
        self, order_id: UUID, amount: float, payment_method: str
    ) -> str:
        """Create HTML content for payment confirmation"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Payment Confirmation</title>
        </head>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background-color: #f8f9fa; padding: 20px; text-align: center;">
                <h1 style="color: #28a745;">Payment Successful!</h1>
            </div>
            
            <div style="padding: 20px;">
                <h2>Thank you for your payment</h2>
                <p>Your payment has been successfully processed.</p>
                
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3>Payment Details</h3>
                    <p><strong>Order ID:</strong> {order_id}</p>
                    <p><strong>Amount:</strong> {amount} SAR</p>
                    <p><strong>Payment Method:</strong> {payment_method.replace('_', ' ').title()}</p>
                    <p><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                
                <p>We will process your order and send you updates via email.</p>
                
                <div style="text-align: center; margin-top: 30px;">
                    <a href="https://brainsait.com" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Visit BrainSAIT Store</a>
                </div>
            </div>
            
            <div style="background-color: #f8f9fa; padding: 20px; text-align: center; color: #666;">
                <p>BrainSAIT Store - Your Technology Partner</p>
                <p style="font-size: 12px;">This is an automated message. Please do not reply to this email.</p>
            </div>
        </body>
        </html>
        """

    def _create_payment_confirmation_text(
        self, order_id: UUID, amount: float, payment_method: str
    ) -> str:
        """Create text content for payment confirmation"""
        return f"""
Payment Successful!

Thank you for your payment to BrainSAIT Store.

Payment Details:
- Order ID: {order_id}
- Amount: {amount} SAR
- Payment Method: {payment_method.replace('_', ' ').title()}
- Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

We will process your order and send you updates via email.

BrainSAIT Store - Your Technology Partner
Visit us at: https://brainsait.com

This is an automated message. Please do not reply to this email.
        """

    def _create_payment_failure_html(self, order_id: UUID, error_message: str) -> str:
        """Create HTML content for payment failure"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Payment Failed</title>
        </head>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background-color: #f8d7da; padding: 20px; text-align: center;">
                <h1 style="color: #721c24;">Payment Failed</h1>
            </div>
            
            <div style="padding: 20px;">
                <h2>We encountered an issue with your payment</h2>
                <p>Unfortunately, we were unable to process your payment for order {order_id}.</p>
                
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3>Error Details</h3>
                    <p><strong>Order ID:</strong> {order_id}</p>
                    <p><strong>Error:</strong> {error_message}</p>
                    <p><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                
                <p>Please try again or contact our support team if the issue persists.</p>
                
                <div style="text-align: center; margin-top: 30px;">
                    <a href="https://brainsait.com/support" style="background-color: #dc3545; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Contact Support</a>
                </div>
            </div>
            
            <div style="background-color: #f8f9fa; padding: 20px; text-align: center; color: #666;">
                <p>BrainSAIT Store - Your Technology Partner</p>
                <p style="font-size: 12px;">This is an automated message. Please do not reply to this email.</p>
            </div>
        </body>
        </html>
        """

    def _create_payment_failure_text(self, order_id: UUID, error_message: str) -> str:
        """Create text content for payment failure"""
        return f"""
Payment Failed

We encountered an issue with your payment for order {order_id}.

Error Details:
- Order ID: {order_id}
- Error: {error_message}
- Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Please try again or contact our support team if the issue persists.

Contact Support: https://brainsait.com/support

BrainSAIT Store - Your Technology Partner
Visit us at: https://brainsait.com

This is an automated message. Please do not reply to this email.
        """

    def _create_invoice_notification_html(
        self, order_id: UUID, invoice_number: str, pdf_url: Optional[str]
    ) -> str:
        """Create HTML content for invoice notification"""
        pdf_link = f'<a href="{pdf_url}" style="color: #007bff;">Download PDF</a>' if pdf_url else 'PDF will be available soon'
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Invoice {invoice_number}</title>
        </head>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background-color: #e3f2fd; padding: 20px; text-align: center;">
                <h1 style="color: #1976d2;">Invoice Available</h1>
            </div>
            
            <div style="padding: 20px;">
                <h2>Your invoice is ready</h2>
                <p>Your ZATCA-compliant invoice has been generated for order {order_id}.</p>
                
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3>Invoice Details</h3>
                    <p><strong>Invoice Number:</strong> {invoice_number}</p>
                    <p><strong>Order ID:</strong> {order_id}</p>
                    <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p><strong>Download:</strong> {pdf_link}</p>
                </div>
                
                <p>This invoice is compliant with Saudi Arabia's ZATCA requirements.</p>
            </div>
            
            <div style="background-color: #f8f9fa; padding: 20px; text-align: center; color: #666;">
                <p>BrainSAIT Store - Your Technology Partner</p>
                <p style="font-size: 12px;">This is an automated message. Please do not reply to this email.</p>
            </div>
        </body>
        </html>
        """

    def _create_invoice_notification_text(
        self, order_id: UUID, invoice_number: str, pdf_url: Optional[str]
    ) -> str:
        """Create text content for invoice notification"""
        pdf_info = f"Download: {pdf_url}" if pdf_url else "PDF will be available soon"
        
        return f"""
Invoice Available

Your ZATCA-compliant invoice has been generated for order {order_id}.

Invoice Details:
- Invoice Number: {invoice_number}
- Order ID: {order_id}
- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- {pdf_info}

This invoice is compliant with Saudi Arabia's ZATCA requirements.

BrainSAIT Store - Your Technology Partner
Visit us at: https://brainsait.com

This is an automated message. Please do not reply to this email.
        """