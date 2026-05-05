import { useMemo, useState } from 'react'
import { Clock3, FolderTree, Plus, Power, RefreshCcw, Trash2 } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { cn } from '@/lib/utils'
import type { RssSourceCreate, RssSourceRead } from '@/types/api'

type SourceSidebarProps = {
  sources: RssSourceRead[]
  selectedSourceId: number | null
  busySourceId: number | null
  onSelectSource: (sourceId: number | null) => void
  onCreateSource: (payload: RssSourceCreate) => Promise<void>
  onFetchSource: (sourceId: number) => void
  onToggleSource: (source: RssSourceRead) => void
  onDeleteSource: (source: RssSourceRead) => void
}

type DraftSource = {
  name: string
  url: string
  category: string
  fetchIntervalMinutes: string
}

const EMPTY_DRAFT: DraftSource = {
  name: '',
  url: '',
  category: '',
  fetchIntervalMinutes: '60',
}

export function SourceSidebar({
  sources,
  selectedSourceId,
  busySourceId,
  onSelectSource,
  onCreateSource,
  onFetchSource,
  onToggleSource,
  onDeleteSource,
}: SourceSidebarProps) {
  const [draft, setDraft] = useState<DraftSource>(EMPTY_DRAFT)
  const [submitting, setSubmitting] = useState(false)
  const [selectedCategory, setSelectedCategory] = useState<string>('all')

  const categories = useMemo(
    () =>
      Array.from(
        new Set(sources.map((source) => source.category).filter((value): value is string => Boolean(value))),
      ).sort((left, right) => left.localeCompare(right)),
    [sources],
  )

  const visibleSources = useMemo(() => {
    if (selectedCategory === 'all') {
      return sources
    }
    return sources.filter((source) => source.category === selectedCategory)
  }, [selectedCategory, sources])

  async function handleSubmit() {
    if (!draft.name.trim() || !draft.url.trim()) {
      return
    }

    setSubmitting(true)
    try {
      await onCreateSource({
        name: draft.name.trim(),
        url: draft.url.trim(),
        category: draft.category.trim() || null,
        fetch_interval_minutes: Math.max(1, Number(draft.fetchIntervalMinutes) || 60),
        enabled: true,
      })
      setDraft(EMPTY_DRAFT)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="flex h-full flex-col">
      <div className="border-b border-slate-200 px-4 py-4">
        <h2 className="text-sm font-semibold text-slate-950">RSS sources</h2>
        <p className="mt-1 text-sm text-slate-500">{sources.length} feeds in this workspace</p>
      </div>

      <div className="border-b border-slate-200 px-4 py-4">
        <div className="flex flex-col gap-3">
          <Input
            value={draft.name}
            onChange={(event) => setDraft((current) => ({ ...current, name: event.target.value }))}
            placeholder="Source name"
            className="h-9"
          />
          <Input
            value={draft.url}
            onChange={(event) => setDraft((current) => ({ ...current, url: event.target.value }))}
            placeholder="https://example.com/feed.xml"
            className="h-9"
          />
          <div className="grid grid-cols-[minmax(0,1fr)_92px] gap-2">
            <Input
              value={draft.category}
              onChange={(event) =>
                setDraft((current) => ({ ...current, category: event.target.value }))
              }
              placeholder="Category"
              className="h-9"
            />
            <Input
              value={draft.fetchIntervalMinutes}
              onChange={(event) =>
                setDraft((current) => ({
                  ...current,
                  fetchIntervalMinutes: event.target.value.replace(/[^\d]/g, ''),
                }))
              }
              placeholder="60"
              className="h-9"
            />
          </div>
          <Button disabled={submitting} onClick={() => void handleSubmit()}>
            <Plus data-icon="inline-start" />
            Add source
          </Button>
        </div>
      </div>

      <div className="border-b border-slate-200 px-4 py-3">
        <div className="mb-2 flex items-center gap-2 text-xs font-medium uppercase tracking-[0.08em] text-slate-500">
          <FolderTree className="size-3.5" />
          Categories
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            onClick={() => setSelectedCategory('all')}
            className={cn(
              'rounded-md border px-2 py-1 text-xs transition-colors',
              selectedCategory === 'all'
                ? 'border-blue-200 bg-blue-50 text-blue-700'
                : 'border-slate-200 bg-white text-slate-600 hover:border-slate-300',
            )}
          >
            All
          </button>
          {categories.map((category) => (
            <button
              key={category}
              type="button"
              onClick={() => setSelectedCategory(category)}
              className={cn(
                'rounded-md border px-2 py-1 text-xs transition-colors',
                selectedCategory === category
                  ? 'border-blue-200 bg-blue-50 text-blue-700'
                  : 'border-slate-200 bg-white text-slate-600 hover:border-slate-300',
              )}
            >
              {category}
            </button>
          ))}
        </div>
      </div>

      <div className="border-b border-slate-200 px-4 py-3">
        <Button
          variant={selectedSourceId === null ? 'default' : 'outline'}
          size="sm"
          onClick={() => onSelectSource(null)}
        >
          All sources
        </Button>
      </div>

      <div className="min-h-0 flex-1 overflow-y-auto px-2 pb-2">
        <div className="flex flex-col gap-2">
          {visibleSources.map((source) => {
            const active = source.id === selectedSourceId
            const busy = busySourceId === source.id

            return (
              <button
                key={source.id}
                type="button"
                onClick={() => onSelectSource(source.id)}
                className={cn(
                  'rounded-lg border px-3 py-3 text-left transition-colors',
                  active
                    ? 'border-blue-200 bg-blue-50'
                    : 'border-transparent bg-white hover:border-slate-200 hover:bg-slate-50',
                )}
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <div className="truncate text-sm font-medium text-slate-950">{source.name}</div>
                    <div className="mt-1 truncate text-xs text-slate-500">{source.url}</div>
                  </div>
                  <span
                    className={cn(
                      'mt-0.5 shrink-0 rounded-full px-2 py-0.5 text-[11px] font-medium',
                      source.enabled ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-500',
                    )}
                  >
                    {source.enabled ? 'Enabled' : 'Disabled'}
                  </span>
                </div>

                <div className="mt-2 flex items-center justify-between gap-2 text-xs text-slate-500">
                  <div className="flex items-center gap-1.5">
                    <Clock3 className="size-3.5" />
                    <span>{source.fetch_interval_minutes} min</span>
                  </div>
                  {source.category ? (
                    <span className="truncate rounded-md bg-slate-100 px-2 py-1">{source.category}</span>
                  ) : null}
                </div>

                <div className="mt-3 flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="xs"
                    disabled={busy}
                    onClick={(event) => {
                      event.stopPropagation()
                      onFetchSource(source.id)
                    }}
                  >
                    <RefreshCcw data-icon="inline-start" />
                    Fetch
                  </Button>
                  <Button
                    variant="outline"
                    size="xs"
                    disabled={busy}
                    onClick={(event) => {
                      event.stopPropagation()
                      onToggleSource(source)
                    }}
                  >
                    <Power data-icon="inline-start" />
                    {source.enabled ? 'Disable' : 'Enable'}
                  </Button>
                  <Button
                    variant="outline"
                    size="xs"
                    disabled={busy}
                    onClick={(event) => {
                      event.stopPropagation()
                      onDeleteSource(source)
                    }}
                  >
                    <Trash2 data-icon="inline-start" />
                    Delete
                  </Button>
                </div>
              </button>
            )
          })}
        </div>
      </div>
    </div>
  )
}
