import { useState, useEffect, useRef, useCallback } from 'react';
import * as apiClient from '@/lib/api/client';
import type { SearchResultItem, SearchResponseData } from '@/lib/api/types';

export interface UseSearchOptions {
  debounceMs?: number;
  limit?: number;
}

export interface UseSearchResult {
  query: string;
  setQuery: (query: string) => void;
  category: string;
  setCategory: (category: string) => void;
  results: SearchResultItem[];
  workplace: 'BUILD' | 'SUPERVISE' | 'GOVERN';
  total: number;
  isLoading: boolean;
  error: string | null;
  clearSearch: () => void;
  refetch: () => void;
}

export function useSearch(options: UseSearchOptions = {}): UseSearchResult {
  const { debounceMs = 300, limit = 20 } = options;
  const [query, setQuery] = useState<string>('');
  const [category, setCategory] = useState<string>('all');
  const [results, setResults] = useState<SearchResultItem[]>([]);
  const [workplace, setWorkplace] = useState<'BUILD' | 'SUPERVISE' | 'GOVERN'>('BUILD');
  const [total, setTotal] = useState<number>(0);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const activeRequestRef = useRef<number>(0);

  const executeSearch = useCallback(
    async (q: string, cat: string) => {
      const cleanQ = q.trim();
      if (!cleanQ) {
        setResults([]);
        setTotal(0);
        setIsLoading(false);
        setError(null);
        return;
      }

      const requestId = ++activeRequestRef.current;
      setIsLoading(true);
      setError(null);

      try {
        const data: SearchResponseData = await apiClient.searchWorkspace({
          q: cleanQ,
          category: cat === 'all' ? undefined : cat,
          limit,
        });

        if (requestId === activeRequestRef.current) {
          setResults(data.results || []);
          setWorkplace(data.workplace || 'BUILD');
          setTotal(data.total || 0);
          setIsLoading(false);
        }
      } catch (err: unknown) {
        if (requestId === activeRequestRef.current) {
          const message = err instanceof Error ? err.message : 'Search failed. Please try again.';
          setError(message);
          setResults([]);
          setTotal(0);
          setIsLoading(false);
        }
      }
    },
    [limit],
  );

  useEffect(() => {
    const cleanQ = query.trim();
    if (!cleanQ) {
      setResults([]);
      setTotal(0);
      setIsLoading(false);
      setError(null);
      return;
    }

    const timer = setTimeout(() => {
      executeSearch(query, category);
    }, debounceMs);

    return () => clearTimeout(timer);
  }, [query, category, debounceMs, executeSearch]);

  const clearSearch = useCallback(() => {
    setQuery('');
    setCategory('all');
    setResults([]);
    setTotal(0);
    setError(null);
    setIsLoading(false);
  }, []);

  const refetch = useCallback(() => {
    executeSearch(query, category);
  }, [executeSearch, query, category]);

  return {
    query,
    setQuery,
    category,
    setCategory,
    results,
    workplace,
    total,
    isLoading,
    error,
    clearSearch,
    refetch,
  };
}
