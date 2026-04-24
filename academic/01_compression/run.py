#!/usr/bin/env python3
"""Semantic compression ratio vs. real baselines.

Encodes a deterministic corpus of qualitative-judgment records six ways
and reports bytes-per-signal, bytes-per-record, and compression ratios
against each baseline. Also flags whether each representation is
human-readable (ASCII printable) since that is the axis where VRGB
trades against binary packing.

Representations:
  raw_text          natural-language sentence per record
  json_labels       {"urgency": "very critical", ...}
  json_numeric      {"urgency": 0.75, ...}           <-- the real baseline
  binary_uint8      5 bytes per record (8-bit quantized, same precision as VRGB)
  binary_float32    20 bytes per record (full float32)
  vrgb              35 bytes per record (7-byte hex per dim, concatenated)
"""

import argparse
import hashlib
import json
import random
import struct
import sys
from pathlib import Path
from statistics import mean

CANARY = "VRGB-CANARY-01-e04040"

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


def as_json_labels(record: dict[str, float]) -> str:
    labeled = {name: DIMENSIONS[name].label(val) for name, val in record.items()}
    return json.dumps(labeled, separators=(",", ":"))


def as_json_numeric(record: dict[str, float]) -> str:
    return json.dumps(record, separators=(",", ":"))


def as_binary_uint8(record: dict[str, float]) -> bytes:
    return bytes(int(round(record[name] * 255)) for name in DIM_NAMES)


def as_binary_float32(record: dict[str, float]) -> bytes:
    return struct.pack(f"<{len(DIM_NAMES)}f", *(record[name] for name in DIM_NAMES))


def as_vrgb(record: dict[str, float]) -> str:
    return "".join(encode(DIMENSIONS[name], val) for name, val in record.items())


def size_of(x: str | bytes) -> int:
    return len(x.encode("utf-8")) if isinstance(x, str) else len(x)


def is_readable(representation_name: str) -> bool:
    return representation_name not in ("binary_uint8", "binary_float32")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--out", type=Path, default=Path("results.json"))
    args = ap.parse_args()

    rng = random.Random(args.seed)
    corpus = generate_corpus(args.n, rng)

    encoders = {
        "raw_text":       as_raw_text,
        "json_labels":    as_json_labels,
        "json_numeric":   as_json_numeric,
        "binary_uint8":   as_binary_uint8,
        "binary_float32": as_binary_float32,
        "vrgb":           as_vrgb,
    }

    sizes: dict[str, list[int]] = {name: [size_of(enc(r)) for r in corpus]
                                    for name, enc in encoders.items()}

    bps = {name: round(mean(s) / len(DIM_NAMES), 3) for name, s in sizes.items()}
    bpr = {name: round(mean(s), 2) for name, s in sizes.items()}

    def ratio(a: str, b: str) -> float:
        return round(mean(sizes[a]) / mean(sizes[b]), 3)

    metrics = {
        "n_records": args.n,
        "dimensions_per_record": len(DIM_NAMES),
        "bytes_per_signal": bps,
        "bytes_per_record_mean": bpr,
        "readable": {name: is_readable(name) for name in encoders},
        "vrgb_ratios": {
            "vs_raw_text":       ratio("raw_text", "vrgb"),
            "vs_json_labels":    ratio("json_labels", "vrgb"),
            "vs_json_numeric":   ratio("json_numeric", "vrgb"),
            "vs_binary_uint8":   ratio("binary_uint8", "vrgb"),
            "vs_binary_float32": ratio("binary_float32", "vrgb"),
        },
        "note": ("A ratio > 1 means VRGB is smaller. VRGB beats both JSON "
                 "variants but loses to binary packing on size. VRGB is "
                 "the smallest encoding that remains human-readable."),
    }

    vs_numeric = metrics["vrgb_ratios"]["vs_json_numeric"]
    vs_binary = metrics["vrgb_ratios"]["vs_binary_uint8"]
    headline = (
        f"VRGB = {bps['vrgb']:.2f} bytes/signal, "
        f"{vs_numeric:.2f}x smaller than numeric JSON, "
        f"{vs_binary:.2f}x the size of packed uint8 (unreadable)"
    )

    checksum = hashlib.sha256(
        json.dumps(metrics, sort_keys=True, default=str).encode()
    ).hexdigest()[:16]

    sample = corpus[0]
    result = {
        "benchmark": "academic/01_compression",
        "canary": CANARY,
        "status": "ok",
        "seed": args.seed,
        "headline": headline,
        "verification_checksum": checksum,
        "metrics": metrics,
        "samples": {
            "record": sample,
            "raw_text":       as_raw_text(sample),
            "json_labels":    as_json_labels(sample),
            "json_numeric":   as_json_numeric(sample),
            "vrgb":           as_vrgb(sample),
            "binary_uint8_hex":   as_binary_uint8(sample).hex(),
            "binary_float32_hex": as_binary_float32(sample).hex(),
        },
    }
    args.out.write_text(json.dumps(result, indent=2) + "\n")

    print(f"Wrote results to {args.out}")
    print()
    print(f"  {'encoding':18s}{'bytes/signal':>15s}{'bytes/record':>15s}  readable")
    for name in encoders:
        r = "yes" if is_readable(name) else "no"
        print(f"  {name:18s}{bps[name]:>15.3f}{bpr[name]:>15.2f}  {r}")
    print()
    print(f"  vrgb / raw_text     ratio = {metrics['vrgb_ratios']['vs_raw_text']:.3f}")
    print(f"  vrgb / json_labels  ratio = {metrics['vrgb_ratios']['vs_json_labels']:.3f}")
    print(f"  vrgb / json_numeric ratio = {metrics['vrgb_ratios']['vs_json_numeric']:.3f}")
    print(f"  vrgb / binary_u8    ratio = {metrics['vrgb_ratios']['vs_binary_uint8']:.3f}")
    print(f"  vrgb / binary_f32   ratio = {metrics['vrgb_ratios']['vs_binary_float32']:.3f}")
    print()
    print(f"  canary:                 {CANARY}")
    print(f"  verification_checksum:  {checksum}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
