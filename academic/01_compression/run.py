#!/usr/bin/env python3
"""Semantic compression ratio.

Encode N qualitative-judgment records three ways (raw text, JSON labels,
VRGB hex) and measure bytes-per-signal. Fully local, fully deterministic.
"""

import argparse
import json
import random
import sys
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from lib.vrgb import DIMENSIONS, encode  # noqa: E402


DIM_NAMES = ["urgency", "confidence", "risk", "priority", "clarity"]


def generate_corpus(n: int, rng: random.Random) -> list[dict[str, float]]:
    return [
        {name: round(rng.random(), 3) for name in DIM_NAMES}
        for _ in range(n)
    ]


def as_raw_text(record: dict[str, float]) -> str:
    parts = []
    for name, val in record.items():
        lbl = DIMENSIONS[name].label(val)
        parts.append(f"{name.capitalize()} is {lbl}.")
    return " ".join(parts)


def as_json(record: dict[str, float]) -> str:
    labeled = {name: DIMENSIONS[name].label(val) for name, val in record.items()}
    return json.dumps(labeled, separators=(",", ":"))


def as_vrgb(record: dict[str, float]) -> str:
    return "".join(encode(DIMENSIONS[name], val) for name, val in record.items())


def bytes_of(s: str) -> int:
    return len(s.encode("utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--out", type=Path, default=Path("results.json"))
    args = ap.parse_args()

    rng = random.Random(args.seed)
    corpus = generate_corpus(args.n, rng)

    raw_sizes = [bytes_of(as_raw_text(r)) for r in corpus]
    json_sizes = [bytes_of(as_json(r)) for r in corpus]
    vrgb_sizes = [bytes_of(as_vrgb(r)) for r in corpus]

    metrics = {
        "n_records": args.n,
        "dimensions_per_record": len(DIM_NAMES),
        "bytes_per_signal": {
            "raw_text": round(mean(raw_sizes) / len(DIM_NAMES), 2),
            "json": round(mean(json_sizes) / len(DIM_NAMES), 2),
            "vrgb": round(mean(vrgb_sizes) / len(DIM_NAMES), 2),
        },
        "bytes_per_record_mean": {
            "raw_text": round(mean(raw_sizes), 2),
            "json": round(mean(json_sizes), 2),
            "vrgb": round(mean(vrgb_sizes), 2),
        },
        "compression_ratio_vs_raw": {
            "json": round(mean(raw_sizes) / mean(json_sizes), 3),
            "vrgb": round(mean(raw_sizes) / mean(vrgb_sizes), 3),
        },
        "compression_ratio_vs_json": {
            "vrgb": round(mean(json_sizes) / mean(vrgb_sizes), 3),
        },
    }

    headline = (
        f"{metrics['compression_ratio_vs_json']['vrgb']:.2f}x vs JSON, "
        f"{metrics['compression_ratio_vs_raw']['vrgb']:.2f}x vs raw text"
    )
    result = {
        "benchmark": "academic/01_compression",
        "status": "ok",
        "seed": args.seed,
        "headline": headline,
        "metrics": metrics,
        "samples": {
            "record": corpus[0],
            "raw_text": as_raw_text(corpus[0]),
            "json": as_json(corpus[0]),
            "vrgb": as_vrgb(corpus[0]),
        },
    }
    args.out.write_text(json.dumps(result, indent=2) + "\n")

    print(f"Wrote results to {args.out}")
    print()
    print("bytes per signal (lower is tighter):")
    for k, v in metrics["bytes_per_signal"].items():
        print(f"  {k:10s} {v:>7.2f}")
    print()
    print("compression ratio (higher = tighter):")
    print(f"  vrgb vs raw_text   {metrics['compression_ratio_vs_raw']['vrgb']:.2f}x")
    print(f"  vrgb vs json        {metrics['compression_ratio_vs_json']['vrgb']:.2f}x")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
