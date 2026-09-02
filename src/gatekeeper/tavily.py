"""Optional Tavily grounding after ALLOW, before Nemotron.

Fail-closed when TAVILY_API_KEY is unset. Public CI never sets the key.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass

TAVILY_SEARCH_URL = "https://api.tavily.com/search"


@dataclass(frozen=True)
class TavilyHit:
    title: str
    url: str
    snippet: str


@dataclass(frozen=True)
class TavilyGrounding:
    query: str
    hits: tuple[TavilyHit, ...]

    def as_notes(self) -> str:
        lines = [f"Tavily grounding query: {self.query}"]
        for i, hit in enumerate(self.hits, 1):
            lines.append(f"{i}. {hit.title} — {hit.url}")
            if hit.snippet:
                lines.append(f"   {hit.snippet[:240]}")
        return "\n".join(lines)


def _api_key() -> str:
    return os.environ.get("TAVILY_API_KEY", "").strip()


def search(query: str, *, max_results: int = 3) -> TavilyGrounding:
    """One Tavily Search runtime call. Raises RuntimeError if the key is missing."""
    api_key = _api_key()
    if not api_key:
        raise RuntimeError("TAVILY_API_KEY not set — Builder Program Tavily key required")
    payload = json.dumps(
        {
            "api_key": api_key,
            "query": query,
            "max_results": max_results,
            "search_depth": "basic",
            "include_answer": False,
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        TAVILY_SEARCH_URL,
        data=payload,
        headers={"Content-Type": "application/json", "User-Agent": "gatekeeper-tavily/0.1"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"Tavily HTTP {exc.code}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Tavily network error: {exc.reason}") from exc

    hits: list[TavilyHit] = []
    for item in body.get("results") or []:
        hits.append(
            TavilyHit(
                title=str(item.get("title") or "").strip(),
                url=str(item.get("url") or "").strip(),
                snippet=str(item.get("content") or item.get("snippet") or "").strip(),
            )
        )
        if len(hits) >= max_results:
            break
    return TavilyGrounding(query=query, hits=tuple(hits))


def ground_candidate(*, package: str, mechanism: str) -> TavilyGrounding:
    query = f"{package} {mechanism} android security named hypothesis"
    return search(query, max_results=3)
