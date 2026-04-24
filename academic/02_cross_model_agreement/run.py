#!/usr/bin/env python3
"""Cross-model coordinate agreement.

Three local Ollama models (qwen2.5:7b, llama3.2:3b, llama3.2:1b) each rate
N incident scenarios for urgency on a 0-100 scale. Each rating is encoded
under the `urgency` dimension; hue is fixed by the dimension, so all
cross-model variance shows up in lightness.

First run calls Ollama and writes `fixture/responses.json`. Subsequent runs
read the fixture deterministically. `--regen` forces a fresh Ollama pass.
"""

import argparse
import hashlib
import json
import re
import sys

CANARY = "VRGB-CANARY-02-2080e0"
from pathlib import Path
from statistics import mean, stdev

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from lib.vrgb import DIMENSIONS, encode, decode  # noqa: E402
from lib.ollama import generate as ollama_generate, available as ollama_available, OllamaError  # noqa: E402


MODELS = ["qwen2.5:7b", "llama3.2:3b", "llama3.2:1b"]


SCENARIOS = [
    "A shared Slack bot posted a duplicate welcome message to one channel.",
    "The auth service has been returning 502s for all login attempts for 6 minutes.",
    "A scheduled report was delivered 30 minutes later than usual.",
    "Customer data from one enterprise tenant is briefly accessible to another tenant.",
    "The search index is an hour behind its normal freshness window.",
    "A deprecated API endpoint logged a warning from an internal service.",
    "The production database primary is unreachable and failover has not triggered.",
    "A feature-flag evaluation returned the default value instead of the rollout bucket for 2% of requests.",
    "The marketing site's footer link to the careers page returns a 404.",
    "Payment authorization is timing out for all customers on the checkout page.",
    "A CI run on the main branch took 12 minutes instead of the usual 8.",
    "An engineer's local IDE integration is hanging when opening the monorepo.",
]


PROMPT_TEMPLATE = (
    "You rate incident severity for an engineering team. "
    "Given the incident below, return ONLY a single integer between 0 and 100, "
    "where 0 means not urgent at all and 100 means drop everything now. "
    "No words. No explanation. Just the integer.\n\n"
    "Incident: {scenario}\n\n"
    "Urgency (0-100):"
)


NUM_RE = re.compile(r"(\d+)")


def parse_rating(text: str) -> int | None:
    """Extract the first integer 0-100 from the model's response."""
    m = NUM_RE.search(text)
    if not m:
        return None
    n = int(m.group(1))
    if not 0 <= n <= 100:
        return None
    return n


def collect_fixture(fixture_path: Path, seed: int) -> dict:
    """Call Ollama for every (model, scenario), return and persist the fixture."""
    responses: dict[str, list[dict]] = {}
    for model in MODELS:
        responses[model] = []
        for idx, scenario in enumerate(SCENARIOS):
            prompt = PROMPT_TEMPLATE.format(scenario=scenario)
            raw = ollama_generate(model, prompt, seed=seed, temperature=0.0, num_predict=16)
            rating = parse_rating(raw)
            responses[model].append({
                "scenario_id": idx,
                "scenario": scenario,
                "raw": raw.strip(),
                "rating": rating,
            })
            print(f"  {model:20s} scenario {idx:2d}: rating={rating} raw={raw.strip()[:40]!r}")
    fixture = {"seed": seed, "models": MODELS, "responses": responses}
    fixture_path.parent.mkdir(parents=True, exist_ok=True)
    fixture_path.write_text(json.dumps(fixture, indent=2) + "\n")
    print(f"\nWrote fixture: {fixture_path}")
    return fixture


