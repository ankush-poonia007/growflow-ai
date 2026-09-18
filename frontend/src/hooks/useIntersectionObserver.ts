import { useEffect, useRef, useState, type RefObject } from 'react';

interface UseIntersectionOptions {
  threshold?: number;
  rootMargin?: string;
  /** If true, unobserve after first intersection (one-shot reveal). Default: true. */
  once?: boolean;
}

/**
 * Observe an element's intersection with the viewport.
 * Returns a ref to attach and a boolean indicating visibility.
 */
export function useIntersectionObserver<T extends HTMLElement = HTMLDivElement>(
  options: UseIntersectionOptions = {},
): [RefObject<T | null>, boolean] {
  const { threshold = 0.05, rootMargin = '0px 0px -20px 0px', once = true } = options;
  const ref = useRef<T | null>(null);

  // Default to visible if user prefers reduced motion
  const [isVisible, setIsVisible] = useState(() => {
    if (typeof window !== 'undefined' && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      return true;
    }
    return false;
  });

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    // Immediately reveal if reduced motion is requested
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      setIsVisible(true);
      return;
    }

    // Immediately reveal if URL hash targets this element or a child inside it
    const checkHashMatch = () => {
      if (window.location.hash) {
        const hashId = window.location.hash.replace('#', '');
        if (el.id === hashId || el.querySelector(`#${CSS.escape(hashId)}`)) {
          setIsVisible(true);
          return true;
        }
      }
      return false;
    };

    if (checkHashMatch()) {
      return;
    }

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry?.isIntersecting) {
          setIsVisible(true);
          if (once) observer.unobserve(el);
        } else if (!once) {
          setIsVisible(false);
        }
      },
      { threshold, rootMargin },
    );

    observer.observe(el);

    // Also respond dynamically to hash navigation
    window.addEventListener('hashchange', checkHashMatch);

    // Fallback safety timer: guarantee visibility within 2.5s even if observer conditions are delayed
    const safetyTimer = setTimeout(() => {
      setIsVisible(true);
    }, 2500);

    return () => {
      observer.disconnect();
      window.removeEventListener('hashchange', checkHashMatch);
      clearTimeout(safetyTimer);
    };
  }, [threshold, rootMargin, once]);

  return [ref, isVisible];
}
