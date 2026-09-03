#!/usr/bin/env python3
"""Offline routing benchmark over synthetic fixtures (no network).

This is NOT a Nemotron quality or vulnerability-detection accuracy benchmark.
"""

from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gatekeeper import nemotron  # noqa: E402
from gatekeeper.pipeline import PipelineOptions, run_pipeline  # noqa: E402
from gatekeeper.tavily import TavilyHit, TavilyResult  # noqa: E402

CASES = ROOT / "fixtures" / "benchmark_cases.json"


def _tavily_result(status: str) -> TavilyResult:
    if status == "grounded":
        return TavilyResult(
            "grounded",
            "q",
            (TavilyHit("Example", "https://example.com/doc", "snippet"),),
        )
    return TavilyResult(status, "q", (), reason=f"status={status}")


def _nemotron_result(verdict: str) -> nemotron.NemotronResult:
    return nemotron.NemotronResult(
        verdict=verdict,
        reason="fixture",
        summary="fixture summary",
        model="nvidia/test",
        latency_ms=12,
    )


def _provider_side_effect(kind: str):
    if kind == "ConnectionError":
        return ConnectionError("dns")
    if kind == "TimeoutError":
        return TimeoutError("timeout")
    if kind == "AttributeError":
        return AttributeError("choices")
    if kind == "APIStatusError429":

        class APIStatusError(Exception):
            status_code = 429

        return APIStatusError("rate limited body must not leak")
    if kind == "APIStatusError500":

        class APIStatusError(Exception):
            status_code = 500

        return APIStatusError("server body must not leak")
    if kind == "EmptyChoices":
        return ValueError("completion has no choices")
    raise AssertionError(f"unknown provider_error {kind}")


def _percentile(values: list[int], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return float(ordered[0])
    # nearest-rank
    idx = min(len(ordered) - 1, max(0, int(round((pct / 100) * (len(ordered) - 1)))))
    return float(ordered[idx])


def main() -> int:
    cases = json.loads(CASES.read_text(encoding="utf-8"))
    gate_latencies: list[int] = []
    routing_false_allow = 0
    routing_false_park = 0
    mismatches = 0
    provider_fail_cases = 0
    provider_fail_closed = 0
    schema_checked = 0
    schema_valid = 0

    totals = {
        "metric_scope": "synthetic_mocked_routing_only",
        "model_quality_measured": False,
        "total_candidates": len(cases),
        "parked_locally": 0,
        "blocked_locally": 0,
        "tavily_calls": 0,
        "nemotron_calls": 0,
        "cloud_calls_avoided": 0,
        "prevented_model_calls": 0,
        "estimated_token_reduction": "NOT_MEASURED",
    }

    for case in cases:
        tavily_status = case.get("tavily_status", "skipped")
        nemotron_verdict = case.get("nemotron_verdict", "PARK")
        provider_error = case.get("provider_error")

        if provider_error:
            nem_side = mock.Mock(side_effect=_provider_side_effect(provider_error))
        else:
            nem_side = mock.Mock(return_value=_nemotron_result(nemotron_verdict))

        with mock.patch(
            "gatekeeper.pipeline.ground_candidate",
            return_value=_tavily_result(tavily_status),
        ) as tav, mock.patch(
            "gatekeeper.pipeline.triage_candidate",
            nem_side,
        ) as nem:
            outcome = run_pipeline(
                PipelineOptions(
                    package=case["package"],
                    mechanism=case["mechanism"],
                    dry_run=case.get("dry_run", False),
                    tavily_only=case.get("tavily_only", False),
                    skip_tavily=case.get("skip_tavily", False),
                    tavily_mode=case.get("tavily_mode", "optional"),
                )
            )

        gate_latencies.append(outcome.latency_ms.gates)
        if outcome.verdict == "PARK" and outcome.park_class:
            totals["parked_locally"] += 1
        if outcome.verdict == "BLOCK":
            totals["blocked_locally"] += 1

        if case.get("expect_tavily"):
            tav.assert_called_once()
            totals["tavily_calls"] += 1
        else:
            tav.assert_not_called()

        if case.get("expect_nemotron"):
            nem.assert_called_once()
            totals["nemotron_calls"] += 1
        else:
            nem.assert_not_called()
            if outcome.verdict in {"PARK", "ALLOW_STATIC", "BLOCKED_INFRA", "BLOCK"}:
                totals["prevented_model_calls"] += 1
                totals["cloud_calls_avoided"] += 1

        # Schema presence for structured outcomes
        schema_checked += 1
        blob = outcome.to_dict()
        required = {"verdict", "reason", "tavily", "nemotron", "latency_ms", "finding"}
        if required.issubset(blob) and "Traceback" not in json.dumps(blob):
            schema_valid += 1

        if provider_error:
            provider_fail_cases += 1
            if (
                outcome.verdict == "BLOCKED_INFRA"
                and outcome.nemotron in {"blocked", "invalid_response"}
                and "dns" not in (outcome.reason or "")
                and "Traceback" not in (outcome.reason or "")
            ):
                provider_fail_closed += 1

        if outcome.verdict != case["expected_verdict"]:
            mismatches += 1
            expected = case["expected_verdict"]
            if expected in {"ALLOW_STATIC", "ALLOW_PREFLIGHT", "TAVILY_GROUNDED"} and outcome.verdict in {
                "PARK",
                "BLOCK",
            }:
                routing_false_park += 1
            elif expected in {"PARK", "BLOCK"} and outcome.verdict not in {"PARK", "BLOCK", "BLOCKED_INFRA"}:
                routing_false_allow += 1

        if case.get("expect_nemotron_status") and outcome.nemotron != case["expect_nemotron_status"]:
            mismatches += 1

    report = {
        **totals,
        "routing_false_allow": routing_false_allow,
        "routing_false_park": routing_false_park,
        "routing_mismatches": mismatches,
        "provider_failure_fail_closed_rate": (
            round(provider_fail_closed / provider_fail_cases, 4) if provider_fail_cases else "NOT_MEASURED"
        ),
        "schema_valid_rate": round(schema_valid / schema_checked, 4) if schema_checked else "NOT_MEASURED",
        "local_gate_latency_p50_ms": _percentile(gate_latencies, 50),
        "local_gate_latency_p95_ms": _percentile(gate_latencies, 95),
        "mean_gate_latency_ms": round(statistics.mean(gate_latencies), 2) if gate_latencies else 0,
        # Back-compat aliases used by older docs
        "false_allow": routing_false_allow,
        "false_park": routing_false_park,
        "p95_gate_latency_ms": _percentile(gate_latencies, 95),
    }
    print(json.dumps(report, indent=2))
    return 1 if mismatches else 0


if __name__ == "__main__":
    raise SystemExit(main())
