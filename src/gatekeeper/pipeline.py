"""Orchestrate gates → Tavily → Nemotron with structured outcomes."""

from __future__ import annotations

import time
from dataclasses import dataclass

from gatekeeper.gates import check_g0_eligible, check_go_contract
from gatekeeper.models import Citation, LatencyMs, TriageOutcome
from gatekeeper.nemotron import TriageRequest, triage_candidate
from gatekeeper.tavily import TavilyResult, ground_candidate


@dataclass(frozen=True)
class PipelineOptions:
    package: str
    mechanism: str
    static_notes: str = ""
    dry_run: bool = False
    tavily_only: bool = False
    skip_tavily: bool = False
    require_tavily_grounded: bool = False


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
        return TriageOutcome(
            verdict="PARK",
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

    if not options.skip_tavily:
        tavily_started = time.perf_counter()
        tavily_result = ground_candidate(package=options.package, mechanism=options.mechanism)
        tavily_ms = tavily_result.latency_ms or int((time.perf_counter() - tavily_started) * 1000)

        if tavily_result.is_grounded:
            extra = tavily_result.as_notes()
            notes = f"{notes}\n\n{extra}".strip() if notes else extra
        elif options.tavily_only or options.require_tavily_grounded:
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
    except RuntimeError as exc:
        total = int((time.perf_counter() - started) * 1000)
        nemotron_ms = int((time.perf_counter() - nemotron_started) * 1000)
        return TriageOutcome(
            verdict="BLOCKED_INFRA",
            reason=str(exc),
            gate="GO_CONTRACT",
            tavily=tavily_result.status,
            tavily_hits=len(tavily_result.hits),
            citations=citations,
            nemotron="blocked",
            latency_ms=LatencyMs(gates=gate_ms, tavily=tavily_ms, nemotron=nemotron_ms, total=total),
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
