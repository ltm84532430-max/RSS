import { Archive, Bookmark, ExternalLink, Search } from 'lucide-react'

import { Badge } from '@/components/ui/badge'
import { Button, buttonVariants } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { cn } from '@/lib/utils'
import type { ArticleListItem } from '@/types/api'

export type ArticleFilters = {
  analysisStatus: 'all' | 'pending' | 'queued' | 'processing' | 'completed' | 'failed'
  priorityLevel: 'all' | 'low' | 'medium' | 'high' | 'critical'
  savedOnly: boolean
  archivedOnly: boolean
}

type ArticleFeedProps = {
  articles: ArticleListItem[]
  selectedArticleId: number | null
  sourceNameById: Map<number, string>
  search: string
  filters: ArticleFilters
  onSearchChange: (value: string) => void
  onFiltersChange: (value: ArticleFilters) => void
  onSelectArticle: (articleId: number) => void
  onSaveArticle: (articleId: number) => void
  onArchiveArticle: (articleId: number) => void
}

const STATUS_OPTIONS: ArticleFilters['analysisStatus'][] = [
  'all',
  'queued',
  'processing',
  'completed',
  'failed',
]

const PRIORITY_OPTIONS: ArticleFilters['priorityLevel'][] = [
  'all',
  'low',
  'medium',
  'high',
  'critical',
]

export function ArticleFeed({
  articles,
  selectedArticleId,
  sourceNameById,
  search,
  filters,
  onSearchChange,
  onFiltersChange,
  onSelectArticle,
  onSaveArticle,
  onArchiveArticle,
}: ArticleFeedProps) {
  return (
    <div className="flex h-full flex-col">
      <div className="border-b border-slate-200 px-4 py-4">
        <div className="flex items-center justify-between gap-3">
          <div>
            <h2 className="text-sm font-semibold text-slate-950">Article stream</h2>
            <p className="mt-1 text-sm text-slate-500">
              Filter by analysis status, priority, and reading state
            </p>
          </div>
        </div>

        <div className="relative mt-4">
          <Search className="pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2 text-slate-400" />
          <Input
            value={search}
            onChange={(event) => onSearchChange(event.target.value)}
            placeholder="Search titles, summaries, or article content"
            className="h-10 rounded-lg pl-9"
          />
        </div>

        <div className="mt-4 flex flex-col gap-3">
          <div className="flex flex-wrap gap-2">
            {STATUS_OPTIONS.map((status) => (
              <FilterButton
                key={status}
                active={filters.analysisStatus === status}
                onClick={() => onFiltersChange({ ...filters, analysisStatus: status })}
              >
                {status}
              </FilterButton>
            ))}
          </div>
          <div className="flex flex-wrap gap-2">
            {PRIORITY_OPTIONS.map((priority) => (
              <FilterButton
                key={priority}
                active={filters.priorityLevel === priority}
                onClick={() => onFiltersChange({ ...filters, priorityLevel: priority })}
              >
                {priority}
              </FilterButton>
            ))}
            <FilterButton
              active={filters.savedOnly}
              onClick={() => onFiltersChange({ ...filters, savedOnly: !filters.savedOnly })}
            >
              saved
            </FilterButton>
            <FilterButton
              active={filters.archivedOnly}
              onClick={() => onFiltersChange({ ...filters, archivedOnly: !filters.archivedOnly })}
            >
              archived
            </FilterButton>
          </div>
        </div>
      </div>

      <div className="min-h-0 flex-1 overflow-y-auto p-3">
        {articles.length === 0 ? (
          <div className="flex h-full min-h-[360px] items-center justify-center rounded-lg border border-dashed border-slate-200 bg-slate-50 px-6 text-center text-sm text-slate-500">
            No articles match the current filters. Fetch a source or loosen the filters.
          </div>
        ) : (
          <div className="flex flex-col gap-3">
            {articles.map((article) => {
              const active = article.id === selectedArticleId

              return (
                <article
                  key={article.id}
                  className={cn(
                    'rounded-lg border p-4 transition-colors',
                    active
                      ? 'border-blue-200 bg-blue-50/60'
                      : 'border-slate-200 bg-white hover:border-slate-300',
                  )}
                >
                  <button type="button" onClick={() => onSelectArticle(article.id)} className="w-full text-left">
                    <div className="flex items-start justify-between gap-4">
                      <div className="min-w-0">
                        <h3 className="line-clamp-2 text-base font-semibold text-slate-950">
                          {article.title}
                        </h3>
                        <div className="mt-1 flex flex-wrap items-center gap-2 text-xs text-slate-500">
                          <span>{formatDate(article.published_at ?? article.created_at)}</span>
                          {article.source_id ? <span>{sourceNameById.get(article.source_id)}</span> : null}
                          {article.author ? <span>{article.author}</span> : null}
                          {article.language ? <span>{article.language.toUpperCase()}</span> : null}
                        </div>
                      </div>
                      <div className="flex shrink-0 flex-col items-end gap-2">
                        <StatusBadge status={article.analysis_status} />
                        {article.analysis?.priority_level ? (
                          <Badge variant="secondary">{article.analysis.priority_level}</Badge>
                        ) : null}
                      </div>
                    </div>

                    <p className="mt-3 line-clamp-3 text-sm leading-6 text-slate-600">
                      {article.summary ?? 'No summary yet. Wait for extraction or structured analysis.'}
                    </p>
                  </button>

                  <div className="mt-4 flex items-center justify-between gap-3">
                    <div className="flex flex-wrap items-center gap-2 text-xs text-slate-500">
                      {article.analysis?.recommended_action ? (
                        <Badge variant="outline">{article.analysis.recommended_action}</Badge>
                      ) : null}
                      {article.analysis?.sentiment ? (
                        <Badge variant="outline">{article.analysis.sentiment}</Badge>
                      ) : null}
                      {article.reading_state?.is_saved ? (
                        <Badge variant="secondary">saved</Badge>
                      ) : null}
                      {article.reading_state?.is_archived ? (
                        <Badge variant="secondary">archived</Badge>
                      ) : null}
                    </div>

                    <div className="flex items-center gap-2">
                      <a
                        href={article.url}
                        target="_blank"
                        rel="noreferrer"
                        className={buttonVariants({ variant: 'outline', size: 'xs' })}
                      >
                        <ExternalLink data-icon="inline-start" />
                        Open
                      </a>
                      <Button variant="outline" size="xs" onClick={() => onSaveArticle(article.id)}>
                        <Bookmark data-icon="inline-start" />
                        Save
                      </Button>
                      <Button variant="outline" size="xs" onClick={() => onArchiveArticle(article.id)}>
                        <Archive data-icon="inline-start" />
                        Archive
                      </Button>
                    </div>
                  </div>
                </article>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}

function FilterButton({
  active,
  children,
  onClick,
}: {
  active: boolean
  children: string
  onClick: () => void
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        'rounded-md border px-2 py-1 text-xs capitalize transition-colors',
        active
          ? 'border-blue-200 bg-blue-50 text-blue-700'
          : 'border-slate-200 bg-white text-slate-600 hover:border-slate-300',
      )}
    >
      {children}
    </button>
  )
}

function StatusBadge({ status }: { status: string }) {
  const tone =
    status === 'completed'
      ? 'bg-emerald-50 text-emerald-700'
      : status === 'failed'
        ? 'bg-rose-50 text-rose-700'
        : status === 'processing'
          ? 'bg-amber-50 text-amber-700'
          : 'bg-slate-100 text-slate-600'

  return <span className={cn('rounded-full px-2 py-1 text-[11px] font-medium', tone)}>{status}</span>
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value))
}
