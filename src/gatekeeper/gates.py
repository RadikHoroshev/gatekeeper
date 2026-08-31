"""Read-only GO/PARK gate checks against bounty KERNEL state."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

BOUNTY_ROOT = Path.home() / "bounty"
QUEUE_STATE = BOUNTY_ROOT / "state/android-park-queue/QUEUE_STATE.json"
INSTANT_PARK = BOUNTY_ROOT / "research/_shared/ANDROID_INSTANT_PARK_PACKAGES.txt"
# Shipped with the public repo so the spray-block demo works without KERNEL.
DEMO_INSTANT_PARK = Path(__file__).resolve().parents[2] / "fixtures" / "instant_park_demo.txt"

GateVerdict = Literal["ALLOW", "PARK", "BLOCK"]


@dataclass(frozen=True)
class GateResult:
    verdict: GateVerdict
    reason: str
    park_class: str | None = None


def _load_queue_state() -> dict:
    if not QUEUE_STATE.is_file():
        return {}
    return json.loads(QUEUE_STATE.read_text(encoding="utf-8"))


def _read_pkg_list(path: Path) -> set[str]:
    if not path.is_file():
        return set()
    return {
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    }


def _instant_park_packages() -> set[str]:
    return _read_pkg_list(INSTANT_PARK) | _read_pkg_list(DEMO_INSTANT_PARK)


def check_go_contract(
    *,
    package: str | None = None,
    mechanism: str | None = None,
    command: str | None = None,
) -> GateResult:
    """Fail-closed on spray patterns and exhausted queue without named GO."""
    state = _load_queue_state()
    do_not_repeat = set(state.get("do_not_repeat", []))

    if command:
        lowered = command.lower()
        if "go a1 next" in lowered or lowered.strip() == "go gms":
            return GateResult("BLOCK", "spray command forbidden without named mechanism")
        if lowered.startswith("go mobile") and not mechanism:
            return GateResult("BLOCK", "GO Mobile requires <pkg> <mechanism>")

    if package:
        for blocked in do_not_repeat:
            if blocked.lower() in package.lower():
                return GateResult("PARK", f"package in do_not_repeat: {blocked}", "PARK_DO_NOT_REPEAT")

        if package in _instant_park_packages():
            return GateResult("PARK", "package on Instant PARK denylist", "PARK_INSTANT")

    if state.get("queue") == "exhausted_idle" and not mechanism:
        return GateResult(
            "BLOCK",
            "queue exhausted_idle — need A1 delta or GO <pkg> <mechanism>",
        )

    if mechanism:
        return GateResult("ALLOW", f"named mechanism: {mechanism}")

    return GateResult("BLOCK", "no named mechanism or CANDIDATE event")


def check_g0_eligible(*, israel_resident: bool = True, ru_by_resident: bool = False) -> GateResult:
    if ru_by_resident:
        return GateResult("BLOCK", "G0 fail: Russia/Belarus residency — Google payout $0")
    if israel_resident:
        return GateResult("ALLOW", "G0 PASS: eligible jurisdiction (operator Israel)")
    return GateResult("BLOCK", "G0 unknown — fail-closed until residency confirmed")
