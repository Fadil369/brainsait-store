import { useState, useCallback, useEffect } from 'react';
import { useForm, UseFormProps, FieldValues, Path, UseFormReturn } from 'react-hook-form';

// Common form validation patterns
export const validationPatterns = {
  email: {
    pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
    message: 'Please enter a valid email address',
  },
  saudiPhone: {
    pattern: /^(\+966|966|0)?[5][0-9]{8}$/,
    message: 'Please enter a valid Saudi phone number',
  },
  required: {
    required: true,
    message: 'This field is required',
  },
  minLength: (length: number) => ({
    minLength: length,
    message: `Minimum ${length} characters required`,
  }),
  maxLength: (length: number) => ({
    maxLength: length,
    message: `Maximum ${length} characters allowed`,
  }),
};

// Common form configurations
export const defaultFormConfig = {
  mode: 'onChange' as const,
  reValidateMode: 'onChange' as const,
  shouldFocusError: true,
};

// Enhanced form hook with common patterns
export function useEnhancedForm<TFormData extends FieldValues>(
  props?: UseFormProps<TFormData> & {
    onSubmitSuccess?: (data: TFormData) => void;
    onSubmitError?: (error: Error) => void;
    validateOnMount?: boolean;
    resetOnSuccess?: boolean;
  }
) {
  const {
    onSubmitSuccess,
    onSubmitError,
    validateOnMount = false,
    resetOnSuccess = false,
    ...formProps
  } = props || {};

  const form = useForm<TFormData>({
    ...defaultFormConfig,
    ...formProps,
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitSuccess, setSubmitSuccess] = useState(false);

  // Validate on mount if requested
  useEffect(() => {
    if (validateOnMount) {
      form.trigger();
    }
  }, [form, validateOnMount]);

  // Enhanced submit handler
  const handleSubmit = useCallback(
    (submitFn: (data: TFormData) => Promise<any> | any) =>
      form.handleSubmit(async (data) => {
        setIsSubmitting(true);
        setSubmitError(null);
        setSubmitSuccess(false);

        try {
          const result = await submitFn(data);
          setSubmitSuccess(true);
          onSubmitSuccess?.(data);
          
          if (resetOnSuccess) {
            form.reset();
          }
          
          return result;
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'An error occurred';
          setSubmitError(errorMessage);
          onSubmitError?.(error instanceof Error ? error : new Error(errorMessage));
          throw error;
        } finally {
          setIsSubmitting(false);
        }
      }),
    [form, onSubmitSuccess, onSubmitError, resetOnSuccess]
  );

  // Enhanced field registration with common validations
  const registerField = useCallback(
    <TField extends Path<TFormData>>(
      name: TField,
      validation?: {
        required?: boolean;
        email?: boolean;
        saudiPhone?: boolean;
        minLength?: number;
        maxLength?: number;
        pattern?: RegExp;
        custom?: (value: any) => string | boolean;
      }
    ) => {
      const rules: any = {};

      if (validation?.required) {
        rules.required = validationPatterns.required.message;
      }

      if (validation?.email) {
        rules.pattern = {
          value: validationPatterns.email.pattern,
          message: validationPatterns.email.message,
        };
      }

      if (validation?.saudiPhone) {
        rules.pattern = {
          value: validationPatterns.saudiPhone.pattern,
          message: validationPatterns.saudiPhone.message,
        };
      }

      if (validation?.minLength) {
        rules.minLength = {
          value: validation.minLength,
          message: validationPatterns.minLength(validation.minLength).message,
        };
      }

      if (validation?.maxLength) {
        rules.maxLength = {
          value: validation.maxLength,
          message: validationPatterns.maxLength(validation.maxLength).message,
        };
      }

      if (validation?.pattern) {
        rules.pattern = {
          value: validation.pattern,
          message: 'Invalid format',
        };
      }

      if (validation?.custom) {
        rules.validate = validation.custom;
      }

      return form.register(name, rules);
    },
    [form]
  );

  return {
    ...form,
    // Enhanced state
    isSubmitting,
    submitError,
    submitSuccess,
    isValid: form.formState.isValid,
    isDirty: form.formState.isDirty,
    
    // Enhanced methods
    handleSubmit,
    registerField,
    
    // Convenience methods
    clearErrors: () => {
      form.clearErrors();
      setSubmitError(null);
    },
    clearSubmitState: () => {
      setSubmitError(null);
      setSubmitSuccess(false);
    },
    resetForm: () => {
      form.reset();
      setSubmitError(null);
      setSubmitSuccess(false);
    },
  };
}

// Hook for multi-step forms
export function useMultiStepForm<TFormData extends FieldValues>(
  steps: string[],
  formProps?: UseFormProps<TFormData>
) {
  const [currentStep, setCurrentStep] = useState(0);
  const [completedSteps, setCompletedSteps] = useState<Set<number>>(new Set());
  const form = useEnhancedForm<TFormData>(formProps);

  const isFirstStep = currentStep === 0;
  const isLastStep = currentStep === steps.length - 1;
  const currentStepName = steps[currentStep];

  const goToStep = useCallback((step: number) => {
    if (step >= 0 && step < steps.length) {
      setCurrentStep(step);
    }
  }, [steps.length]);

  const nextStep = useCallback(async () => {
    // Validate current step before proceeding
    const isStepValid = await form.trigger();
    
    if (isStepValid && !isLastStep) {
      setCompletedSteps(prev => new Set(prev).add(currentStep));
      setCurrentStep(prev => prev + 1);
    }
    
    return isStepValid;
  }, [form, isLastStep, currentStep]);

  const prevStep = useCallback(() => {
    if (!isFirstStep) {
      setCurrentStep(prev => prev - 1);
    }
  }, [isFirstStep]);

  const markStepComplete = useCallback((step: number) => {
    setCompletedSteps(prev => new Set(prev).add(step));
  }, []);

  const isStepComplete = useCallback((step: number) => {
    return completedSteps.has(step);
  }, [completedSteps]);

  return {
    ...form,
    // Step management
    currentStep,
    currentStepName,
    steps,
    isFirstStep,
    isLastStep,
    completedSteps: Array.from(completedSteps),
    
    // Step navigation
    goToStep,
    nextStep,
    prevStep,
    
    // Step validation
    markStepComplete,
    isStepComplete,
    
    // Progress
    progress: ((currentStep + 1) / steps.length) * 100,
  };
}

// Hook for form field arrays (dynamic lists)
export function useFieldArray<TFormData extends FieldValues, TFieldArray>(
  form: UseFormReturn<TFormData>,
  name: Path<TFormData>,
  defaultItem: TFieldArray
) {
  const [items, setItems] = useState<TFieldArray[]>([]);

  const addItem = useCallback((item?: Partial<TFieldArray>) => {
    const newItem = { ...defaultItem, ...item };
    setItems(prev => [...prev, newItem]);
  }, [defaultItem]);

  const removeItem = useCallback((index: number) => {
    setItems(prev => prev.filter((_, i) => i !== index));
  }, []);

  const moveItem = useCallback((fromIndex: number, toIndex: number) => {
    setItems(prev => {
      const newItems = [...prev];
      const [movedItem] = newItems.splice(fromIndex, 1);
      newItems.splice(toIndex, 0, movedItem);
      return newItems;
    });
  }, []);

  const updateItem = useCallback((index: number, updates: Partial<TFieldArray>) => {
    setItems(prev => prev.map((item, i) => 
      i === index ? { ...item, ...updates } : item
    ));
  }, []);

  // Sync with form
  useEffect(() => {
    form.setValue(name, items as any);
  }, [form, name, items]);

  return {
    items,
    addItem,
    removeItem,
    moveItem,
    updateItem,
    count: items.length,
  };
}

// Hook for form persistence (localStorage)
export function useFormPersistence<TFormData extends FieldValues>(
  key: string,
  form: UseFormReturn<TFormData>,
  debounceMs: number = 1000
) {
  const [isSaving, setIsSaving] = useState(false);

  // Load saved data on mount
  useEffect(() => {
    const savedData = localStorage.getItem(key);
    if (savedData) {
      try {
        const parsedData = JSON.parse(savedData);
        form.reset(parsedData);
      } catch (error) {
        console.warn('Failed to parse saved form data:', error);
      }
    }
  }, [key, form]);

  // Save data when form changes
  useEffect(() => {
    const subscription = form.watch((data) => {
      setIsSaving(true);
      
      const timeoutId = setTimeout(() => {
        localStorage.setItem(key, JSON.stringify(data));
        setIsSaving(false);
      }, debounceMs);

      return () => clearTimeout(timeoutId);
    });

    return () => subscription.unsubscribe();
  }, [form, key, debounceMs]);

  const clearSavedData = useCallback(() => {
    localStorage.removeItem(key);
  }, [key]);

  return {
    isSaving,
    clearSavedData,
  };
}

// Common form field components with consistent error handling
export function useFormField<TFormData extends FieldValues>(
  form: UseFormReturn<TFormData>,
  name: Path<TFormData>
) {
  const fieldState = form.getFieldState(name);
  const error = fieldState.error?.message;
  const hasError = !!error;

  return {
    name,
    error,
    hasError,
    isDirty: fieldState.isDirty,
    isTouched: fieldState.isTouched,
    isValid: !hasError,
    register: form.register(name),
    value: form.watch(name),
    setValue: (value: any) => form.setValue(name, value),
    clearError: () => form.clearErrors(name),
  };
}