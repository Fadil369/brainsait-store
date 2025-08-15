'use client';

import React from 'react';
import { cn } from '@/lib/utils';
import { Input, InputProps } from './Input';
import { Eye, EyeOff, Check, X } from 'lucide-react';

// Base form field wrapper
export interface BaseFormFieldProps {
  label?: string;
  labelAr?: string;
  error?: string;
  required?: boolean;
  children: React.ReactNode;
  className?: string;
  description?: string;
  descriptionAr?: string;
}

const BaseFormField: React.FC<BaseFormFieldProps> = ({
  label,
  labelAr,
  error,
  required,
  children,
  className,
  description,
  descriptionAr,
}) => {
  const currentLanguage = ('en' as 'en' | 'ar'); // This would come from your i18n context

  return (
    <div className={cn('space-y-2', className)}>
      {(label || labelAr) && (
        <label className="block text-sm font-medium text-text-primary">
          {currentLanguage === 'ar' ? labelAr : label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      
      {children}
      
      {(description || descriptionAr) && !error && (
        <p className="text-xs text-text-secondary">
          {currentLanguage === 'ar' ? descriptionAr : description}
        </p>
      )}
      
      {error && (
        <p className="text-xs text-red-500 flex items-center gap-1">
          <X className="h-3 w-3" />
          {error}
        </p>
      )}
    </div>
  );
};

// Enhanced text input with validation states
export interface TextFieldProps extends Omit<InputProps, 'error'> {
  label?: string;
  labelAr?: string;
  error?: string;
  required?: boolean;
  description?: string;
  descriptionAr?: string;
  showValidation?: boolean;
  isValid?: boolean;
}

const TextField: React.FC<TextFieldProps> = ({
  label,
  labelAr,
  error,
  required,
  description,
  descriptionAr,
  showValidation = false,
  isValid = false,
  className,
  ...inputProps
}) => {
  return (
    <BaseFormField
      label={label}
      labelAr={labelAr}
      error={error}
      required={required}
      description={description}
      descriptionAr={descriptionAr}
      className={className}
    >
      <div className="relative">
        <Input
          {...inputProps}
          error={error}
        />
        {showValidation && (
          <div className="absolute right-3 top-1/2 -translate-y-1/2">
            {isValid ? (
              <Check className="h-4 w-4 text-green-500" />
            ) : error ? (
              <X className="h-4 w-4 text-red-500" />
            ) : null}
          </div>
        )}
      </div>
    </BaseFormField>
  );
};

// Password field with toggle visibility
export interface PasswordFieldProps extends Omit<TextFieldProps, 'type'> {
  showStrengthIndicator?: boolean;
}

const PasswordField: React.FC<PasswordFieldProps> = ({
  showStrengthIndicator = false,
  ...props
}) => {
  const [showPassword, setShowPassword] = React.useState(false);
  const [strength, setStrength] = React.useState(0);

  const calculateStrength = (password: string): number => {
    let score = 0;
    if (password.length >= 8) score++;
    if (/[a-z]/.test(password)) score++;
    if (/[A-Z]/.test(password)) score++;
    if (/[0-9]/.test(password)) score++;
    if (/[^A-Za-z0-9]/.test(password)) score++;
    return score;
  };

  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const password = e.target.value;
    if (showStrengthIndicator) {
      setStrength(calculateStrength(password));
    }
    props.onChange?.(e);
  };

  const strengthLabels = ['Very Weak', 'Weak', 'Fair', 'Good', 'Strong'];
  const strengthColors = ['bg-red-500', 'bg-orange-500', 'bg-yellow-500', 'bg-blue-500', 'bg-green-500'];

  return (
    <div className="space-y-2">
      <TextField
        {...props}
        type={showPassword ? 'text' : 'password'}
        onChange={handlePasswordChange}
        rightIcon={
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="text-text-secondary hover:text-text-primary transition-colors"
          >
            {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
          </button>
        }
      />
      
      {showStrengthIndicator && props.value && (
        <div className="space-y-1">
          <div className="flex space-x-1">
            {Array.from({ length: 5 }).map((_, index) => (
              <div
                key={index}
                className={cn(
                  'h-1 flex-1 rounded-full transition-colors',
                  index < strength ? strengthColors[strength - 1] : 'bg-gray-200'
                )}
              />
            ))}
          </div>
          {strength > 0 && (
            <p className="text-xs text-text-secondary">
              Password strength: {strengthLabels[strength - 1]}
            </p>
          )}
        </div>
      )}
    </div>
  );
};

// Select field component
export interface SelectFieldProps extends Omit<React.SelectHTMLAttributes<HTMLSelectElement>, 'onChange'> {
  label?: string;
  labelAr?: string;
  error?: string;
  required?: boolean;
  description?: string;
  descriptionAr?: string;
  options: Array<{ value: string; label: string; labelAr?: string }>;
  placeholder?: string;
  placeholderAr?: string;
  onChange?: (value: string) => void;
}

const SelectField: React.FC<SelectFieldProps> = ({
  label,
  labelAr,
  error,
  required,
  description,
  descriptionAr,
  options,
  placeholder,
  placeholderAr,
  onChange,
  className,
  ...selectProps
}) => {
  const currentLanguage = ('en' as 'en' | 'ar'); // This would come from your i18n context

  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    onChange?.(e.target.value);
  };

  return (
    <BaseFormField
      label={label}
      labelAr={labelAr}
      error={error}
      required={required}
      description={description}
      descriptionAr={descriptionAr}
      className={className}
    >
      <select
        {...selectProps}
        onChange={handleChange}
        className={cn(
          'flex w-full rounded-xl border bg-transparent px-4 py-3 text-sm transition-all duration-300',
          'glass border-glass-border hover:border-vision-green/50 focus:border-vision-green text-text-primary',
          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-vision-green focus-visible:ring-offset-2',
          'disabled:cursor-not-allowed disabled:opacity-50',
          error && 'border-red-500 focus:border-red-500 focus:ring-red-500'
        )}
      >
        {(placeholder || placeholderAr) && (
          <option value="">
            {currentLanguage === 'ar' ? placeholderAr : placeholder}
          </option>
        )}
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {currentLanguage === 'ar' ? option.labelAr : option.label}
          </option>
        ))}
      </select>
    </BaseFormField>
  );
};

