import React, { type ReactNode } from 'react';
import { Link } from 'react-router';
import { cn } from '@/utils/cn';
import './PageHeader.css';

export interface BreadcrumbItem {
  label: string;
  to?: string;
}

export interface PageHeaderProps {
  title: string;
  description?: string;
  eyebrow?: string;
  badge?: ReactNode;
  breadcrumbs?: BreadcrumbItem[];
  actions?: ReactNode;
  action?: ReactNode;
  className?: string;
}

export function PageHeader({
  title,
  description,
  eyebrow,
  badge,
  breadcrumbs,
  actions,
  action,
  className,
}: PageHeaderProps) {
  const renderedActions = actions ?? action;
  return (
    <header className={cn('gf-page-header', className)}>
      {breadcrumbs && breadcrumbs.length > 0 && (
        <nav aria-label="Breadcrumb" className="gf-page-header__breadcrumbs">
          {breadcrumbs.map((crumb, idx) => (
            <React.Fragment key={crumb.label}>
              {idx > 0 && (
                <span className="gf-page-header__breadcrumb-sep" aria-hidden="true">
                  /
                </span>
              )}
              {crumb.to ? (
                <Link to={crumb.to} className="gf-page-header__breadcrumb-link">
                  {crumb.label}
                </Link>
              ) : (
                <span aria-current="page">{crumb.label}</span>
              )}
            </React.Fragment>
          ))}
        </nav>
      )}

      <div className="gf-page-header__main">
        <div className="gf-page-header__content">
          {eyebrow && <span className="gf-page-header__eyebrow">{eyebrow}</span>}
          <div className="gf-page-header__title-row">
            <h1 className="gf-page-header__title">{title}</h1>
            {badge && <span className="gf-page-header__badge">{badge}</span>}
          </div>
          {description && <p className="gf-page-header__description">{description}</p>}
        </div>

        {renderedActions && <div className="gf-page-header__actions">{renderedActions}</div>}
      </div>
    </header>
  );
}
