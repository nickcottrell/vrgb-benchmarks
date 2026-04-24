# Length calibration

> **Status: NOT IMPLEMENTED. No measurements in this benchmark.**
> Do not cite results from this directory. The proposal below describes
> what the benchmark would measure once built.

**Proposal:** Density encoding is a continuous word-budget dial. Same
prompt, three density states → 50 / 200 / 800 words, monotonically.

## Method (planned)

1. Fix a story prompt.
2. Three anchors on the `density` dimension mapping to target word
   counts (50 / 200 / 800).
3. Generate outputs (via local Ollama), measure actual word counts,
   report deviation from target.
4. A smooth budget → word-count curve across the three states is the
   headline.

## Running

Not runnable yet — `run.py` is a stub.

## Status

Stub.
