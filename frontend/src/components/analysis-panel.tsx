import { useMemo, useState } from 'react'
import type { ReactNode } from 'react'
import {
  AlertCircle,
  BrainCircuit,
  ExternalLink,
  FileText,
  Minus,
  Plus,
  RefreshCcw,
} from 'lucide-react'

import { Badge } from '@/components/ui/badge'
import { Button, buttonVariants } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { cn } from '@/lib/utils'
import type { AnalysisRead, ArticleDetail } from '@/types/api'

type AnalysisPanelProps = {
  article: ArticleDetail
  sourceName: string | null | undefined
  analysis: AnalysisRead
  loading: boolean
  busy: boolean
  onAnalyze: () => void
}

type PanelTab = 'read' | 'ai'

export function AnalysisPanel({
  article,
  sourceName,
  analysis,
  loading,
  busy,
  onAnalyze,
}: AnalysisPanelProps) {
  const [tab, setTab] = useState<PanelTab>('read')
  const [fontScale, setFontScale] = useState(16)

  const actionLabel = useMemo(() => {
    if (analysis.status === 'completed' || analysis.status === 'failed') {
      return 'Reanalyze'
    }
    if (analysis.status === 'queued' || analysis.status === 'processing') {
      return 'Queued'
    }
    return 'Start analysis'
  }, [analysis.status])

  const actionDisabled = busy || analysis.status === 'queued' || analysis.status === 'processing'

  return (
    <div className="flex h-full flex-col">
      <div className="border-b border-slate-200 px-4 py-4">
        <div className="flex items-start justify-between gap-3">
          <div>
            <h2 className="text-sm font-semibold text-slate-950">Reading workspace</h2>
            <p className="mt-1 line-clamp-2 text-sm text-slate-500">{article.title}</p>
            <div className="mt-2 flex flex-wrap gap-2 text-xs text-slate-500">
              {sourceName ? <span>{sourceName}</span> : null}
              <span>{formatDate(article.published_at ?? article.created_at)}</span>
              {article.author ? <span>{article.author}</span> : null}
            </div>
          </div>
          <a
            href={article.url}
            target="_blank"
            rel="noreferrer"
            className={buttonVariants({ variant: 'outline', size: 'sm' })}
          >
            <ExternalLink data-icon="inline-start" />
            Open
          </a>
        </div>

        <div className="mt-4 flex items-center justify-between gap-3">
          <div className="flex gap-2">
            <TabButton active={tab === 'read'} onClick={() => setTab('read')}>
              <FileText className="size-4" />
              Read
            </TabButton>
            <TabButton active={tab === 'ai'} onClick={() => setTab('ai')}>
              <BrainCircuit className="size-4" />
              AI
            </TabButton>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="icon-sm"
              onClick={() => setFontScale((value) => Math.max(14, value - 1))}
              disabled={tab !== 'read'}
            >
              <Minus />
            </Button>
            <div className="w-12 text-center text-sm text-slate-600">{fontScale}px</div>
            <Button
              variant="outline"
              size="icon-sm"
              onClick={() => setFontScale((value) => Math.min(22, value + 1))}
              disabled={tab !== 'read'}
            >
              <Plus />
            </Button>
          </div>
        </div>
      </div>

      <div className="min-h-0 flex-1 overflow-y-auto">
        {tab === 'read' ? (
          <article className="mx-auto max-w-3xl px-5 py-6">
            <div className="mb-5 flex flex-wrap gap-2">
              <Badge variant="secondary">{article.analysis_status}</Badge>
              {analysis.priority_level ? <Badge variant="outline">{analysis.priority_level}</Badge> : null}
              {analysis.recommended_action ? (
                <Badge variant="outline">{analysis.recommended_action}</Badge>
              ) : null}
            </div>
            <h3 className="text-2xl font-semibold leading-8 text-slate-950">{article.title}</h3>
            {article.summary ? (
              <p className="mt-4 text-base leading-7 text-slate-600">{article.summary}</p>
            ) : null}
            <Separator className="my-5" />
            <div
              className="whitespace-pre-wrap text-slate-800"
              style={{
                fontSize: `${fontScale}px`,
                lineHeight: 1.85,
              }}
            >
              {article.content ?? article.summary ?? 'No article content extracted yet.'}
            </div>
          </article>
        ) : (
          <div className="flex flex-col">
            <div className="border-b border-slate-200 px-4 py-4">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <div className="text-sm font-semibold text-slate-950">AI analysis</div>
                  <div className="mt-1 text-sm text-slate-500">
                    You decide when to run the three-layer analysis.
                  </div>
                </div>
                <Button variant="outline" size="sm" disabled={actionDisabled} onClick={onAnalyze}>
                  <RefreshCcw data-icon="inline-start" />
                  {actionLabel}
                </Button>
              </div>

              <div className="mt-4 grid grid-cols-2 gap-2">
                <Metric label="status" value={analysis.status} />
                <Metric label="priority" value={analysis.priority_level ?? '-'} />
                <Metric label="sentiment" value={analysis.sentiment ?? '-'} />
                <Metric label="importance" value={String(analysis.importance_score ?? '-')} />
              </div>
            </div>

            {analysis.error_message ? (
              <div className="m-4 rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
                <div className="flex items-center gap-2 font-medium">
                  <AlertCircle className="size-4" />
                  Analysis failed
                </div>
                <p className="mt-2 leading-6">{analysis.error_message}</p>
              </div>
            ) : null}

            <LayerSection
              title="Structured Layer"
              subtitle="Summary, entities, key facts, sentiment, and scoring."
              data={analysis.structured_result}
              loading={loading}
            />
            <Separator />
            <LayerSection
              title="Cognitive Layer"
              subtitle="Insight, drivers, trend type, impact scope, and uncertainty."
              data={analysis.cognitive_result}
              loading={loading}
            />
            <Separator />
            <LayerSection
              title="Decision Layer"
              subtitle="Priority, recommended action, impact direction, and watchlist tags."
              data={analysis.decision_result}
              loading={loading}
            />
          </div>
        )}
      </div>
    </div>
  )
}

