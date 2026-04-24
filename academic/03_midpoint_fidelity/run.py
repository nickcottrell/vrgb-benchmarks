#!/usr/bin/env python3
"""Midpoint interpolation fidelity.

For every dimension and every pair (a, b) in a grid over [0, 1], encode both,
compute the geometric midpoint, decode it, and compare against (a + b) / 2.
Pure math, no network, deterministic.
"""

import argparse
import json
import sys
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from lib.vrgb import DIMENSIONS, encode, decode, midpoint  # noqa: E402


def sweep(step: float) -> list[dict]:
    """All (dim, a, b) combinations with a < b, stepping by `step`."""
    grid = []
    i = 0.0
    while i <= 1.0 + 1e-9:
        grid.append(round(i, 3))
        i += step
    rows = []
    for dim in DIMENSIONS.values():
        for a in grid:
            for b in grid:
                if a >= b:
                    continue
                ha, hb = encode(dim, a), encode(dim, b)
                hm = midpoint(ha, hb)
                decoded, label = decode(dim, hm)
                expected = (a + b) / 2
                rows.append({
                    "dimension": dim.name,
                    "a": a,
                    "b": b,
                    "expected": round(expected, 6),
                    "decoded": round(decoded, 6),
                    "error": round(abs(decoded - expected), 6),
                    "label": label,
                })
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--step", type=float, default=0.05,
                    help="grid step for anchor values (default 0.05 => 231 pairs/dim)")
    ap.add_argument("--out", type=Path, default=Path("results.json"))
    args = ap.parse_args()

    rows = sweep(args.step)
    errors = [r["error"] for r in rows]

    metrics = {
        "n_dimensions": len(DIMENSIONS),
        "n_pairs_tested": len(rows),
        "grid_step": args.step,
        "error_mean": round(mean(errors), 6),
        "error_max": round(max(errors), 6),
        "error_p99": round(sorted(errors)[int(0.99 * len(errors))], 6),
        "error_rms": round((sum(e * e for e in errors) / len(errors)) ** 0.5, 6),
        "tolerance": 0.01,
        "pairs_within_tolerance": sum(1 for e in errors if e <= 0.01),
        "pass_rate": round(sum(1 for e in errors if e <= 0.01) / len(errors), 4),
    }

    # Worst cases for the audit trail
    worst = sorted(rows, key=lambda r: -r["error"])[:5]

    headline = (
        f"{metrics['pass_rate']*100:.2f}% of {metrics['n_pairs_tested']} pairs "
        f"within ±0.01 (max error {metrics['error_max']})"
    )

    result = {
        "benchmark": "academic/03_midpoint_fidelity",
        "status": "ok",
        "seed": args.seed,
        "headline": headline,
        "metrics": metrics,
        "worst_cases": worst,
    }
    args.out.write_text(json.dumps(result, indent=2) + "\n")

    print(f"Wrote results to {args.out}")
    print()
    print(f"  pairs tested     {metrics['n_pairs_tested']}")
    print(f"  dimensions       {metrics['n_dimensions']}")
    print(f"  error mean       {metrics['error_mean']}")
    print(f"  error max        {metrics['error_max']}")
    print(f"  error RMS        {metrics['error_rms']}")
    print(f"  within ±0.01     {metrics['pass_rate']*100:.2f}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