// Checkbox field component
export interface CheckboxFieldProps {
  label?: string;
  labelAr?: string;
  error?: string;
  required?: boolean;
  description?: string;
  descriptionAr?: string;
  checked?: boolean;
  onChange?: (checked: boolean) => void;
  className?: string;
  id?: string;
}

const CheckboxField: React.FC<CheckboxFieldProps> = ({
  label,
  labelAr,
  error,
  required,
  description,
  descriptionAr,
  checked,
  onChange,
  className,
  id,
}) => {
  const currentLanguage = ('en' as 'en' | 'ar'); // This would come from your i18n context
  const checkboxId = id || `checkbox-${Math.random().toString(36).substr(2, 9)}`;

  return (
    <BaseFormField
      error={error}
      description={description}
      descriptionAr={descriptionAr}
      className={className}
    >
      <div className="flex items-start space-x-3">
        <input
          type="checkbox"
          id={checkboxId}
          checked={checked}
          onChange={(e) => onChange?.(e.target.checked)}
          className={cn(
            'mt-1 h-4 w-4 rounded border-gray-300 text-vision-green',
            'focus:ring-vision-green focus:ring-2 focus:ring-offset-2',
            error && 'border-red-500'
          )}
        />
        <div className="flex-1">
          <label htmlFor={checkboxId} className="text-sm text-text-primary cursor-pointer">
            {currentLanguage === 'ar' ? labelAr : label}
            {required && <span className="text-red-500 ml-1">*</span>}
          </label>
        </div>
      </div>
    </BaseFormField>
  );
};

// Radio group component
export interface RadioOption {
  value: string;
  label: string;
  labelAr?: string;
  description?: string;
  descriptionAr?: string;
}

export interface RadioGroupProps {
  label?: string;
  labelAr?: string;
  error?: string;
  required?: boolean;
  description?: string;
  descriptionAr?: string;
  options: RadioOption[];
  value?: string;
  onChange?: (value: string) => void;
  className?: string;
  name: string;
}

