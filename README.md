# VRGB Benchmarks

Reproducible benchmarks for **VRGB** — the colorspace-encoding protocol that maps semantic parameters to hex tokens so they can be compressed, diffed, interpolated, and retrieved like any other geometric data.

> **Pick your entry point.** Researchers → `academic/`. Builders → `practical/`.

## What is VRGB?

Most systems store qualitative signals (urgency, tone, confidence, register) as strings in JSON blobs. VRGB stores them as coordinates in a colorspace, serialized as a hex string. Because colorspace is *geometric*, you get compression, interpolation, retrieval-by-similarity, and git-diffable drift for free.

A working shim lives in `lib/vrgb.py`. It is the same math every benchmark imports.

## Repo layout

```
vrgb-benchmarks/
├── lib/                       shared encode/decode/interpolate
├── academic/                  proves the math
│   ├── 01_compression/
│   ├── 02_cross_model_agreement/
│   ├── 03_midpoint_fidelity/
│   ├── 04_retrieval_precision/
│   └── 05_drift_tracking/
├── practical/                 proves the utility
│   ├── 01_tone_steering/
│   ├── 02_length_calibration/
│   ├── 03_voice_register/
│   └── 04_genre_blend/
├── tools/regen_results.py     rebuilds RESULTS.md from per-benchmark JSON
└── RESULTS.md                 regenerated table, check before running
```

## Running a benchmark

Every benchmark follows one interface:

```bash
cd academic/01_compression
python run.py --seed 42 --out results.json
```

Flags that every benchmark accepts:
- `--seed INT` — deterministic PRNG seed (default: 42)
- `--out PATH` — where to write `results.json` (default: `./results.json`)

Regenerate the top-level table after any run:

```bash
python tools/regen_results.py
```

## Academic tier

| # | Benchmark | What it proves |
|---|-----------|----------------|
| 1 | Semantic compression ratio | Bytes-per-signal beats raw text and JSON |
| 2 | Cross-model coordinate agreement | ΔHue variance is small across LLM vendors — colorspace is model-invariant |
| 3 | Midpoint interpolation fidelity | Geometric midpoint in hex decodes to a semantic midpoint |
| 4 | Retrieval precision @ k | Hue-band query beats keyword search on "feels similar" queries |
| 5 | Drift tracking under git | Hex deltas over 30 simulated days tell a coherent story vs. JSON blob diffs |

## Practical tier

| # | Demo | What you'll see |
|---|------|-----------------|
| 1 | Tone steering | Same product-launch prompt, three VRGB states, three distinct outputs |
| 2 | Length calibration | Density hex as a word-budget dial (50 / 200 / 800 words) |
| 3 | Voice/register | "Explain recursion" across teacher-to-child, PhD-to-PhD, standup |
| 4 | Genre blend | Noir detective ↔ cozy mystery, interpolated at 0 / 50 / 100% |

## Status

v0.1 — scaffold in place, `academic/01_compression` is the reference
implementation. Other benchmarks ship as stubs with the interface fixed; swap
`run.py` internals to flesh them out. Pull requests welcome once the scaffold
is tagged.

## License

MIT. See [LICENSE](LICENSE).