def load_fixture(fixture_path: Path) -> dict:
    return json.loads(fixture_path.read_text())


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--fixture", type=Path, default=Path("fixture/responses.json"))
    ap.add_argument("--regen", action="store_true",
                    help="call Ollama and overwrite fixture before scoring")
    ap.add_argument("--out", type=Path, default=Path("results.json"))
    args = ap.parse_args()

    fixture_path = args.fixture
    if args.regen or not fixture_path.exists():
        if not ollama_available():
            print("ERROR: Ollama unreachable at http://localhost:11434", file=sys.stderr)
            print("Start Ollama, or run against an existing fixture.", file=sys.stderr)
            return 2
        print("Calling Ollama (this may take a minute)...")
        try:
            fixture = collect_fixture(fixture_path, args.seed)
        except OllamaError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return 2
    else:
        fixture = load_fixture(fixture_path)
        print(f"Using cached fixture: {fixture_path}")

    # Score: for each scenario, encode each model's rating and measure cross-model lightness spread.
    dim = DIMENSIONS["urgency"]
    per_scenario = []
    parse_failures = 0
    for idx, scenario in enumerate(SCENARIOS):
        ratings = []
        hexes = []
        for model in MODELS:
            entry = fixture["responses"][model][idx]
            rating = entry.get("rating")
            if rating is None:
                parse_failures += 1
                continue
            value = rating / 100.0
            hex_tag = encode(dim, value)
            decoded_value, _ = decode(dim, hex_tag)
            ratings.append({"model": model, "rating": rating, "value": value,
                            "hex": hex_tag, "decoded": decoded_value})
            hexes.append(hex_tag)
        if len(ratings) < 2:
            continue
        decoded_vals = [r["decoded"] for r in ratings]
        delta = max(decoded_vals) - min(decoded_vals)
        sd = stdev(decoded_vals) if len(decoded_vals) > 1 else 0.0
        per_scenario.append({
            "scenario_id": idx,
            "scenario": scenario,
            "ratings": ratings,
            "delta_lightness": round(delta, 4),
            "stdev_lightness": round(sd, 4),
        })

    deltas = [s["delta_lightness"] for s in per_scenario]
    sds = [s["stdev_lightness"] for s in per_scenario]

    # Pairwise cross-model agreement.
    pairwise = {}
    for i, a in enumerate(MODELS):
        for b in MODELS[i + 1:]:
            diffs = []
            for s in per_scenario:
                by_model = {r["model"]: r["decoded"] for r in s["ratings"]}
                if a in by_model and b in by_model:
                    diffs.append(abs(by_model[a] - by_model[b]))
            pairwise[f"{a} vs {b}"] = round(mean(diffs), 4) if diffs else None

    # Outlier identification: for each scenario, which model is furthest from the median?
    outlier_counts: dict[str, int] = {m: 0 for m in MODELS}
    for s in per_scenario:
        vals = [(r["model"], r["decoded"]) for r in s["ratings"]]
        if len(vals) < 3:
            continue
        decoded_vals = sorted(v for _, v in vals)
        median = decoded_vals[len(decoded_vals) // 2]
        furthest = max(vals, key=lambda mv: abs(mv[1] - median))
        outlier_counts[furthest[0]] += 1

    metrics = {
        "n_scenarios": len(SCENARIOS),
        "scored_scenarios": len(per_scenario),
        "parse_failures": parse_failures,
        "models": MODELS,
        "delta_lightness_mean_all": round(mean(deltas), 4) if deltas else None,
        "delta_lightness_max_all": round(max(deltas), 4) if deltas else None,
        "stdev_lightness_mean_all": round(mean(sds), 4) if sds else None,
        "pairwise_mean_delta": pairwise,
        "outlier_count_by_model": outlier_counts,
        "hue_variance": 0.0,
        "hue_variance_note": "Hue is fixed by the dimension; all cross-model variance lives in lightness.",
    }

    best_pair = min(pairwise.items(), key=lambda kv: kv[1])
    headline = (
        f"mean Δlightness all-3 = {metrics['delta_lightness_mean_all']:.3f}; "
        f"best pair {best_pair[0]} = {best_pair[1]:.3f}; "
        f"outlier counts: {outlier_counts}"
    )

    checksum = hashlib.sha256(
        json.dumps(metrics, sort_keys=True, default=str).encode()
    ).hexdigest()[:16]

    result = {
        "benchmark": "academic/02_cross_model_agreement",
        "canary": CANARY,
        "status": "ok",
        "seed": args.seed,
        "headline": headline,
        "verification_checksum": checksum,
        "metrics": metrics,
        "per_scenario": per_scenario,
    }
    args.out.write_text(json.dumps(result, indent=2) + "\n")

    print(f"\nWrote results to {args.out}")
    print()
    print(f"  scenarios scored           {metrics['scored_scenarios']}/{metrics['n_scenarios']}")
    print(f"  parse failures              {parse_failures}")
    print(f"  mean Δlightness all-3       {metrics['delta_lightness_mean_all']}")
    print(f"  max Δlightness all-3        {metrics['delta_lightness_max_all']}")
    print()
    print(f"  pairwise mean Δlightness:")
    for pair, d in pairwise.items():
        print(f"    {pair:45s}  {d}")
    print()
    print(f"  outlier count by model:")
    for m, c in outlier_counts.items():
        print(f"    {m:20s}  {c}")
    print()
    print(f"  canary:                 {CANARY}")
    print(f"  verification_checksum:  {checksum}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
