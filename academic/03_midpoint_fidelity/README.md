# Midpoint interpolation fidelity

**Claim:** The geometric midpoint of two encoded values, decoded back to
a semantic label, reads as a semantic midpoint.

## Method

1. Pick a dimension (e.g. `urgency`) and two anchor values `A = 0.2`, `B = 0.8`.
2. Encode both, compute `midpoint(A, B)` via `lib.vrgb.midpoint`.
3. Decode the midpoint back to (value, label) under the same dimension.
4. Compare decoded value to expected `0.5`.
5. For the human-coherence half: collect N rater judgments comparing the
   midpoint output to A and B outputs and report agreement with "the middle
   one is in the middle."

## Running

```bash
python run.py --seed 42 --out results.json
```

## Status

Stub (the math half is trivial with `lib.vrgb.midpoint` and can be filled in
without raters; the rater half is out of scope for a local script).
