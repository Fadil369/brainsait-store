/**
 * Frontend security utilities for XSS prevention, input sanitization, and secure API calls
 */

import { z } from 'zod';

// CSP nonce for inline scripts (should be set by server)
declare global {
  interface Window {
    __CSP_NONCE__?: string;
  }
}

/**
 * Security configuration
 */
export const SECURITY_CONFIG = {
  // Maximum file upload size (10MB)
  MAX_FILE_SIZE: 10 * 1024 * 1024,
  
  // Allowed file types for upload
  ALLOWED_IMAGE_TYPES: ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
  ALLOWED_DOCUMENT_TYPES: [
    'application/pdf',
    'text/plain',
    'text/csv',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
  ],
  
  // Dangerous file extensions to block
  DANGEROUS_EXTENSIONS: [
    '.exe', '.bat', '.cmd', '.com', '.pif', '.scr', '.vbs', '.js', '.jar',
    '.app', '.deb', '.pkg', '.dmg', '.iso', '.msi', '.run', '.bin'
  ],
  
  // API rate limiting
  API_RATE_LIMIT: {
    maxRequests: 100,
    windowMs: 60000, // 1 minute
  },
  
  // Session timeout (30 minutes)
  SESSION_TIMEOUT: 30 * 60 * 1000,
} as const;

/**
 * XSS Prevention utilities
 */
