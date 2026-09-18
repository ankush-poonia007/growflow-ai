import { forwardRef, useId, type InputHTMLAttributes, type ReactNode } from 'react';
import { cn } from '@/utils/cn';
import './Input.css';

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  fullWidth?: boolean;
  leftAddon?: ReactNode;
  rightAddon?: ReactNode;
}

/**
 * GrowFlow Canonical Form Input Primitive
 *
 * Implements:
 * - Clear label-to-input association
 * - Semantic error messaging with ARIA attributes
 * - Accessible focus ring using design system tokens
 * - Respects prefers-reduced-motion
 * - Ready for reuse in P04 and A01–A06 authentication workflows
 */
export const Input = forwardRef<HTMLInputElement, InputProps>(function Input(
  {
    label,
    error,
    helperText,
    fullWidth = true,
    required,
    disabled,
    id: explicitId,
    className,
    leftAddon,
    rightAddon,
    ...props
  },
  ref,
) {
  const generatedId = useId();
  const inputId = explicitId || `gf-input-${generatedId}`;
  const errorId = `${inputId}-error`;
  const helperId = `${inputId}-helper`;

  const describedBy = [
    error ? errorId : null,
    helperText ? helperId : null,
  ]
    .filter(Boolean)
    .join(' ') || undefined;

  return (
    <div
      className={cn(
        'gf-form-field',
        fullWidth && 'gf-form-field--full',
        disabled && 'gf-form-field--disabled',
        error && 'gf-form-field--error',
      )}
    >
      {label && (
        <label htmlFor={inputId} className="gf-form-label">
          {label}
          {required && (
            <span className="gf-form-required" aria-hidden="true">
              *
            </span>
          )}
        </label>
      )}

      <div className="gf-input-wrapper">
        {leftAddon && <span className="gf-input-addon gf-input-addon--left">{leftAddon}</span>}

        <input
          ref={ref}
          id={inputId}
          required={required}
          disabled={disabled}
          aria-invalid={!!error}
          aria-required={required}
          aria-describedby={describedBy}
          className={cn(
            'gf-input',
            Boolean(leftAddon) && 'gf-input--with-left-addon',
            Boolean(rightAddon) && 'gf-input--with-right-addon',
            Boolean(error) && 'gf-input--error',
            className,
          )}
          {...props}
        />

        {rightAddon && <span className="gf-input-addon gf-input-addon--right">{rightAddon}</span>}
      </div>

      {error && (
        <span id={errorId} className="gf-form-error" role="alert">
          {error}
        </span>
      )}

      {!error && helperText && (
        <span id={helperId} className="gf-form-helper">
          {helperText}
        </span>
      )}
    </div>
  );
});
