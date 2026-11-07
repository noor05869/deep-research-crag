import React from 'react';
import { CheckCircle2, AlertCircle } from 'lucide-react';
import type { ResearchResponse } from '../types';

interface AuditBannerProps {
  data: ResearchResponse;
}

export const AuditBanner: React.FC<AuditBannerProps> = ({ data }) => {
  const isGrounded = data.hallucination_grade === 'grounded';

  return (
    <div className="flex flex-wrap items-center justify-between gap-3 py-3 px-4 rounded-lg bg-[#111216] border border-zinc-800 text-xs text-zinc-300 mb-6">
      <div className="flex items-center space-x-2">
        {isGrounded ? (
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
        ) : (
          <AlertCircle className="w-4 h-4 text-rose-400" />
        )}
        <span className="font-medium text-zinc-200">
          {isGrounded ? 'Factually Grounded' : 'Flagged Unverified Claims'}
        </span>
        <span className="text-zinc-600">•</span>
        <span className="text-zinc-400">
          {data.web_search_needed ? 'DuckDuckGo Live Search' : 'Internal Qdrant Knowledge'}
        </span>
      </div>

      <div className="flex items-center space-x-4 text-zinc-400 font-mono text-[11px]">
        <span>{data.documents_count} chunks evaluated</span>
        <span className="text-zinc-600">•</span>
        <span>Loop {data.loop_step}/3</span>
        <span className="text-zinc-600">•</span>
        <span>{data.execution_time_seconds}s latency</span>
      </div>
    </div>
  );
};