const RadioGroup: React.FC<RadioGroupProps> = ({
  label,
  labelAr,
  error,
  required,
  description,
  descriptionAr,
  options,
  value,
  onChange,
  className,
  name,
}) => {
  const currentLanguage = ('en' as 'en' | 'ar'); // This would come from your i18n context

  return (
    <BaseFormField
      label={label}
      labelAr={labelAr}
      error={error}
      required={required}
      description={description}
      descriptionAr={descriptionAr}
      className={className}
    >
      <div className="space-y-3">
        {options.map((option) => (
          <div key={option.value} className="flex items-start space-x-3">
            <input
              type="radio"
              id={`${name}-${option.value}`}
              name={name}
              value={option.value}
              checked={value === option.value}
              onChange={(e) => onChange?.(e.target.value)}
              className={cn(
                'mt-1 h-4 w-4 border-gray-300 text-vision-green',
                'focus:ring-vision-green focus:ring-2 focus:ring-offset-2',
                error && 'border-red-500'
              )}
            />
            <div className="flex-1">
              <label 
                htmlFor={`${name}-${option.value}`} 
                className="text-sm text-text-primary cursor-pointer"
              >
                {currentLanguage === 'ar' ? option.labelAr : option.label}
              </label>
              {(option.description || option.descriptionAr) && (
                <p className="text-xs text-text-secondary mt-1">
                  {currentLanguage === 'ar' ? option.descriptionAr : option.description}
                </p>
              )}
            </div>
          </div>
        ))}
      </div>
    </BaseFormField>
  );
};

// Textarea field component
export interface TextareaFieldProps extends Omit<React.TextareaHTMLAttributes<HTMLTextAreaElement>, 'onChange'> {
  label?: string;
  labelAr?: string;
  error?: string;
  required?: boolean;
  description?: string;
  descriptionAr?: string;
  showCharCount?: boolean;
  maxLength?: number;
  onChange?: (value: string) => void;
}

const TextareaField: React.FC<TextareaFieldProps> = ({
  label,
  labelAr,
  error,
  required,
  description,
  descriptionAr,
  showCharCount = false,
  maxLength,
  onChange,
  className,
  value = '',
  ...textareaProps
}) => {
  const charCount = typeof value === 'string' ? value.length : 0;

  return (
    <BaseFormField
      label={label}
      labelAr={labelAr}
      error={error}
      required={required}
      description={description}
      descriptionAr={descriptionAr}
      className={className}
    >
      <div className="space-y-1">
        <textarea
          {...textareaProps}
          value={value}
          maxLength={maxLength}
          onChange={(e) => onChange?.(e.target.value)}
          className={cn(
            'flex w-full rounded-xl border bg-transparent px-4 py-3 text-sm transition-all duration-300',
            'glass border-glass-border hover:border-vision-green/50 focus:border-vision-green text-text-primary',
            'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-vision-green focus-visible:ring-offset-2',
            'disabled:cursor-not-allowed disabled:opacity-50 resize-none',
            error && 'border-red-500 focus:border-red-500 focus:ring-red-500'
          )}
        />
        {showCharCount && (maxLength || charCount > 0) && (
          <div className="flex justify-end">
            <span className={cn(
              'text-xs',
              maxLength && charCount > maxLength * 0.9 ? 'text-orange-500' : 'text-text-secondary',
              maxLength && charCount >= maxLength ? 'text-red-500' : ''
            )}>
              {charCount}{maxLength && ` / ${maxLength}`}
            </span>
          </div>
        )}
      </div>
    </BaseFormField>
  );
};

// Phone input with country code (focused on Saudi Arabia)
export interface PhoneFieldProps extends Omit<TextFieldProps, 'type' | 'leftIcon'> {
  countryCode?: string;
  onPhoneChange?: (phone: string, countryCode: string) => void;
}

const PhoneField: React.FC<PhoneFieldProps> = ({
  countryCode = '+966',
  onPhoneChange,
  onChange,
  ...props
}) => {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const phone = e.target.value;
    onPhoneChange?.(phone, countryCode);
    onChange?.(e);
  };

  return (
    <TextField
      {...props}
      type="tel"
      leftIcon={
        <span className="text-text-secondary text-sm font-medium">
          {countryCode}
        </span>
      }
      onChange={handleChange}
      placeholder="501234567"
    />
  );
};

// Form actions component for consistent button layouts
export interface FormActionsProps {
  children: React.ReactNode;
  className?: string;
  align?: 'left' | 'center' | 'right' | 'between';
}

const FormActions: React.FC<FormActionsProps> = ({
  children,
  className,
  align = 'right',
}) => {
  const alignClasses = {
    left: 'justify-start',
    center: 'justify-center',
    right: 'justify-end',
    between: 'justify-between',
  };

  return (
    <div className={cn(
      'flex items-center gap-3 pt-6',
      alignClasses[align],
      className
    )}>
      {children}
    </div>
  );
};

// Export all components
export {
  BaseFormField,
  TextField,
  PasswordField,
  SelectField,
  CheckboxField,
  RadioGroup,
  TextareaField,
  PhoneField,
  FormActions,
};