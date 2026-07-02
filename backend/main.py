from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from aggregator import fetch_all_articles
from crossref import cluster_articles, find_matching_sources
from factcheck import check_claim
from models import FeedResponse, CheckRequest, CheckResponse
from config import ALLOWED_ORIGINS

app = FastAPI(title="NewsCheck API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
def root():
    return {"status": "ok", "service": "NewsCheck API"}


@app.get("/feed", response_model=FeedResponse)
async def get_feed(refresh: bool = False):
    """Aggregated news feed, clustered by story with source-agreement scores."""
    articles = await fetch_all_articles(force_refresh=refresh)
    if not articles:
        raise HTTPException(status_code=503, detail="Could not fetch any news sources right now. Try again shortly.")

    clusters = cluster_articles(articles)
    distinct_sources = len(set(a.source for a in articles))

    return FeedResponse(
        clusters=clusters,
        total_articles=len(articles),
        total_sources=distinct_sources,
    )


@app.post("/check", response_model=CheckResponse)
async def check(request: CheckRequest):
    """User submits a claim/headline; we cross-reference against aggregated sources and ask Claude for a verdict."""
    if not request.claim or not request.claim.strip():
        raise HTTPException(status_code=400, detail="Claim text is required.")

    articles = await fetch_all_articles()
    matched_sources = find_matching_sources(request.claim, articles)

    result = check_claim(request.claim, matched_sources)
    return result
