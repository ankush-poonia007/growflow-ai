/**
GrowFlow Workspace API Types (S16 Blueprint Workspace & S17 Document Viewer)
*/

export interface BlueprintSectionDetail {
  section_key: string;
  title: string;
  structured_content: Record<string, any>;
  markdown: string;
  approved_at: string | null;
}

export interface BlueprintDocumentSummary {
  key: string;
  title: string;
  format: string;
  section_order: number;
}

export interface BlueprintDocumentDetail {
  document_key: string;
  title: string;
  version: string;
  status: string;
  format: string;
  markdown: string;
  structured?: Record<string, any> | null;
  available_documents: BlueprintDocumentSummary[];
  approved_at: string | null;
}
