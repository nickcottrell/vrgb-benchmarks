# Tone steering

> **Status: NOT IMPLEMENTED. No measurements in this benchmark.**
> Do not cite results from this directory. The proposal below describes
> what the benchmark would measure once built.

**Proposal:** The same prompt, steered through three VRGB states on the
`tone` dimension, should produce three distinctly different outputs
measurable on simple text features (formality word counts, punctuation
distributions).

## Method (planned)

1. Fix a prompt: "Write a 4-sentence product launch email."
2. Three anchor states on the `tone` dimension — formal / corporate,
   warm / casual, urgent / punchy. Anchor values would live in
   `config.json`.
3. For each state, decode the hex to a scalar and inject into the
   prompt as a formality target ("formality = X/100").
4. Measure formality-word counts and inter-output distinctiveness.
5. Ship prompt, config, and recorded outputs so any reviewer can
   re-run against a different LLM.

## Running

Not runnable yet — `run.py` is a stub that writes
`{"status": "stub"}`.

## Status

Stub. LLM-output-quality claims are harder to pressure-test than the
academic tier; this one is parked until it can be implemented with a
locked generation + measurement harness.
