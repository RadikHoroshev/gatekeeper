"""CLI entry: static gates first, Nemotron only on ALLOW."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone

from gatekeeper.gates import check_g0_eligible, check_go_contract
from gatekeeper.nemotron import TriageRequest, triage_candidate


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Gatekeeper triage (gates → optional Nemotron)")
    parser.add_argument("--package", required=True)
    parser.add_argument("--mechanism", required=True)
    parser.add_argument("--static-notes", default="")
    parser.add_argument("--dry-run", action="store_true", help="Skip Nemotron even if ALLOW")
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
        print(json.dumps({"verdict": "ALLOW_STATIC", "nemotron": "skipped", "finding": False}, indent=2))
        return 0

    try:
        result = triage_candidate(
            TriageRequest(
                package=args.package,
                mechanism=args.mechanism,
                static_notes=args.static_notes,
            )
        )
    except RuntimeError as exc:
        print(json.dumps({"verdict": "BLOCKED_INFRA", "reason": str(exc)}, indent=2))
        return 3

    print(
        json.dumps(
            {
                "verdict": "TRIAGED",
                "ts": datetime.now(timezone.utc).isoformat(),
                "model": result.model,
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
