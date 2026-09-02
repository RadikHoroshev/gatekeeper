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
    if not os.environ.get("TAVILY_API_KEY", "").strip():
        print("BLOCKED_INFRA: set TAVILY_API_KEY (Builder Program Tavily key; see BUILD.md)")
        return 3
    grounding = search("NVIDIA Nemotron Nebius Token Factory", max_results=3)
    print(f"query={grounding.query!r}")
    print(f"hits={len(grounding.hits)}")
    for hit in grounding.hits:
        print(json.dumps({"title": hit.title, "url": hit.url}, ensure_ascii=False))
    ok = len(grounding.hits) >= 1 and all(h.url.startswith("http") for h in grounding.hits)
    print("PASS" if ok else "WARN: no usable Tavily hits")
    return 0 if ok else 4


if __name__ == "__main__":
    sys.exit(main())
