"""Offline reservation-ledger tests (no network, no spend).

Covers the 10 Phase-5 scenarios with a stub transport + tmp ledgers:
concurrency race, crash windows, timeout ambiguity, mismatch billing,
retries, corruption, reconciliation, and both exhaustion caps.

Usage (from repo root): python local-tests/ai-lab/tests/test_budget.py
"""

import json
import multiprocessing as mp
import sys
import tempfile
import threading
from pathlib import Path

AI_LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AI_LAB))

import budget as budget_mod
import call as call_mod
from providers import vultr

PRICING = {"m": (1.0, 3.0)}  # $1/M in, $3/M out
PASS = 0


def check(name: str, cond: bool, detail: str = ""):
    global PASS
    assert cond, f"FAIL {name}: {detail}"
    PASS += 1
    print(f"  [ok] {name}")


def ok_result(pt=100, ct=50, model="m", finish="stop", sid="srv-1"):
    return {"request_id": sid, "model_requested": "m",
            "model_returned": model, "identity_ok": model == "m",
            "text": "VERDICT: X", "reasoning": "",
            "finish_reason": finish, "native_finish_reason": "",
            "prompt_tokens": pt, "completion_tokens": ct,
            "reasoning_tokens": 0, "cached_tokens": 0, "latency_s": 0.1}


def scripted(outcomes):
    """Stub transport replaying outcomes (dicts or exceptions)."""
    state = {"i": 0}

    def run(model, messages, max_out=0, temperature=0.0,
            reasoning_budget=None, timeout=0):
        out = outcomes[min(state["i"], len(outcomes) - 1)]
        state["i"] += 1
        if isinstance(out, Exception):
            raise out
        return dict(out)

    run.calls = state
    return run


def noop_sleep(_s):
    pass


def fresh(path, cap=10.0, max_req=200, clock=None):
    kw = {"ttl_s": 100, "clock": clock} if clock else {"ttl_s": 100}
    return budget_mod.Ledger(path, cap, max_req, PRICING, **kw)


def line_count(path):
    with open(path, encoding="utf-8") as f:
        return len(f.readlines())


# Scenario 1: concurrent race (threads + processes) -------------------
def _proc_worker(path_str, cap, req_id, queue):
    try:
        led = budget_mod.Ledger(Path(path_str), cap, 100, PRICING)
        led.reserve(req_id, "m", "c", "t", 900, 1100)
        queue.put("admitted")
    except budget_mod.BudgetExceeded:
        queue.put("refused")
    except Exception as exc:  # noqa: BLE001 - report worker faults
        queue.put(f"ERROR {exc}")


def test_concurrent_race():
    with tempfile.TemporaryDirectory() as tmp:
        led = fresh(Path(tmp) / "race.jsonl")
        _, est = led.reserve("probe", "m", "c", "t", 900, 1100)
        cap = est * 2 + est / 2  # room for exactly 2
        p = Path(tmp) / "race.jsonl"
        p.write_text("", encoding="utf-8")
        led = budget_mod.Ledger(p, cap, 100, PRICING)
        results = []
        threads = []
        for i in range(8):
            t = threading.Thread(
                target=lambda i=i: results.append(
                    "admitted" if _try_reserve(led, f"t{i}") else
                    "refused"))
            threads.append(t)
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        check("threads: exactly 2 admitted",
              results.count("admitted") == 2, str(results))
        spent, held, n, corrupt = led.totals()
        check("threads: held == 2*est, none over cap",
              abs(held - 2 * est) < 1e-12 and spent + held <= cap,
              f"held={held} est={est}")
        # Separate processes racing the same file.
        p2 = Path(tmp) / "race2.jsonl"
        p2.write_text("", encoding="utf-8")
        ctx = mp.get_context("spawn")
        queue = ctx.Queue()
        procs = [ctx.Process(target=_proc_worker,
                             args=(str(p2), cap, f"p{i}", queue))
                 for i in range(4)]
        for pr in procs:
            pr.start()
        for pr in procs:
            pr.join(120)
        outs = [queue.get() for _ in procs]
        check("processes: exactly 2 admitted, no errors",
              outs.count("admitted") == 2 and
              not [o for o in outs if o.startswith("ERROR")], str(outs))


