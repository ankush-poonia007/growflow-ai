import { useEffect, useRef } from 'react';
import { useLocation } from 'react-router';

/**
 * ScrollToTop — Centralized route-level scroll restoration.
 *
 * Rules:
 * 1. When navigating between different routes (pathname changes):
 *    - Reset window scroll position to the top (scrollY = 0).
 * 2. When navigating to an anchor on the same page or with an initial hash:
 *    - Scroll to the targeted anchor element without resetting to top.
 * 3. Disables browser default auto-scroll restoration so it does not fight programmatic navigation.
 */
export function ScrollToTop() {
  const { pathname, hash } = useLocation();
  const prevPathnameRef = useRef(pathname);
  const isFirstRenderRef = useRef(true);

  // Configure browser scrollRestoration to manual once on mount
  useEffect(() => {
    if ('scrollRestoration' in window.history) {
      window.history.scrollRestoration = 'manual';
    }
  }, []);

  useEffect(() => {
    // 1. Initial page load
    if (isFirstRenderRef.current) {
      isFirstRenderRef.current = false;
      if (hash) {
        const id = hash.replace(/^#/, '');
        const element = document.getElementById(id);
        if (element) {
          element.scrollIntoView();
          return;
        }
        requestAnimationFrame(() => {
          document.getElementById(id)?.scrollIntoView();
        });
      } else {
        window.scrollTo({ top: 0, left: 0, behavior: 'instant' });
      }
      return;
    }

    // 2. Route/Path changed (navigation between different pages)
    if (prevPathnameRef.current !== pathname) {
      prevPathnameRef.current = pathname;

      // If the new URL includes an anchor (e.g. /documentation#agents)
      if (hash) {
        const id = hash.replace(/^#/, '');
        const element = document.getElementById(id);
        if (element) {
          element.scrollIntoView();
          return;
        }
        requestAnimationFrame(() => {
          const deferredElement = document.getElementById(id);
          if (deferredElement) {
            deferredElement.scrollIntoView();
          } else {
            window.scrollTo({ top: 0, left: 0, behavior: 'instant' });
          }
        });
        return;
      }

      // Normal route navigation: always start at the top
      window.scrollTo({ top: 0, left: 0, behavior: 'instant' });
      return;
    }

    // 3. Same-page hash navigation (pathname did not change)
    if (hash) {
      const id = hash.replace(/^#/, '');
      const element = document.getElementById(id);
      if (element) {
        element.scrollIntoView({ behavior: 'smooth' });
      } else {
        requestAnimationFrame(() => {
          document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
        });
      }
    }
  }, [pathname, hash]);

  return null;
}
