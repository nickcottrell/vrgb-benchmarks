# Genre blend

**Claim:** Interpolation isn't a parlor trick. A hex value halfway between
"noir detective" and "cozy mystery" produces prose that *reads* like a
coherent blend, not a malfunction.

## Method

1. Two anchor hexes:
   - `A` — noir detective
   - `B` — cozy mystery
2. Same prompt ("a body in the greenhouse") at 0%, 50%, 100% along A → B,
   where 50% is `lib.vrgb.midpoint(A, B)`.
3. Present three outputs side-by-side.
4. Optional: rater pass for "does 50% feel like a coherent midpoint?"

## Running

```bash
python run.py --seed 42 --out results.json
```

## Status

Stub.
