# Tone steering

**Claim:** The same prompt, steered through three VRGB states, produces three
distinctly different outputs. Reader sees "oh, this is a tuning knob."

## Method

1. Fix a single prompt: "Write a product launch email for a new SaaS tool."
2. Pick three VRGB states:
   - `#2040a0` — formal / corporate
   - `#f0a040` — warm / casual
   - `#e04060` — urgent / punchy
3. Inject each state as context, collect the three outputs side-by-side.
4. Ship the prompt + hex values + the three sample outputs so anyone can
   re-run with their own LLM.

## Running

```bash
python run.py --seed 42 --out results.json
```

## Status

Stub. Either wire to an LLM SDK of choice or ship a fixture of pre-recorded
outputs.
