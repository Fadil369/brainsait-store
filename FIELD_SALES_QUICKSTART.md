# Field Sales Features - Quick Start Guide

## 🚀 Access Field Sales Features

### URLs
- **Dashboard**: `/field-sales/dashboard`
- **Check-In**: `/field-sales/check-in`
- **Voice Order**: `/field-sales/voice-order`
- **Credit Request**: `/field-sales/credit`
- **Leaderboard**: `/field-sales/leaderboard`

### Demo Mode
Currently using demo rep ID: `demo-rep-id`

To use with real authentication:
1. Update the `repId` in each page component
2. Get rep ID from authentication context
3. Link to user's sales rep record

## ✨ Key Features

### 1. Mobile Check-In 📍
- GPS location tracking
- Camera for photo evidence
- Offline support with IndexedDB
- Geofence validation

**Required Permissions:**
- Location access
- Camera access

### 2. Voice Orders 🎤
- Bilingual (Arabic/English)
- Offline recording
- Speech-to-text integration point
- Automatic order processing

**Required Permissions:**
- Microphone access

### 3. Credit Requests 💳
- AI-powered risk assessment
- Instant scoring (0-100)
- Risk factor analysis
- Approval workflow

### 4. Gamification 🏆
- Points and levels
- Badges and achievements
- Leaderboards (daily/weekly/monthly)
- Territory rankings

### 5. Offline Support 📱
- IndexedDB storage
- Automatic background sync
- Network status detection
- Batch operations

## 🔧 Setup Instructions

### Backend

```bash
cd backend

# Run database migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload

# API will be available at http://localhost:8000
# API docs at http://localhost:8000/api/docs
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# App will be available at http://localhost:3000
```

### Environment Variables

**Backend (.env):**
```env
DATABASE_URL=postgresql://user:pass@localhost/brainsait
```

**Frontend (.env.local):**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📱 Mobile Testing

### Test on Device
1. Ensure backend is accessible from mobile device (use ngrok or similar)
2. Update `NEXT_PUBLIC_API_URL` to public URL
3. Access from mobile browser
4. Grant permissions when prompted

### Chrome DevTools
1. Open DevTools (F12)
2. Toggle device toolbar (Ctrl+Shift+M)
3. Select mobile device
4. Test GPS/Camera via DevTools sensors

## 🔌 Integration Points

### Speech Recognition
File: `backend/app/services/field_sales.py:process_voice_order()`

Integrate with:
- Google Cloud Speech-to-Text
- Azure Speech Services
- Amazon Transcribe

### AR Catalog
Endpoint: `GET /api/v1/field-sales/ar-catalog/products`

Ready for:
- ARKit (iOS)
- ARCore (Android)
- WebXR

### AI Credit Scoring
File: `backend/app/services/field_sales.py:_assess_credit_risk()`

Integrate with:
- TensorFlow models
- Scikit-learn
- Cloud ML services

## 🧪 Testing Checklist

- [ ] Check-in with location enabled
- [ ] Check-in with location denied
- [ ] Check-in offline mode
- [ ] Photo capture
- [ ] Voice recording (Arabic)
- [ ] Voice recording (English)
- [ ] Credit request submission
- [ ] AI assessment display
- [ ] Leaderboard loading
- [ ] Offline data sync
- [ ] Dashboard metrics

## 📚 Documentation

Full documentation: `docs/FIELD_SALES_README.md`

## 🐛 Troubleshooting

### Location Not Working
- Check browser permissions
- Ensure HTTPS in production
- Verify geolocation API support

### Camera Not Working
- Check browser permissions
- Ensure HTTPS in production
- Try different browser

### Voice Recording Issues
- Check microphone permissions
- Test in different browsers
- Verify MediaRecorder support

### Offline Sync Not Working
- Clear IndexedDB data
- Check service worker status
- Verify network status detection

## 🎯 Next Steps

1. **Add Authentication**: Link to actual user/rep accounts
2. **Deploy Backend**: Set up production server
3. **Configure Speech API**: Add speech-to-text service
4. **Enable AR**: Implement AR model viewer
5. **Train AI Model**: Deploy credit scoring model
6. **Add Push Notifications**: Alert reps of important events
7. **Create Admin Panel**: Manage reps, territories, targets

## 📞 Support

For issues or questions:
- Check API docs: http://localhost:8000/api/docs
- Review full documentation: `docs/FIELD_SALES_README.md`
- Contact development team

---
**Version**: 1.0.0
**Last Updated**: 2024
