# Results

*Regenerated: 2026-04-24 21:11 UTC*

Run any benchmark, then `python tools/regen_results.py` from the repo root to
refresh this file.

| Tier | Benchmark | Status | Seed | Headline |
|------|-----------|--------|------|----------|
| academic | `01_compression` | ok | 42 | VRGB = 7.00 bytes/signal, 2.33x smaller than numeric JSON, 0.14x the size of packed uint8 (unreadable) |
| academic | `02_cross_model_agreement` | ok | 42 | mean Δlightness all-3 = 0.395; best pair qwen2.5:7b vs llama3.2:3b = 0.153; outlier counts: {'qwen2.5:7b': 3, 'llama3.2:3b': 4, 'llama3.2:1b': 5} |
| academic | `03_midpoint_fidelity` | ok | 42 | 100.00% of 1680 pairs within ±0.01 (max error 0.003081) |
| academic | `04_retrieval_precision` | ok | 42 | p@5: oracle=0.960, vrgb=0.960, nomic-embed=0.025, bm25=0.025 |
| academic | `05_drift_tracking` | ok | 42 | Silent drift: labels lose 78.5% of events, floats lose 1.5%, vrgb 0%. Float JSON and VRGB tie on capture; label JSON is the outlier. |
| academic | `06_feature_matrix` | ok | 42 | VRGB is the only encoding passing all four properties (compact/readable/interpolable/queryable). Passing set: ['vrgb'] |
| practical | `01_tone_steering` | stub | 42 | stub |
| practical | `02_length_calibration` | stub | 42 | stub |
| practical | `03_voice_register` | stub | 42 | stub |
| practical | `04_genre_blend` | stub | 42 | stub |

See each benchmark's `results.json` for the full metric payload.
