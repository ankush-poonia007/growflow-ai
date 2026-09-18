import type { ReactNode } from 'react';
import { cn } from '@/utils/cn';
import './EmptyState.css';

export interface EmptyStateProps {
  title: string;
  description: string;
  icon?: ReactNode;
  action?: ReactNode;
  secondaryAction?: ReactNode;
  className?: string;
  compact?: boolean;
}

export function EmptyState({
  title,
  description,
  icon,
  action,
  secondaryAction,
  className,
  compact = false,
}: EmptyStateProps) {
  return (
    <div className={cn('gf-empty-state', compact && 'gf-empty-state--compact', className)}>
      {icon && <div className="gf-empty-state__icon" aria-hidden="true">{icon}</div>}
      <h3 className="gf-empty-state__title">{title}</h3>
      <p className="gf-empty-state__description">{description}</p>
      {(action || secondaryAction) && (
        <div className="gf-empty-state__actions">
          {action}
          {secondaryAction}
        </div>
      )}
    </div>
  );
}
