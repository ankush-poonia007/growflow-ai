import type { ReactNode } from 'react';
import { cn } from '@/utils/cn';
import './StatTile.css';

export interface StatTileProps {
  label: string;
  value: ReactNode;
  subtext?: ReactNode;
  icon?: ReactNode;
  tone?: 'default' | 'success' | 'warning' | 'danger' | 'accent';
  className?: string;
}

export function StatTile({
  label,
  value,
  subtext,
  icon,
  tone = 'default',
  className,
}: StatTileProps) {
  return (
    <div
      className={cn(
        'gf-stat-tile',
        tone !== 'default' && `gf-stat-tile--tone-${tone}`,
        className,
      )}
    >
      <div className="gf-stat-tile__header">
        <span className="gf-stat-tile__label">{label}</span>
        {icon && <span className="gf-stat-tile__icon" aria-hidden="true">{icon}</span>}
      </div>
      <div className="gf-stat-tile__value">{value}</div>
      {subtext && <div className="gf-stat-tile__subtext">{subtext}</div>}
    </div>
  );
}
