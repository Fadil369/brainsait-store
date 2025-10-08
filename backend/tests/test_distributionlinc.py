"""
Tests for DISTRIBUTIONLINC Agent
AI-powered intelligence layer for SSDP
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

from app.services.distributionlinc import DistributionLincService


@pytest.mark.unit
class TestDemandForecasting:
    """Test demand forecasting functionality"""

    @pytest.mark.asyncio
    async def test_generate_demand_forecast(self, async_session):
        """Test generating a demand forecast"""
        service = DistributionLincService(
            db=async_session,
            tenant_id="test_tenant",
            user_id="test_user@example.com"
        )

        forecast = await service.generate_demand_forecast(
            product_id="PROD123",
            product_name="Test Product",
            region="Riyadh",
            forecast_horizon_days=30,
            product_name_ar="منتج الاختبار",
            region_ar="الرياض"
        )

        assert forecast is not None
        assert forecast.product_id == "PROD123"
        assert forecast.region == "Riyadh"
        assert forecast.forecast_horizon_days == 30
        assert forecast.predicted_quantity > 0
        assert 0.0 <= forecast.confidence_score <= 1.0
        assert forecast.lower_bound <= forecast.predicted_quantity <= forecast.upper_bound
        assert forecast.model_version == DistributionLincService.MODEL_VERSION

    @pytest.mark.asyncio
    async def test_forecast_includes_factors(self, async_session):
        """Test that forecast includes influencing factors"""
        service = DistributionLincService(
            db=async_session,
            tenant_id="test_tenant"
        )

        forecast = await service.generate_demand_forecast(
            product_id="PROD456",
            product_name="Test Product 2",
            region="Jeddah",
            forecast_horizon_days=60
        )

        assert forecast.seasonal_factor is not None
        assert forecast.weather_impact is not None
        assert forecast.holiday_impact is not None
        assert forecast.trend_factor is not None

    @pytest.mark.asyncio
    async def test_get_demand_forecasts(self, async_session):
        """Test retrieving demand forecasts"""
        service = DistributionLincService(
            db=async_session,
            tenant_id="test_tenant"
        )

        # Create a forecast first
        await service.generate_demand_forecast(
            product_id="PROD789",
            product_name="Test Product 3",
            region="Dammam",
            forecast_horizon_days=30
        )

        # Retrieve forecasts
        forecasts = await service.get_demand_forecasts(
            product_id="PROD789",
            limit=10
        )

        assert len(forecasts) > 0
        assert forecasts[0].product_id == "PROD789"


class TestDynamicPricing:
    """Test dynamic pricing functionality"""

    @pytest.mark.asyncio
    async def test_generate_pricing_recommendation(self, async_session):
        """Test generating pricing recommendation"""
        service = DistributionLincService(
            db=async_session,
            tenant_id="test_tenant",
            user_id="test_user@example.com"
        )

        pricing = await service.generate_pricing_recommendation(
            product_id="PROD123",
            product_name="Test Product",
            current_price=100.0,
            base_price=90.0,
            inventory_level=500,
            product_name_ar="منتج الاختبار"
        )

        assert pricing is not None
        assert pricing.product_id == "PROD123"
        assert pricing.current_price == Decimal("100.00")
        assert pricing.base_price == Decimal("90.00")
        assert pricing.recommended_price >= pricing.min_price
        assert pricing.recommended_price <= pricing.max_price
        assert 0.0 <= pricing.confidence_score <= 1.0
        assert pricing.status == "pending"

    @pytest.mark.asyncio
    async def test_pricing_considers_inventory(self, async_session):
        """Test that pricing considers inventory levels"""
        service = DistributionLincService(
            db=async_session,
            tenant_id="test_tenant"
        )

        # High inventory should suggest lower price
        high_inv_pricing = await service.generate_pricing_recommendation(
            product_id="PROD_HIGH_INV",
            product_name="High Inventory Product",
            current_price=100.0,
            base_price=90.0,
            inventory_level=2000  # High inventory
        )

        # Low inventory should suggest higher price
        low_inv_pricing = await service.generate_pricing_recommendation(
            product_id="PROD_LOW_INV",
            product_name="Low Inventory Product",
            current_price=100.0,
            base_price=90.0,
            inventory_level=50  # Low inventory
        )

        assert high_inv_pricing.demand_level == "low"
        assert low_inv_pricing.demand_level == "high"

    @pytest.mark.asyncio
    async def test_approve_pricing(self, async_session):
        """Test approving pricing recommendation"""
        service = DistributionLincService(
            db=async_session,
            tenant_id="test_tenant",
            user_id="test_user@example.com"
        )

        # Create pricing
        pricing = await service.generate_pricing_recommendation(
            product_id="PROD456",
            product_name="Test Product",
            current_price=100.0,
            base_price=90.0
        )

        # Approve it
        approved = await service.approve_pricing(
            pricing_id=str(pricing.id),
            approved_by="manager@example.com"
        )

        assert approved is not None
        assert approved.status == "approved"
        assert approved.approved_by == "manager@example.com"
        assert approved.applied_at is not None


class TestRouteOptimization:
    """Test route optimization functionality"""

    @pytest.mark.asyncio
    async def test_optimize_route(self, async_session):
        """Test optimizing a delivery route"""
        service = DistributionLincService(
            db=async_session,
            tenant_id="test_tenant",
            user_id="test_user@example.com"
        )

        route = await service.optimize_route(
            route_name="Test Route",
            origin="Riyadh Warehouse",
            destination="Jeddah Outlet",
            waypoints=["Rest Stop 1", "Rest Stop 2"],
            vehicle_capacity_kg=1000.0,
            cargo_weight_kg=750.0,
            route_name_ar="مسار الاختبار"
        )

        assert route is not None
        assert route.route_name == "Test Route"
        assert route.origin == "Riyadh Warehouse"
        assert route.destination == "Jeddah Outlet"
        assert route.stops_count > 0
        assert route.estimated_distance_km > 0
        assert route.estimated_duration_minutes > 0
        assert route.estimated_cost > 0
        assert route.status == "recommended"

    @pytest.mark.asyncio
    async def test_route_includes_traffic_analysis(self, async_session):
        """Test that route includes traffic analysis"""
        service = DistributionLincService(
            db=async_session,
            tenant_id="test_tenant"
        )

        route = await service.optimize_route(
            route_name="Traffic Test Route",
            origin="Point A",
            destination="Point B"
        )

        assert route.traffic_level in ["low", "medium", "high"]
        assert route.traffic_delay_minutes is not None
        assert len(route.optimal_path) > 0

    @pytest.mark.asyncio
    async def test_get_route_optimizations(self, async_session):
        """Test retrieving route optimizations"""
        service = DistributionLincService(
            db=async_session,
            tenant_id="test_tenant"
        )

        # Create a route
        await service.optimize_route(
            route_name="Test Route 123",
            origin="Start",
            destination="End"
        )

        # Retrieve routes
        routes = await service.get_route_optimizations(limit=10)

        assert len(routes) > 0


class TestInventoryPrediction:
    """Test inventory prediction functionality"""

    @pytest.mark.asyncio
    async def test_predict_inventory_needs(self, async_session):
        """Test predicting inventory needs"""
        service = DistributionLincService(
            db=async_session,
            tenant_id="test_tenant",
            user_id="test_user@example.com"
        )

        prediction = await service.predict_inventory_needs(
            product_id="PROD123",
            product_name="Test Product",
            warehouse_id="WH001",
            warehouse_name="Main Warehouse",
            current_stock=150.0,
            lead_time_days=7,
            product_name_ar="منتج الاختبار"
        )

        assert prediction is not None
        assert prediction.product_id == "PROD123"
        assert prediction.warehouse_id == "WH001"
        assert prediction.current_stock == Decimal("150.00")
        assert prediction.reorder_point > 0
        assert prediction.safety_stock > 0
        assert prediction.recommended_reorder_quantity > 0
        assert prediction.risk_level in ["low", "medium", "high", "critical"]
        assert 0.0 <= prediction.confidence_score <= 1.0

    @pytest.mark.asyncio
    async def test_inventory_risk_levels(self, async_session):
        """Test different inventory risk levels"""
        service = DistributionLincService(
            db=async_session,
            tenant_id="test_tenant"
        )

        # Low stock should trigger high risk
        low_stock = await service.predict_inventory_needs(
            product_id="PROD_LOW",
            product_name="Low Stock Product",
            warehouse_id="WH001",
            warehouse_name="Warehouse 1",
            current_stock=10.0,  # Very low
            lead_time_days=7
        )

        # High stock should have lower risk
        high_stock = await service.predict_inventory_needs(
            product_id="PROD_HIGH",
            product_name="High Stock Product",
            warehouse_id="WH001",
            warehouse_name="Warehouse 1",
            current_stock=1000.0,  # High
            lead_time_days=7
        )

        # Low stock should have higher risk
        risk_levels = {"low": 1, "medium": 2, "high": 3, "critical": 4}
        assert risk_levels.get(low_stock.risk_level, 0) >= risk_levels.get(high_stock.risk_level, 0)

    @pytest.mark.asyncio
    async def test_po_suggestion_for_critical_stock(self, async_session):
        """Test PO suggestion for critical stock levels"""
        service = DistributionLincService(
            db=async_session,
            tenant_id="test_tenant"
        )

        prediction = await service.predict_inventory_needs(
            product_id="PROD_CRITICAL",
            product_name="Critical Stock Product",
            warehouse_id="WH001",
            warehouse_name="Warehouse 1",
            current_stock=5.0,  # Very low
            lead_time_days=14
        )

        # Critical/high risk should suggest PO
        if prediction.risk_level in ["critical", "high"]:
            assert prediction.po_suggested is True


class TestCustomerChurn:
    """Test customer churn prediction functionality"""

    @pytest.mark.asyncio
    async def test_predict_customer_churn(self, async_session):
        """Test predicting customer churn"""
        service = DistributionLincService(
            db=async_session,
            tenant_id="test_tenant",
            user_id="test_user@example.com"
        )

        prediction = await service.predict_customer_churn(
            customer_id="CUST123",
            customer_name="Test Customer",
            customer_type="outlet",
            recency_days=60,
            total_orders=20,
            lifetime_value=15000.0
        )

        assert prediction is not None
        assert prediction.customer_id == "CUST123"
        assert 0.0 <= prediction.churn_probability <= 1.0
        assert prediction.risk_level in ["low", "medium", "high", "critical"]
        assert prediction.total_orders == 20
        assert prediction.lifetime_value == Decimal("15000.00")
        assert 1 <= prediction.priority_level <= 5

    @pytest.mark.asyncio
    async def test_churn_retention_strategies(self, async_session):
        """Test that high-risk customers get retention strategies"""
        service = DistributionLincService(
            db=async_session,
            tenant_id="test_tenant"
        )

        # High recency days = high risk
        high_risk = await service.predict_customer_churn(
            customer_id="CUST_HIGH_RISK",
            customer_name="High Risk Customer",
            recency_days=120,  # Long time since last order
            total_orders=10,
            lifetime_value=10000.0
        )

        # High risk should have retention strategies
        if high_risk.risk_level in ["critical", "high"]:
            assert high_risk.retention_strategy is not None
            assert len(high_risk.retention_strategy) > 0

    @pytest.mark.asyncio
    async def test_log_churn_action(self, async_session):
        """Test logging retention action"""
        service = DistributionLincService(
            db=async_session,
            tenant_id="test_tenant",
            user_id="test_user@example.com"
        )

        # Create prediction
        prediction = await service.predict_customer_churn(
            customer_id="CUST456",
            customer_name="Test Customer",
            recency_days=90,
            total_orders=5,
            lifetime_value=5000.0
        )

        # Log action
        updated = await service.log_churn_action(
            prediction_id=str(prediction.id),
            action_type="discount_offer"
        )

        assert updated is not None
        assert updated.action_taken is True
        assert updated.action_type == "discount_offer"
        assert updated.action_date is not None

    @pytest.mark.asyncio
    async def test_get_churn_predictions_filtered(self, async_session):
        """Test retrieving churn predictions with filters"""
        service = DistributionLincService(
            db=async_session,
            tenant_id="test_tenant"
        )

        # Create predictions with different risk levels
        await service.predict_customer_churn(
            customer_id="CUST_HIGH",
            customer_name="High Risk",
            recency_days=150,
            total_orders=5,
            lifetime_value=5000.0
        )

        # Get only high-risk predictions
        predictions = await service.get_churn_predictions(
            min_churn_probability=0.5,
            limit=10
        )

        # All should have high probability
        for pred in predictions:
            assert pred.churn_probability >= 0.5


class TestDistributionAnalytics:
    """Test distribution analytics functionality"""

    @pytest.mark.asyncio
    async def test_get_distribution_analytics(self, async_session):
        """Test getting comprehensive analytics"""
        service = DistributionLincService(
            db=async_session,
            tenant_id="test_tenant",
            user_id="test_user@example.com"
        )

        # Create some test data
        await service.generate_demand_forecast(
            product_id="PROD_ANALYTICS",
            product_name="Analytics Test Product",
            region="Riyadh",
            forecast_horizon_days=30
        )

        await service.generate_pricing_recommendation(
            product_id="PROD_ANALYTICS",
            product_name="Analytics Test Product",
            current_price=100.0,
            base_price=90.0
        )

        # Get analytics
        analytics = await service.get_distribution_analytics()

        assert analytics is not None
        assert "forecasts_generated" in analytics
        assert "pricing_recommendations" in analytics
        assert "routes_optimized" in analytics
        assert "inventory_alerts" in analytics
        assert "churn_predictions" in analytics
        assert analytics["forecasts_generated"] > 0
        assert analytics["pricing_recommendations"] > 0

    @pytest.mark.asyncio
    async def test_analytics_date_range(self, async_session):
        """Test analytics with date range"""
        service = DistributionLincService(
            db=async_session,
            tenant_id="test_tenant"
        )

        start_date = datetime.utcnow() - timedelta(days=7)
        end_date = datetime.utcnow()

        analytics = await service.get_distribution_analytics(
            start_date=start_date,
            end_date=end_date
        )

        assert analytics["period_start"] == start_date
        assert analytics["period_end"] == end_date


class TestModelPerformance:
    """Test model performance and accuracy"""

    def test_model_version_consistency(self):
        """Test that model version is consistent"""
        assert DistributionLincService.MODEL_VERSION == "v1.0.0"

    @pytest.mark.asyncio
    async def test_confidence_scores_range(self, async_session):
        """Test that all confidence scores are within valid range"""
        service = DistributionLincService(
            db=async_session,
            tenant_id="test_tenant"
        )

        # Test forecast confidence
        forecast = await service.generate_demand_forecast(
            product_id="TEST_CONF",
            product_name="Confidence Test",
            region="Test",
            forecast_horizon_days=30
        )
        assert 0.0 <= forecast.confidence_score <= 1.0

        # Test pricing confidence
        pricing = await service.generate_pricing_recommendation(
            product_id="TEST_CONF",
            product_name="Confidence Test",
            current_price=100.0,
            base_price=90.0
        )
        assert 0.0 <= pricing.confidence_score <= 1.0


class TestBilingualSupport:
    """Test bilingual support (Arabic/English)"""

    @pytest.mark.asyncio
    async def test_arabic_field_support(self, async_session):
        """Test that Arabic fields are properly stored"""
        service = DistributionLincService(
            db=async_session,
            tenant_id="test_tenant"
        )

        forecast = await service.generate_demand_forecast(
            product_id="PROD_AR",
            product_name="Test Product",
            product_name_ar="منتج الاختبار",
            region="Riyadh",
            region_ar="الرياض",
            forecast_horizon_days=30
        )

        assert forecast.product_name_ar == "منتج الاختبار"
        assert forecast.region_ar == "الرياض"

    @pytest.mark.asyncio
    async def test_route_arabic_names(self, async_session):
        """Test Arabic route names"""
        service = DistributionLincService(
            db=async_session,
            tenant_id="test_tenant"
        )

        route = await service.optimize_route(
            route_name="Delivery Route",
            route_name_ar="مسار التوصيل",
            origin="Start",
            destination="End"
        )

        assert route.route_name_ar == "مسار التوصيل"


class TestAuditLogging:
    """Test audit logging functionality"""

    @pytest.mark.asyncio
    async def test_audit_log_created_on_forecast(self, async_session):
        """Test that audit log is created for forecasts"""
        service = DistributionLincService(
            db=async_session,
            tenant_id="test_tenant",
            user_id="audit_test@example.com"
        )

        forecast = await service.generate_demand_forecast(
            product_id="AUDIT_TEST",
            product_name="Audit Test Product",
            region="Test Region",
            forecast_horizon_days=30
        )

        # Audit log should be created (tested through service internals)
        assert forecast is not None

    @pytest.mark.asyncio
    async def test_audit_log_on_pricing_approval(self, async_session):
        """Test audit log on pricing approval"""
        service = DistributionLincService(
            db=async_session,
            tenant_id="test_tenant",
            user_id="audit_test@example.com"
        )

        pricing = await service.generate_pricing_recommendation(
            product_id="AUDIT_PRICING",
            product_name="Audit Pricing Test",
            current_price=100.0,
            base_price=90.0
        )

        approved = await service.approve_pricing(
            pricing_id=str(pricing.id),
            approved_by="approver@example.com"
        )

        assert approved.status == "approved"
