"""Nemotron inference via Nebius Token Factory (OpenAI-compatible API)."""

from __future__ import annotations

import os
from dataclasses import dataclass

from openai import OpenAI

DEFAULT_BASE_URL = "https://api.tokenfactory.nebius.com/v1/"
DEFAULT_MODEL = "nvidia/nemotron-3-super-120b-a12b"


@dataclass
class TriageRequest:
    package: str
    mechanism: str
    static_notes: str


@dataclass
class TriageResponse:
    summary: str
    recommendation: str
    model: str


def client_from_env() -> OpenAI:
    api_key = os.environ.get("NEBIUS_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("NEBIUS_API_KEY not set — join Builder Program and create API key")
    base_url = os.environ.get("NEBIUS_BASE_URL", DEFAULT_BASE_URL).strip()
    return OpenAI(base_url=base_url, api_key=api_key)


def triage_candidate(req: TriageRequest) -> TriageResponse:
    """Expensive Nemotron call — only after static gates return ALLOW."""
    model = os.environ.get("NEMOTRON_MODEL", DEFAULT_MODEL)
    client = client_from_env()
    prompt = (
        "You are Gatekeeper, a personal AI that enforces bounty hunt discipline.\n"
        f"Package: {req.package}\n"
        f"Mechanism: {req.mechanism}\n"
        f"Static notes:\n{req.static_notes}\n\n"
        "Reply in two short paragraphs: (1) triage summary, (2) ALLOW live preflight or PARK with class."
    )
    completion = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=512,
    )
    text = completion.choices[0].message.content or ""
    parts = text.split("\n\n", 1)
    return TriageResponse(
        summary=parts[0].strip(),
        recommendation=parts[1].strip() if len(parts) > 1 else text.strip(),
        model=model,
    )
