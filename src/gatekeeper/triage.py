"""CLI entry: static gates first, Nemotron only on ALLOW."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone

from gatekeeper.gates import check_g0_eligible, check_go_contract
from gatekeeper.nemotron import TriageRequest, triage_candidate
from gatekeeper.tavily import ground_candidate


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Gatekeeper triage (gates → optional Tavily → optional Nemotron)")
    parser.add_argument("--package", required=True)
    parser.add_argument("--mechanism", required=True)
    parser.add_argument("--static-notes", default="")
    parser.add_argument("--dry-run", action="store_true", help="Skip Tavily and Nemotron even if ALLOW")
    parser.add_argument("--tavily-only", action="store_true", help="After ALLOW, call Tavily then stop (no Nemotron)")
    parser.add_argument("--skip-tavily", action="store_true", help="Do not call Tavily even if the key is set")
    args = parser.parse_args(argv)

    g0 = check_g0_eligible()
    if g0.verdict != "ALLOW":
        print(json.dumps({"verdict": g0.verdict, "gate": "G0", "reason": g0.reason}, indent=2))
        return 2

    gate = check_go_contract(package=args.package, mechanism=args.mechanism)
    if gate.verdict != "ALLOW":
        out = {
            "verdict": gate.verdict,
            "gate": "GO_CONTRACT",
            "reason": gate.reason,
            "park_class": gate.park_class,
            "finding": False,
        }
        print(json.dumps(out, indent=2))
        return 0 if gate.verdict == "PARK" else 1

    if args.dry_run:
        print(
            json.dumps(
                {
                    "verdict": "ALLOW_STATIC",
                    "nemotron": "skipped",
                    "tavily": "skipped",
                    "finding": False,
                },
                indent=2,
            )
        )
        return 0

    notes = args.static_notes
    tavily_status = "skipped"
    tavily_hits = 0
    if not args.skip_tavily:
        try:
            grounding = ground_candidate(package=args.package, mechanism=args.mechanism)
        except RuntimeError as exc:
            if args.tavily_only:
                print(json.dumps({"verdict": "BLOCKED_INFRA", "reason": str(exc), "tavily": "blocked"}, indent=2))
                return 3
            tavily_status = "skipped"
        else:
            tavily_status = "grounded"
            tavily_hits = len(grounding.hits)
            extra = grounding.as_notes()
            notes = f"{notes}\n\n{extra}".strip() if notes else extra

    if args.tavily_only:
        print(
            json.dumps(
                {
                    "verdict": "TAVILY_GROUNDED" if tavily_status == "grounded" else "BLOCKED_INFRA",
                    "tavily": tavily_status,
                    "tavily_hits": tavily_hits,
                    "nemotron": "skipped",
                    "finding": False,
                },
                indent=2,
            )
        )
        return 0 if tavily_status == "grounded" else 3

    try:
        result = triage_candidate(
            TriageRequest(
                package=args.package,
                mechanism=args.mechanism,
                static_notes=notes,
            )
        )
    except RuntimeError as exc:
        print(json.dumps({"verdict": "BLOCKED_INFRA", "reason": str(exc), "tavily": tavily_status}, indent=2))
        return 3

    print(
        json.dumps(
            {
                "verdict": "TRIAGED",
                "ts": datetime.now(timezone.utc).isoformat(),
                "model": result.model,
                "tavily": tavily_status,
                "tavily_hits": tavily_hits,
                "summary": result.summary,
                "recommendation": result.recommendation,
                "finding": False,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
