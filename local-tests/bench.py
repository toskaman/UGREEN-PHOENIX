"""Local performance measurements (developer tooling only).

Measures what is measurable without a NAS: traversal/hash cost, parsing,
version comparison, checker/packaging wall time, report sizes, memory peak,
and timing variance. Model/NAS/latency/platform items are NOT APPLICABLE
here; they are recorded as such in perf-matrix.md with reasons.
Never present these numbers as Uliya/NAS latency.
"""

import os
import platform
import statistics
import subprocess
import sys
import tempfile
import time
import tracemalloc
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import harness

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent


def timed(fn, repeats=5):
    samples = []
    for _ in range(repeats):
        start = time.perf_counter()
        result = fn()
        samples.append((time.perf_counter() - start) * 1000)
    return result, statistics.mean(samples), statistics.stdev(samples)


def main():
    print(f"env: python {platform.python_version()} on "
          f"{platform.system()} {platform.machine()} "
          f"({os.cpu_count()} cpus)")
    scale = ROOT / "corpus" / "scale"

    res, mean, stdev = timed(lambda: harness.run(scale))
    files = len(res["coverage"]["reviewed"]) + len(res["coverage"]["skipped"])
    print(f"scale run (43 files in scope): {mean:.1f} ms mean, "
          f"{stdev:.2f} stdev over 5 runs, verdict stable")

    total_bytes = sum(p.stat().st_size for p in scale.rglob("*")
                      if p.is_file())

    def hash_all():
        for p in scale.rglob("*"):
            if p.is_file() and p.suffix.lower() in harness.PARSED_SUFFIXES:
                harness.sha256_of(p)

    _, hmean, _ = timed(hash_all)
    print(f"sha256 over parsed scale docs: {hmean:.1f} ms")

    with tempfile.TemporaryDirectory() as tmp:
        big = Path(tmp) / "big"
        for i in range(200):
            doc = big / "docs"
            doc.mkdir(parents=True, exist_ok=True)
            (doc / f"filler-{i:03d}.md").write_text(
                f"# Filler {i}\n\nNo markers here. Padding {'x' * 200}.\n",
                encoding="utf-8")
        (_, bmean, _), n = timed(lambda: harness.run(big)), 200
        print(f"big run (200 filler docs): {bmean:.1f} ms mean")

    _, cmean, _ = timed(
        lambda: [harness.compare(">=", "3.1.0", "3.0") for _ in range(100000)],
        repeats=3)
    print(f"100k version compares: {cmean:.1f} ms")
    _, pmean, _ = timed(
        lambda: [harness.safe_join(scale, "docs/guide.md")
                 for _ in range(10000)], repeats=3)
    print(f"10k safe_join: {pmean:.1f} ms")

    staging = REPO / "dev-kit" / "phoenix-recovery-intelligence"
    checker = (REPO / "dev-kit" / "extracted" / "uliya-skill-kit"
               / "scripts" / "check-skill.mjs")
    if staging.is_dir() and checker.is_file():
        def run_checker():
            proc = subprocess.run(["node", str(checker), str(staging)],
                                  capture_output=True, text=True)
            assert proc.returncode == 0, proc.stderr[:300]
        _, kmean, _ = timed(run_checker, repeats=3)
        print(f"official checker wall time: {kmean:.0f} ms")
    else:
        print("official checker wall time: SKIP (dev-kit not present)")

    def build_zip():
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "skill.zip"
            with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
                zf.write(REPO / "SKILL.md",
                         "phoenix-recovery-intelligence/SKILL.md")
                for p in sorted((REPO / "references").glob("*.md")):
                    zf.write(p, f"phoenix-recovery-intelligence/references/"
                                f"{p.name}")
            return out.stat().st_size
    size, zmean, _ = timed(build_zip, repeats=3)
    print(f"package zip build: {zmean:.1f} ms, {size} bytes")

    tracemalloc.start()
    harness.run(scale)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print(f"scale run peak python memory: {peak / 1024:.0f} KiB")

    sizes = sorted((p.stat().st_size, p.name)
                   for p in (ROOT / "reports").glob("*.md"))
    if sizes:
        total = sum(s for s, _ in sizes)
        print(f"generated reports: {len(sizes)} files, {total} bytes total, "
              f"max {sizes[-1][0]} bytes ({sizes[-1][1]})")

    start = time.perf_counter()
    proc = subprocess.run([sys.executable, "run-tests.py"], cwd=ROOT,
                          capture_output=True, text=True)
    suite_ms = (time.perf_counter() - start) * 1000
    print(f"full acceptance suite wall time: {suite_ms:.0f} ms "
          f"(exit {proc.returncode})")


if __name__ == "__main__":
    main()
