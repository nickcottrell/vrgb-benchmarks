# VRGB Benchmarks

Reproducible benchmarks for VRGB.

## Layout

```
vrgb-benchmarks/
├── lib/                       shared encode/decode/interpolate
├── academic/
│   ├── 01_compression/
│   ├── 02_cross_model_agreement/
│   ├── 03_midpoint_fidelity/
│   ├── 04_retrieval_precision/
│   └── 05_drift_tracking/
├── practical/
│   ├── 01_tone_steering/
│   ├── 02_length_calibration/
│   ├── 03_voice_register/
│   └── 04_genre_blend/
├── tools/regen_results.py
└── RESULTS.md
```

## Running

```
cd academic/01_compression
python run.py --seed 42 --out results.json
```

Every benchmark accepts:
- `--seed INT` (default 42)
- `--out PATH` (default `./results.json`)

Regenerate the top-level table after any run:

```
python tools/regen_results.py
```

## Academic tier

| # | Benchmark | Claim |
|---|-----------|-------|
| 1 | Semantic compression ratio | Fewer bytes per signal than raw text or JSON, exact round-trip |
| 2 | Cross-model coordinate agreement | Low ΔHue variance across vendors on the same prompt |
| 3 | Midpoint interpolation fidelity | Geometric midpoint decodes to a semantic midpoint |
| 4 | Retrieval precision @ k | Hue-band query beats keyword search on similarity queries |
| 5 | Drift tracking under git | Per-day deltas are tighter and more legible than JSON diffs |

## Practical tier

| # | Benchmark | Claim |
|---|-----------|-------|
| 1 | Tone steering | One prompt, three states, three distinct outputs |
| 2 | Length calibration | Word-budget is a continuous dial, not a discrete limit |
| 3 | Voice / register | One prompt, three registers, three distinct outputs |
| 4 | Genre blend | Two anchors, midpoint decodes to a coherent blend |

## Status

v0.2. `academic/01_compression` is the reference implementation. Remaining
benchmarks ship as stubs with the `--seed` / `--out` interface fixed.

## License

MIT. See [LICENSE](LICENSE).

---

— Nick Cottrell · [linkedin.com/in/nickcottrell](https://www.linkedin.com/in/nickcottrell/)
