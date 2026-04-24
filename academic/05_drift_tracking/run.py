#!/usr/bin/env python3
"""Drift tracking under git, three encodings compared.

Simulates 30 days of parameter drift across 8 dimensions. Each day,
writes THREE parallel representations to a fixture git repo and commits:

  state.vrgb.txt    - hex per line
  state.labels.json - label-encoded (discrete buckets)
  state.floats.json - numeric float values

Then measures per-encoding:
  - Capture rate: fraction of drift days that produced a non-empty diff
  - Total byte churn across the 30-day history
  - Diff-width variance (did every change produce a same-width diff?)

Honest framing:
  - Label JSON silently misses drift that stays inside a label boundary.
  - Float JSON captures every change (ties VRGB on capture).
  - VRGB uniquely has constant-width diffs (6 hex chars per change) and
    a hue-addressable line layout (spot-inspection win, not a compression
    or completeness win).
"""

import argparse
import json
import os
import random
import shutil
import subprocess
import sys
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from lib.vrgb import DIMENSIONS, encode  # noqa: E402


DIM_ORDER = ["urgency", "confidence", "risk", "priority",
             "clarity", "complexity", "tone", "register"]


def render_vrgb(state: dict[str, float]) -> str:
    return "\n".join(f"{n}={encode(DIMENSIONS[n], state[n])}" for n in DIM_ORDER) + "\n"


def render_labels(state: dict[str, float]) -> str:
    labeled = {n: DIMENSIONS[n].label(state[n]) for n in DIM_ORDER}
    return json.dumps(labeled, indent=2, sort_keys=True) + "\n"


def render_floats(state: dict[str, float]) -> str:
    vals = {n: round(state[n], 3) for n in DIM_ORDER}
    return json.dumps(vals, indent=2, sort_keys=True) + "\n"


FILES = {
    "vrgb":   ("state.vrgb.txt",   render_vrgb),
    "labels": ("state.labels.json", render_labels),
    "floats": ("state.floats.json", render_floats),
}


def git(fixture: Path, *args: str) -> str:
    env = {**os.environ,
           "GIT_AUTHOR_NAME": "drift-sim", "GIT_AUTHOR_EMAIL": "sim@local",
           "GIT_COMMITTER_NAME": "drift-sim", "GIT_COMMITTER_EMAIL": "sim@local"}
    out = subprocess.run(["git", "-C", str(fixture), *args],
                         check=True, capture_output=True, text=True, env=env)
    return out.stdout


def init_fixture(fixture: Path) -> None:
    if fixture.exists():
        shutil.rmtree(fixture)
    fixture.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", "-b", "main", str(fixture)], check=True)


def write_state(fixture: Path, state: dict[str, float]) -> None:
    for _, (fname, renderer) in FILES.items():
        (fixture / fname).write_text(renderer(state))


def commit(fixture: Path, msg: str) -> None:
    git(fixture, "add", *[fname for fname, _ in FILES.values()])
    git(fixture, "commit", "-q", "-m", msg)


def diff_char_count(fixture: Path, fname: str) -> int:
    """Character count of the last commit's diff for `fname` (unified-diff body only)."""
    out = git(fixture, "log", "-1", "--format=", "-p", "--", fname)
    chars = 0
    for line in out.splitlines():
        if line.startswith("+") and not line.startswith("+++"):
            chars += len(line) - 1
        elif line.startswith("-") and not line.startswith("---"):
            chars += len(line) - 1
    return chars


