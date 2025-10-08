# Driver & Logistics Empowerment Features Guide

## Overview

The SSDP (Saudi Smart Delivery Platform) Driver & Logistics features provide comprehensive tools for delivery drivers, fleet managers, and logistics coordinators. The system includes AI-powered route optimization, proof of delivery capture, incident reporting, and safety management.

## Features

### 1. Driver Management

#### Driver Registration
Register new drivers with comprehensive profile information:

```bash
POST /api/v1/drivers/
```

**Request Body:**
```json
{
  "full_name": "Ahmed Al-Saud",
  "phone": "+966501234567",
  "email": "ahmed@example.com",
  "license_number": "LIC123456",
  "license_type": "Class C",
  "license_expiry": "2025-12-31T23:59:59Z",
  "vehicle_type": "van",
  "vehicle_plate": "ABC-1234",
  "vehicle_capacity_kg": 1000.0,
  "vehicle_capacity_m3": 10.0,
  "hourly_rate": 50.0,
  "per_delivery_rate": 15.0,
  "emergency_contact": {
    "name": "Mohammad Al-Saud",
    "phone": "+966507654321",
    "relationship": "brother"
  }
}
```

#### Driver Statistics
Get comprehensive driver performance metrics:

```bash
GET /api/v1/drivers/{driver_id}/stats
```

**Response:**
```json
{
  "driver_id": "uuid",
  "today_deliveries": 12,
  "week_deliveries": 68,
  "month_deliveries": 287,
  "today_earnings": 450.0,
  "week_earnings": 3200.0,
  "month_earnings": 12800.0,
  "current_rating": 4.8,
  "active_routes": 1,
  "completion_rate": 96.5
}
```

### 2. AI-Powered Route Optimization

#### Multi-Constraint Route Optimization
Optimize delivery routes using AI algorithms that consider:
- Distance minimization
- Time windows
- Vehicle capacity (weight and volume)
- Priority deliveries
- Traffic patterns
- Fuel efficiency

```bash
POST /api/v1/logistics/routes/optimize
```

**Request Body:**
```json
{
  "driver_id": "uuid",
  "delivery_ids": ["uuid1", "uuid2", "uuid3"],
  "start_location": {
    "lat": 24.7136,
    "lng": 46.6753,
    "address": "Main Warehouse, Riyadh"
  },
  "constraints": {
    "max_weight_kg": 1000.0,
    "max_volume_m3": 10.0,
    "time_window_start": "08:00:00",
    "time_window_end": "18:00:00",
    "priority_delivery_ids": ["uuid1"],
    "avoid_tolls": false,
    "avoid_highways": false
  },
  "optimization_algorithm": "ai_multi_constraint"
}
```

**Response:**
```json
{
  "route_id": "uuid",
  "optimized_waypoints": [
    {
      "id": "uuid",
      "lat": 24.7136,
      "lng": 46.6753,
      "address": "Warehouse",
      "type": "start"
    },
    {
      "id": "delivery-uuid-1",
      "lat": 24.7500,
      "lng": 46.7000,
      "address": "Customer 1",
      "type": "delivery",
      "priority": 1
    }
  ],
  "total_distance_km": 45.8,
  "estimated_duration_min": 180,
  "optimization_score": 94.5,
  "fuel_efficiency": 3.66,
  "carbon_footprint_kg": 5.49
}
```

**Optimization Algorithm Details:**
- Uses nearest neighbor heuristic with time window constraints
- Priority deliveries are weighted to appear earlier in sequence
- Considers vehicle capacity constraints
- Estimates fuel consumption and carbon footprint
- Provides optimization score (0-100)

### 3. Proof of Delivery (POD)

#### Capture POD with Multiple Methods
Support for signature, photo, and GPS verification:

```bash
PUT /api/v1/logistics/deliveries/{delivery_id}
```

**Request Body:**
```json
{
  "status": "delivered",
  "pod": {
    "signature": "base64_encoded_signature_image",
    "photo": "https://cdn.example.com/delivery-proof.jpg",
    "gps_location": {
      "lat": 24.7500,
      "lng": 46.7000,
      "accuracy": 5.0
    },
    "recipient_name": "Mohammad Ali",
    "notes": "Delivered to reception desk, signed by security"
  }
}
```

**POD Features:**
- Digital signature capture
- Photo documentation
- GPS location verification with accuracy tracking
- Recipient name capture
- Delivery notes
- Automatic timestamp recording

### 4. Incident Reporting with AI Suggestions

#### Report Incidents
Report incidents with AI-powered categorization and action suggestions:

```bash
POST /api/v1/logistics/incidents
```

