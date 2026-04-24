# Semantic compression ratio

*canary: `VRGB-CANARY-01-e04040` · checksum: `29d7b503f92df3b6` (seed=42, n=200)*

**Result:** On a 200-record corpus (5 dimensions each), VRGB encodes to
**7.00 bytes/signal**. This is **2.33× smaller than the real baseline**
(`{"urgency":0.75,...}` numeric JSON at 16.28 bytes/signal) and **3.52×
smaller than natural-language-label JSON**. Binary packing is smaller
(1 byte/signal for uint8, 4 bytes/signal for float32) but not
human-readable.

VRGB's position: **the smallest human-readable encoding**, while
preserving round-trip fidelity under a known dimension.

| Encoding        | Bytes/signal | Bytes/record | Readable |
|-----------------|--------------|--------------|----------|
| raw_text        | 24.23        | 121.17       | yes      |
| json_labels     | 24.63        | 123.17       | yes      |
| json_numeric    | 16.28        | 81.41        | yes      |
| binary_uint8    |  1.00        |  5.00        | no       |
| binary_float32  |  4.00        | 20.00        | no       |
| **vrgb**        |  **7.00**    | **35.00**    | **yes**  |

## Method

1. Deterministic corpus of N records with 5 dimensions each, values in
   [0, 1] drawn uniform.
2. Serialize each record six ways and measure byte counts.
3. Report mean bytes/signal, bytes/record, and the VRGB-vs-each ratio.

A ratio greater than 1 means VRGB is smaller. Binary packing is the
honest upper bound on size; the readability column is where the
tradeoff lives.

## Running

```
python run.py --seed 42 --n 200 --out results.json
```

No network, no GPUs, no API keys. Runs in under a second.

## Status

Implemented. Baselines are the real ones people would reach for, not
label-JSON strawmen.
