"""Deterministic generator for the scale-test corpus (40 filler docs)."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent / "corpus" / "scale"

GUIDE = """# Deployment guide — scale project (synthetic)

## Prerequisites
REQUIRES: app/main.py
REQUIRES: config/app.yaml
REQUIRES: config/missing.yaml
REQUIRES: runtime >= 3.0
REQUIRES: worker >= 2.0
"""

FILLER = """# Working note {i:02d} (synthetic filler)

This document carries no requirements and no version facts. It exists
to measure coverage reporting and timing over a larger corpus.
Reference number: SCALE-{i:04d}.
"""


def main():
    (ROOT / "docs").mkdir(parents=True, exist_ok=True)
    (ROOT / "app").mkdir(parents=True, exist_ok=True)
    (ROOT / "config").mkdir(parents=True, exist_ok=True)
    (ROOT / "docs" / "guide.md").write_text(GUIDE, encoding="utf-8")
    (ROOT / "app" / "main.py").write_text('print("scale (synthetic)")\n',
                                          encoding="utf-8")
    (ROOT / "config" / "app.yaml").write_text(
        "# Application configuration (synthetic)\n"
        "PROVIDES: runtime 3.0.5\n", encoding="utf-8")
    for i in range(40):
        (ROOT / "docs" / f"filler-{i:02d}.md").write_text(
            FILLER.format(i=i), encoding="utf-8")
    print(f"scale corpus written to {ROOT}")


if __name__ == "__main__":
    main()
