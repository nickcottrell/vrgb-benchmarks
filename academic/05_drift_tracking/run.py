#!/usr/bin/env python3
"""Drift tracking under git.

Simulate 30 days of parameter drift on 8 dimensions. Each day, write two
parallel representations to a fixture git repo: a VRGB file (hex per line)
and a JSON file (label per key). Commit each day. Then measure:

- Per-day byte churn in each representation (git diff --numstat).
- Number of days where JSON missed the drift because the label boundary
  wasn't crossed (VRGB always records lightness-level changes; JSON labels
  are discrete).

Deterministic given --seed; fully offline.
"""

import argparse
import json
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
    lines = []
    for name in DIM_ORDER:
        lines.append(f"{name}={encode(DIMENSIONS[name], state[name])}")
    return "\n".join(lines) + "\n"


def render_json(state: dict[str, float]) -> str:
    labeled = {name: DIMENSIONS[name].label(state[name]) for name in DIM_ORDER}
    return json.dumps(labeled, indent=2, sort_keys=True) + "\n"


def git(fixture: Path, *args: str) -> str:
    env = {"GIT_AUTHOR_NAME": "drift-sim", "GIT_AUTHOR_EMAIL": "sim@local",
           "GIT_COMMITTER_NAME": "drift-sim", "GIT_COMMITTER_EMAIL": "sim@local"}
    out = subprocess.run(["git", "-C", str(fixture), *args],
                         check=True, capture_output=True, text=True, env={**__import__("os").environ, **env})
    return out.stdout


def simulate(rng: random.Random, days: int, fixture: Path) -> list[dict]:
    # Fresh fixture repo.
    if fixture.exists():
        shutil.rmtree(fixture)
    fixture.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", "-b", "main", str(fixture)], check=True)

    # Initial state: centered.
    state = {name: 0.5 for name in DIM_ORDER}
    events = []

    # Day 0 commit.
    (fixture / "state.vrgb.txt").write_text(render_vrgb(state))
    (fixture / "state.json").write_text(render_json(state))
    git(fixture, "add", "state.vrgb.txt", "state.json")
    git(fixture, "commit", "-q", "-m", "day 0: init")

    for day in range(1, days + 1):
        # Snapshot prior labels to detect boundary crossings.
        prior_labels = {n: DIMENSIONS[n].label(state[n]) for n in DIM_ORDER}
        # Perturb 1-3 dimensions by a small delta.
        k = rng.randint(1, 3)
        touched = rng.sample(DIM_ORDER, k)
        for name in touched:
            delta = rng.uniform(-0.08, 0.08)
            state[name] = max(0.0, min(1.0, state[name] + delta))

        new_labels = {n: DIMENSIONS[n].label(state[n]) for n in DIM_ORDER}
        label_changes = sum(1 for n in touched if prior_labels[n] != new_labels[n])

        (fixture / "state.vrgb.txt").write_text(render_vrgb(state))
        (fixture / "state.json").write_text(render_json(state))
        git(fixture, "add", "state.vrgb.txt", "state.json")
        git(fixture, "commit", "-q", "-m", f"day {day}: drift {k} dims")

        # Measure per-file line churn via numstat.
        numstat = git(fixture, "log", "-1", "--numstat", "--format=").strip().splitlines()
        churn = {"vrgb": (0, 0), "json": (0, 0)}
        for line in numstat:
            added, removed, fname = line.split("\t")
            key = "vrgb" if "vrgb" in fname else "json"
            churn[key] = (int(added), int(removed))

        events.append({
            "day": day,
            "touched_dims": k,
            "label_boundary_crossings": label_changes,
            "vrgb_lines_added": churn["vrgb"][0],
            "vrgb_lines_removed": churn["vrgb"][1],
            "json_lines_added": churn["json"][0],
            "json_lines_removed": churn["json"][1],
        })

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

    days_with_drift = len(events)
    vrgb_days_captured = sum(1 for e in events if e["vrgb_lines_added"] > 0)
    json_days_captured = sum(1 for e in events if e["json_lines_added"] > 0)

    total_drift_dims = sum(e["touched_dims"] for e in events)
    total_label_changes = sum(e["label_boundary_crossings"] for e in events)
    silent_drift_dims = total_drift_dims - total_label_changes

    metrics = {
        "days_simulated": days_with_drift,
        "total_drift_events": total_drift_dims,
        "label_boundary_crossings": total_label_changes,
        "silent_drift_dims": silent_drift_dims,
        "silent_drift_rate": round(silent_drift_dims / total_drift_dims, 4),
        "days_vrgb_captured_change": vrgb_days_captured,
        "days_json_captured_change": json_days_captured,
        "mean_vrgb_lines_changed_per_day": round(
            mean(e["vrgb_lines_added"] + e["vrgb_lines_removed"] for e in events), 3),
        "mean_json_lines_changed_per_day": round(
            mean(e["json_lines_added"] + e["json_lines_removed"] for e in events), 3),
    }

    headline = (
        f"VRGB captured {vrgb_days_captured}/{days_with_drift} drift days, "
        f"JSON captured {json_days_captured}/{days_with_drift} "
        f"({silent_drift_dims}/{total_drift_dims} drift events invisible to JSON)"
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
    for k, v in metrics.items():
        print(f"  {k:42s} {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
