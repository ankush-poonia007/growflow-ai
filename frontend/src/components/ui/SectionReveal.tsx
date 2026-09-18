import type { ReactNode } from 'react';
import { useIntersectionObserver } from '@/hooks/useIntersectionObserver';
import { cn } from '@/utils/cn';

interface SectionRevealProps {
  children: ReactNode;
  className?: string;
  as?: 'section' | 'div';
  id?: string;
}

/**
 * Wraps content with a scroll-triggered fade-up reveal animation.
 * Respects prefers-reduced-motion via CSS (no JS override needed).
 */
export function SectionReveal({
  children,
  className,
  as = 'section',
  id,
}: SectionRevealProps) {
  const [ref, isVisible] = useIntersectionObserver<HTMLElement>();

  const fullClassName = cn('gf-reveal', isVisible && 'gf-reveal--visible', className);

  if (as === 'div') {
    return (
      <div
        ref={ref as React.RefObject<HTMLDivElement | null>}
        id={id}
        className={fullClassName}
      >
        {children}
      </div>
    );
  }

  return (
    <section
      ref={ref as React.RefObject<HTMLElement | null>}
      id={id}
      className={fullClassName}
    >
      {children}
    </section>
  );
}
