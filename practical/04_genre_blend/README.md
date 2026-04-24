# Genre blend

> **Status: NOT IMPLEMENTED. No measurements in this benchmark.**
> Do not cite results from this directory. The proposal below describes
> what the benchmark would measure once built.

**Proposal:** The midpoint between two anchors (noir detective and
cozy mystery) decodes to prose that reads as a coherent blend.

## Method (planned)

1. Two anchors `A` (noir) and `B` (cozy) on the `atmosphere` dimension.
2. Same prompt at 0%, 50%, 100% along A → B, where 50% is
   `lib.vrgb.midpoint(A, B)`.
3. Present three outputs side-by-side.
4. Optional rater pass on "does 50% read as a coherent midpoint?"

## Running

Not runnable yet — `run.py` is a stub.

## Status

Stub.
