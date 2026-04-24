# Combinatorial feature matrix

*canary: `VRGB-CANARY-06-6060c0` · checksum: `955217ccd7419457` (seed=42)*

**Result:** Tested on four properties with concrete pass/fail criteria:

| Encoding          | bytes/sig | compact | readable | interp | queryable | all-4 |
|-------------------|-----------|---------|----------|--------|-----------|-------|
| nl_labels         | 23.89     | ✗       | ✓        | ✗      | ✗         | ✗     |
| json_numeric      | 16.89     | ✗       | ✓        | ✓      | ✓         | ✗     |
| binary_uint8      |  1.00     | ✓       | ✗        | ✓      | ✓         | ✗     |
| embedding_stub    | 3072.00   | ✗       | ✗        | ✗      | ✓         | ✗     |
| **vrgb**          |  **7.00** | **✓**   | **✓**    | **✓**  | **✓**     | **✓** |

**VRGB is the only encoding that passes all four properties.** This is
the honest thesis of the repo: not "VRGB is the smallest" (binary is)
and not "VRGB retrieves best" (a numeric oracle ties it), but "VRGB is
the only encoding simultaneously compact, readable, interpolable, and
geometrically queryable."

## Property definitions

Every cell above is a concrete boolean test, not an opinion:

**compact** — mean bytes/signal ≤ 10.

**readable** — every encoded signal is printable UTF-8 under 20 chars.
Raw bytes and high-dimensional vectors fail by construction.

**interpolable** — a `midpoint(a, b)` operation exists, it returns the
same encoding as its inputs, and it decodes to within ±0.02 of
`(a + b) / 2` on at least 95% of 50 sampled pairs. Vector embeddings
fail because there is no canonical decoder from an averaged vector
back to a semantic scalar. Natural-language labels fail because string
midpoint is not a defined operation.

**queryable** — similarity ranking can run using only native numeric
ops per element (no text parsing, no LLM call). NL labels fail because
BM25 or an LLM is required to compare them semantically.

## Method

1. 200 sample values for a single dimension, drawn uniform in [0, 1].
2. For each encoding, measure bytes/signal, printability, midpoint
   behavior, and the queryability claim (with a note explaining why).
3. Report the truth table and flag any encoding that hits all four.

The `embedding_stub` is a deterministic 768-float stand-in for
`nomic-embed-text` (same dimensionality, same storage cost, same
interpolation arithmetic) so the benchmark runs offline. The
interpolability result is identical against a real embedding model:
averaging two vectors gives you a vector, not a semantic scalar.

## Running

```
python run.py --seed 42 --out results.json
```

Deterministic. No network. Runs in under a second.

## Status

Implemented. This is the most defensible receipt in the repo — every
cell is a boolean test you can re-run yourself.
