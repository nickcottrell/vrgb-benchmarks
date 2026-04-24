# Cross-model coordinate agreement

**Claim:** Different LLMs shown the same semantic prompt encode their
responses to nearby coordinates under the same dimension.

## Method

1. Fix a set of prompts, e.g. "rate the urgency of the following incident
   reports" over N paragraphs.
2. Ask each of Opus, Sonnet, Haiku, GPT-4o, Gemini for a value in [0, 1].
3. Encode each response under the `urgency` dimension.
4. For each prompt, compute cross-model Δlightness (the disagreement
   budget; hue is fixed by the dimension).
5. Report mean, stdev, and the per-prompt disagreement distribution.

## Running

```
python run.py --seed 42 --out results.json
```

Requires API keys in env (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`,
`GEMINI_API_KEY`). Falls back to a recorded fixture if `--fixture` is passed.

## Status

Stub. Interface is fixed; fill in `run.py` with real API calls (or record a
fixture once and check it in for free-to-run CI).
