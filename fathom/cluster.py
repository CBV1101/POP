from __future__ import annotations

import math
import re
from collections import defaultdict

STOP = {
    "the", "and", "for", "that", "with", "this", "from", "have", "your", "you", "our",
    "are", "was", "were", "but", "not", "can", "could", "would", "should", "just",
    "like", "they", "them", "their", "about", "into", "when", "what", "which", "been",
    "being", "will", "than", "then", "also", "very", "more", "some", "any", "all",
    "out", "get", "got", "has", "had", "did", "does", "don", "its", "it", "we", "i",
    "a", "an", "to", "of", "in", "on", "is", "or", "as", "at", "by", "if",     "be", "because", "required", "requested", "support", "please", "page",
    "team", "still", "until", "after", "before", "ticket", "review", "call",
}

FAMILY = {"configuration", "permissions", "infrastructure-as-code"}


def primary_theme(signal: dict) -> str | None:
    themes = set(signal.get("themes") or [])
    if themes & FAMILY:
        return "integration-family"
    if "documentation" in themes and not themes & {"billing", "search", "identity", "notifications", "export"}:
        return "integration-family"
    if themes:
        return sorted(themes)[0]
    return None


def tokenize(text: str) -> list[str]:
    cleaned = re.sub(r"[^a-z0-9\s]", " ", text.lower())
    tokens = []
    for raw in cleaned.split():
        t = re.sub(r"(ing|ed|es|s)$", "", raw)
        if len(t) > 2 and t not in STOP:
            tokens.append(t)
    return tokens


def tfidf_vectors(docs: list[list[str]]) -> list[dict[str, float]]:
    df: dict[str, int] = defaultdict(int)
    for doc in docs:
        for term in set(doc):
            df[term] += 1
    n = len(docs)
    vectors = []
    for doc in docs:
        tf: dict[str, int] = defaultdict(int)
        for term in doc:
            tf[term] += 1
        vec = {}
        length = max(len(doc), 1)
        for term, count in tf.items():
            idf = math.log((n + 1) / (df[term] + 1)) + 1
            vec[term] = (count / length) * idf
        vectors.append(vec)
    return vectors


def cosine(a: dict[str, float], b: dict[str, float]) -> float:
    na = sum(v * v for v in a.values())
    nb = sum(v * v for v in b.values())
    if not na or not nb:
        return 0.0
    keys, other = (a, b) if len(a) < len(b) else (b, a)
    dot = sum(v * other.get(k, 0.0) for k, v in keys.items())
    return dot / (math.sqrt(na) * math.sqrt(nb))


class UnionFind:
    def __init__(self, n: int):
        self.parent = list(range(n))

    def find(self, i: int) -> int:
        if self.parent[i] != i:
            self.parent[i] = self.find(self.parent[i])
        return self.parent[i]

    def union(self, a: int, b: int) -> None:
        pa, pb = self.find(a), self.find(b)
        if pa != pb:
            self.parent[pb] = pa


def cluster_signals(signals: list[dict]) -> tuple[list[dict], list[str]]:
    n = len(signals)
    if n == 0:
        return [], []
    tokens = [tokenize(s["text"]) for s in signals]
    vectors = tfidf_vectors(tokens)
    uf = UnionFind(n)
    for i in range(n):
        for j in range(i + 1, n):
            theme_i = primary_theme(signals[i])
            theme_j = primary_theme(signals[j])
            same_theme = bool(theme_i and theme_i == theme_j)
            sim = cosine(vectors[i], vectors[j])
            if same_theme and sim >= 0.11:
                uf.union(i, j)
            elif theme_i and theme_j and theme_i != theme_j:
                continue
            elif sim >= 0.42:
                uf.union(i, j)
                uf.union(i, j)
    groups: dict[int, list[str]] = defaultdict(list)
    for i, signal in enumerate(signals):
        groups[uf.find(i)].append(signal["id"])
    clusters = []
    unclustered: list[str] = []
    idx = 1
    for ids in groups.values():
        if len(ids) >= 3:
            clusters.append({"id": f"OPP-{idx:02d}", "signalIds": ids})
            idx += 1
        else:
            unclustered.extend(ids)
    clusters.sort(key=lambda c: len(c["signalIds"]), reverse=True)
    return clusters, unclustered