export class XSSProtection {
  private static readonly dangerousPatterns = [
    /<script[^>]*>/gi,
    /javascript:/gi,
    /vbscript:/gi,
    /onload\s*=/gi,
    /onerror\s*=/gi,
    /onclick\s*=/gi,
    /onmouseover\s*=/gi,
    /<iframe[^>]*>/gi,
    /<object[^>]*>/gi,
    /<embed[^>]*>/gi,
    /eval\s*\(/gi,
    /document\.cookie/gi,
    /document\.write/gi,
    /window\.location/gi,
    /<meta[^>]+http-equiv/gi,
    /<link[^>]+href\s*=\s*["']javascript:/gi,
  ];

  /**
   * Sanitize HTML input to prevent XSS attacks
   */
  static sanitizeHTML(input: string): string {
    if (typeof input !== 'string') return '';
    
    return input
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#x27;')
      .replace(/\//g, '&#x2F;')
      .trim();
  }

  /**
   * Sanitize for use in HTML attributes
   */
  static sanitizeAttribute(input: string): string {
    if (typeof input !== 'string') return '';
    
    return input
      .replace(/[&<>"']/g, (match) => {
        const escapeMap: Record<string, string> = {
          '&': '&amp;',
          '<': '&lt;',
          '>': '&gt;',
          '"': '&quot;',
          "'": '&#x27;'
        };
        return escapeMap[match] || match;
      });
  }

  /**
   * Check if input contains dangerous patterns
   */
  static containsDangerousContent(input: string): boolean {
    if (typeof input !== 'string') return false;
    
    return this.dangerousPatterns.some(pattern => pattern.test(input));
  }

  /**
   * Validate and sanitize user input
   */
  static validateInput(input: string, fieldName: string = 'input'): string {
    if (this.containsDangerousContent(input)) {
      throw new Error(`${fieldName} contains potentially dangerous content`);
    }
    
    return this.sanitizeHTML(input);
  }
}

/**
 * SQL Injection Prevention
 */
export class SQLInjectionProtection {
  private static readonly sqlPatterns = [
    /union\s+select/gi,
    /drop\s+table/gi,
    /delete\s+from/gi,
    /insert\s+into/gi,
    /update\s+.+set/gi,
    /exec\s*\(/gi,
    /xp_cmdshell/gi,
    /sp_executesql/gi,
    /--/g,
    /\/\*/g,
    /\*\//g,
    /char\s*\(/gi,
    /nchar\s*\(/gi,
    /varchar\s*\(/gi,
    /nvarchar\s*\(/gi,
    /alter\s+table/gi,
    /create\s+table/gi,
    /truncate\s+table/gi,
  ];

  /**
   * Check if input contains SQL injection patterns
   */
  static containsSQLInjection(input: string): boolean {
    if (typeof input !== 'string') return false;
    
    return this.sqlPatterns.some(pattern => pattern.test(input));
  }

  /**
   * Validate input against SQL injection
   */
  static validateInput(input: string, fieldName: string = 'input'): string {
    if (this.containsSQLInjection(input)) {
      throw new Error(`${fieldName} contains invalid characters`);
    }
    
    return input;
  }
}

/**
 * File Upload Security
 */
export class FileUploadSecurity {
  /**
   * Validate file for security issues
   */
  static validateFile(file: File): { isValid: boolean; errors: string[] } {
    const errors: string[] = [];

    // Check file size
    if (file.size > SECURITY_CONFIG.MAX_FILE_SIZE) {
      errors.push(`File size exceeds ${SECURITY_CONFIG.MAX_FILE_SIZE / 1024 / 1024}MB limit`);
    }

    // Check for dangerous extensions
    const fileName = file.name.toLowerCase();
    const hasDangerousExtension = SECURITY_CONFIG.DANGEROUS_EXTENSIONS.some(ext => 
      fileName.endsWith(ext)
    );
    
    if (hasDangerousExtension) {
      errors.push('File type is not allowed for security reasons');
    }

    // Check MIME type
    const isImageType = (SECURITY_CONFIG.ALLOWED_IMAGE_TYPES as readonly string[]).includes(file.type);
    const isDocumentType = (SECURITY_CONFIG.ALLOWED_DOCUMENT_TYPES as readonly string[]).includes(file.type);
    
    if (!isImageType && !isDocumentType) {
      errors.push('File type is not supported');
    }

    // Check for suspicious file names
    if (this.hasSuspiciousFileName(fileName)) {
      errors.push('File name contains invalid characters');
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  /**
   * Check for suspicious file names
   */
  private static hasSuspiciousFileName(fileName: string): boolean {
    const suspiciousPatterns = [
      /\.\.\//, // Directory traversal
      /\x00/, // Null bytes
      /<script/i, // HTML injection
      /javascript:/i, // JavaScript protocol
      /[<>:"|?*]/, // Invalid filename characters on Windows
    ];

    return suspiciousPatterns.some(pattern => pattern.test(fileName));
  }

  /**
   * Generate secure filename
   */
  static generateSecureFileName(originalName: string): string {
    const extension = originalName.split('.').pop() || '';
    const timestamp = Date.now();
    const randomString = Math.random().toString(36).substring(2, 15);
    
    return `${timestamp}_${randomString}.${extension}`;
  }
}

/**
 * API Security utilities
 */
export class APISecurity {
  private static requestCounts = new Map<string, { count: number; resetTime: number }>();

  /**
   * Rate limiting for API calls
   */
  static checkRateLimit(endpoint: string): boolean {
    const now = Date.now();
    const key = endpoint;
    const limit = SECURITY_CONFIG.API_RATE_LIMIT;
    
    const current = this.requestCounts.get(key);
    
    if (!current || now > current.resetTime) {
      this.requestCounts.set(key, {
        count: 1,
        resetTime: now + limit.windowMs
      });
      return true;
    }
    
    if (current.count >= limit.maxRequests) {
      return false;
    }
    
    current.count++;
    return true;
  }

  /**
   * Secure headers for API requests
   */
  static getSecureHeaders(includeAuth: boolean = false): Record<string, string> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      'X-Requested-With': 'XMLHttpRequest',
    };

    // Add CSP nonce if available
    if (window.__CSP_NONCE__) {
      headers['X-CSP-Nonce'] = window.__CSP_NONCE__;
    }

    // Add auth header if needed
    if (includeAuth) {
      const token = this.getAuthToken();
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
    }

    return headers;
  }

  /**
   * Get authentication token securely
   */
  private static getAuthToken(): string | null {
    try {
      return localStorage.getItem('auth_token');
    } catch {
      return null;
    }
  }

  /**
   * Validate API response
   */
  static validateResponse(response: Response): void {
    // Check for suspicious response headers
    const contentType = response.headers.get('content-type');
    if (contentType && !contentType.includes('application/json')) {
      throw new Error('Invalid response content type');
    }

    // Check for security headers
    const securityHeaders = [
      'x-content-type-options',
      'x-frame-options',
      'x-xss-protection'
    ];

    securityHeaders.forEach(header => {
      if (!response.headers.get(header)) {
        console.warn(`Missing security header: ${header}`);
      }
    });
  }
}

/**
 * Session Security
 */
export class SessionSecurity {
  private static lastActivity = Date.now();
  private static timeoutWarningShown = false;

  /**
   * Update last activity timestamp
   */
  static updateActivity(): void {
    this.lastActivity = Date.now();
    this.timeoutWarningShown = false;
  }

  /**
   * Check if session has timed out
   */
  static isSessionExpired(): boolean {
    return Date.now() - this.lastActivity > SECURITY_CONFIG.SESSION_TIMEOUT;
  }

  /**
   * Get remaining session time in milliseconds
   */
  static getRemainingTime(): number {
    const elapsed = Date.now() - this.lastActivity;
    return Math.max(0, SECURITY_CONFIG.SESSION_TIMEOUT - elapsed);
  }

  /**
   * Show timeout warning
   */
  static shouldShowTimeoutWarning(): boolean {
    const remaining = this.getRemainingTime();
    const warningThreshold = 5 * 60 * 1000; // 5 minutes
    
    return remaining <= warningThreshold && remaining > 0 && !this.timeoutWarningShown;
  }

  /**
   * Mark timeout warning as shown
   */
  static markTimeoutWarningShown(): void {
    this.timeoutWarningShown = true;
  }

  /**
   * Clear session data securely
   */
  static clearSession(): void {
    try {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user_data');
      sessionStorage.clear();
    } catch (error) {
      console.error('Error clearing session:', error);
    }
  }
}

/**
 * Content Security Policy utilities
 */
export class CSPUtils {
  /**
   * Check if inline script execution is allowed
   */
  static isInlineScriptAllowed(): boolean {
    return !!window.__CSP_NONCE__;
  }

  /**
   * Create secure script element with nonce
   */
  static createSecureScript(content: string): HTMLScriptElement {
    const script = document.createElement('script');
    
    if (window.__CSP_NONCE__) {
      script.nonce = window.__CSP_NONCE__;
    }
    
    script.textContent = content;
    return script;
  }

  /**
   * Report CSP violations (if endpoint is configured)
   */
  static reportViolation(violation: SecurityPolicyViolationEvent): void {
    console.warn('CSP Violation:', violation);
    
    // In production, send to monitoring service
    if (process.env.NODE_ENV === 'production') {
      // fetch('/api/security/csp-violations', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({
      //     blockedURI: violation.blockedURI,
      //     documentURI: violation.documentURI,
      //     violatedDirective: violation.violatedDirective,
      //     timestamp: new Date().toISOString()
      //   })
      // }).catch(console.error);
    }
  }
}

/**
 * Password strength validation
 */
export class PasswordSecurity {
  /**
   * Calculate password strength score (0-100)
   */
  static calculateStrength(password: string): number {
    let score = 0;
    
    // Length bonus
    if (password.length >= 8) score += 25;
    if (password.length >= 12) score += 10;
    if (password.length >= 16) score += 10;
    
    // Character variety
    if (/[a-z]/.test(password)) score += 10;
    if (/[A-Z]/.test(password)) score += 10;
    if (/\d/.test(password)) score += 10;
    if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) score += 15;
    
    // Pattern checking
    if (!/(.)\1{2,}/.test(password)) score += 10; // No repeated characters
    
    return Math.min(100, score);
  }

  /**
   * Get password strength label
   */
  static getStrengthLabel(score: number): string {
    if (score < 30) return 'Very Weak';
    if (score < 50) return 'Weak';
    if (score < 70) return 'Fair';
    if (score < 90) return 'Good';
    return 'Excellent';
  }

  /**
   * Check if password is commonly used
   */
  static isCommonPassword(password: string): boolean {
    const commonPasswords = [
      'password', '123456', '123456789', 'qwerty', 'abc123',
      'password123', 'admin', 'letmein', 'welcome', 'monkey',
      'dragon', 'qwertyuiop', '123321', 'master', 'hello'
    ];
    
    return commonPasswords.includes(password.toLowerCase());
  }
}

/**
 * Initialize security features
 */
export function initializeSecurity(): void {
  // Set up CSP violation reporting
  document.addEventListener('securitypolicyviolation', CSPUtils.reportViolation);
  
  // Set up activity tracking
  const trackActivity = () => SessionSecurity.updateActivity();
  
  ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click'].forEach(event => {
    document.addEventListener(event, trackActivity, true);
  });
  
  // Check for session timeout periodically
  setInterval(() => {
    if (SessionSecurity.isSessionExpired()) {
      SessionSecurity.clearSession();
      window.location.href = '/login?reason=session_expired';
    } else if (SessionSecurity.shouldShowTimeoutWarning()) {
      SessionSecurity.markTimeoutWarningShown();
      // Show timeout warning modal/notification
      console.warn('Session will expire soon');
    }
  }, 60000); // Check every minute
  
  console.log('Security features initialized');
}

// Export all security utilities as default export to avoid redeclaration errors
export default {
  XSSProtection,
  SQLInjectionProtection,
  FileUploadSecurity,
  APISecurity,
  SessionSecurity,
  CSPUtils,
  PasswordSecurity,
};