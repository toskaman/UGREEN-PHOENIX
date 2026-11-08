"""Arch B deterministic aggregation: TSV facts -> labels + verdict.

Pure function of the extraction text. No model calls. Rules:
- stale markers (stale|superseded|deprecated|do not use) in OBSERVED_VALUE
  on a pathed row -> CONFLICTING, even when the required file itself is
  stale-marked (stale-never-satisfies; '-' restatement rows exempt).
- version constraints via normalize.py (EN/FR bounds, ranges, series,
  strict/inclusive, exclusions): SATISFIED -> FOUND, VIOLATED ->
  CONFLICTING, anything ambiguous -> UNKNOWN (abstain, never guess).
  Operand selection is noun-aware; bare stated versions clear only on
  equality and abstain on difference. Numeric dot-separated comparison.
- same SUBJECT with differing REQUIRED_CONSTRAINT across rows -> CONFLICTING.
- OBSERVED_PATH MISSING on a required path -> NOT FOUND IN SCOPE.
- TRUNC rows / TRUNCATED keywords make their subject UNKNOWN; when
  truncated_docs is supplied, model-claimed truncation counts only for
  byte-confirmed documents.
- ALT groups: subject passes if ANY option row passes fully (an option
  with a constraint passes only when provably SATISFIED).
- malformed rows (whitespace or <> in a path cell: thinking-trace
  chatter shaped like TSV) -> UNKNOWN, never a FOUND/BLOCKER vote,
  and excluded from cross-row contradiction detection.
- when known (path -> max line) is supplied, a row scores only if at
  least one of its path:line citations resolves into it; forged
  citations to absent paths/lines are dropped (never scored).
- verdict: any required CONFLICTING/NOT-FOUND -> BLOCKER; elif any
  required UNKNOWN/INACCESSIBLE -> INSUFFICIENT; else NO BLOCKER.
"""

import re

from evaluators import normalize as norm_mod

STALE = re.compile(r"stale|superseded|deprecated|do not use", re.I)


def _version_ok(req_constraint: str, obs_value: str) -> bool:
    """True only when the observed version provably satisfies the
    normalized constraint (shared by scoring and ALT relief)."""
    norm = norm_mod.normalize_constraint(req_constraint)
    code, _ = norm_mod.compare(
        norm, norm_mod.pick_observed(
            req_constraint, obs_value,
            norm_op=norm["op"] if norm else None))
    return code == "SATISFIED"


CITE = re.compile(r"[\w./-]+\.\w+:\d+")


def _cite_resolves(sources: str, known: dict) -> bool:
    """True if any path:line citation resolves into path->max-line."""
    for s in sources.split(","):
        p, _, num = s.strip().partition(":")
        p = p.strip()
        num = num.strip()
        if p in known and num.isdigit() and 1 <= int(num) <= known[p]:
            return True
    return False


def _path_cells_ok(req_path: str, obs_path: str) -> bool:
    """Path cells are single tokens: whitespace or angle brackets mark
    thinking-trace chatter ('the plates folder', '<subject>'), never a
    real transcribed path (which may still be '-' or MISSING)."""
    for cell in (req_path, obs_path):
        if any(c.isspace() for c in cell) or "<" in cell or ">" in cell:
            return False
    return True


def split_row(line: str) -> list[str]:
    """Field separator: tabs if the line has them (true TSV), else pipes
    (the visual separator from the prompt examples)."""
    return line.split("\t") if "\t" in line else line.split("|")


def _seps(line: str) -> tuple[str, int]:
    if "\t" in line and line.count("\t") >= line.count("|"):
        return ("\t", line.count("\t"))
    return ("|", line.count("|"))


def _physical_lines(tsv: str) -> list[str]:
    """Join wrapped rows: a fragment line (<7 fields) continues only onto
    a fragment buffer with the SAME separator. Pure prose (no separator)
    is dropped, never glued to rows; a complete row always flushes."""
    out, buf, buf_sep, buf_n = [], "", "|", 0

    def flush():
        nonlocal buf, buf_n
        if buf:
            out.append(buf)
            buf, buf_n = "", 0

    for raw in tsv.splitlines():
        line = raw.strip()
        if not line:
            flush()
            continue
        head = split_row(line)[0].strip().upper()
        if head in ("ALT", "TRUNC", "SUBJECT") or line.startswith("#"):
            flush()
            out.append(line)
            continue
        sep, n = _seps(line)
        if n == 0:
            flush()  # prose, never row content
            continue
        if buf and buf_n < 6 and n < 6 and sep == buf_sep:
            buf = f"{buf} {line}"
            buf_n = buf.count(sep)
            if buf_n >= 6:
                flush()
        else:
            flush()
            buf, buf_sep, buf_n = line, sep, n
            if buf_n >= 6:
                flush()
    flush()
    return out


