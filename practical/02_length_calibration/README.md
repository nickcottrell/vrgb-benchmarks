# Length calibration

**Claim:** Density hex is a *continuous* word-budget dial, not a discrete
token limit. Same story prompt, three hex values → 50 / 200 / 800 words,
monotonically.

## Method

1. Fix a story prompt: "Tell me about the time the lights went out at the
   summer camp."
2. Pick three density hex values that map to (50, 200, 800) word budgets.
3. Generate outputs, measure actual word counts.
4. Report deviation from target — lower is better. A smooth
   budget → word-count curve is the headline.

## Running

```bash
python run.py --seed 42 --out results.json
```

## Status

Stub. Uses the same density-hex protocol as the book-gen pipeline
(steer_coordinates.py in maestro); the mapping is hex → word-budget.
