# Genre blend

**Claim:** The midpoint between two anchors — noir detective and cozy
mystery — decodes to prose that reads as a coherent blend.

## Method

1. Two anchors `A` (noir detective) and `B` (cozy mystery) on the `genre`
   dimension.
2. Same prompt ("a body in the greenhouse") at 0%, 50%, 100% along A → B,
   where 50% is `lib.vrgb.midpoint(A, B)`.
3. Present three outputs side-by-side.
4. Optional rater pass on "does 50% read as a coherent midpoint?"

## Running

```bash
python run.py --seed 42 --out results.json
```

## Status

Stub.
