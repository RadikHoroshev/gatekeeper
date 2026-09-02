"""Optional Tavily grounding after ALLOW, before Nemotron.

Fail-closed when TAVILY_API_KEY is unset. Public CI never sets the key.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Callable, Literal
from urllib.parse import urlsplit

TAVILY_SEARCH_URL = "https://api.tavily.com/search"
MAX_TITLE_LEN = 200
MAX_URL_LEN = 2048
MAX_SNIPPET_LEN = 500
MIN_MAX_RESULTS = 1
MAX_MAX_RESULTS = 10

TavilyStatus = Literal[
    "skipped",
    "missing_key",
    "network_error",
    "http_error",
    "invalid_response",
    "zero_hits",
    "grounded",
]


@dataclass(frozen=True)
class TavilyHit:
    title: str
    url: str
    snippet: str


@dataclass(frozen=True)
class TavilyResult:
    status: TavilyStatus
    query: str
    hits: tuple[TavilyHit, ...]
    reason: str = ""
    latency_ms: int = 0
    http_status: int | None = None

    @property
    def is_grounded(self) -> bool:
        return self.status == "grounded" and len(self.hits) > 0

    def as_notes(self) -> str:
        lines = [f"Tavily grounding query: {self.query}"]
        for i, hit in enumerate(self.hits, 1):
            lines.append(f"{i}. {hit.title} — {hit.url}")
            if hit.snippet:
                lines.append(f"   {hit.snippet}")
        return "\n".join(lines)

    def citations(self) -> tuple[TavilyHit, ...]:
        return self.hits


def _api_key() -> str:
    return os.environ.get("TAVILY_API_KEY", "").strip()


def _clamp_max_results(max_results: int) -> int:
    if max_results < MIN_MAX_RESULTS or max_results > MAX_MAX_RESULTS:
        raise ValueError(f"max_results must be {MIN_MAX_RESULTS}..{MAX_MAX_RESULTS}")
    return max_results


def _sanitize_text(value: object, *, limit: int) -> str:
    text = str(value or "").strip()
    if len(text) > limit:
        return text[: limit - 3] + "..."
    return text


def _sanitize_hit(item: dict) -> TavilyHit | None:
    if not isinstance(item, dict):
        return None
    url = _sanitize_text(item.get("url"), limit=MAX_URL_LEN)
    try:
        parsed = urlsplit(url)
        hostname = parsed.hostname
    except ValueError:
        return None
    if (
        parsed.scheme.lower() not in {"http", "https"}
        or not hostname
        or parsed.username is not None
        or parsed.password is not None
    ):
        return None
    title = _sanitize_text(item.get("title"), limit=MAX_TITLE_LEN)
    snippet = _sanitize_text(item.get("content") or item.get("snippet"), limit=MAX_SNIPPET_LEN)
    return TavilyHit(title=title, url=url, snippet=snippet)


def _parse_response(body: object, *, query: str, max_results: int) -> TavilyResult:
    if not isinstance(body, dict):
        return TavilyResult("invalid_response", query, (), reason="response is not a JSON object")
    raw_results = body.get("results")
    if raw_results is None:
        return TavilyResult("invalid_response", query, (), reason="missing results array")
    if not isinstance(raw_results, list):
        return TavilyResult("invalid_response", query, (), reason="results is not a list")

    hits: list[TavilyHit] = []
    for item in raw_results:
        hit = _sanitize_hit(item)
        if hit is not None:
            hits.append(hit)
        if len(hits) >= max_results:
            break
    if not hits:
        return TavilyResult("zero_hits", query, (), reason="no usable Tavily hits after sanitization")
    return TavilyResult("grounded", query, tuple(hits))


UrlOpener = Callable[[urllib.request.Request], object]


def search(
    query: str,
    *,
    max_results: int = 3,
    opener: UrlOpener | None = None,
) -> TavilyResult:
    """One Tavily Search runtime call."""
    started = time.perf_counter()
    query = query.strip()
    if not query:
        return TavilyResult("invalid_response", "", (), reason="empty query")

    try:
        max_results = _clamp_max_results(max_results)
    except ValueError as exc:
        return TavilyResult("invalid_response", query, (), reason=str(exc))

    api_key = _api_key()
    if not api_key:
        return TavilyResult("missing_key", query, (), reason="TAVILY_API_KEY not set")

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
        headers={"Content-Type": "application/json", "User-Agent": "gatekeeper-tavily/0.2"},
        method="POST",
    )
    open_fn = opener or urllib.request.urlopen
    try:
        with open_fn(req, timeout=30) as resp:  # type: ignore[call-arg, union-attr]
            raw = resp.read()  # type: ignore[union-attr]
    except urllib.error.HTTPError as exc:
        latency = int((time.perf_counter() - started) * 1000)
        return TavilyResult(
            "http_error",
            query,
            (),
            reason=f"Tavily HTTP {exc.code}",
            latency_ms=latency,
            http_status=exc.code,
        )
    except urllib.error.URLError as exc:
        latency = int((time.perf_counter() - started) * 1000)
        return TavilyResult(
            "network_error",
            query,
            (),
            reason=f"Tavily network error: {exc.reason}",
            latency_ms=latency,
        )
    except OSError as exc:
        latency = int((time.perf_counter() - started) * 1000)
        return TavilyResult("network_error", query, (), reason=str(exc), latency_ms=latency)

    latency = int((time.perf_counter() - started) * 1000)
    try:
        body = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return TavilyResult("invalid_response", query, (), reason=str(exc), latency_ms=latency)

    parsed = _parse_response(body, query=query, max_results=max_results)
    return TavilyResult(
        parsed.status,
        parsed.query,
        parsed.hits,
        reason=parsed.reason,
        latency_ms=latency,
        http_status=parsed.http_status,
    )


def ground_candidate(*, package: str, mechanism: str, opener: UrlOpener | None = None) -> TavilyResult:
    query = f"{package} {mechanism} android security named hypothesis"
    return search(query, max_results=3, opener=opener)
