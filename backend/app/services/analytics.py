"""
Advanced Analytics Service
Provides comprehensive reporting and insights for BrainSAIT B2B platform
"""

import json
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import and_, asc, case, desc, extract, func, or_
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.orders import Order, OrderItem, OrderStatus, PaymentStatus
from app.models.products import Product
from app.models.users import User


class AnalyticsService:
    """Advanced analytics and reporting service"""

    def __init__(self, db: Session):
        self.db = db

    async def get_revenue_analytics(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        tenant_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get comprehensive revenue analytics"""

        # Default to last 30 days if no dates provided
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=30)

        # Base query filters
        filters = [
            Order.created_at >= start_date,
            Order.created_at <= end_date + timedelta(days=1),
            Order.status == OrderStatus.COMPLETED,
        ]

        if tenant_id:
            filters.append(Order.tenant_id == tenant_id)

        # Total revenue
        total_revenue = self.db.query(func.sum(Order.total_amount)).filter(
            *filters
        ).scalar() or Decimal("0.00")

        # Revenue by payment method
        revenue_by_payment = (
            self.db.query(
                Order.payment_method,
                func.sum(Order.total_amount).label("revenue"),
                func.count(Order.id).label("order_count"),
            )
            .filter(*filters)
            .group_by(Order.payment_method)
            .all()
        )

        # Daily revenue trend
        daily_revenue = (
            self.db.query(
                func.date(Order.created_at).label("date"),
                func.sum(Order.total_amount).label("revenue"),
                func.count(Order.id).label("orders"),
            )
            .filter(*filters)
            .group_by(func.date(Order.created_at))
            .order_by(func.date(Order.created_at))
            .all()
        )

        # Average order value
        avg_order_value = self.db.query(func.avg(Order.total_amount)).filter(
            *filters
        ).scalar() or Decimal("0.00")

        # Revenue growth (compared to previous period)
        prev_start = start_date - (end_date - start_date)
        prev_end = start_date

        prev_filters = [
            Order.created_at >= prev_start,
            Order.created_at <= prev_end,
            Order.status == OrderStatus.COMPLETED,
        ]

        if tenant_id:
            prev_filters.append(Order.tenant_id == tenant_id)

        prev_revenue = self.db.query(func.sum(Order.total_amount)).filter(
            *prev_filters
        ).scalar() or Decimal("0.00")

        revenue_growth = 0.0
        if prev_revenue > 0:
            revenue_growth = float((total_revenue - prev_revenue) / prev_revenue * 100)

        return {
            "total_revenue": float(total_revenue),
            "average_order_value": float(avg_order_value),
            "revenue_growth_percentage": revenue_growth,
            "revenue_by_payment_method": [
                {
                    "payment_method": payment.value if payment else "unknown",
                    "revenue": float(revenue),
                    "order_count": order_count,
                }
                for payment, revenue, order_count in revenue_by_payment
            ],
            "daily_revenue_trend": [
                {
                    "date": date_val.isoformat(),
                    "revenue": float(revenue),
                    "orders": orders,
                }
                for date_val, revenue, orders in daily_revenue
            ],
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
        }

    async def get_customer_analytics(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        tenant_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get customer behavior analytics"""

        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=30)

        base_filters = []
        if tenant_id:
            base_filters.append(User.tenant_id == tenant_id)

        # Total customers
        total_customers = (
            self.db.query(func.count(User.id)).filter(*base_filters).scalar()
        )

        # New customers in period
        new_customers = (
            self.db.query(func.count(User.id))
            .filter(
                User.created_at >= start_date,
                User.created_at <= end_date + timedelta(days=1),
                *base_filters,
            )
            .scalar()
        )

        # Active customers (with orders in period)
        active_customers = (
            self.db.query(func.count(func.distinct(Order.user_id)))
            .join(User)
            .filter(
                Order.created_at >= start_date,
                Order.created_at <= end_date + timedelta(days=1),
                *base_filters,
            )
            .scalar()
        )

        # Customer lifetime value
        customer_ltv = self.db.query(
            func.avg(
                self.db.query(func.sum(Order.total_amount))
                .filter(Order.user_id == User.id)
                .scalar_subquery()
            )
        ).filter(*base_filters).scalar() or Decimal("0.00")

        # Top customers by revenue
        top_customers = (
            self.db.query(
                User.id,
                User.email,
                User.full_name,
                func.sum(Order.total_amount).label("total_spent"),
                func.count(Order.id).label("order_count"),
            )
            .join(Order)
            .filter(
                Order.created_at >= start_date,
                Order.created_at <= end_date + timedelta(days=1),
                Order.status == OrderStatus.COMPLETED,
                *base_filters,
            )
            .group_by(User.id, User.email, User.full_name)
            .order_by(desc("total_spent"))
            .limit(10)
            .all()
        )

        # Customer acquisition by month
        customer_acquisition = (
            self.db.query(
                extract("year", User.created_at).label("year"),
                extract("month", User.created_at).label("month"),
                func.count(User.id).label("new_customers"),
            )
            .filter(*base_filters)
            .group_by(
                extract("year", User.created_at), extract("month", User.created_at)
            )
            .order_by("year", "month")
            .all()
        )

        return {
            "total_customers": total_customers,
            "new_customers": new_customers,
            "active_customers": active_customers,
            "customer_lifetime_value": float(customer_ltv),
            "top_customers": [
                {
                    "id": customer_id,
                    "email": email,
                    "full_name": full_name,
                    "total_spent": float(total_spent),
                    "order_count": order_count,
                }
                for customer_id, email, full_name, total_spent, order_count in top_customers
            ],
            "customer_acquisition_trend": [
                {"year": int(year), "month": int(month), "new_customers": new_customers}
                for year, month, new_customers in customer_acquisition
            ],
        }

    async def get_product_analytics(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        tenant_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get product performance analytics"""

        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=30)

        # Base filters for orders
        order_filters = [
            Order.created_at >= start_date,
            Order.created_at <= end_date + timedelta(days=1),
            Order.status == OrderStatus.COMPLETED,
        ]

        if tenant_id:
            order_filters.append(Order.tenant_id == tenant_id)

        # Top selling products
        top_products = (
            self.db.query(
                Product.id,
                Product.name,
                Product.price,
                func.sum(OrderItem.quantity).label("total_sold"),
                func.sum(OrderItem.subtotal).label("total_revenue"),
                func.count(func.distinct(Order.id)).label("order_count"),
            )
            .join(OrderItem)
            .join(Order)
            .filter(*order_filters)
            .group_by(Product.id, Product.name, Product.price)
            .order_by(desc("total_revenue"))
            .limit(10)
            .all()
        )

        # Product categories performance
        category_performance = (
            self.db.query(
                Product.category,
                func.sum(OrderItem.quantity).label("total_sold"),
                func.sum(OrderItem.subtotal).label("total_revenue"),
                func.count(func.distinct(Product.id)).label("product_count"),
            )
            .join(OrderItem)
            .join(Order)
            .filter(*order_filters)
            .group_by(Product.category)
            .order_by(desc("total_revenue"))
            .all()
        )

        # Product conversion rates (views to purchases)
        # This would require tracking product views - placeholder for now
        conversion_data = []

        return {
            "top_selling_products": [
                {
                    "id": product_id,
                    "name": name,
                    "price": float(price),
                    "total_sold": total_sold,
                    "total_revenue": float(total_revenue),
                    "order_count": order_count,
                }
                for product_id, name, price, total_sold, total_revenue, order_count in top_products
            ],
            "category_performance": [
                {
                    "category": category,
                    "total_sold": total_sold,
                    "total_revenue": float(total_revenue),
                    "product_count": product_count,
                }
                for category, total_sold, total_revenue, product_count in category_performance
            ],
            "conversion_rates": conversion_data,
        }

    async def get_payment_analytics(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        tenant_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get payment method and transaction analytics"""

        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=30)

        filters = [
            Order.created_at >= start_date,
            Order.created_at <= end_date + timedelta(days=1),
        ]

        if tenant_id:
            filters.append(Order.tenant_id == tenant_id)

        # Payment method distribution
        payment_distribution = (
            self.db.query(
                Order.payment_method,
                func.count(Order.id).label("transaction_count"),
                func.sum(Order.total_amount).label("total_amount"),
                func.avg(Order.total_amount).label("avg_amount"),
            )
            .filter(*filters)
            .group_by(Order.payment_method)
            .all()
        )

        # Payment success rates
        success_rates = (
            self.db.query(
                Order.payment_method,
                func.count(case([(Order.status == OrderStatus.COMPLETED, 1)])).label(
                    "successful"
                ),
                func.count(case([(Order.status == OrderStatus.FAILED, 1)])).label(
                    "failed"
                ),
                func.count(Order.id).label("total"),
            )
            .filter(*filters)
            .group_by(Order.payment_method)
            .all()
        )

        # Daily transaction volume
        daily_transactions = (
            self.db.query(
                func.date(Order.created_at).label("date"),
                func.count(Order.id).label("transaction_count"),
                func.sum(Order.total_amount).label("total_amount"),
            )
            .filter(*filters)
            .group_by(func.date(Order.created_at))
            .order_by(func.date(Order.created_at))
            .all()
        )

        return {
            "payment_method_distribution": [
                {
                    "payment_method": method.value if method else "unknown",
                    "transaction_count": count,
                    "total_amount": float(total),
                    "average_amount": float(avg),
                }
                for method, count, total, avg in payment_distribution
            ],
            "success_rates": [
                {
                    "payment_method": method.value if method else "unknown",
                    "successful_transactions": successful,
                    "failed_transactions": failed,
                    "total_transactions": total,
                    "success_rate": (successful / total * 100) if total > 0 else 0,
                }
                for method, successful, failed, total in success_rates
            ],
            "daily_transaction_volume": [
                {
                    "date": date_val.isoformat(),
                    "transaction_count": count,
                    "total_amount": float(amount),
                }
                for date_val, count, amount in daily_transactions
            ],
        }

    async def get_geographic_analytics(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        tenant_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get geographic distribution analytics"""

        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=30)

        filters = [
            Order.created_at >= start_date,
            Order.created_at <= end_date + timedelta(days=1),
            Order.status == OrderStatus.COMPLETED,
        ]

        if tenant_id:
            filters.append(Order.tenant_id == tenant_id)

        # Revenue by country (assuming billing_country field exists)
        # This is a placeholder - would need to add geography fields to Order model
        country_revenue = []

        # City distribution
        city_revenue = []

        return {
            "revenue_by_country": country_revenue,
            "revenue_by_city": city_revenue,
            "geographic_insights": {"top_countries": [], "emerging_markets": []},
        }

    async def generate_executive_summary(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        tenant_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Generate executive summary dashboard"""

        # Get all analytics
        revenue_data = await self.get_revenue_analytics(start_date, end_date, tenant_id)
        customer_data = await self.get_customer_analytics(
            start_date, end_date, tenant_id
        )
        product_data = await self.get_product_analytics(start_date, end_date, tenant_id)
        payment_data = await self.get_payment_analytics(start_date, end_date, tenant_id)

        # Calculate key metrics
        total_orders = len(revenue_data.get("daily_revenue_trend", []))

        return {
            "summary": {
                "total_revenue": revenue_data["total_revenue"],
                "total_customers": customer_data["total_customers"],
                "new_customers": customer_data["new_customers"],
                "average_order_value": revenue_data["average_order_value"],
                "revenue_growth": revenue_data["revenue_growth_percentage"],
            },
            "top_metrics": {
                "best_selling_product": (
                    product_data["top_selling_products"][0]
                    if product_data["top_selling_products"]
                    else None
                ),
                "preferred_payment_method": (
                    payment_data["payment_method_distribution"][0]
                    if payment_data["payment_method_distribution"]
                    else None
                ),
                "top_customer": (
                    customer_data["top_customers"][0]
                    if customer_data["top_customers"]
                    else None
                ),
            },
            "trends": {
                "revenue_trend": revenue_data["daily_revenue_trend"][
                    -7:
                ],  # Last 7 days
                "customer_acquisition": customer_data["customer_acquisition_trend"][
                    -3:
                ],  # Last 3 months
            },
            "period": revenue_data["period"],
        }
