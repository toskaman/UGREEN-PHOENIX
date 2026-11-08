"""Constraint normalization: natural-language version requirements
(English + French) into machine-comparable bounds.

Pipeline: EXTRACT tags/numbers -> NORMALIZE to a bound struct ->
COMPARE against the observed version. Fail-closed throughout: any
ambiguity (contradictory cues, decimal commas, vague qualifiers,
multi-number confusion, imprecise series evidence) yields None /
UNKNOWN, never a guessed comparison.

Bound struct: {op, low, high, lo_inc, hi_inc, exclusions} with ops:
  GE/GT/LE/LT  one-sided bounds, inclusive/exclusive
  EQ           exact version
  RANGE        closed/open interval (endpoint flags)
  SERIES       major series N.x (observed major must equal N)
  BARE         bare stated version (equal clears, differ abstains)
  ANY          no bound (only exclusions apply)
Tuples compare dot-separated numerically with zero-padding, so
2.4 == 2.4.0 and 1.10 > 1.9.
"""

import re
import unicodedata

NUM = r"\d+(?:\.\d+)*"
NUM_RE = re.compile(NUM)
DECIMAL_COMMA_RE = re.compile(r"\d,\d")
SERIES_RE = re.compile(r"(\d+)\s*\.\s*x\b")
PLUS_RE = re.compile(r"(\d+(?:\.\d+)*)\s*\+")
NOUN_BEFORE_RE = re.compile(r"[a-z]{2,}")

# Cue/adjective vocabulary is never a subject noun: in 'schema
# exactly 3' the operand noun is 'schema', not 'exactly'.
NOUN_CUE_STOP = frozenset({
    "exact", "exactly", "minimum", "maximum", "newer", "newest",
    "older", "oldest", "later", "latest", "earlier", "earliest",
    "recent", "exactement", "precisement", "recente", "recents",
    "ancien", "ancienne", "anciens", "superieur", "superieure",
    "inferieur", "inferieure", "ulterieur", "ulterieure",
    "anterieur", "anterieure", "at", "least", "most", "than",
    "must", "be", "doit", "etre", "pinned", "version",
})

# Observed values that carry no comparable version.
VAGUE_RE = re.compile(
    r"\btbd\b|\blatest\b|\brecent\b|\ba confirmer\b|\ben attente\b|"
    r"\ble plus recent\b|\bto be confirmed\b|\bunknown\b|\bn/a\b|"
    r"\btodo\b|\b\?\?\?")

STRONG_EXACT_RE = re.compile(r"exactly|exactement|precisement|==")
WEAK_EXACT_RE = re.compile(r"must be|doit etre|pinned at")
EQ_SYMBOL_RE = re.compile(r"(?<![<>=!])=(?![=])")
NEQ_RE = re.compile(r"!=")
MIN_RE = re.compile(
    r"or newer|or later|at least|minimum|au moins|>=|"
    r"ou\s+superieur\w*|ou\s+plus\s+recent\w*|ou\s+ulterieur\w*")
MAX_RE = re.compile(
    r"or older|or earlier|at most|maximum|up to|no newer than|"
    r"no later than|not\s+newer than|not\s+later than|<=|"
    r"ou\s+anterieur\w*|ou\s+plus\s+ancien\w*|au\s+plus|jusqu['\.]?a")
STRICT_GT_RE = re.compile(
    r"(?<![<>=!])>(?![=])|(?<!no\s)(?<!not\s)newer than|"
    r"(?<!no\s)(?<!not\s)later than|above\s+\d|"
    r"strictement\s+superieur|plus\s+recent\s+que")
STRICT_LT_RE = re.compile(
    r"(?<![<>=!])<(?![=])|older than|earlier than|below\s+\d|"
    r"strictement\s+inferieur\w*|anterieur\w*\s+a\b|"
    r"inferieur\w*\s+a\b|"
    r"plus\s+ancien\s+que|plus\s+vieux\s+que")
