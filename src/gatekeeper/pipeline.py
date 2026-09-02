"""Orchestrate gates → Tavily → Nemotron with structured outcomes."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Literal

from gatekeeper.gates import check_g0_eligible, check_go_contract
from gatekeeper.models import Citation, LatencyMs, TriageOutcome
from gatekeeper.nemotron import TriageRequest, triage_candidate
from gatekeeper.tavily import TavilyResult, ground_candidate

TavilyMode = Literal["optional", "required"]


def _provider_failure_reason(exc: Exception) -> str:
    """Secret-free reason for any failure during a Nemotron attempt."""
    status_code = getattr(exc, "status_code", None)
    if isinstance(status_code, int):
        return f"Nemotron provider HTTP {status_code}"
    if isinstance(exc, RuntimeError) and "NEBIUS_API_KEY not set" in str(exc):
        return "NEBIUS_API_KEY not set"
    # Transport / shape failures: one stable public reason (never echo exc text).
    if isinstance(
        exc,
        (TimeoutError, OSError, IndexError, AttributeError, TypeError, KeyError),
    ):
        return "Nemotron provider failure"
    error_type = type(exc)
    if error_type.__module__.split(".", 1)[0] in {"openai", "httpx"} or error_type.__name__ in {
        "APIError",
        "APIConnectionError",
        "APIStatusError",
        "APITimeoutError",
        "HTTPError",
        "TimeoutException",
    }:
        return "Nemotron provider failure"
    return "Nemotron provider failure"


@dataclass(frozen=True)
class PipelineOptions:
    package: str
    mechanism: str
    static_notes: str = ""
    dry_run: bool = False
    tavily_only: bool = False
    skip_tavily: bool = False
    tavily_mode: TavilyMode = "optional"

    def grounding_required(self) -> bool:
        return self.tavily_mode == "required" or self.tavily_only


def _citations_from_tavily(result: TavilyResult) -> tuple[Citation, ...]:
    return tuple(
        Citation(title=hit.title, url=hit.url, snippet=hit.snippet) for hit in result.hits
    )


def run_pipeline(options: PipelineOptions) -> TriageOutcome:
    started = time.perf_counter()
    gate_started = time.perf_counter()

    g0 = check_g0_eligible()
    if g0.verdict != "ALLOW":
        latency = LatencyMs(gates=int((time.perf_counter() - gate_started) * 1000))
        return TriageOutcome(
            verdict="BLOCK",
            reason=g0.reason,
            gate="G0",
            latency_ms=latency,
        )

    gate = check_go_contract(package=options.package, mechanism=options.mechanism)
    gate_ms = int((time.perf_counter() - gate_started) * 1000)
    if gate.verdict != "ALLOW":
        # Preserve PARK vs BLOCK from the gate (do not collapse BLOCK → PARK).
        return TriageOutcome(
            verdict=gate.verdict,
            reason=gate.reason,
            gate="GO_CONTRACT",
            park_class=gate.park_class,
            latency_ms=LatencyMs(gates=gate_ms),
        )

    if options.dry_run:
        total = int((time.perf_counter() - started) * 1000)
        return TriageOutcome(
            verdict="ALLOW_STATIC",
            reason="dry-run: static gates passed",
            gate="GO_CONTRACT",
            nemotron="skipped",
            tavily="skipped",
            latency_ms=LatencyMs(gates=gate_ms, total=total),
        )

    notes = options.static_notes
    tavily_result = TavilyResult("skipped", "", ())
    tavily_ms = 0

    if options.skip_tavily and options.grounding_required():
        total = int((time.perf_counter() - started) * 1000)
        return TriageOutcome(
            verdict="BLOCKED_INFRA",
            reason="Tavily required but --skip-tavily was set",
            gate="GO_CONTRACT",
            tavily="skipped",
            nemotron="skipped",
            latency_ms=LatencyMs(gates=gate_ms, total=total),
        )

    if not options.skip_tavily:
        tavily_started = time.perf_counter()
        tavily_result = ground_candidate(package=options.package, mechanism=options.mechanism)
        tavily_ms = tavily_result.latency_ms or int((time.perf_counter() - tavily_started) * 1000)

        if tavily_result.is_grounded:
            extra = tavily_result.as_notes()
            notes = f"{notes}\n\n{extra}".strip() if notes else extra
        elif options.grounding_required():
            total = int((time.perf_counter() - started) * 1000)
            return TriageOutcome(
                verdict="BLOCKED_INFRA",
                reason=tavily_result.reason or tavily_result.status,
                gate="GO_CONTRACT",
                tavily=tavily_result.status,
                tavily_hits=len(tavily_result.hits),
                nemotron="skipped",
                latency_ms=LatencyMs(gates=gate_ms, tavily=tavily_ms, total=total),
            )

    if options.tavily_only:
        total = int((time.perf_counter() - started) * 1000)
        if tavily_result.is_grounded:
            return TriageOutcome(
                verdict="TAVILY_GROUNDED",
                reason="Tavily grounding succeeded",
                gate="GO_CONTRACT",
                tavily="grounded",
                tavily_hits=len(tavily_result.hits),
                citations=_citations_from_tavily(tavily_result),
                nemotron="skipped",
                latency_ms=LatencyMs(gates=gate_ms, tavily=tavily_ms, total=total),
            )
        return TriageOutcome(
            verdict="BLOCKED_INFRA",
            reason=tavily_result.reason or tavily_result.status,
            gate="GO_CONTRACT",
            tavily=tavily_result.status,
            tavily_hits=len(tavily_result.hits),
            nemotron="skipped",
            latency_ms=LatencyMs(gates=gate_ms, tavily=tavily_ms, total=total),
        )

    citations = _citations_from_tavily(tavily_result) if tavily_result.is_grounded else ()
    nemotron_started = time.perf_counter()
    try:
        model_result = triage_candidate(
            TriageRequest(
                package=options.package,
                mechanism=options.mechanism,
                static_notes=notes,
                citations=citations,
            )
        )
    except ValueError as exc:
        total = int((time.perf_counter() - started) * 1000)
        nemotron_ms = int((time.perf_counter() - nemotron_started) * 1000)
        return TriageOutcome(
            verdict="BLOCKED_INFRA",
            reason=f"invalid Nemotron response: {exc}",
            gate="GO_CONTRACT",
            tavily=tavily_result.status,
            tavily_hits=len(tavily_result.hits),
            citations=citations,
            nemotron="invalid_response",
            latency_ms=LatencyMs(gates=gate_ms, tavily=tavily_ms, nemotron=nemotron_ms, total=total),
        )
    except Exception as exc:
        # Fail-closed for transport/SDK/shape errors (ConnectionError, empty choices, etc.).
        total = int((time.perf_counter() - started) * 1000)
        nemotron_ms = int((time.perf_counter() - nemotron_started) * 1000)
        return TriageOutcome(
            verdict="BLOCKED_INFRA",
            reason=_provider_failure_reason(exc),
            gate="GO_CONTRACT",
            tavily=tavily_result.status,
            tavily_hits=len(tavily_result.hits),
            citations=citations,
            nemotron="blocked",
            latency_ms=LatencyMs(gates=gate_ms, tavily=tavily_ms, nemotron=nemotron_ms, total=total),
        )

    nemotron_ms = model_result.latency_ms or int((time.perf_counter() - nemotron_started) * 1000)
    total = int((time.perf_counter() - started) * 1000)
    return TriageOutcome(
        verdict=model_result.verdict,  # ALLOW_PREFLIGHT or PARK
        reason=model_result.reason,
        summary=model_result.summary,
        recommendation=model_result.reason,
        gate="GO_CONTRACT",
        model=model_result.model,
        citations=citations,
        tavily=tavily_result.status,
        tavily_hits=len(tavily_result.hits),
        nemotron="completed",
        latency_ms=LatencyMs(gates=gate_ms, tavily=tavily_ms, nemotron=nemotron_ms, total=total),
        usage=model_result.usage,
        request_id=model_result.request_id,
    )
