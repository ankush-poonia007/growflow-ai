import type { HTMLAttributes, ReactNode } from 'react';
import { Link, type LinkProps } from 'react-router';
import { cn } from '@/utils/cn';
import './Card.css';

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
  variant?: 'default' | 'bordered' | 'subtle';
  interactive?: boolean;
  as?: 'div' | 'article' | 'section';
}

export function Card({
  children,
  variant = 'default',
  interactive = false,
  as: Component = 'div',
  className,
  ...props
}: CardProps) {
  return (
    <Component
      className={cn(
        'gf-card',
        variant === 'bordered' && 'gf-card--bordered',
        variant === 'subtle' && 'gf-card--subtle',
        interactive && 'gf-card--interactive',
        className,
      )}
      {...props}
    >
      {children}
    </Component>
  );
}

export interface CardLinkProps extends LinkProps {
  children: ReactNode;
  variant?: 'default' | 'bordered' | 'subtle';
}

export function CardLink({
  children,
  variant = 'default',
  className,
  ...props
}: CardLinkProps) {
  return (
    <Link
      className={cn(
        'gf-card',
        'gf-card--interactive',
        variant === 'bordered' && 'gf-card--bordered',
        variant === 'subtle' && 'gf-card--subtle',
        className,
      )}
      {...props}
    >
      {children}
    </Link>
  );
}

export function CardHeader({
  children,
  className,
  ...props
}: HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={cn('gf-card__header', className)} {...props}>
      {children}
    </div>
  );
}

export function CardTitle({
  children,
  className,
  as: Heading = 'h3',
  ...props
}: HTMLAttributes<HTMLHeadingElement> & { as?: 'h2' | 'h3' | 'h4' | 'h5' | 'h6' }) {
  return (
    <Heading className={cn('gf-card__title', className)} {...props}>
      {children}
    </Heading>
  );
}

export function CardDescription({
  children,
  className,
  ...props
}: HTMLAttributes<HTMLParagraphElement>) {
  return (
    <p className={cn('gf-card__description', className)} {...props}>
      {children}
    </p>
  );
}

export function CardContent({
  children,
  className,
  ...props
}: HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={cn('gf-card__content', className)} {...props}>
      {children}
    </div>
  );
}

export function CardFooter({
  children,
  className,
  ...props
}: HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={cn('gf-card__footer', className)} {...props}>
      {children}
    </div>
  );
}