EXCLUDE_RE = re.compile(r"not\s+including|exclu\w*|excluded|but\s+not")
RANGE_RES = (
    re.compile(r"between\s+(NUM)\s+and\s+(NUM)".replace("NUM", NUM)),
    re.compile(r"entre\s+(NUM)\s+et\s+(NUM)".replace("NUM", NUM)),
    re.compile(r"(NUM)\s+through\s+(NUM)".replace("NUM", NUM)),
    re.compile(r"versions?\s+(NUM)\s+to\s+(NUM)".replace("NUM", NUM)),
    re.compile(r"versions?\s+(NUM)\s+a\s+(NUM)".replace("NUM", NUM)),
    re.compile(r"\bde\s+(NUM)\s+a\s+(NUM)".replace("NUM", NUM)),
    re.compile(r"versions?\s+(NUM)\s*-\s*(NUM)".replace("NUM", NUM)),
)


def fold(text: str) -> str:
    """NFKC + lowercase + accent/apostrophe folding. Digits/dots kept."""
    text = unicodedata.normalize("NFKC", text).lower()
    text = text.replace("’", "'").replace("‘", "'").replace("`", "'")
    out = []
    for ch in unicodedata.normalize("NFD", text):
        if unicodedata.category(ch) != "Mn":
            out.append(ch)
    return "".join(out)


def _tup(num: str) -> tuple[int, ...]:
    return tuple(int(x) for x in num.split("."))


def _pad(a: tuple[int, ...], b: tuple[int, ...]):
    n = max(len(a), len(b))
    return a + (0,) * (n - len(a)), b + (0,) * (n - len(b))


def _cmp(a: tuple[int, ...], b: tuple[int, ...]) -> int:
    a, b = _pad(a, b)
    return (a > b) - (a < b)


def extract_tagged(text: str) -> list:
    """[(noun|None, version-tuple)] in order. 'schema 2' -> ('schema',
    (2,)); bare '2' -> (None, (2,)). The noun is the nearest
    preceding word that is not cue vocabulary ('schema exactly 3'
    tags 3 with 'schema')."""
    out = []
    for m in NUM_RE.finditer(text):
        words = NOUN_BEFORE_RE.findall(text[:m.start()])
        noun = None
        for w in reversed(words[-3:]):
            if w not in NOUN_CUE_STOP:
                noun = w
                break
        out.append((noun, _tup(m.group(0))))
    return out


def _excluded_numbers(folded: str) -> set:
    """Version numbers named by an exclusion cue, either side
    ('not including 5', 'version 6 exclue', '(2 excluded)').
    Windows are tight so a distant bound is never swallowed."""
    out = set()
    for m in EXCLUDE_RE.finditer(folded):
        fwd = folded[m.end():m.end() + 12]
        nm = NUM_RE.search(fwd)
        if nm:
            out.add(_tup(nm.group(0)))
            continue
        back = folded[max(0, m.start() - 14):m.start()]
        nms = list(NUM_RE.finditer(back))
        if nms:
            out.add(_tup(nms[-1].group(0)))
    return out


def _struct(op, low=None, high=None, lo_inc=True, hi_inc=True,
            major=None, exclusions=frozenset()):
    return {"op": op, "low": low, "high": high, "lo_inc": lo_inc,
            "hi_inc": hi_inc, "major": major, "exclusions": exclusions}


