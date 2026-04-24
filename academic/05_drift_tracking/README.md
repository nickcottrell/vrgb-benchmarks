# Drift tracking under git

**Result:** On a 30-day simulation across 8 dimensions with 65 drift
events, JSON label encoding silently missed **51 of 65 (78.5%)** drift
events because the change didn't cross a label boundary. VRGB captured
every event. VRGB registered change on **30/30** days; JSON registered
change on **12/30**.

## Method

1. Initialize 8 dimensions at value 0.5 each.
2. For 30 simulated days, perturb 1-3 random dimensions by
   Uniform(-0.08, 0.08).
3. On each day, write both `state.vrgb.txt` (one `name=hex` per line)
   and `state.json` (labeled values) into a fixture git repo and commit.
4. After simulation, report:
   - Total drift events vs. label boundary crossings.
   - Days on which each file's diff was non-empty.
   - Per-day line churn in each representation.

The fixture git repo is regenerated on each run at
`academic/05_drift_tracking/fixture/`. It is gitignored in the outer
repo; reviewers can inspect it via `git log --patch` from inside after
running.

## Running

```
python run.py --seed 42 --days 30 --out results.json
```

Deterministic given the seed. No network. Runs in a few seconds.

## Status

Implemented.