**Request Body:**
```json
{
  "incident_type": "traffic_delay",
  "severity": "medium",
  "title": "Heavy traffic on Highway 65",
  "description": "Unexpected traffic congestion due to accident ahead. Estimated 30 minutes delay.",
  "location": {
    "lat": 24.7200,
    "lng": 46.6800,
    "address": "Highway 65, Riyadh"
  },
  "route_id": "uuid",
  "estimated_delay_min": 30,
  "photos": [
    "https://cdn.example.com/incident-photo-1.jpg"
  ]
}
```

**Response with AI Suggestions:**
```json
{
  "id": "uuid",
  "incident_number": "INC-20240115-ABC123",
  "incident_type": "traffic_delay",
  "severity": "medium",
  "title": "Heavy traffic on Highway 65",
  "ai_suggested_category": "Delivery Impact",
  "ai_suggested_actions": [
    "Update ETA for affected deliveries",
    "Find alternate route if possible",
    "Notify customers of delay",
    "Document traffic conditions"
  ],
  "ai_confidence_score": 0.88,
  "occurred_at": "2024-01-15T10:30:00Z"
}
```

**Incident Types:**
- `accident` - Vehicle accident
- `vehicle_breakdown` - Mechanical failure
- `traffic_delay` - Traffic congestion
- `weather_delay` - Weather-related delays
- `customer_unavailable` - Customer not present
- `package_damage` - Package damaged
- `security_issue` - Security concern
- `other` - Other incidents

**Severity Levels:**
- `low` - Minor issue, minimal impact
- `medium` - Moderate issue, some delay expected
- `high` - Significant issue, major delays
- `critical` - Emergency situation, immediate action required

### 5. Load Planning with 3D Optimization

#### Create Optimized Load Plans
Generate 3D load plans for optimal cargo placement:

```bash
POST /api/v1/logistics/load-plans
```

**Request Body:**
```json
{
  "route_id": "uuid",
  "vehicle_length_m": 3.0,
  "vehicle_width_m": 2.0,
  "vehicle_height_m": 2.5,
  "max_weight_kg": 1000.0,
  "items": [
    {
      "item_id": "ITEM-001",
      "delivery_id": "uuid",
      "length_m": 0.5,
      "width_m": 0.4,
      "height_m": 0.3,
      "weight_kg": 25.0,
      "fragile": false,
      "stackable": true,
      "priority": 1
    },
    {
      "item_id": "ITEM-002",
      "length_m": 0.6,
      "width_m": 0.5,
      "height_m": 0.4,
      "weight_kg": 30.0,
      "fragile": true,
      "stackable": false,
      "priority": 2
    }
  ]
}
```

**Response:**
```json
{
  "id": "uuid",
  "route_id": "uuid",
  "total_weight_kg": 55.0,
  "weight_utilization_pct": 5.5,
  "volume_utilization_pct": 1.2,
  "optimization_score": 92.5,
  "balance_score": 85.0,
  "accessibility_score": 90.0,
  "loading_sequence": [
    {
      "item_id": "ITEM-002",
      "position": 1,
      "instructions": "Load first (fragile)"
    },
    {
      "item_id": "ITEM-001",
      "position": 2,
      "instructions": "Standard loading"
    }
  ]
}
```

**Load Planning Features:**
- 3D space optimization
- Weight distribution balancing
- Fragile item protection
- Delivery sequence optimization
- Loading order recommendations
- Utilization percentage calculation

### 6. Safety & Fatigue Management

#### Fatigue Analysis
Monitor driver fatigue and get safety recommendations:

```bash
GET /api/v1/drivers/{driver_id}/fatigue-analysis
```

**Response:**
```json
{
  "driver_id": "uuid",
  "hours_driven_today": 6.5,
  "continuous_drive_time_min": 180,
  "fatigue_score": 65.5,
  "recommendation": "WARNING: Driver should plan for a break soon",
  "break_required": true,
  "estimated_break_time_min": 15
}
```

**Fatigue Score Interpretation:**
- **0-50**: Safe driving conditions, no break required
- **51-70**: Moderate fatigue, break recommended soon
- **71-100**: High fatigue, immediate break required

#### Safety Alerts
Create and manage safety alerts:

```bash
POST /api/v1/logistics/safety-alerts
```

**Request Body:**
```json
{
  "alert_type": "fatigue",
  "severity": "medium",
  "message": "Driver has been driving continuously for 3 hours. Break recommended.",
  "location": {
    "lat": 24.7200,
    "lng": 46.6800
  },
  "metadata": {
    "continuous_drive_time": 180,
    "last_break": "2024-01-15T08:00:00Z"
  }
}
```

### 7. Earnings Tracking

