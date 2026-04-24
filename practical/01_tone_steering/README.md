# Tone steering

**Claim:** The same prompt, steered through three VRGB states on the
`tone` dimension, produces three distinctly different outputs.

## Method

1. Fix a single prompt: "Write a product launch email for a new SaaS tool."
2. Pick three anchor states on the `tone` dimension — formal / corporate,
   warm / casual, urgent / punchy. Anchor values live in `config.json`.
3. Inject each state as context, collect the three outputs side-by-side.
4. Ship the prompt, the anchor config, and the recorded outputs so any
   reviewer can re-run against a different LLM and compare.

## Running

```
python run.py --seed 42 --out results.json
```

## Status

Stub. Either wire to an LLM SDK of choice or ship a fixture of recorded
outputs.
