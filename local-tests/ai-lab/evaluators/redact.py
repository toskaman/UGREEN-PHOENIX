"""Deterministic secret redaction for persisted transcripts.

High-precision shapes only (Bearer [REDACTED] keys, JWTs, PEM blocks,
password/api-key assignments). Applied at transcript-write time so a
model that echoes a readable credential never persists it verbatim.

Deliberately NOT redacted: bare 'token' words (a legitimate corpus
subject, e.g. token files) and novel secret shapes. Residual risk is
documented, not silently guessed at: unknown shapes stay visible so a
reviewer can extend the patterns.

The marker contains no pipes/tabs/citation shapes, so redacted TSVs
keep their field structure (redacted values simply stop parsing as
versions, which fails closed to UNKNOWN).
"""

import re

MARKER = "[REDACTED]"

_PATTERNS = (
    # Authorization: Bearer [REDACTED] / Basic dGhpcw==
    re.compile(r"(?i)(bearer|basic)\s+[A-Za-z0-9\-._~+/=]+"),
    # AWS access key ids
    re.compile(r"AKIA[0-9A-Z]{16}"),
    # JWTs (header.payload[.signature])
    re.compile(r"eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}"
               r"(?:\.[A-Za-z0-9_-]*)?"),
    # PEM blocks (full span, multiline)
    re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----.*?-----END "
               r"[A-Z0-9 ]*PRIVATE KEY-----", re.DOTALL),
    # password/passwd/pwd/api-key/api_token assignments
    re.compile(r"(?i)(password|passwd|pwd|api[_-]?key|api[_-]?token|secret)"
               r"(\s*[:=]\s*)([^\s,;\"']+)"),
)


def redact(text: str) -> str:
    """Replace secret shapes with [REDACTED], keeping TSV structure."""
    out = text
    for pat in _PATTERNS[:4]:
        out = pat.sub(MARKER, out)
    out = _PATTERNS[4].sub(
        lambda m: m.group(1) + m.group(2) + MARKER, out)
    return out
