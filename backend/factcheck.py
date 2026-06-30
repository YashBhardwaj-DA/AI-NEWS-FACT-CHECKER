"""
Sends a user claim + cross-referenced source context to Claude for a grounded verdict.

Important design choice: we don't just ask Claude "is this true?" in a vacuum.
We give it the actual matching headlines we found via crossref.py, and ask it to
reason over THAT evidence. This is more defensible than a bare LLM opinion, and
makes the "fake news" judgment auditable - you can see exactly what evidence it used.
"""
import json
from typing import List
from anthropic import Anthropic

from models import Article, CheckResponse
from config import ANTHROPIC_API_KEY, CLAUDE_MODEL

client = Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """You are a careful news fact-checking assistant. You will be given:
1. A claim submitted by a user
2. A list of headlines found from cross-referencing multiple news sources (may be empty)

Your job is to assess the claim based ONLY on the evidence given plus your general world knowledge.
Be honest about uncertainty - do not overstate confidence.

Respond ONLY with valid JSON, no markdown fences, no preamble, in this exact shape:
{
  "verdict": "Likely True" | "Likely False" | "Unverified" | "Misleading" | "Needs Context",
  "confidence": "High" | "Medium" | "Low",
  "reasoning": "2-4 sentences explaining the verdict, referencing the source evidence if any was provided"
}

Rules:
- If no matching sources were found at all, lean toward "Unverified" with Low/Medium confidence rather than guessing.
- If multiple independent sources corroborate the claim, that increases confidence in "Likely True".
- If the claim contains exaggeration or missing context even if technically rooted in something real, use "Misleading".
- Never fabricate sources or facts not given to you.
"""


def _build_user_message(claim: str, matched_sources: List[Article]) -> str:
    if matched_sources:
        sources_text = "\n".join(
            f"- [{a.source}] {a.title} ({a.link})" for a in matched_sources
        )
    else:
        sources_text = "(No matching headlines found in aggregated sources.)"

    return f"""Claim to check: "{claim}"

Cross-referenced headlines from news sources:
{sources_text}

Provide your verdict as JSON per the system instructions."""


def check_claim(claim: str, matched_sources: List[Article]) -> CheckResponse:
    user_msg = _build_user_message(claim, matched_sources)

    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=500,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_msg}],
    )

    raw_text = "".join(block.text for block in response.content if hasattr(block, "text")).strip()

    # Defensive parsing in case the model wraps in fences despite instructions
    cleaned = raw_text.replace("```json", "").replace("```", "").strip()

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        parsed = {
            "verdict": "Unverified",
            "confidence": "Low",
            "reasoning": "Could not parse model response. Raw output: " + raw_text[:300],
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
