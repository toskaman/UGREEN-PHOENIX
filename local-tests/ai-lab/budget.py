"""Append-only budget ledger with atomic, concurrency-safe accounting.

Every paid request passes through Ledger.authorize() BEFORE the HTTP
call (worst-case estimate) and Ledger.record() AFTER it (actual usage).
The ledger file is never rewritten or reset; caps bind across restarts.
No secrets are ever written here.
"""

import json
import os
from pathlib import Path

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


class BudgetExceeded(RuntimeError):
    pass


class Ledger:
    def __init__(self, path: Path, cap_usd: float, max_requests: int,
                 pricing: dict):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("", encoding="utf-8")
        self.cap_usd = cap_usd
        self.max_requests = max_requests
        self.pricing = pricing  # model -> (in_per_m, out_per_m)

    def totals(self) -> tuple[float, int]:
        spent, n = 0.0, 0
        with open(self.path, encoding="utf-8") as f:
            _lock(f)
            try:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    e = json.loads(line)
                    if e.get("status") == "ok":
                        spent += float(e.get("cost_usd", 0.0))
                        n += 1
            finally:
                _unlock(f)
        return spent, n

    def estimate_max(self, model: str, prompt_chars: int,
                     max_out: int) -> float:
        """Worst-case cost upper bound. Input tokens overestimated as
        chars/3 (conservative for code/English); output at full max_out
        plus equal reasoning tokens for reasoning models."""
        in_per_m, out_per_m = self.pricing[model]
        in_tok = (prompt_chars // 3) + 1
        out_tok = max_out * 2  # completion + reasoning worst case
        return (in_tok * in_per_m + out_tok * out_per_m) / 1e6

    def authorize(self, model: str, prompt_chars: int, max_out: int) -> float:
        est = self.estimate_max(model, prompt_chars, max_out)
        spent, n = self.totals()
        if n >= self.max_requests:
            raise BudgetExceeded(f"request cap reached ({n})")
        if spent + est > self.cap_usd:
            raise BudgetExceeded(
                f"${spent:.4f} spent + ${est:.4f} est > ${self.cap_usd}")
        return est

    def record(self, entry: dict) -> None:
        entry = dict(entry)
        assert "api_key" not in json.dumps(entry).lower(), \
            "secret leak into ledger refused"
        with open(self.path, "a", encoding="utf-8") as f:
            _lock(f)
            try:
                f.write(json.dumps(entry) + "\n")
                f.flush()
                os.fsync(f.fileno())
            finally:
                _unlock(f)

    @staticmethod
    def actual_cost(model: str, prompt_tok: int, completion_tok: int,
                    pricing: dict) -> float:
        in_per_m, out_per_m = pricing[model]
        return (prompt_tok * in_per_m + completion_tok * out_per_m) / 1e6
