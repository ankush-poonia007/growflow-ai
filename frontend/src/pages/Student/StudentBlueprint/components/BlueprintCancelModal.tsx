import { useEffect, useRef } from 'react';
import { Button } from '@/components/ui/Button';

export interface BlueprintCancelModalProps {
  isOpen: boolean;
  isCancelling?: boolean;
  onClose: () => void;
  onConfirm: () => void;
}

export function BlueprintCancelModal({
  isOpen,
  isCancelling = false,
  onClose,
  onConfirm,
}: BlueprintCancelModalProps) {
  const modalRef = useRef<HTMLDivElement | null>(null);
  const previousActiveElementRef = useRef<HTMLElement | null>(null);

  // Manage focus and keyboard interaction
  useEffect(() => {
    if (!isOpen) return;

    // Capture currently focused element to restore upon close
    previousActiveElementRef.current = document.activeElement as HTMLElement | null;

    // Focus "Keep Generating" button by default to prevent accidental cancellation
    const timer = window.setTimeout(() => {
      const firstBtn = modalRef.current?.querySelector<HTMLButtonElement>('button');
      firstBtn?.focus();
    }, 50);

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        if (!isCancelling) {
          e.preventDefault();
          onClose();
        }
        return;
      }

      // Simple focus trap
      if (e.key === 'Tab' && modalRef.current) {
        const focusableElements = modalRef.current.querySelectorAll<HTMLElement>(
          'button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
        );
        if (focusableElements.length === 0) return;

        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];
        if (!firstElement || !lastElement) return;

        if (e.shiftKey) {
          if (document.activeElement === firstElement) {
            e.preventDefault();
            lastElement.focus();
          }
        } else {
          if (document.activeElement === lastElement) {
            e.preventDefault();
            firstElement.focus();
          }
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);

    return () => {
      window.clearTimeout(timer);
      window.removeEventListener('keydown', handleKeyDown);
      if (previousActiveElementRef.current) {
        previousActiveElementRef.current.focus();
      }
    };
  }, [isOpen, isCancelling, onClose]);

  if (!isOpen) return null;

  return (
    <div
      className="gf-blueprint-modal-backdrop"
      onClick={(e) => {
        if (e.target === e.currentTarget && !isCancelling) {
          onClose();
        }
      }}
    >
      <div
        ref={modalRef}
        className="gf-blueprint-modal-card"
        role="dialog"
        aria-modal="true"
        aria-labelledby="blueprint-cancel-modal-title"
        aria-describedby="blueprint-cancel-modal-desc"
      >
        <div className="gf-blueprint-modal-header">
          <div className="gf-blueprint-modal-icon-wrap">
            <svg
              viewBox="0 0 24 24"
              width="24"
              height="24"
              stroke="currentColor"
              strokeWidth="2"
              fill="none"
              aria-hidden="true"
            >
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
          </div>
          <h2 id="blueprint-cancel-modal-title" className="gf-blueprint-modal-title">
            Cancel Blueprint Generation?
          </h2>
        </div>

        <div className="gf-blueprint-modal-body">
          <p id="blueprint-cancel-modal-desc" className="gf-blueprint-modal-desc">
            Are you sure you want to stop generation? Any uncommitted architectural sections from this run will be discarded.
          </p>
        </div>

        <div className="gf-blueprint-modal-footer">
          <Button
            variant="secondary"
            size="md"
            onClick={onClose}
            disabled={isCancelling}
          >
            Keep Generating
          </Button>
          <Button
            variant="primary"
            size="md"
            className="gf-btn--danger"
            onClick={onConfirm}
            disabled={isCancelling}
          >
            {isCancelling ? 'Cancelling...' : 'Yes, Cancel Generation'}
          </Button>
        </div>
      </div>
    </div>
  );
}
