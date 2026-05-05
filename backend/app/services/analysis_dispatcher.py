from uuid import uuid4


def enqueue_article_analysis(article_id: int) -> str:
    """Return a task id placeholder until the async worker backend is selected."""
    _ = article_id
    return str(uuid4())
