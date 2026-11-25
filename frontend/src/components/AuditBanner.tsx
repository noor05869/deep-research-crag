import React from 'react';
import { CheckCircle2, AlertCircle, Clock } from 'lucide-react';
import type { ResearchResponse } from '../types';

interface AuditBannerProps {
  data: ResearchResponse;
}

export const AuditBanner: React.FC<AuditBannerProps> = ({ data }) => {
  const isGrounded = data.hallucination_grade === 'grounded';
  const latency = data.execution_time_seconds;

  // Visual latency performance color indicators
  const latencyBadgeColor =
    latency < 6
      ? 'text-emerald-400 border-emerald-800/80 bg-emerald-950/40'
      : latency < 12
      ? 'text-amber-400 border-amber-800/80 bg-amber-950/40'
      : 'text-rose-400 border-rose-800/80 bg-rose-950/40';

  return (
    <div className="flex flex-wrap items-center justify-between gap-3 py-3 px-4 rounded-lg bg-[#111216] border border-zinc-800 text-xs text-zinc-300 mb-6">
      <div className="flex items-center space-x-2">
        {isGrounded ? (
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
        ) : (
          <AlertCircle className="w-4 h-4 text-rose-400" />
        )}
        <span className="font-medium text-zinc-200">
          {isGrounded ? 'Passed Grounding Audit' : data.hallucination_grade === 'audit_failed'
            ? 'Audit Could Not Complete' : 'Answer Could Not Be Verified'}
        </span>
        <span className="text-zinc-600">•</span>
        <span className="text-zinc-400">
          {data.web_search_needed ? 'DuckDuckGo Live Search' : 'Internal Qdrant Knowledge'}
        </span>
      </div>

      <div className="flex items-center space-x-3 text-zinc-400 font-mono text-[11px]">
        <span>{data.documents_count} chunks evaluated</span>
        <span className="text-zinc-600">•</span>
        <span>Loop {data.loop_step}/3</span>
        <span className="text-zinc-600">•</span>
        <span
          className={`inline-flex items-center space-x-1.5 px-2.5 py-0.5 rounded border font-semibold ${latencyBadgeColor}`}
          title="Total end-to-end execution latency"
        >
          <Clock className="w-3 h-3" />
          <span>{latency.toFixed(2)}s latency</span>
        </span>
      </div>
    </div>
  );
};

