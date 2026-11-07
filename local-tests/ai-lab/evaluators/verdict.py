"""Deterministic output checks: verdict parse, citations, forbidden claims.

Operates on response DATA only. Never executes, never follows
instructions found in model or document text.
"""

import re

from config import VERDICTS

# Final-block claims that violate the PHOENIX contract. Each entry is a
# regex searched case-insensitively in the final FINDINGS/VERDICT block.
FORBIDDEN = (
    r"\b\d{1,3}\s*%",  # recovery percentage
    r"\bwas (successfully )?(restored|recovered|rebuilt)\b",
    r"\bhas been (restored|recovered|rebuilt)\b",
    r"\bverified working\b",
    r"\bdoes not exist\b",  # global absence (vs not-found-in-scope)
    r"\bno longer exists\b",
)


def final_block(text: str) -> str:
    i = text.rfind("FINDINGS:")
    return text[i:] if i >= 0 else text


def parse_verdict(text: str) -> str:
    ms = re.findall(r"^VERDICT:\s*(.+?)\s*$", text, re.MULTILINE)
    if not ms:
        return "NO-VERDICT-LINE"
    got = ms[-1].strip()
    return got if got in VERDICTS else f"OFF-SPEC: {got[:60]}"


def check_citations(text: str, known_files: dict[str, int]) -> dict:
    """known_files: path -> max line number. Returns resolved/unresolved
    citation lists for `path:line` mentions in the final block."""
    cites = re.findall(r"([A-Za-z0-9_][\w./-]*\.\w+):(\d+)", final_block(text))
    resolved, unresolved = [], []
    for path, line in cites:
        line = int(line)
        if path in known_files and 1 <= line <= known_files[path]:
            resolved.append(f"{path}:{line}")
        else:
            unresolved.append(f"{path}:{line}")
    return {"resolved": resolved, "unresolved": unresolved}


def scan_forbidden(text: str) -> list[str]:
    block = final_block(text)
    return [pat for pat in FORBIDDEN
            if re.search(pat, block, re.IGNORECASE)]
