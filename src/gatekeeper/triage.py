"""CLI entry: static gates first, Nemotron only on ALLOW."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone

from gatekeeper.pipeline import PipelineOptions, run_pipeline


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Gatekeeper triage (gates → optional Tavily → optional Nemotron)")
    parser.add_argument("--package", required=True)
    parser.add_argument("--mechanism", required=True)
    parser.add_argument("--static-notes", default="")
    parser.add_argument("--dry-run", action="store_true", help="Skip Tavily and Nemotron even if ALLOW")
    parser.add_argument("--tavily-only", action="store_true", help="After ALLOW, call Tavily then stop (no Nemotron)")
    parser.add_argument("--skip-tavily", action="store_true", help="Do not call Tavily even if the key is set")
    args = parser.parse_args(argv)

    outcome = run_pipeline(
        PipelineOptions(
            package=args.package,
            mechanism=args.mechanism,
            static_notes=args.static_notes,
            dry_run=args.dry_run,
            tavily_only=args.tavily_only,
            skip_tavily=args.skip_tavily,
            require_tavily_grounded=False,
        )
    )

    payload = outcome.to_dict()
    payload["ts"] = datetime.now(timezone.utc).isoformat()
    if outcome.verdict == "ALLOW_STATIC":
        payload.setdefault("nemotron", "skipped")
        payload.setdefault("tavily", outcome.tavily)
    if outcome.verdict in {"ALLOW_PREFLIGHT", "PARK"}:
        payload["finding"] = False
        payload.setdefault("recommendation", outcome.recommendation or outcome.reason)
        payload.setdefault("summary", outcome.summary or outcome.reason)
    print(json.dumps(payload, indent=2))

    if outcome.verdict == "BLOCK":
        return 2
    if outcome.verdict == "BLOCKED_INFRA":
        return 3
    if outcome.verdict == "TAVILY_GROUNDED":
        return 0 if outcome.tavily == "grounded" else 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
