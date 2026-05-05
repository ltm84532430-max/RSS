export type RssSourceRead = {
  id: number
  name: string
  url: string
  category: string | null
  enabled: boolean
  fetch_interval_minutes: number
  last_fetch_time: string | null
  created_at: string
  updated_at: string
}

export type RssSourceCreate = {
  name: string
  url: string
  category?: string | null
  enabled?: boolean
  fetch_interval_minutes?: number
}

export type RssSourceUpdate = {
  name?: string
  url?: string
  category?: string | null
  enabled?: boolean
  fetch_interval_minutes?: number
}

export type RssSourceFetchResponse = {
  source_id: number
  fetched_count: number
  inserted_count: number
  queued_analysis_count: number
  status: string
  message: string
}

export type AnalysisSummary = {
  status: string | null
  priority_level: string | null
  recommended_action: string | null
  sentiment: string | null
  importance_score: number | null
}

export type ReadingStateRead = {
  is_read: boolean
  is_saved: boolean
  is_archived: boolean
  read_at: string | null
}

export type ArticleListItem = {
  id: number
  source_id: number | null
  title: string
  url: string
  author: string | null
  published_at: string | null
  summary: string | null
  language: string | null
  analysis_status: string
  created_at: string
  analysis: AnalysisSummary | null
  reading_state: ReadingStateRead | null
}

export type ArticleDetail = ArticleListItem & {
  content: string | null
  source?: RssSourceRead | null
  tags: string[]
}

export type ArticleListResponse = {
  items: ArticleListItem[]
  total: number
  limit: number
  offset: number
}

export type AnalysisRead = {
  article_id: number
  status: string
  structured_result: Record<string, unknown> | null
  cognitive_result: Record<string, unknown> | null
  decision_result: Record<string, unknown> | null
  error_message: string | null
  model_provider: string | null
  model_name: string | null
  task_id: string | null
  priority_level: string | null
  recommended_action: string | null
  sentiment: string | null
  importance_score: number | null
  analyzed_at: string | null
  updated_at: string | null
}

export type ReanalyzeResponse = {
  article_id: number
  task_id: string
  status: string
}

export type AnalyzeResponse = {
  article_id: number
  task_id: string
  status: string
}
