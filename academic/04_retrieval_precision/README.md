# Retrieval precision @ k

**Claim:** Hue-band retrieval beats keyword retrieval on similarity
queries over qualitative signals.

## Method

1. Build a corpus of N paragraphs tagged with VRGB values across several
   dimensions (urgency, confidence, register, etc.).
2. For a set of queries:
   - **VRGB retrieval:** rank by hue + lightness distance to the query.
   - **Keyword retrieval:** rank by BM25 / TF-IDF on the underlying text.
3. Compute precision@{1, 3, 5, 10} against a labeled similarity ground-truth.
4. Report both raw precision and the delta.

## Running

```bash
python run.py --seed 42 --out results.json
```

## Status

Stub. Corpus generation can be synthetic (templated paragraphs with known
tags), so this benchmark can run offline once filled in.
