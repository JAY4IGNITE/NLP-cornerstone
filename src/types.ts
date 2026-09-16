export interface CitationSource {
  chunk_id: string;
  source_document: string;
  page: number;
  section: string;
  course_code?: string;
  course_name?: string;
  relevance_score: number;
  is_cited: boolean;
}

export interface ConfidenceBreakdown {
  intent_confidence?: number;
  top_retrieval_score?: number;
  top_rerank_score?: number;
  entity_alignment?: number;
  citation_score?: number;
  guardrail_triggered?: string;
  reason?: string;
}

export interface ChatMessage {
  id: string;
  sender: "user" | "bot";
  text: string;
  timestamp: string;
  intent?: string;
  intent_confidence?: number;
  entities?: {
    course?: string | null;
    canonical_course_name?: string | null;
    course_code?: string | null;
    branch?: string | null;
    semester?: number | null;
    unit?: number | null;
  };
  sources?: CitationSource[];
  is_grounded?: boolean;
  overall_confidence?: number;
  confidence_breakdown?: ConfidenceBreakdown;
  latency_ms?: number;
  feedback?: "thumbs_up" | "thumbs_down" | null;
}

export interface CourseSummary {
  course_code: string;
  course_name: string;
  branch: string;
  semester: number;
  total_units: number;
  sections_count: number;
}

export interface CourseChunk {
  chunk_id: string;
  document_name: string;
  branch: string;
  course_code: string;
  course_name: string;
  semester: number;
  section: string;
  page: number;
  text: string;
  unit?: number;
}

export interface CourseDetail {
  course_code: string;
  course_name: string;
  branch: string;
  semester: number;
  document_name: string;
  chunks: CourseChunk[];
}

export interface SystemHealth {
  status: string;
  service: string;
  version: string;
  uptime_seconds: number;
  qdrant_collection: string;
  indexed_chunks_count: number;
  vector_provider?: string;
  cloudflare_index?: string;
  vector_dimensions?: number;
  is_remote_cloudflare?: boolean;
  models: {
    intent_classifier: string;
    entity_extractor: string;
    dense_embeddings: string;
    reranker: string;
    llm_generator: string;
  };
  thresholds: {
    intent_confidence_threshold: number;
    retrieval_score_threshold: number;
  };
}

export interface ResourceCatalogItem {
  id: string;
  name: string;
  type: string;
  category: string;
  description: string;
  total_chunks: number;
  source_documents: string[];
  status: string;
}

export interface ResourcesCatalogResponse {
  total_integrated_resources: number;
  total_indexed_chunks: number;
  vector_engine: string;
  resources: ResourceCatalogItem[];
  category_breakdown: Record<string, number>;
  source_breakdown: Record<string, number>;
}

export interface CloudflareStatusResponse {
  status: string;
  provider: string;
  index_name: string;
  dimensions: number;
  metric: string;
  total_vectors: number;
  is_remote_authenticated: boolean;
  edge_storage_status: string;
  account_configured: boolean;
  latency_benchmark_ms: number;
}

export interface EvaluationMetrics {
  evaluation: {
    intent_classification?: {
      accuracy: number;
      macro_f1: number;
      weighted_f1: number;
      test_samples: number;
      num_classes: number;
    };
    hybrid_retrieval?: {
      dense_only_mrr: number;
      hybrid_mrr: number;
      dense_only_recall_at_5: number;
      hybrid_recall_at_5: number;
      reranker_top1_precision: number;
    };
    architecture_comparison?: Array<{
      model: string;
      accuracy: number;
      f1_macro: number;
      latency_ms: number;
      inference_speed: string;
    }>;
  };
  dataset: {
    total_queries: number;
    intents: number;
  };
  runtime_metrics: {
    total_queries_served: number;
    average_latency_ms: number;
    intents_supported: number;
    classes: string[];
  };
}
