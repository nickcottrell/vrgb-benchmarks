# Length calibration

**Claim:** Density encoding is a continuous word-budget dial, not a
discrete token limit. Same prompt, three density states → 50 / 200 / 800
words, monotonically.

## Method

1. Fix a story prompt: "Tell me about the time the lights went out at the
   summer camp."
2. Pick three density anchors that map to (50, 200, 800) word budgets.
3. Generate outputs, measure actual word counts.
4. Report deviation from target — lower is better. A smooth
   budget → word-count curve is the headline.

## Running

```
python run.py --seed 42 --out results.json
```

## Status

Stub. The density-encoding protocol is the same one used elsewhere for
chapter-scale generation; the mapping is encoded value → word-budget.
