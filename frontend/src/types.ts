export interface Citation {
  citation_id: string;
  source: string;
  quote: string;
}

export interface ResearchResponse {
  query: string;
  transformed_query: string | null;
  final_response: string;
  citations: Citation[];
  web_search_needed: boolean;
  hallucination_grade: 'grounded' | 'hallucinated' | string | null;
  loop_step: number;
  documents_count: number;
  execution_time_seconds: number;
}

export type PipelineStage = 'idle' | 'retrieving' | 'grading' | 'fallback' | 'generating' | 'evaluating' | 'completed' | 'error';
