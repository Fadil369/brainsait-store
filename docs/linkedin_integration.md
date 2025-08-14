# LinkedIn Integration (Lead Sync + Apply Connect)

This guide explains how to enable LinkedIn integrations in BrainSAIT B2B using direct HTTP calls (httpx) and a Cloudflare Worker for secure webhooks.

## Prerequisites

- LinkedIn developer app verified and granted access to the required products:
  - Lead Sync API: `r_marketing_leadgen_automation` (requires program approval)
  - Advertising APIs: `r_ads`, `rw_ads` (as needed)
  - Sign In w/ LinkedIn OpenID Connect: `openid`, `profile`, `email`
- Appropriate Ad Account or Organization roles, otherwise LinkedIn returns 403.
- Cloudflare account with Workers, KV, R2, and Queues.

## Backend setup

1. Configure environment variables (example):

```bash
LINKEDIN_CLIENT_ID=...
LINKEDIN_CLIENT_SECRET=...
LINKEDIN_REDIRECT_URI=https://api.brainsait.com/api/v1/integrations/linkedin/oauth/callback
# Optional version; see deprecation notes and versioning in docs
LINKEDIN_API_VERSION=202501
```

1. Install dependencies:

```bash
pip install -r backend/requirements.txt
```

1. Endpoints:

- GET `/api/v1/integrations/linkedin/oauth/url?scopes=r_liteprofile,r_ads,r_marketing_leadgen_automation`
- POST `/api/v1/integrations/linkedin/oauth/callback` with `{ "code": "..." }`
- POST `/api/v1/integrations/linkedin/oauth/refresh` with `{ "refresh_token": "..." }`
- POST `/api/v1/integrations/linkedin/lead-forms` with `{ "access_token": "..." }`
- POST `/api/v1/integrations/linkedin/lead-form-responses` with filters, e.g. `{ "access_token": "...", "lead_gen_form_urn": "urn:li:leadGenForm:...", "created_after": 1710000000000 }`
- POST `/api/v1/integrations/linkedin/webhooks/lead-notifications` (receiver, called by Worker)

## Cloudflare Worker

- Source: `infrastructure/cloudflare/workers/src/index.js`
- Config: `infrastructure/cloudflare/workers/wrangler.toml`
- Secrets (set via dashboard or CLI):
  - `LINKEDIN_WEBHOOK_SECRET` (or rely on `LINKEDIN_CLIENT_SECRET`)

Deploy (staging):

```bash
cd infrastructure/cloudflare/workers
wrangler deploy --env staging
```

## Security

- Webhook signed using HMAC SHA-256. Worker validates before forwarding.
- Do not log raw PII. Store to R2 if required and purge per retention policy.
- Use HTTPS end-to-end; avoid storing tokens in plaintext.

## Notes from LinkedIn docs

- Some older Marketing API versions are sunset. Use current version strings.
- Lead Sync requires program approval and specific roles (403 without them).
- Lead forms endpoints and payloads can be versioned; include `version_string` when required.

## Next steps

- Persist 3-legged tokens per tenant (DB + refresh) and rotate with `/oauth/refresh`.
- Confirm Lead Sync access and iterate on lead responses filters and pagination.
- Add Apply Connect flows (provisionedApplications, jobs sync) if needed.
