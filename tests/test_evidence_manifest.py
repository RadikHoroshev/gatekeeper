"""Tests for evidence manifest builder and redaction."""

from __future__ import annotations

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_evidence_manifest as manifest  # noqa: E402

FULL_SHA = "92a491f54a991952d932b0c14e987077be0f8913"


def _write_pair(out: Path, label: str, payload: dict, exit_code: int = 0) -> None:
    (out / f"{label}.json").write_text(json.dumps(payload), encoding="utf-8")
    (out / f"{label}.exit").write_text(f"{exit_code}\n", encoding="utf-8")
    (out / f"{label}.stderr").write_text("", encoding="utf-8")


class EvidenceManifestTests(unittest.TestCase):
    def test_redacts_secret_like_fields(self):
        payload = {
            "verdict": "PARK",
            "api_key": "tvly-should-not-appear",
            "nested": {"Authorization": "Bearer abc.def"},
            "note": "normal text",
        }
        redacted, paths = manifest.redact_obj(payload)
        self.assertEqual(redacted["api_key"], "<redacted>")
        self.assertEqual(redacted["nested"]["Authorization"], "<redacted>")
        self.assertIn("$.api_key", paths)
        blob = json.dumps(redacted)
        self.assertNotIn("tvly-should-not-appear", blob)
        self.assertNotIn("Bearer abc", blob)

    def test_excludes_manifest_outputs_from_evidence_sha256(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            _write_pair(
                out,
                "golden_path",
                {
                    "verdict": "PARK",
                    "provider": "nebius-token-factory",
                    "model": "nvidia/nemotron-3-super-120b-a12b",
                    "tavily": "grounded",
                    "tavily_hits": 3,
                    "citations": [{"title": "t", "url": "https://example.com", "snippet": "s"}],
                    "usage": {"total_tokens": 10},
                    "request_id": "req-1",
                    "latency_ms": {"total": 1},
                    "finding": False,
                    "nemotron": "completed",
                },
            )
            _write_pair(
                out,
                "golden_path_repeat",
                {
                    "verdict": "PARK",
                    "provider": "nebius-token-factory",
                    "model": "nvidia/nemotron-3-super-120b-a12b",
                    "tavily": "grounded",
                    "tavily_hits": 3,
                    "citations": [{"title": "t", "url": "https://example.com", "snippet": "s"}],
                    "usage": {"total_tokens": 11},
                    "request_id": "req-2",
                    "latency_ms": {"total": 2},
                    "finding": False,
                    "nemotron": "completed",
                },
            )
            (out / "release-manifest.json").write_text("{}\n", encoding="utf-8")
            (out / "manifest_stdout.json").write_text("{}\n", encoding="utf-8")
            (out / "release-manifest.json.sha256").write_text("abc\n", encoding="utf-8")

            built = manifest.build_manifest(
                git_sha=FULL_SHA,
                outdir=out,
                command_argv=list(manifest.DEFAULT_COMMAND_ARGV),
                ci_url="https://example.com/ci",
                demo_url="https://youtu.be/_nyPil6cb_g",
                limitations=["example"],
                citation_relevance="FAILED_MANUAL_REVIEW",
            )
            keys = set(built["evidence_sha256"])
            self.assertIn("golden_path.json", keys)
            self.assertIn("golden_path_repeat.json", keys)
            self.assertNotIn("release-manifest.json", keys)
            self.assertNotIn("manifest_stdout.json", keys)
            self.assertNotIn("release-manifest.json.sha256", keys)
            self.assertNotIn("manifest_sha256", built)
            self.assertNotIn("GO_RUNTIME_PROOF", json.dumps(built))
            self.assertEqual(built["run_count"], 2)
            self.assertEqual(len(built["runs"]), 2)
            self.assertEqual(built["command_argv"], list(manifest.DEFAULT_COMMAND_ARGV))
            self.assertEqual(built["citation_relevance"], "FAILED_MANUAL_REVIEW")
            self.assertEqual(built["artifact_type"], "runtime_smoke")
            self.assertEqual(built["source_git_sha"], FULL_SHA)

            write_path = out / "release-manifest.new.json"
            digest = manifest.write_manifest_with_sidecar(built, write_path)
            sidecar = write_path.with_name(write_path.name + ".sha256")
            self.assertTrue(sidecar.is_file())
            self.assertEqual(sidecar.read_text(encoding="utf-8").strip(), digest)
            self.assertEqual(manifest.sha256_file(write_path), digest)
            # still excluded if present under outdir naming
            self.assertTrue(manifest.is_excluded_evidence_path("release-manifest.new.json"))

    def test_command_argv_round_trip_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            _write_pair(
                out,
                "golden_path",
                {
                    "verdict": "PARK",
                    "provider": "nebius-token-factory",
                    "model": "nvidia/nemotron-3-super-120b-a12b",
                    "tavily": "grounded",
                    "tavily_hits": 1,
                    "citations": [],
                    "finding": False,
                    "nemotron": "completed",
                },
            )
            argv = [
                "--git-sha",
                FULL_SHA,
                "--outdir",
                str(out),
                "--citation-relevance",
                "NOT_MEASURED",
                "--command-argv-json",
                json.dumps(list(manifest.DEFAULT_COMMAND_ARGV)),
                "--write",
                str(out / "release-manifest.json"),
            ]
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = manifest.main(argv)
            self.assertEqual(rc, 0)
            data = json.loads((out / "release-manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(data["command_argv"], list(manifest.DEFAULT_COMMAND_ARGV))
            self.assertTrue((out / "release-manifest.json.sha256").is_file())

    def test_secret_in_evidence_fails_closed_without_printing_value(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            secret = "tvly-SYNTHETICSECRETVALUE99"
            _write_pair(
                out,
                "golden_path",
                {"verdict": "PARK", "note": f"leaked {secret}"},
            )
            buf = io.StringIO()
            with redirect_stdout(buf):
                with mock.patch.object(manifest, "load_dotenv_values", return_value={}):
                    rc = manifest.main(
                        ["--git-sha", FULL_SHA, "--outdir", str(out), "--write", str(out / "m.json")]
                    )
            self.assertNotEqual(rc, 0)
            printed = buf.getvalue()
            self.assertNotIn(secret, printed)
            self.assertIn("secret_in_evidence", printed)
            self.assertIn("golden_path.json", printed)

    def test_env_value_match_reports_key_not_value(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            env_secret = "NEBIUS_LIVE_TEST_VALUE_XYZ"
            _write_pair(out, "golden_path", {"verdict": "PARK", "x": env_secret})
            buf = io.StringIO()
            with redirect_stdout(buf):
                try:
                    manifest.build_manifest(
                        git_sha=FULL_SHA,
                        outdir=out,
                        command_argv=["python3", "-m", "gatekeeper.triage"],
                        ci_url=None,
                        demo_url=None,
                        limitations=[],
                        citation_relevance="NOT_MEASURED",
                        env_values={"NEBIUS_API_KEY": env_secret},
                    )
                    self.fail("expected RuntimeError")
                except RuntimeError as exc:
                    self.assertEqual(str(exc), "secret_in_evidence")
            printed = buf.getvalue()
            self.assertNotIn(env_secret, printed)
            self.assertIn("NEBIUS_API_KEY", printed)
            self.assertIn("golden_path.json", printed)

    def test_invalid_git_sha_rejected(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = manifest.main(["--git-sha", "deadbeef", "--outdir", "/tmp"])
        self.assertEqual(rc, 2)
        self.assertIn("invalid_git_sha", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
