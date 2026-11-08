"""Append-only reservation budget ledger (schema v2).

Every paid request passes through a reservation lifecycle; the ledger
file is never rewritten or reset, so caps bind across restarts:

  RESERVED -> IN_FLIGHT -> COMPLETED | FAILED_NO_CHARGE | UNKNOWN_CHARGE
  RESERVED -> EXPIRED (stale reservation, frees its hold; terminal)

Current state per req_id = the LAST line for that req_id. Terminal
states are final, except reconcile() may supersede UNKNOWN_CHARGE with
COMPLETED when provider-statement evidence arrives.

Accounting (all computed under one file lock):
- spent = SUM(actual_usd over COMPLETED, including identity_ok=false:
  billed-but-rejected calls are real spend)
- held  = SUM(est_max_usd over RESERVED / IN_FLIGHT / UNKNOWN_CHARGE)
- count = distinct req_ids excluding EXPIRED (reservations count as
  requests; only expiry frees a slot)
- corrupt = torn/unparseable lines skipped (never fatal)

reserve() performs check + append in ONE critical section, closing the
authorize/record TOCTOU: concurrent reserver threads/processes cannot
over-admit past either cap.

Error -> ledger mapping (Vultr docs state retry policy but not chat
billing per status; mapping is conservative by design):
- 401 / missing key / 400 / 404 / connection-refused pre-send ->
  FAILED_NO_CHARGE (request refused before generation)
- timeout / 5xx / empty / non-JSON / payload-error-without-usage ->
  UNKNOWN_CHARGE holding the full estimate (server may have billed)
- payload-error WITH usage -> COMPLETED with actual cost (billed)

No secrets are ever written here: entry keys are allowlisted and every
append is scanned unconditionally (never assert-based).
"""

import json
import os
import threading
import time
import uuid
from pathlib import Path

TERMINAL = ("COMPLETED", "FAILED_NO_CHARGE", "UNKNOWN_CHARGE", "EXPIRED")
OPEN = ("RESERVED", "IN_FLIGHT", "UNKNOWN_CHARGE")
SCHEMA_V = 2

ENTRY_KEYS = frozenset({
    "v", "req_id", "state", "model", "case", "tag", "est_max_usd",
    "actual_usd", "identity_ok", "finish_reason", "status", "server_id",
    "attempts", "created_ts", "updated_ts", "note",
})
ATTEMPT_KEYS = frozenset({
    "n", "http", "prompt_tok", "completion_tok", "err", "retry_after",
    "server_id", "no_charge",
})

# Fail-closed secret scan: any of these in an appended line refuses the
# write. Unconditional (works under python -O, unlike assert).
_SECRET_MARKERS = ("api_key", "apikey", "bearer ", "sk-", "token=",
                   "token:", "BEGIN PRIVATE KEY", "AKIA", "eyJ")


class BudgetExceeded(RuntimeError):
    pass


class ReservationTerminal(RuntimeError):
    """reserve() hit an existing terminal state for this req_id."""

    def __init__(self, req_id: str, state: str):
        super().__init__(f"req {req_id} already terminal: {state}")
        self.req_id = req_id
        self.state = state


try:
    import msvcrt

    def _lock(f):
        f.seek(0)
        msvcrt.locking(f.fileno(), msvcrt.LK_LOCK, 1)

    def _unlock(f):
        f.seek(0)
        msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
except ImportError:  # POSIX
    import fcntl

    def _lock(f):
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)

    def _unlock(f):
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)


def _scrubbed(entry: dict) -> dict:
    """Allowlist keys + unconditional secret scan. Raises ValueError."""
    for key in entry:
        if key not in ENTRY_KEYS:
            raise ValueError(f"ledger refuses non-allowlisted key: {key!r}")
    for attempt in entry.get("attempts") or []:
        for key in attempt:
            if key not in ATTEMPT_KEYS:
                raise ValueError(
                    f"ledger refuses non-allowlisted attempt key: {key!r}")
    blob = json.dumps(entry).lower()
    for marker in _SECRET_MARKERS:
        if marker in blob:
            raise ValueError("secret leak into ledger refused")
    return entry


