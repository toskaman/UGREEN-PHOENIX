"""Skill-contract consistency tests (offline, deterministic).

Guards the TITAN v7 Phase 4 finding: the SKILL.md step-4 verification
contract must agree with the validated harness behavior
(check-then-report-absence, including document-referenced Category B
paths) and with references/decision-protocol.md. A Skill sentence that
contradicts the tested behavior fails here, not on the NAS.
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PASS = 0
FAIL = 0


def check(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  [ok] {name}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name}" + (f" — {detail}" if detail else ""))


skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
proto = (ROOT / "references" / "decision-protocol.md").read_text(
    encoding="utf-8")

# --- 1. no refuse-if-undiscovered contradiction -----------------------------
check("contract: no refuse-if-undiscovered sentence",
      "refuse any path the discovery did not verify" not in skill,
      "SKILL.md step-4 forbids Category B verification")

# --- 2. Category A/B/C verification sources ---------------------------------
step4 = skill.split("4. For each critical referenced dependency,")[1]
step4 = step4.split("4b.")[0]
check("contract: Category A (discovered) allowed",
      "already present in the step-2 discovery result" in step4, step4[:80])
check("contract: Category B (document-cited) allowed",
      "(B)" in step4 and "document-referenced" in step4
      and "path:line citation" in step4,
      "document-referenced paths need an explicit allow rule")
check("contract: Category C (invented) refused",
      "Category C" in step4, "refusal needs a precise target")
check("contract: traversal/out-of-scope rejected without access",
      "traversal" in step4 and "out-of-scope" in step4,
      "path validation must be explicit")

# --- 3. verdict outcomes cover the required cases ---------------------------
check("contract: RESULT covers ABSENT",
      "ABSENT" in step4, "missing-dependency verdicts must be possible")
check("contract: RESULT covers OUT OF SCOPE and UNSAFE",
      "OUT OF SCOPE" in step4 and "UNSAFE" in step4,
      "rejected paths need distinct outcomes, not silence")

# --- 4. protocol agreement ---------------------------------------------------
check("contract: protocol defines Category A/B/C",
      "Category A" in proto and "Category B" in proto
      and "Category C" in proto,
      "references/decision-protocol.md must mirror the contract")

# --- 5. v7 conditional-dependency transfer ------------------------------------
# Gated requirements (unless/only-if/si...) must abstain unless the gating
# condition is itself verified from authorized evidence; XOR ("but not
# both") means exactly one member. The native Skill must state this, since
# the local abstention logic does not run on the NAS.
check("contract: protocol gates conditional requirements",
      "unless" in proto and "only if" in proto
      and "UNKNOWN" in proto,
      "gated requirements need an explicit abstention rule")
check("contract: protocol defines XOR exclusivity",
      "but not both" in proto and "exactly one" in proto,
      "exclusive alternatives need an explicit exactly-one rule")

# --- 6. v7 in-context extraction rule --------------------------------------
# The step-3 delegate instruction (what the model follows in-context) must
# state the gated/XOR semantics itself, not rely on the linked protocol.
step3 = skill.split("3. Only after discovery is")[1].split("4. For each")[0]
check("contract: step-3 states gated-requirement rule",
      "unless" in step3 and "UNKNOWN" in step3,
      "extraction must abstain on unverified gates in-context")
check("contract: step-3 states XOR rule",
      "but not both" in step3 and "exactly one" in step3,
      "extraction must state exactly-one exclusivity in-context")

print(f"\n{PASS} skill-contract checks passed"
      + (f", {FAIL} FAILED" if FAIL else ", ALL GREEN (offline)"))
sys.exit(1 if FAIL else 0)
