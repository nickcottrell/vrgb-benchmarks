# Retrieval precision @ k

**Claim:** Searching a corpus by hue band ("show me records whose urgency
feels like this one") beats keyword search at finding *semantically similar*
records.

## Method

1. Build a corpus of N paragraphs tagged with VRGB hex values across several
   dimensions (urgency, confidence, register, etc.).
2. For a set of queries:
   - **VRGB retrieval:** rank by `hue_distance + lightness distance` to the
     query hex.
   - **Keyword retrieval:** rank by BM25 / TF-IDF on the underlying text.
3. Compute precision@{1,3,5,10} against a labeled ground-truth "feels
   similar" set.
4. Report both raw precision and the delta.

## Running

```bash
python run.py --seed 42 --out results.json
```

## Status

Stub. Corpus generation can be synthetic (templated paragraphs with known
VRGB tags), so this benchmark can run offline once filled in.
