"""Extended benchmark loader (x01..x30 dev/validation/locked splits,
plus m01..m12 multilingual-dev split).

Same feeding contract as trackb.py. No model calls here.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent / "ext"


def labels() -> dict:
    return json.loads((ROOT / "labels.json").read_text(encoding="utf-8"))


def splits() -> dict:
    return labels()["_splits"]


def _gold(case: str, labels_map: dict) -> dict:
    return labels_map[case]


def case_input(case: str, labels_map: dict) -> str:
    scope = ROOT / "corpus" / case
    unreadable = labels_map.get(case, {}).get("unreadable", {})
    parts = []
    for path in sorted(scope.rglob("*")):
        if path.is_dir():
            continue
        rel = path.relative_to(scope).as_posix()
        if rel in unreadable:
            parts.append(f"=== {rel} ({path.stat().st_size} bytes) ===\n"
                         f"[UNREADABLE: {unreadable[rel]}]")
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            parts.append(f"=== {rel} ===\n[UNREADABLE: binary or OS error]")
            continue
        numbered = "\n".join(f"{i}| {ln}" for i, ln in
                             enumerate(text.splitlines(), 1))
        parts.append(f"=== {rel} ({path.stat().st_size} bytes) ===\n{numbered}")
    return "\n\n".join(parts)


def known_files(case: str, labels_map: dict) -> dict[str, int]:
    scope = ROOT / "corpus" / case
    unreadable = labels_map.get(case, {}).get("unreadable", {})
    out = {}
    for path in sorted(scope.rglob("*")):
        if path.is_dir():
            continue
        rel = path.relative_to(scope).as_posix()
        if rel in unreadable:
            out[rel] = 1
            continue
        try:
            out[rel] = len(path.read_text(encoding="utf-8").splitlines())
        except (OSError, UnicodeError):
            out[rel] = 1
    return out
