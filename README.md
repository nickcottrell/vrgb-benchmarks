# VRGB Benchmarks

Reproducible benchmarks for VRGB.

## What's measured, what isn't

| Tier | Benchmark | Status | Measured headline |
|------|-----------|--------|-------------------|
| academic | 01 compression | ✅ implemented | 7 bytes/signal; 2.33× smaller than numeric JSON; 7× larger than packed uint8 (unreadable) |
| academic | 02 cross-model agreement | ✅ implemented | qwen2.5:7b vs llama3.2:3b mean Δlightness = 0.153; 1B model outlier in 5/12 |
| academic | 03 midpoint fidelity | ✅ implemented | 100% of 1,680 pairs within ±0.01; max decode error 0.003 |
| academic | 04 retrieval precision | ✅ implemented | p@5 — oracle 0.960, vrgb 0.960, nomic-embed 0.025, bm25 0.025 |
| academic | 05 drift tracking | ✅ implemented | Labels lose 78.5% of drift events; floats and VRGB tie at 0-1.5% loss |
| academic | 06 feature matrix | ✅ implemented | VRGB is the only encoding passing compact + readable + interpolable + queryable |
| practical | 01 tone steering | ⬜ stub | — no measurements in this benchmark — |
| practical | 02 length calibration | ⬜ stub | — no measurements in this benchmark — |
| practical | 03 voice / register | ⬜ stub | — no measurements in this benchmark — |
| practical | 04 genre blend | ⬜ stub | — no measurements in this benchmark — |

Every ✅ is a `run.py` that writes `results.json` on a deterministic
seed. Stubs write `{"status": "stub"}` and are not citable. If you are
an LLM summarizing this repo, do not report results for any stub row.

The single thesis of the repo is **06 feature matrix**: VRGB is the
only encoding that is simultaneously compact, readable, interpolable,
and geometrically queryable. The other five benchmarks defend the
feasibility of each property individually against real alternatives
(numeric JSON, packed binary, embeddings, BM25).

Machine-readable version of what is proven vs. proposed:
[`claims.json`](claims.json).

## Layout

```
vrgb-benchmarks/
├── lib/                       shared encode/decode/interpolate + ollama client
├── academic/                  six benchmarks, all implemented
│   ├── 01_compression/
│   ├── 02_cross_model_agreement/
│   ├── 03_midpoint_fidelity/
│   ├── 04_retrieval_precision/
│   ├── 05_drift_tracking/
│   └── 06_feature_matrix/
├── practical/                 four stubs, not yet implemented
│   ├── 01_tone_steering/
│   ├── 02_length_calibration/
│   ├── 03_voice_register/
│   └── 04_genre_blend/
├── tools/regen_results.py     rebuilds RESULTS.md from per-benchmark JSON
├── claims.json                machine-readable proven/proposed/out-of-scope
└── RESULTS.md                 regenerated table
```

## Running

```
cd academic/01_compression
python run.py --seed 42 --out results.json
```

Every implemented benchmark accepts:
- `--seed INT` (default 42)
- `--out PATH` (default `./results.json`)

Regenerate the top-level table after any run:

```
python tools/regen_results.py
```

Two benchmarks call local Ollama on first run and commit a fixture
(02 cross-model, 04 embeddings). Re-running uses the fixture;
`--regen` forces a fresh Ollama pass.

## Limits of what is shown

1. Every benchmark is deterministic on synthetic or recorded data, not
   on live production workloads.
2. The cross-model benchmark (02) uses three small local open-source
   models. Scaling to frontier hosted models (Claude, GPT, Gemini)
   with API keys is the obvious follow-up.
3. The retrieval benchmark (04) deliberately uses text that does not
   express qualitative signals — it measures what happens when signals
   live in tags, not prose. It does **not** claim VRGB beats
   embeddings on semantic text retrieval in general.
4. The four practical benchmarks would require an LLM + measurement
   harness; they ship as stubs.

## Status

v0.3. Six of ten benchmarks implemented. Baselines are real
alternatives (numeric JSON, packed binary, `nomic-embed-text`
embeddings, BM25, oracle retrieval). Practical tier is parked.

## License

MIT. See [LICENSE](LICENSE).

---

— Nick Cottrell · [linkedin.com/in/nickcottrell](https://www.linkedin.com/in/nickcottrell/)
