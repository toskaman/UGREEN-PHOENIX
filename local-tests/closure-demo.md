# Flagship demo: "THE BACKUP THAT LOOKED COMPLETE"

A fictional studio saved nearly every project file on its NAS. Filename
search says everything is there. PHOENIX shows the project still cannot
be documented as ready — then proves whether the fix worked.

Rendered evidence (deterministic local simulation of the Skill contract,
rebuilt by `python local-tests/render-demo.py` — not NAS runtime
evidence):

- [Scenario A render](closure-demo-A.rendered.md) — missing asset
- [Scenario B render](closure-demo-B.rendered.md) — hidden incompatibility
- [Scenario C render](closure-demo-C.rendered.md) — false reassurance

## The seven beats

**Beat 1 — False confidence.** The archive looks complete: every expected
filename is found (A: even a stale same-named decoy; C: literally every
named file exists). A file count proves nothing about versions,
locations, or observed facts.

**Beat 2 — Hidden failure.** One critical dependency is wrong. A: the
deployment guide requires `config/prod-config.yaml`, absent from the
authorized scope. B: the guide requires `runtime >= 3.0`; the observed
config declares `runtime 2.4.1`. C: `license >= 2.0` was never observed
at all.

**Beat 3 — Discovery.** PHOENIX assesses the scope: A and B report
`DOCUMENTARY BLOCKER IDENTIFIED` (NOT FOUND IN SCOPE / CONFLICTING);
C reports `INSUFFICIENT EVIDENCE` instead of a false clear.

**Beat 4 — Proof.** Every claim carries its exact source: the rendered
Proof Graphs cite guide lines against observed file lines side by side
(B shows both versions; C shows the gap explicitly).

**Beat 5 — Action.** Section 7 of each report gives prioritized next
steps: B opens with a P1 ("confirm the intended version with the
document owners"); C opens with a P2 ("resolve the evidence gap with a
clearer source"). Specific, evidence-linked, secret-free.

**Beat 6 — Verification.** After the operator changes files inside the
scope, PHOENIX re-inspects from scratch — "I fixed it" is never proof.
The Recovery Delta compares before/after evidence: A and B show
RESOLVED with new citations; C shows STILL UNCERTAIN after an unrelated
readme change, with nothing falsely RESOLVED.

**Beat 7 — Honest outcome.** A corrected documentary blocker is still
not a tested restoration: every delta states it. The user knows what was
wrong, why it mattered, what to do, whether the evidence changed, and
what remains unverified.

## Scenario reference

### Scenario A — Missing asset (`core-a`)

Before: guide requires `config/prod-config.yaml`; stale decoy with the
same basename sits in `old-backup/`. Filename search says FOUND.
PHOENIX says NOT FOUND IN SCOPE (wrong path), verdict BLOCKER.
Fix: operator supplies the file at the documented path.
Recheck: same requirement FOUND, delta RESOLVED, verdict CLEAR.
Covered by checks "A: ...".

### Scenario B — Hidden incompatibility (`core-b`)

Before: `core-b` requires `runtime >= 3.0`; observed `runtime 2.4.1`.
The file exists, so naive checks pass. PHOENIX says CONFLICTING with
both sources cited, verdict BLOCKER, P1 recommendation.
Fix: configuration bumped to a satisfying version.
Recheck: delta RESOLVED, never claiming restoration.
Covered by checks "B: ...".

### Scenario C — False reassurance (synthetic scope)

A scope looks complete (all named files exist) but a version fact was
never observed: verdict INSUFFICIENT EVIDENCE, not CLEAR. An unrelated
change (new readme) must not move the verdict: recheck stays
INSUFFICIENT with STILL UNCERTAIN, nothing falsely RESOLVED.
Covered by checks "C: ...".

## Reproduce

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

Or run the closure block of `run-tests.py` (checks "A:/B:/C: ..."), or
rebuild all three renders with `python local-tests/render-demo.py`.

## What the Skill does on the NAS (same contract)

1. First assessment → 8-section report (§7 Next steps, §8 verdict).
2. User fixes the cited issues inside the authorized scope.
3. User re-invokes with the prior report → steps re-run on fresh evidence.
4. Appended §9 Recovery Delta answers: resolved? what changed? what is
   still unknown? what next? Never a tested restoration.
