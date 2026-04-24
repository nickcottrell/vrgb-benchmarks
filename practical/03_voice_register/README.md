# Voice / register

**Claim:** VRGB can steer *register* (who the speaker is, not just how they
feel) as cleanly as tone. "Explain recursion" across three registers should
read as three different humans.

## Method

1. Prompt: "Explain recursion."
2. Three VRGB states:
   - `#80c040` — teacher to a child
   - `#404080` — PhD to PhD
   - `#c04020` — standup comedian
3. Generate three outputs, present side-by-side.
4. Optional: a short rubric (vocabulary level, sentence length, analogy use)
   to quantify the register shift.

## Running

```bash
python run.py --seed 42 --out results.json
```

## Status

Stub.
