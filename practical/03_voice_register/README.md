# Voice / register

**Claim:** The `register` dimension steers speaker identity — teacher vs
researcher vs performer — as cleanly as `tone` steers affect.

## Method

1. Prompt: "Explain recursion."
2. Three anchor states on the `register` dimension — teacher-to-child,
   PhD-to-PhD, standup comedian. Anchor values live in `config.json`.
3. Generate three outputs, present side-by-side.
4. Optional rubric (vocabulary level, sentence length, analogy use) to
   quantify the register shift.

## Running

```
python run.py --seed 42 --out results.json
```

## Status

Stub.
