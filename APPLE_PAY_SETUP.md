# Apple Pay Domain Association Setup Guide

## Overview
This guide explains how to set up Apple Pay domain verification for `store.brainsait.io`

## Files Created
- ✅ **Domain Association File**: `/frontend/public/.well-known/apple-developer-merchantid-domain-association.txt`
- ✅ **Next.js Configuration**: Updated to serve the association file correctly
- ✅ **Environment Variables**: Updated with correct domain

## Domain Verification

### 1. File Location
The Apple Pay domain association file is located at:
```
/frontend/public/.well-known/apple-developer-merchantid-domain-association.txt
```

### 2. URL Accessibility
After deployment, the file must be accessible at:
```
https://store.brainsait.io/.well-known/apple-developer-merchantid-domain-association.txt
```

### 3. File Content
The file contains your Apple Pay merchant certificate data for domain `store.brainsait.io` with:
- **Team ID**: ZSVA8A67UW
- **Domain**: store.brainsait.io
- **Date Created**: 2025-08-14
- **Version**: 1

## Deployment Instructions

### For Vercel Deployment:
1. **Upload the file**: The file is already in `/public/.well-known/` directory
2. **Deploy**: Run `vercel --prod`
3. **Verify**: Check `https://store.brainsait.io/.well-known/apple-developer-merchantid-domain-association.txt`

### For Cloudflare Pages:
1. **Build and Deploy**: The file will be served from the public directory
2. **Verify Headers**: Ensure proper Content-Type headers (configured in next.config.js)

### For Custom Server:
Ensure your server serves the file with:
- **Content-Type**: `text/plain`
- **Status Code**: `200 OK`
- **No redirects**: Direct access required

## Verification Steps

1. **Test URL Access**:
   ```bash
   curl -I https://store.brainsait.io/.well-known/apple-developer-merchantid-domain-association.txt
   ```

2. **Expected Response**:
   ```
   HTTP/2 200
   content-type: text/plain
   cache-control: public, max-age=86400
   ```

3. **Apple Pay Configuration**:
   - Merchant ID: `merchant.io.brainsait.store`
   - Domain: `store.brainsait.io`
   - Display Name: `BrainSAIT Solutions`

## Environment Variables

### Frontend (.env.local):
```env
NEXT_PUBLIC_APPLE_PAY_MERCHANT_ID=merchant.io.brainsait.store
NEXT_PUBLIC_APPLE_PAY_DISPLAY_NAME=BrainSAIT Solutions
NEXT_PUBLIC_APPLE_PAY_DOMAIN=store.brainsait.io
```

### Backend (.env):
```env
APPLE_PAY_MERCHANT_ID=merchant.io.brainsait.store
APPLE_PAY_DOMAIN=store.brainsait.io
```

## Troubleshooting

### Common Issues:

1. **404 Error**:
   - Ensure the file is in `/public/.well-known/` directory
   - Check Next.js rewrites configuration

2. **Wrong Content-Type**:
   - Verify Next.js headers configuration
   - Check server configuration

3. **File Not Found**:
   - Ensure deployment includes static files
   - Check build output

### Apple Pay Domain Verification:
1. **Apple Developer Console**: Register the domain in your Apple Pay merchant configuration
2. **Certificate**: Ensure the certificate matches your merchant ID
3. **HTTPS**: Domain must be served over HTTPS

## Security Notes

- ✅ File contains only Apple's public certificate data
- ✅ No sensitive information exposed
- ✅ Standard Apple Pay domain verification process
- ✅ Cached for 24 hours for performance

## Next Steps

1. **Deploy** the application to `store.brainsait.io`
2. **Verify** the URL is accessible
3. **Configure** Apple Pay in Apple Developer Console
4. **Test** Apple Pay integration

## Support

For Apple Pay specific issues:
- [Apple Pay Developer Documentation](https://developer.apple.com/apple-pay/)
- [Domain Verification Guide](https://developer.apple.com/documentation/apple_pay_on_the_web/setting_up_apple_pay_on_the_web)

For BrainSAIT specific issues:
- Check payment service configuration
- Verify environment variables
- Test with other payment methods first