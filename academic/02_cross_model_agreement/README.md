# Cross-model coordinate agreement

**Claim:** If VRGB is a real semantic geometry, different LLMs shown the same
prompt should encode their responses to *similar hues*. High cross-model ΔHue
variance would mean the colorspace is model-specific (bad). Low variance means
it is model-invariant (the point).

## Method

1. Fix a set of semantic prompts, e.g. "rate the urgency of the following
   incident reports" over N paragraphs.
2. Ask each of Opus, Sonnet, Haiku, GPT-4o, Gemini for a value in [0, 1].
3. Encode each response to hex under the `urgency` dimension.
4. For each prompt, compute ΔHue across models (should be ~0 since the
   dimension hue is fixed) and, more interestingly, Δlightness — the
   disagreement budget.
5. Report mean, stdev, and the per-prompt disagreement distribution.

## Running

```bash
python run.py --seed 42 --out results.json
```

Requires API keys in env (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`,
`GEMINI_API_KEY`). Falls back to a recorded fixture if `--fixture` is passed.

## Status

Stub. Interface is fixed; fill in `run.py` with real API calls (or record a
fixture once and check it in for free-to-run CI).
