/**
 * Comprehensive validation schemas using Zod for enhanced security
 */

import { z } from 'zod';

// Common patterns for validation
const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
const strongPasswordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/;

// XSS prevention patterns
const dangerousPatterns = [
  /<script[^>]*>/i,
  /javascript:/i,
  /vbscript:/i,
  /onload\s*=/i,
  /onerror\s*=/i,
  /onclick\s*=/i,
  /<iframe[^>]*>/i,
  /<object[^>]*>/i,
  /<embed[^>]*>/i,
  /eval\s*\(/i,
  /document\.cookie/i,
  /document\.write/i,
  /window\.location/i
];

// Custom validation functions
export const validateNoXSS = (value: string): boolean => {
  return !dangerousPatterns.some(pattern => pattern.test(value));
};

export const validateNoSQLInjection = (value: string): boolean => {
  const sqlPatterns = [
    /union\s+select/i,
    /drop\s+table/i,
    /delete\s+from/i,
    /insert\s+into/i,
    /update\s+.+set/i,
    /exec\s*\(/i,
    /xp_cmdshell/i,
    /sp_executesql/i,
    /--/,
    /\/\*/,
    /\*\//
  ];
  
  return !sqlPatterns.some(pattern => pattern.test(value));
};

export const sanitizeInput = (value: string): string => {
  return value
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;')
    .replace(/\//g, '&#x2F;')
    .trim();
};

// Base string validation with security checks
export const secureStringSchema = (fieldName: string = 'field') =>
  z.string()
    .refine(validateNoXSS, { message: `${fieldName} contains invalid characters` })
    .refine(validateNoSQLInjection, { message: `${fieldName} contains invalid characters` })
    .transform(sanitizeInput);

// Enhanced string schema that allows chaining of additional validations
export const createSecureStringSchema = (fieldName: string = 'field') => {
  return z.string()
    .refine(validateNoXSS, { message: `${fieldName} contains invalid characters` })
    .refine(validateNoSQLInjection, { message: `${fieldName} contains invalid characters` })
    .transform(sanitizeInput);
};

// Authentication schemas
export const loginSchema = z.object({
  email: z.string()
    .min(1, 'Email is required')
    .max(254, 'Email is too long')
    .email('Invalid email format')
    .refine(validateNoXSS, { message: 'Email contains invalid characters' })
    .transform(val => val.toLowerCase().trim()),
  
  password: z.string()
    .min(1, 'Password is required')
    .max(128, 'Password is too long'),
  
  rememberMe: z.boolean().optional().default(false),
  
  mfaCode: z.string()
    .length(6, 'MFA code must be 6 digits')
    .regex(/^\d{6}$/, 'MFA code must contain only digits')
    .optional(),
    
  tenantSubdomain: z.string()
    .min(2, 'Tenant subdomain must be at least 2 characters')
    .max(50, 'Tenant subdomain is too long')
    .regex(/^[a-z0-9\-_]+$/, 'Tenant subdomain can only contain lowercase letters, numbers, hyphens, and underscores')
    .refine(validateNoXSS, { message: 'Tenant subdomain contains invalid characters' })
    .transform(sanitizeInput)
    .optional()
});

export const registerSchema = z.object({
  email: z.string()
    .min(1, 'Email is required')
    .max(254, 'Email is too long')
    .email('Invalid email format')
    .refine(validateNoXSS, { message: 'Email contains invalid characters' })
    .transform(val => val.toLowerCase().trim()),
  
  password: z.string()
    .min(8, 'Password must be at least 8 characters')
    .max(128, 'Password is too long')
    .regex(strongPasswordRegex, 'Password must contain at least one lowercase letter, one uppercase letter, one digit, and one special character'),
  
  confirmPassword: z.string(),
  
  fullName: z.string()
    .min(2, 'Full name must be at least 2 characters')
    .max(100, 'Full name is too long')
    .regex(/^[a-zA-Z\s\u0600-\u06FF]+$/, 'Full name can only contain letters and spaces')
    .refine(validateNoXSS, { message: 'Full name contains invalid characters' })
    .transform(sanitizeInput),
  
  company: z.string()
    .min(2, 'Company name must be at least 2 characters')
    .max(100, 'Company name is too long')
    .refine(validateNoXSS, { message: 'Company contains invalid characters' })
    .transform(sanitizeInput)
    .optional()
    .or(z.literal('')),
  
  phone: z.string()
    .regex(phoneRegex, 'Invalid phone number format')
    .optional()
    .or(z.literal('')),
  
  termsAccepted: z.boolean()
    .refine(val => val === true, { message: 'You must accept the terms and conditions' })
}).refine(data => data.password === data.confirmPassword, {
  message: 'Passwords do not match',
  path: ['confirmPassword']
});

export const resetPasswordSchema = z.object({
  email: z.string()
    .min(1, 'Email is required')
    .max(254, 'Email is too long')
    .email('Invalid email format')
    .refine(validateNoXSS, { message: 'Email contains invalid characters' })
    .transform(val => val.toLowerCase().trim())
});

export const changePasswordSchema = z.object({
  currentPassword: z.string()
    .min(1, 'Current password is required'),
  
  newPassword: z.string()
    .min(8, 'Password must be at least 8 characters')
    .max(128, 'Password is too long')
    .regex(strongPasswordRegex, 'Password must contain at least one lowercase letter, one uppercase letter, one digit, and one special character'),
  
  confirmNewPassword: z.string()
}).refine(data => data.newPassword === data.confirmNewPassword, {
  message: 'Passwords do not match',
  path: ['confirmNewPassword']
}).refine(data => data.currentPassword !== data.newPassword, {
  message: 'New password must be different from current password',
  path: ['newPassword']
});

// Product and content schemas
export const productSearchSchema = z.object({
  query: z.string()
    .min(1, 'Search query is required')
    .max(200, 'Search query is too long')
    .refine(validateNoXSS, { message: 'Search query contains invalid characters' })
    .refine(validateNoSQLInjection, { message: 'Search query contains invalid characters' })
    .transform(sanitizeInput),
  
  category: z.string()
    .max(50, 'Category name is too long')
    .refine(validateNoXSS, { message: 'Category contains invalid characters' })
    .transform(sanitizeInput)
    .optional(),
  
  minPrice: z.number()
    .min(0, 'Minimum price cannot be negative')
    .max(1000000, 'Price is too high')
    .optional(),
  
  maxPrice: z.number()
    .min(0, 'Maximum price cannot be negative')
    .max(1000000, 'Price is too high')
    .optional(),
  
  sortBy: z.enum(['name', 'price', 'date', 'popularity']).optional()
}).refine(data => {
  if (data.minPrice && data.maxPrice) {
    return data.minPrice <= data.maxPrice;
  }
  return true;
}, {
  message: 'Minimum price cannot be greater than maximum price',
  path: ['maxPrice']
});

export const contactSchema = z.object({
  name: z.string()
    .min(2, 'Name must be at least 2 characters')
    .max(100, 'Name is too long')
    .regex(/^[a-zA-Z\s\u0600-\u06FF]+$/, 'Name can only contain letters and spaces')
    .refine(validateNoXSS, { message: 'Name contains invalid characters' })
    .transform(sanitizeInput),
  
  email: z.string()
    .min(1, 'Email is required')
    .max(254, 'Email is too long')
    .email('Invalid email format')
    .refine(validateNoXSS, { message: 'Email contains invalid characters' })
    .transform(val => val.toLowerCase().trim()),
  
  subject: z.string()
    .min(5, 'Subject must be at least 5 characters')
    .max(200, 'Subject is too long')
    .refine(validateNoXSS, { message: 'Subject contains invalid characters' })
    .transform(sanitizeInput),
  
  message: z.string()
    .min(10, 'Message must be at least 10 characters')
    .max(2000, 'Message is too long')
    .refine(validateNoXSS, { message: 'Message contains invalid characters' })
    .transform(sanitizeInput),
  
  phone: z.string()
    .regex(phoneRegex, 'Invalid phone number format')
    .optional()
    .or(z.literal(''))
});

// File upload schemas
export const fileUploadSchema = z.object({
  file: z.any()
    .refine(file => file instanceof File, { message: 'Please select a file' })
    .refine(file => file.size <= 10 * 1024 * 1024, { message: 'File size must be less than 10MB' })
    .refine(file => {
      const allowedTypes = [
        'image/jpeg', 'image/png', 'image/gif', 'image/webp',
        'application/pdf', 'text/plain', 'text/csv',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
      ];
      return allowedTypes.includes(file.type);
    }, { message: 'File type not allowed' })
    .refine(file => {
      const dangerousExtensions = [
        '.exe', '.bat', '.cmd', '.com', '.pif', '.scr', '.vbs', '.js', '.jar',
        '.app', '.deb', '.pkg', '.dmg', '.iso', '.msi', '.run', '.bin'
      ];
      const fileName = file.name.toLowerCase();
      return !dangerousExtensions.some(ext => fileName.endsWith(ext));
    }, { message: 'File type is not allowed for security reasons' }),
  
  category: z.enum(['images', 'documents', 'avatars']).default('documents'),
  
  description: z.string()
    .max(500, 'Description is too long')
    .refine(validateNoXSS, { message: 'Description contains invalid characters' })
    .transform(sanitizeInput)
    .optional()
});

// Profile update schema
export const profileUpdateSchema = z.object({
  fullName: z.string()
    .min(2, 'Full name must be at least 2 characters')
    .max(100, 'Full name is too long')
    .regex(/^[a-zA-Z\s\u0600-\u06FF]+$/, 'Full name can only contain letters and spaces')
    .refine(validateNoXSS, { message: 'Full name contains invalid characters' })
    .transform(sanitizeInput),
  
  company: z.string()
    .min(2, 'Company name must be at least 2 characters')
    .max(100, 'Company name is too long')
    .refine(validateNoXSS, { message: 'Company contains invalid characters' })
    .transform(sanitizeInput)
    .optional()
    .or(z.literal('')),
  
  phone: z.string()
    .regex(phoneRegex, 'Invalid phone number format')
    .optional()
    .or(z.literal('')),
  
  bio: z.string()
    .max(500, 'Bio is too long')
    .refine(validateNoXSS, { message: 'Bio contains invalid characters' })
    .transform(sanitizeInput)
    .optional()
    .or(z.literal('')),
  
  website: z.string()
    .url('Invalid website URL')
    .max(200, 'Website URL is too long')
    .optional()
    .or(z.literal('')),
  
  location: z.string()
    .max(100, 'Location is too long')
    .refine(validateNoXSS, { message: 'Location contains invalid characters' })
    .transform(sanitizeInput)
    .optional()
    .or(z.literal('')),
  
  language: z.enum(['en', 'ar']).default('en'),
  
  timezone: z.string()
    .max(50, 'Timezone is too long')
    .optional()
});

// MFA setup schema
export const mfaSetupSchema = z.object({
  verificationCode: z.string()
    .length(6, 'Verification code must be 6 digits')
    .regex(/^\d{6}$/, 'Verification code must contain only digits'),
  
  backupCodes: z.array(z.string()).optional()
});

export const mfaDisableSchema = z.object({
  password: z.string()
    .min(1, 'Password is required'),
  
  verificationCode: z.string()
    .length(6, 'Verification code must be 6 digits')
    .regex(/^\d{6}$/, 'Verification code must contain only digits')
});

// Payment schema (for checkout forms)
export const paymentInfoSchema = z.object({
  cardNumber: z.string()
    .min(13, 'Card number must be at least 13 digits')
    .max(19, 'Card number must be at most 19 digits')
    .regex(/^\d+$/, 'Card number must contain only digits'),
  
  expiryMonth: z.string()
    .regex(/^(0[1-9]|1[0-2])$/, 'Invalid expiry month'),
  
  expiryYear: z.string()
    .regex(/^20\d{2}$/, 'Invalid expiry year')
    .refine(year => parseInt(year) >= new Date().getFullYear(), {
      message: 'Card has expired'
    }),
  
  cvv: z.string()
    .min(3, 'CVV must be at least 3 digits')
    .max(4, 'CVV must be at most 4 digits')
    .regex(/^\d+$/, 'CVV must contain only digits'),
  
  cardholderName: z.string()
    .min(2, 'Cardholder name must be at least 2 characters')
    .max(100, 'Cardholder name is too long')
    .regex(/^[a-zA-Z\s\u0600-\u06FF]+$/, 'Cardholder name can only contain letters and spaces')
    .refine(validateNoXSS, { message: 'Cardholder name contains invalid characters' })
    .transform(sanitizeInput)
});

// Billing address schema
export const billingAddressSchema = z.object({
  firstName: z.string()
    .min(1, 'First name is required')
    .max(50, 'First name is too long')
    .regex(/^[a-zA-Z\s\u0600-\u06FF]+$/, 'First name can only contain letters and spaces')
    .refine(validateNoXSS, { message: 'First name contains invalid characters' })
    .transform(sanitizeInput),
  
  lastName: z.string()
    .min(1, 'Last name is required')
    .max(50, 'Last name is too long')
    .regex(/^[a-zA-Z\s\u0600-\u06FF]+$/, 'Last name can only contain letters and spaces')
    .refine(validateNoXSS, { message: 'Last name contains invalid characters' })
    .transform(sanitizeInput),
  
  address1: z.string()
    .min(5, 'Address must be at least 5 characters')
    .max(100, 'Address is too long')
    .refine(validateNoXSS, { message: 'Address contains invalid characters' })
    .transform(sanitizeInput),
  
  address2: z.string()
    .max(100, 'Address is too long')
    .refine(validateNoXSS, { message: 'Address contains invalid characters' })
    .transform(sanitizeInput)
    .optional()
    .or(z.literal('')),
  
  city: z.string()
    .min(2, 'City must be at least 2 characters')
    .max(50, 'City name is too long')
    .regex(/^[a-zA-Z\s\u0600-\u06FF]+$/, 'City name can only contain letters and spaces')
    .refine(validateNoXSS, { message: 'City contains invalid characters' })
    .transform(sanitizeInput),
  
  state: z.string()
    .min(2, 'State must be at least 2 characters')
    .max(50, 'State name is too long')
    .regex(/^[a-zA-Z\s\u0600-\u06FF]+$/, 'State name can only contain letters and spaces')
    .refine(validateNoXSS, { message: 'State contains invalid characters' })
    .transform(sanitizeInput),
  
  postalCode: z.string()
    .min(3, 'Postal code must be at least 3 characters')
    .max(10, 'Postal code is too long')
    .regex(/^[A-Za-z0-9\s\-]+$/, 'Invalid postal code format'),
  
  country: z.string()
    .min(2, 'Country is required')
    .max(2, 'Country code must be 2 characters')
    .regex(/^[A-Z]{2}$/, 'Country must be a valid 2-letter code')
});

// Type exports for use in components
export type LoginFormData = z.infer<typeof loginSchema>;
export type RegisterFormData = z.infer<typeof registerSchema>;
export type ResetPasswordFormData = z.infer<typeof resetPasswordSchema>;
export type ChangePasswordFormData = z.infer<typeof changePasswordSchema>;
export type ProductSearchFormData = z.infer<typeof productSearchSchema>;
export type ContactFormData = z.infer<typeof contactSchema>;
export type FileUploadFormData = z.infer<typeof fileUploadSchema>;
export type ProfileUpdateFormData = z.infer<typeof profileUpdateSchema>;
export type MFASetupFormData = z.infer<typeof mfaSetupSchema>;
export type MFADisableFormData = z.infer<typeof mfaDisableSchema>;
export type PaymentInfoFormData = z.infer<typeof paymentInfoSchema>;
export type BillingAddressFormData = z.infer<typeof billingAddressSchema>;