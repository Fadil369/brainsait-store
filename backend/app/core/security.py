"""
Enhanced security utilities for authentication, validation, and protection
"""

import hashlib
import hmac
import re
import secrets
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

import bcrypt
from fastapi import HTTPException, Request, status
from jose import jwt
from passlib.context import CryptContext

from .config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Common security patterns
SUSPICIOUS_PATTERNS = [
    r"<script[^>]*>",
    r"javascript:",
    r"vbscript:",
    r"onload\s*=",
    r"onerror\s*=",
    r"onclick\s*=",
    r"<iframe[^>]*>",
    r"<object[^>]*>",
    r"<embed[^>]*>",
    r"eval\s*\(",
    r"document\.cookie",
    r"document\.write",
    r"window\.location",
    r"union\s+select",
    r"drop\s+table",
    r"delete\s+from",
    r"insert\s+into",
    r"update\s+.+set",
    r"exec\s*\(",
    r"xp_cmdshell",
    r"sp_executesql",
]

# Compiled regex patterns for performance
COMPILED_PATTERNS = [re.compile(pattern, re.IGNORECASE) for pattern in SUSPICIOUS_PATTERNS]

# File upload security
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"}
ALLOWED_DOCUMENT_EXTENSIONS = {".pdf", ".doc", ".docx", ".txt", ".csv", ".xlsx", ".xls"}
ALLOWED_ARCHIVE_EXTENSIONS = {".zip", ".tar", ".gz", ".7z"}

DANGEROUS_EXTENSIONS = {
    ".exe", ".bat", ".cmd", ".com", ".pif", ".scr", ".vbs", ".js", ".jar",
    ".app", ".deb", ".pkg", ".dmg", ".iso", ".msi", ".run", ".bin"
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB default


def hash_password(password: str) -> str:
    """Hash a password with bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Dict[str, Any]:
    """Verify and decode a JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


def generate_secure_token(length: int = 32) -> str:
    """Generate a cryptographically secure random token"""
    return secrets.token_urlsafe(length)


def generate_otp(length: int = 6) -> str:
    """Generate a one-time password"""
    return ''.join(secrets.choice('0123456789') for _ in range(length))


def validate_input_security(value: str, field_name: str = "input") -> str:
    """
    Validate input against XSS and injection attacks
    Returns sanitized value or raises HTTPException
    """
    if not value:
        return value
    
    # Check for suspicious patterns
    for pattern in COMPILED_PATTERNS:
        if pattern.search(value):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid characters detected in {field_name}"
            )
    
    # Basic HTML entity encoding for common XSS characters
    value = value.replace("<", "&lt;")
    value = value.replace(">", "&gt;")
    value = value.replace("\"", "&quot;")
    value = value.replace("'", "&#x27;")
    value = value.replace("/", "&#x2F;")
    
    return value


def validate_sql_input(value: str) -> str:
    """Validate input against SQL injection"""
    if not value:
        return value
    
    # SQL injection patterns
    sql_patterns = [
        r"union\s+select", r"drop\s+table", r"delete\s+from", r"insert\s+into",
        r"update\s+.+set", r"exec\s*\(", r"xp_cmdshell", r"sp_executesql",
        r"--", r"/\*", r"\*/", r"char\s*\(", r"nchar\s*\(", r"varchar\s*\(",
        r"nvarchar\s*\(", r"alter\s+table", r"create\s+table", r"truncate\s+table"
    ]
    
    for pattern in sql_patterns:
        if re.search(pattern, value, re.IGNORECASE):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid characters detected in input"
            )
    
    return value


def validate_file_upload(filename: str, content: bytes, allowed_types: Optional[List[str]] = None) -> bool:
    """
    Validate file upload for security
    """
    if not filename or not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file"
        )
    
    # Check file size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE / 1024 / 1024}MB"
        )
    
    # Get file extension
    file_ext = filename.lower().split('.')[-1] if '.' in filename else ''
    file_ext = f".{file_ext}"
    
    # Check for dangerous extensions
    if file_ext in DANGEROUS_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File type not allowed"
        )
    
    # Check allowed types if specified
    if allowed_types:
        allowed_extensions = set()
        for file_type in allowed_types:
            if file_type == "image":
                allowed_extensions.update(ALLOWED_IMAGE_EXTENSIONS)
            elif file_type == "document":
                allowed_extensions.update(ALLOWED_DOCUMENT_EXTENSIONS)
            elif file_type == "archive":
                allowed_extensions.update(ALLOWED_ARCHIVE_EXTENSIONS)
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
            )
    
    # Basic magic number validation for images
    if file_ext in ALLOWED_IMAGE_EXTENSIONS:
        if not _validate_image_content(content):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid image file"
            )
    
    return True


