"""
Groups articles covering the same underlying story across different sources.
Uses TF-IDF + cosine similarity on headlines — cheap, no API calls, no training needed.

The core idea: if 4 independent outlets are reporting near-identical headlines,
that's a real story. If only one obscure source has it and nobody else does,
that's a flag worth surfacing (not proof of fakeness, but a useful signal).
"""
from typing import List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from models import Article, StoryCluster
from config import SIMILARITY_THRESHOLD


def cluster_articles(articles: List[Article]) -> List[StoryCluster]:
    if not articles:
        return []

    titles = [a.title for a in articles]

    vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
    try:
        tfidf_matrix = vectorizer.fit_transform(titles)
    except ValueError:
        # happens if all titles are empty/stopwords only - bail gracefully
        return [
            StoryCluster(representative_title=a.title, articles=[a], source_count=1, agreement_score=0.0)
            for a in articles
        ]

    sim_matrix = cosine_similarity(tfidf_matrix)

    visited = [False] * len(articles)
    clusters: List[StoryCluster] = []

    for i in range(len(articles)):
        if visited[i]:
            continue
        group_indices = [i]
        visited[i] = True
        for j in range(i + 1, len(articles)):
            if visited[j]:
                continue
            if sim_matrix[i][j] >= SIMILARITY_THRESHOLD:
                group_indices.append(j)
                visited[j] = True

        group_articles = [articles[idx] for idx in group_indices]
        distinct_sources = len(set(a.source for a in group_articles))

        # agreement_score: normalized by total number of sources we aggregate from,
        # capped at 1.0. More distinct sources reporting it = higher score.
        agreement_score = min(distinct_sources / 4.0, 1.0)

        clusters.append(
            StoryCluster(
                representative_title=group_articles[0].title,
                articles=group_articles,
                source_count=distinct_sources,
                agreement_score=round(agreement_score, 2),
            )
        )

    # Sort by agreement score descending, then by cluster size — most-corroborated stories first
    clusters.sort(key=lambda c: (c.agreement_score, len(c.articles)), reverse=True)
    return clusters


def find_matching_sources(claim: str, articles: List[Article], top_k: int = 5) -> List[Article]:
    """
    Given a user-submitted claim, find the most textually similar articles
    from the aggregated pool. Used as grounding context for the fact-check LLM call.
    """
    if not articles:
        return []

    corpus = [claim] + [a.title for a in articles]
    vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
    try:
        tfidf_matrix = vectorizer.fit_transform(corpus)
    except ValueError:
        return []

    claim_vec = tfidf_matrix[0]
    article_vecs = tfidf_matrix[1:]
    sims = cosine_similarity(claim_vec, article_vecs)[0]

    ranked_indices = np.argsort(sims)[::-1]
    matches = []
    for idx in ranked_indices[:top_k]:
        if sims[idx] > 0.1:  # ignore near-zero matches
            matches.append(articles[idx])
    return matches
