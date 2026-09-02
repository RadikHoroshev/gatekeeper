#!/usr/bin/env python3
"""Offline benchmark over synthetic fixtures (no network)."""

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


def main() -> int:
    cases = json.loads(CASES.read_text(encoding="utf-8"))
    gate_latencies: list[int] = []
    false_allow = 0
    false_park = 0
    totals = {
        "total_candidates": len(cases),
        "parked_locally": 0,
        "tavily_calls": 0,
        "nemotron_calls": 0,
        "prevented_model_calls": 0,
        "estimated_token_reduction": "NOT_MEASURED",
    }

    for case in cases:
        tavily_status = case.get("tavily_status", "skipped")
        nemotron_verdict = case.get("nemotron_verdict", "PARK")

        with mock.patch(
            "gatekeeper.pipeline.ground_candidate",
            return_value=_tavily_result(tavily_status),
        ) as tav, mock.patch(
            "gatekeeper.pipeline.triage_candidate",
            return_value=_nemotron_result(nemotron_verdict),
        ) as nem:
            outcome = run_pipeline(
                PipelineOptions(
                    package=case["package"],
                    mechanism=case["mechanism"],
                    dry_run=case.get("dry_run", False),
                    tavily_only=case.get("tavily_only", False),
                )
            )

        gate_latencies.append(outcome.latency_ms.gates)
        if outcome.verdict == "PARK" and outcome.park_class:
            totals["parked_locally"] += 1
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

        if outcome.verdict != case["expected_verdict"]:
            if case["expected_verdict"] in {"ALLOW_STATIC", "ALLOW_PREFLIGHT", "TAVILY_GROUNDED"} and outcome.verdict == "PARK":
                false_park += 1
            elif case["expected_verdict"] == "PARK" and outcome.verdict != "PARK":
                false_allow += 1

    report = {
        **totals,
        "false_allow": false_allow,
        "false_park": false_park,
        "mean_gate_latency_ms": round(statistics.mean(gate_latencies), 2) if gate_latencies else 0,
        "p95_gate_latency_ms": round(statistics.quantiles(gate_latencies, n=20)[-1], 2)
        if len(gate_latencies) >= 2
        else (gate_latencies[0] if gate_latencies else 0),
    }
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
