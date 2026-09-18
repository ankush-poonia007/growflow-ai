/**
 * GrowFlow — Search API Types (Phase 8 Batch 3)
 */

export interface SearchResultItem {
  id?: string | null;
  title: string;
  subtitle: string;
  resource_type: string;
  url: string;
  badge: string;
  metadata: Record<string, unknown>;
}

export interface SearchResponseData {
  query: string;
  workplace: 'BUILD' | 'SUPERVISE' | 'GOVERN';
  total: number;
  results: SearchResultItem[];
}
