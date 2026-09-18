import React, { type HTMLAttributes } from 'react';
import { cn } from '@/utils/cn';
import './Skeleton.css';

export interface SkeletonProps extends HTMLAttributes<HTMLDivElement> {
  variant?: 'rect' | 'circle' | 'text';
  width?: string | number;
  height?: string | number;
  animate?: boolean;
}

export function Skeleton({
  variant = 'rect',
  width,
  height,
  animate = true,
  className,
  style,
  ...props
}: SkeletonProps) {
  const inlineStyles: React.CSSProperties = {
    width: typeof width === 'number' ? `${width}px` : width,
    height: typeof height === 'number' ? `${height}px` : height,
    ...style,
  };

  return (
    <div
      role="status"
      aria-busy="true"
      aria-label="Loading..."
      className={cn(
        'gf-skeleton',
        animate && 'gf-skeleton--pulse',
        variant === 'circle' && 'gf-skeleton--circle',
        variant === 'text' && 'gf-skeleton--text',
        className,
      )}
      style={inlineStyles}
      {...props}
    />
  );
}
