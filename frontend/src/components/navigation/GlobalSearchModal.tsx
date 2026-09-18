import { useEffect, useRef, useState, type KeyboardEvent } from 'react';
import { useNavigate } from 'react-router';
import { useSearch } from '@/hooks/useSearch';
import { useOnlineStatus } from '@/hooks/useOnlineStatus';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { EmptyState } from '@/components/ui/EmptyState';
import { InlineErrorState } from '@/components/ui/InlineErrorState';
import type { SearchResultItem } from '@/lib/api/types';
import './GlobalSearchModal.css';

export interface GlobalSearchModalProps {
  isOpen: boolean;
  onClose: () => void;
  workplace?: 'BUILD' | 'SUPERVISE' | 'GOVERN';
}

const CATEGORY_MAP: Record<string, { label: string; value: string }[]> = {
  BUILD: [
    { label: 'All', value: 'all' },
    { label: 'Projects', value: 'projects' },
    { label: 'Tasks', value: 'tasks' },
    { label: 'Milestones', value: 'milestones' },
    { label: 'Documents', value: 'documents' },
    { label: 'Catalog', value: 'definitions' },
    { label: 'Help', value: 'help_requests' },
  ],
  SUPERVISE: [
    { label: 'All', value: 'all' },
    { label: 'Groups', value: 'groups' },
    { label: 'Students', value: 'students' },
    { label: 'Projects', value: 'projects' },
    { label: 'Tasks', value: 'tasks' },
    { label: 'Help', value: 'help_requests' },
    { label: 'Changes', value: 'change_requests' },
    { label: 'Definitions', value: 'definitions' },
  ],
  GOVERN: [
    { label: 'All', value: 'all' },
    { label: 'Users', value: 'users' },
    { label: 'Groups', value: 'groups' },
    { label: 'Definitions', value: 'definitions' },
    { label: 'Projects', value: 'projects' },
    { label: 'Audit', value: 'events' },
    { label: 'Documents', value: 'documents' },
  ],
};

