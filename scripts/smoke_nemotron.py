#!/usr/bin/env python3
"""Smoke test: one Nemotron call via Nebius Token Factory."""

from __future__ import annotations

import os
import sys

from openai import OpenAI

BASE_URL = os.environ.get("NEBIUS_BASE_URL", "https://api.tokenfactory.nebius.com/v1/")
MODEL = os.environ.get("NEMOTRON_MODEL", "nvidia/nemotron-3-super-120b-a12b")
EXPECTED = "Gatekeeper smoke OK"


def main() -> int:
    api_key = os.environ.get("NEBIUS_API_KEY", "").strip()
    if not api_key:
        print("BLOCKED_INFRA: set NEBIUS_API_KEY (see BUILD.md §1)")
        return 3

    client = OpenAI(base_url=BASE_URL, api_key=api_key)
    completion = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": f"Reply with exactly: {EXPECTED}"}],
        max_tokens=64,
        temperature=0,
    )
    text = (completion.choices[0].message.content or "").strip()
    print(f"model={MODEL}")
    print(f"response={text!r}")
    if text == EXPECTED:
        print("PASS")
        return 0
    print("FAIL: unexpected response")
    return 1


if __name__ == "__main__":
    sys.exit(main())
