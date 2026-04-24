#!/usr/bin/env python3
"""Walk academic/*/results.json and practical/*/results.json, rebuild RESULTS.md.

Each results.json must be a dict with at least:
    {"benchmark": "<path>", "status": "ok"|"stub", "metrics": {...}}

The summary column is derived per-status: ok -> first scalar metric found,
stub -> "stub".
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TIERS = ("academic", "practical")


def find_results() -> list[Path]:
    paths: list[Path] = []
    for tier in TIERS:
        for p in sorted((ROOT / tier).glob("*/results.json")):
            paths.append(p)
    return paths


def first_scalar_metric(metrics: dict) -> str:
    for k, v in metrics.items():
        if isinstance(v, (int, float)):
            return f"{k} = {v}"
        if isinstance(v, dict):
            for kk, vv in v.items():
                if isinstance(vv, (int, float)):
                    return f"{k}.{kk} = {vv}"
    return "—"


def summarize(result: dict) -> str:
    if result.get("status") == "ok":
        if "headline" in result:
            return str(result["headline"])
        return first_scalar_metric(result.get("metrics", {}))
    return "stub"


def build_table() -> str:
    lines = [
        "| Tier | Benchmark | Status | Seed | Headline |",
        "|------|-----------|--------|------|----------|",
    ]
    for path in find_results():
        tier = path.parent.parent.name
        name = path.parent.name
        try:
            result = json.loads(path.read_text())
        except json.JSONDecodeError:
            continue
        status = result.get("status", "?")
        seed = result.get("seed", "—")
        headline = summarize(result)
        lines.append(f"| {tier} | `{name}` | {status} | {seed} | {headline} |")
    return "\n".join(lines)


def main() -> int:
    table = build_table()
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    body = f"""# Results

*Regenerated: {stamp}*

Run any benchmark, then `python tools/regen_results.py` from the repo root to
refresh this file.

{table}

See each benchmark's `results.json` for the full metric payload.
"""
    (ROOT / "RESULTS.md").write_text(body)
    print(f"Wrote {ROOT / 'RESULTS.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