def _try_reserve(led, req_id):
    try:
        led.reserve(req_id, "m", "c", "t", 900, 1100)
        return True
    except budget_mod.BudgetExceeded:
        return False


# Scenario 2: crash after reservation ---------------------------------
def test_crash_after_reserve():
    with tempfile.TemporaryDirectory() as tmp:
        now = [1000.0]
        led = fresh(Path(tmp) / "l.jsonl",
                    clock=lambda: now[0])
        _, est = led.reserve("c1", "m", "c", "t", 300, 100)
        # Crash: drop the object, reopen the same file.
        led2 = fresh(Path(tmp) / "l.jsonl", clock=lambda: now[0])
        spent, held, n, _ = led2.totals()
        check("crashed reservation still held pre-TTL",
              held == est and n == 1, f"held={held}")
        now[0] += 10000.0  # past TTL
        rep = led2.reconcile()
        check("stale reservation expires", rep["expired"] == ["c1"],
              str(rep))
        spent, held, n, _ = led2.totals()
        check("expiry frees hold and slot",
              held == 0.0 and n == 0, f"held={held} n={n}")
        # And the req_id becomes reservable again.
        led2.reserve("c1", "m", "c", "t", 300, 100)
        _, held, n, _ = led2.totals()
        check("expired id re-reservable", n == 1 and held == est)


# Scenario 3: crash after response, before record ---------------------
def test_crash_after_response():
    with tempfile.TemporaryDirectory() as tmp:
        led = fresh(Path(tmp) / "l.jsonl")
        led.reserve("c2", "m", "c", "t", 300, 100)
        usage = {"prompt_tok": 100, "completion_tok": 50,
                 "server_id": "srv-9"}
        led.note_attempt("c2", [{"n": 1, "http": 200, **usage}])
        # Crash here: complete() never runs. Reopen.
        led2 = fresh(Path(tmp) / "l.jsonl")
        st = led2.request_state("c2")
        spent, held, n, _ = led2.totals()
        check("crashed flight holds est, not $0",
              st["state"] == "IN_FLIGHT" and held > 0.0,
              f"{st['state']} held={held}")
        actual = budget_mod.Ledger.actual_cost(
            "m", usage["prompt_tok"], usage["completion_tok"], PRICING)
        led2.complete("c2", actual, identity_ok=True,
                      finish_reason="stop", status="ok",
                      server_id=usage["server_id"], attempts=[])
        spent, _, _, _ = led2.totals()
        check("reconciled to exact actual", spent == actual,
              f"spent={spent}")
        # Crash-retry double-complete must not double-count.
        led2.complete("c2", actual, identity_ok=True,
                      finish_reason="stop", status="ok", server_id="srv-9",
                      attempts=[])
        spent2, _, _, _ = led2.totals()
        check("terminal completion idempotent", spent2 == actual)


# Scenario 4: timeout -> unknown charge -------------------------------
def test_timeout_unknown():
    with tempfile.TemporaryDirectory() as tmp:
        led = fresh(Path(tmp) / "l.jsonl")
        transport = scripted([vultr.VultrError("boom", status="timeout")])
        try:
            call_mod.paid_chat("m", [], 100, led, "c3", "c", "t", 300,
                               transport=transport, sleep=noop_sleep)
            check("timeout raises", False)
        except vultr.VultrError:
            check("timeout raises", True)
        st = led.request_state("c3")
        spent, held, n, _ = led.totals()
        check("timeout holds full est, never $0",
              st["state"] == "UNKNOWN_CHARGE" and held == st["est_max_usd"]
              and spent == 0.0, f"{st['state']} held={held}")
        # Same req_id must not silently re-spend.
        try:
            led.reserve("c3", "m", "c", "t", 300, 100)
            check("unknown blocks re-reserve", False)
        except budget_mod.ReservationTerminal as exc:
            check("unknown blocks re-reserve",
                  exc.state == "UNKNOWN_CHARGE")
        # Statement evidence supersedes to exact COMPLETED.
        st_lines = led._scan()[0]["c3"]
        assert st_lines["state"] == "UNKNOWN_CHARGE"
        rep = led.reconcile(statement={})
        check("no-evidence reconcile keeps hold",
              rep["held"] == ["c3"] and rep["matched"] == [], str(rep))


