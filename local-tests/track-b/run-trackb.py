"""Track B runner: feed held-out natural-language cases to a local model.

Usage: python run-trackb.py <ollama-model>   (daemon must be running)
Feeds each tb* case (numbered lines, unreadable content withheld per
labels.json) with the frozen prompt.md at temperature 0, saves raw
transcripts to transcripts/<model>_<case>.json, and prints a parsed
verdict line per case. Grading against labels.json is manual (see
results.md). Stdlib only. Remember: `ollama stop <model>` when done.
"""

import hashlib
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VERDICTS = ("DOCUMENTARY BLOCKER IDENTIFIED",
            "NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES",
            "INSUFFICIENT EVIDENCE")


def build_case_input(case: str, labels: dict) -> str:
    scope = ROOT / "corpus" / case
    unreadable = labels.get(case, {}).get("unreadable", {})
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


def query(model: str, prompt: str) -> tuple[str, float]:
    body = json.dumps({"model": model, "prompt": prompt, "stream": False,
                       "options": {"temperature": 0, "num_ctx": 8192}}
                      ).encode("utf-8")
    req = urllib.request.Request("http://127.0.0.1:11434/api/generate",
                                 data=body,
                                 headers={"Content-Type": "application/json"})
    start = time.perf_counter()
    with urllib.request.urlopen(req, timeout=900) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data.get("response", ""), time.perf_counter() - start


def parse_verdict(text: str) -> str:
    ms = re.findall(r"^VERDICT:\s*(.+?)\s*$", text, re.MULTILINE)
    if not ms:
        return "NO-VERDICT-LINE"
    got = ms[-1].strip()  # last line wins: thinking may quote the template
    return got if got in VERDICTS else f"OFF-SPEC: {got[:60]}"


def main() -> int:
    model = sys.argv[1]
    prompt = (ROOT / "prompt.md").read_text(encoding="utf-8")
    phash = hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:16]
    labels = json.loads((ROOT / "labels.json").read_text(encoding="utf-8"))
    outdir = ROOT / "transcripts"
    outdir.mkdir(exist_ok=True)
    print(f"model={model} prompt_sha={phash} temp=0")
    for case in sorted(labels):
        full = prompt + "\n" + build_case_input(case, labels)
        try:
            text, secs = query(model, full)
        except Exception as exc:  # noqa: BLE001 - runner must report, not crash
            print(f"{case}: ERROR {exc}")
            continue
        (outdir / f"{model.replace(':', '_')}_{case}.json").write_text(
            json.dumps({"model": model, "case": case, "prompt_sha": phash,
                        "seconds": round(secs, 1), "response": text},
                       indent=2), encoding="utf-8")
        print(f"{case}: {parse_verdict(text)} ({secs:.0f}s)", flush=True)
    print("Done. Unload the model: ollama stop", model)
    return 0


if __name__ == "__main__":
    sys.exit(main())
