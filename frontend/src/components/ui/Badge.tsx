import type { ReactNode } from 'react';
import { cn } from '@/utils/cn';
import './Badge.css';

type BadgeVariant = 'success' | 'warning' | 'danger' | 'info' | 'neutral' | 'accent';

interface BadgeProps {
  variant?: BadgeVariant;
  dot?: boolean;
  size?: 'sm' | 'md';
  children: ReactNode;
  className?: string;
}

export function Badge({ variant = 'neutral', dot = false, size = 'md', children, className }: BadgeProps) {
  return (
    <span className={cn('gf-badge', `gf-badge--${variant}`, size === 'sm' && 'gf-badge--sm', className)}>
      {dot && <span className="gf-badge__dot" aria-hidden="true" />}
      {children}
    </span>
  );
}
