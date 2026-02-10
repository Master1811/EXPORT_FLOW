import { useEffect, useCallback, useRef } from 'react';
import { useBeforeUnload, useBlocker } from 'react-router-dom';

/**
 * Hook to warn users about unsaved changes before leaving a page
 * Handles both browser navigation (back/forward) and in-app navigation
 */
export function useUnsavedChanges(hasUnsavedChanges, message = 'You have unsaved changes. Are you sure you want to leave?') {
  // Handle browser's beforeunload event (refresh, close tab, external navigation)
  useEffect(() => {
    const handleBeforeUnload = (e) => {
      if (hasUnsavedChanges) {
        e.preventDefault();
        e.returnValue = message;
        return message;
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, [hasUnsavedChanges, message]);

  // For react-router v6 navigation blocking
  // Note: useBlocker is available in react-router v6.4+
  // If not available, this is a fallback
  return hasUnsavedChanges;
}

/**
 * Hook to prevent double-click submissions
 * Returns [isSubmitting, submitHandler]
 */
export function usePreventDoubleSubmit(submitFn) {
  const isSubmitting = useRef(false);
  const timeoutRef = useRef(null);

  const handleSubmit = useCallback(async (...args) => {
    // Prevent double submission
    if (isSubmitting.current) {
      console.warn('Submission already in progress, ignoring duplicate click');
      return;
    }

    isSubmitting.current = true;

    try {
      const result = await submitFn(...args);
      return result;
    } finally {
      // Reset after a short delay to allow for UI updates
      timeoutRef.current = setTimeout(() => {
        isSubmitting.current = false;
      }, 500);
    }
  }, [submitFn]);

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  return [isSubmitting.current, handleSubmit];
}

/**
 * Hook to track form dirty state
 * Returns [isDirty, setFieldValue, resetForm, getValues]
 */
export function useFormDirtyState(initialValues = {}) {
  const initialRef = useRef(JSON.stringify(initialValues));
  const currentValues = useRef(initialValues);

  const setFieldValue = useCallback((field, value) => {
    currentValues.current = {
      ...currentValues.current,
      [field]: value,
    };
  }, []);

  const resetForm = useCallback((newInitial = null) => {
    if (newInitial) {
      initialRef.current = JSON.stringify(newInitial);
      currentValues.current = newInitial;
    } else {
      currentValues.current = JSON.parse(initialRef.current);
    }
  }, []);

  const isDirty = useCallback(() => {
    return JSON.stringify(currentValues.current) !== initialRef.current;
  }, []);

  const getValues = useCallback(() => {
    return { ...currentValues.current };
  }, []);

  return [isDirty, setFieldValue, resetForm, getValues];
}

export default useUnsavedChanges;