def _fold(lines: list[str]) -> tuple[dict, int]:
    """Fold raw lines -> (req_id -> last entry dict, corrupt count).

    Torn/unparseable lines are counted and skipped, never fatal.
    Schema v1 lines (legacy {status, cost_usd}) map read-only:
    status ok -> COMPLETED spent, anything else -> FAILED_NO_CHARGE.
    """
    state: dict[str, dict] = {}
    corrupt = 0
    for idx, raw in enumerate(lines):
        line = raw.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except (json.JSONDecodeError, ValueError):
            corrupt += 1
            continue
        if not isinstance(entry, dict):
            corrupt += 1
            continue
        if entry.get("v") == SCHEMA_V and entry.get("req_id") \
                and entry.get("state") in TERMINAL + OPEN:
            state[entry["req_id"]] = entry
            continue
        if "status" in entry and "req_id" not in entry:
            # Legacy v1 line; positional pseudo-id keeps the fold
            # deterministic across processes and restarts.
            pseudo = f"v1-{idx}"
            if entry.get("status") == "ok":
                state[pseudo] = {
                    "state": "COMPLETED",
                    "actual_usd": float(entry.get("cost_usd", 0.0))}
            else:
                state[pseudo] = {"state": "FAILED_NO_CHARGE"}
            continue
        corrupt += 1
    return state, corrupt


