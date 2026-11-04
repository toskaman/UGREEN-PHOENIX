"""Wave-1 rehearsal: validate the prompt pack and generate session artifacts.

Validations (fail loudly, exit non-zero):
  - 1:1 coverage between prompts.json and labels.json corpora
  - prompt.expected matches the predeclared ground-truth verdict
  - local harness verdict matches too (prediction == ground truth)
  - paste contains the <SCOPE> placeholder and a report-only instruction
  - paste leaks no verdict string and no exact file-subject answer
Generated artifacts (all under local-tests/wave1/):
  - prompt-pack.md, predicted/<id>-<corpus>.md, run-log.md, scoring.md
  - phoenix-wave1-corpora.zip (corpora only; labels stay on the laptop)
"""

import json
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import harness

ROOT = Path(__file__).resolve().parent
WAVE1 = ROOT / "wave1"
VERDICTS = ("DOCUMENTARY BLOCKER IDENTIFIED",
            "NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES",
            "INSUFFICIENT EVIDENCE")
FAILURES = []


def fail(message):
    FAILURES.append(message)
    print("  [FAIL]", message)


def main():
    prompts = json.loads((ROOT / "prompts.json").read_text(encoding="utf-8"))["prompts"]
    labels = json.loads((ROOT / "labels.json").read_text(encoding="utf-8"))["cases"]
    print(f"validating {len(prompts)} prompts against {len(labels)} labeled corpora...")

    ids = [p["id"] for p in prompts]
    if len(set(ids)) != len(ids):
        fail("duplicate prompt ids")
    if {p["corpus"] for p in prompts} != set(labels):
        fail("prompt corpora do not match labels.json cases exactly")

    predicted = {}
    for p in prompts:
        case, paste = p["corpus"], p["paste"]
        scope = ROOT / "corpus" / case
        if not scope.is_dir():
            fail(f"{p['id']}: missing corpus dir {case}")
            continue
        if p["expected"] != labels[case]["verdict"]:
            fail(f"{p['id']}: expected differs from labels.json ground truth")
        result = harness.run(scope)
        predicted[p["id"]] = result
        if result["verdict"] != labels[case]["verdict"]:
            fail(f"{p['id']}: harness prediction differs from ground truth")
        if "<SCOPE>" not in paste:
            fail(f"{p['id']}: paste lacks <SCOPE> placeholder")
        if "Report only" not in paste or "do not save" not in paste:
            fail(f"{p['id']}: paste lacks report-only instruction")
        if any(v in paste for v in VERDICTS):
            fail(f"{p['id']}: paste leaks a verdict string")
        for subject in labels[case].get("key_labels", {}):
            if "/" in subject and subject in paste:
                fail(f"{p['id']}: paste names file-subject answer {subject}")
        if not p.get("watch"):
            fail(f"{p['id']}: empty watch list")
    if FAILURES:
        print(f"\n{len(FAILURES)} validation failures — no artifacts written.")
        return 1
    print("all validations passed.")

    WAVE1.mkdir(exist_ok=True)
    (WAVE1 / "predicted").mkdir(exist_ok=True)

    lines = ["# Wave-1 prompt pack",
             "",
             "Replace `<SCOPE>` with the real NAS upload path. Paste only the",
             "PASTE block. EXPECTED and WATCH sections are scoring-only and",
             "must never be sent to the model.",
             "",
             "Setup note: `access-denied.txt` is a local-simulation stand-in",
             "and is NOT uploaded. On the NAS, enforce the edge denial with",
             "real file permissions on `edge/docs/secret-plan.md`.", ""]
    for p in prompts:
        lines += [f"## {p['id']} — {p['title']} (`{p['corpus']}`)", "",
                  "```text", p["paste"], "```", "",
                  f"EXPECTED (scoring only): {p['expected']}", ""]
        lines += ["WATCH (scoring only):"] + [f"- {w}" for w in p["watch"]] + [""]
    (WAVE1 / "prompt-pack.md").write_text("\n".join(lines), encoding="utf-8")

    for p in prompts:
        result = predicted[p["id"]]
        (WAVE1 / "predicted" / f"{p['id']}-{p['corpus']}.md").write_text(
            f"# Predicted report {p['id']} ({p['corpus']})\n\n"
            "Local-harness prediction for same-day comparison with the real "
            "NAS report. A mismatch is a finding, not a failure.\n\n"
            + result["report"] + "\n", encoding="utf-8")

    log = ["# Wave-1 run log (fill during the session)", ""]
    for p in prompts:
        log += [f"## {p['id']} — {p['corpus']}", "",
                "- Start/end time: ", f"- Pasted scope: `<SCOPE>` = ",
                "- Actual verdict: ", "- Matches predicted: yes/no",
                "- Delegation trace visible: yes/no/partial",
                "- Approval dialogs (screenshots): ",
                "- Deviations from predicted report: ",
                "- Screenshots/recordings: ", ""]
    (WAVE1 / "run-log.md").write_text("\n".join(log), encoding="utf-8")

    scoring = ["# Wave-1 scoring (fill after the session)", "",
               "| prompt | corpus | expected | actual | match | notes |",
               "|---|---|---|---|---|---|"]
    for p in prompts:
        scoring.append(f"| {p['id']} | {p['corpus']} | {p['expected']} "
                       "|  |  |  |")
    (WAVE1 / "scoring.md").write_text("\n".join(scoring), encoding="utf-8")

    zip_path = WAVE1 / "phoenix-wave1-corpora.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted((ROOT / "corpus").rglob("*")):
            if path.is_file() and path.name != "access-denied.txt":
                zf.write(path, path.relative_to(ROOT / "corpus"))
    with zipfile.ZipFile(zip_path) as zf:
        names = zf.namelist()
        assert not any(n.endswith("access-denied.txt") for n in names), \
            "stand-in manifest leaked into upload ZIP"
        assert not any("labels.json" in n or "prompt" in n for n in names), \
            "answers leaked into upload ZIP"
    print(f"artifacts written to {WAVE1} "
          f"(zip: {zip_path.stat().st_size} bytes).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
