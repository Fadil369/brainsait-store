"""
Tests for Driver Management API
"""

import pytest
from datetime import datetime, timedelta
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.logistics import Driver, DriverStatus, VehicleType


@pytest.mark.asyncio
async def test_register_driver(client: AsyncClient, test_user_headers):
    """Test driver registration"""
    driver_data = {
        "full_name": "Ahmed Al-Saud",
        "phone": "+966501234567",
        "email": "ahmed@example.com",
        "license_number": "LIC123456",
        "license_type": "Class C",
        "license_expiry": (datetime.now() + timedelta(days=365)).isoformat(),
        "vehicle_type": "van",
        "vehicle_plate": "ABC-1234",
        "vehicle_capacity_kg": 1000.0,
        "vehicle_capacity_m3": 10.0,
        "hourly_rate": 50.0,
        "per_delivery_rate": 15.0,
    }
    
    response = await client.post(
        "/api/v1/drivers/",
        json=driver_data,
        headers=test_user_headers,
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["full_name"] == driver_data["full_name"]
    assert data["phone"] == driver_data["phone"]
    assert data["vehicle_type"] == driver_data["vehicle_type"]
    assert "driver_code" in data
    assert data["status"] == "available"


@pytest.mark.asyncio
async def test_list_drivers(client: AsyncClient, test_user_headers, db_session: AsyncSession):
    """Test listing drivers with pagination"""
    # Create test drivers
    for i in range(5):
        driver = Driver(
            tenant_id="test-tenant",
            driver_code=f"DRV-TEST-{i:03d}",
            full_name=f"Test Driver {i}",
            phone=f"+96650{i:07d}",
            license_number=f"LIC{i:06d}",
            license_type="Class C",
            license_expiry=datetime.now() + timedelta(days=365),
            vehicle_type=VehicleType.VAN,
            vehicle_plate=f"ABC-{i:04d}",
        )
        db_session.add(driver)
    
    await db_session.commit()
    
    response = await client.get(
        "/api/v1/drivers/?page=1&per_page=10",
        headers=test_user_headers,
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) >= 5


@pytest.mark.asyncio
async def test_get_driver_stats(client: AsyncClient, test_user_headers, db_session: AsyncSession):
    """Test getting driver statistics"""
    # Create test driver
    driver = Driver(
        tenant_id="test-tenant",
        driver_code="DRV-TEST-STATS",
        full_name="Test Driver Stats",
        phone="+966501111111",
        license_number="LIC999999",
        license_type="Class C",
        license_expiry=datetime.now() + timedelta(days=365),
        vehicle_type=VehicleType.VAN,
        vehicle_plate="TEST-STATS",
        total_deliveries=100,
        successful_deliveries=95,
        rating=4.8,
    )
    db_session.add(driver)
    await db_session.commit()
    await db_session.refresh(driver)
    
    response = await client.get(
        f"/api/v1/drivers/{driver.id}/stats",
        headers=test_user_headers,
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["driver_id"] == str(driver.id)
    assert "completion_rate" in data
    assert "current_rating" in data
    assert data["current_rating"] == 4.8


@pytest.mark.asyncio
async def test_update_driver_status(client: AsyncClient, test_user_headers, db_session: AsyncSession):
    """Test updating driver status"""
    # Create test driver
    driver = Driver(
        tenant_id="test-tenant",
        driver_code="DRV-TEST-STATUS",
        full_name="Test Driver Status",
        phone="+966502222222",
        license_number="LIC888888",
        license_type="Class C",
        license_expiry=datetime.now() + timedelta(days=365),
        vehicle_type=VehicleType.VAN,
        vehicle_plate="TEST-STATUS",
        status=DriverStatus.AVAILABLE,
    )
    db_session.add(driver)
    await db_session.commit()
    await db_session.refresh(driver)
    
    response = await client.post(
        f"/api/v1/drivers/{driver.id}/status?new_status=on_route",
        headers=test_user_headers,
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "on_route"


@pytest.mark.asyncio
async def test_fatigue_analysis(client: AsyncClient, test_user_headers, db_session: AsyncSession):
    """Test driver fatigue analysis"""
    # Create test driver
    driver = Driver(
        tenant_id="test-tenant",
        driver_code="DRV-TEST-FATIGUE",
        full_name="Test Driver Fatigue",
        phone="+966503333333",
        license_number="LIC777777",
        license_type="Class C",
        license_expiry=datetime.now() + timedelta(days=365),
        vehicle_type=VehicleType.VAN,
        vehicle_plate="TEST-FATIGUE",
    )
    db_session.add(driver)
    await db_session.commit()
    await db_session.refresh(driver)
    
    response = await client.get(
        f"/api/v1/drivers/{driver.id}/fatigue-analysis",
        headers=test_user_headers,
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["driver_id"] == str(driver.id)
    assert "fatigue_score" in data
    assert "recommendation" in data
    assert "break_required" in data
