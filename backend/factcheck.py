import json
import httpx
from typing import List

from models import Article, CheckResponse
from config import GEMINI_API_KEY

SYSTEM_PROMPT = """You are a careful news fact-checking assistant. You will be given:
1. A claim submitted by a user
2. A list of headlines found from cross-referencing multiple news sources (may be empty)

Your job is to assess the claim based ONLY on the evidence given plus your general world knowledge.
Be honest about uncertainty - do not overstate confidence.

Respond ONLY with valid JSON, no markdown fences, no preamble, in this exact shape:
{
  "verdict": "Likely True" | "Likely False" | "Unverified" | "Misleading" | "Needs Context",
  "confidence": "High" | "Medium" | "Low",
  "reasoning": "2-4 sentences explaining the verdict"
}

Rules:
- If no matching sources were found, lean toward Unverified with Low confidence.
- If multiple independent sources corroborate the claim, confidence in Likely True increases.
- If the claim contains exaggeration or missing context, use Misleading.
- Never fabricate sources or facts not given to you."""


def _build_user_message(claim: str, matched_sources: List[Article]) -> str:
    if matched_sources:
        sources_text = "\n".join(
            f"- [{a.source}] {a.title}" for a in matched_sources
        )
    else:
        sources_text = "(No matching headlines found.)"

    return f"""Claim to check: "{claim}"

Cross-referenced headlines from news sources:
{sources_text}

Provide your verdict as JSON per the system instructions."""


def check_claim(claim: str, matched_sources: List[Article]) -> CheckResponse:
    user_msg = _build_user_message(claim, matched_sources)

  url=f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

    payload = {
        "contents": [{"parts": [{"text": SYSTEM_PROMPT + "\n\n" + user_msg}]}],
        "generationConfig": {"maxOutputTokens": 500, "temperature": 0.2},
    }

    with httpx.Client(timeout=30.0) as client:
        resp = client.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()

    raw_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
    cleaned = raw_text.replace("```json", "").replace("```", "").strip()

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        parsed = {
            "verdict": "Unverified",
            "confidence": "Low",
            "reasoning": "Could not parse model response: " + raw_text[:200],
        }

    distinct_sources = len(set(a.source for a in matched_sources))

    return CheckResponse(
        claim=claim,
        verdict=parsed.get("verdict", "Unverified"),
        confidence=parsed.get("confidence", "Low"),
        reasoning=parsed.get("reasoning", ""),
        matched_sources=matched_sources,
        source_agreement_count=distinct_sources,
    )
