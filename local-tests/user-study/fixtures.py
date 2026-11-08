"""Build user-study task dirs. Usage:
python local-tests/user-study/fixtures.py A|B <dest-dir>

Copies the broken corpus, writes the participant TASK.md, the
facilitator-only FIX_SHEET.md, and the PHOENIX_BEFORE.md printout
(first-run report). Synthetic data only.
"""

import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

import harness

SCENARIOS = {
    "A": {"corpus": "core-a", "title": "Missing asset",
          "fix": ("Create the file `config/prod-config.yaml` inside the "
                  "task folder (any content, e.g. `# supplied`). "
                  "Do NOT create it elsewhere.")},
    "B": {"corpus": "core-b", "title": "Hidden incompatibility",
          "fix": ("Edit `config/runtime.yaml` so it declares "
                  "`PROVIDES: runtime 3.0` (replace the old version line). "
                  "Do NOT touch the deployment guide.")},
}

TASK_MD = """# Task ({tag}): {title}

You lost your main computer. This folder is the project copy from the
NAS. Your goal: decide whether the project can be reconstructed, and
say what is missing or contradictory and what to do next.

Rules: read any file in this folder. Do NOT copy files in from
outside. Think aloud — say what you assume before you verify it.
The facilitator times each step with a stopwatch.
"""

FIX_SHEET = """# FIX SHEET — FACILITATOR ONLY, sealed until T5

Scenario {tag} ({title}). When the participant reaches T5, hand them
this sheet and let them apply the fix with their own hands:

{fix}

After the fix: manual condition → participant re-inspects and judges
resolved/still-uncertain. PHOENIX condition → facilitator regenerates
the report (`harness.run` on this dir with the before-report as
prior), prints the Recovery Delta, participant judges.
"""


def main():
    tag, dest = sys.argv[1].upper(), Path(sys.argv[2])
    sc = SCENARIOS[tag]
    dest.mkdir(parents=True, exist_ok=True)
    for item in (ROOT / "corpus" / sc["corpus"]).iterdir():
        tgt = dest / item.name
        if item.is_dir():
            shutil.copytree(item, tgt, dirs_exist_ok=True)
        else:
            shutil.copy2(item, tgt)
    (dest / "TASK.md").write_text(
        TASK_MD.format(tag=tag, title=sc["title"]), encoding="utf-8")
    (dest / "FIX_SHEET.md").write_text(
        FIX_SHEET.format(tag=tag, title=sc["title"], fix=sc["fix"]),
        encoding="utf-8")
    res = harness.run(dest)
    (dest / "PHOENIX_BEFORE.md").write_text(
        "# PHOENIX first-run report (printout for the PHOENIX condition)\n\n"
        + res["report"] + "\n", encoding="utf-8")
    print(f"task {tag} ready at {dest} (verdict: {res['verdict']})")


if __name__ == "__main__":
    main()
