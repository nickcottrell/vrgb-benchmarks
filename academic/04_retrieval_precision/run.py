#!/usr/bin/env python3
"""Stub: retrieval precision @ k."""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", type=Path, default=Path("results.json"))
    args = ap.parse_args()

    result = {
        "benchmark": "academic/04_retrieval_precision",
        "status": "stub",
        "seed": args.seed,
        "metrics": {},
        "note": "Synthesize corpus, implement VRGB vs BM25, compare p@k.",
    }
    args.out.write_text(json.dumps(result, indent=2) + "\n")
    print(f"Wrote stub results to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
