export type SortOption =
  | 'recently_created'
  | 'name_asc'
  | 'name_desc'
  | 'complexity_asc'
  | 'complexity_desc';

export interface CatalogFilterState {
  searchQuery: string;
  complexityFilter: string;
  sortBy: SortOption;
}
