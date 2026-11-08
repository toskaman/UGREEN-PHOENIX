"""Descriptive analysis for user-study results. Usage:
python local-tests/user-study/analyze.py results.csv

Prints medians + ranges per condition × task. No p-values, no
generalization beyond the sample. Refuses files with <1 real row.
"""

import csv
import statistics
import sys
from pathlib import Path


def main():
    rows = [r for r in csv.DictReader(
        (ln for ln in Path(sys.argv[1]).read_text(encoding="utf-8")
         .splitlines() if not ln.startswith("#")))]
    if not rows:
        sys.exit("no data rows")
    print("condition | task | n | score median [range] | seconds median [range]")
    for cond in ("manual", "phoenix"):
        for task in ("T1", "T2", "T3", "T4", "T5", "T6"):
            sel = [r for r in rows
                   if r["condition"] == cond and r["task"] == task]
            if not sel:
                continue
            sc = sorted(int(r["score"]) for r in sel)
            se = sorted(int(r["seconds"]) for r in sel)
            print(f"{cond} | {task} | {len(sel)} | "
                  f"{statistics.median(sc)} [{sc[0]}-{sc[-1]}] | "
                  f"{statistics.median(se)} [{se[0]}-{se[-1]}]")


if __name__ == "__main__":
    main()
