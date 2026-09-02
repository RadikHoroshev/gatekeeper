"""Structured triage results for judges and tests."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

Verdict = Literal[
    "ALLOW_STATIC",
    "ALLOW_PREFLIGHT",
    "PARK",
    "BLOCK",
    "BLOCKED_INFRA",
    "TRIAGED",
    "TAVILY_GROUNDED",
]

TavilyStatusName = Literal[
    "skipped",
    "missing_key",
    "network_error",
    "http_error",
    "invalid_response",
    "zero_hits",
    "grounded",
]


@dataclass(frozen=True)
class Citation:
    title: str
    url: str
    snippet: str


@dataclass(frozen=True)
class TokenUsage:
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None


@dataclass(frozen=True)
class LatencyMs:
    gates: int = 0
    tavily: int = 0
    nemotron: int = 0
    total: int = 0


@dataclass
class TriageOutcome:
    verdict: Verdict
    reason: str
    finding: bool = False
    gate: str | None = None
    park_class: str | None = None
    model: str | None = None
    provider: str = "nebius-token-factory"
    summary: str | None = None
    recommendation: str | None = None
    citations: tuple[Citation, ...] = ()
    tavily: TavilyStatusName = "skipped"
    tavily_hits: int = 0
    nemotron: str = "skipped"
    latency_ms: LatencyMs = field(default_factory=LatencyMs)
    usage: TokenUsage | None = None
    request_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        if self.usage is None:
            data.pop("usage", None)
        if self.request_id is None:
            data.pop("request_id", None)
        return data
