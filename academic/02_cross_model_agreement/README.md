# Cross-model coordinate agreement

*canary: `VRGB-CANARY-02-2080e0` · checksum: `3b7ac8f7b2f715c7` (seed=42)*

**Result:** Three local Ollama models (qwen2.5:7b, llama3.2:3b,
llama3.2:1b) rated 12 urgency scenarios on a 0-100 scale. All 36
responses parsed. Because the `urgency` dimension fixes hue, all
cross-model variance lives in lightness and is directly comparable.

| Pair | Mean Δlightness |
|------|-----------------|
| qwen2.5:7b vs llama3.2:3b | **0.153** |
| qwen2.5:7b vs llama3.2:1b | 0.324 |
| llama3.2:3b vs llama3.2:1b | 0.313 |

The two larger models agree tightly (0.15). The 1B model roughly doubles
the disagreement budget and is identified as the outlier on 5 of 12
scenarios via median-distance ranking.

## Method

1. 12 incident scenarios ranging from minor UI bugs to production
   outages.
2. Each model receives the same prompt: "Rate urgency 0-100, return a
   single integer."
3. Generation runs at temperature 0, seed 42, so responses are
   reproducible (and are committed as `fixture/responses.json`).
4. Parse the first integer 0-100 from each response, encode under the
   `urgency` dimension, decode back to lightness.
5. Report all-three Δlightness, pairwise Δlightness, and per-scenario
   outlier identification (model furthest from the median).

Hue variance is zero by construction — same dimension, same hue anchor.
The design property is that **all opinion spread becomes measurable
lightness variance on a comparable scale**.

## Running

```
python run.py --seed 42 --out results.json           # uses cached fixture
python run.py --seed 42 --regen --out results.json   # re-calls Ollama
```

Regeneration requires Ollama reachable at `http://localhost:11434` with
the three models pulled. First run takes ~15 seconds; cached-fixture
runs are instant.

## Status

Implemented. Scaling this to frontier hosted models (Claude, GPT,
Gemini) with API keys is the obvious follow-up and would test
agreement in a higher-capability regime.
