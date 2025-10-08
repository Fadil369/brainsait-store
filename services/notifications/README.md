# Notifications Service

Multi-channel notification service for email, SMS, and push notifications.

## Features

- Email notifications (transactional & marketing)
- SMS notifications (OTP, alerts)
- Push notifications (iOS/Android)
- Bilingual templates (Arabic/English)
- Notification scheduling
- Delivery tracking and analytics

## API Endpoints

### Email
- `POST /api/notifications/email` - Send email
- `POST /api/notifications/email/bulk` - Send bulk emails

### SMS
- `POST /api/notifications/sms` - Send SMS
- `POST /api/notifications/sms/otp` - Send OTP

### Push
- `POST /api/notifications/push` - Send push notification
- `POST /api/notifications/push/topic` - Send to topic subscribers

### Templates
- `GET /api/templates` - List notification templates
- `POST /api/templates` - Create template

## Channels

- **Email**: SendGrid/AWS SES
- **SMS**: Twilio/STC
- **Push**: Firebase Cloud Messaging (FCM)

## Configuration

Environment variables:
- `DATABASE_URL` - PostgreSQL connection string
- `PORT` - Service port (default: 3005)
- `SENDGRID_API_KEY` - SendGrid API key
- `TWILIO_ACCOUNT_SID` - Twilio account SID
- `TWILIO_AUTH_TOKEN` - Twilio auth token
- `FCM_PROJECT_ID` - Firebase project ID

## Development

```bash
npm install
npm run dev
```