def aggregate(tsv: str, known: dict | None = None,
              truncated_docs: set | None = None) -> dict:
    rows, alts, truncs = [], {}, set()
    for line in _physical_lines(tsv):
        if line.startswith(("SUBJECT", "#")):
            continue
        parts = split_row(line)
        tag = parts[0].strip().upper()
        if tag == "ALT" and len(parts) >= 4:
            alts.setdefault(parts[1].strip(), []).append(
                (parts[2].strip(), parts[3].strip()))
            continue
        if tag == "TRUNC" and len(parts) >= 3:
            # Model-claimed truncation is honored only when the byte
            # net confirms the document (when a net is supplied);
            # otherwise any row could force-abstain its subject.
            doc = parts[1].strip()
            if truncated_docs is None or doc in truncated_docs:
                truncs.add(doc)
            continue
        if len(parts) < 7:
            continue
        sources = parts[5].strip()
        if not CITE.search(sources):
            continue  # chatter line, not a cited row
        if known is not None and not _cite_resolves(sources, known):
            continue  # forged or misaddressed citation, never scored
        if "*" in parts[0] or "`" in parts[0]:
            continue  # markdown-quoted chatter, not a real row
        req_path = parts[1].strip()
        req_constraint = parts[2].strip()
        if req_constraint == req_path:
            req_constraint = "-"  # model echoed the path, not a constraint
        rows.append({
            "subject": parts[0].strip(), "req_path": req_path,
            "req_constraint": req_constraint, "obs_path": parts[3].strip(),
            "obs_value": parts[4].strip(), "sources": sources,
            "notes": parts[6].strip(),
            "suspect": not _path_cells_ok(
                req_path, parts[3].strip())})

    # contradiction: same subject AND same observed file, but differing
    # required constraints. (Same subject on different files is two
    # requirements sharing a name, not a contradiction.)
    seen: dict[tuple[str, str], set[str]] = {}
    for r in rows:
        if r["obs_path"].upper() not in ("MISSING", "UNREADABLE") \
                and not r["suspect"]:
            seen.setdefault((r["subject"], r["obs_path"]),
                            set()).add(r["req_constraint"])
    conflicted = {s for (s, _), v in seen.items() if len(v) > 1}
    # observed-value disagreement: same subject stated with different
    # numeric values across readable sources (e.g. port 8080 vs 9090).
    # Values group by subject noun ('port 8080 schema 2' votes under
    # both 'port' and 'schema'), with trailing zeros stripped so 2.4
    # and 2.4.0 agree. Rows without numerics do not participate.
    obs_groups: dict[str, dict[str | None, set]] = {}
    for r in rows:
        if r["obs_path"].upper() in ("MISSING", "UNREADABLE"):
            continue
        if r["suspect"]:
            continue
        for noun, tup in norm_mod.extract_tagged(
                norm_mod.fold(r["obs_value"])):
            while len(tup) > 1 and tup[-1] == 0:
                tup = tup[:-1]
            obs_groups.setdefault(r["subject"], {}).setdefault(
                noun, set()).add(tup)
    conflicted |= {s for s, g in obs_groups.items()
                   if any(len(v) > 1 for v in g.values())}

    findings = []
    for r in rows:
        subj = r["subject"]
        src_paths = {s.split(":")[0].strip()
                     for s in r["sources"].split(",") if s.strip()}
        kw_trunc = "TRUNCATED" in r["notes"].upper()
        if kw_trunc and truncated_docs is not None:
            # A model-typed TRUNCATED keyword counts only when a cited
            # document is byte-confirmed truncated.
            kw_trunc = bool(src_paths & truncated_docs)
        truncated = (kw_trunc or bool(src_paths & truncs))
        if r["suspect"]:
            label, why = "UNKNOWN", "row cells malformed; not trusted"
        elif truncated:
            label, why = "UNKNOWN", "requirement truncated"
        elif subj in conflicted:
            label, why = "CONFLICTING", "differing requirements across rows"
        elif r["obs_path"].upper() == "UNREADABLE":
            label, why = "UNKNOWN", "file withheld as unreadable"
        elif r["obs_path"].upper() == "MISSING" and r["req_path"] != "-":
            label, why = "NOT FOUND IN SCOPE", "no candidate file observed"
        elif r["req_path"] != "-" and STALE.search(r["obs_value"]):
            # Stale-never-satisfies, including when the required file
            # itself is stale-marked (not only a divergent decoy).
            label, why = "CONFLICTING", "stale-marked evidence observed"
        elif r["req_constraint"] not in ("-", "") and \
                r["obs_path"].upper() != "MISSING":
            norm = norm_mod.normalize_constraint(r["req_constraint"])
            code, why2 = norm_mod.compare(
                norm, norm_mod.pick_observed(
                    r["req_constraint"], r["obs_value"],
                    norm_op=norm["op"] if norm else None))
            if code == "SATISFIED":
                label, why = "FOUND", why2
            elif code == "VIOLATED":
                label, why = "CONFLICTING", why2
            else:
                label, why = "UNKNOWN", why2
        elif r["obs_path"].upper() == "MISSING":
            label, why = "UNKNOWN", "no evidence either way"
        else:
            label, why = "FOUND", "present at required path, no constraint"

        # ALT relief: any passing option clears the rows it covers. ALT
        # lines match rows by subject OR by option path (models often
        # name the group, e.g. "billing job", instead of a row subject).
        covering = [opts for _s, opts in alts.items()
                    if _s == subj or any(
                        r["req_path"] == o or r["obs_path"] == o
                        for tup in opts for o in tup)]
        if covering and label in ("NOT FOUND IN SCOPE", "UNKNOWN",
                                  "CONFLICTING"):
            opts = [o for pairs in covering for tup in pairs
                    for o in tup]
            passed = False
            for o in opts:
                for x in rows:
                    if x["obs_path"] == o and not STALE.search(x["obs_value"]):
                        if x["req_constraint"] in ("-", ""):
                            passed = True
                        elif _version_ok(x["req_constraint"],
                                         x["obs_value"]):
                            passed = True
            if passed:
                label, why = "FOUND", "alternative option satisfied"

        findings.append({"subject": subj, "label": label, "reason": why,
                         "sources": r["sources"],
                         "req_path": r["req_path"],
                         "obs_path": r["obs_path"]})

    # Fail-closed: an empty extraction proves nothing and must never
    # clear a case.
    if not rows:
        return {"findings": [{"subject": "(extraction empty)",
                              "label": "UNKNOWN",
                              "reason": "no requirements transcribed",
                              "sources": "-", "req_path": "-",
                              "obs_path": "-"}],
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
