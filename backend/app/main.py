from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import analysis, articles, rss


app = FastAPI(
    title="AI RSS Reader API",
    version="0.1.0",
    description="FastAPI backend for RSS source management, article queries, and AI analysis results.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(rss.router)
app.include_router(articles.router)
app.include_router(analysis.router)


@app.get("/health", tags=["System"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}

