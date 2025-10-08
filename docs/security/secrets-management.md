# Secrets Management Procedures

## Overview
This document defines the procedures for managing secrets, credentials, and sensitive configuration data across the BrainSAIT and GIVC integration, ensuring compliance with security best practices and regulatory requirements.

---

## Encryption Standards

### Data at Rest
- **Algorithm**: AES-256-GCM (Galois/Counter Mode)
- **Key Size**: 256 bits
- **Key Derivation**: PBKDF2 with SHA-256, 100,000 iterations
- **Initialization Vector**: Unique per encryption operation (96 bits for GCM)

### Data in Transit
- **Protocol**: TLS 1.3 (minimum TLS 1.2)
- **Cipher Suites**: 
  - TLS_AES_256_GCM_SHA384
  - TLS_CHACHA20_POLY1305_SHA256
  - TLS_AES_128_GCM_SHA256
- **Certificate**: Valid SSL/TLS certificates from trusted CAs
- **HSTS**: HTTP Strict Transport Security enabled (max-age=31536000)

### Database Encryption
- **PostgreSQL**: Transparent Data Encryption (TDE) enabled
- **Sensitive Columns**: Additional application-level encryption for PHI
- **Backup Encryption**: All database backups encrypted with AES-256

---

## Secret Types & Classification

### Level 1: Critical Secrets (Highest Security)
**Examples**: Database credentials, JWT signing keys, encryption keys, NPHIES certificates

**Storage**:
- **Production**: HashiCorp Vault or Cloudflare Workers Secrets
- **Development**: Local encrypted storage (.env.encrypted)
- **Never**: Git repositories, plain text files, logs

**Access Control**:
- Restricted to production services only
- Human access requires multi-factor authentication (MFA)
- Audit logging for all access attempts

**Rotation Schedule**: Every 90 days (automated)

### Level 2: Sensitive Secrets
**Examples**: API keys (Stripe, PayPal), OAuth client secrets, SMTP passwords

**Storage**:
- **Production**: Cloudflare Workers Secrets or AWS Secrets Manager
- **Development**: .env files (git-ignored)

**Access Control**:
- Service-specific access only
- Human access requires MFA for production
- Audit logging enabled

**Rotation Schedule**: Every 180 days (semi-automated)

### Level 3: Configuration Secrets
**Examples**: Redis connection strings, CDN tokens, analytics IDs

**Storage**:
- **Production**: Environment variables or configuration management
- **Development**: .env files

**Access Control**:
- Team access with role-based permissions
- Audit logging recommended

**Rotation Schedule**: Annually or on compromise

---

## Secret Storage Solutions

### 1. HashiCorp Vault (Recommended for Production)

**Setup**:
```bash
# Install Vault
brew install vault  # macOS
# or
sudo apt-get install vault  # Linux

# Start Vault server (dev mode for testing)
vault server -dev

# Set environment variable
export VAULT_ADDR='http://127.0.0.1:8200'
export VAULT_TOKEN='dev-token'
```

**Store Secrets**:
```bash
# Database credentials
vault kv put secret/brainsait/production/database \
  url="postgresql://user:pass@host:5432/db" \
  username="brainsait_user" \
  password="secure_password_here"

# JWT signing key
vault kv put secret/brainsait/production/auth \
  jwt_secret="your_jwt_secret_key_min_32_chars" \
  jwt_algorithm="HS256"

# GIVC integration
vault kv put secret/brainsait/production/givc \
  api_url="https://givc-healthcare-api.fadil.workers.dev" \
  api_key="givc_integration_key" \
  webhook_secret="webhook_secret"

# NPHIES credentials
vault kv put secret/brainsait/production/nphies \
  client_id="nphies_client_id" \
  client_secret="nphies_client_secret" \
  certificate_path="/path/to/cert.pem" \
  private_key_path="/path/to/key.pem"
```

