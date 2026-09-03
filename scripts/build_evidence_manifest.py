#!/usr/bin/env python3
"""Build a sanitized release/evidence manifest (no secrets).

Manifest JSON is never hashed into evidence_sha256. After write, a sidecar
``release-manifest.json.sha256`` contains the digest of the final bytes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SECRET_RE = re.compile(
    r"(?i)(authorization\s*[:=]\s*\S+|bearer\s+[a-z0-9\-._~+/]+=*|"
    r"api[_-]?key\s*[:=]\s*\S+|tvly-[a-z0-9]+|sk-[a-z0-9]+|"
    r"NEBIUS_API_KEY\s*=\s*\S+|TAVILY_API_KEY\s*=\s*\S+)"
)
GIT_SHA_RE = re.compile(r"^[0-9a-f]{40}$")

EXCLUDE_NAME_EXACT = {"manifest_stdout.json"}
EXCLUDE_NAME_PREFIX = ("release-manifest",)
EXCLUDE_SUFFIX = (".sha256",)

DEFAULT_COMMAND_ARGV = [
    ".venv/bin/python3",
    "-m",
    "gatekeeper.triage",
    "--package",
    "com.example.synthetic.gatekeeper.demo",
    "--mechanism",
    "SEND-extra-to-privileged-persist",
    "--static-notes",
    "Synthetic judge demo; not a finding; public fixture only.",
    "--tavily-mode",
    "required",
]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def is_excluded_evidence_path(rel: str) -> bool:
    name = Path(rel).name
    if name in EXCLUDE_NAME_EXACT:
        return True
    if name.endswith(EXCLUDE_SUFFIX):
        return True
    if name.startswith(EXCLUDE_NAME_PREFIX) and name.endswith(".json"):
        return True
    return False


def load_dotenv_values(env_path: Path) -> dict[str, str]:
    """Load KEY=VALUE pairs; never print values."""
    out: dict[str, str] = {}
    if not env_path.is_file():
        return out
    for line in env_path.read_text(encoding="utf-8").splitlines():
        raw = line.strip()
        if not raw or raw.startswith("#") or "=" not in raw:
            continue
        key, _, value = raw.partition("=")
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        if key and value:
            out[key] = value
    return out


def redact_obj(obj: Any) -> tuple[Any, list[str]]:
    redactions: list[str] = []

    def walk(value: Any, path: str) -> Any:
        if isinstance(value, dict):
            out = {}
            for k, v in value.items():
                lk = str(k).lower()
                if lk in {"authorization", "api_key", "apikey", "token", "password", "secret"}:
                    redactions.append(f"{path}.{k}")
                    out[k] = "<redacted>"
                else:
                    out[k] = walk(v, f"{path}.{k}")
            return out
        if isinstance(value, list):
            return [walk(v, f"{path}[{i}]") for i, v in enumerate(value)]
        if isinstance(value, str):
            if SECRET_RE.search(value):
                redactions.append(path)
                return SECRET_RE.sub("<redacted>", value)
            return value
        return value

    return walk(obj, "$"), redactions


def load_json_strict(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"malformed_json:{path.name}") from exc


def extract_run_summary(payload: dict[str, Any], *, exit_code: int | None, label: str) -> dict[str, Any]:
    return {
        "label": label,
        "verdict": payload.get("verdict"),
        "provider": payload.get("provider"),
        "model": payload.get("model"),
        "tavily": payload.get("tavily"),
        "tavily_hits": payload.get("tavily_hits"),
        "citation_count": len(payload.get("citations") or []),
        "usage": payload.get("usage"),
        "request_id": payload.get("request_id"),
        "latency_ms": payload.get("latency_ms"),
        "exit_code": exit_code,
        "finding": payload.get("finding"),
        "nemotron": payload.get("nemotron"),
    }


def scan_for_secrets(
    *,
    outdir: Path,
    env_values: dict[str, str],
) -> list[dict[str, str]]:
    """Return findings as {file, key_or_pattern} — never include secret values."""
    findings: list[dict[str, str]] = []
    for path in sorted(outdir.rglob("*")):
        if not path.is_file() or is_excluded_evidence_path(str(path.relative_to(outdir))):
            # Still scan JSON outcomes; exclude only from hashing. Scan all text evidence.
            pass
        if not path.is_file():
            continue
        rel = str(path.relative_to(outdir))
        if is_excluded_evidence_path(rel) and path.suffix == ".sha256":
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for key, value in env_values.items():
            if value and value in text:
                findings.append({"file": rel, "key": key})
        if SECRET_RE.search(text):
            findings.append({"file": rel, "key": "pattern:auth_or_api_key"})
    return findings


def collect_evidence_digests(outdir: Path) -> dict[str, str]:
    digests: dict[str, str] = {}
    for path in sorted(outdir.rglob("*")):
        if not path.is_file():
            continue
        rel = str(path.relative_to(outdir))
        if is_excluded_evidence_path(rel):
            continue
        digests[rel] = sha256_file(path)
    return digests


def load_run_outcomes(outdir: Path) -> list[dict[str, Any]]:
    runs: list[dict[str, Any]] = []
    pairs = [
        ("golden_path.json", "golden_path.exit", "golden_path"),
        ("golden_path_repeat.json", "golden_path_repeat.exit", "golden_path_repeat"),
    ]
    for json_name, exit_name, label in pairs:
        jp = outdir / json_name
        if not jp.exists():
            continue
        payload = load_json_strict(jp)
        if not isinstance(payload, dict):
            raise ValueError(f"malformed_json:{json_name}:not_object")
        exit_code = None
        ep = outdir / exit_name
        if ep.exists():
            raw = ep.read_text(encoding="utf-8").strip()
            exit_code = int(raw) if raw.isdigit() else None
        redacted, _ = redact_obj(payload)
        assert isinstance(redacted, dict)
        runs.append(extract_run_summary(redacted, exit_code=exit_code, label=label))
    return runs


def build_manifest(
    *,
    git_sha: str,
    outdir: Path,
    command_argv: list[str],
    ci_url: str | None,
    demo_url: str | None,
    limitations: list[str],
    citation_relevance: str,
    artifact_type: str = "runtime_smoke",
    env_values: dict[str, str] | None = None,
) -> dict[str, Any]:
    if not GIT_SHA_RE.match(git_sha):
        raise ValueError("invalid_git_sha")

    if env_values is None:
        env_values = load_dotenv_values(outdir.parents[1] / ".env") if (outdir.parents[1] / ".env").exists() else {}
        # Prefer repo-root .env next to scripts parent (gatekeeper/.env)
        gk_env = Path(__file__).resolve().parents[1] / ".env"
        if gk_env.is_file():
            env_values = load_dotenv_values(gk_env)

    findings = scan_for_secrets(outdir=outdir, env_values=env_values)
    if findings:
        # Fail closed — report file + key name only
        print(json.dumps({"error": "secret_in_evidence", "findings": findings}))
        raise RuntimeError("secret_in_evidence")

    runs = load_run_outcomes(outdir)
    digests = collect_evidence_digests(outdir)
    primary = runs[0] if runs else {}

    return {
        "artifact_type": artifact_type,
        "source_git_sha": git_sha,
        "git_sha": git_sha,
        "utc_timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "command_argv": command_argv,
        "command": " ".join(command_argv),
        "run_count": len(runs),
        "runs": runs,
        "exit_code": primary.get("exit_code"),
        "provider": primary.get("provider"),
        "model": primary.get("model"),
        "request_id": primary.get("request_id"),
        "usage": primary.get("usage"),
        "latency_ms": primary.get("latency_ms"),
        "tavily": primary.get("tavily"),
        "tavily_hits": primary.get("tavily_hits"),
        "verdict": primary.get("verdict"),
        "citation_relevance": citation_relevance,
        "evidence_sha256": digests,
        "ci_url": ci_url,
        "demo_url": demo_url,
        "redactions": [],
        "limitations": limitations,
        "metric_scope_note": (
            "Runtime smoke proves plumbing and fail-closed behavior. "
            "Citation relevance and model/vulnerability accuracy are separate claims."
        ),
    }


def write_manifest_with_sidecar(manifest: dict[str, Any], write_path: Path) -> str:
    text = json.dumps(manifest, indent=2) + "\n"
    if SECRET_RE.search(text):
        raise RuntimeError("secret_pattern_in_manifest")
    write_path.write_text(text, encoding="utf-8")
    digest = sha256_bytes(text.encode("utf-8"))
    sidecar = write_path.with_name(write_path.name + ".sha256")
    sidecar.write_text(digest + "\n", encoding="utf-8")
    return digest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build sanitized Gatekeeper evidence manifest")
    parser.add_argument("--git-sha", required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument(
        "--command-argv-json",
        default=None,
        help="JSON array of sanitized argv tokens (preferred over repeated flags)",
    )
    parser.add_argument("--ci-url", default=None)
    parser.add_argument("--demo-url", default=None)
    parser.add_argument("--citation-relevance", default="NOT_MEASURED")
    parser.add_argument("--artifact-type", default="runtime_smoke")
    parser.add_argument("--limitation", action="append", default=[])
    parser.add_argument("--write", type=Path, default=None, help="Write manifest JSON here")
    args = parser.parse_args(argv)

    if not args.outdir.is_dir():
        print(json.dumps({"error": "outdir missing", "outdir": str(args.outdir)}))
        return 2

    if not GIT_SHA_RE.match(args.git_sha):
        print(json.dumps({"error": "invalid_git_sha"}))
        return 2

    if args.command_argv_json:
        try:
            command_argv = json.loads(args.command_argv_json)
        except json.JSONDecodeError:
            print(json.dumps({"error": "malformed_command_argv_json"}))
            return 2
        if not isinstance(command_argv, list) or not all(isinstance(x, str) for x in command_argv):
            print(json.dumps({"error": "command_argv_json_must_be_string_array"}))
            return 2
    else:
        command_argv = list(DEFAULT_COMMAND_ARGV)
    limitations = list(args.limitation) or [
        "request_id/usage are null when API does not return them",
        "routing benchmark is offline/mocked and is not model quality",
        "citation_relevance is independent of tavily=grounded status",
    ]

    try:
        manifest = build_manifest(
            git_sha=args.git_sha,
            outdir=args.outdir,
            command_argv=command_argv,
            ci_url=args.ci_url,
            demo_url=args.demo_url,
            limitations=limitations,
            citation_relevance=args.citation_relevance,
            artifact_type=args.artifact_type,
        )
    except RuntimeError as exc:
        if str(exc) == "secret_in_evidence":
            return 3
        print(json.dumps({"error": str(exc)}))
        return 3
    except ValueError as exc:
        print(json.dumps({"error": str(exc)}))
        return 2

    if args.write:
        try:
            digest = write_manifest_with_sidecar(manifest, args.write)
        except RuntimeError as exc:
            print(json.dumps({"error": str(exc)}))
            return 3
        # Print digest path only, not secrets
        print(json.dumps({"wrote": str(args.write), "sidecar_sha256": digest}))
    else:
        text = json.dumps(manifest, indent=2)
        if SECRET_RE.search(text):
            print(json.dumps({"error": "secret_pattern_in_manifest"}))
            return 3
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
