#!/usr/bin/env python3
"""Retrieval precision @ k: hue-band vs BM25.

Corpus: N synthetic incident reports. Each record has:
  - topical text (neutral prose; does not expose qualitative signals)
  - VRGB tags for urgency, risk, confidence

Query: pick M records, ask "find records with similar (urgency, risk,
confidence) to this one." Ground truth = records whose combined
value-space distance is under a fixed epsilon.

VRGB ranks by sum of |Δlightness| across the three tagged dimensions.
BM25 ranks by term-frequency score on the text.

The test measures what happens when qualitative signals are stored as
hex tags rather than expressed in the text: VRGB can retrieve, BM25
cannot see the signal.
"""

import argparse
import json
import math
import random
import sys
from collections import Counter
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from lib.vrgb import DIMENSIONS, encode, decode  # noqa: E402


TAGGED_DIMS = ["urgency", "risk", "confidence"]

TOPICS = [
    "database", "cache", "load balancer", "message queue", "auth service",
    "payment pipeline", "search index", "cron job", "webhook dispatcher",
    "feature flag service", "ci pipeline", "container registry",
]

EVENTS = [
    "returned a 500 response", "produced a timeout", "emitted a restart event",
    "logged a warning", "dropped a connection", "consumed unexpected cpu",
    "spiked memory usage", "rejected a health check", "failed to deploy",
    "reported latency above p99 baseline",
]

SHIFTS = ["morning", "afternoon", "evening", "overnight"]


def make_text(rng: random.Random) -> str:
    topic = rng.choice(TOPICS)
    event = rng.choice(EVENTS)
    shift = rng.choice(SHIFTS)
    day = rng.randint(1, 28)
    return (f"The {topic} system {event} during the {shift} on day {day}. "
            f"On-call engineer investigated.")


def build_corpus(n: int, rng: random.Random) -> list[dict]:
    corpus = []
    for i in range(n):
        values = {dim: rng.random() for dim in TAGGED_DIMS}
        tags = {dim: encode(DIMENSIONS[dim], v) for dim, v in values.items()}
        corpus.append({
            "id": i,
            "text": make_text(rng),
            "values": values,
            "tags": tags,
        })
    return corpus


def value_distance(a: dict, b: dict) -> float:
    return sum(abs(a[d] - b[d]) for d in TAGGED_DIMS)


def vrgb_distance(query_tags: dict, doc_tags: dict) -> float:
    """Sum of per-dim lightness differences computed from hex (not values)."""
    total = 0.0
    for dim in TAGGED_DIMS:
        v_q, _ = decode(DIMENSIONS[dim], query_tags[dim])
        v_d, _ = decode(DIMENSIONS[dim], doc_tags[dim])
        total += abs(v_q - v_d)
    return total


class BM25:
    def __init__(self, corpus_texts: list[str], k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.docs = [t.lower().split() for t in corpus_texts]
        self.avgdl = sum(len(d) for d in self.docs) / len(self.docs)
        self.N = len(self.docs)
        self.df: Counter = Counter()
        for doc in self.docs:
            for term in set(doc):
                self.df[term] += 1

    def idf(self, term: str) -> float:
        df = self.df.get(term, 0)
        return math.log((self.N - df + 0.5) / (df + 0.5) + 1.0)

    def score(self, query_tokens: list[str], idx: int) -> float:
        doc = self.docs[idx]
        dl = len(doc)
        tf = Counter(doc)
        s = 0.0
        for term in query_tokens:
            if term not in tf:
                continue
            idf = self.idf(term)
            num = tf[term] * (self.k1 + 1)
            den = tf[term] + self.k1 * (1 - self.b + self.b * dl / self.avgdl)
            s += idf * num / den
        return s


def precision_at_k(ranked_ids: list[int], relevant: set[int], k: int) -> float:
    top_k = ranked_ids[:k]
    if not top_k:
        return 0.0
    return sum(1 for i in top_k if i in relevant) / k


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--n", type=int, default=300, help="corpus size")
    ap.add_argument("--queries", type=int, default=40)
    ap.add_argument("--epsilon", type=float, default=0.30,
                    help="value-space distance threshold for ground-truth relevance")
    ap.add_argument("--out", type=Path, default=Path("results.json"))
    args = ap.parse_args()

    rng = random.Random(args.seed)
    corpus = build_corpus(args.n, rng)
    bm25 = BM25([r["text"] for r in corpus])

    # Pick queries deterministically.
    query_ids = rng.sample(range(args.n), args.queries)

    ks = [1, 3, 5, 10]
    vrgb_at_k = {k: [] for k in ks}
    bm25_at_k = {k: [] for k in ks}
    avg_relevant = []

    for qid in query_ids:
        q = corpus[qid]
        # Ground truth: all OTHER records within epsilon in value-space.
        relevant = {
            r["id"] for r in corpus
            if r["id"] != qid and value_distance(q["values"], r["values"]) < args.epsilon
        }
        avg_relevant.append(len(relevant))

        # VRGB ranking (ascending distance; exclude query itself).
        vrgb_ranked = sorted(
            (r["id"] for r in corpus if r["id"] != qid),
            key=lambda i: vrgb_distance(q["tags"], corpus[i]["tags"]),
        )

        # BM25 ranking (descending score; exclude query itself).
        q_tokens = q["text"].lower().split()
        bm25_ranked = sorted(
            (r["id"] for r in corpus if r["id"] != qid),
            key=lambda i: -bm25.score(q_tokens, i),
        )

        for k in ks:
            vrgb_at_k[k].append(precision_at_k(vrgb_ranked, relevant, k))
            bm25_at_k[k].append(precision_at_k(bm25_ranked, relevant, k))

    metrics = {
        "n_corpus": args.n,
        "n_queries": args.queries,
        "epsilon": args.epsilon,
        "mean_relevant_per_query": round(mean(avg_relevant), 2),
        "vrgb_p_at_k": {k: round(mean(vrgb_at_k[k]), 4) for k in ks},
        "bm25_p_at_k": {k: round(mean(bm25_at_k[k]), 4) for k in ks},
        "delta_p_at_k": {k: round(mean(vrgb_at_k[k]) - mean(bm25_at_k[k]), 4) for k in ks},
    }

    headline = (
        f"VRGB p@5 = {metrics['vrgb_p_at_k'][5]:.3f}, "
        f"BM25 p@5 = {metrics['bm25_p_at_k'][5]:.3f} "
        f"(Δ = {metrics['delta_p_at_k'][5]:+.3f})"
    )

    result = {
        "benchmark": "academic/04_retrieval_precision",
        "status": "ok",
        "seed": args.seed,
        "headline": headline,
        "metrics": metrics,
        "note": ("Text is topical and does not express qualitative signals; "
                 "BM25 has no signal to match on the qualitative query."),
    }
    args.out.write_text(json.dumps(result, indent=2) + "\n")

    print(f"Wrote results to {args.out}")
    print()
    print(f"  corpus        {args.n}")
    print(f"  queries       {args.queries}")
    print(f"  epsilon       {args.epsilon}")
    print(f"  mean relevant {metrics['mean_relevant_per_query']}")
    print()
    print(f"  k     VRGB      BM25      Δ")
    for k in ks:
        print(f"  {k:<4}  {metrics['vrgb_p_at_k'][k]:.4f}    "
              f"{metrics['bm25_p_at_k'][k]:.4f}    "
              f"{metrics['delta_p_at_k'][k]:+.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