**Retrieve Secrets** (in application):
```python
# backend/app/core/secrets.py
import hvac
import os

class VaultSecretManager:
    def __init__(self):
        self.client = hvac.Client(
            url=os.getenv('VAULT_ADDR'),
            token=os.getenv('VAULT_TOKEN')
        )
    
    def get_secret(self, path: str, key: str) -> str:
        """Retrieve secret from Vault"""
        try:
            secret = self.client.secrets.kv.v2.read_secret_version(
                path=path,
                mount_point='secret'
            )
            return secret['data']['data'][key]
        except Exception as e:
            logger.error(f"Failed to retrieve secret: {e}")
            raise
    
    def get_database_url(self) -> str:
        """Get database connection URL"""
        return self.get_secret(
            path='brainsait/production/database',
            key='url'
        )
    
    def get_jwt_secret(self) -> str:
        """Get JWT signing secret"""
        return self.get_secret(
            path='brainsait/production/auth',
            key='jwt_secret'
        )
```

### 2. Cloudflare Workers Secrets

**Setup** (for API Gateway and Workers):
```bash
# Set secret via wrangler CLI
wrangler secret put JWT_SECRET_KEY --env production
# Prompt: Enter JWT secret key (will not be displayed)

wrangler secret put DATABASE_URL --env production
wrangler secret put GIVC_API_KEY --env production
wrangler secret put NPHIES_CLIENT_SECRET --env production

# List secrets (values not shown)
wrangler secret list --env production
```

**Access in Worker**:
```javascript
// infrastructure/cloudflare/workers/src/index.js
export default {
  async fetch(request, env, ctx) {
    // Access secrets from env
    const jwtSecret = env.JWT_SECRET_KEY;
    const databaseUrl = env.DATABASE_URL;
    const givcApiKey = env.GIVC_API_KEY;
    
    // Use secrets for authentication, DB connection, etc.
    // Secrets are never logged or exposed in responses
  }
}
```

### 3. Environment Variables (Development Only)

**Setup**:
```bash
# Create .env file (never commit this)
cat > .env << 'EOF'
# Application
SECRET_KEY=your-secret-key-here-min-32-chars
DEBUG=True
ENVIRONMENT=development

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/brainsait_store
REDIS_URL=redis://localhost:6379/0

# JWT Authentication
JWT_SECRET_KEY=dev_jwt_secret_key_min_32_chars
JWT_ALGORITHM=HS256

# GIVC Integration
GIVC_API_URL=https://givc-healthcare-api.fadil.workers.dev
GIVC_API_KEY=dev_givc_api_key
GIVC_WEBHOOK_SECRET=dev_webhook_secret

# NPHIES (Development - use test environment)
NPHIES_BASE_URL=https://nphies-test.sa/api
NPHIES_CLIENT_ID=dev_client_id
NPHIES_CLIENT_SECRET=dev_client_secret

# Stripe (Test Keys)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
EOF

# Ensure .env is in .gitignore
echo ".env" >> .gitignore
echo ".env.*" >> .gitignore
echo "!.env.example" >> .gitignore
```

---

## Secret Rotation Procedures

### Automated Rotation (Critical Secrets)

**JWT Signing Key Rotation**:
```python
# scripts/rotate_jwt_secret.py
import os
import secrets
from datetime import datetime, timedelta
from app.core.secrets import VaultSecretManager

def rotate_jwt_secret():
    """Rotate JWT signing secret"""
    vault = VaultSecretManager()
    
    # Generate new secret (256-bit)
    new_secret = secrets.token_urlsafe(32)
    
    # Store new secret with version
    vault.client.secrets.kv.v2.create_or_update_secret(
        path='brainsait/production/auth',
        secret={
            'jwt_secret': new_secret,
            'jwt_secret_old': vault.get_jwt_secret(),  # Keep old for grace period
            'rotated_at': datetime.utcnow().isoformat(),
            'rotation_reason': 'scheduled'
        },
        mount_point='secret'
    )
    
    print(f"JWT secret rotated successfully at {datetime.utcnow()}")
    print("Grace period: 24 hours for old tokens to expire")

if __name__ == '__main__':
    rotate_jwt_secret()
```

**Scheduled Rotation** (cron job):
```bash
# Run every 90 days at 2 AM
0 2 */90 * * /usr/bin/python3 /path/to/scripts/rotate_jwt_secret.py
```

