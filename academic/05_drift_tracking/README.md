# Drift tracking under git

**Claim:** 30 days of parameter edits produce tighter and more legible
diffs when stored as VRGB deltas than as labeled JSON.

## Method

1. Simulate 30 days of changes to a semantic parameter bundle (urgency,
   confidence, risk, priority, ...).
2. On each day, commit two parallel representations to a git repo:
   - `state.vrgb.txt` — one hex per line, one dimension per line.
   - `state.json` — the same values as labeled JSON.
3. Run `git log -p` on both files and measure:
   - Lines changed per day (hex deltas should be tighter).
   - Diff readability — "what changed and in which direction" should be
     legible from hex but not from JSON.
4. Ship the tiny simulated repo in `fixture/` so reviewers can `git log` it
   themselves.

## Running

```bash
python run.py --seed 42 --out results.json
```

## Status

Stub. Good first-PR target for a contributor.
