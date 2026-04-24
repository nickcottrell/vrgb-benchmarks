# Drift tracking under git

*canary: `VRGB-CANARY-05-b04060` · checksum: `e1620054fc0ec3f2` (seed=42, days=30)*

**Result:** On a 30-day simulation across 8 dimensions (65 drift events
total), the three encodings break down like this:

| Encoding      | Silent drift events | Capture |
|---------------|---------------------|---------|
| label JSON    | 51 of 65 (**78.5%**) | 21.5%   |
| float JSON    |  1 of 65 ( 1.5%)    | 98.5%   |
| **vrgb hex**  |  0 of 65 (  0%)     | 100%    |

**Honest reading:** float JSON and VRGB tie on drift capture
(quantization floor differences between 3-decimal float and 8-bit
lightness are negligible at this scale). The real finding is that
**label encoding silently loses ~78% of small drift** because changes
stay inside a discrete label boundary. Don't store drift-sensitive
state as labels.

VRGB's contribution here is not finer drift capture — it's the same
capture as numeric JSON at roughly half the byte cost plus
dimension-addressable lines (`git log -p -S '#e0'` finds every red-band
change across history).

## Method

1. Initialize 8 dimensions at 0.5 each.
2. For 30 simulated days, perturb 1-3 random dimensions by
   Uniform(-0.08, 0.08).
3. On each day, write three parallel files and commit them:
   - `state.vrgb.txt` — `name=#rrggbb` per line
   - `state.labels.json` — discrete label per key
   - `state.floats.json` — numeric value per key (3-decimal precision)
4. Report per-event silent-drift rate and per-day diff-char churn for
   each encoding.

The fixture git repo regenerates on each run at
`academic/05_drift_tracking/fixture/` and is gitignored in the outer
repo. Reviewers can `git log --patch` inside.

## Running

```
python run.py --seed 42 --days 30 --out results.json
```

Deterministic given the seed. No network. Runs in a few seconds.

## Status

Implemented. Baselines are fair: label JSON vs numeric JSON vs VRGB.
