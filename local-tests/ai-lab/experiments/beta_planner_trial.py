"""Beta planner model trial: v8 vs v9 §7 instructions on 9B + 14B.

Frozen inputs (core-a: 1 NOT_FOUND; core-b: 1 CONFLICTING). Each model
writes §7 under the v8 format, then under the planner format. Scored:
termination, per-line valid cite, no invented subject, planner markers.
Local Ollama only ($0). Writes transcripts to ai-lab/reports/.
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
    },
    "core-b": {
        "evidence": ("- runtime: CONFLICTING (required by "
                     "docs/deployment-guide.md:6) — guide wants 2-or-newer, "
                     "observed 1.9 in config/runtime.yaml:2."),
        "verdict": "DOCUMENTARY BLOCKER IDENTIFIED",
        "subjects": ["runtime"],
        "cites": ["docs/deployment-guide.md:6", "config/runtime.yaml:2"],
    },
}
V8_INSTR = ("Write 'Next steps': one line per item: `- P1: <action> "
            "(evidence: <path:line cite>; authorization: <note>)`. Use only "
            "the evidence above; invent nothing.")
V9_INSTR = ("Write 'Next steps' as an Evidence Gain Planner. Mark the single "
            "first check with [FIRST CHECK]. Every action line: `- P1: "
            "<action> (why: <which blocker/gap it addresses>; evidence: "
            "<path:line cite>; resolved-if: <what observed result counts as "
            "resolved>; authorization: <note>)`. Close with a '- Regardless "
            "of results: <what stays unverified>' line. Use only the "
            "evidence above; invent nothing.")


def score(text, case, planner):
    lines = [ln.strip() for ln in text.splitlines()
             if ln.strip().startswith("- P")]
    cites = CASES[case]["cites"]
    subjects = CASES[case]["subjects"]
    valid_cite = sum(1 for ln in lines if any(c in ln for c in cites))
    grounded = sum(1 for ln in lines if any(s in ln for s in subjects))
    markers = {"first": "[FIRST CHECK]" in text,
               "why": "(why:" in text,
               "resolved_if": "resolved-if:" in text,
               "residual": "- Regardless of results:" in text}
    ok = (len(lines) >= 1 and valid_cite == len(lines)
          and grounded == len(lines))
    if planner:
        ok = ok and all(markers.values())
    return {"action_lines": len(lines), "valid_cite": valid_cite,
            "grounded": grounded, "markers": markers, "pass": ok}


def main():
    out = []
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    for model in MODELS:
        for case, data in CASES.items():
            for variant, instr in (("v8", V8_INSTR), ("v9", V9_INSTR)):
                prompt = (f"Evidence:\n{data['evidence']}\nVerdict: "
                          f"{data['verdict']}\n\n{instr}\nNext steps:")
                r = generate(model, prompt)
                s = score(r["text"], case, planner=(variant == "v9"))
                s.update({"model": model, "case": case, "variant": variant,
                          "finish": r["finish_reason"],
                          "identity_ok": r["identity_ok"],
                          "latency_s": r["latency_s"],
                          "completion_tokens": r["completion_tokens"]})
                if r["finish_reason"] != "stop" or not r["identity_ok"]:
                    s["pass"] = False
                out.append(s)
                print(f"{model.split(':')[0]} | {case} | {variant} | "
                      f"finish={r['finish_reason']} lines={s['action_lines']} "
                      f"cite={s['valid_cite']} markers={s['markers']} "
                      f"PASS={s['pass']} ({r['latency_s']}s)")
                (HERE / "ai-lab" / "reports").mkdir(exist_ok=True)
                (HERE / "ai-lab" / "reports" /
                 f"beta-trial-{stamp}-{model.split(':')[0]}-{case}-{variant}.txt"
                 ).write_text(f"MODEL: {model}\nCASE: {case}\n"
                              f"VARIANT: {variant}\nPROMPT:\n{prompt}\n\n"
                              f"RESPONSE:\n{r['text']}\n",
                              encoding="utf-8")
    n = sum(1 for s in out if s["pass"])
    print(f"\n{n}/{len(out)} trial cells passed")
    (HERE / "ai-lab" / "reports" / f"beta-trial-{stamp}.json").write_text(
        json.dumps(out, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