# Scenario 5: billed-but-rejected (mismatch) still spends ------------
def test_mismatch_spends():
    with tempfile.TemporaryDirectory() as tmp:
        led = fresh(Path(tmp) / "l.jsonl")
        transport = scripted([ok_result(model="other-model", sid="srv-x")])
        res = call_mod.paid_chat("m", [], 100, led, "c4", "c", "t", 300,
                                 transport=transport, sleep=noop_sleep)
        check("mismatch flagged", res["identity_ok"] is False)
        expect = budget_mod.Ledger.actual_cost("m", 100, 50, PRICING)
        spent, held, n, _ = led.totals()
        check("mismatch actual counted in spent",
              abs(spent - expect) < 1e-12 and held == 0.0 and n == 1,
              f"spent={spent}")
        st = led.request_state("c4")
        check("mismatch terminal keeps usage + server id",
              st["state"] == "COMPLETED" and st["status"] == "mismatch"
              and st["server_id"] == "srv-x" and len(st["attempts"]) == 1,
              str({k: st.get(k) for k in
                       ("state", "status", "server_id")}))
        # Re-running the same req_id refuses (no silent double-spend).
        try:
            call_mod.paid_chat("m", [], 100, led, "c4", "c", "t", 300,
                               transport=transport, sleep=noop_sleep)
            check("completed id blocks rerun", False)
        except budget_mod.ReservationTerminal as exc:
            check("completed id blocks rerun",
                  exc.state == "COMPLETED")


# Scenario 6: 429 -> 500 -> ok retry chain -----------------------------
def test_retry_chain():
    with tempfile.TemporaryDirectory() as tmp:
        led = fresh(Path(tmp) / "l.jsonl")
        transport = scripted([
            vultr.VultrError("slow down", status=429, retry_after=0),
            vultr.VultrError("bad gateway", status=500),
            ok_result(pt=100, ct=50, sid="srv-r"),
        ])
        res = call_mod.paid_chat("m", [], 100, led, "c5", "c", "t", 300,
                                 transport=transport, sleep=noop_sleep)
        check("retry chain succeeds", res["ledger_state"] == "COMPLETED")
        check("three attempts, one req", len(res["attempts"]) == 3,
              str(res["attempts"]))
        expect = budget_mod.Ledger.actual_cost("m", 100, 50, PRICING)
        spent, _, n, _ = led.totals()
        check("spent == final actual only",
              abs(spent - expect) < 1e-12 and n == 1, f"spent={spent}")
        check("transport called 3x", transport.calls["i"] == 3)
        # 500 retried at most once: 500,500,ok still succeeds (2nd 500
        # is the single allowed retry), but 500x3 then ok must fail.
        transport2 = scripted([vultr.VultrError("e500", status=500)] * 3
                              + [ok_result()])
        try:
            call_mod.paid_chat("m", [], 100, led, "c5b", "c", "t", 300,
                               transport=transport2, sleep=noop_sleep)
            check("triple-500 stops", False)
        except vultr.VultrError:
            check("triple-500 stops", transport2.calls["i"] == 2,
                  f"calls={transport2.calls['i']}")
        st = led.request_state("c5b")
        check("exhausted 500s hold unknown",
              st["state"] == "UNKNOWN_CHARGE", st["state"])


# Scenario 7: torn + garbage lines -------------------------------------
def test_corruption():
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "l.jsonl"
        led = fresh(p, cap=10.0, max_req=1)
        led.reserve("k1", "m", "c", "t", 300, 100)
        led.complete("k1", 0.001, identity_ok=True, finish_reason="stop",
                     status="ok", server_id="s", attempts=[])
        with open(p, "a", encoding="utf-8") as f:
            f.write('{"v": 2, "req_id": "torn", "state": "RES\n')
            f.write("not json at all\n")
        spent, held, n, corrupt = led.totals()
        check("corrupt lines skipped + counted",
              corrupt == 2 and (spent, n) == (0.001, 1),
              f"corrupt={corrupt} spent={spent} n={n}")
        try:
            led.reserve("k2", "m", "c", "t", 300, 100)
            check("caps enforced despite corruption", False)
        except budget_mod.BudgetExceeded:
            check("caps enforced despite corruption", True)


