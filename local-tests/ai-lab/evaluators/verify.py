"""Row verification: check extraction rows against ground corpus bytes.

Deterministic. For each row, given the case's known_files map and the
withheld (unreadable) map:
- obs UNREADABLE + path in withheld map -> VERIFIED (correctly withheld)
- obs UNREADABLE + path absent from corpus -> CORRECTABLE-TO-MISSING
  (the file does not exist; the model mislabeled absence)
- obs UNREADABLE + path readable in corpus -> UNVERIFIED (the model
  failed to transcribe a readable file; escalate with a targeted
  re-extraction call)
- obs MISSING + path exists readable -> UNVERIFIED (missed a file)
- obs <path> + path absent from corpus -> UNVERIFIED (hallucinated path)
- otherwise -> VERIFIED (value-level checking is future work)

Returns (corrected_tsv, unverified_subjects). Corrections are applied;
unverified rows are left for escalation and flagged.
"""

import re

from datasets import extset, trackb
from evaluators.aggregate import split_row


def _rows(tsv: str) -> list[str]:
    return [ln for ln in (l.strip() for l in tsv.splitlines())
            if ln and not ln.startswith(("SUBJECT", "#"))]


def _src_path(sources: str, known: dict) -> str:
    for s in sources.split(","):
        p = s.split(":")[0].strip()
        if p in known:
            return p
    return sources.split(",")[0].split(":")[0].strip()


def _cites(sources: str, path: str, known: dict) -> bool:
    """True if sources contain a valid path:line citation into path."""
    for s in sources.split(","):
        p, _, num = s.strip().partition(":")
        if p.strip() != path or not num.strip().isdigit():
            continue
        if 1 <= int(num) <= known.get(path, 0):
            return True
    return False


ALT_MARKERS = ("either", "one of", "alternatively", "option")


def _alt_grounded(subject: str, options: list, rows: list, case: str,
                  ds) -> bool:
    """An ALT line is honored only if a cited guide line for a covered
    row actually offers alternatives. Kills invented either/ors (e.g.
    tb2's guides, which mandate different versions without offering a
    choice). Rows match by subject OR by option path."""
    root = ds.ROOT / "corpus" / case
    for r in rows:
        parts = split_row(r)
        if len(parts) < 7:
            continue
        subj, req, obs = (parts[0].strip(), parts[1].strip(),
                          parts[3].strip())
        if subj != subject and req not in options and obs not in options:
            continue
        for cite in parts[5].split(","):
            cite = cite.strip()
            if ":" not in cite:
                continue
            path, _, num = cite.partition(":")
            try:
                lines = (root / path).read_text(encoding="utf-8").splitlines()
                i = int(num) - 1
                window = " ".join(lines[max(0, i - 2):i + 3]).lower()
            except (OSError, ValueError, IndexError, UnicodeError):
                continue
            if any(m in window for m in ALT_MARKERS):
                return True
    return False


def _truncated_docs(case: str, ds, known: dict, withheld: dict) -> set[str]:
    """Deterministic truncation net: a guide-ish document (*.md) whose
    last line lacks terminal punctuation, or that names absent content,
    is treated as truncated even if the model did not flag it."""
    root = ds.ROOT / "corpus" / case
    out = set()
    for rel in known:
        if rel in withheld or not rel.endswith(".md"):
            continue
        try:
            text = (root / rel).read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
        lines = [l for l in text.splitlines() if l.strip()]
        if not lines:
            continue
        low = text.lower()
        if "appendix" in low and "appendix.md" not in str(list(known)):
            out.add(rel)
            continue
        if re.search(r"page \d+.*missing|missing.*page|truncat", low):
            out.add(rel)
            continue
        if not lines[-1].rstrip().endswith((".", "!", "?", ":", '"', "'")):
            out.add(rel)
    return out


def verify(case: str, tsv: str, dataset: str = "trackb") -> dict:
    ds = trackb if dataset == "trackb" else extset
    labels = ds.labels()
    known = ds.known_files(case, labels)
    withheld = labels.get(case, {}).get("unreadable", {})
    for rel in sorted(_truncated_docs(case, ds, known, withheld)):
        tsv += f"\nTRUNC | {rel} | deterministic: abrupt or marked ending"
    raw_lines = _rows(tsv)
    corrected, unverified = [], []
    for line in raw_lines:
        parts = split_row(line)
        tag = parts[0].strip().upper()
        if tag == "ALT" and len(parts) >= 4:
            if _alt_grounded(parts[1].strip(),
                             [p.strip() for p in parts[2:4]],
                             raw_lines, case, ds):
                corrected.append(line)
            # else: invented alternative, dropped with prejudice
            continue
        if tag == "TRUNC" or len(parts) < 7:
            corrected.append(line)
            continue
        subj = parts[0].strip()
        obs = parts[3].strip()
        obs_u = obs.upper()
        if obs_u == "UNREADABLE":
            # which path did the model mean? recover from sources or req
            cand = parts[1].strip()
            srcs = [s.split(":")[0].strip()
                    for s in parts[5].split(",") if s.strip()]
            path = cand if cand != "-" else next(
                (s for s in srcs if s in known or s in withheld), cand)
            if cand in withheld or path in withheld:
                corrected.append(line)  # correctly withheld
            elif cand != "-" and cand not in known and path not in known:
                parts[3] = "MISSING"  # absence, not unreadability
                corrected.append("|".join(parts))
            elif parts[4].strip() not in ("", "-") and _cites(
                    parts[5], cand if cand != "-" else path, known):
                parts[3] = cand if cand != "-" else path
                corrected.append("|".join(parts))
                # observably read: valid citation into the file
            else:
                unverified.append((subj, _src_path(parts[5], known)))
                corrected.append(line)
        elif obs_u == "MISSING":
            cand = parts[1].strip()
            if cand != "-" and cand in known and cand not in withheld:
                unverified.append((subj, _src_path(parts[5], known)))
            corrected.append(line)
        else:
            if obs not in known:
                unverified.append((subj, _src_path(parts[5], known)))
            corrected.append(line)
    return {"tsv": "\n".join(corrected),
            "unverified": sorted(set(unverified))}
