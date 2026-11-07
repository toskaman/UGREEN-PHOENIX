"""Track B dataset loader (v4 held-out corpus tb1..tb6).

Same feeding contract as track-b/run-trackb.py: numbered lines,
unreadable content withheld per labels.json. No model calls here.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "track-b"


def labels() -> dict:
    return json.loads((ROOT / "labels.json").read_text(encoding="utf-8"))


def prompt_text() -> str:
    return (ROOT / "prompt.md").read_text(encoding="utf-8")


def prompt_sha() -> str:
    import hashlib
    return hashlib.sha256(prompt_text().encode("utf-8")).hexdigest()[:16]


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
    """path -> max line number, for citation resolution checks."""
    scope = ROOT / "corpus" / case
    unreadable = labels_map.get(case, {}).get("unreadable", {})
    out = {}
    for path in sorted(scope.rglob("*")):
        if path.is_dir():
            continue
        rel = path.relative_to(scope).as_posix()
        if rel in unreadable:
            out[rel] = 1  # the marker line
            continue
        try:
            out[rel] = len(path.read_text(encoding="utf-8").splitlines())
        except (OSError, UnicodeError):
            out[rel] = 1
    return out
