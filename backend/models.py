from pydantic import BaseModel
from typing import List, Optional


class Article(BaseModel):
    title: str
    link: str
    source: str
    category: str
    published: Optional[str] = None


class StoryCluster(BaseModel):
    """A group of articles from different sources covering the same story."""
    representative_title: str
    articles: List[Article]
    source_count: int
    agreement_score: float  # 0-1, how many distinct sources are covering this


class FeedResponse(BaseModel):
    clusters: List[StoryCluster]
    total_articles: int
    total_sources: int


class CheckRequest(BaseModel):
    claim: str


class CheckResponse(BaseModel):
    claim: str
    verdict: str           # e.g. "Likely True", "Likely False", "Unverified", "Misleading"
    confidence: str         # "High", "Medium", "Low"
    reasoning: str
    matched_sources: List[Article] = []
    source_agreement_count: int = 0
