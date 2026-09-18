import { type HTMLAttributes } from 'react';
import { cn } from '@/utils/cn';
import './LoadingSpinner.css';

export interface LoadingSpinnerProps extends HTMLAttributes<HTMLDivElement> {
  size?: 'sm' | 'md' | 'lg';
  label?: string;
  inline?: boolean;
}

/**
 * Canonical GrowFlow LoadingSpinner component.
 *
 * Provides accessible loading state micro-animation adhering to Soft Intelligence tokens.
 * Sizes:
 * - 'sm': 16px (buttons, inline badges, compact widgets)
 * - 'md': 28px (section headers, content panels)
 * - 'lg': 44px (full-page or large viewport regions)
 */
export function LoadingSpinner({
  size = 'md',
  label = 'Loading...',
  inline = false,
  className,
  ...props
}: LoadingSpinnerProps) {
  return (
    <div
      role="status"
      aria-live="polite"
      aria-label={label}
      className={cn(
        'gf-loading-spinner',
        `gf-loading-spinner--${size}`,
        inline && 'gf-loading-spinner--inline',
        className,
      )}
      {...props}
    >
      <div className="gf-loading-spinner__circle" aria-hidden="true" />
      <span className="gf-loading-spinner__sr-only">{label}</span>
    </div>
  );
}