class Ledger:
    def __init__(self, path: Path, cap_usd: float, max_requests: int,
                 pricing: dict, ttl_s: int = 7200,
                 clock=time.time):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("", encoding="utf-8")
        self.cap_usd = cap_usd
        self.max_requests = max_requests
        self.pricing = pricing  # model -> (in_per_m, out_per_m)
        self.ttl_s = ttl_s
        self._clock = clock
        self._mutex = threading.Lock()  # intra-process guard; the
        # file lock below serializes across processes too.

    # -- read side -------------------------------------------------
    def _scan(self) -> tuple[dict, int]:
        with open(self.path, encoding="utf-8") as f:
            _lock(f)
            try:
                return _fold(f.readlines())
            finally:
                _unlock(f)

    @staticmethod
    def _account(state: dict) -> tuple[float, float, int]:
        spent = held = 0.0
        n = 0
        for entry in state.values():
            st = entry.get("state")
            if st == "EXPIRED":
                continue
            n += 1
            if st == "COMPLETED":
                spent += float(entry.get("actual_usd", 0.0))
            elif st in ("RESERVED", "IN_FLIGHT", "UNKNOWN_CHARGE"):
                held += float(entry.get("est_max_usd", 0.0))
        return spent, held, n

    def totals(self) -> tuple[float, float, int, int]:
        """(spent_usd, held_usd, request_count, corrupt_lines)."""
        with self._mutex:
            state, corrupt = self._scan()
            spent, held, n = self._account(state)
            return spent, held, n, corrupt

    def request_state(self, req_id: str) -> dict | None:
        with self._mutex:
            state, _ = self._scan()
            return state.get(req_id)

    def estimate_max(self, model: str, prompt_chars: int,
                     max_out: int) -> float:
        """Worst-case cost upper bound. Input tokens overestimated as
        chars/3 (conservative for code/English); output at full max_out
        plus equal reasoning tokens for reasoning models."""
        in_per_m, out_per_m = self.pricing[model]
        in_tok = (prompt_chars // 3) + 1
        out_tok = max_out * 2  # completion + reasoning worst case
        return (in_tok * in_per_m + out_tok * out_per_m) / 1e6

    @staticmethod
    def actual_cost(model: str, prompt_tok: int, completion_tok: int,
                    pricing: dict) -> float:
        in_per_m, out_per_m = pricing[model]
        return (prompt_tok * in_per_m + completion_tok * out_per_m) / 1e6

    # -- write side (each op: one critical section) ----------------
    def _append(self, entry: dict) -> None:
        _scrubbed(entry)
        line = json.dumps(entry) + "\n"
        with open(self.path, "a", encoding="utf-8") as f:
            _lock(f)
            try:
                f.write(line)
                f.flush()
                os.fsync(f.fileno())
            finally:
                _unlock(f)

    def _base(self, req_id: str, model: str, case: str, tag: str,
              est: float, attempts: list) -> dict:
        now = self._clock()
        return {"v": SCHEMA_V, "req_id": req_id, "model": model,
                "case": case, "tag": tag, "est_max_usd": est,
                "attempts": attempts, "created_ts": now,
                "updated_ts": now}

    def reserve(self, req_id: str | None, model: str, case: str,
                tag: str, prompt_chars: int, max_out: int) -> tuple[str,
                                                                   float]:
        """Reserve worst-case spend. Check + append under ONE lock hold,
        so concurrent reservers cannot over-admit past either cap.

        Returns (req_id, est). Re-reserving an OPEN req_id adopts it
        (idempotent, no new hold). A terminal req_id raises
        ReservationTerminal; UNKNOWN_CHARGE terminals must go through
        reconcile() first and are never silently superseded here.
        """
        req_id = req_id or f"req-{uuid.uuid4().hex[:12]}"
        est = self.estimate_max(model, prompt_chars, max_out)
        with self._mutex:
            with open(self.path, "a+", encoding="utf-8") as f:
                _lock(f)
                try:
                    f.seek(0)
                    state, _ = _fold(f.readlines())
                    prev = state.get(req_id)
                    if prev is not None:
                        if prev.get("state") not in TERMINAL:
                            return req_id, float(
                                prev.get("est_max_usd", est))
                        if prev.get("state") != "EXPIRED":
                            raise ReservationTerminal(
                                req_id, prev.get("state", "?"))
                        # EXPIRED: fall through to cap-check + fresh
                        # RESERVED, which supersedes via last-wins.
                    spent, held, n = self._account(state)
                    if n >= self.max_requests:
                        raise BudgetExceeded(
                            f"request cap reached ({n})")
                    if spent + held + est > self.cap_usd:
                        raise BudgetExceeded(
                            f"${spent:.4f} spent + ${held:.4f} held + "
                            f"${est:.4f} est > ${self.cap_usd}")
                    entry = self._base(req_id, model, case, tag, est, [])
                    entry["state"] = "RESERVED"
                    _scrubbed(entry)
                    f.write(json.dumps(entry) + "\n")
                    f.flush()
                    os.fsync(f.fileno())
                finally:
                    _unlock(f)
        return req_id, est

    def _transition(self, req_id: str, entry_fn) -> dict:
        """Append a follow-up line for req_id. Scan + append under ONE
        lock hold, so concurrent completions cannot double-append.
        Idempotent on COMPLETED / FAILED_NO_CHARGE / UNKNOWN_CHARGE
        (crash-retry safe). EXPIRED raises ReservationTerminal so the
        caller re-reserves instead of flying without a hold."""
        with self._mutex:
            with open(self.path, "a+", encoding="utf-8") as f:
                _lock(f)
                try:
                    f.seek(0)
                    state, _ = _fold(f.readlines())
                    prev = state.get(req_id)
                    if prev is None:
                        raise KeyError(f"unknown req_id: {req_id}")
                    if prev.get("state") in TERMINAL:
                        if prev.get("state") == "EXPIRED":
                            raise ReservationTerminal(req_id, "EXPIRED")
                        return prev
                    entry = entry_fn(prev)
                    entry["updated_ts"] = self._clock()
                    _scrubbed(entry)
                    f.write(json.dumps(entry) + "\n")
                    f.flush()
                    os.fsync(f.fileno())
                finally:
                    _unlock(f)
            return entry

    def note_attempt(self, req_id: str, attempts: list) -> dict:
        def build(prev):
            entry = self._base(req_id, prev.get("model", ""),
                               prev.get("case", ""), prev.get("tag", ""),
                               float(prev.get("est_max_usd", 0.0)),
                               attempts)
            entry["state"] = "IN_FLIGHT"
            entry["created_ts"] = prev.get("created_ts",
                                           entry["created_ts"])
            return entry
        return self._transition(req_id, build)

    def complete(self, req_id: str, actual_usd: float, *,
                 identity_ok: bool, finish_reason: str, status: str,
                 server_id: str, attempts: list,
                 note: str = "") -> dict:
        def build(prev):
            entry = self._base(req_id, prev.get("model", ""),
                               prev.get("case", ""), prev.get("tag", ""),
                               float(prev.get("est_max_usd", 0.0)),
                               attempts)
            entry.update(state="COMPLETED", actual_usd=actual_usd,
                         identity_ok=identity_ok,
                         finish_reason=finish_reason, status=status,
                         server_id=server_id)
            if note:
                entry["note"] = note
            entry["created_ts"] = prev.get("created_ts",
                                           entry["created_ts"])
            return entry
        return self._transition(req_id, build)

    def fail_no_charge(self, req_id: str, note: str = "") -> dict:
        def build(prev):
            entry = self._base(req_id, prev.get("model", ""),
                               prev.get("case", ""), prev.get("tag", ""),
                               float(prev.get("est_max_usd", 0.0)),
                               list(prev.get("attempts", [])))
            entry.update(state="FAILED_NO_CHARGE", actual_usd=0.0)
            if note:
                entry["note"] = note
            entry["created_ts"] = prev.get("created_ts",
                                           entry["created_ts"])
            return entry
        return self._transition(req_id, build)

    def fail_unknown(self, req_id: str, note: str = "") -> dict:
        """Terminal UNKNOWN_CHARGE: keeps holding the estimate. Only
        reconcile() with provider-statement evidence may supersede it."""

        def build(prev):
            entry = self._base(req_id, prev.get("model", ""),
                               prev.get("case", ""), prev.get("tag", ""),
                               float(prev.get("est_max_usd", 0.0)),
                               list(prev.get("attempts", [])))
            entry["state"] = "UNKNOWN_CHARGE"
            if note:
                entry["note"] = note
            entry["created_ts"] = prev.get("created_ts",
                                           entry["created_ts"])
            return entry
        return self._transition(req_id, build)

    def reconcile(self, statement: dict | None = None) -> dict:
        """Crash recovery + provider-statement reconciliation.

        - RESERVED older than TTL with no later line -> append EXPIRED
          (frees hold and request slot).
        - IN_FLIGHT / UNKNOWN_CHARGE stay held; UNKNOWN_CHARGE becomes
          COMPLETED only with statement evidence
          (statement: server_id -> actual_usd).
        - Torn lines are counted, never fatal.
        Append-only: existing bytes are never mutated.
        """
        statement = statement or {}
        report = {"matched": [], "gaps": [], "expired": [],
                  "held": [], "corrupt": 0}
        with self._mutex:
            state, corrupt = self._scan()
            report["corrupt"] = corrupt
            now = self._clock()
            for req_id, entry in sorted(state.items()):
                st = entry.get("state")
                if st == "RESERVED" and \
                        now - float(entry.get("created_ts", now)) > \
                        self.ttl_s:
                    exp = dict(entry)
                    exp["state"] = "EXPIRED"
                    exp["updated_ts"] = now
                    exp["note"] = "reservation TTL elapsed, no flight"
                    self._append(exp)
                    report["expired"].append(req_id)
                elif st in ("IN_FLIGHT", "UNKNOWN_CHARGE"):
                    sids = [a.get("server_id", "") for a in
                            entry.get("attempts", [])]
                    if entry.get("server_id"):
                        sids.append(entry["server_id"])
                    sid = next((s for s in sids if s in statement), "")
                    if st == "UNKNOWN_CHARGE" and sid in statement:
                        sup = dict(entry)
                        sup.update(
                            state="COMPLETED",
                            actual_usd=float(statement[sid]),
                            status="reconciled",
                            updated_ts=now,
                            note="superseded by provider statement")
                        self._append(sup)
                        report["matched"].append(req_id)
                    else:
                        report["held"].append(req_id)
                        if st == "UNKNOWN_CHARGE" and not any(sids):
                            report["gaps"].append(req_id)
        return report
