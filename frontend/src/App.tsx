import { useCallback, useEffect, useMemo, useState } from 'react'
import { BrainCircuit, Newspaper, RefreshCcw, Rss } from 'lucide-react'

import { AnalysisPanel } from '@/components/analysis-panel'
import { ArticleFeed, type ArticleFilters } from '@/components/article-feed'
import { SourceSidebar } from '@/components/source-sidebar'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import {
  analyzeArticle,
  archiveArticle,
  createSource,
  deleteSource,
  fetchAnalysis,
  fetchArticleDetail,
  fetchArticles,
  fetchRssSource,
  fetchSources,
  reanalyzeArticle,
  saveArticle,
  updateSource,
} from '@/lib/api'
import type {
  AnalysisRead,
  ArticleDetail,
  ArticleListItem,
  ArticleListResponse,
  RssSourceCreate,
  RssSourceRead,
} from '@/types/api'

const POLLING_STATUSES = new Set(['queued', 'processing'])

function App() {
  const [sources, setSources] = useState<RssSourceRead[]>([])
  const [articles, setArticles] = useState<ArticleListItem[]>([])
  const [total, setTotal] = useState(0)
  const [selectedSourceId, setSelectedSourceId] = useState<number | null>(null)
  const [selectedArticleId, setSelectedArticleId] = useState<number | null>(null)
  const [selectedArticleDetail, setSelectedArticleDetail] = useState<ArticleDetail | null>(null)
  const [selectedAnalysis, setSelectedAnalysis] = useState<AnalysisRead | null>(null)
  const [search, setSearch] = useState('')
  const [articleFilters, setArticleFilters] = useState<ArticleFilters>({
    analysisStatus: 'all',
    priorityLevel: 'all',
    savedOnly: false,
    archivedOnly: false,
  })
  const [sourcesLoading, setSourcesLoading] = useState(true)
  const [articlesLoading, setArticlesLoading] = useState(true)
  const [analysisLoading, setAnalysisLoading] = useState(false)
  const [refreshingArticleId, setRefreshingArticleId] = useState<number | null>(null)
  const [sourceBusyId, setSourceBusyId] = useState<number | null>(null)
  const [actionMessage, setActionMessage] = useState<string | null>(null)

  const sourceNameById = useMemo(
    () => new Map(sources.map((source) => [source.id, source.name])),
    [sources],
  )

  const loadSources = useCallback(async () => {
    setSourcesLoading(true)
    try {
      const nextSources = await fetchSources()
      setSources(nextSources)
      if (selectedSourceId && !nextSources.some((source) => source.id === selectedSourceId)) {
        setSelectedSourceId(null)
      }
    } finally {
      setSourcesLoading(false)
    }
  }, [selectedSourceId])

  const loadArticles = useCallback(
    async (options?: { silent?: boolean }) => {
      if (!options?.silent) {
        setArticlesLoading(true)
      }

      try {
        const response: ArticleListResponse = await fetchArticles({
          source_id: selectedSourceId ?? undefined,
          q: search.trim() || undefined,
          analysis_status:
            articleFilters.analysisStatus === 'all' ? undefined : articleFilters.analysisStatus,
          priority_level:
            articleFilters.priorityLevel === 'all' ? undefined : articleFilters.priorityLevel,
          saved: articleFilters.savedOnly ? true : undefined,
          archived: articleFilters.archivedOnly ? true : undefined,
          limit: 50,
        })

        setArticles(response.items)
        setTotal(response.total)

        if (response.items.length === 0) {
          setSelectedArticleId(null)
          setSelectedArticleDetail(null)
          setSelectedAnalysis(null)
          return
        }

        setSelectedArticleId((current) => {
          if (current && response.items.some((article) => article.id === current)) {
            return current
          }
          return response.items[0].id
        })
      } finally {
        if (!options?.silent) {
          setArticlesLoading(false)
        }
      }
    },
    [articleFilters, search, selectedSourceId],
  )

  const loadArticleDetail = useCallback(async (articleId: number) => {
    const detail = await fetchArticleDetail(articleId)
    setSelectedArticleDetail((current) => {
      if (current && current.id !== articleId) {
        return current
      }
      return detail
    })
  }, [])

  const loadAnalysis = useCallback(
    async (articleId: number, options?: { silent?: boolean }) => {
      if (!options?.silent) {
        setAnalysisLoading(true)
      }

      try {
        const analysis = await fetchAnalysis(articleId)
        setSelectedAnalysis((current) => {
          if (selectedArticleId !== articleId) {
            return current
          }
          return analysis
        })
      } finally {
        if (!options?.silent) {
          setAnalysisLoading(false)
        }
      }
    },
    [selectedArticleId],
  )

  useEffect(() => {
    void loadSources()
  }, [loadSources])

  useEffect(() => {
    void loadArticles()
  }, [loadArticles])

  useEffect(() => {
    if (!selectedArticleId) {
      setSelectedArticleDetail(null)
      return
    }
    void loadArticleDetail(selectedArticleId)
    void loadAnalysis(selectedArticleId)
  }, [loadAnalysis, loadArticleDetail, selectedArticleId])

  useEffect(() => {
    if (!selectedArticleId || !selectedAnalysis || !POLLING_STATUSES.has(selectedAnalysis.status)) {
      return
    }

    const timer = window.setInterval(() => {
      void loadAnalysis(selectedArticleId, { silent: true })
      void loadArticleDetail(selectedArticleId)
      void loadArticles({ silent: true })
    }, 5000)

    return () => window.clearInterval(timer)
  }, [loadAnalysis, loadArticleDetail, loadArticles, selectedArticleId, selectedAnalysis])

  const selectedArticle = useMemo(() => {
    if (selectedArticleDetail && selectedArticleDetail.id === selectedArticleId) {
      return selectedArticleDetail
    }
    return null
  }, [selectedArticleDetail, selectedArticleId])

  async function handleCreateSource(payload: RssSourceCreate) {
    setActionMessage('Adding RSS source...')
    try {
      const source = await createSource(payload)
      setSelectedSourceId(source.id)
      setActionMessage(`RSS source added: ${source.name}`)
      await loadSources()
    } catch (error) {
      setActionMessage(getErrorMessage(error))
      throw error
    }
  }

  async function handleToggleSource(source: RssSourceRead) {
    setSourceBusyId(source.id)
    setActionMessage(`Updating source: ${source.name}`)
    try {
      await updateSource(source.id, { enabled: !source.enabled })
      setActionMessage(`${source.name} is now ${source.enabled ? 'disabled' : 'enabled'}.`)
      await loadSources()
    } catch (error) {
      setActionMessage(getErrorMessage(error))
    } finally {
      setSourceBusyId(null)
    }
  }

  async function handleDeleteSource(source: RssSourceRead) {
    const confirmed = window.confirm(`Delete RSS source "${source.name}"?`)
    if (!confirmed) {
      return
    }

    setSourceBusyId(source.id)
    setActionMessage(`Deleting source: ${source.name}`)
    try {
      await deleteSource(source.id)
      setActionMessage(`Deleted source: ${source.name}`)
      await Promise.all([loadSources(), loadArticles({ silent: true })])
    } catch (error) {
      setActionMessage(getErrorMessage(error))
    } finally {
      setSourceBusyId(null)
    }
  }

  async function handleFetchSource(sourceId: number) {
    setSourceBusyId(sourceId)
    setRefreshingArticleId(null)
    setActionMessage('Fetching RSS source...')
    try {
      const result = await fetchRssSource(sourceId)
      setActionMessage(
        `Fetched ${result.fetched_count} items, inserted ${result.inserted_count}, auto-queued ${result.queued_analysis_count}.`,
      )
      await Promise.all([loadSources(), loadArticles()])
    } catch (error) {
      setActionMessage(getErrorMessage(error))
    } finally {
      setSourceBusyId(null)
    }
  }

  async function handleAnalyze(articleId: number) {
    setRefreshingArticleId(articleId)
    const mode =
      selectedAnalysis?.status === 'completed' || selectedAnalysis?.status === 'failed'
        ? 'reanalyze'
        : 'analyze'
    setActionMessage(mode === 'reanalyze' ? 'Reanalysis queued.' : 'Analysis queued.')

    try {
      if (mode === 'reanalyze') {
        await reanalyzeArticle(articleId)
      } else {
        await analyzeArticle(articleId)
      }
      await Promise.all([
        loadArticles({ silent: true }),
        loadArticleDetail(articleId),
        loadAnalysis(articleId, { silent: true }),
      ])
    } catch (error) {
      setActionMessage(getErrorMessage(error))
    } finally {
      setRefreshingArticleId(null)
    }
  }

  async function handleSaveArticle(articleId: number) {
    setActionMessage('Updating saved state...')
    try {
      await saveArticle(articleId)
      await Promise.all([loadArticles({ silent: true }), loadArticleDetail(articleId)])
    } catch (error) {
      setActionMessage(getErrorMessage(error))
    }
  }

  async function handleArchiveArticle(articleId: number) {
    setActionMessage('Updating archived state...')
    try {
      await archiveArticle(articleId)
      await Promise.all([loadArticles({ silent: true }), loadArticleDetail(articleId)])
    } catch (error) {
      setActionMessage(getErrorMessage(error))
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b border-slate-200 bg-white/90 backdrop-blur">
        <div className="mx-auto flex max-w-[1600px] items-center justify-between gap-4 px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-3">
            <div className="flex size-10 items-center justify-center rounded-lg bg-blue-600 text-white">
              <Rss className="size-5" />
            </div>
            <div>
              <h1 className="text-lg font-semibold text-slate-950">AI RSS Reader</h1>
              <p className="text-sm text-slate-500">Manual-analysis reading workspace</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={() => void loadSources()}>
              <RefreshCcw data-icon="inline-start" />
              Refresh sources
            </Button>
            <Button variant="outline" size="sm" onClick={() => void loadArticles()}>
              <Newspaper data-icon="inline-start" />
              Refresh articles
            </Button>
          </div>
        </div>
      </header>

      <main className="mx-auto flex max-w-[1600px] flex-col px-4 py-4 sm:px-6 lg:px-8">
        <section className="mb-4 flex min-h-10 items-center justify-between gap-4 rounded-lg border border-slate-200 bg-white px-4 py-2">
          <div className="flex items-center gap-2 text-sm text-slate-600">
            <BrainCircuit className="size-4 text-blue-600" />
            <span>
              {actionMessage ?? 'Read first, then decide whether to run AI analysis for the article.'}
            </span>
          </div>
          <div className="text-sm text-slate-500">Articles {total}</div>
        </section>

        <div className="grid min-h-[calc(100vh-158px)] grid-cols-1 gap-4 xl:grid-cols-[320px_minmax(0,1fr)_520px]">
          <aside className="overflow-hidden rounded-lg border border-slate-200 bg-white">
            {sourcesLoading ? (
              <div className="flex h-full flex-col gap-3 p-4">
                {Array.from({ length: 8 }).map((_, index) => (
                  <Skeleton key={index} className="h-12 rounded-lg" />
                ))}
              </div>
            ) : (
              <SourceSidebar
                sources={sources}
                selectedSourceId={selectedSourceId}
                busySourceId={sourceBusyId}
                onSelectSource={setSelectedSourceId}
                onCreateSource={handleCreateSource}
                onFetchSource={handleFetchSource}
                onToggleSource={handleToggleSource}
                onDeleteSource={handleDeleteSource}
              />
            )}
          </aside>

          <section className="overflow-hidden rounded-lg border border-slate-200 bg-white">
            {articlesLoading ? (
              <div className="flex flex-col gap-3 p-4">
                {Array.from({ length: 7 }).map((_, index) => (
                  <Skeleton key={index} className="h-28 rounded-lg" />
                ))}
              </div>
            ) : (
              <ArticleFeed
                articles={articles}
                selectedArticleId={selectedArticleId}
                sourceNameById={sourceNameById}
                search={search}
                filters={articleFilters}
                onSearchChange={setSearch}
                onFiltersChange={setArticleFilters}
                onSelectArticle={setSelectedArticleId}
                onSaveArticle={handleSaveArticle}
                onArchiveArticle={handleArchiveArticle}
              />
            )}
          </section>

          <aside className="overflow-hidden rounded-lg border border-slate-200 bg-white">
            {selectedArticle && selectedAnalysis ? (
              <AnalysisPanel
                article={selectedArticle}
                sourceName={selectedArticle.source_id ? sourceNameById.get(selectedArticle.source_id) : null}
                analysis={selectedAnalysis}
                loading={analysisLoading}
                busy={refreshingArticleId === selectedArticle.id}
                onAnalyze={() => void handleAnalyze(selectedArticle.id)}
              />
            ) : (
              <div className="flex h-full min-h-[420px] items-center justify-center p-6 text-center text-sm text-slate-500">
                Select an article to read the full content and decide whether to run AI analysis.
              </div>
            )}
          </aside>
        </div>
      </main>
    </div>
  )
}

function getErrorMessage(error: unknown) {
  if (error instanceof Error) {
    return error.message
  }
  return 'Request failed. Check that the backend service is running.'
}

export default App
