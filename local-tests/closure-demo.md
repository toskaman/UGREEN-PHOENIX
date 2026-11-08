# Flagship demo: "The Recovery That Looked Complete"

A fictional studio preserved nearly every project file — yet PHOENIX shows
the project cannot be documented as ready. Three scenarios, each
reproducible locally (simulation of the Skill's recheck mode):

## Scenario A — Missing asset

Before: `core-a` requires `config/prod-config.yaml`; a stale decoy with
the same basename sits in `old-backup/`. Filename search says FOUND.
PHOENIX says NOT FOUND IN SCOPE (wrong path), verdict BLOCKER.
Fix: operator supplies the file at the documented path.
Recheck: same requirement FOUND, delta RESOLVED, verdict CLEAR.

Reproduce: run the closure block of `run-tests.py` (checks "A: ..."), or:

```python
import harness, shutil, tempfile
from pathlib import Path
with tempfile.TemporaryDirectory() as tmp:
    t = Path(tmp) / "a"
    shutil.copytree("local-tests/corpus/core-a", t)
    before = harness.run(t)                      # BLOCKER
    (t / "config").mkdir(parents=True, exist_ok=True)
    (t / "config" / "prod-config.yaml").write_text("# fix\n")
    after = harness.run(t, prior=before)         # CLEAR + section 9
    print(after["report"].split("## 9. Recovery Delta")[1])
```

## Scenario B — Hidden incompatibility

Before: `core-b` requires `runtime >= 3.0`; observed `runtime 2.4.1`.
The file exists, so naive checks pass. PHOENIX says CONFLICTING with both
sources cited, verdict BLOCKER, recommendation: confirm the intended
version with the document owners.
Fix: configuration bumped to a satisfying version.
Recheck: delta RESOLVED. Covered by checks "B: ...".

## Scenario C — False reassurance

A scope looks complete (all named files exist) but a version fact was
never observed: verdict INSUFFICIENT EVIDENCE, not CLEAR. An unrelated
change (new readme) must not move the verdict: recheck stays
INSUFFICIENT with STILL UNCERTAIN, nothing falsely RESOLVED.
Covered by checks "C: ...".

## What the Skill does on the NAS (same contract)

1. First assessment → 8-section report (§7 recommendations, §8 verdict).
2. User fixes the cited issues inside the authorized scope.
3. User re-invokes with the prior report → steps re-run on fresh evidence.
4. Appended §9 Recovery Delta answers: resolved? what changed? what is
   still unknown? what next? Never a tested restoration.
