# Customer Portal Documentation

## Overview
The Customer Portal is a comprehensive self-service platform designed for SSDP outlet owners to manage their orders, inventory, payments, and business operations efficiently.

## Features

### 1. Dashboard Overview
**Route:** `/customer-portal`

The dashboard provides a comprehensive overview of key business metrics:
- Total orders and order trends
- Available products in catalog
- Current balance and credit information
- Orders in transit
- Low stock alerts
- Recent orders summary
- Fast-moving items

**Key Components:**
- `DashboardOverview.tsx` - Main dashboard with statistics cards
- Real-time updates of metrics
- Visual indicators for trends (+/- percentages)

### 2. Self-Service Ordering
**Features:**
- Product search and filtering
- Real-time stock availability
- Add products to cart
- View cart summary with totals
- Confirm orders with one click

**API Endpoints:**
- `GET /api/v1/customer-portal/inventory` - Get available products
- `POST /api/v1/customer-portal/orders` - Create new order

### 3. Inventory Insights
**Features:**
- Stock level tracking
- Expiry date monitoring (60-day alerts)
- Fast-moving items identification
- Low stock alerts
- Category-based filtering
- Visual progress indicators

**Metrics:**
- Low stock count
- Expiring soon count
- Fast moving items count
- Stock velocity (fast/medium/slow)

### 4. Payment Management
**Features:**
- Current balance display
- Credit limit and available credit tracking
- Transaction history (payment, credit, refunds)
- Credit utilization percentage
- Payment due dates
- Minimum payment calculations
- Multiple payment methods
- Make payment functionality

**API Endpoints:**
- `GET /api/v1/customer-portal/payment-summary` - Get payment info
- `GET /api/v1/customer-portal/transactions` - Get transaction history

### 5. Promotions & Notifications
**Features:**

**Promotions:**
- Active promotions with discount codes
- Copy-to-clipboard functionality
- Validity dates
- Discount percentages

**Notifications:**
- Order status updates
- Promotion announcements
- Payment confirmations
- Inventory alerts
- Read/unread status
- Timestamp tracking

**API Endpoints:**
- `GET /api/v1/customer-portal/promotions` - Get active promotions
- `GET /api/v1/customer-portal/notifications` - Get user notifications

### 6. AI Recommendations
**Features:**
- Reorder suggestions based on patterns
- Bundle opportunities
- Best timing for orders
- Seasonal demand forecasts
- Estimated savings calculations
- Priority-based recommendations (high/medium/low)

**Recommendation Types:**
- Reorder suggestions
- Bundle opportunities
- Timing optimization
- Seasonal forecasting

**API Endpoints:**
- `GET /api/v1/customer-portal/recommendations` - Get AI-powered recommendations

### 7. Complaint Resolution
**Features:**
- Submit new complaints
- Track complaint status (open/in-progress/resolved)
- Priority management (low/medium/high)
- Category-based organization
- Message tracking
- Assignment tracking
- Status updates

**Complaint Categories:**
- Quality
- Delivery
- Order
- Payment
- Service
- Other

**API Endpoints:**
- `POST /api/v1/customer-portal/complaints` - Submit complaint
- `GET /api/v1/customer-portal/complaints` - Get user complaints
- `PATCH /api/v1/customer-portal/complaints/{id}` - Update complaint

## Bilingual Support (AR/EN)
All portal features fully support:
- Arabic (AR) - Right-to-left layout
- English (EN) - Left-to-right layout

Language switching is seamless and affects:
- Navigation
- All UI text
- Data labels
- Error messages
- Success messages

## Responsive Design
The portal is fully responsive and optimized for:
- Desktop (1920px+)
- Laptop (1024px - 1920px)
- Tablet (768px - 1024px)
- Mobile (320px - 768px)

### Mobile Optimizations:
- Tab navigation with icons
- Collapsible sections
- Touch-friendly buttons
- Swipeable cards
- Optimized forms

## Analytics & Feedback

### Usage Analytics
**Endpoint:** `GET /api/v1/customer-portal/usage-analytics`

Tracks:
- Total logins
- Orders placed
- Average session duration
- Most used features
- Time periods (week/month/year)

### Feedback Collection
**Endpoint:** `POST /api/v1/customer-portal/feedback`

Collects:
- Rating (1-5 stars)
- Comments
- Feature feedback

## Technical Stack

### Frontend
- **Framework:** Next.js 14
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **State Management:** Zustand
- **UI Components:** 
  - Custom components
  - Heroicons for icons
  - Radix UI for accessible components

### Backend
- **Framework:** FastAPI
- **Database:** PostgreSQL
- **Authentication:** JWT tokens
- **API Documentation:** OpenAPI/Swagger

## API Authentication
All customer portal endpoints require authentication:
```
Authorization: Bearer <token>
X-Tenant-ID: <tenant-id>
```

## Getting Started

### For Users
1. Navigate to `/customer-portal`
2. Login with your credentials
3. Access all features from the tab navigation
4. Switch language using the language toggle

### For Developers

**Running Locally:**
```bash
# Frontend
cd frontend
npm install
npm run dev

# Backend
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

**Running Tests:**
```bash
# Frontend tests
cd frontend
npm test

# Backend tests
cd backend
pytest
```

## Security Features
- Role-based access control
- Tenant isolation
- Rate limiting
- HTTPS only
- Secure payment handling
- Data encryption

## Performance
- Lazy loading of components
- Code splitting
- Image optimization
- API response caching
- Optimistic UI updates

## Future Enhancements
- [ ] Mobile app (iOS/Android)
- [ ] Push notifications
- [ ] Advanced analytics dashboard
- [ ] Export reports (PDF/Excel)
- [ ] Integration with ERP systems
- [ ] Voice ordering
- [ ] AR product preview
- [ ] Predictive inventory AI
- [ ] Multi-language support (beyond AR/EN)
- [ ] Dark mode

## Support
For technical support or feature requests:
- Email: support@brainsait.io
- Portal: `/customer-portal` → Complaints tab
- Phone: +966-XXX-XXXX

## License
© 2025 BrainSAIT Ltd. All rights reserved.