### Manual Rotation (On Compromise)

**Immediate Steps**:
1. **Identify Scope**: Determine which secrets were compromised
2. **Rotate Immediately**: Generate and deploy new secrets
3. **Revoke Old**: Invalidate all old credentials
4. **Audit Access**: Review access logs for unauthorized use
5. **Notify Stakeholders**: Inform security team and affected users
6. **Document Incident**: Record details for post-mortem

**Example - Database Credential Rotation**:
```bash
# 1. Create new database user
psql -U postgres -c "CREATE USER brainsait_new WITH PASSWORD 'new_secure_password';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE brainsait_store TO brainsait_new;"

# 2. Update secret in Vault
vault kv put secret/brainsait/production/database \
  url="postgresql://brainsait_new:new_secure_password@host:5432/db" \
  username="brainsait_new" \
  password="new_secure_password"

# 3. Restart services to pick up new credentials
kubectl rollout restart deployment brainsait-backend

# 4. Verify services are running with new credentials
kubectl get pods -l app=brainsait-backend

# 5. Revoke old user access
psql -U postgres -c "REVOKE ALL PRIVILEGES ON DATABASE brainsait_store FROM brainsait_old;"
psql -U postgres -c "DROP USER brainsait_old;"
```

---

## Access Control & Audit Logging

### Role-Based Access Control (RBAC)

**Roles**:
```yaml
# vault-policies/brainsait-admin.hcl
path "secret/data/brainsait/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

# vault-policies/brainsait-backend.hcl
path "secret/data/brainsait/production/database" {
  capabilities = ["read"]
}
path "secret/data/brainsait/production/auth" {
  capabilities = ["read"]
}
path "secret/data/brainsait/production/givc" {
  capabilities = ["read"]
}

# vault-policies/brainsait-developer.hcl
path "secret/data/brainsait/development/*" {
  capabilities = ["read", "list"]
}
```

**Apply Policies**:
```bash
vault policy write brainsait-admin vault-policies/brainsait-admin.hcl
vault policy write brainsait-backend vault-policies/brainsait-backend.hcl
vault policy write brainsait-developer vault-policies/brainsait-developer.hcl

# Create token with policy
vault token create -policy="brainsait-backend" -ttl=24h
```

### Audit Logging

**Enable Vault Audit Logging**:
```bash
# Enable file audit log
vault audit enable file file_path=/var/log/vault/audit.log

# Enable syslog audit log
vault audit enable syslog
```

**Audit Log Entry Example**:
```json
{
  "time": "2025-01-09T12:00:00Z",
  "type": "response",
  "auth": {
    "client_token": "hmac-sha256:token_hash",
    "accessor": "hmac-sha256:accessor_hash",
    "display_name": "brainsait-backend",
    "policies": ["brainsait-backend"],
    "token_policies": ["brainsait-backend"]
  },
  "request": {
    "id": "request_uuid",
    "operation": "read",
    "path": "secret/data/brainsait/production/auth",
    "remote_address": "10.0.1.100"
  },
  "response": {
    "data": {
      "jwt_secret": "hmac-sha256:secret_hash"
    }
  }
}
```

**Application-Level Audit**:
```python
# backend/app/core/audit.py
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

class SecretAccessAudit:
    @staticmethod
    async def log_secret_access(
        secret_name: str,
        actor_id: str,
        actor_type: str,
        action: str,
        status: str,
        ip_address: Optional[str] = None
    ):
        """Log secret access to audit table"""
        audit_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': 'secret.access',
            'secret_name': secret_name,
            'actor_id': actor_id,
            'actor_type': actor_type,  # 'user', 'service', 'system'
            'action': action,  # 'read', 'write', 'delete'
            'status': status,  # 'success', 'failure'
            'ip_address': ip_address
        }
        
        # Log to database
        # INSERT INTO audit_logs (...) VALUES (...)
        
        # Also log to structured logger
        logger.info(f"Secret access: {audit_entry}")
```

---

