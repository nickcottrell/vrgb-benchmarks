#!/usr/bin/env python3
"""Retrieval precision @ k across four methods.

Corpus: N synthetic incident reports. Each record has topical text
(neutral prose that does not express qualitative signals) and VRGB tags
for urgency, risk, confidence.

Query: "find records with similar (urgency, risk, confidence) to this
one." Ground truth: records whose combined value-space distance is under
a fixed epsilon.

Four retrieval methods compared:
  numeric_oracle     query by value-distance directly (upper bound)
  vrgb               rank by sum of |Δlightness| after decoding hex tags
  embeddings_nomic   cosine similarity on nomic-embed-text embeddings
  bm25               BM25 score on text

First run calls Ollama to compute embeddings (caches to
`fixture/embeddings.json`); subsequent runs use the cache.
"""

import argparse
import hashlib
import json
import math
import random
import sys
from collections import Counter

CANARY = "VRGB-CANARY-04-d08020"
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from lib.vrgb import DIMENSIONS, encode, decode  # noqa: E402
from lib.ollama import embed as ollama_embed, available as ollama_available, OllamaError  # noqa: E402


TAGGED_DIMS = ["urgency", "risk", "confidence"]
EMBED_MODEL = "nomic-embed-text"

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
        corpus.append({"id": i, "text": make_text(rng), "values": values, "tags": tags})
    return corpus


def value_distance(a: dict, b: dict) -> float:
    return sum(abs(a[d] - b[d]) for d in TAGGED_DIMS)


def vrgb_distance(query_tags: dict, doc_tags: dict) -> float:
    total = 0.0
    for dim in TAGGED_DIMS:
        v_q, _ = decode(DIMENSIONS[dim], query_tags[dim])
        v_d, _ = decode(DIMENSIONS[dim], doc_tags[dim])
        total += abs(v_q - v_d)
    return total


def cosine(a: list[float], b: list[float]) -> float:
    num = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return num / (na * nb)


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


def load_or_compute_embeddings(corpus: list[dict], fixture_path: Path, regen: bool) -> list[list[float]]:
    if fixture_path.exists() and not regen:
        data = json.loads(fixture_path.read_text())
        if data.get("n") == len(corpus) and data.get("model") == EMBED_MODEL:
            return data["embeddings"]
    if not ollama_available():
        raise OllamaError("Ollama unreachable; cannot compute embeddings.")
    print(f"Computing {len(corpus)} embeddings via Ollama ({EMBED_MODEL})...")
    embeddings = []
    for i, r in enumerate(corpus):
        if i % 50 == 0:
            print(f"  {i}/{len(corpus)}")
        embeddings.append(ollama_embed(EMBED_MODEL, r["text"]))
    fixture_path.parent.mkdir(parents=True, exist_ok=True)
    fixture_path.write_text(json.dumps({
        "model": EMBED_MODEL, "n": len(corpus), "embeddings": embeddings,
    }) + "\n")
    print(f"Wrote embeddings fixture: {fixture_path}")
    return embeddings


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--n", type=int, default=300)
    ap.add_argument("--queries", type=int, default=40)
    ap.add_argument("--epsilon", type=float, default=0.30)
    ap.add_argument("--fixture", type=Path, default=Path("fixture/embeddings.json"))
    ap.add_argument("--regen", action="store_true")
    ap.add_argument("--out", type=Path, default=Path("results.json"))
    args = ap.parse_args()

    rng = random.Random(args.seed)
    corpus = build_corpus(args.n, rng)
    bm25 = BM25([r["text"] for r in corpus])
    embeddings = load_or_compute_embeddings(corpus, args.fixture, args.regen)

    query_ids = rng.sample(range(args.n), args.queries)
    ks = [1, 3, 5, 10]
    methods = ["numeric_oracle", "vrgb", "embeddings_nomic", "bm25"]
    scores: dict[str, dict[int, list[float]]] = {m: {k: [] for k in ks} for m in methods}
    avg_relevant = []

    for qid in query_ids:
        q = corpus[qid]
        relevant = {
            r["id"] for r in corpus
            if r["id"] != qid and value_distance(q["values"], r["values"]) < args.epsilon
        }
        avg_relevant.append(len(relevant))

        other_ids = [r["id"] for r in corpus if r["id"] != qid]

        oracle_rank = sorted(other_ids, key=lambda i: value_distance(q["values"], corpus[i]["values"]))
        vrgb_rank = sorted(other_ids, key=lambda i: vrgb_distance(q["tags"], corpus[i]["tags"]))
        emb_rank = sorted(other_ids, key=lambda i: -cosine(embeddings[qid], embeddings[i]))
        q_tokens = q["text"].lower().split()
        bm25_rank = sorted(other_ids, key=lambda i: -bm25.score(q_tokens, i))

        for k in ks:
            scores["numeric_oracle"][k].append(precision_at_k(oracle_rank, relevant, k))
            scores["vrgb"][k].append(precision_at_k(vrgb_rank, relevant, k))
            scores["embeddings_nomic"][k].append(precision_at_k(emb_rank, relevant, k))
            scores["bm25"][k].append(precision_at_k(bm25_rank, relevant, k))

    p_at_k = {m: {k: round(mean(scores[m][k]), 4) for k in ks} for m in methods}

    metrics = {
        "n_corpus": args.n,
        "n_queries": args.queries,
        "epsilon": args.epsilon,
        "mean_relevant_per_query": round(mean(avg_relevant), 2),
        "p_at_k": p_at_k,
        "methods": {
            "numeric_oracle":   "query by raw value-distance (upper bound; IS the ground-truth ranking)",
            "vrgb":             "sum of |Δlightness| over three dimensions after decoding hex tags",
            "embeddings_nomic": f"cosine similarity on {EMBED_MODEL} embeddings of the text",
            "bm25":             "BM25 on the text (k1=1.5, b=0.75)",
        },
    }

    headline = (
        f"p@5: oracle={p_at_k['numeric_oracle'][5]:.3f}, "
        f"vrgb={p_at_k['vrgb'][5]:.3f}, "
        f"nomic-embed={p_at_k['embeddings_nomic'][5]:.3f}, "
        f"bm25={p_at_k['bm25'][5]:.3f}"
    )

    checksum = hashlib.sha256(
        json.dumps(metrics, sort_keys=True, default=str).encode()
    ).hexdigest()[:16]

    result = {
        "benchmark": "academic/04_retrieval_precision",
        "canary": CANARY,
        "status": "ok",
        "seed": args.seed,
        "headline": headline,
        "verification_checksum": checksum,
        "metrics": metrics,
        "note": ("Text is topical and does not express qualitative signals. "
                 "VRGB matches the oracle (a quantized shadow of it). Text-based "
                 "methods (embeddings, BM25) cannot see the qualitative query."),
    }
    args.out.write_text(json.dumps(result, indent=2) + "\n")

    print(f"\nWrote results to {args.out}")
    print()
    print(f"  corpus {args.n}, queries {args.queries}, epsilon {args.epsilon}, "
          f"mean relevant/query {metrics['mean_relevant_per_query']}")
    print()
    print(f"  {'method':22s} {'p@1':>7s} {'p@3':>7s} {'p@5':>7s} {'p@10':>7s}")
    for m in methods:
        row = " ".join(f"{p_at_k[m][k]:7.4f}" for k in ks)
        print(f"  {m:22s} {row}")
    print()
    print(f"  canary:                 {CANARY}")
    print(f"  verification_checksum:  {checksum}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