function TabButton({
  active,
  children,
  onClick,
}: {
  active: boolean
  children: ReactNode
  onClick: () => void
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        'inline-flex items-center gap-2 rounded-md border px-3 py-1.5 text-sm transition-colors',
        active
          ? 'border-blue-200 bg-blue-50 text-blue-700'
          : 'border-slate-200 bg-white text-slate-600 hover:border-slate-300',
      )}
    >
      {children}
    </button>
  )
}

function Metric({
  label,
  value,
  className,
}: {
  label: string
  value: string
  className?: string
}) {
  return (
    <div className={cn('rounded-lg border border-slate-200 bg-slate-50 px-3 py-2', className)}>
      <div className="text-[11px] font-medium uppercase tracking-[0.08em] text-slate-500">{label}</div>
      <div className="mt-1 text-sm font-medium text-slate-800">{value}</div>
    </div>
  )
}

type LayerSectionProps = {
  title: string
  subtitle: string
  data: Record<string, unknown> | null
  loading: boolean
}

function LayerSection({ title, subtitle, data, loading }: LayerSectionProps) {
  return (
    <section className="px-4 py-4">
      <div className="flex items-center gap-2">
        <BrainCircuit className="size-4 text-blue-600" />
        <h3 className="text-sm font-semibold text-slate-950">{title}</h3>
      </div>
      <p className="mt-1 text-sm text-slate-500">{subtitle}</p>

      <div className="mt-4 rounded-lg border border-slate-200 bg-slate-50 px-3 py-3">
        {loading ? (
          <div className="text-sm text-slate-500">Loading analysis...</div>
        ) : data ? (
          <div className="flex flex-col gap-3">
            {Object.entries(data).map(([key, value]) => (
              <div key={key} className="grid grid-cols-[112px_minmax(0,1fr)] gap-3">
                <div className="text-xs font-medium uppercase tracking-[0.08em] text-slate-500">
                  {key.replace(/_/g, ' ')}
                </div>
                <div className="text-sm leading-6 text-slate-700">{renderValue(value)}</div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-sm text-slate-500">No result has been written for this layer yet.</div>
        )}
      </div>
    </section>
  )
}

function renderValue(value: unknown): ReactNode {
  if (value === null || value === undefined) {
    return '-'
  }

  if (typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean') {
    return String(value)
  }

  if (Array.isArray(value)) {
    if (value.length === 0) {
      return '-'
    }

    return (
      <div className="flex flex-wrap gap-2">
        {value.map((item, index) => (
          <span
            key={`${String(item)}-${index}`}
            className="rounded-md border border-slate-200 bg-white px-2 py-1 text-xs text-slate-700"
          >
            {typeof item === 'object' ? JSON.stringify(item) : String(item)}
          </span>
        ))}
      </div>
    )
  }

  if (typeof value === 'object') {
    return (
      <div className="flex flex-col gap-2">
        {Object.entries(value as Record<string, unknown>).map(([nestedKey, nestedValue]) => (
          <div key={nestedKey} className="rounded-md border border-slate-200 bg-white px-3 py-2">
            <div className="text-xs font-medium uppercase tracking-[0.08em] text-slate-500">
              {nestedKey.replace(/_/g, ' ')}
            </div>
            <div className="mt-1 text-sm text-slate-700">{renderValue(nestedValue)}</div>
          </div>
        ))}
      </div>
    )
  }

  return String(value)
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value))
}