## Secret Synchronization (BrainSAIT ↔ GIVC)

### Shared Secrets

**Critical Shared Secrets**:
1. **JWT_SECRET_KEY**: Must be identical across BrainSAIT Store and GIVC
2. **NPHIES_CLIENT_SECRET**: Shared for healthcare integration
3. **WEBHOOK_SECRET**: For secure webhook communication
4. **DATABASE_ENCRYPTION_KEY**: If using shared database

**Synchronization Procedure**:
```bash
#!/bin/bash
# scripts/sync_shared_secrets.sh

# Sync JWT secret from BrainSAIT Vault to GIVC Workers
JWT_SECRET=$(vault kv get -field=jwt_secret secret/brainsait/production/auth)
wrangler secret put JWT_SECRET_KEY --env production <<< "$JWT_SECRET"

# Sync NPHIES credentials
NPHIES_CLIENT_SECRET=$(vault kv get -field=client_secret secret/brainsait/production/nphies)
wrangler secret put NPHIES_CLIENT_SECRET --env production <<< "$NPHIES_CLIENT_SECRET"

# Sync webhook secret
WEBHOOK_SECRET=$(vault kv get -field=webhook_secret secret/brainsait/production/givc)
wrangler secret put BRAINSAIT_WEBHOOK_SECRET --env production <<< "$WEBHOOK_SECRET"

echo "Shared secrets synchronized successfully"
```

**Verification**:
```python
# Test JWT token validation across services
import jwt

# Token created by BrainSAIT Store
token_brainsait = jwt.encode(
    {'sub': 'user_123', 'aud': ['brainsait-store', 'givc-api']},
    secret_key_brainsait,
    algorithm='HS256'
)

# Validate token in GIVC API (must use same secret)
try:
    payload = jwt.decode(
        token_brainsait,
        secret_key_givc,  # Must equal secret_key_brainsait
        algorithms=['HS256'],
        audience='givc-api'
    )
    print("Token validated successfully - secrets are in sync")
except jwt.InvalidSignatureError:
    print("ERROR: Secrets are out of sync!")
```

---

## Compliance & Best Practices

### HIPAA Compliance
- **Access Controls**: Implement unique user IDs and automatic logoff
- **Audit Logging**: Track all PHI access with date, time, user
- **Encryption**: PHI encrypted at rest (AES-256) and in transit (TLS 1.3)
- **Integrity Controls**: Ensure PHI is not improperly altered or destroyed

### PCI DSS Compliance (Payment Data)
- **Never Store**: CVV/CVC codes
- **Tokenization**: Use Stripe/PayPal tokens instead of raw card data
- **Encryption**: All payment data encrypted with strong cryptography
- **Access Logging**: Monitor and log all access to cardholder data

### Saudi Compliance
- **ZATCA**: Secure storage of e-invoicing private keys
- **NPHIES**: Protect healthcare provider credentials and certificates
- **Data Residency**: Ensure secrets for Saudi services stored in-region

### General Best Practices
1. **Principle of Least Privilege**: Grant minimal necessary access
2. **Never Hard-Code**: No secrets in source code, ever
3. **Git-Ignore**: Ensure .env files never committed
4. **Separate Environments**: Different secrets for dev/staging/production
5. **Regular Rotation**: Automate rotation for critical secrets
6. **MFA Required**: Multi-factor auth for human access to secrets
7. **Secure Transmission**: Only transmit secrets over encrypted channels
8. **Delete Unused**: Remove old secrets after grace period
9. **Document Everything**: Maintain this document and procedures
10. **Incident Response**: Have plan for secret compromise

---

## Emergency Procedures

### Secret Compromise Detected

**Immediate Actions** (within 1 hour):
```bash
# 1. Revoke compromised secret immediately
vault kv metadata delete secret/brainsait/production/compromised_path

# 2. Generate and deploy new secret
vault kv put secret/brainsait/production/compromised_path \
  new_secret="newly_generated_secure_value"

# 3. Restart affected services
kubectl rollout restart deployment brainsait-backend
wrangler deploy --env production

# 4. Invalidate all existing sessions (if auth secret compromised)
redis-cli FLUSHDB  # Caution: This clears all sessions

# 5. Notify security team
./scripts/send_security_alert.sh "Secret compromise detected: compromised_path"
```

