"""Arch B deterministic aggregation: TSV facts -> labels + verdict.

Pure function of the extraction text. No model calls. Rules:
- stale markers (stale|superseded|deprecated|do not use) in OBSERVED_VALUE
  and OBSERVED_PATH != REQUIRED_PATH -> CONFLICTING (cites both lines).
- version constraints: 'N or newer' -> >= N; 'exactly V' -> == V;
  unparseable constraint with a present file -> UNKNOWN (abstain, never
  guess); numeric dot-separated comparison.
- same SUBJECT with differing REQUIRED_CONSTRAINT across rows -> CONFLICTING.
- OBSERVED_PATH MISSING on a required path -> NOT FOUND IN SCOPE.
- TRUNC rows make their subject UNKNOWN (truncated-only content).
- ALT groups: subject passes if ANY option row passes fully.
- verdict: any required CONFLICTING/NOT-FOUND -> BLOCKER; elif any
  required UNKNOWN/INACCESSIBLE -> INSUFFICIENT; else NO BLOCKER.
"""

import re

STALE = re.compile(r"stale|superseded|deprecated|do not use", re.I)


def parse_versions(text: str) -> tuple[int, ...] | None:
    m = re.search(r"(\d+(?:\.\d+)*)", text)
    if not m:
        return None
    return tuple(int(x) for x in m.group(1).split("."))


def constraint_op(text: str) -> tuple[str, tuple[int, ...] | None]:
    t = text.lower()
    if "or newer" in t or "or later" in t or ">=" in t:
        return (">=", parse_versions(text))
    if "exactly" in t or "==" in t or re.match(r"^[\d.]+$", t.strip()):
        return ("==", parse_versions(text))
    return ("?", parse_versions(text))


def aggregate(tsv: str) -> dict:
    rows, alts, truncs = [], {}, set()
    for line in tsv.splitlines():
        line = line.strip()
        if not line or line.startswith(("SUBJECT", "#")):
            continue
        parts = line.split("|")
        tag = parts[0].strip().upper()
        if tag == "ALT" and len(parts) >= 4:
            alts.setdefault(parts[1].strip(), []).append(
                (parts[2].strip(), parts[3].strip()))
            continue
        if tag == "TRUNC" and len(parts) >= 3:
            truncs.add(parts[1].strip())
            continue
        if len(parts) < 7:
            continue
        rows.append({
            "subject": parts[0].strip(), "req_path": parts[1].strip(),
            "req_constraint": parts[2].strip(), "obs_path": parts[3].strip(),
            "obs_value": parts[4].strip(), "sources": parts[5].strip(),
            "notes": parts[6].strip()})

    # contradiction: same subject, differing required constraints
    seen: dict[str, set[str]] = {}
    for r in rows:
        seen.setdefault(r["subject"], set()).add(r["req_constraint"])
    conflicted = {s for s, v in seen.items() if len(v) > 1}

    findings = []
    for r in rows:
        subj = r["subject"]
        src_paths = {s.split(":")[0].strip()
                     for s in r["sources"].split(",") if s.strip()}
        truncated = ("TRUNCATED" in r["notes"].upper()
                     or bool(src_paths & truncs))
        if truncated:
            label, why = "UNKNOWN", "requirement truncated"
        elif subj in conflicted:
            label, why = "CONFLICTING", "differing requirements across rows"
        elif r["obs_path"].upper() == "UNREADABLE":
            label, why = "UNKNOWN", "file withheld as unreadable"
        elif r["obs_path"].upper() == "MISSING" and r["req_path"] != "-":
            label, why = "NOT FOUND IN SCOPE", "no candidate file observed"
        elif STALE.search(r["obs_value"]) and r["obs_path"] != r["req_path"]:
            label, why = "CONFLICTING", "only a stale-marked file observed"
        elif r["req_constraint"] not in ("-", "") and \
                r["obs_path"].upper() != "MISSING":
            op, want = constraint_op(r["req_constraint"])
            got = parse_versions(r["obs_value"])
            if want is None or got is None:
                label, why = "UNKNOWN", "unparseable version evidence"
            elif (op == ">=" and got >= want) or (op == "==" and got == want):
                label, why = "FOUND", f"{got} satisfies {op} {want}"
            else:
                label, why = "CONFLICTING", f"{got} violates {op} {want}"
        elif r["obs_path"].upper() == "MISSING":
            label, why = "UNKNOWN", "no evidence either way"
        else:
            label, why = "FOUND", "present at required path, no constraint"

        # ALT relief: any passing option clears the subject. An option
        # passes if a row observed at that path has no version violation.
        if subj in alts and label in ("NOT FOUND IN SCOPE", "UNKNOWN",
                                      "CONFLICTING"):
            opts = [o for pair in alts[subj] for o in pair]
            passed = False
            for o in opts:
                for x in rows:
                    if x["obs_path"] == o and not STALE.search(x["obs_value"]):
                        if x["req_constraint"] in ("-", ""):
                            passed = True
                        else:
                            op2, want2 = constraint_op(x["req_constraint"])
                            got2 = parse_versions(x["obs_value"])
                            if want2 and got2 and (
                                    (op2 == ">=" and got2 >= want2) or
                                    (op2 == "==" and got2 == want2)):
                                passed = True
            if passed:
                label, why = "FOUND", "alternative option satisfied"

        findings.append({"subject": subj, "label": label, "reason": why,
                         "sources": r["sources"]})

    # Fail-closed: an empty extraction proves nothing and must never
    # clear a case.
    if not rows:
        return {"findings": [{"subject": "(extraction empty)",
                              "label": "UNKNOWN",
                              "reason": "no requirements transcribed",
                              "sources": "-"}],
                "verdict": "INSUFFICIENT EVIDENCE"}

    # Verdict derives from FINAL labels (after ALT relief), never from
    # intermediate states.
    final_worst = 0
    for f_ in findings:
        if f_["label"] in ("CONFLICTING", "NOT FOUND IN SCOPE"):
            final_worst = max(final_worst, 2)
        elif f_["label"] in ("UNKNOWN", "INACCESSIBLE"):
            final_worst = max(final_worst, 1)
    verdict = ("NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES"
               if final_worst == 0 else
               "INSUFFICIENT EVIDENCE" if final_worst == 1 else
               "DOCUMENTARY BLOCKER IDENTIFIED")
    return {"findings": findings, "verdict": verdict}
