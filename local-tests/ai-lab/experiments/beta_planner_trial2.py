"""Beta planner trial round 2: guarded v9 instruction + fixed scorer.

Round 1 (4/8) showed two genuine transfer risks: action over-generation
(14B wrote 4 lines for 1 item) and action drift (version updates,
similar-name searches). Round 2 adds a cardinality guard and a
verification-only allowlist to the v9 instruction, and fixes the scorer
(basename-aware grounding; exact line-count check). Round-1 transcripts
are rescored with the fixed scorer WITHOUT re-inference (disclosed).
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "ai-lab"))

from providers.ollama import generate  # noqa: E402

MODELS = ["qwen2.5-coder-14b-opt:latest", "qwythos-9b-abliterated:optimized"]
CASES = {
    "core-a": {
        "evidence": ("- config/prod-config.yaml: NOT FOUND IN SCOPE "
                     "(required by docs/deployment-guide.md:5) — no "
                     "observed file provides it."),
        "verdict": "DOCUMENTARY BLOCKER IDENTIFIED",
        "subjects": ["config/prod-config.yaml"],
        "cites": ["docs/deployment-guide.md:5"],
        "n_items": 1,
    },
    "core-b": {
        "evidence": ("- runtime: CONFLICTING (required by "
                     "docs/deployment-guide.md:6) — guide wants 2-or-newer, "
                     "observed 1.9 in config/runtime.yaml:2."),
        "verdict": "DOCUMENTARY BLOCKER IDENTIFIED",
        "subjects": ["runtime"],
        "cites": ["docs/deployment-guide.md:6", "config/runtime.yaml:2"],
        "n_items": 1,
    },
}
V9_GUARDED = ("Write 'Next steps' as an Evidence Gain Planner. There is "
              "exactly {n} evidence item above: write exactly {n} action "
              "line(s), one per item, no more. Mark the single first check "
              "with [FIRST CHECK]. Every action line: `- P1: <action> (why: "
              "<which blocker/gap it addresses>; evidence: <path:line "
              "cite>; resolved-if: <what observed result counts as "
              "resolved>; authorization: <note>)`. Actions must be "
              "verification checks only (re-observe, confirm, request "
              "access): never propose modifying files, updating versions, "
              "or searching for similar names; cite exact paths only. Close "
              "with a '- Regardless of results: <what stays unverified>' "
              "line. Use only the evidence above; invent nothing.")
BANNED = ["update the", "upgrade the", "modify ", "similar", "rename",
          "create ", "delete ", "edit "]


def score(text, case):
    lines = [ln.strip() for ln in text.splitlines()
             if ln.strip().startswith("- P")]
    data = CASES[case]
    bases = [s.split("/")[-1] for s in data["subjects"]]
    valid_cite = sum(1 for ln in lines
                     if any(c in ln for c in data["cites"]))
    grounded = sum(1 for ln in lines
                   if any(s in ln or b in ln
                          for s, b in zip(data["subjects"], bases)))
    drift = [w for w in BANNED
             if any(w in ln.lower() for ln in lines)]
    markers = {"first": "[FIRST CHECK]" in text,
               "why": "(why:" in text,
               "resolved_if": "resolved-if:" in text,
               "residual": "- Regardless of results:" in text}
    ok = (len(lines) == data["n_items"]
          and valid_cite == len(lines) and grounded == len(lines)
          and not drift and all(markers.values()))
    return {"action_lines": len(lines), "valid_cite": valid_cite,
            "grounded": grounded, "drift": drift, "markers": markers,
            "pass": ok}


def main():
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = []
    for model in MODELS:
        for case, data in CASES.items():
            prompt = (f"Evidence:\n{data['evidence']}\nVerdict: "
                      f"{data['verdict']}\n\n"
                      f"{V9_GUARDED.format(n=data['n_items'])}\nNext steps:")
            r = generate(model, prompt)
            s = score(r["text"], case)
            s.update({"model": model, "case": case,
                      "finish": r["finish_reason"],
                      "identity_ok": r["identity_ok"],
                      "latency_s": r["latency_s"],
                      "completion_tokens": r["completion_tokens"]})
            if r["finish_reason"] != "stop" or not r["identity_ok"]:
                s["pass"] = False
            out.append(s)
            print(f"{model.split(':')[0]} | {case} | v9-guarded | "
                  f"finish={r['finish_reason']} lines={s['action_lines']} "
                  f"cite={s['valid_cite']} drift={s['drift']} "
                  f"markers={s['markers']} PASS={s['pass']} "
                  f"({r['latency_s']}s)")
            (HERE / "ai-lab" / "reports" /
             f"beta-trial2-{stamp}-{model.split(':')[0]}-{case}.txt"
             ).write_text(f"MODEL: {model}\nCASE: {case}\n"
                          f"PROMPT:\n{prompt}\n\nRESPONSE:\n{r['text']}\n",
                          encoding="utf-8")
    n = sum(1 for s in out if s["pass"])
    print(f"\n{n}/{len(out)} round-2 cells passed")
    (HERE / "ai-lab" / "reports" / f"beta-trial2-{stamp}.json").write_text(
        json.dumps(out, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
