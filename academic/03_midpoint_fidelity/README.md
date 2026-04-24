# Midpoint interpolation fidelity

*canary: `VRGB-CANARY-03-80d080` · checksum: `02cbb05ec0bf5b90` (seed=42)*

**Result:** The geometric midpoint of two encoded values decodes back to
within ±0.003 of the arithmetic midpoint across 1,680 (dimension, a, b)
triples. 100% of pairs land inside ±0.01 tolerance.

## Method

1. Sweep every dimension (`urgency`, `confidence`, `risk`, `priority`,
   `clarity`, `complexity`, `tone`, `register`) with an anchor grid over
   [0, 1] at step 0.05.
2. For each pair (a, b) with a < b: encode both, compute
   `midpoint(A, B)` via `lib.vrgb.midpoint`, decode the result.
3. Compare decoded value to (a + b) / 2. Report mean, max, RMS, and p99
   error, plus the pass rate at ±0.01 tolerance.

The error floor is 8-bit hex quantization (1/256 ≈ 0.004), so ±0.003 is
at the quantization limit. The test measures **encoding fidelity**, not
rater agreement on LLM outputs — that half requires human raters and is
out of scope for a local script.

## Running

```
python run.py --seed 42 --out results.json
```

Runs in under a second with no network.

## Status

Implemented.
