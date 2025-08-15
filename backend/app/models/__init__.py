# Models package

# Import all models to ensure they are registered with SQLAlchemy
from . import users
from . import products 
from . import orders
from . import payments
from . import invoices
from . import sso
from . import analytics

# Make models available for import
from .users import User, UserSession, UserPreference, UserRole, UserStatus
from .products import Product, Category, Brand, ProductVariant, ProductReview, ProductStatus, StockStatus
from .orders import Order, OrderItem, CartItem, OrderStatusHistory, OrderStatus, PaymentStatus as OrderPaymentStatus
from .payments import (
    Payment, PaymentRefund, UserPaymentMethod, PaymentWebhook, PaymentMethod, PaymentStatus, RefundStatus,
    PaymentAuditLog, PaymentReconciliation, FraudDetectionLog
)
from .invoices import Invoice, InvoiceLineItem, ZATCASubmission, InvoiceType, InvoiceStatus, ZATCAStatus
from .sso import TenantSSO, SSOSession, SSOUserMapping, SSOType, SSOProvider
from .analytics import (
    AnalyticsEvent, ProductAnalytics, UserBehaviorAnalytics, BusinessMetrics, RetentionAnalytics, EventType
)

__all__ = [
    # Model classes
    "User", "UserSession", "UserPreference", "UserRole", "UserStatus",
    "Product", "Category", "Brand", "ProductVariant", "ProductReview", "ProductStatus", "StockStatus",
    "Order", "OrderItem", "CartItem", "OrderStatusHistory", "OrderStatus", "OrderPaymentStatus",
    "Payment", "PaymentRefund", "UserPaymentMethod", "PaymentWebhook", "PaymentMethod", "PaymentStatus", "RefundStatus",
    "PaymentAuditLog", "PaymentReconciliation", "FraudDetectionLog",
    "Invoice", "InvoiceLineItem", "ZATCASubmission", "InvoiceType", "InvoiceStatus", "ZATCAStatus",
    "TenantSSO", "SSOSession", "SSOUserMapping", "SSOType", "SSOProvider",
    "AnalyticsEvent", "ProductAnalytics", "UserBehaviorAnalytics", "BusinessMetrics", "RetentionAnalytics", "EventType",
]
