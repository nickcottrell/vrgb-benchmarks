# Retrieval precision @ k

**Result:** On a 300-record synthetic corpus with qualitative signals
stored as hex tags and topical text that does not express those
signals, VRGB retrieval achieves p@1 = 1.00 / p@5 = 0.96 against a
value-space ground-truth. BM25 on the same corpus performs at
approximately random (p@1 = 0.025 / p@5 = 0.025) because the query
signal is not in the text.

## Method

1. Generate 300 synthetic incident reports. Each record has:
   - **Topical text** describing what system did what, on which shift —
     neutral prose that does not express urgency, risk, or confidence.
   - **VRGB tags** for `urgency`, `risk`, `confidence`, drawn uniform
     in [0, 1] and encoded via `lib.vrgb.encode`.
2. Pick 40 query records. For each query, define relevance as "records
   whose combined value-space distance (sum of `|Δvalue|` across the
   three tagged dimensions) is below ε = 0.30."
3. Rank all non-query records two ways:
   - **VRGB** — ascending by `Σ |Δlightness|` after decoding each tag
     under its dimension.
   - **BM25** — descending by BM25 score using the query's text as the
     query string.
4. Compute precision@{1, 3, 5, 10} for both and report the delta.

The test deliberately chooses a corpus where the query signal is not
in the text. This is the realistic shape for operational metadata —
you tag records with qualitative scores separately, and you want to
retrieve by those scores. BM25 can only match on text tokens; hex tags
are unreachable to it by design.

## Running

```
python run.py --seed 42 --n 300 --queries 40 --out results.json
```

Deterministic. No network. Runs in seconds. BM25 is implemented inline
(~30 lines) with standard k1=1.5, b=0.75.

## Status

Implemented.