def normalize_constraint(text: str):
    """Natural-language requirement -> bound struct, or None when the
    constraint is absent, vague, contradictory, or ambiguous."""
    f = fold(text)
    if DECIMAL_COMMA_RE.search(f):
        return None  # '2,4' is never parsed as 2.4
    tagged = extract_tagged(f)
    numbers = [t for _, t in tagged]
    if len(set(numbers)) == 1:
        # Redundant restatement ('newer than 2 (2 excluded)') names
        # one bound twice; degenerate ranges stay None downstream.
        numbers = numbers[:1]
    series = SERIES_RE.search(f)
    plus = PLUS_RE.search(f)
    has_min = bool(MIN_RE.search(f)) or bool(plus)
    has_max = bool(MAX_RE.search(f))
    has_gt = bool(STRICT_GT_RE.search(f))
    has_lt = bool(STRICT_LT_RE.search(f))
    has_strong = bool(STRONG_EXACT_RE.search(f))
    has_weak = bool(WEAK_EXACT_RE.search(f)) or bool(EQ_SYMBOL_RE.search(f))
    has_neq = bool(NEQ_RE.search(f))
    excluded = _excluded_numbers(f)

    # Explicit two-number ranges first (most specific).
    for rx in RANGE_RES:
        m = rx.search(f)
        if m:
            lo, hi = _tup(m.group(1)), _tup(m.group(2))
            if len(numbers) != 2 or _cmp(lo, hi) > 0:
                return None
            struct = _struct("RANGE", lo, hi, lo not in excluded,
                             hi not in excluded)
            struct["exclusions"] = frozenset(set(excluded) - {lo, hi})
            return struct
    # Series N.x (optionally 'compatible with N.x').
    if series and len(numbers) == 1 \
            and not (has_min or has_max or has_gt or has_lt or has_strong
                     or has_weak or has_neq):
        return _struct("SERIES", major=int(series.group(1)))
    # One lower bound + one upper bound + two numbers form a range
    # ('at least 2 and at most 5'); anything more tangled abstains.
    lower = [has_min, has_gt]
    upper = [has_max, has_lt]
    if sum(lower) == 1 and sum(upper) == 1 and len(numbers) == 2:
        lo, hi = numbers[0], numbers[1]
        if _cmp(lo, hi) > 0:
            return None
        struct = _struct("RANGE", lo, hi,
                         lo_inc=not has_gt and lo not in excluded,
                         hi_inc=not has_lt and hi not in excluded)
        struct["exclusions"] = frozenset(set(excluded) - {lo, hi})
        return struct
    if sum(lower) + sum(upper) > 1:
        return None  # mixed bounds without a range parse
    if has_neq and not sum(lower) and not sum(upper) and not has_strong \
            and not has_weak:
        return _struct("ANY", exclusions=frozenset(excluded or set(
            numbers)))
    # Excluded numbers are holes, not bounds ('version 3 minimum,
    # version 6 exclue' bounds on 3 with a hole at 6). When every
    # number is excluded, the exclusion targets the bound itself
    # ('up to but not including 5' strictens it).
    bounds = [n for n in numbers if n not in excluded] or numbers
    bound_cues = sum(lower) + sum(upper)
    if has_strong:
        # Strong exactness contradicts any bound cue and needs exactly
        # one number ('exactly 2 or newer' abstains).
        if bound_cues or len(bounds) != 1:
            return None
        want = bounds[0]
        if want in excluded:
            return None
        return _struct("EQ", want, want,
                       exclusions=frozenset(excluded))
    if has_weak and not bound_cues:
        # Weak exactness ('must be', '=') yields to bound cues: 'must
        # be 6 or older' is a maximum, 'must be newer than 2' strict.
        if len(bounds) != 1:
            return None
        want = bounds[0]
        if want in excluded:
            return None
        return _struct("EQ", want, want,
                       exclusions=frozenset(excluded))
    if has_min or has_gt:
        if len(bounds) != 1:
            return None
        want = bounds[0]
        inc = has_min and want not in excluded
        struct = _struct("GE" if inc else "GT", want, None)
        struct["exclusions"] = frozenset(set(excluded) - {want})
        return struct
    if has_max or has_lt:
        if len(bounds) != 1:
            return None
        want = bounds[0]
        inc = (not has_lt) and want not in excluded
        struct = _struct("LE" if inc else "LT", None, want)
        struct["exclusions"] = frozenset(set(excluded) - {want})
        return struct
    if not bounds:
        return None
    if len(bounds) == 1:
        return _struct("BARE", bounds[0], bounds[0],
                       exclusions=frozenset(excluded))
    return None  # several numbers, no recognizable relation


