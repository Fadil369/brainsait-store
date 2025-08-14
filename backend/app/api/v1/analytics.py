"""
Analytics API endpoints
Provides comprehensive reporting and insights
"""

from datetime import date, datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.users import User
from app.services.analytics import AnalyticsService

router = APIRouter()


class DateRangeRequest(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None


@router.get("/revenue")
async def get_revenue_analytics(
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get comprehensive revenue analytics"""
    analytics_service = AnalyticsService(db)

    try:
        result = await analytics_service.get_revenue_analytics(
            start_date=start_date, end_date=end_date, tenant_id=current_user.tenant_id
        )

        return {
            "success": True,
            "data": result,
            "message": "Revenue analytics retrieved successfully",
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve revenue analytics: {str(e)}",
        )


@router.get("/customers")
async def get_customer_analytics(
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get customer behavior analytics"""
    analytics_service = AnalyticsService(db)

    try:
        result = await analytics_service.get_customer_analytics(
            start_date=start_date, end_date=end_date, tenant_id=current_user.tenant_id
        )

        return {
            "success": True,
            "data": result,
            "message": "Customer analytics retrieved successfully",
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve customer analytics: {str(e)}",
        )


@router.get("/products")
async def get_product_analytics(
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get product performance analytics"""
    analytics_service = AnalyticsService(db)

    try:
        result = await analytics_service.get_product_analytics(
            start_date=start_date, end_date=end_date, tenant_id=current_user.tenant_id
        )

        return {
            "success": True,
            "data": result,
            "message": "Product analytics retrieved successfully",
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve product analytics: {str(e)}",
        )


@router.get("/payments")
async def get_payment_analytics(
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get payment method and transaction analytics"""
    analytics_service = AnalyticsService(db)

    try:
        result = await analytics_service.get_payment_analytics(
            start_date=start_date, end_date=end_date, tenant_id=current_user.tenant_id
        )

        return {
            "success": True,
            "data": result,
            "message": "Payment analytics retrieved successfully",
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve payment analytics: {str(e)}",
        )


@router.get("/geographic")
async def get_geographic_analytics(
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get geographic distribution analytics"""
    analytics_service = AnalyticsService(db)

    try:
        result = await analytics_service.get_geographic_analytics(
            start_date=start_date, end_date=end_date, tenant_id=current_user.tenant_id
        )

        return {
            "success": True,
            "data": result,
            "message": "Geographic analytics retrieved successfully",
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve geographic analytics: {str(e)}",
        )


@router.get("/dashboard")
async def get_executive_dashboard(
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get executive summary dashboard"""
    analytics_service = AnalyticsService(db)

    try:
        result = await analytics_service.generate_executive_summary(
            start_date=start_date, end_date=end_date, tenant_id=current_user.tenant_id
        )

        return {
            "success": True,
            "data": result,
            "message": "Executive dashboard retrieved successfully",
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve executive dashboard: {str(e)}",
        )


@router.get("/export")
async def export_analytics_report(
    report_type: str = Query(
        ..., description="Type of report (revenue, customers, products, payments)"
    ),
    format: str = Query("json", description="Export format (json, csv)"),
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Export analytics report in specified format"""
    analytics_service = AnalyticsService(db)

    try:
        # Get the appropriate analytics data
        if report_type == "revenue":
            data = await analytics_service.get_revenue_analytics(
                start_date, end_date, current_user.tenant_id
            )
        elif report_type == "customers":
            data = await analytics_service.get_customer_analytics(
                start_date, end_date, current_user.tenant_id
            )
        elif report_type == "products":
            data = await analytics_service.get_product_analytics(
                start_date, end_date, current_user.tenant_id
            )
        elif report_type == "payments":
            data = await analytics_service.get_payment_analytics(
                start_date, end_date, current_user.tenant_id
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid report type. Choose from: revenue, customers, products, payments",
            )

        if format == "csv":
            # Convert to CSV format (simplified example)
            # In a real implementation, you'd use pandas or csv module
            csv_data = "Report generated in CSV format"
            return {
                "success": True,
                "data": csv_data,
                "format": "csv",
                "message": f"{report_type.title()} report exported successfully",
            }
        else:
            return {
                "success": True,
                "data": data,
                "format": "json",
                "message": f"{report_type.title()} report exported successfully",
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export {report_type} report: {str(e)}",
        )


@router.get("/real-time")
async def get_real_time_metrics(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get real-time metrics for live dashboard"""
    analytics_service = AnalyticsService(db)

    try:
        # Get today's metrics
        today = date.today()
        yesterday = today - timedelta(days=1)

        today_revenue = await analytics_service.get_revenue_analytics(
            start_date=today, end_date=today, tenant_id=current_user.tenant_id
        )

        yesterday_revenue = await analytics_service.get_revenue_analytics(
            start_date=yesterday, end_date=yesterday, tenant_id=current_user.tenant_id
        )

        # Calculate real-time metrics
        real_time_data = {
            "today_revenue": today_revenue["total_revenue"],
            "yesterday_revenue": yesterday_revenue["total_revenue"],
            "revenue_change": today_revenue["total_revenue"]
            - yesterday_revenue["total_revenue"],
            "current_hour_orders": 0,  # Would need to implement hour-based tracking
            "active_sessions": 0,  # Would need session tracking
            "conversion_rate": 0.0,  # Would need view tracking
            "last_updated": datetime.now().isoformat(),
        }

        return {
            "success": True,
            "data": real_time_data,
            "message": "Real-time metrics retrieved successfully",
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve real-time metrics: {str(e)}",
        )
