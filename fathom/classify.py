from __future__ import annotations

import re

from .parse import with_normalized_meta
from .themes import match_themes

SOLUTION_PATTERNS = [
    re.compile(r"\bcan you add\b", re.I),
    re.compile(r"\bplease add\b", re.I),
    re.compile(r"\bwe need\b", re.I),
    re.compile(r"\bwould love\b", re.I),
    re.compile(r"\bfeature request\b", re.I),
    re.compile(r"\bintegrate with\b", re.I),
    re.compile(r"\badd (a |an |the )?", re.I),
    re.compile(r"\bbuild (a |an )?", re.I),
    re.compile(r"\bsupport for\b", re.I),
    re.compile(r"\bterraform\b", re.I),
    re.compile(r"\bpulumi\b", re.I),
    re.compile(r"\bshould (just )?have\b", re.I),
    re.compile(r"\bwhy don't you\b", re.I),
    re.compile(r"\bnative integration\b", re.I),
]

PROBLEM_PATTERNS = [
    re.compile(r"\bcouldn['’]t\b", re.I),
    re.compile(r"\bcan['’]t\b", re.I),
    re.compile(r"\bcannot\b", re.I),
    re.compile(r"\bfailed\b", re.I),
    re.compile(r"\bblocked\b", re.I),
    re.compile(r"\bconfus", re.I),
    re.compile(r"\btook\b", re.I),
    re.compile(r"\bweeks?\b", re.I),
    re.compile(r"\bdocs say\b", re.I),
    re.compile(r"\bdoesn['’]t (work|match|say)\b", re.I),
    re.compile(r"\bunable\b", re.I),
    re.compile(r"\bfrustrating\b", re.I),
    re.compile(r"\bpainful\b", re.I),
    re.compile(r"\bbroken\b", re.I),
    re.compile(r"\berror\b", re.I),
    re.compile(r"\bmismatch\b", re.I),
    re.compile(r"\bunclear\b", re.I),
    re.compile(r"\bhard to\b", re.I),
    re.compile(r"\bdifficult\b", re.I),
]

PRAISE_PATTERNS = [
    re.compile(r"\blove\b", re.I),
    re.compile(r"\bgreat\b", re.I),
    re.compile(r"\bawesome\b", re.I),
    re.compile(r"\bworks well\b", re.I),
]

HIGH_SEVERITY = [
    re.compile(r"\bweek", re.I),
    re.compile(r"\bblocked\b", re.I),
    re.compile(r"\bchurn\b", re.I),
    re.compile(r"\bdeal\b", re.I),
    re.compile(r"\bsecurity\b", re.I),
    re.compile(r"\bcan['’]t ship\b", re.I),
    re.compile(r"\blegal\b", re.I),
    re.compile(r"\bcompliance\b", re.I),
    re.compile(r"\boutage\b", re.I),
    re.compile(r"\bdata loss\b", re.I),
    re.compile(r"\bunusable\b", re.I),
]

MEDIUM_SEVERITY = [
    re.compile(r"\bfrustrating\b", re.I),
    re.compile(r"\bslow\b", re.I),
    re.compile(r"\bconfus", re.I),
    re.compile(r"\bpain", re.I),
    re.compile(r"\bworkaround\b", re.I),
    re.compile(r"\bmanual\b", re.I),
]


def classify_kind(text: str) -> str:
    solution = any(p.search(text) for p in SOLUTION_PATTERNS)
    problem = any(p.search(text) for p in PROBLEM_PATTERNS)
    praise = any(p.search(text) for p in PRAISE_PATTERNS) and not problem and not solution
    if praise:
        return "praise"
    if solution and problem:
        return "mixed"
    if solution:
        return "solution_request"
    if problem:
        return "problem"
    return "other"


def classify_severity(text: str, kind: str) -> str:
    if any(p.search(text) for p in HIGH_SEVERITY):
        return "high"
    if kind == "problem" and any(p.search(text) for p in MEDIUM_SEVERITY):
        return "medium"
    if kind == "problem":
        return "medium"
    if kind == "solution_request":
        return "low"
    return "low"


def extract_requested_solutions(text: str) -> list[str]:
    solutions = []
    if re.search(r"\bterraform\b", text, re.I):
        solutions.append("Terraform integration")
    add = re.search(r"\b(?:add|build|support)\b(.{8,60}?)(?:[.!?]|$)", text, re.I)
    if add:
        solutions.append(add.group(0).strip(" ."))
    seen = []
    for s in solutions:
        if s not in seen:
            seen.append(s)
    return seen[:3]


def problem_summary(text: str, kind: str) -> str:
    if kind == "solution_request":
        return "Customer proposed a solution; underlying job-to-be-done is inferred from cluster context."
    return text[:177] + "…" if len(text) > 180 else text


def to_signals(raw_items: list[dict]) -> list[dict]:
    signals = []
    for index, raw in enumerate(raw_items):
        meta = with_normalized_meta(raw)
        kind = classify_kind(meta["text"])
        signals.append(
            {
                "id": meta.get("id") or f"SIG-{index + 1:03d}",
                "text": meta["text"],
                "source": meta["source"],
                "customer": meta["customer"],
                "segment": meta["segment"],
                "date": meta.get("date"),
                "kind": kind,
                "severity": classify_severity(meta["text"], kind),
                "themes": match_themes(meta["text"]),
                "requestedSolutions": extract_requested_solutions(meta["text"]),
                "problemSummary": problem_summary(meta["text"], kind),
            }
        )
    return signals
