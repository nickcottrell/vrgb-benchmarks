# Semantic compression ratio

**Claim:** For qualitative-judgment records, a VRGB hex is smaller than the
equivalent JSON label dict or natural-language sentence, with exact
round-trip under a known dimension.

## Method

1. Generate a deterministic corpus of N records, each with 5 dimensions
   (urgency, confidence, risk, priority, clarity) drawn uniform in [0, 1].
2. Serialize each record three ways:
   - **raw_text** — "Urgency is very critical. Confidence is moderately
     uncertain. …"
   - **json** — `{"urgency":"very critical","confidence":"moderately
     uncertain",…}` (compact, no whitespace)
   - **vrgb** — concatenated hex, one per dimension, positional
3. Measure mean bytes/record and bytes-per-signal (bytes ÷ dimensions).
4. Report raw sizes and the compression ratios.

Round-trip is exact under the dimension catalog in `lib/vrgb.py` — this
benchmark measures byte cost only, not decode error.

## Running

```bash
python run.py --seed 42 --n 200 --out results.json
```

Flags:
- `--seed INT` (default 42) — deterministic corpus
- `--n INT` (default 200) — records in the corpus
- `--out PATH` (default ./results.json)

No network, no GPUs, no API keys. Runs in <1s.
