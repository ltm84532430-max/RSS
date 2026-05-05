import type {
  AnalysisRead,
  AnalyzeResponse,
  ArticleDetail,
  ArticleListResponse,
  ReanalyzeResponse,
  RssSourceCreate,
  RssSourceFetchResponse,
  RssSourceRead,
  RssSourceUpdate,
} from '@/types/api'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000'

type QueryValue = string | number | boolean | null | undefined

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers ?? {}),
    },
    ...init,
  })

  if (!response.ok) {
    const detail = await safeReadError(response)
    throw new Error(detail)
  }

  if (response.status === 204) {
    return undefined as T
  }

  return (await response.json()) as T
}

export function fetchSources() {
  return request<RssSourceRead[]>('/api/rss-sources')
}

export function createSource(payload: RssSourceCreate) {
  return request<RssSourceRead>('/api/rss-sources', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function updateSource(sourceId: number, payload: RssSourceUpdate) {
  return request<RssSourceRead>(`/api/rss-sources/${sourceId}`, {
    method: 'PUT',
    body: JSON.stringify(payload),
  })
}

export function deleteSource(sourceId: number) {
  return request<void>(`/api/rss-sources/${sourceId}`, {
    method: 'DELETE',
  })
}

export function fetchRssSource(sourceId: number) {
  return request<RssSourceFetchResponse>(`/api/rss-sources/${sourceId}/fetch`, {
    method: 'POST',
  })
}

export function fetchArticles(params: Record<string, QueryValue>) {
  const query = new URLSearchParams()

  for (const [key, value] of Object.entries(params)) {
    if (value === undefined || value === null || value === '') {
      continue
    }
    query.set(key, String(value))
  }

  const suffix = query.size > 0 ? `?${query.toString()}` : ''
  return request<ArticleListResponse>(`/api/articles${suffix}`)
}

export function fetchArticleDetail(articleId: number) {
  return request<ArticleDetail>(`/api/articles/${articleId}`)
}

export function fetchAnalysis(articleId: number) {
  return request<AnalysisRead>(`/api/articles/${articleId}/analysis`)
}

export function analyzeArticle(articleId: number) {
  return request<AnalyzeResponse>(`/api/articles/${articleId}/analyze`, {
    method: 'POST',
  })
}

export function reanalyzeArticle(articleId: number) {
  return request<ReanalyzeResponse>(`/api/articles/${articleId}/reanalyze`, {
    method: 'POST',
  })
}

export function saveArticle(articleId: number) {
  return request(`/api/articles/${articleId}/save`, {
    method: 'POST',
  })
}

export function archiveArticle(articleId: number) {
  return request(`/api/articles/${articleId}/archive`, {
    method: 'POST',
  })
}

async function safeReadError(response: Response) {
  try {
    const payload = (await response.json()) as { detail?: string }
    return payload.detail ?? `Request failed: ${response.status}`
  } catch {
    return `Request failed: ${response.status}`
  }
}