export function GlobalSearchModal({ isOpen, onClose, workplace = 'BUILD' }: GlobalSearchModalProps) {
  const navigate = useNavigate();
  const isOnline = useOnlineStatus();
  const inputRef = useRef<HTMLInputElement>(null);
  const [selectedIndex, setSelectedIndex] = useState<number>(-1);

  const {
    query,
    setQuery,
    category,
    setCategory,
    results,
    total,
    isLoading,
    error,
    clearSearch,
    refetch,
  } = useSearch({ debounceMs: 250, limit: 20 });

  // Focus on open, reset selected index
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
      setSelectedIndex(-1);
      setTimeout(() => {
        inputRef.current?.focus();
      }, 50);
    } else {
      document.body.style.overflow = '';
      clearSearch();
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen, clearSearch]);

  // Keep selected index within bounds
  useEffect(() => {
    if (results.length === 0) {
      setSelectedIndex(-1);
    } else if (selectedIndex >= results.length) {
      setSelectedIndex(results.length - 1);
    }
  }, [results, selectedIndex]);

  const handleSelectResult = (item: SearchResultItem) => {
    if (item.url) {
      navigate(item.url);
      onClose();
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex((prev) => (prev < results.length - 1 ? prev + 1 : 0));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex((prev) => (prev > 0 ? prev - 1 : results.length - 1));
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (selectedIndex >= 0 && selectedIndex < results.length) {
        const item = results[selectedIndex];
        if (item) {
          handleSelectResult(item);
        }
      }
    } else if (e.key === 'Escape') {
      e.preventDefault();
      onClose();
    }
  };

  if (!isOpen) return null;

  const categories = CATEGORY_MAP[workplace] ?? CATEGORY_MAP.BUILD ?? [];

  return (
    <div
      className="gf-search-backdrop"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
      role="presentation"
    >
      <div
        className="gf-search-modal"
        role="dialog"
        aria-modal="true"
        aria-label="Global Workspace Search"
      >
        {/* Offline Banner */}
        {!isOnline && (
          <div className="gf-search-offline-banner" role="alert">
            <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" strokeWidth="2" fill="none">
              <line x1="1" y1="1" x2="23" y2="23" />
              <path d="M16.72 11.06A10.94 10.94 0 0 1 19 12.55" />
              <path d="M5 12.55a10.94 10.94 0 0 1 5.17-2.39" />
              <path d="M10.71 5.05A16 16 0 0 1 22.58 9" />
              <path d="M1.42 9a15.91 15.91 0 0 1 4.7-2.88" />
              <path d="M8.53 16.11a6 6 0 0 1 6.95 0" />
              <line x1="12" y1="20" x2="12.01" y2="20" />
            </svg>
            <span>You are currently offline. Workspace search requires an active network connection.</span>
          </div>
        )}

        {/* Header / Input */}
        <div className="gf-search-modal__header">
          <div className="gf-search-modal__input-wrapper">
            <svg
              className="gf-search-modal__search-icon"
              viewBox="0 0 24 24"
              width="18"
              height="18"
              stroke="currentColor"
              strokeWidth="2"
              fill="none"
              aria-hidden="true"
            >
              <circle cx="11" cy="11" r="8" />
              <line x1="21" y1="21" x2="16.65" y2="16.65" />
            </svg>
            <input
              ref={inputRef}
              type="text"
              className="gf-search-modal__input"
              placeholder={`Search ${workplace.toLowerCase()} workspace...`}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              aria-label="Search workspace"
              aria-autocomplete="list"
              aria-controls="gf-search-results"
            />
            {query && (
              <button
                type="button"
                className="gf-search-modal__clear-btn"
                onClick={() => {
                  setQuery('');
                  inputRef.current?.focus();
                }}
                aria-label="Clear query"
              >
                <svg viewBox="0 0 24 24" width="14" height="14" stroke="currentColor" strokeWidth="2" fill="none">
                  <line x1="18" y1="6" x2="6" y2="18" />
                  <line x1="6" y1="6" x2="18" y2="18" />
                </svg>
              </button>
            )}
          </div>
          <div className="gf-search-modal__actions">
            <kbd className="gf-search-modal__kbd">ESC</kbd>
            <button
              type="button"
              className="gf-search-modal__close-btn"
              onClick={onClose}
              aria-label="Close search"
            >
              <svg viewBox="0 0 24 24" width="18" height="18" stroke="currentColor" strokeWidth="2" fill="none">
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>
          </div>
        </div>

        {/* Category Filter Chips */}
        <div className="gf-search-modal__categories" role="toolbar" aria-label="Filter categories">
          {categories.map((cat) => (
            <button
              key={cat.value}
              type="button"
              className={`gf-search-chip ${category === cat.value ? 'gf-search-chip--active' : ''}`}
              onClick={() => setCategory(cat.value)}
              aria-pressed={category === cat.value}
            >
              {cat.label}
            </button>
          ))}
        </div>

        {/* Body Content */}
        <div className="gf-search-modal__body" id="gf-search-results">
          {/* 1. Loading State */}
          {isLoading && (
            <div className="gf-search-modal__loading">
              <LoadingSpinner size="md" label="Searching workspace..." />
            </div>
          )}

          {/* 2. Error State */}
          {!isLoading && error && (
            <div className="gf-search-modal__error">
              <InlineErrorState
                error={error}
                title="Search Error"
                onRetry={refetch}
                retryLabel="Retry search"
              />
            </div>
          )}

          {/* 3. Empty Initial State (No query yet) */}
          {!isLoading && !error && !query.trim() && (
            <EmptyState
              compact
              title={`${workplace} Workspace Search`}
              description={`Role-aware discovery across your authorized ${workplace.toLowerCase()} resources. Type a search term to begin.`}
              icon={
                <svg viewBox="0 0 24 24" width="28" height="28" stroke="currentColor" strokeWidth="1.5" fill="none">
                  <circle cx="11" cy="11" r="8" />
                  <line x1="21" y1="21" x2="16.65" y2="16.65" />
                </svg>
              }
            />
          )}

          {/* 4. No Results Found State */}
          {!isLoading && !error && query.trim() && results.length === 0 && (
            <EmptyState
              compact
              title="No resources found"
              description={`No matching authorized resources found for "${query}". Check your spelling or select a different category.`}
              icon={
                <svg viewBox="0 0 24 24" width="28" height="28" stroke="currentColor" strokeWidth="1.5" fill="none">
                  <circle cx="11" cy="11" r="8" />
                  <line x1="21" y1="21" x2="16.65" y2="16.65" />
                  <line x1="8" y1="11" x2="14" y2="11" />
                </svg>
              }
            />
          )}

          {/* 5. Results List */}
          {!isLoading && !error && results.length > 0 && (
            <ul className="gf-search-results-list" role="listbox" aria-label="Search results">
              {results.map((item, idx) => (
                <li
                  key={`${item.resource_type}-${item.title}-${idx}`}
                  className={`gf-search-result-item ${
                    selectedIndex === idx ? 'gf-search-result-item--selected' : ''
                  }`}
                  role="option"
                  aria-selected={selectedIndex === idx}
                  onClick={() => handleSelectResult(item)}
                  onMouseEnter={() => setSelectedIndex(idx)}
                >
                  <div className="gf-search-result-item__main">
                    <h4 className="gf-search-result-item__title">{item.title}</h4>
                    <p className="gf-search-result-item__subtitle">{item.subtitle}</p>
                  </div>
                  {item.badge && (
                    <span className="gf-search-result-item__badge">{item.badge}</span>
                  )}
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Footer */}
        <div className="gf-search-modal__footer">
          <div className="gf-search-modal__hints">
            <span className="gf-search-modal__hint-item">
              <kbd className="gf-search-modal__kbd">↑</kbd>
              <kbd className="gf-search-modal__kbd">↓</kbd> to navigate
            </span>
            <span className="gf-search-modal__hint-item">
              <kbd className="gf-search-modal__kbd">↵</kbd> to select
            </span>
            <span className="gf-search-modal__hint-item">
              <kbd className="gf-search-modal__kbd">ESC</kbd> to close
            </span>
          </div>
          <div className="gf-search-modal__scope">
            Scope: <span className="gf-search-modal__scope-badge">{workplace}</span>
            {total > 0 && <span> • {total} result{total === 1 ? '' : 's'}</span>}
          </div>
        </div>
      </div>
    </div>
  );
}
