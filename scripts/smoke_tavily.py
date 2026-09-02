#!/usr/bin/env python3
"""Smoke: one Tavily Search runtime call. Fail-closed without TAVILY_API_KEY."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gatekeeper.tavily import search  # noqa: E402


def main() -> int:
    result = search("NVIDIA Nemotron Nebius Token Factory", max_results=3)
    print(f"status={result.status}")
    print(f"query={result.query!r}")
    print(f"hits={len(result.hits)}")
    if result.reason:
        print(f"reason={result.reason}")
    for hit in result.hits:
        print(json.dumps({"title": hit.title, "url": hit.url}, ensure_ascii=False))
    if result.status == "missing_key":
        print("BLOCKED_INFRA: set TAVILY_API_KEY (Builder Program Tavily key; see BUILD.md)")
        return 3
    if result.status == "grounded":
        print("PASS")
        return 0
    print("FAIL")
    return 4 if result.status in {"http_error", "network_error", "invalid_response", "zero_hits"} else 4


if __name__ == "__main__":
    sys.exit(main())