def pick_observed(constraint_text: str, observed_text: str,
                norm_op: str | None = None):
    """Observed version tuple, or None when unparseable/vague.

    Operand selection:
    1. One observed number -> it.
    2. Shared subject noun ('schema 3' vs 'port 8080 schema 2' picks
       the schema-tagged 2, never the first number).
    3. Otherwise: directional bounds (GE/GT/LE/LT/RANGE/ANY/SERIES)
       read an untagged headline first number ('v 3, patch 2' -> 3);
       equality checks (BARE/EQ) abstain on ambiguous operands, as
       does a tagged headline ('port 8080, schema 1'), which names a
       subject the constraint never asked about.
    """
    f = fold(observed_text)
    if VAGUE_RE.search(f) or DECIMAL_COMMA_RE.search(f):
        return None
    if SERIES_RE.search(f):
        return None  # imprecise series evidence ('2.x')
    got = extract_tagged(f)
    if not got:
        return None
    if len(got) == 1:
        return got[0][1]
    want_nouns = {n for n, _ in extract_tagged(fold(constraint_text))
                  if n}
    shared = [(n, t) for n, t in got if n in want_nouns]
    if len(shared) == 1:
        return shared[0][1]
    if norm_op not in ("BARE", "EQ") and got[0][0] is None:
        return got[0][1]
    return None


def compare(norm, got) -> tuple[str, str]:
    """(SATISFIED | VIOLATED | UNKNOWN, human-readable explanation)."""
    if norm is None or got is None:
        return ("UNKNOWN", "unparseable version evidence")
    for exc in norm["exclusions"]:
        if _cmp(got, exc) == 0:
            return ("VIOLATED", f"{got} is explicitly excluded")
    op = norm["op"]
    if op == "SERIES":
        if got and got[0] == norm["major"]:
            return ("SATISFIED",
                    f"{got} is in the {norm['major']}.x series")
        return ("VIOLATED", f"{got} is outside {norm['major']}.x")
    if op == "BARE":
        if _cmp(got, norm["low"]) == 0:
            return ("SATISFIED", f"{got} matches stated {norm['low']}")
        return ("UNKNOWN", "bare version differs; comparison unknown")
    if op == "ANY":
        return ("SATISFIED", f"{got} is not excluded")
    if op == "EQ":
        if _cmp(got, norm["low"]) == 0:
            return ("SATISFIED", f"{got} satisfies == {norm['low']}")
        return ("VIOLATED", f"{got} violates == {norm['low']}")
    if op in ("GE", "GT"):
        c = _cmp(got, norm["low"])
        ok = c > 0 or (c == 0 and op == "GE")
        verb = "satisfies" if ok else "violates"
        sym = ">=" if op == "GE" else ">"
        return ("SATISFIED" if ok else "VIOLATED",
                f"{got} {verb} {sym} {norm['low']}")
    if op in ("LE", "LT"):
        c = _cmp(got, norm["high"])
        ok = c < 0 or (c == 0 and op == "LE")
        verb = "satisfies" if ok else "violates"
        sym = "<=" if op == "LE" else "<"
        return ("SATISFIED" if ok else "VIOLATED",
                f"{got} {verb} {sym} {norm['high']}")
    if op == "RANGE":
        clo = _cmp(got, norm["low"])
        chi = _cmp(got, norm["high"])
        ok = (clo > 0 or (clo == 0 and norm["lo_inc"])) and \
            (chi < 0 or (chi == 0 and norm["hi_inc"]))
        span = ( "[" if norm["lo_inc"] else "(") + \
            f"{norm['low']}, {norm['high']}" + \
            ("]" if norm["hi_inc"] else ")")
        verb = "satisfies" if ok else "violates"
        return ("SATISFIED" if ok else "VIOLATED",
                f"{got} {verb} range {span}")
    return ("UNKNOWN", "unparseable version evidence")