#### Get Driver Earnings
Track earnings with detailed breakdown:

```bash
GET /api/v1/drivers/{driver_id}/earnings?start_date=2024-01-01&end_date=2024-01-31
```

**Response:**
```json
{
  "driver_id": "uuid",
  "period_start": "2024-01-01T00:00:00Z",
  "period_end": "2024-01-31T23:59:59Z",
  "total_earnings": 12800.0,
  "total_bonuses": 1500.0,
  "total_deductions": 200.0,
  "net_earnings": 14100.0,
  "deliveries_completed": 287,
  "hours_worked": 180.5,
  "average_rating": 4.8,
  "breakdown": [
    {
      "date": "2024-01-15T00:00:00Z",
      "base_amount": 400.0,
      "bonus_amount": 50.0,
      "deduction_amount": 0.0,
      "total_amount": 450.0,
      "hours_worked": 8.0,
      "deliveries_completed": 12,
      "distance_traveled_km": 85.5,
      "on_time_bonus": 30.0,
      "rating_bonus": 10.0,
      "efficiency_bonus": 10.0
    }
  ]
}
```

**Bonus Types:**
- **On-Time Bonus**: Awarded for completing deliveries within time windows
- **Rating Bonus**: Based on customer ratings
- **Efficiency Bonus**: For optimal route completion

## Driver Dashboard

### Accessing the Dashboard
Navigate to: `/dashboard/driver`

### Dashboard Features

#### 1. Performance Metrics
- Today's deliveries count
- Today's earnings
- Current rating
- Completion rate

#### 2. Active Routes
- View in-progress routes
- Track completion progress
- See remaining stops

#### 3. Safety Alerts
- View unacknowledged alerts
- Alert severity indicators
- Quick acknowledge actions

#### 4. Monthly Overview
- Total monthly deliveries
- Total monthly earnings
- Active routes count

#### 5. Quick Actions
- View routes
- Report incidents
- View profile

## API Authentication

All API endpoints require authentication using Bearer tokens:

```bash
Authorization: Bearer <your_access_token>
```

Multi-tenant support via tenant ID header:

```bash
X-Tenant-ID: <your_tenant_id>
```

## Best Practices

### Route Optimization
1. **Plan ahead**: Optimize routes at the start of the day
2. **Consider traffic**: Use time window constraints for peak hours
3. **Prioritize urgent deliveries**: Mark priority deliveries in constraints
4. **Monitor fuel efficiency**: Track optimization scores

### Proof of Delivery
1. **Capture clear photos**: Ensure good lighting
2. **Verify GPS accuracy**: Check accuracy field (< 10m recommended)
3. **Get recipient name**: Always record who received the package
4. **Add notes**: Document special circumstances

### Incident Reporting
1. **Report immediately**: Don't delay incident reporting
2. **Be specific**: Provide detailed descriptions
3. **Take photos**: Visual documentation is crucial
4. **Follow AI suggestions**: Use AI-recommended actions

### Safety Management
1. **Monitor fatigue**: Check fatigue analysis regularly
2. **Take breaks**: Follow break recommendations
3. **Acknowledge alerts**: Respond to safety alerts promptly
4. **Update status**: Keep driver status current

## Troubleshooting

### Common Issues

**Issue**: Route optimization fails
- **Solution**: Check that all delivery IDs are valid and belong to the tenant
- Verify vehicle capacity constraints are reasonable

**Issue**: POD upload fails
- **Solution**: Ensure photo URLs are accessible or base64 data is valid
- Check GPS location has valid lat/lng values

**Issue**: Earnings not updating
- **Solution**: Verify deliveries are marked as "delivered" status
- Check that route is completed

## Support

For technical support or questions:
- Email: support@brainsait.com
- Documentation: https://docs.brainsait.com
- API Reference: https://api.brainsait.com/docs

## Compliance

### Saudi Vision 2030 Alignment
The SSDP logistics features support Saudi Vision 2030 goals:
- Digital transformation of logistics sector
- Environmental sustainability through route optimization
- Safety and compliance monitoring
- Economic efficiency improvements

### Data Privacy
All driver data is handled in compliance with:
- Saudi Personal Data Protection Law (PDPL)
- ISO 27001 standards
- GDPR principles where applicable

## Future Enhancements

### Planned Features
- Real-time traffic integration
- Predictive maintenance alerts
- Advanced 3D load visualization
- Voice-activated incident reporting
- Integration with Saudi Post
- Electric vehicle route optimization
- Customer communication portal
- Multi-language support (Arabic/English)

---

**Version**: 1.0.0  
**Last Updated**: January 2024  
**Maintained by**: BrainSAIT Development Team