**Follow-Up Actions** (within 24 hours):
1. Conduct full security audit of access logs
2. Identify unauthorized access attempts
3. Assess data breach scope
4. Notify affected parties if required by law
5. Document incident and lessons learned
6. Update security procedures if needed

### Secret Rotation Failure

**Troubleshooting**:
```bash
# Check Vault status
vault status

# Verify secret exists
vault kv get secret/brainsait/production/auth

# Test application can read secret
./scripts/test_secret_access.sh

# Check service logs for errors
kubectl logs -l app=brainsait-backend --tail=100

# Rollback to previous secret version if needed
vault kv rollback -version=1 secret/brainsait/production/auth
```

---

## Monitoring & Alerts

### Secret Access Monitoring

**Alerts to Configure**:
1. **Unusual Access Patterns**: Access from unexpected IPs or services
2. **Failed Access Attempts**: Multiple failed attempts (>5 in 5 minutes)
3. **Secret Rotation Overdue**: Alert 1 week before rotation due
4. **Secret Read by Human**: Any human access to production secrets
5. **Vault Seal Event**: Vault becomes sealed (emergency)

**Monitoring Dashboard**:
```python
# Example metrics to track
- secret_access_count (by service, secret_name)
- secret_rotation_age_days (by secret_name)
- failed_access_attempts_count (by ip_address)
- secrets_approaching_rotation (count)
- vault_health_status (healthy/sealed/uninitialized)
```

---

## Secrets Inventory

### Production Secrets Checklist

| Secret Name | Type | Storage | Rotation | Last Rotated | Next Rotation |
|-------------|------|---------|----------|--------------|---------------|
| DATABASE_URL | Critical | Vault | 90 days | 2024-10-15 | 2025-01-13 |
| JWT_SECRET_KEY | Critical | Vault + Workers | 90 days | 2024-11-01 | 2025-01-30 |
| REDIS_URL | Critical | Vault | 90 days | 2024-10-15 | 2025-01-13 |
| GIVC_API_KEY | Sensitive | Vault + Workers | 180 days | 2024-07-01 | 2025-01-01 |
| NPHIES_CLIENT_SECRET | Critical | Vault | 90 days | 2024-12-01 | 2025-03-01 |
| STRIPE_SECRET_KEY | Sensitive | Vault | 180 days | 2024-06-15 | 2024-12-15 |
| PAYPAL_SECRET | Sensitive | Vault | 180 days | 2024-06-15 | 2024-12-15 |
| SMTP_PASSWORD | Configuration | Vault | 365 days | 2024-01-15 | 2025-01-15 |

**Verification Command**:
```bash
# Generate secrets inventory report
./scripts/secrets_inventory.sh > secrets_inventory_$(date +%Y%m%d).txt
```

---

## Training & Access Request

### Developer Onboarding

**Required Training**:
1. Secrets management overview (this document)
2. Hands-on with development environment secrets
3. Security best practices quiz (pass required)
4. HIPAA and PCI DSS basics (for healthcare/payment work)

### Access Request Process

**To Request Secret Access**:
1. Submit ticket to DevOps team with justification
2. Manager approval required
3. Security team review for production access
4. Access granted with MFA enabled
5. Access logged and reviewed quarterly

**Access Review Schedule**:
- **Weekly**: Automated review of access logs
- **Monthly**: Human review of unusual patterns
- **Quarterly**: Full access rights audit
- **Annually**: Policy and procedure review

---

## Contact Information

**Security Team**: security@brainsait.com  
**DevOps Team**: devops@brainsait.com  
**On-Call Security**: +966-xxx-xxx-xxxx  
**Incident Hotline**: +966-xxx-xxx-xxxx (24/7)

---

**Document Version**: 1.0  
**Last Updated**: 2025-01-09  
**Document Owner**: Security Team  
**Review Frequency**: Quarterly  
**Next Review**: 2025-04-09
