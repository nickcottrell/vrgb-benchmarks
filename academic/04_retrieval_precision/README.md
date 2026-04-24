# Retrieval precision @ k

**Result:** On 300 records with qualitative signals stored as hex tags
and topical text that does not express those signals, precision@k:

| Method            | p@1   | p@3   | p@5   | p@10  |
|-------------------|-------|-------|-------|-------|
| numeric_oracle    | 1.000 | 1.000 | 0.960 | 0.775 |
| **vrgb**          | **1.000** | **1.000** | **0.960** | **0.773** |
| embeddings_nomic  | 0.000 | 0.033 | 0.025 | 0.023 |
| bm25              | 0.025 | 0.033 | 0.025 | 0.028 |

**Honest reading:** VRGB is a quantized shadow of the numeric oracle
and matches it within 8-bit quantization noise (Δ at p@10 ≈ 0.003).
Embeddings and BM25 both fail on this corpus because the query signal
(urgency, risk, confidence) is intentionally absent from the text —
both methods can only see text-level similarity.

The finding is **not** that VRGB beats embeddings at retrieval in
general. It is that when qualitative signals are stored as hex tags
rather than in prose, VRGB retrieves at oracle precision while adding
compression and readability that numeric values alone don't provide.

## Method

1. Generate 300 synthetic incident reports. Each has:
   - Topical text describing what system did what, on which shift —
     neutral prose that does not express urgency, risk, or confidence.
   - VRGB tags for `urgency`, `risk`, `confidence`, uniform in [0, 1].
2. 40 query records. Relevance = records within ε=0.30 combined
   value-distance.
3. Rank all non-query records four ways:
   - **numeric_oracle**: ascending by raw value-distance (upper bound).
   - **vrgb**: ascending by `Σ |Δlightness|` after decoding each hex tag.
   - **embeddings_nomic**: descending by cosine similarity on
     `nomic-embed-text` embeddings via Ollama.
   - **bm25**: descending by BM25 on text (k1=1.5, b=0.75).
4. Report p@{1, 3, 5, 10} for each method.

Embeddings are computed once and committed at
`fixture/embeddings.json` (300 × 768-dim nomic vectors, ~1MB). The
benchmark uses the fixture on subsequent runs; `--regen` rebuilds it
against a live Ollama.

## Running

```
python run.py --seed 42 --n 300 --queries 40 --out results.json           # use cached embeddings
python run.py --seed 42 --regen --out results.json                        # recompute via Ollama
```

No API keys. BM25 is implemented inline (~30 lines).

## Status

Implemented. Baselines are fair: the oracle is the upper bound;
embeddings and BM25 are real text-based alternatives; VRGB matches the
oracle.