def _validate_image_content(content: bytes) -> bool:
    """Validate image file by checking magic numbers"""
    if len(content) < 8:
        return False
    
    # JPEG
    if content[:3] == b'\xff\xd8\xff':
        return True
    
    # PNG
    if content[:8] == b'\x89\x50\x4e\x47\x0d\x0a\x1a\x0a':
        return True
    
    # GIF
    if content[:6] in [b'GIF87a', b'GIF89a']:
        return True
    
    # WebP
    if content[:4] == b'RIFF' and content[8:12] == b'WEBP':
        return True
    
    # SVG (simplified check)
    if b'<svg' in content[:200].lower():
        return True
    
    return False


def validate_password_strength(password: str) -> List[str]:
    """
    Validate password strength and return list of issues
    """
    issues = []
    
    if len(password) < 8:
        issues.append("Password must be at least 8 characters long")
    
    if len(password) > 128:
        issues.append("Password must not exceed 128 characters")
    
    if not re.search(r'[a-z]', password):
        issues.append("Password must contain at least one lowercase letter")
    
    if not re.search(r'[A-Z]', password):
        issues.append("Password must contain at least one uppercase letter")
    
    if not re.search(r'\d', password):
        issues.append("Password must contain at least one digit")
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        issues.append("Password must contain at least one special character")
    
    # Check for common patterns
    if re.search(r'(.)\1{2,}', password):
        issues.append("Password must not contain repeated characters")
    
    if password.lower() in ['password', '123456789', 'qwerty123', 'admin123']:
        issues.append("Password is too common")
    
    return issues


def create_audit_entry(
    user_id: Optional[int],
    action: str,
    resource_type: str,
    resource_id: Optional[Union[int, str]] = None,
    details: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    tenant_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create an audit log entry
    """
    return {
        "user_id": user_id,
        "action": action,
        "resource_type": resource_type,
        "resource_id": str(resource_id) if resource_id else None,
        "details": details or {},
        "ip_address": ip_address,
        "user_agent": user_agent,
        "tenant_id": tenant_id,
        "timestamp": datetime.utcnow().isoformat(),
    }


def verify_hmac_signature(payload: bytes, signature: str, secret: str) -> bool:
    """
    Verify HMAC signature for webhook validation
    """
    if not signature or not secret:
        return False
    
    # Remove the algorithm prefix if present (e.g., "sha256=")
    if "=" in signature:
        signature = signature.split("=", 1)[1]
    
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent directory traversal and other attacks
    """
    if not filename:
        return "unnamed_file"
    
    # Remove directory traversal attempts
    filename = filename.replace('..', '').replace('/', '').replace('\\', '')
    
    # Remove or replace dangerous characters
    filename = re.sub(r'[<>:"|?*]', '_', filename)
    
    # Ensure filename is not empty after sanitization
    if not filename.strip():
        filename = "unnamed_file"
    
    return filename[:255]  # Limit length


def check_rate_limit_violations(request: Request, identifier: str) -> Optional[Dict[str, Any]]:
    """
    Check for rate limit violations and return violation details if any
    """
    # This would typically integrate with Redis or database
    # For now, return None (no violations)
    return None


def validate_ip_address(ip: str) -> bool:
    """
    Validate if IP address is allowed
    """
    import ipaddress
    
    try:
        ip_obj = ipaddress.ip_address(ip)
        
        # Block private networks in production
        if not settings.DEBUG and ip_obj.is_private:
            return False
        
        # Block localhost in production
        if not settings.DEBUG and ip_obj.is_loopback:
            return False
        
        return True
    except ValueError:
        return False


def encrypt_sensitive_data(data: str, key: Optional[str] = None) -> str:
    """
    Encrypt sensitive data using Fernet (symmetric encryption)
    """
    import base64
    from cryptography.fernet import Fernet
    
    if key is None:
        key = settings.SECRET_KEY
    
    # Ensure key is the right length for Fernet
    key_bytes = hashlib.sha256(key.encode()).digest()
    key_b64 = base64.urlsafe_b64encode(key_bytes)
    
    f = Fernet(key_b64)
    encrypted_data = f.encrypt(data.encode())
    return base64.urlsafe_b64encode(encrypted_data).decode()


def decrypt_sensitive_data(encrypted_data: str, key: Optional[str] = None) -> str:
    """
    Decrypt sensitive data using Fernet
    """
    import base64
    from cryptography.fernet import Fernet
    
    if key is None:
        key = settings.SECRET_KEY
    
    try:
        # Ensure key is the right length for Fernet
        key_bytes = hashlib.sha256(key.encode()).digest()
        key_b64 = base64.urlsafe_b64encode(key_bytes)
        
        f = Fernet(key_b64)
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted_data = f.decrypt(encrypted_bytes)
        return decrypted_data.decode()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to decrypt data"
        )