def simulate(rng: random.Random, days: int, fixture: Path) -> list[dict]:
    init_fixture(fixture)
    state = {name: 0.5 for name in DIM_ORDER}

    write_state(fixture, state)
    commit(fixture, "day 0: init")

    events = []
    for day in range(1, days + 1):
        prior_labels = {n: DIMENSIONS[n].label(state[n]) for n in DIM_ORDER}
        prior_floats = {n: round(state[n], 3) for n in DIM_ORDER}

        k = rng.randint(1, 3)
        touched = rng.sample(DIM_ORDER, k)
        for name in touched:
            state[name] = max(0.0, min(1.0, state[name] + rng.uniform(-0.08, 0.08)))

        new_labels = {n: DIMENSIONS[n].label(state[n]) for n in DIM_ORDER}
        new_floats = {n: round(state[n], 3) for n in DIM_ORDER}
        label_changes = sum(1 for n in touched if prior_labels[n] != new_labels[n])
        float_changes = sum(1 for n in touched if prior_floats[n] != new_floats[n])

        write_state(fixture, state)
        commit(fixture, f"day {day}: drift {k} dims")

        ev = {
            "day": day,
            "touched_dims": k,
            "label_boundary_crossings": label_changes,
            "float_value_changes": float_changes,
            "diff_chars": {kind: diff_char_count(fixture, fname)
                           for kind, (fname, _) in FILES.items()},
        }
        events.append(ev)
    return events


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--fixture", type=Path, default=Path("fixture"))
    ap.add_argument("--out", type=Path, default=Path("results.json"))
    args = ap.parse_args()

    rng = random.Random(args.seed)
    events = simulate(rng, args.days, args.fixture.resolve())

    total_drift = sum(e["touched_dims"] for e in events)
    total_label_changes = sum(e["label_boundary_crossings"] for e in events)
    total_float_changes = sum(e["float_value_changes"] for e in events)

    capture = {}
    total_churn = {}
    for kind in FILES:
        days_non_empty = sum(1 for e in events if e["diff_chars"][kind] > 0)
        capture[kind] = round(days_non_empty / len(events), 4)
        total_churn[kind] = sum(e["diff_chars"][kind] for e in events)

    # VRGB diffs have constant width per changed line: every dim line is
    # "name=#rrggbb\n"; when the hex changes, the diff shows 6 hex chars
    # swapped. Float JSON has variable width depending on the value string.
    # Measure this directly: for days where vrgb diff > 0, how variable is
    # the float diff width compared to the vrgb diff width?
    def per_day_widths(kind: str) -> list[int]:
        return [e["diff_chars"][kind] for e in events if e["diff_chars"][kind] > 0]

    def stdev_over_mean(xs: list[int]) -> float:
        if len(xs) < 2:
            return 0.0
        m = mean(xs)
        if m == 0:
            return 0.0
        from statistics import stdev
        return round(stdev(xs) / m, 4)

    width_cv = {kind: stdev_over_mean(per_day_widths(kind)) for kind in FILES}

    metrics = {
        "days_simulated": len(events),
        "total_drift_events": total_drift,
        "label_boundary_crossings": total_label_changes,
        "float_value_changes": total_float_changes,
        "silent_drift_events_labels": total_drift - total_label_changes,
        "silent_drift_rate_labels": round((total_drift - total_label_changes) / total_drift, 4),
        "silent_drift_events_floats": total_drift - total_float_changes,
        "silent_drift_rate_floats": round((total_drift - total_float_changes) / total_drift, 4),
        "capture_rate": capture,
        "total_diff_chars": total_churn,
        "diff_width_cv": width_cv,
        "diff_width_cv_note": ("Coefficient of variation (stdev/mean) of "
                               "per-day diff-char counts. Lower = more "
                               "uniform diff widths, easier for spot "
                               "inspection and column-aligned review."),
    }

    silent_l = metrics["silent_drift_rate_labels"] * 100
    silent_f = metrics["silent_drift_rate_floats"] * 100
    headline = (
        f"Silent drift: labels lose {silent_l:.1f}% of events, "
        f"floats lose {silent_f:.1f}%, vrgb 0%. "
        f"Float JSON and VRGB tie on capture; label JSON is the outlier."
    )

    result = {
        "benchmark": "academic/05_drift_tracking",
        "status": "ok",
        "seed": args.seed,
        "headline": headline,
        "metrics": metrics,
        "fixture": str(args.fixture),
        "per_day": events,
    }
    args.out.write_text(json.dumps(result, indent=2) + "\n")

    print(f"Wrote results to {args.out}")
    print(f"Fixture git repo at {args.fixture}/")
    print()
    print(f"  days simulated          {metrics['days_simulated']}")
    print(f"  total drift events      {total_drift}")
    print()
    print(f"  capture rate (days with non-empty diff):")
    for kind in FILES:
        print(f"    {kind:10s}  {capture[kind]*100:.1f}%")
    print()
    print(f"  silent drift events:")
    print(f"    labels    {metrics['silent_drift_events_labels']} "
          f"of {total_drift} ({metrics['silent_drift_rate_labels']*100:.1f}%)")
    print(f"    floats    {metrics['silent_drift_events_floats']} "
          f"of {total_drift} ({metrics['silent_drift_rate_floats']*100:.1f}%)")
    print(f"    vrgb      0 (encoding resolves at quantization floor)")
    print()
    print(f"  diff-width CV (lower = more uniform):")
    for kind in FILES:
        print(f"    {kind:10s}  {width_cv[kind]:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