# Scenario 8: reconcile fixture + statement ----------------------------
def test_reconcile():
    with tempfile.TemporaryDirectory() as tmp:
        now = [5000.0]
        led = fresh(Path(tmp) / "l.jsonl", clock=lambda: now[0])
        for rid in ("a1", "a2"):
            led.reserve(rid, "m", "c", "t", 300, 100)
            led.complete(rid, 0.001, identity_ok=True,
                         finish_reason="stop", status="ok",
                         server_id="srv-" + rid, attempts=[])
        led.reserve("u1", "m", "c", "t", 300, 100)
        led.note_attempt("u1", [{"n": 1, "http": "timeout",
                                 "server_id": "srv-u1"}])
        led.fail_unknown("u1", note="timeout")
        led.reserve("old", "m", "c", "t", 300, 100)
        now[0] += 100000.0
        led.reserve("young", "m", "c", "t", 300, 100)
        led.note_attempt("young", [{"n": 1, "http": 200,
                                    "server_id": "srv-y"}])
        before = Path(tmp, "l.jsonl").read_bytes()
        rep = led.reconcile(statement={"srv-u1": 0.0004})
        after = Path(tmp, "l.jsonl").read_bytes()
        check("reconcile sets exact",
              rep["matched"] == ["u1"] and rep["expired"] == ["old"]
              and rep["held"] == ["young"] and rep["gaps"] == [],
              str(rep))
        check("append-only: byte prefix preserved",
              after.startswith(before))
        spent, held, n, _ = led.totals()
        _, est = led.reserve("probe-x", "m", "c", "t", 300, 100)
        led.fail_no_charge("probe-x")
        check("reconciled actual replaces hold",
              abs(spent - (0.002 + 0.0004)) < 1e-12
              and abs(held - est) < 1e-12 and n == 4,
              f"spent={spent} held={held} n={n}")


# Scenario 9: budget exhaustion ----------------------------------------
def test_budget_exhaust():
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "l.jsonl"
        led = fresh(p, cap=0.005, max_req=100)
        n0 = line_count(p)
        try:
            led.reserve("big", "m", "c", "t", 300000, 100000)
            check("usd cap trips", False)
        except budget_mod.BudgetExceeded:
            check("usd cap trips", True)
        check("refusal appends nothing",
              line_count(p) == n0 and led.totals() == (0.0, 0.0, 0, 0))


# Scenario 10: request-limit exhaustion --------------------------------
def test_request_exhaust():
    with tempfile.TemporaryDirectory() as tmp:
        led = fresh(Path(tmp) / "l.jsonl", cap=100.0, max_req=2)
        led.reserve("q1", "m", "c", "t", 300, 100)
        led.reserve("q2", "m", "c", "t", 300, 100)
        try:
            led.reserve("q3", "m", "c", "t", 300, 100)
            check("open reservations count toward max", False)
        except budget_mod.BudgetExceeded:
            check("open reservations count toward max", True)


# Secret guard + legacy fold -------------------------------------------
def test_guards():
    with tempfile.TemporaryDirectory() as tmp:
        led = fresh(Path(tmp) / "l.jsonl")
        try:
            led._append({"v": 2, "req_id": "x", "state": "RESERVED",
                         "api_key": "sk-live-123"})
            check("secret key refused", False)
        except ValueError:
            check("secret key refused", True)
        try:
            led._append({"v": 2, "req_id": "x", "state": "RESERVED",
                         "note": "Authorization: Bearer abcdef"})
            check("bearer marker refused", False)
        except ValueError:
            check("bearer marker refused", True)
        p2 = Path(tmp) / "v1.jsonl"
        p2.write_text('{"status": "ok", "cost_usd": 0.002}\n'
                      '{"status": "error", "cost_usd": 0.0}\n',
                      encoding="utf-8")
        led2 = fresh(p2)
        spent, _, n, _ = led2.totals()
        # ok -> COMPLETED spent; error -> FAILED slot (v2 counts every
        # req_id against MAX_REQUESTS, failed or not).
        check("legacy v1 folds read-only", (spent, n) == (0.002, 2))


if __name__ == "__main__":
    test_concurrent_race()
    test_crash_after_reserve()
    test_crash_after_response()
    test_timeout_unknown()
    test_mismatch_spends()
    test_retry_chain()
    test_corruption()
    test_reconcile()
    test_budget_exhaust()
    test_request_exhaust()
    test_guards()
    print(f"{PASS} budget checks passed, ALL GREEN (offline)")
